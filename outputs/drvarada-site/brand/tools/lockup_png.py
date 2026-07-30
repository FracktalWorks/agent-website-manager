"""Raster exports of the lockups, for the places that cannot take an SVG:
email signatures, Word and PowerPoint, WhatsApp, print-shop submissions.

Sizes come from the artwork's own aspect ratio, so nothing is ever stretched.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import raster                                          # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCKUPS = ROOT / "lockups"
OUT = LOCKUPS / "png"
OUT.mkdir(exist_ok=True)

# (svg, target width in px, background)
JOBS = [
    ("logo-horizontal-light.svg", 1600, "transparent"),
    ("logo-horizontal-tagline-light.svg", 1600, "transparent"),
    ("logo-horizontal-tagline-dark.svg", 1600, "#1E3A63"),
    ("logo-stacked-tagline-light.svg", 1200, "transparent"),
    ("logo-stacked-tagline-dark.svg", 1200, "#1E3A63"),
    ("logo-wordmark-tagline-light.svg", 1600, "transparent"),
]


def aspect(svg_path):
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',
                   svg_path.read_text(encoding="utf-8"))
    return float(vb.group(1)), float(vb.group(2))


def main():
    for name, width, bg in JOBS:
        src = LOCKUPS / name
        w, h = aspect(src)
        px_h = round(width * h / w)
        out = OUT / f"{name[:-4]}-{width}.png"
        raster.shot_box(src, width, px_h, out, bg)
        print(f"  {out.name:46} {width} x {px_h}")


if __name__ == "__main__":
    main()
