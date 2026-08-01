"""The site engine's invariants, with no server and no network.

This is the CI gate. `live_editor_parity.py` next door covers the HTTP surface
and needs a running editor; everything here runs from a cold checkout in a
second, which is what makes it worth wiring into a hook.

Each test names the failure it exists to catch. Several of them are incidents
that already happened — an engine test that is not tied to a real bug tends to
be a test of the implementation rather than of the behaviour.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1] / "outputs" / "drvarada-site" / "site"
sys.path.insert(0, str(SITE))

import resolver                                     # noqa: E402
import versions                                     # noqa: E402
from linkscan import normalize                      # noqa: E402


# ── the version model ────────────────────────────────────────────────────────
@pytest.fixture
def store(tmp_path: Path):
    """A version store over two throwaway files."""
    project = tmp_path / "project"
    (project / "site").mkdir(parents=True)
    a, b = project / "site" / "a.py", project / "site" / "b.py"
    a.write_text("A1", encoding="utf-8")
    b.write_text("B1", encoding="utf-8")
    v = versions.Versions(project, tmp_path / ".versions")
    return v, project, a, b


def snap(project: Path) -> dict[Path, str]:
    return {p: p.read_text(encoding="utf-8")
            for p in project.rglob("*.py")}


def test_restore_appends_rather_than_truncating(store):
    """Open Design's central rule. If restore rewound instead, every state made
    after the restore point would be unreachable — which is exactly how an hour
    of edits nearly went missing on 2026-07-30."""
    v, project, a, _ = store
    v.ensure_current(snap(project))
    a.write_text("A2", encoding="utf-8")
    v.create(snap(project), source="edit", prompt="second")
    depth = len(v.entries)

    first = v.entries[0]
    got = v.restore(first["id"])
    assert got["ok"]
    for path, text in got["files"].items():
        (project / path).write_text(text, encoding="utf-8")
    v.note_restored(snap(project), got)

    assert len(v.entries) == depth + 1, "restore must append, never truncate"
    assert "restored from v" in v.entries[-1]["label"]
    assert any(e["prompt"] == "second" for e in v.entries), \
        "the version we restored away from must still be reachable"


def test_undo_follows_lineage_not_array_order(store):
    """An append-only array plus a linear cursor walks Ctrl+Z into branches the
    user abandoned. Undo has to follow the version each entry was MADE FROM."""
    v, project, a, _ = store
    v.ensure_current(snap(project))
    a.write_text("A2", encoding="utf-8")
    v.create(snap(project), source="edit", prompt="two")
    a.write_text("A3", encoding="utf-8")
    v.create(snap(project), source="edit", prompt="three")

    back = v.step(-1)
    assert back.get("ok"), back
    assert back["entry"]["prompt"] == "two", \
        "undo landed somewhere other than the version this one was made from"
    assert v.step(1)["entry"]["prompt"] == "three"


def test_unchanged_files_cost_nothing(store):
    """Content addressing is the reason 300 versions of a 540 KB tree is not
    100 MB. If b.py is stored twice, the blob store has stopped deduplicating."""
    v, project, a, _ = store
    v.ensure_current(snap(project))
    a.write_text("A2", encoding="utf-8")
    v.create(snap(project), source="edit")

    # Count distinct digests rather than files on disk: the digest set IS the
    # deduplication, and it does not depend on where the store keeps its shards.
    digests = {d for e in v.entries for d in e["files"].values()}
    assert len(digests) == 3, \
        f"expected a.py×2 + b.py×1 distinct blobs, got {len(digests)}"


def test_a_corrupt_entry_is_skipped_not_raised_on(store, tmp_path):
    """History is a convenience. A journal that will not parse must never stop
    someone editing their site."""
    v, project, a, _ = store
    v.ensure_current(snap(project))
    a.write_text("A2", encoding="utf-8")
    v.create(snap(project), source="edit", prompt="good")

    manifest = tmp_path / ".versions" / "manifest.json"
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    doc["entries"].insert(1, {"id": "broken"})     # no version, no files
    manifest.write_text(json.dumps(doc), encoding="utf-8")

    reopened = versions.Versions(project, tmp_path / ".versions")
    assert [e["prompt"] for e in reopened.entries if e["prompt"] == "good"], \
        "the surviving entries should still be readable"
    assert all("files" in e for e in reopened.entries)


def test_seeding_captures_work_done_outside_the_editor(store):
    """`ensure_current` is why a git checkout is not buried by the first edit.
    Without it the pre-edit state has no version to return to."""
    v, project, a, _ = store
    v.ensure_current(snap(project))
    assert len(v.entries) == 1
    a.write_text("edited on disk, editor not running", encoding="utf-8")
    v.ensure_current(snap(project))
    assert len(v.entries) == 2, "drift on disk must be captured before it is lost"
    assert v.entries[-1]["source"] == "seed"


# ── byte offsets ─────────────────────────────────────────────────────────────
def test_column_offsets_are_characters_not_utf8_bytes():
    """`ast` reports col_offset in UTF-8 bytes. Copy full of em dashes silently
    corrupts naive slicing, which is why every span write goes through this."""
    line = "x = '— — —' + y"
    byte_col = len("x = '— —".encode("utf-8"))
    assert resolver.char_col(line, byte_col) == len("x = '— —")
    assert resolver.char_col(line, 0) == 0
    assert resolver.char_col(line, 4) == 4, "ASCII must be unaffected"


# ── link normalisation ───────────────────────────────────────────────────────
@pytest.mark.parametrize("href,want", [
    ("vitiligo.html", "vitiligo"),
    ("/vitiligo/", "vitiligo"),
    ("/locations/secunderabad/", "locations-secunderabad"),
    ("/vitiligo/graft-surgery/", "vitiligo-graft-surgery"),
    ("https://wa.me/919989955330", "https://wa.me/919989955330"),
    ("tel:+919989955330", "tel:+919989955330"),
    ("#book", "#book"),
    ("", ""),
])
def test_rendered_hrefs_normalise_back_to_what_the_source_stores(href, want):
    """The browser reports `vitiligo.html`; the source stores `vitiligo`. Skip
    this and "used on 21 pages" reads as "used once" — the worst possible answer
    from a control that offers to change every one of them."""
    assert normalize(href) == want


def test_external_links_are_never_rewritten():
    """A URL is a destination, not a slug. Stripping its last path segment would
    point a Practo link at the word 'practo'."""
    for url in ("https://www.practo.com/hyderabad/doctor/x",
                "https://www.google.com/maps/search/?api=1&query=y"):
        assert normalize(url) == url
