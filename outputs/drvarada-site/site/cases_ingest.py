"""Turn clinic camera rolls into case-study frames the site can carry.

WHAT THIS IS FOR
  The clinic photographs cases on a phone. Those files are 3–7 MB, arbitrarily
  oriented, sometimes landscape and sometimes portrait, and a few carry things
  that must never be published: a burned-in date stamp, a camera watermark, or
  a patient's face. This turns them into matched 4:5 frames at a sane weight,
  deterministically, so the same file always produces the same output and a
  crop can be argued with rather than redone by hand.

THE THREE RULES IT ENFORCES

  1. FACES ARE CROPPED OUT, NOT BLURRED. A blur says "there was a face here"
     and invites the reader to wonder whose. A crop to the treated area says
     what a clinical photograph is supposed to say, which is nothing about the
     person except the skin being discussed. Where the useful anatomy IS the
     face, the frame is cut to the band that carries the finding — a hairline,
     not a portrait.

  2. BURNED-IN STAMPS ARE CROPPED OUT. A date stamp in the corner of a
     photograph is not evidence, it is metadata that survived into the picture,
     and on a published case it dates a specific patient's specific visit.
     Camera watermarks go for the same reason plus a duller one: "REDMI NOTE 8
     AI QUAD CAMERA" across a clinical result looks like a stock photo.

  3. EXIF IS DROPPED. Phone photographs carry GPS, device serial and capture
     time. None of that belongs on a website and all of it survives a naive
     re-save. Pillow does not copy EXIF into WebP unless asked, and this never
     asks — but the transpose happens FIRST, because orientation is the one
     piece of EXIF that has to be honoured before it is thrown away.

FRAMING, AND THE BUG THAT MATTERED
  Every frame is 4:5 portrait, because that is what the `ba` grid renders and
  because a series shot at three different aspect ratios shows the camera
  moving rather than the skin changing. The crop is a box in fractions of the
  corrected image, grown to 4:5 rather than cut to it, so nothing inside the
  box is lost. Fractions rather than pixels means a re-shot original at a
  different resolution needs no new numbers.

  The first version of this grew every box within the whole image, and that is
  exactly wrong for the crops that matter. Asking for "the forehead only" on a
  landscape photograph of a face gives a box too wide to be 4:5, so growing it
  vertically ran out of room, fell back to taking the full height — and put the
  eyes back in the frame the crop existed to remove. A box that says "this must
  survive" cannot also say "and nothing else may enter".

  So a frame can be `strict`: its box is a hard boundary the crop may never
  leave, and 4:5 is reached by shrinking inside it. Every frame that excludes a
  face, a date stamp or a watermark is strict. The proof sheet is what caught
  this, and is why it exists.

USAGE
  python cases_ingest.py           # writes assets/img/cases/ + a proof sheet
  python cases_ingest.py --proof   # proof sheet only, nothing written
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageOps

SITE = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(r"C:\Users\VijayRaghavVarada\Downloads\DrVaradas Pictures"
                   r"\B&A Folders 02 AUG")
OUT = SITE / "assets" / "img" / "cases"
PROOF = SITE / ".diagram-queue" / "cases-proof"

TARGET = (1200, 1500)          # 4:5. Never upscaled past the source.
RATIO = 4 / 5
WEBP_QUALITY = 82

# (source path, output stem, box as l,t,r,b fractions, strict?, why)
#
# strict=True means the box is a HARD BOUNDARY the crop may never leave —
# used wherever something must be excluded rather than merely centred. Every
# face, date stamp and camera watermark in this set is held out by one.
#
# The focus box is what must survive. Everything about a crop that is a
# judgement rather than arithmetic is written down here, because in six months
# "why is this one cropped so tight" is a question with a real answer.
FRAMES = [
    # ── alopecia areata / totalis, patient 1 ────────────────────────────
    (r"Alopecia Totalis\pt 1\BEFORE.jpg", "alopecia-1-before",
     (0.02, 0.02, 0.98, 0.62),
     False, "scalp only; the shoulder and clothing below carry nothing clinical"),
    (r"Alopecia Totalis\pt 1\AFTER.jpg", "alopecia-1-after",
     (0.02, 0.08, 0.98, 0.70),
     True, "CUT ABOVE THE FACE — a child's eyes and nose are visible below 0.72"),

    # ── alopecia areata / totalis, patient 2 — the three-frame series ───
    (r"Alopecia Totalis\pt2\BEFORE.jpg", "alopecia-2-before",
     (0.02, 0.02, 0.98, 0.88), False, "bald scalp, no face in frame"),
    (r"Alopecia Totalis\pt2\DURING.jpg", "alopecia-2-during",
     (0.02, 0.02, 0.98, 0.90), False, "occipital regrowth, no face in frame"),
    (r"Alopecia Totalis\pt2\AFTER.jpg", "alopecia-2-after",
     (0.02, 0.04, 0.98, 0.60),
     True, "CUT ABOVE THE FACE — the same child's brow and eyes appear below 0.62"),

    # ── vitiligo, near-complete repigmentation ─────────────────────────
    (r"converting 95% to100% VITILIGO\BEFORE.jpg", "vitiligo-arm-before",
     (0.16, 0.02, 0.98, 0.98), False, "the forearm; bedding at the left is noise"),
    (r"converting 95% to100% VITILIGO\AFTER.jpg", "vitiligo-arm-after",
     (0.16, 0.02, 0.98, 0.98), False, "same forearm, framed to match the baseline"),

    # ── eczema ─────────────────────────────────────────────────────────
    (r"eczema\BEFORE.jpg", "eczema-before",
     (0.22, 0.00, 0.78, 1.00),
     True, "CAMERA WATERMARK bottom-left is outside x=0.22; landscape source"),
    (r"eczema\AFTER.jpg", "eczema-after",
     (0.26, 0.12, 1.00, 0.96), False, "the treated ankle, matching the baseline side"),

    # ── punch grafting for stable vitiligo (no baseline supplied) ───────
    (r"FUE FOR VITILIGO\DURING.jpg", "fue-vitiligo-during",
     (0.06, 0.14, 0.96, 0.88), False, "the graft bed, grafts in place"),
    (r"FUE FOR VITILIGO\AFTER.jpg", "fue-vitiligo-after",
     (0.06, 0.14, 0.96, 0.92), False, "same site, pigment spreading from each graft"),

    # ── hair grafting (no baseline supplied) ───────────────────────────
    (r"HAIR GRAFTING\DURING.jpg", "hair-graft-during",
     (0.10, 0.38, 0.96, 1.00),
     True, "CUT BELOW THE EYES — the source is a full, identifiable face. Only the "
     "forehead and the marked hairline survive, which is the whole clinical "
     "content of the frame"),
    (r"HAIR GRAFTING\AFTER.jpg", "hair-graft-after",
     (0.00, 0.04, 1.00, 0.96), False, "temple and hairline; no face in frame"),

    # ── morphea ────────────────────────────────────────────────────────
    (r"morphea before after\BEFORE.jpg", "morphea-before",
     (0.06, 0.02, 0.96, 0.96), False, "hand and wrist, the sclerotic bands"),
    (r"morphea before after\AFTER.jpg", "morphea-after",
     (0.04, 0.04, 0.96, 1.00), False, "same hand; landscape source, grown to 4:5"),

    # ── onychomycosis ──────────────────────────────────────────────────
    (r"nail fungus before and after\before rt toe.jpg", "nail-before",
     (0.02, 0.02, 0.98, 0.86),
     True, "DATE STAMP '2023/10/5' burned into the bottom-right is cut at 0.86"),
    (r"nail fungus before and after\after.jpg", "nail-after",
     (0.02, 0.02, 0.98, 0.96), False, "both great toes at follow-up"),

    # ── psoriasis, patient 1 — the best-matched pair in the set ────────
    (r"PSORISIS\pt 1\BEFORE.jpg", "psoriasis-1-before",
     (0.00, 0.00, 1.00, 1.00), False, "both shins; nothing to remove"),
    (r"PSORISIS\pt 1\AFTER.jpg", "psoriasis-1-after",
     (0.00, 0.00, 0.87, 1.00),
     True, "a bystander's hand intrudes at the top right; 0.93 still left "
     "fingers in shot, so it is cut back to 0.87"),

    # ── psoriasis, patient 2 ───────────────────────────────────────────
    (r"PSORISIS\pt 2\BEFORE.jpg", "psoriasis-2-before",
     (0.00, 0.00, 1.00, 0.90), True, "CAMERA WATERMARK bottom-left cut at 0.90"),
    (r"PSORISIS\pt 2\AFTER.jpg", "psoriasis-2-after",
     (0.00, 0.00, 1.00, 0.90), True, "same watermark, same cut, same framing"),

    # ── vitiligo, repigmentation after immunotherapy ───────────────────
    # These two are 455x607 and 280x607 — exports rather than originals, and
    # the only frames on the site below the target width.
    #
    # They were briefly published as a tall 1:2 pair, on the reasoning that a
    # limb photographed elbow-to-fingertip is a tall subject. That was right
    # about the photograph and wrong about the page: one case in a different
    # shape makes a row of cases look broken, and a reader reads that as the
    # site being careless before they read a word of it. So both frames are cut
    # to a matched 4:5 band across the forearms — the same span in each, which
    # is the only rule that actually matters — and the hands, which change least
    # and change slowest, fall outside both.
    (r"VITILIGO POST IMMUNOTHERAPY\BEFORE.png", "vitiligo-immuno-before",
     (0.10, 0.06, 0.96, 0.72), True,
     "both forearms; DATE STAMP '2020-1-8' bottom-right is far outside the box"),
    (r"VITILIGO POST IMMUNOTHERAPY\AFTER.png", "vitiligo-immuno-after",
     (0.00, 0.06, 1.00, 0.72), True,
     "the same forearm span; CAMERA WATERMARK bottom-left is outside the box"),
]

# Frames needing a shape other than the default. Empty, deliberately: every
# frame on the site is 4:5 so that a row of cases reads as one row. The hook
# stays because the next odd-shaped source will want it.
RATIOS: dict[str, float] = {}

# Held out, with the reason. Silence is the failure mode here: a case that
# quietly never appeared looks exactly like a case nobody sent.
SKIPPED = [
    (r"nail fungus before and after\before left toe.jpg",
     "112x150 — a thumbnail, not a photograph"),
]


def fit_ratio(box, bounds, ratio: float = RATIO) -> tuple[int, int, int, int]:
    """Reach `ratio` by growing `box` inside `bounds`; shrink only if it can't.

    `bounds` is the hard edge. For an ordinary frame it is the whole image, so
    the box grows outward and nothing inside it is lost — reaching an aspect
    ratio by trimming a focus box would quietly cut the edge off a lesion to
    satisfy a layout constraint, which is the wrong way round.

    For a strict frame `bounds` IS the box, so growth is impossible and the
    largest 4:5 rectangle inside it is taken instead. That is what keeps a face
    or a date stamp out: the crop cannot expand back over the thing it was
    drawn to exclude, whatever the aspect ratio would prefer.
    """
    L, T, R, B = bounds
    l, t, r, b = max(box[0], L), max(box[1], T), min(box[2], R), min(box[3], B)

    def span(lo, hi, want, floor, ceil):
        """Centre a `want`-long span on (lo, hi), clamped inside (floor, ceil)."""
        c = (lo + hi) / 2
        s, e = c - want / 2, c + want / 2
        if s < floor:
            s, e = floor, floor + want
        if e > ceil:
            s, e = ceil - want, ceil
        return s, e

    w, h = r - l, b - t
    if w / h < ratio:                                   # too tall: widen
        want = h * ratio
        if want <= R - L:
            l, r = span(l, r, want, L, R)
        else:                                           # no room: shorten
            l, r = L, R
            t, b = span(t, b, (R - L) / ratio, T, B)
    else:                                               # too wide: heighten
        want = w / ratio
        if want <= B - T:
            t, b = span(t, b, want, T, B)
        else:                                           # no room: narrow
            t, b = T, B
            l, r = span(l, r, (B - T) * ratio, L, R)

    return tuple(int(round(v)) for v in (l, t, r, b))


def load(rel: str) -> Image.Image:
    """Open, honour the orientation tag, and drop everything else EXIF held."""
    im = Image.open(SRC / rel)
    return ImageOps.exif_transpose(im).convert("RGB")


def frame(im: Image.Image, focus, strict: bool, ratio: float = RATIO
          ) -> tuple[Image.Image, tuple[int, int, int, int]]:
    W, H = im.size
    box = (focus[0] * W, focus[1] * H, focus[2] * W, focus[3] * H)
    # A strict frame may not leave its own box; an ordinary one may grow to the
    # edge of the picture.
    box = fit_ratio(box, box if strict else (0, 0, W, H), ratio)
    cut = im.crop(box)
    if cut.width > TARGET[0]:                  # never upscale a small original
        cut = cut.resize((TARGET[0], int(round(TARGET[0] / ratio))), Image.LANCZOS)
    return cut, box


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--proof", action="store_true",
                    help="write the proof sheet only; touch no site assets")
    args = ap.parse_args()

    if not SRC.exists():
        sys.exit(f"source folder not found: {SRC}")
    OUT.mkdir(parents=True, exist_ok=True)
    PROOF.mkdir(parents=True, exist_ok=True)

    for rel, why in SKIPPED:
        print(f"  skipped  {rel}  — {why}")

    total = 0
    for rel, stem, focus, strict, note in FRAMES:
        im = load(rel)
        cut, box = frame(im, focus, strict, RATIOS.get(stem, RATIO))

        # The proof sheet shows the ORIGINAL with the kept region outlined and
        # everything discarded dimmed, which is the only way to check by eye
        # that a face or a date stamp actually fell outside the crop.
        proof = im.copy()
        dim = Image.new("RGB", im.size, (0, 0, 0))
        proof = Image.blend(proof, dim, 0.62)
        proof.paste(im.crop(box), (box[0], box[1]))
        d = ImageDraw.Draw(proof)
        d.rectangle(box, outline=(255, 0, 170), width=max(4, im.width // 240))
        proof.thumbnail((520, 520), Image.LANCZOS)
        proof.save(PROOF / f"{stem}.png")

        if not args.proof:
            out = OUT / f"{stem}.webp"
            cut.save(out, "WEBP", quality=WEBP_QUALITY, method=6)
            kb = out.stat().st_size // 1024
            flag = "  ⚠ below target" if cut.width < TARGET[0] else ""
            print(f"  {stem:<24} {im.size[0]}x{im.size[1]} → "
                  f"{cut.size[0]}x{cut.size[1]}  {kb} KB{flag}")
            total += 1

    print(f"\n{'proof sheet only' if args.proof else f'{total} frame(s) → assets/img/cases/'}"
          f"\nproof sheet -> {PROOF.relative_to(SITE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
