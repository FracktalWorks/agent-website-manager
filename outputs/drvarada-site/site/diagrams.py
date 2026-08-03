"""Generate the site's illustrative diagrams against OpenAI's image API.

WHY THIS IS A SCRIPT AND NOT AN MCP SERVER
  The work is deterministic: read a staged prompt, POST it, crop the result to
  the aspect ratio the page slot wants, write a WebP into `assets/`. Wrapping
  one HTTP call in an MCP server would cost a process and a tool schema every
  session to buy nothing — the same reasoning that retired the `site-feedback`
  MCP server. Deterministic work belongs in `scripts/`; the model's job is
  writing the prompt and judging the picture, both of which happen elsewhere.

WHY THE CROP EXISTS
  `gpt-image-2` offers square and 3:2 sizes, not 16:9, but the `media wide`
  slot these land in is `aspect-ratio: 16/9` with `object-fit: cover`. Shipping
  a 3:2 file would let the browser crop it — blindly, from the centre, at
  whatever width the viewport happens to be. Cropping here instead means the
  decision is made once, against the actual pixels, and is visible in review.
  The crop is content-aware: it finds the drawn subject and keeps it, rather
  than trusting that the interesting half is the middle.

USAGE
  python diagrams.py gen A2                 # one item from the current batch
  python diagrams.py gen --all              # every unfinished item
  python diagrams.py gen A2 --ref none      # without the style anchor
  python diagrams.py gen A2 --quality high --size 2k
  python diagrams.py list                   # what is queued and what exists

The queue is `.diagram-queue/batch-NN.json`, written by the planning step and
documented in DIAGRAMS.md. Raw API output is kept in `.diagram-queue/out/` so a
rejected generation can be looked at again without paying to remake it.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageChops

SITE = Path(__file__).resolve().parent
REPO = SITE.parents[2]
QUEUE_DIR = SITE / ".diagram-queue"
RAW_DIR = QUEUE_DIR / "out"
ASSETS = SITE / "assets" / "img" / "diagrams"
ANCHOR = ASSETS / "A1-skin-cross-section.webp"

API_GENERATE = "https://api.openai.com/v1/images/generations"
API_EDIT = "https://api.openai.com/v1/images/edits"

# gpt-image-2 takes named sizes, none of which is 16:9. 3:2 landscape is the
# closest and crops down to 16:9 with the least loss.
SIZES = {"1k": "1536x1024", "2k": "1536x1024"}

TARGET_RATIO = 16 / 9
WEBP_QUALITY = 88

# Share of the added width that goes on the right, where the label chips sit.
# 0.5 would centre the artwork and leave the labels crowding its edge.
RIGHT_BIAS = 0.78


def load_key() -> str:
    """Read OPENAI_API_KEY from the environment, falling back to the repo .env.

    Parsed by hand rather than with python-dotenv so that running this script
    never depends on a package the rest of the site build does not need.
    """
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key.strip()
    env = REPO / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip()
    sys.exit("No OPENAI_API_KEY in the environment or in .env")


def latest_batch() -> Path:
    batches = sorted(QUEUE_DIR.glob("batch-*.json"))
    if not batches:
        sys.exit(f"No batch file in {QUEUE_DIR}")
    return batches[-1]


def fit_to_ratio(im: Image.Image, ratio: float = TARGET_RATIO,
                 right_bias: float = RIGHT_BIAS) -> Image.Image:
    """Reach `ratio` by PADDING with the background colour. Never by cropping.

    This replaced a content-aware crop, which was wrong for a reason worth
    keeping written down. `gpt-image-2` returns 3:2; reaching 16:9 by cutting
    means removing 160 rows, and an illustration that fills its frame loses the
    top and bottom of the drawing — the skin block ends flush against the edge
    of the figure and reads as a rendering fault. Nothing about a diagram is
    disposable; the model was asked to leave a margin, not to leave slack.

    Padding is safe here specifically because the artwork sits on a flat
    porcelain field: extending that field is invisible. The background colour is
    measured from the four corners rather than assumed, so a diagram that came
    back a shade off still pads seamlessly.

    `right_bias` puts most of the new width on the right, where the label chips
    go. Padding to the correct shape and opening the label gutter are the same
    operation, so the gutter costs nothing.
    """
    w, h = im.size
    if abs((w / h) - ratio) < 0.005:
        return im
    bg = _background(im)

    if (w / h) < ratio:                       # too tall: widen
        new_w, new_h = int(round(h * ratio)), h
        pad = new_w - w
        left = int(round(pad * (1 - right_bias)))
        box = (left, 0)
    else:                                     # too wide: heighten, centred
        new_w, new_h = w, int(round(w / ratio))
        box = (0, (new_h - h) // 2)

    out = Image.new("RGB", (new_w, new_h), bg)
    out.paste(im, box)
    return out


def trim_to_subject(im: Image.Image, pad: float = 0.05,
                    tol: int = 12) -> Image.Image:
    """Crop away the flat field around the drawing, leaving a `pad` margin.

    Anatomy never wants this — the margin IS the label gutter. An emblem does,
    and for a reason that is not aesthetic: the badge on the page is 68px
    across, and the model returns a circle filling about 60% of its frame. Shown
    whole, the emblem lands at ~40px and a guilloche ring or a rope twist stops
    being line work and becomes grey mush. Trimming first is the difference
    between a mark you can read and a smudge.

    The bounding box is measured against the field colour rather than against
    white, so it survives the warm porcelain these are drawn on.
    """
    bg = _background(im)
    solid = Image.new("RGB", im.size, bg)
    mask = (ImageChops.difference(im.convert("RGB"), solid)
            .convert("L").point(lambda v: 255 if v > tol else 0))
    box = mask.getbbox()
    if not box:
        return im
    left, top, right, bottom = box
    m = int(round(max(right - left, bottom - top) * pad))
    return im.crop((max(0, left - m), max(0, top - m),
                    min(im.width, right + m), min(im.height, bottom + m)))


def _background(im: Image.Image) -> tuple[int, int, int]:
    """The flat field colour, taken as the median of the four corners.

    One corner can be wrong — a diagram whose subject runs into it, a stray
    shadow — and a single bad sample would pad with tissue pink. Three
    agreeing corners outvote it.
    """
    w, h = im.size
    pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    samples = [im.convert("RGB").getpixel(p) for p in pts]
    return tuple(sorted(c[i] for c in samples)[1] for i in range(3))


def call_api(key: str, prompt: str, size: str, quality: str,
             reference: Path | None) -> bytes:
    """One image. Uses the edits endpoint when a style reference is supplied."""
    headers = {"Authorization": f"Bearer {key}"}
    if reference and reference.exists():
        with open(reference, "rb") as fh:
            files = {"image[]": (reference.name, fh.read(), "image/webp")}
        data = {"model": "gpt-image-2", "prompt": prompt,
                "size": size, "quality": quality, "n": "1"}
        resp = requests.post(API_EDIT, headers=headers, data=data,
                             files=files, timeout=300)
    else:
        payload = {"model": "gpt-image-2", "prompt": prompt,
                   "size": size, "quality": quality, "n": 1}
        resp = requests.post(API_GENERATE, headers=headers,
                             json=payload, timeout=300)

    if resp.status_code != 200:
        raise RuntimeError(f"{resp.status_code}: {resp.text[:600]}")

    item = resp.json()["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    return requests.get(item["url"], timeout=120).content


def generate(item: dict, key: str, quality: str, size_key: str,
             use_ref: bool) -> Path:
    ident = item["id"]
    prompt = item["params"]["prompt"]
    reference = ANCHOR if (use_ref and item["params"].get("medias")) else None

    print(f"  {ident}: requesting ({quality}/{size_key}"
          f"{', anchored' if reference else ', no reference'}) …", flush=True)
    started = time.time()
    raw = call_api(key, prompt, SIZES[size_key], quality, reference)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = len(list(RAW_DIR.glob(f"{ident}-*.png"))) + 1
    raw_path = RAW_DIR / f"{ident}-{stamp:02d}.png"
    raw_path.write_bytes(raw)

    im = Image.open(io.BytesIO(raw)).convert("RGB")
    before = im.size
    # Anatomy is 16:9 with the padding pushed right, because that is where the
    # label gutter goes. An emblem has no labels and no gutter — it wants to be
    # square and dead centre, or the circular crop on the page takes a bite out
    # of one side of it. So the shape is a property of the item, not of the run.
    fit = item.get("fit") or {}
    if fit.get("trim"):
        im = trim_to_subject(im)
    im = fit_to_ratio(im, fit.get("ratio", TARGET_RATIO),
                      fit.get("right_bias", RIGHT_BIAS))

    out = ASSETS / item["target_file"]
    # `target_file` may name a subdirectory — placeholder/ for stand-ins that
    # must not reach production. Making only ASSETS meant the picture came
    # back, cost credits, and then failed on write with nowhere to land.
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "WEBP", quality=WEBP_QUALITY, method=6)

    print(f"     {before[0]}x{before[1]} -> {im.size[0]}x{im.size[1]}  "
          f"{out.name}  ({out.stat().st_size // 1024} KB, "
          f"{time.time() - started:.0f}s)")
    print(f"     raw kept at {raw_path.relative_to(SITE)}")
    return out


def refit(item: dict) -> Path | None:
    """Re-derive the shipped WebP from the newest kept raw PNG.

    The raw API output is kept precisely so that changing how images are fitted
    to the page — as the crop→pad change did — costs nothing. Re-running the
    prompts would spend credits and return different pictures, which is the
    wrong way to fix a framing bug.
    """
    ident = item["id"]
    raws = sorted(RAW_DIR.glob(f"{ident}-*.png"))
    if not raws:
        print(f"  {ident}: no raw kept, skipped")
        return None
    im = Image.open(raws[-1]).convert("RGB")
    before = im.size
    fit = item.get("fit") or {}
    if fit.get("trim"):
        im = trim_to_subject(im)
    im = fit_to_ratio(im, fit.get("ratio", TARGET_RATIO),
                      fit.get("right_bias", RIGHT_BIAS))
    out = ASSETS / item["target_file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "WEBP", quality=WEBP_QUALITY, method=6)
    print(f"  {ident}: {before[0]}x{before[1]} -> {im.size[0]}x{im.size[1]}  "
          f"{out.name}  ({out.stat().st_size // 1024} KB)  from {raws[-1].name}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=("gen", "list", "refit"))
    ap.add_argument("ids", nargs="*", help="diagram ids, e.g. A2 B5")
    ap.add_argument("--all", action="store_true", help="every queued item")
    ap.add_argument("--quality", default="low",
                    choices=("low", "medium", "high"))
    ap.add_argument("--size", default="1k", choices=tuple(SIZES))
    ap.add_argument("--ref", default="anchor", choices=("anchor", "none"))
    args = ap.parse_args()

    batch = json.loads(latest_batch().read_text(encoding="utf-8"))
    items = batch["items"]

    if args.command == "list":
        print(f"{latest_batch().name} — {len(items)} item(s)")
        for it in items:
            done = (ASSETS / it["target_file"]).exists()
            print(f"  [{'x' if done else ' '}] {it['id']:<3} "
                  f"{it['target_file']:<32} -> {it['page']} "
                  f"§{it['after_section']}")
        return

    wanted = items if args.all else [i for i in items if i["id"] in args.ids]
    if not wanted:
        sys.exit("Nothing selected. Pass ids, or --all. Try: diagrams.py list")

    if args.command == "refit":
        print(f"refitting {len(wanted)} diagram(s) — no API calls")
        for it in wanted:
            refit(it)
        print("\ndone — label x-positions are percentages of the NEW box; "
              "re-check them with diagram_sheet.py")
        return

    key = load_key()
    print(f"generating {len(wanted)} diagram(s) from {latest_batch().name}")
    failures = []
    for it in wanted:
        try:
            generate(it, key, args.quality, args.size, args.ref == "anchor")
        except Exception as exc:                       # noqa: BLE001
            failures.append((it["id"], str(exc)))
            print(f"  {it['id']}: FAILED — {exc}")

    if failures:
        print(f"\n{len(failures)} failed:")
        for ident, err in failures:
            print(f"  {ident}: {err}")
        sys.exit(1)
    print("\ndone — review the images, then embed them")


if __name__ == "__main__":
    main()
