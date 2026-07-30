# -*- coding: utf-8 -*-
r"""Generate agent-data/design-systems/INDEX.md — the file the agent actually reads.

WHY
  Choosing a design system must not cost 152 folder reads. INDEX.md is the one
  scannable page that makes a choice possible from a brief, so its one-liners have
  to be genuinely DISCRIMINATING. Two sources, deliberately combined:

  1. CHARACTER (human prose). The corpus convention puts a `> ...` blockquote
     right under the H1 of every DESIGN.md — the author's own one-line summary
     ("Payment infrastructure. Signature purple gradients, weight-300 elegance.").
     That beats anything we can compute. `manifest.description` is NOT used: it is
     boilerplate ("Bundled Open Design package for X, derived from curated...").
  2. SIGNATURE (measured). Derived from tokens.css so it cannot drift from the
     binding contract: display-font class + real family, ground lightness and
     temperature, accent hue name, corner radius, container width, section rhythm.
     This is the part that separates two systems whose prose both says "minimal".

  Regenerate after adding/importing a system:
      python .tmp/scripts/build_ds_index.py

Usage:
  python .tmp/scripts/build_ds_index.py            # write INDEX.md
  python .tmp/scripts/build_ds_index.py --stdout    # print, do not write
  python .tmp/scripts/build_ds_index.py --check     # exit 1 if INDEX.md is stale
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_systems as ds  # noqa: E402

INDEX_PATH = os.path.join(ds.CORPUS, "INDEX.md")


# ─────────────────────────────────────────────────────────────────────────────
# Color parsing — just enough to name a hue. Anything exotic returns None so the
# signature degrades gracefully rather than printing a guess.
# ─────────────────────────────────────────────────────────────────────────────
def _resolve(value, declared, depth=0):
    """Follow `var(--x)` one or two hops inside the same :root block."""
    if not value or depth > 2:
        return value
    m = re.fullmatch(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,[^)]*)?\)", value.strip())
    if m and m.group(1) in declared:
        return _resolve(declared[m.group(1)], declared, depth + 1)
    return value


def parse_rgb(value):
    """#rgb / #rrggbb / rgb() / rgba() -> (r, g, b) floats 0-1, else None."""
    if not value:
        return None
    v = value.strip().lower()
    m = re.match(r"^#([0-9a-f]{3,8})\b", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h[:3])
        elif len(h) in (6, 8):
            h = h[:6]
        else:
            return None
        return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    m = re.match(r"^rgba?\(\s*([0-9.]+)[,\s]+([0-9.]+)[,\s]+([0-9.]+)", v)
    if m:
        return tuple(min(1.0, float(m.group(i)) / 255.0) for i in (1, 2, 3))
    return None


def _hsl(rgb):
    r, g, b = rgb
    mx, mn = max(rgb), min(rgb)
    light = (mx + mn) / 2.0
    if mx == mn:
        return 0.0, 0.0, light
    d = mx - mn
    sat = d / (2.0 - mx - mn) if light > 0.5 else d / (mx + mn)
    if mx == r:
        hue = ((g - b) / d) % 6
    elif mx == g:
        hue = (b - r) / d + 2
    else:
        hue = (r - g) / d + 4
    return hue * 60.0, sat, light


# Practical hue names — chosen so two systems that both say "warm accent" still
# read differently ("terracotta" vs "amber" vs "crimson").
_HUE_NAMES = [
    (14, "red"), (28, "terracotta"), (40, "orange"), (52, "amber"), (66, "gold"),
    (90, "lime"), (150, "green"), (175, "teal"), (200, "cyan"), (225, "azure"),
    (255, "blue"), (275, "indigo"), (295, "violet"), (320, "purple"),
    (342, "magenta"), (360, "crimson"),
]


def hue_name(value, declared):
    rgb = parse_rgb(_resolve(value, declared))
    if rgb is None:
        return None
    hue, sat, light = _hsl(rgb)
    if sat < 0.10:
        return "black" if light < 0.2 else ("white" if light > 0.85 else "grey")
    # A light, saturated red reads as coral, not "red"/"crimson" — the distinction
    # matters because half the corpus's warm accents sit in that narrow band.
    if (hue < 20 or hue >= 345) and light > 0.58:
        return "coral"
    for edge, name in _HUE_NAMES:
        if hue < edge:
            return name
    return "red"


