"""The webfonts — a defect that was invisible to every gate for months.

The build named Montserrat and Work Sans in the `<head>` as a Google Fonts
`<link>`, and `deploy.py cmd_prep` carried that link into the deployed body
along with the `/assets/` stylesheets. Locally it worked: `verify.py` and
`mobile.py` render the built files, the font loaded, and every measurement they
took — tap targets, drawn text sizes, the home page's trust chips tuned to fit
two per row — was a measurement of Montserrat.

No visitor ever saw it. **LiteSpeed Cache's "Remove Google Fonts" is enabled on
fracktal.in** and strips exactly that tag: on the live page the two `preconnect`
hints survive, both same-origin stylesheets survive, and the Google Fonts
stylesheet is gone. Every page rendered in `system-ui`. Nothing failed — the
page was valid, fast and complete, just set in the wrong typeface, and the gates
could not see it because they never look at the live site.

The fonts are self-hosted now (`fonts.py`), which is also the only fix that does
not involve turning a site-wide performance setting off to make a deploy work.
These are the assertions that keep it that way.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "fracktal-site" / "site"
ASSETS = SITE / "assets"

pytestmark = pytest.mark.skipif(
    not (SITE / "fonts.py").exists(),
    reason="fracktal site not in this checkout")

RUPEE = 0x20B9


def faces() -> list[dict]:
    """Every `@font-face` chrome.css declares, as family/url/unicode-range."""
    css = (ASSETS / "chrome.css").read_text(encoding="utf-8")
    out = []
    for rule in re.findall(r"@font-face\{([^}]*)\}", css):
        def field(name):
            m = re.search(rf"{name}:\s*([^;]+)", rule)
            return m.group(1).strip() if m else ""
        url = re.search(r"url\('([^']+)'\)", rule)
        out.append({"family": field("font-family").strip("'\""),
                    "url": url.group(1) if url else "",
                    "range": field("unicode-range")})
    return out


def covers(spec: str, cp: int) -> bool:
    for part in spec.split(","):
        part = part.strip()
        if "-" in part[2:]:
            lo, hi = part[2:].split("-")
            if int(lo, 16) <= cp <= int(hi, 16):
                return True
        elif int(part[2:], 16) == cp:
            return True
    return False


def test_every_declared_font_file_is_actually_there():
    """An `@font-face` pointing at nothing degrades in silence.

    The browser falls back to the next family in the stack and renders a
    perfectly good page in the wrong typeface — which is the exact failure this
    whole module exists because of.
    """
    assert faces(), "chrome.css declares no @font-face at all"
    for face in faces():
        assert face["url"].startswith("/assets/fonts/"), face
        path = SITE / face["url"].lstrip("/")
        assert path.exists(), f"{face['family']}: no file at {face['url']}"
        assert path.stat().st_size > 5000, f"{path} is suspiciously small"


def test_the_rupee_sign_is_covered_by_a_shipped_subset():
    """₹ is NOT in Google's latin subset. It lives in latin-ext.

    This site prices in rupees on its most-read line. Ship only the latin
    subset and the digits come from Montserrat while the ₹ falls back to
    system-ui — a glyph of a different weight and width welded onto the front
    of every price. It is small, it is on every pricing page, and it is the
    kind of thing that reads as "not quite finished" without anyone being able
    to say why.
    """
    from fontTools.ttLib import TTFont
    families = {f["family"] for f in faces()}
    for family in families:
        declared = [f for f in faces()
                    if f["family"] == family and covers(f["range"], RUPEE)]
        assert declared, (
            f"no {family} subset declares U+20B9 — every ₹ on the site will "
            f"fall back to another typeface")
        for face in declared:
            cmap = TTFont(SITE / face["url"].lstrip("/")).getBestCmap()
            assert RUPEE in cmap, (
                f"{face['url']} claims U+20B9 in its unicode-range but the "
                f"file does not contain the glyph")


def test_nothing_asks_google_for_a_font_any_more():
    """It is stripped in production, so a request here is a silent downgrade.

    Both routes are covered: the `<link>` the head used to emit, and the
    `@import` that sat at the top of site.css. An @import is worse than the
    link even where it survives — the browser cannot see it until site.css has
    downloaded and parsed, so it serialises two round trips before any text can
    paint.
    """
    offenders = []
    for css in ASSETS.glob("*.css"):
        if "fonts.googleapis" in css.read_text(encoding="utf-8"):
            offenders.append(css.name)
    for py in (SITE / "chrome.py",):
        if "fonts.googleapis.com/css2" in py.read_text(encoding="utf-8"):
            offenders.append(py.name)
    assert not offenders, (
        f"{offenders} still request a font from Google, which LiteSpeed "
        f"removes from every live page")


def test_the_font_is_declared_where_every_page_will_see_it():
    """chrome.css is the one sheet all four page stylesheets share.

    Declared in `landing.css` instead, the material pages — which load
    `site.css` — would render in the fallback while the printer pages did not,
    and the two would be a hairline apart in a way nobody would think to check.
    """
    assert "@font-face" in (ASSETS / "chrome.css").read_text(encoding="utf-8")
    stacks = {}
    for css in ASSETS.glob("*.css"):
        text = css.read_text(encoding="utf-8")
        for family in re.findall(r"--(?:fw-)?font[a-z-]*:\s*'?\"?([^,;'\"]+)",
                                 text):
            stacks.setdefault(family.strip(), []).append(css.name)
    declared = {f["family"] for f in faces()}
    missing = {f: w for f, w in stacks.items()
               if f not in declared and not f.startswith(("var(", "system"))}
    assert not missing, (
        f"these families are asked for but never self-hosted: {missing}")
