#!/usr/bin/env python
"""Drive this site from any of the 152 vendored design systems.

    python brandkit.py list                  # brands that can drive the site
    python brandkit.py show stripe           # derived palette + contrast report
    python brandkit.py apply stripe          # write assets/brand.css, activate it
    python brandkit.py apply --native        # back to the hand-tuned kit
    python brandkit.py calibrate             # do the rules reproduce the native kit?
    python brandkit.py check                 # every var() the site uses resolves

WHY THIS EXISTS
  The corpus in `agent-data/design-systems/` speaks a shared vocabulary of 54
  token names — `--bg`, `--fg`, `--accent`, `--radius-lg`. This site speaks its
  own — `--ground`, `--ink`, `--mint`, `--r`. The two share *zero* names, so
  before this module existed "build this like Stripe" produced an unstyled page:
  every `var(--ground)` resolved to nothing and every rule that used one was
  dropped. Nothing errored. The page just came out grey.

  This is the bridge. It reads a brand's canonical `:root`, derives this site's
  49 tokens from it, and writes a stylesheet that loads *after* the site's own
  so its `:root` wins. Two things make it more than a rename table:

  DERIVATION, NOT ALIASING.
  The site needs colours the schema has no name for: a dark punctuation band, a
  ramp for text on that band, three category pastels for the condition cards, a
  gold for star glyphs. Those are computed in OKLCH from the brand's own hue —
  so a Stripe build gets violet category cards, not the schema's absent ones.
  Aliasing alone would leave a third of the site undefined.

  CONTRAST IS REPAIRED, NOT INHERITED.
  Every derived text colour is walked along its lightness axis until it meets
  WCAG AA against the surfaces it actually appears on. A brand whose `--meta` is
  a decorative 3:1 grey cannot reintroduce the `--ink-3` failure that shipped on
  all 45 pages of this site, because the derivation will darken it and the
  build's contrast gate will catch it if the hue makes AA unreachable.

WHAT THIS DOES NOT DO
  It ports a brand's *palette, type and geometry* into this site's idiom. It
  does not restyle the site into the brand's idiom — Stripe's dense data panels
  and gradient hero are its layout language, not its tokens, and this site keeps
  its own. A Stripe build looks like this clinic site drawn in Stripe's colours
  and typeface. That is the honest description of what a token bridge can buy.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SITE_DIR = ROOT.parent
REPO = SITE_DIR.parent.parent
sys.path.insert(0, str(REPO / ".tmp" / "scripts"))

import design_systems as ds                       # noqa: E402
import webfonts as wf                             # noqa: E402

KIT = SITE_DIR / "design-system" / "kit" / "colors_and_type.css"
BRAND_CSS = ROOT / "assets" / "brand.css"
BRAND_STATE = ROOT / "assets" / "brand.json"
FONT_DIR = ROOT / "assets" / "fonts"


# ═════════════════════════════════════════════════════════════════════════════
# Colour
# ═════════════════════════════════════════════════════════════════════════════
# OKLab (Björn Ottosson, 2020) rather than HSL. HSL's "lightness" is not
# perceptual — darkening a yellow and a blue by the same HSL amount moves them
# by wildly different perceived distances, so a hue-rotated palette built in HSL
# comes out with one washed-out member and one muddy one. Every derivation here
# holds L and C steady and moves only H, which is only meaningful in OKLab.

def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(_clamp(c) * 255):02X}" for c in rgb)


def _to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _to_srgb(c: float) -> float:
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_oklab(rgb) -> tuple[float, float, float]:
    r, g, b = (_to_linear(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def oklab_to_rgb(lab, clamp: bool = True) -> tuple[float, float, float]:
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (x ** 3 for x in (l_, m_, s_))
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    out = tuple(_to_srgb(c) for c in (r, g, bb))
    return tuple(_clamp(c) for c in out) if clamp else out  # type: ignore


def to_lch(value: str) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(hex_to_rgb(value))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def from_lch(L: float, C: float, H: float) -> str:
    """OKLCH -> hex, reducing chroma until the colour is inside sRGB.

    Clamping the channels instead (the obvious shortcut) shifts hue: a
    saturated violet at high lightness clips blue first and drifts pink. Walking
    chroma down keeps the hue the caller asked for, which is the whole point of
    deriving a sibling colour by rotation.
    """
    L = _clamp(L, 0.0, 1.0)
    rad = math.radians(H)
    for step in range(41):
        c = max(0.0, C * (1 - step / 40))
        lab = (L, c * math.cos(rad), c * math.sin(rad))
        if all(-0.001 <= v <= 1.001 for v in oklab_to_rgb(lab, clamp=False)):
            return rgb_to_hex(oklab_to_rgb(lab))
        # Nothing at this hue and lightness is representable even at zero
        # chroma only when L itself is out of range, which _clamp prevented.
    return rgb_to_hex(oklab_to_rgb((L, 0, 0)))


def luminance(value: str) -> float:
    r, g, b = (_to_linear(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """Interpolate in OKLab — t=0 is `a`, t=1 is `b`."""
    la, lb = rgb_to_oklab(hex_to_rgb(a)), rgb_to_oklab(hex_to_rgb(b))
    return rgb_to_hex(oklab_to_rgb(tuple(x + (y - x) * t for x, y in zip(la, lb))))


def toward_contrast(fg: str, backgrounds, target: float) -> str:
    """Walk `fg` along its own lightness axis until it clears `target` on all backgrounds.

    Direction is chosen from the backgrounds, not from the foreground: text on
    pale surfaces must get darker, text on a dark band must get lighter. Hue and
    chroma are held, so the result is still recognisably the brand's colour —
    which is what separates this from "give up and use #333".
    """
    if isinstance(backgrounds, str):
        backgrounds = [backgrounds]
    if not backgrounds:
        return fg
    L, C, H = to_lch(fg)

    def worst(c: str) -> float:
        return min(contrast(c, b) for b in backgrounds)

    if worst(fg) >= target:
        return fg

    # Sweep the whole lightness axis rather than walking one direction. Several
    # corpus brands put a dark page background behind white cards, so the site's
    # single body-copy colour has to clear AA on surfaces at both ends — and the
    # only colours that can are in the middle, which a one-directional walk from
    # either end passes straight through and never considers. Among candidates
    # that clear the target, the one nearest the brand's original lightness wins,
    # so a readable colour is also still the brand's colour.
    best, best_ratio, passing = fg, worst(fg), []
    for step in range(201):
        cand_l = step / 200
        cand = from_lch(cand_l, C, H)
        ratio = worst(cand)
        if ratio >= target:
            passing.append((abs(cand_l - L), cand))
        if ratio > best_ratio:
            best, best_ratio = cand, ratio
    if passing:
        return min(passing)[1]
    return best            # unreachable target — the build's contrast gate reports it


def rgba(value: str, alpha: float) -> str:
    r, g, b = (round(c * 255) for c in hex_to_rgb(value))
    return f"rgba({r}, {g}, {b}, {alpha:g})".replace("0.", ".")


def composite(fg: str, alpha: float, bg: str) -> str:
    """Flatten a translucent colour over its background, for contrast checking."""
    f, b = hex_to_rgb(fg), hex_to_rgb(bg)
    return rgb_to_hex(tuple(x * alpha + y * (1 - alpha) for x, y in zip(f, b)))


# ═════════════════════════════════════════════════════════════════════════════
# Reading a brand's canonical tokens
# ═════════════════════════════════════════════════════════════════════════════
_MIX = re.compile(
    r"color-mix\(\s*in\s+\w+\s*,\s*(.+?)\s*,\s*(black|white|transparent)\s+([\d.]+)%\s*\)",
    re.I)


def resolve_colour(name: str, tokens: dict[str, str], depth: int = 0) -> str | None:
    """Reduce a token's value to a flat hex, following the forms the corpus uses.

    Four of them occur: hex, `rgba(...)`, `var(--other)` aliasing, and
    `color-mix(in oklab, var(--accent), black 8%)`. The alias and the mix both
    have to be evaluated here rather than left to the browser, because every
    derived value gets contrast-checked in Python — a value the checker cannot
    read is a value that silently skips the gate.
    """
    if depth > 6 or name not in tokens:
        return None
    v = str(tokens[name]).strip()
    return _resolve_value(v, tokens, depth)


def _resolve_value(v: str, tokens: dict[str, str], depth: int = 0) -> str | None:
    if depth > 6:
        return None
    v = v.strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3,8}", v):
        return "#" + v.lstrip("#")[:6].upper()
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)\s*(?:[,/]\s*[\d.%]+\s*)?\)", v)
    if m:
        return rgb_to_hex(tuple(float(x) / 255 for x in m.groups()))  # type: ignore
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,.*)?\)", v)
    if m:
        return resolve_colour(m.group(1), tokens, depth + 1)
    m = _MIX.fullmatch(v)
    if m:
        base = _resolve_value(m.group(1), tokens, depth + 1)
        if not base:
            return None
        pct = float(m.group(3)) / 100
        target = m.group(2).lower()
        if target == "transparent":
            return base            # alpha is not representable in a flat hex
        return mix(base, "#000000" if target == "black" else "#FFFFFF", pct)
    return None


def _px(value: str, default: float) -> float:
    m = re.search(r"(-?[\d.]+)\s*px", str(value))
    return float(m.group(1)) if m else default


def load_brand(system_id: str) -> tuple[dict[str, str], list[str]]:
    """Canonical token map for a corpus system, with A2 fallbacks filled in.

    The schema's `fallback` field is explicitly *not* a runtime default (there
    is no stylesheet in the cascade to provide it), so a brand that omits
    `--motion-fast` leaves `transition: var(--motion-fast)` unresolvable and the
    whole declaration is dropped. Filling them at authoring time is the step the
    schema documents and no corpus file performs.
    """
    css = ds.read_text(Path(ds.system_dir(system_id)) / "tokens.css")
    parsed = {k: v["value"] for k, v in ds.parse_root_tokens(css).items()}
    notes: list[str] = []
    for spec in ds.TOKEN_SCHEMA:
        n = spec["name"]
        if n in parsed:
            continue
        filler = spec.get("fallback") or spec.get("alias_to")
        if filler:
            parsed[n] = filler
            notes.append(f"{n} absent — filled from the schema ({spec['layer']})")
        else:
            notes.append(f"{n} absent and has no schema default ({spec['layer']})")
    return parsed, notes


def native_canonical() -> dict[str, str]:
    """Express the hand-tuned drvarada kit in canonical names.

    Used by `calibrate`: feeding the native brand through the same derivation
    the corpus brands go through, and diffing against the values a designer
    actually chose, is the only honest test of whether the rules are any good.
    """
    kit = {k: v["value"] for k, v in ds.parse_root_tokens(KIT.read_text(encoding="utf-8")).items()}
    return {
        "--bg": kit["--ground"], "--surface": kit["--paper"],
        "--surface-warm": kit["--tint"],
        "--fg": kit["--ink"], "--fg-2": kit["--ink-2"],
        "--muted": kit["--ink-2"], "--meta": kit["--ink-3"],
        "--border": "rgba(18, 32, 47, .16)", "--border-soft": "rgba(18, 32, 47, .10)",
        "--accent": kit["--mint-dp"], "--accent-on": kit["--paper"],
        "--accent-hover": "color-mix(in oklab, var(--accent), black 8%)",
        "--accent-active": "color-mix(in oklab, var(--accent), black 14%)",
        "--font-display": kit["--display"], "--font-body": kit["--body"],
        "--font-mono": kit["--mono"],
        "--text-xs": "12px", "--text-sm": "14.5px", "--text-base": "16px",
        "--text-lg": "20px", "--text-xl": "28px", "--text-2xl": "36px",
        "--text-3xl": "46px", "--text-4xl": "76px",
        "--leading-body": "1.65", "--leading-tight": "1.08",
        "--tracking-display": "-.03em",
        "--space-1": "4px", "--space-2": "8px", "--space-3": "12px",
        "--space-4": "16px", "--space-5": "20px", "--space-6": "24px",
        "--space-8": "32px", "--space-12": "48px",
        "--section-y-desktop": "128px", "--section-y-tablet": "96px",
        "--section-y-phone": "64px",
        "--radius-sm": kit["--r-sm"], "--radius-md": "20px", "--radius-lg": kit["--r"],
        "--radius-pill": kit["--r-pill"],
        "--elev-flat": "none", "--elev-ring": "0 0 0 1px var(--border)",
        "--elev-raised": kit["--shadow"],
        "--focus-ring": "0 0 0 3px rgba(11, 99, 83, .3)",
        "--motion-fast": "160ms", "--motion-base": "220ms",
        "--ease-standard": "cubic-bezier(0.2, 0, 0, 1)",
        "--container-max": kit["--wrap"],
        "--container-gutter-desktop": "22px", "--container-gutter-tablet": "22px",
        "--container-gutter-phone": "18px",
    }


# ═════════════════════════════════════════════════════════════════════════════
# Derivation
# ═════════════════════════════════════════════════════════════════════════════
# mint / apricot / lilac, evenly spaced around the accent. The order is not
# arbitrary: the site's second family is the warm one (aesthetics) and the third
# is the cool one (trichology), so rotating negative-then-positive from a
# blue-green accent lands them the right way round. Reversing the two produces a
# palette that passes every check and reads backwards.
CATEGORY_ROTATION = (0, -115, +115)
PASTEL_L, PASTEL_C = 0.865, 0.085    # the register drvarada's pastels sit in
SOFT_C = 0.030                       # chroma of the card tints
GOLD_HUE = 78.0                      # where "gold" reads as gold, not brown


def derive(canon: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Canonical brand tokens -> this site's 50 tokens, plus a report of choices made."""
    say: list[str] = []

    def col(name: str, fallback: str) -> str:
        v = resolve_colour(name, canon)
        if v is None:
            say.append(f"{name} unreadable — used {fallback}")
            return fallback
        return v

    bg = col("--bg", "#FFFFFF")
    surface = col("--surface", bg)
    warm = col("--surface-warm", surface)
    fg = col("--fg", "#111111")
    muted = col("--muted", fg)
    meta = col("--meta", muted)
    accent = col("--accent", fg)
    border = col("--border", mix(fg, bg, 0.86))
    border_soft = col("--border-soft", mix(fg, bg, 0.9))

    t = {}

    # ── surfaces ──────────────────────────────────────────────────────────
    t["--ground"] = bg
    t["--paper"] = surface
    # A tint that is within a hair of the page background makes the alternating
    # band rhythm invisible, and the rhythm is load-bearing on pages this long.
    if abs(luminance(warm) - luminance(bg)) < 0.012:
        warm = mix(bg, accent, 0.06)
        say.append(f"--surface-warm was indistinguishable from --bg — mixed 6% "
                   f"accent into the background instead ({warm})")
    t["--tint"] = warm

    # The dark punctuation band has no counterpart in the schema. Derived from
    # the brand's foreground so it stays in family, with chroma capped: a highly
    # saturated dark band fights the clinical photography it sits behind.
    L, C, H = to_lch(fg)
    t["--dark"] = from_lch(_clamp(L, 0.16, 0.24), min(C, 0.055), H)

    # ── ink ───────────────────────────────────────────────────────────────
    surfaces = [t["--ground"], t["--paper"], t["--tint"]]
    t["--ink"] = fg
    t["--ink-2"] = toward_contrast(muted, surfaces, 4.5)
    t["--ink-3"] = toward_contrast(meta, surfaces, 4.5)
    for label, src, out in (("--muted", muted, t["--ink-2"]), ("--meta", meta, t["--ink-3"])):
        if out != src:
            say.append(f"{label} {src} was {min(contrast(src, s) for s in surfaces):.2f}:1 on "
                       f"the site's surfaces — darkened to {out} for AA")

    dark = t["--dark"]
    t["--on-dark-str"] = "#FFFFFF"
    t["--on-dark-3"] = toward_contrast(muted, [dark], 4.5)
    # Body copy on the dark band is translucent by design (it sits over
    # photography as often as over flat colour), so the ratio has to be checked
    # on the composited result, not on the source colour.
    light = from_lch(max(to_lch(bg)[0], 0.95), min(to_lch(bg)[1], 0.02), to_lch(bg)[2])
    alpha = 0.78
    while alpha <= 1.0 and contrast(composite(light, alpha, dark), dark) < 4.5:
        alpha = round(alpha + 0.02, 2)
    t["--on-dark"] = rgba(light, min(alpha, 1.0))
    t["--dark-line"] = "rgba(255, 255, 255, .14)"
    t["--on-dark-card"] = "rgba(255, 255, 255, .06)"

    # ── identity + category families ──────────────────────────────────────
    aL, aC, aH = to_lch(accent)
    # Navy is the logo colour, not the interface accent — in the native kit the
    # two are deliberately close and do different jobs. Deriving it from --fg
    # keeps that relationship; deriving it from --accent would make the mark
    # change colour whenever the CTA does.
    fL, fC, fH = to_lch(fg)
    t["--navy"] = from_lch(0.32, max(min(fC * 2.2, 0.09), 0.03), fH)
    if aC < 0.03:
        say.append(f"--accent {accent} is effectively neutral (chroma {aC:.3f}) — the "
                   "three category pastels would be indistinguishable greys, so "
                   "fixed teal/amber/violet hues are used at the brand's lightness")
        hues = (168.0, 62.0, 292.0)
        chroma = 0.075
    else:
        hues = tuple((aH + r) % 360 for r in CATEGORY_ROTATION)
        chroma = min(aC, PASTEL_C)

    # The soft tier is a card tint, so it has to sit just off the page surface —
    # NOT at a fixed light value. Hard-coding it light was the single rule that
    # broke every dark brand in the corpus: the deep tier is solved against both
    # the page surfaces and its own soft tint at once, and on a dark brand those
    # two pulled in opposite directions, so no colour could satisfy either.
    bg_l = to_lch(bg)[0]
    soft_l = bg_l - 0.02 if bg_l > 0.5 else bg_l + 0.07
    deep_l = 0.42 if bg_l > 0.5 else 0.88

    families = (("--mint", "--mint-dp", "--mint-sf"),
                ("--apricot", "--apr-dp", "--apr-sf"),
                ("--lilac", "--lil-dp", "--lil-sf"))
    for (base, deep, soft), hue in zip(families, hues):
        t[base] = from_lch(PASTEL_L, chroma, hue)
        t[soft] = from_lch(_clamp(soft_l, 0.05, 0.985), min(chroma, SOFT_C), hue)
        # The deep tier does two jobs — an eyebrow on its own soft tint, and link
        # text on every page surface — so it is solved against all of them at once.
        t[deep] = toward_contrast(from_lch(deep_l, min(aC, 0.13), hue),
                                  surfaces + [t[soft]], 4.5)

    # The primary button is a filled pastel with text on it; that pairing is a
    # third job the deep tier cannot always satisfy, so it gets its own token.
    t["--mint-on"] = (t["--mint-dp"] if contrast(t["--mint-dp"], t["--mint"]) >= 4.5
                      else toward_contrast(t["--mint-dp"], [t["--mint"]], 4.5))

    # Star glyphs. 3:1 is the correct bar — they are 18px+ non-text graphics.
    t["--gold"] = toward_contrast(from_lch(0.62, 0.115, GOLD_HUE), surfaces, 3.0)

    # ── lines, elevation, geometry ────────────────────────────────────────
    t["--line"] = rgba(border_soft, 0.55) if _is_flat(canon, "--border-soft") else border_soft
    t["--line-2"] = rgba(border, 0.7) if _is_flat(canon, "--border") else border
    t["--shadow"] = _flatten_vars(canon.get("--elev-raised", "none"), canon)
    t["--r"] = str(canon.get("--radius-lg", "16px")).strip()
    t["--r-sm"] = str(canon.get("--radius-sm", "8px")).strip()
    t["--r-pill"] = str(canon.get("--radius-pill", "999px")).strip()
    t["--unit"] = str(canon.get("--space-1", "4px")).strip()
    lo = _px(canon.get("--section-y-phone", "64px"), 64)
    hi = _px(canon.get("--section-y-desktop", "128px"), 128)
    t["--band-pad"] = f"clamp({lo:g}px, 9vw, {hi:g}px)"
    t["--wrap"] = str(canon.get("--container-max", "1180px")).strip()

    # ── type ──────────────────────────────────────────────────────────────
    fonts = {}
    for site_name, canon_name, role in (("--display", "--font-display", "sans"),
                                        ("--body", "--font-body", "sans"),
                                        ("--mono", "--font-mono", "mono")):
        r = wf.resolve(str(canon.get(canon_name, "")), role=role)
        t[site_name] = r["stack"]
        fonts[site_name] = r
        if r["status"] in ("substitute", "unmatched"):
            say.append(f"{canon_name}: {r['note']}")

    # Fluid type: the corpus states one fixed size per step, but this site's
    # headings are clamps. Keeping the brand's size as the ceiling and scaling
    # the floor preserves both the brand's scale and the site's responsiveness.
    hero = _px(canon.get("--text-4xl", "76px"), 76)
    h2 = _px(canon.get("--text-3xl", "46px"), 46)
    t["--t-hero"] = f"clamp({hero * 0.55:.0f}px, 6.5vw, {hero:g}px)"
    t["--t-h2"] = f"clamp({h2 * 0.65:.0f}px, 4.2vw, {h2:g}px)"
    t["--t-h3"] = f"clamp({h2 * 0.61:.0f}px, 3.6vw, {h2 * 0.91:.0f}px)"
    t["--t-card"] = str(canon.get("--text-lg", "20px")).strip()
    t["--t-body"] = str(canon.get("--text-base", "16px")).strip()
    t["--t-small"] = str(canon.get("--text-sm", "14.5px")).strip()
    t["--t-eyebrow"] = str(canon.get("--text-xs", "12px")).strip()

    # ── component tokens ──────────────────────────────────────────────────
    # The booking band is a full-bleed fill of --mint carrying a heading and a
    # paragraph. Both need AA against that fill, which the ink ramp cannot give.
    t["--booking-ink"] = toward_contrast(t["--mint-dp"], [t["--mint"]], 7.0)
    t["--booking-ink-2"] = toward_contrast(t["--mint-dp"], [t["--mint"]], 4.5)
    t["--booking-line"] = rgba(t["--booking-ink"], 0.25)
    t["--header-scrim"] = rgba(t["--ground"], 0.88)
    t["--crumb-line"] = rgba(t["--ink"], 0.07)
    t["--dock-scrim"] = rgba(t["--paper"], 0.92)
    t["--photo-label"] = "rgba(255, 255, 255, .88)"

    return t, say