def ground_words(value, declared):
    """(lightness, temperature) for the page canvas, e.g. ("light", "warm")."""
    rgb = parse_rgb(_resolve(value, declared))
    if rgb is None:
        return None, None
    hue, sat, light = _hsl(rgb)
    lightness = "light" if light >= 0.72 else ("dark" if light <= 0.28 else "mid")
    if sat < 0.045:
        temp = "neutral"
    elif hue < 95 or hue >= 320:
        temp = "warm"
    elif hue < 150:
        temp = "green"
    elif hue < 265:
        temp = "cool"
    else:
        temp = "violet"
    return lightness, temp


# ─────────────────────────────────────────────────────────────────────────────
# Typography + rhythm
# ─────────────────────────────────────────────────────────────────────────────
def font_words(stack):
    """(class, first family) from a font stack.

    The GENERIC tail is authoritative: `"Anthropic Serif", Georgia, serif` ends in
    `serif`, so we do not have to recognize the proprietary family name at all.
    """
    if not stack:
        return None, None
    families = [f.strip().strip('"\'') for f in stack.split(",") if f.strip()]
    first = families[0] if families else None
    tail = " ".join(families).lower()
    if "monospace" in tail or "mono" in (first or "").lower():
        cls = "mono"
    elif "sans-serif" in tail or "sans" in tail.replace("sans-serif", ""):
        cls = "sans"
    elif re.search(r"\bserif\b", tail):
        cls = "serif"
    elif "cursive" in tail:
        cls = "script"
    else:
        cls = None
    # A family literally named "... Serif"/"... Sans" beats an omitted generic tail.
    low = (first or "").lower()
    if "serif" in low and "sans" not in low:
        cls = "serif"
    elif "sans" in low or "grotesk" in low or "grotesque" in low:
        cls = "sans"
    return cls, first


def _px(value):
    """px / rem / em / unitless-0 -> px float. Unitless non-zero is not CSS-legal
    for a length, so it is rejected rather than guessed. `--radius-md: 0` is real
    and common (BMW, brutalism) — losing it would drop the sharpest signal there is.
    """
    if not value:
        return None
    v = value.strip()
    m = re.match(r"^(-?[0-9.]+)\s*(px|rem|em)?\b", v)
    if not m:
        return None
    n = float(m.group(1))
    unit = m.group(2)
    if unit in ("rem", "em"):
        return n * 16.0
    if unit == "px":
        return n
    return 0.0 if n == 0 else None


def signature(declared):
    """A measured, comparable fingerprint. Empty parts are dropped, never faked."""
    parts = []

    cls, family = font_words(declared.get("--font-display"))
    body_cls, _ = font_words(declared.get("--font-body"))
    if cls or family:
        label = "%s display" % cls if cls else "display"
        if family and family.lower() not in (cls or ""):
            label += " (%s)" % family
        if body_cls and body_cls != cls:
            label += " / %s body" % body_cls
        parts.append(label)

    lightness, temp = ground_words(declared.get("--bg"), declared)
    if lightness:
        parts.append("%s %s ground" % (lightness, temp))

    accent = hue_name(declared.get("--accent"), declared)
    if accent:
        parts.append("%s accent" % accent)

    radius = _px(declared.get("--radius-md"))
    if radius is not None:
        parts.append("sharp corners" if radius <= 2 else
                     ("r%d" % radius if radius < 20 else "r%d (very round)" % radius))

    section = _px(declared.get("--section-y-desktop"))
    if section is not None:
        parts.append("%dpx rhythm%s" % (section,
                                        " (airy)" if section >= 120 else
                                        " (tight)" if section <= 64 else ""))

    container = declared.get("--container-max")
    if container:
        parts.append("max %s" % container.strip())

    return " · ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Rows
