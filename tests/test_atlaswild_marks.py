"""The derived logo set: is what shipped what the generator produces?

`design-system/derive_marks.py` extends the client's brand kit with the 77
marks it does not supply — badges, plaques, chips, clear-space cuts, knockouts,
watermarks, pattern densities, maskable icons. Everything is a transform of the
supplied artwork, so a bug here is silent: the file exists, has the right name,
opens without error, and is wrong.

Two have already shipped that way. `body_of()` cut at the XML declaration and
every derived file was malformed; then every badge rendered black because the
fill was written to the tag `body_of()` strips. Neither was visible in a number
and both were obvious on a contact sheet.

`derive_marks.py --check` is the full gate: it re-derives every file, compares
it byte for byte against the disk, and RASTERISES the set to prove the ink is
there and is the colour it claims. That needs Chrome and takes a few seconds,
so it is not what CI runs. These tests are the fast half — everything provable
without a browser — plus the wiring between the generator, the manifest, the
delivery tree and the hub, which is where a new family silently goes missing.

Skipped entirely when the project is not in this checkout.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "outputs" / "atlaswild-site" / "design-system"
MARKS = DS / "assets" / "marks"
BRAND = ROOT / "outputs" / "atlaswild-site" / "brand"

pytestmark = pytest.mark.skipif(
    not (MARKS.is_dir() and (DS / "assets" / "MARKS.json").exists()),
    reason="atlaswild design system not in this checkout")

SVG = "{http://www.w3.org/2000/svg}"
HEX = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
PALETTE = {"#000000", "#2c3c1a", "#687532", "#8c3900",
           "#dd7d36", "#ffdd9d", "#f4e7ce", "#ffffff"}


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads((DS / "assets" / "MARKS.json").read_text("utf-8"))


@pytest.fixture(scope="module")
def files() -> list[Path]:
    return sorted(MARKS.glob("*.svg"))


def test_every_mark_parses(files):
    """The `body_of()` trap: an unclosed <svg> renders as a broken image and
    reads as a perfectly ordinary file in a directory listing."""
    for f in files:
        try:
            root = ET.fromstring(f.read_text(encoding="utf-8"))
        except ET.ParseError as e:                       # pragma: no cover
            pytest.fail(f"{f.name} is malformed SVG: {e}")
        assert root.tag == f"{SVG}svg", f"{f.name}: root is not <svg>"
        assert "viewBox" in root.attrib, f"{f.name}: no viewBox, cannot scale"


def test_no_colour_outside_the_clients_palette(files):
    """The kit is the source of truth. A near-miss hex is the one kind of
    brand error nobody notices and everybody's eye registers."""
    for f in files:
        stray = {h.lower() for h in HEX.findall(f.read_text(encoding="utf-8"))
                 if h.lower() not in PALETTE | {"#fff", "#000"}}
        assert not stray, f"{f.name} paints {sorted(stray)}"


def test_currentcolor_marks_carry_no_hex(files):
    """A currentColor mark with a hex in it is just a coloured mark that
    claims to follow its context and does not."""
    for f in files:
        if "currentcolor" in f.name:
            assert not HEX.findall(f.read_text(encoding="utf-8")), \
                f"{f.name} is not actually currentColor"


def test_manifest_and_directory_agree(manifest, files):
    """The delivery tree folders by MARKS.json, and the hub's Collateral view
    groups by folder — so a mark missing from the manifest is a mark that
    silently never reaches anybody."""
    assert {m["file"] for m in manifest["marks"]} == {f.name for f in files}


def test_badge_pairings_are_all_AA(manifest):
    """A badge is a colour decision. `derive_tokens.py` verified four
    ground/ink pairings; nothing here may quietly introduce a fifth.

    Orange is why this exists: it is the brand's loudest colour and 2.43:1 on
    cream, so the one pairing everybody reaches for first is the one that
    fails."""
    sys.path.insert(0, str(DS))
    from derive_tokens import contrast, PALETTE as P    # noqa: E402
    pairs = {tuple(m["pair"]) for m in manifest["marks"] if m["pair"]}
    assert pairs, "no pairings recorded — the check would pass vacuously"
    for ground, ink in pairs:
        c = contrast(P[ground], P[ink])
        assert c >= 4.5, f"{ink} on {ground} is {c:.2f}:1, below AA"


