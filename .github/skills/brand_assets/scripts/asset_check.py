#!/usr/bin/env python
"""Measure brand assets against a platform's spec, and at the size it shows.

    python asset_check.py <file-or-dir> --spec whatsapp-catalogue
    python asset_check.py brand/google --spec gbp-logo --sheet out.png

Two questions, both answered by measurement rather than by looking at the
1024px file in an image viewer:

  1. Does it meet the platform's stated spec (square, minimum side, format,
     byte ceiling)?
  2. Does it survive the size the platform actually DRAWS it at? A catalogue
     grid draws ~150px, a search result draws a favicon at 16-48px, a profile
     is cropped to a circle. An asset is judged there, not at full size.

The margin measurement uses an ink threshold of sum(RGB) < 450, not the more
obvious < 700. A pale brand wash sums to roughly 670, so the looser threshold
counts the background as ink and reports a confident, wrong "0px margin".
Thresholds that sound safe are the ones that lie.

--sheet writes a contact sheet at the consumption size. That image, not this
table, is the artefact a tile set is signed off on.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from PIL import Image

# side_min, aspect (w/h or None for any), max_bytes, cell drawn at, circle?
SPECS = {
    "whatsapp-catalogue": (500, 1.0, 5_000_000, 150, False),
    "whatsapp-profile":   (192, 1.0, 5_000_000, 64, True),
    "gbp-logo":           (250, 1.0, 5_000_000, 48, True),
    "gbp-cover":          (1024, 16 / 9, 5_000_000, 320, False),
    "og-image":           (600, 1.91, 8_000_000, 300, False),
    "app-icon":           (512, 1.0, 5_000_000, 48, True),
}
INK = 450          # see module docstring
EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def ink_box(im: Image.Image, ignore_bottom: int = 0):
    """Bounding box of real ink, ignoring a bleed rule at the bottom."""
    import numpy as np
    arr = np.asarray(im.convert("RGB")).astype(int)
    if ignore_bottom:
        arr = arr[:-ignore_bottom]
    mask = arr.sum(2) < INK
    if not mask.any():
        return None
    ys, xs = mask.any(1), mask.any(0)
    return (int(xs.argmax()), int(ys.argmax()),
            int(len(xs) - xs[::-1].argmax()), int(len(ys) - ys[::-1].argmax()))


def circle_spill(im: Image.Image) -> float:
    """Fraction of ink outside the inscribed circle a profile crop keeps."""
    import numpy as np
    arr = np.asarray(im.convert("RGB")).astype(int)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = min(h, w) / 2
    outside = ((xx - w / 2) ** 2 + (yy - h / 2) ** 2) > r * r
    mask = arr.sum(2) < INK
    total = mask.sum()
    return float((mask & outside).sum() / total) if total else 0.0


def check(path: pathlib.Path, spec: str, bleed: int) -> tuple[str, str]:
    side_min, aspect, max_bytes, _, circle = SPECS[spec]
    im = Image.open(path)
    w, h = im.size
    nbytes = path.stat().st_size
    bad: list[str] = []
    if aspect and abs((w / h) - aspect) > 0.02:
        bad.append(f"aspect {w / h:.2f} != {aspect:.2f}")
    if min(w, h) < side_min:
        bad.append(f"{min(w, h)}px < {side_min}px minimum")
    if nbytes > max_bytes:
        bad.append(f"{nbytes / 1e6:.1f}MB over {max_bytes / 1e6:.0f}MB")

    box = ink_box(im, bleed)
    note = ""
    if box:
        m = min(box[0], box[1], w - box[2], h - box[3])
        pct = 100 * m / min(w, h)
        note = f"margin {pct:4.1f}%"
        if pct < 3:
            bad.append(f"margin {pct:.1f}% - any surface that trims a few "
                       "percent clips the artwork")
    if circle:
        spill = circle_spill(im)
        note += f"  spill {spill * 100:4.1f}%"
        if spill > 0.005:
            bad.append(f"{spill * 100:.1f}% of the ink falls outside the "
                       "circle crop")
    head = f"{w}x{h}  {nbytes / 1024:5.0f} KB  {note}"
    return ("FAIL  " + "; ".join(bad)) if bad else "OK", head


def sheet(files: list[pathlib.Path], cell: int, out: pathlib.Path) -> None:
    gap, pad = 18, 22
    n = len(files)
    w = pad * 2 + cell * n + gap * (n - 1)
    canvas = Image.new("RGB", (w, cell + pad * 2), (237, 237, 240))
    for i, f in enumerate(files):
        t = Image.open(f).convert("RGB").resize((cell, cell), Image.LANCZOS)
        canvas.paste(t, (pad + i * (cell + gap), pad))
    canvas.save(out)
    print(f"\n  contact sheet at {cell}px -> {out}")
    print("  Look at it. If a line cannot be read there it does not belong\n"
          "  on the tile, and a bigger upload will not fix it.\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--spec", choices=sorted(SPECS), required=True)
    ap.add_argument("--bleed", type=int, default=0,
                    help="px of deliberate edge bleed to exclude from margins")
    ap.add_argument("--sheet", help="write a contact sheet here")
    ap.add_argument("--cell", type=int, default=0,
                    help="override the consumption size for the sheet")
    a = ap.parse_args()

    files: list[pathlib.Path] = []
    for p in a.paths:
        q = pathlib.Path(p)
        files += (sorted(f for f in q.iterdir() if f.suffix.lower() in EXTS)
                  if q.is_dir() else [q])
    files = [f for f in files if not f.name.startswith("preview-")]
    if not files:
        print("no images found")
        return 2

    bad = 0
    width = max(len(f.name) for f in files)
    print()
    for f in files:
        verdict, head = check(f, a.spec, a.bleed)
        bad += verdict != "OK"
        print(f"  {f.name:<{width}}  {head}   {verdict}")

    if a.sheet:
        cell = a.cell or SPECS[a.spec][3]
        pngs = [f for f in files if f.suffix.lower() != ".jpg"] or files
        sheet(pngs, cell, pathlib.Path(a.sheet))
    print(f"  {len(files) - bad}/{len(files)} meet the {a.spec} spec\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