def _is_flat(canon: dict[str, str], name: str) -> bool:
    """True when a border token is an opaque colour rather than an alpha overlay.

    Borders in the corpus come both ways. An opaque `#e5edf5` looks right on the
    surface it was picked against and wrong on the other two; re-expressing it
    as alpha over whatever is behind keeps it quiet on all three.
    """
    return bool(re.fullmatch(r"\s*#[0-9a-fA-F]{3,8}\s*", str(canon.get(name, ""))))


def _flatten_vars(value: str, canon: dict[str, str]) -> str:
    """Rewrite var(--canonical) inside a passed-through value to its literal.

    Shadow tokens routinely reference `var(--border)` or `var(--fg)`. Those names
    do not exist in the emitted site vocabulary, so leaving them in produces a
    shadow that silently disappears.
    """
    def sub(m):
        return resolve_colour(m.group(1), canon) or m.group(0)
    return re.sub(r"var\(\s*(--[\w-]+)\s*\)", sub, str(value)).strip()


# ═════════════════════════════════════════════════════════════════════════════
# Emit
# ═════════════════════════════════════════════════════════════════════════════
ORDER = [
    ("surfaces", ["--ground", "--paper", "--tint", "--dark"]),
    ("ink", ["--ink", "--ink-2", "--ink-3", "--on-dark", "--on-dark-str",
             "--on-dark-3", "--dark-line", "--on-dark-card"]),
    ("identity", ["--navy"]),
    ("accents", ["--mint", "--mint-dp", "--mint-sf", "--mint-on",
                 "--apricot", "--apr-dp", "--apr-sf",
                 "--lilac", "--lil-dp", "--lil-sf", "--gold"]),
    ("lines and elevation", ["--line", "--line-2", "--shadow"]),
    ("geometry", ["--r", "--r-sm", "--r-pill", "--unit", "--band-pad", "--wrap"]),
    ("type", ["--display", "--body", "--mono", "--t-hero", "--t-h2", "--t-h3",
              "--t-card", "--t-body", "--t-small", "--t-eyebrow"]),
    ("components", ["--booking-ink", "--booking-ink-2", "--booking-line",
                    "--header-scrim", "--crumb-line", "--dock-scrim",
                    "--photo-label"]),
]