# ─────────────────────────────────────────────────────────────────────────────
def _cell(text, limit):
    """Markdown-safe single-line cell."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    text = text.replace("|", "\\|").replace("`", "")
    if len(text) > limit:
        text = text[:limit - 1].rsplit(" ", 1)[0] + "…"
    return text


def character(sid):
    """Prose one-liner: DESIGN.md blockquote > USAGE.md first highlight > 1st para."""
    d = ds.system_dir(sid)
    design_md = ds.read_text(os.path.join(d, "DESIGN.md"))
    _, blurb = ds.design_blurb(design_md)
    if blurb:
        return blurb
    highlights = ds.usage_section(ds.read_text(os.path.join(d, "USAGE.md")), "Design Highlights")
    if highlights:
        bullets = [re.sub(r"^[-*]\s*", "", ln).strip()
                   for ln in highlights.split("\n") if ln.strip().startswith(("-", "*"))]
        if bullets:
            return "; ".join(bullets[:2])
    return ds.design_first_paragraph(design_md) or ""


def build_rows():
    rows = []
    for row in ds.list_systems():
        sid = row["id"]
        declared = ds.parse_root_tokens(ds.read_text(os.path.join(ds.system_dir(sid), "tokens.css")))
        declared = {k: v["value"] for k, v in declared.items()}
        rows.append({
            "id": sid,
            "name": row["name"],
            "category": row["category"] or "—",
            "character": character(sid),
            "signature": signature(declared),
            "legacy": row["legacy"],
            "rich": "usage" in row["files"] and "components" in row["files"],
            "token_count": len(declared),
        })
    return rows


HEADER = """<!-- GENERATED by .tmp/scripts/build_ds_index.py — do not hand-edit. -->
# Design System Index

{count} vendored design systems (see `PROVENANCE.md`). **Pick one from this table,
then load it — never author tokens from scratch when a system already fits.**

```bash
python .tmp/scripts/design_systems.py search "warm editorial serif"   # find
python .tmp/scripts/design_systems.py show <id>                       # inspect
python .tmp/scripts/design_systems.py show <id> --root                # the :root block to paste
python .tmp/scripts/design_systems.py tokens <id>                     # values + missing tiers
python .tmp/scripts/design_systems.py validate <id>                   # contract check
```

**Character** is the package author's own one-line summary (the `>` blockquote
under each `DESIGN.md` H1). **Signature** is *measured* from `tokens.css`, so it
never drifts from the binding contract: display/body font class and real family,
canvas lightness + temperature, accent hue, corner radius, section rhythm,
container width. `L` = legacy `DESIGN.md`-only package (prose only, no token
contract to paste). `R` = rich package (USAGE.md + components.html + preview).

Universal, brand-independent craft rules live in `_craft/` — brand tokens win on
value conflicts; craft covers everything the brand does not override.

## By category

{categories}

## All systems

| | id | name | category | character | signature |
|---|---|------|----------|-----------|-----------|
"""


def render(rows):
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r["id"])
    categories = "\n".join(
        "- **%s** (%d) — %s" % (cat, len(ids), ", ".join(sorted(ids)))
        for cat, ids in sorted(by_cat.items())
    )
    out = [HEADER.format(count=len(rows), categories=categories).rstrip("\n")]
    for r in sorted(rows, key=lambda x: x["id"]):
        flag = "L" if r["legacy"] else ("R" if r["rich"] else "·")
        out.append("| %s | `%s` | %s | %s | %s | %s |" % (
            flag, r["id"], _cell(r["name"], 40), _cell(r["category"], 32),
            _cell(r["character"], 150), _cell(r["signature"], 130)))
    out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    ap.add_argument("--check", action="store_true", help="exit 1 if INDEX.md is stale")
    args = ap.parse_args(argv)

    text = render(build_rows())
    if args.stdout:
        sys.stdout.write(text)
        return 0
    if args.check:
        current = ds.read_text(INDEX_PATH)
        if current == ds._norm_eol(text):
            print("INDEX.md is up to date")
            return 0
        print("INDEX.md is stale — run: python .tmp/scripts/build_ds_index.py")
        return 1
    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    rows = text.count("\n| ")
    print("wrote %s (%d rows)" % (INDEX_PATH, rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