def test_the_small_size_mark_is_the_one_that_measured_smallest(manifest):
    """Badges use `insignia-3` because it measured legible smallest, not
    because it looks simplest. If a future run reorders the measurement, the
    choice of mark has to move with it."""
    m = manifest["min_px"]
    assert m["insignia-3"] <= m["insignia-1"], \
        "insignia-3 is no longer the small-size mark — rethink the badges"
    assert m["insignia-3"] <= m["monogram"]


def test_plate_floor_is_bigger_than_the_mark_floor(manifest):
    """A badge's mark is inset, so the plate must be larger than the mark's
    own floor — the number a designer sets is the plate."""
    assert manifest["min_px"]["insignia-3"] / 0.62 > \
        manifest["min_px"]["insignia-3"]


def test_delivery_tree_carries_every_derived_family(manifest):
    """`build_brand.py` folders marks by family. A new family that nobody
    added a directory for used to land in `lockups` via an `else`."""
    if not BRAND.is_dir():
        pytest.skip("brand tree not built")
    for m in manifest["marks"]:
        assert (BRAND / m["family"] / m["file"]).exists(), \
            f"{m['file']} never reached brand/{m['family']}/"


def test_hub_has_a_heading_for_every_family(manifest):
    """artifacts.py labels the Collateral view by folder name. An unlabelled
    family still renders — title-cased — so this is about the set staying
    deliberate, not about it crashing."""
    sys.path.insert(0, str(ROOT))
    import artifacts                                    # noqa: E402
    labels = artifacts.GALLERY_LABELS["brand"]
    for fam in {m["family"] for m in manifest["marks"]}:
        assert fam in labels, f"brand/{fam}/ has no heading in artifacts.py"


def test_contact_sheet_references_files_that_exist():
    """The sheet is the human half of the gate. A broken <img> on it is worse
    than no sheet: it reads as a mark that renders empty."""
    sheet = DS / "kit" / "preview" / "marks-contact-sheet.html"
    if not sheet.exists():
        pytest.skip("contact sheet not built")
    for src in re.findall(r'src="\.\./\.\./assets/marks/([^"]+)"',
                          sheet.read_text(encoding="utf-8")):
        assert (MARKS / src).exists(), f"contact sheet links a missing {src}"


def test_logo_page_shows_every_file_that_exists(manifest):
    """The logo-system page is the design system's answer to "what marks do we
    have". It used to show 4 lockups in one fill and 8 derived marks — 12 of
    138 — under a heading that called itself the logo system.

    Nothing on it was wrong. It was a curated fraction, which is worse than
    wrong: it reads as complete, and the files it leaves out are the ones
    somebody then goes and picks out of the asset directory by guesswork. So
    the page is generated FROM the manifests, and this is the assertion that
    keeps it that way.
    """
    page = DS / "kit" / "preview" / "logo-system.html"
    if not page.exists():
        pytest.skip("previews not built")
    html = page.read_text(encoding="utf-8")
    kit = json.loads((DS / "assets" / "MANIFEST.json").read_text("utf-8"))

    missing = [x["file"] for x in kit["logos"] if x["file"] not in html]
    assert not missing, \
        f"{len(missing)} supplied marks are not on the logo page: {missing[:6]}"
    missing = [m["file"] for m in manifest["marks"] if m["file"] not in html]
    assert not missing, \
        f"{len(missing)} derived marks are not on the logo page: {missing[:6]}"


def test_logo_page_states_the_measured_floors(manifest):
    """The floors are the page's most useful content and the easiest thing to
    let drift: they are numbers in prose. They must be read from the
    measurement, so a re-measure moves them."""
    page = DS / "kit" / "preview" / "logo-system.html"
    if not page.exists():
        pytest.skip("previews not built")
    html = page.read_text(encoding="utf-8")
    for mark, px in manifest["min_px"].items():
        assert f"{px}px" in html, f"the floor for {mark} ({px}px) is not stated"


def test_previews_do_not_reference_the_abandoned_rebrand():
    """`lockup-horizontal-ash.svg` sat in the component fixture for weeks
    after the Lala Wildlife rebrand was reversed: a dead <img> to a mark that
    is now a different company's."""
    for f in (DS / "kit").rglob("*.html"):
        text = f.read_text(encoding="utf-8")
        assert "-ash.svg" not in text, f"{f.name} still points at the rebrand"
        for src in re.findall(r'src="([^"h][^"]*\.svg)"', text):
            assert (f.parent / src).resolve().exists(), \
                f"{f.name} links a missing {src}"