def emit(system_id: str, canon: dict[str, str], site: dict[str, str],
         say: list[str], fonts: dict) -> str:
    face_css = "\n".join(wf.face_css(f["family"]) for f in fonts.values()
                         if f.get("cached")) or ""
    lines = [
        "/* GENERATED by site/brandkit.py — do not hand-edit.",
        f" * Brand: {system_id}   (agent-data/design-systems/{system_id}/)",
        " *",
        " * Loaded AFTER design-system.css and site.css so this :root wins. The",
        " * canonical block is kept because passed-through values (shadows, rings)",
        " * may still reference it, and because it documents what was mapped from",
        " * what. Regenerate with `python site/brandkit.py apply " + system_id + "`.",
        " *",
        " * Derivation notes:",
    ] + [f" *   - {n}" for n in (say or ["(nothing needed adjusting)"])] + [" */", ""]

    if face_css:
        lines += ["/* webfonts: openly licensed, cached under agent-data/fonts/ */",
                  face_css, ""]

    lines.append("/* ---- the brand, in the corpus vocabulary ---- */")
    lines.append(":root {")
    for spec in ds.TOKEN_SCHEMA:
        n = spec["name"]
        if n in canon:
            lines.append(f"  {n}: {str(canon[n]).strip()};")
    lines += ["}", ""]

    lines.append("/* ---- this site's vocabulary, derived from the above ---- */")
    lines.append(":root {")
    for group, names in ORDER:
        lines.append(f"  /* {group} */")
        for n in names:
            if n in site:
                lines.append(f"  {n}: {site[n]};")
    lines.append("}")
    return "\n".join(lines) + "\n"


