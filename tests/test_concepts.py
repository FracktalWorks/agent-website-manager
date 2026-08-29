"""The design-concepting round: scaffold, compare page, decision.

`concepts.py` owns the deterministic half of the design_concepting skill.
These tests cover the ways its state-reading has been (or would be) got
wrong: titles from NOTES.md, the decision marker, working-state exclusion,
and a compare page that must reflect what is actually on disk.
"""
from __future__ import annotations

import importlib.util
from argparse import Namespace
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "concepts",
    Path(__file__).resolve().parents[1] / ".github" / "skills"
    / "design_concepting" / "scripts" / "concepts.py")
concepts = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(concepts)


@pytest.fixture()
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A fake outputs/ tree with one project and two directions."""
    monkeypatch.setattr(concepts, "OUTPUTS", tmp_path)
    croot = tmp_path / "acme-site" / "concepts"
    for rel, text in (
            ("calm/index.html", "<h1>calm</h1>"),
            ("calm/NOTES.md",
             "# Calm Editorial\n\n**Dials:** variance 5 / motion 3\n"),
            ("bold/index.html", "<h1>bold</h1>"),
            ("_wip/index.html", "draft")):
        f = croot / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    return croot


def test_directions_skip_working_state(project: Path):
    """`_wip/` is a draft, not a direction the user gets to choose."""
    assert [d.name for d in concepts.directions(project)] == ["bold", "calm"]


def test_notes_name_the_direction(project: Path):
    meta = concepts.notes_meta(project / "calm")
    assert meta["title"] == "Calm Editorial"
    assert meta["dials"] == "variance 5 / motion 3"
    # A bare direction still has a readable name.
    assert concepts.notes_meta(project / "bold")["title"] == "Bold"


def test_compare_page_reflects_the_decision(project: Path, capsys):
    """Before a decision the page says so; after, the chosen card is badged.
    The page embeds every direction as a live iframe, relative paths only,
    so it works from disk and through the hub's /art/ route alike."""
    concepts.cmd_compare(Namespace(project="acme-site"))
    page = (project / "compare.html").read_text(encoding="utf-8")
    assert page.count('<iframe src="') == 2
    assert "no decision yet" in page and "badge chosen" not in page

    concepts.cmd_decide(
        Namespace(project="acme-site", direction="bold", force=False))
    concepts.cmd_compare(Namespace(project="acme-site"))
    page = (project / "compare.html").read_text(encoding="utf-8")
    assert 'badge chosen' in page and "Direction chosen" in page
    assert concepts.chosen_slug(project) == "bold"


def test_decide_refuses_a_direction_that_does_not_exist(project: Path):
    """A typo must not silently bless a non-existent mockup."""
    with pytest.raises(SystemExit):
        concepts.cmd_decide(
            Namespace(project="acme-site", direction="nope", force=False))
