"""`_scope_css` must scope selectors INSIDE at-rules, not only around them.

This exists because of a live failure on fracktal.in that no existing gate
caught. The scoper prefixes every selector with `.od-embed` so a design's
generic rules cannot restyle the theme's chrome. It scoped the base rules and
silently skipped everything inside `@media`, because it read the at-rule
keyword with `prelude.split()` and minified CSS writes `@media(max-width:...)`
with no space — so the token was the whole prelude, missed the recognised list,
and the block was kept verbatim.

The damage is entirely about specificity. `.od-embed .grid-4` is (0,2,0) and a
bare `.grid-4` inside a media query is (0,1,0); media queries add none. So the
desktop rule outranked every responsive override at every width, the grids
never collapsed, and the page had a horizontal scrollbar on a phone.

It was invisible to `verify.py`, which renders the LOCAL build. Locally there
is no `.od-embed` wrapper, both rules tie at (0,1,0), source order puts the
media query last, and all five widths pass. The defect only exists after the
deploy-time scoping — so it has to be tested here, at the scoper.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / ".tmp" / "scripts"))

from open_design_bridge import _scope_css  # noqa: E402

SCOPE = ".od-embed"


def _block(css: str, opener: str) -> str:
    """The text inside the first at-rule whose prelude contains `opener`."""
    m = re.search(re.escape(opener) + r"[^{]*\{", css)
    assert m, f"no at-rule matching {opener!r} in:\n{css}"
    i, depth = m.end(), 1
    while i < len(css) and depth:
        depth += (css[i] == "{") - (css[i] == "}")
        i += 1
    return css[m.end():i]


@pytest.mark.parametrize("prelude", [
    "@media(max-width:1000px)",      # minified — the form that broke
    "@media (max-width: 1000px)",    # spaced — the form that always worked
    "@supports(display:grid)",
    "@container(min-width:400px)",
])
def test_selectors_inside_at_rules_are_scoped(prelude: str) -> None:
    out = _scope_css(".grid-4{color:red}\n%s{.grid-4{color:blue}}" % prelude,
                     SCOPE)
    inner = _block(out, prelude.split("(")[0])
    assert f"{SCOPE} .grid-4" in inner, (
        f"selector inside {prelude} was left unscoped — it will lose to the "
        f"scoped base rule at every width, because media queries add no "
        f"specificity.\ngot: {inner!r}")


def test_base_and_at_rule_selectors_end_up_equally_specific() -> None:
    """The real invariant. Equal specificity is what lets source order win.

    A responsive override is only reachable if it is at least as specific as
    the base rule it overrides. Counting `.od-embed` occurrences is a crude
    proxy for specificity, and crude is the point: it fails loudly the moment
    one side gets scoped and the other does not.
    """
    css = ".grid-4{grid-template-columns:repeat(4,1fr)}\n" \
          "@media(max-width:1000px){.grid-4{grid-template-columns:repeat(2,1fr)}}"
    out = _scope_css(css, SCOPE)
    base = out[:out.index("@media")]
    inner = _block(out, "@media")
    assert base.count(SCOPE) == inner.count(SCOPE) == 1


def test_keyframes_are_left_verbatim() -> None:
    """`0%`/`to` are not selectors. Scoping them produces invalid CSS."""
    out = _scope_css("@keyframes spin{from{transform:none}to{transform:none}}",
                     SCOPE)
    assert SCOPE not in out, f"keyframe steps must not be scoped: {out!r}"


def test_font_face_is_left_verbatim() -> None:
    out = _scope_css("@font-face{font-family:X;src:url(x.woff2)}", SCOPE)
    assert SCOPE not in out


def test_nested_at_rules_recurse() -> None:
    out = _scope_css(
        "@supports(display:grid){@media(max-width:600px){.a{color:red}}}", SCOPE)
    assert f"{SCOPE} .a" in out


def test_real_home_css_has_no_unscoped_grid_rule() -> None:
    """The actual stylesheet that shipped broken, if it is still in the repo."""
    css_path = (pathlib.Path(__file__).resolve().parents[1] / "outputs" /
                "fracktal-site" / "site" / "assets" / "home.css")
    if not css_path.exists():
        pytest.skip("fracktal-site/site/assets/home.css not present")
    out = _scope_css(css_path.read_text(encoding="utf-8"), SCOPE)
    # every selector mentioning a grid class must carry the scope
    for sel in re.findall(r"([^{}]*\.(?:grid-[34]|prod-grid)[^{}]*)\{", out):
        assert SCOPE in sel, f"unscoped grid selector survived: {sel.strip()!r}"