# ═════════════════════════════════════════════════════════════════════════════
# Reporting
# ═════════════════════════════════════════════════════════════════════════════
# Same pairings the build gates on, restated here so `show` can report a brand's
# accessibility before it is applied rather than after the build refuses it.
PAIRS = [
    ("body copy on page", "--ink-2", "--ground", 16, 400),
    ("body copy on cards", "--ink-2", "--paper", 15, 400),
    ("body copy on tint", "--ink-2", "--tint", 16, 400),
    ("eyebrow / table head", "--ink-3", "--ground", 12, 600),
    ("eyebrow on cards", "--ink-3", "--paper", 12, 600),
    ("eyebrow on tint", "--ink-3", "--tint", 12, 600),
    ("headings", "--ink", "--ground", 32, 700),
    ("footer headings", "--on-dark-3", "--dark", 11.5, 600),
    ("primary button label", "--mint-on", "--mint", 15.5, 600),
    ("booking heading", "--booking-ink", "--mint", 32, 600),
    ("booking body", "--booking-ink-2", "--mint", 16, 400),
    ("accent text on soft mint", "--mint-dp", "--mint-sf", 15, 500),
    ("accent text on soft apricot", "--apr-dp", "--apr-sf", 15, 500),
    ("accent text on soft lilac", "--lil-dp", "--lil-sf", 15, 500),
    ("star glyphs", "--gold", "--ground", 18, 400),
]


