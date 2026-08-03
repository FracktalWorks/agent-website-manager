#!/usr/bin/env python
"""Draw every label's ring onto its own artwork, for reviewing WHERE they point.

    python diagram_review.py                # every distinct placement
    python diagram_review.py C3 B5          # just these artworks
    -> .diagram-queue/review/<artwork>--<slug>.png

WHY THIS IS A SEPARATE TOOL FROM `diagram_audit.py`
  The audit proves a ring renders at the coordinate it was given. It cannot
  prove the coordinate was right. Those are different failures and only one of
  them is mechanical: a ring can sit at exactly (38%, 19%) in every browser at
  every width and still be pointing at empty background six percent above the
  structure it names. That is what happened to "Active scaly border" on
  `C3-fungal-infection`, and no amount of measuring the DOM would have found
  it — it needed someone to look.

  So this draws the rings straight onto the artwork at full size and leaves the
  looking to a human (or to a model that can see). No browser, no page, no
  downscale.

WHY IT DRAWS AT FULL SIZE
  Reading coordinates off a downscaled montage is what produced this site's two
  worst label passes — one 15% low in `y`, one uniformly 1.45x wrong in `x`.
  Nothing here is measured from the output: the sheets are for spotting a ring
  in the wrong place, and `diagram_grid.py` is for reading the right one.

DEDUPLICATION
  Sixty-six placements use forty-four artworks, and most of the repeats are the
  same coordinates on a translated page — one sheet covers all of them. A
  placement is re-emitted only when its coordinates differ.
"""

from __future__ import annotations

import argparse
import importlib
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

import siteconf

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ASSETS = pathlib.Path("assets/img/diagrams")
OUT = pathlib.Path(".diagram-queue/review")

RING_R = 26         # px radius of the drawn ring, at full artwork size
RING_W = 5
CROSS = 16          # px arms of the centre cross — the ring alone hides its own point
BAR = 132           # px of caption strip under the artwork


def font(size):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def placements():
    """Every distinct (artwork, coordinates) pair actually rendered on the site."""
    seen, out = set(), []
    for name in siteconf.MODULES:
        for page in importlib.import_module(f"content.{name}").PAGES:
            for sec in page.get("sections") or []:
                if sec.get("kind") != "diagram" or not sec.get("image"):
                    continue
                labels = sec.get("labels") or []
                src = sec["image"]["src"].split("/")[-1]
                key = (src, tuple((lab["x"], lab["y"]) for lab in labels))
                if key in seen:
                    continue
                seen.add(key)
                out.append((src, page["slug"], bool(sec.get("rail")), labels))
    return out


def sheet(src, slug, rail, labels):
    art = ASSETS / src
    if not art.exists():
        return None
    im = Image.open(art).convert("RGB")
    w, h = im.size
    canvas = Image.new("RGB", (w, h + BAR), "white")
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas)
    big, small = font(40), font(30)

    for n, lab in enumerate(labels, 1):
        cx, cy = w * lab["x"] / 100, h * lab["y"] / 100
        # Magenta appears nowhere in this artwork palette, so a ring in the
        # wrong place cannot be mistaken for part of the drawing.
        d.ellipse([cx - RING_R, cy - RING_R, cx + RING_R, cy + RING_R],
                  outline=(230, 0, 140), width=RING_W)
        d.line([cx - CROSS, cy, cx + CROSS, cy], fill=(230, 0, 140), width=3)
        d.line([cx, cy - CROSS, cx, cy + CROSS], fill=(230, 0, 140), width=3)
        d.text((cx + RING_R + 8, cy - 22), str(n), font=big, fill=(230, 0, 140),
               stroke_width=5, stroke_fill="white")

    d.text((22, h + 14), f"{src}   ·   {slug}   ·   {'RAIL' if rail else 'PIN'}",
           font=small, fill=(20, 20, 20))
    key = "   ".join(f"{n}. {lab['text']}  ({lab['x']},{lab['y']})"
                     for n, lab in enumerate(labels, 1))
    d.text((22, h + 58), key[:200], font=small, fill=(70, 70, 70))
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="artwork ids or filename stems")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for src, slug, rail, labels in placements():
        stem = src.replace(".webp", "")
        if args.ids and not any(stem == i or stem.startswith(i + "-")
                                for i in args.ids):
            continue
        img = sheet(src, slug, rail, labels)
        if img is None:
            print(f"  missing artwork: {src}")
            continue
        path = OUT / f"{stem}--{slug}.png"
        img.save(path)
        made += 1
        print(f"  {path}  ({len(labels)} labels)")
    print(f"\n{made} sheet(s) in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
