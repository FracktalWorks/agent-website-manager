"""Application tiles on the material pages — one picture, one job.

Fifty tiles across twelve material pages were sharing fifteen pictures. A
single photograph of a matte black bracket was Automotive on eight different
materials; one prototyping shot appeared eleven times; ASA showed the SAME
image for "Outdoor / Garden" and for "Marine", two tiles apart on one page.
Seven tiles were blank.

None of that fails a build. Every file existed, every path resolved, every page
rendered clean at five widths — `verify.py` checks that an image LOADS, and all
of these loaded. What was wrong is the only thing it cannot check: whether the
picture is of the thing the words underneath it describe.

The blank seven are the tell. They were emptied on purpose (`briefs/
RESTORE.json`) because the photograph was of a *different material* — a CF-PA
enclosure standing in for ABS, which on a page selling ABS is a claim about
what arrives in the box. Emptying them was right; leaving them empty was the
half of the job that never got finished.

So these assertions are about provenance and fit, not about files loading.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "fracktal-site" / "site"
COPY = SITE / "content" / "materials-copy.json"
IMG = SITE / "assets" / "img"

pytestmark = pytest.mark.skipif(
    not COPY.exists(), reason="fracktal site not in this checkout")

# Two tiles keep a photograph whose filename does not carry the page's slug.
# `cf-nylon` is the site's URL for the material the media library files under
# its resin name, CF-PA. They are real photographs of the right material on
# that material's own page, used once each — a generated picture that fitted
# the bullets more neatly would still be a worse picture than a true one.
REAL_PHOTOS = {
    "cf-nylon": {"fracktal-cf-pa-aerospace-drone-frame.webp",
                 "fracktal-cf-pa-electronics-enclosure.webp"},
}


def tiles():
    """(material, index, title, image dict) for every application tile."""
    page = json.loads(COPY.read_text(encoding="utf-8"))
    for material, data in page.items():
        for i, tile in enumerate(data["applications"]["tiles"]):
            yield material, i, tile["title"], (tile.get("image") or {})


def test_every_application_tile_has_a_picture():
    """A blank tile in a grid of pictures reads as a page still being built.

    Seven were blank when this started — emptied on purpose because the
    photograph was of a different material, then left that way. There is no
    allowance here any more: every one of the fifty has its own picture, and a
    tile that loses one should stop the build rather than wait to be noticed.
    """
    blank = [f"{m}[{i}] {t}" for m, i, t, im in tiles() if not im.get("src")]
    assert not blank, f"tiles with no image: {blank}"


def test_no_picture_does_duty_on_two_different_tiles():
    """The defect itself, stated as a rule.

    A tile says "this material, in this industry". The same photograph under
    eight different materials contradicts seven of those sentences, and the
    reader who notices trusts the specifications less for it. Reuse WITHIN a
    page is worse still — ASA's Outdoor and Marine tiles were two apart.
    """
    seen: dict[str, list[str]] = {}
    for material, i, title, im in tiles():
        if im.get("src"):
            seen.setdefault(im["src"], []).append(f"{material}[{i}] {title}")
    shared = {src: where for src, where in seen.items() if len(where) > 1}
    assert not shared, f"pictures used on more than one tile: {shared}"


def test_no_tile_borrows_a_picture_of_another_material():
    """The failure that got seven tiles emptied in the first place.

    Enforced on the filename because that is what a person reads when they go
    looking: `apps/abs-automotive-trim.jpg` on the ABS page is checkable at a
    glance, and `apps/cf-nylon-...` on the PET-G page would not survive one.
    The name is not proof of what is in the picture — nothing here can be —
    but it makes the wrong thing loud instead of invisible.
    """
    wrong = []
    for material, i, title, im in tiles():
        src = im.get("src", "")
        if not src:
            continue
        if src in REAL_PHOTOS.get(material, ()):
            continue
        parts = Path(src).parts
        stem = Path(src).stem
        owned = parts[0] == material or stem.startswith(f"{material}-")
        if not owned:
            wrong.append(f"{material}[{i}] {title} -> {src}")
    assert not wrong, (
        "these tiles show a picture named for another material: " f"{wrong}")


def test_every_tile_picture_exists_and_declares_its_real_size():
    """A declared ratio that disagrees with the file squashes the picture.

    The tiles are `object-fit: cover` at a fixed height, so a wrong ratio does
    not letterbox — it silently crops differently than intended, which is the
    kind of thing that looks like a bad photograph rather than a bad number.
    """
    from PIL import Image
    bad = []
    for material, i, title, im in tiles():
        src = im.get("src")
        if not src:
            continue
        path = IMG / src
        if not path.exists():
            bad.append(f"{material}[{i}] missing file {src}")
            continue
        if not (im.get("width") and im.get("height")):
            continue
        with Image.open(path) as f:
            real = f.width / f.height
        declared = im["width"] / im["height"]
        if abs(real - declared) > 0.01:
            bad.append(f"{material}[{i}] {src}: declared "
                       f"{im['width']}x{im['height']}, file is {f.width}x"
                       f"{f.height}")
    assert not bad, bad


def test_every_generated_tile_picture_is_in_the_ledger():
    """`GENERATED.md` is how a picture can be corrected rather than defended.

    Forty of these were made by a model. Without the prompt on record the only
    way to fix one is to guess what was asked for, and the one thing this repo
    has learned about generated imagery is that the failure is a good picture
    of the wrong thing — which you can only correct if you can re-run the ask.
    """
    ledger = (IMG / "GENERATED.md").read_text(encoding="utf-8")
    missing = [im["src"] for _, _, _, im in tiles()
               if im.get("src", "").startswith("apps/")
               and f"`{im['src']}`" not in ledger]
    assert not missing, f"generated but unrecorded: {missing}"