def audit(site: dict[str, str]) -> list[tuple[str, str, float, float, bool]]:
    out = []
    for label, fg, bg, size, weight in PAIRS:
        a, b = site.get(fg), site.get(bg)
        if not a or not b or not a.startswith("#") or not b.startswith("#"):
            continue
        ratio = contrast(a, b)
        large = size >= 24 or (size >= 18.66 and weight >= 700)
        need = 3.0 if (large or label == "star glyphs") else 4.5
        out.append((label, f"{fg} on {bg}", ratio, need, ratio >= need))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# Commands
# ═════════════════════════════════════════════════════════════════════════════
def active() -> str:
    if BRAND_STATE.exists():
        return json.loads(BRAND_STATE.read_text(encoding="utf-8")).get("brand", "native")
    return "native"


def build_for(system_id: str):
    canon, notes = load_brand(system_id)
    site, say = derive(canon)
    fonts = {k: wf.resolve(str(canon.get(v, "")), role=r)
             for k, v, r in (("--display", "--font-display", "sans"),
                             ("--body", "--font-body", "sans"),
                             ("--mono", "--font-mono", "mono"))}
    return canon, site, notes + say, fonts


def cmd_list(args):
    systems = ds.list_systems()
    print(f"active brand: {active()}\n")
    print(f"  native{'':24s}the hand-tuned kit in design-system/kit/ (default)")
    for s in systems:
        blurb = (s.get("blurb") or s.get("name") or "")[:64]
        print(f"  {s['id']:30s}{blurb}")
    print(f"\n{len(systems)} corpus brands + native. "
          "`show <id>` before `apply <id>` — show reports contrast without writing.")
    return 0


