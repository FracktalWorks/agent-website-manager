"""Overlay a percentage grid on a diagram so label coordinates can be READ.

WHY THIS EXISTS
  Label positions are percentages of the image box, and estimating them by eye
  off a review montage went wrong twice on this site — once ~15% low in `y`,
  then uniformly **1.45x too small in `x`**, because the pixel positions were
  read from a downscaled preview while the grid numbers had been burned in at
  full size. Both passes had to be redone.

  The fix is to never do arithmetic on a screenshot. This draws the grid AND
  its numbers into the image at one scale, so whatever size the result is
  viewed at, the number beside a structure IS that structure's coordinate.

  Emits one sheet per artwork rather than a montage, for the same reason: a
  montage forces a downscale, and a downscale is what caused the error.

USAGE
  python diagram_grid.py B3 B4 D12          # by id, or by filename stem
  python diagram_grid.py --batch 3          # every artwork in a batch file
  -> .diagram-queue/grid/<name>.png
"""
import argparse
import json
import pathlib
import sys

from PIL import Image, ImageDraw

ASSETS = pathlib.Path("assets/img/diagrams")
QUEUE = pathlib.Path(".diagram-queue")
OUT = QUEUE / "grid"

STEP = 10          # percent between labelled lines
MINOR = 5          # percent between faint lines
WIDTH = 1400       # the sheet is rendered once, at this width, and not resized


def sheet(src: pathlib.Path) -> pathlib.Path:
    im = Image.open(src).convert("RGB")
    w0, h0 = im.size
    w = WIDTH
    h = round(h0 * w / w0)
    im = im.resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")

    for p in range(MINOR, 100, MINOR):
        x, y = round(w * p / 100), round(h * p / 100)
        major = p % STEP == 0
        ink = (18, 32, 47, 90 if major else 38)
        d.line([(x, 0), (x, h)], fill=ink, width=1)
        d.line([(0, y), (w, y)], fill=ink, width=1)

    # Numbers go in at the SAME scale as the grid — that is the whole point.
    for p in range(STEP, 100, STEP):
        x, y = round(w * p / 100), round(h * p / 100)
        for tx, ty, txt in ((x + 3, 3, str(p)), (3, y + 2, str(p))):
            d.rectangle([tx - 2, ty - 1, tx + 22, ty + 13], fill=(255, 255, 255, 205))
            d.text((tx, ty), txt, fill=(18, 32, 47))

    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{src.stem}.png"
    im.save(dst)
    return dst


def resolve(tokens):
    """Accept ids (`B3`), stems (`B3-vitiligo-patterns`), or paths."""
    found = []
    for t in tokens:
        p = pathlib.Path(t)
        if p.exists():
            found.append(p)
            continue
        hits = sorted(ASSETS.glob(f"{t}-*.webp")) or sorted(ASSETS.glob(f"{t}.webp"))
        if not hits:
            print(f"  !! no artwork matches {t!r}")
            continue
        found += hits
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--batch", type=int, help="every artwork in batch-NN.json")
    args = ap.parse_args()

    tokens = list(args.ids)
    if args.batch:
        b = json.loads((QUEUE / f"batch-{args.batch:02d}.json").read_text(encoding="utf-8"))
        tokens += [i["target_file"].removesuffix(".webp") for i in b["items"]]
    if not tokens:
        ap.error("give some ids or --batch N")

    n = 0
    for src in resolve(tokens):
        print(f"  {sheet(src)}")
        n += 1
    print(f"\n{n} grid sheet(s) at {WIDTH}px — read the burned-in numbers, "
          f"never pixel offsets")
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main())
