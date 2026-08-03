"""Screenshot a built page at a TRUE viewport width, for eyeballing diagrams.

WHY THIS EXISTS
  Chrome on Windows refuses to open a window narrower than ~500px, so
  `--headless --window-size=390,…` silently lays the page out at ~512px and
  crops the screenshot to 390. Everything then looks subtly wrong — labels land
  in the wrong place, the artwork appears to overflow — and the bug is in the
  screenshot, not the page. `verify.py` already solves this by measuring inside
  an iframe of the exact width; this borrows the same trick for pictures.

    python diagram_shot.py vitiligo 390
    python diagram_shot.py hair-loss-treatment-hyderabad 1440 --out shot.png
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tempfile

SITE = pathlib.Path(__file__).resolve().parent
DIST = SITE / "dist"

HARNESS = """<!doctype html><meta charset="utf-8">
<body style="margin:0;background:#fff">
<iframe src="PAGE" style="width:WIDTHpx;height:HEIGHTpx;border:0;display:block">
</iframe>
"""


def chrome() -> str:
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "google-chrome", "chromium"):
        if pathlib.Path(c).exists() or "/" not in c and "\\" not in c:
            return c
    sys.exit("Chrome not found")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("width", type=int)
    ap.add_argument("--height", type=int, default=5200)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    page = DIST / f"{args.slug}.html"
    if not page.exists():
        sys.exit(f"no such page: {page}")

    tmp = pathlib.Path(tempfile.mkdtemp()) / "harness.html"
    tmp.write_text(
        HARNESS.replace("PAGE", page.resolve().as_uri())
               .replace("WIDTH", str(args.width))
               .replace("HEIGHT", str(args.height)),
        encoding="utf-8")

    out = pathlib.Path(args.out or (SITE / ".diagram-queue" /
                                    f"shot-{args.slug}-{args.width}.png"))
    out.parent.mkdir(parents=True, exist_ok=True)

    # The window must be wider than Chrome's ~500px floor; the iframe inside it
    # is the real viewport, and the extra is cropped off by taking the left
    # `width` pixels.
    subprocess.run([
        chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--allow-file-access-from-files", "--virtual-time-budget=20000",
        f"--window-size={max(args.width, 560)},{args.height}",
        f"--screenshot={out}", tmp.resolve().as_uri(),
    ], check=False, capture_output=True)

    if not out.exists():
        sys.exit("chrome produced no screenshot")

    from PIL import Image
    im = Image.open(out)
    if im.width > args.width:
        im.crop((0, 0, args.width, im.height)).save(out)
        im = Image.open(out)
    print(f"{out}  {im.width}x{im.height}  (true {args.width}px viewport)")


if __name__ == "__main__":
    main()