def cmd_show(args):
    canon, site, say, fonts = build_for(args.system)
    print(f"BRAND  {args.system}\n")
    for group, names in ORDER:
        print(f"  {group}")
        for n in names:
            if n in site:
                print(f"    {n:16s} {site[n]}")
    print("\n  fonts")
    for k, r in fonts.items():
        print(f"    {k:10s} {r['status']:10s} {r['family']}"
              f"{'' if r['cached'] else '  (NOT CACHED — run webfonts.py fetch)'}")
    print("\n  contrast (WCAG 2.1 AA)")
    bad = 0
    for label, pair, ratio, need, ok in audit(site):
        flag = "ok  " if ok else "FAIL"
        bad += 0 if ok else 1
        print(f"    {flag} {ratio:5.2f}:1 (needs {need})  {label:28s} {pair}")
    print(f"\n  {bad} contrast failure(s)")
    if say:
        print("\n  derivation notes")
        for n in say:
            print(f"    - {n}")
    return 0


def cmd_apply(args):
    if args.native:
        BRAND_CSS.unlink(missing_ok=True)
        BRAND_STATE.unlink(missing_ok=True)
        # The staged fonts are copies of the cache under agent-data/fonts/ and
        # belong to the brand that asked for them. Leaving them behind makes the
        # next build ship a typeface no stylesheet references.
        shutil.rmtree(FONT_DIR, ignore_errors=True)
        print("brand reset to native — assets/brand.css and staged fonts removed.")
        print("Rebuild with `python build.py` to see it.")
        return 0

    canon, site, say, fonts = build_for(args.system)
    failures = [a for a in audit(site) if not a[4]]
    if failures and not args.force:
        print(f"NOT APPLIED — {args.system} fails {len(failures)} contrast pairing(s):\n")
        for label, pair, ratio, need, _ in failures:
            print(f"  · {label}: {pair} is {ratio:.2f}:1, needs {need}")
        print("\nThe derivation already walked these colours as far as their hue "
              "allows.\nUse --force to write anyway (the build will still refuse "
              "it), or pick\nanother brand.")
        return 1

    BRAND_CSS.parent.mkdir(parents=True, exist_ok=True)
    BRAND_CSS.write_text(emit(args.system, canon, site, say, fonts), encoding="utf-8")

    copied = []
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for r in fonts.values():
        if r.get("cached"):
            copied += wf.copy_faces(r["family"], str(FONT_DIR))
    # The build cannot infer these from the stylesheet without parsing it, and
    # two things outside the token system depend on them: which cut of the logo
    # stays legible, and the theme-color the browser paints its own chrome with.
    BRAND_STATE.write_text(json.dumps({
        "brand": args.system,
        "page_is_dark": luminance(site["--ground"]) < 0.18,
        "theme_color": site["--ground"],
        "fonts": {k: {"family": v["family"], "status": v["status"]}
                  for k, v in fonts.items()},
        "font_files": copied,
    }, indent=2), encoding="utf-8")

    print(f"applied {args.system} -> assets/brand.css")
    print(f"  {len(site)} site tokens derived, all {len(audit(site))} contrast "
          "pairings pass")
    if copied:
        print(f"  {len(copied)} webfont file(s) staged in assets/fonts/")
    for r in fonts.values():
        if r["status"] == "substitute":
            print(f"  font: {r['note']}")
        elif r["status"] == "unmatched":
            print(f"  font: WARNING — {r['note']}")
    print("\nNext: python build.py  (then verify.py --all)")
    return 0


