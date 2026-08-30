"""Every icon a page asks for must exist, and must be drawn like the others.

WHAT THIS EXISTS TO CATCH

There were two icon registries and both defaulted to an empty string:
`content/icons.json` behind `chrome.icon()`, and a hard-coded `_FEATURE_ICONS`
dict inside chrome.py behind its own `.get(name, "")`. Neither knew about the
other. **549 of the 789 icon references on this site resolved to nothing** —
seventy-two of the ninety-six pages shipped cards with an empty red tile where
the glyph belonged, and every gate passed, because an empty string is valid
HTML and an empty tile is a plausible design.

Thirty-seven names existed in both dicts as two different drawings, so `spool`
was two different pictures on one site depending on which block rendered it.

It was found by a person looking at one section of one page. That is the part
worth fixing: not the icons, but the silence.

WHAT IS NOT TESTED HERE

Whether an icon *reads*. A 24px glyph can be geometrically perfect and still be
unrecognisable — `spool` and `target` were both three concentric circles and
therefore the same picture until someone looked at them side by side. Run
`python icons.py --sheet` and open it; no assertion substitutes for that.
"""
from __future__ import annotations

import glob
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "fracktal-site" / "site"
STORE = SITE / "content" / "icons.json"

pytestmark = pytest.mark.skipif(
    not STORE.exists(), reason="fracktal site not in this checkout")

# The keys chrome.py passes to icon(). Kept here rather than derived so that a
# new one added to chrome.py without a thought here shows up as a gap.
ICON_KEYS = {"icon", "tick"}


def _icons() -> dict[str, str]:
    return json.loads(STORE.read_text(encoding="utf-8"))


def _module(name: str):
    spec = importlib.util.spec_from_file_location(f"fracktal_{name}",
                                                  SITE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _referenced() -> dict[str, list[str]]:
    """icon name -> the page files that ask for it."""
    out: dict[str, list[str]] = {}

    def walk(node, slug, key=None):
        if isinstance(node, str):
            if key in ICON_KEYS and node:
                out.setdefault(node, []).append(slug)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, slug, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, slug, key)

    for f in sorted(glob.glob(str(SITE / "content" / "*-copy.json"))):
        slug = Path(f).name.replace("-copy.json", "")
        walk(json.loads(Path(f).read_text(encoding="utf-8")), slug)
    return out


def test_every_reference_resolves():
    icons, used = _icons(), _referenced()
    missing = {n: sorted(set(p))[:4]
               for n, p in used.items() if n not in icons}
    assert not missing, (
        "icon name(s) the pages ask for and icons.json does not have — "
        "these render as an empty tile:\n"
        + "\n".join(f"  {n}: {p}" for n, p in sorted(missing.items())))


def test_unknown_name_raises_rather_than_blanking():
    """The silence is the bug. A typo must stop the build, not ship a hole."""
    chrome = _module("chrome")
    assert chrome.icon("") == "", "an absent icon is a real state; keep it"
    with pytest.raises(KeyError):
        chrome.icon("no-such-icon-anywhere")


def test_no_icon_is_defined_but_unused():
    """Dead art drifts out of style and gets copied by the next person."""
    icons, used = _icons(), _referenced()
    dead = sorted(set(icons) - set(used))
    assert not dead, f"defined but never referenced: {dead}"


@pytest.mark.parametrize("attr,want", [
    ("stroke", "currentColor"),
    ("stroke-linecap", "round"),
    ("stroke-linejoin", "round"),
    ("fill", "none"),
])
def test_new_icons_share_the_house_style(attr, want):
    """The 43 drawn in-repo must sit beside the 28 scraped ones without a seam.

    Only the semantic names are checked. The hashed ids came off the old
    Elementor site with their own hard-coded strokes (`#f25e50`, `#ffffff`),
    and rewriting those would change pages nobody asked us to change.
    """
    icons = _icons()
    ours = {n: s for n, s in icons.items()
            if not re.fullmatch(r"i[0-9a-f]{8}", n)}
    assert len(ours) >= 40, "expected the in-repo icon set"
    bad = [n for n, svg in ours.items() if f'{attr}="{want}"' not in svg]
    assert not bad, f"{attr} is not {want!r} on: {sorted(bad)}"


def test_every_icon_declares_the_same_viewbox():
    """A different viewBox is a different scale, and it shows on the card."""
    ours = {n: s for n, s in _icons().items()
            if not re.fullmatch(r"i[0-9a-f]{8}", n)}
    bad = [n for n, svg in ours.items() if 'viewBox="0 0 24 24"' not in svg]
    assert not bad, f"not on the 24x24 grid: {sorted(bad)}"


def test_every_icon_actually_draws_something():
    """An icon with no geometry is the empty tile wearing a definition."""
    ours = {n: s for n, s in _icons().items()
            if not re.fullmatch(r"i[0-9a-f]{8}", n)}
    shapes = r'<(path|circle|rect|line|polyline|polygon)\b'
    empty = [n for n, svg in ours.items() if not re.search(shapes, svg)]
    assert not empty, f"defined but draws nothing: {sorted(empty)}"
    stub = [n for n, svg in ours.items() if len(svg) < 180]
    assert not stub, f"suspiciously little geometry: {sorted(stub)}"


# NOTE: there is deliberately no test that the art stays inside the 24x24 box.
# The obvious version of it — scan the `d` attribute for a number outside
# 0..24 — is wrong, because SVG paths are mostly RELATIVE: in `M2.5 21h19`
# the 19 is a distance, not a coordinate, and every icon trips it. Doing it
# properly means walking each path command and tracking the current point,
# which is a real parser to maintain for a defect the contact sheet shows at a
# glance. Clipping is a visual check: `python icons.py --sheet`.


def test_no_svg_lookup_falls_back_to_nothing():
    """An empty-string default on a dict of SVG is the whole bug, twice.

    `_FEATURE_ICONS.get(name, "")` is what shipped 549 empty tiles. The rule is
    not "one registry" — chrome.py legitimately holds three other SVG dicts —
    it is that none of them may answer a miss with nothing:

      LUCIDE["lightbulb"], _SVG["chev"]     direct subscript, raises on a miss
      REVIEW_MARKS.get(src, ...["google"])  falls back to a real mark

    Each of those fails loudly or produces a picture. An empty string produces
    a hole that looks like a design decision, and that is the one shape banned.
    """
    src = (SITE / "chrome.py").read_text(encoding="utf-8")
    holders = re.findall(r"^([A-Za-z_]\w*)\s*=\s*\{[^}]*<svg", src, re.M)
    assert holders, "expected chrome.py to hold some SVG; check this pattern"
    blank = [n for n in holders
             if re.search(rf"\b{n}\.get\([^)]*,\s*[\"']{{2}}\s*\)", src)]
    assert not blank, (
        f"these answer an unknown name with an empty string: {blank}. "
        "Page icons belong in content/icons.json behind icon(), which raises; "
        "anything else needs a real fallback, not a hole.")