def cmd_calibrate(args):
    """Do the derivation rules reproduce a palette a designer actually chose?

    Feeding the native kit's own canonical tokens through the same derivation
    the corpus brands go through, then diffing against the hand-tuned values, is
    the only test that can tell "the rules are sound" from "the rules produce
    something plausible-looking".
    """
    kit = {k: v["value"] for k, v in ds.parse_root_tokens(
        KIT.read_text(encoding="utf-8")).items()}
    site, say = derive(native_canonical())

    print("CALIBRATION — derived from the native kit's own canonical tokens,\n"
          "compared with the values a designer hand-tuned.\n")
    print(f"  {'token':16s} {'hand-tuned':12s} {'derived':12s}  ΔE(ok)  note")
    worst = []
    for group, names in ORDER:
        for n in names:
            want, got = kit.get(n), site.get(n)
            if not want or not got:
                continue
            if want.strip().startswith("#") and got.startswith("#"):
                la, lb = rgb_to_oklab(hex_to_rgb(want.strip())), rgb_to_oklab(hex_to_rgb(got))
                de = math.dist(la, lb)
                worst.append((de, n))
                mark = "same" if de < 0.02 else "close" if de < 0.06 else "DIVERGES"
                print(f"  {n:16s} {want.strip():12s} {got:12s}  {de:.3f}   {mark}")
    worst.sort(reverse=True)
    print(f"\n  {sum(1 for d, _ in worst if d < 0.06)}/{len(worst)} colours within "
          "perceptual tolerance of the hand-tuned value")
    print("  largest divergences: " + ", ".join(f"{n} ({d:.2f})" for d, n in worst[:5]))
    bad = [a for a in audit(site) if not a[4]]
    print(f"  contrast: {len(audit(site)) - len(bad)}/{len(audit(site))} pairings pass")
    for label, pair, ratio, need, _ in bad:
        print(f"    FAIL {label}: {pair} {ratio:.2f}:1 needs {need}")
    return 0


def cmd_check(args):
    """Every var() the site's CSS reads must be defined by the active brand.

    This is the gate that would have caught "build this like Stripe renders a
    grey page": an undefined custom property is not an error in CSS, it drops
    the declaration that used it and says nothing.
    """
    sources = [ROOT / "assets" / "site.css", KIT, ROOT / "chrome.py"]
    defined: set[str] = set()
    for f in [KIT, ROOT / "assets" / "site.css", BRAND_CSS]:
        if f.exists():
            text = re.sub(r"base64,[A-Za-z0-9+/=]+", "base64,B",
                          f.read_text(encoding="utf-8"))
            defined |= {m.group(1) for m in re.finditer(r"(--[\w-]+)\s*:\s*[^;{}]+;", text)}

    used: dict[str, list[str]] = {}
    for f in sources:
        if not f.exists():
            continue
        text = re.sub(r"base64,[A-Za-z0-9+/=]+", "base64,B",
                      f.read_text(encoding="utf-8"))
        for m in re.finditer(r"var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)", text):
            used.setdefault(m.group(1), []).append(f.name)

    missing = {k: v for k, v in used.items() if k not in defined}
    print(f"active brand: {active()}")
    print(f"  {len(defined)} tokens defined, {len(used)} referenced")
    if missing:
        print(f"\nUNRESOLVED — {len(missing)} token(s) referenced but never defined:")
        for k, where in sorted(missing.items()):
            print(f"  · {k}  (used in {', '.join(sorted(set(where)))})")
        print("\nEach of these silently drops the declaration that reads it.")
        return 1
    unused = sorted(defined - set(used) - {"--tw-ring-color"})
    print("  all references resolve")
    if unused and args.verbose:
        print(f"  {len(unused)} defined but unused: {', '.join(unused)}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(fn=cmd_list)

    p = sub.add_parser("show", help="derived palette + contrast, without writing")
    p.add_argument("system")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("apply", help="write assets/brand.css and activate")
    p.add_argument("system", nargs="?")
    p.add_argument("--native", action="store_true", help="restore the hand-tuned kit")
    p.add_argument("--force", action="store_true", help="write despite contrast failures")
    p.set_defaults(fn=cmd_apply)

    sub.add_parser("calibrate").set_defaults(fn=cmd_calibrate)

    p = sub.add_parser("check", help="every var() the site uses resolves")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(fn=cmd_check)

    args = ap.parse_args(argv)
    if args.cmd == "apply" and not args.system and not args.native:
        ap.error("apply needs a system id, or --native")
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
