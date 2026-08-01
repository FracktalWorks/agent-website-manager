"""Prepare Dr. Varada's cut-out for the hero slot.

THE SOURCE
  3712x5568 RGBA, already keyed — 16.2M transparent pixels against 4.3M opaque.
  What it is NOT is clean: 95% of the semi-transparent edge pixels are blue
  (B mean 194 against R 129), matte spill left over from whatever the figure was
  keyed off. On a black preview that is invisible. On this site's light mint
  panel it would read as a blue halo tracing the whole silhouette.

THE TREATMENT
  1. Despill — pull the blue in edge pixels back towards the red/green level, so
     what remains of the fringe is a neutral grey rather than a colour.
  2. Erode the alpha by a few pixels. Despill alone leaves a soft grey outline;
     eating the outermost ring removes it. At 3712px wide a 5px erosion is barely
     a pixel once the image is downscaled 4x, so nothing real is lost.
  3. Crop half-length for the hero. The silhouette profile says the head ends
     around 13% down, the crossed arms peak at 30% and finish near 40%. Cutting
     at 48% keeps the whole gesture — face, coat, crossed arms — and lands in
     open coat rather than slicing the hem. At full length in a 4:5 box the
     figure would be 36% of the width and the face too small to read.
  4. Bottom edge is the frame edge, deliberately. `object-fit: cover` puts the
     cut exactly on the arch's lower border, so it reads as a frame cropping him
     rather than a torso floating in space. No fade needed, and no fade wanted.

OUTPUT
  Transparent, so the panel behind it stays a CSS token and `brandkit.py apply`
  can still restyle this site into another design system without a mint
  rectangle baked into the photograph.
"""

from pathlib import Path

from PIL import Image, ImageFilter

REPO = Path(r"c:\Users\VijayRaghavVarada\Documents\Github\agent-website-manager")
SRC = REPO / "inputs" / "dr-varada-standing.png"
OUT = REPO / "outputs" / "drvarada-site" / "site" / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

ERODE_PX = 5
HERO_W, HERO_H = 880, 1100          # 4:5, 2x the ~440px slot
FULL_H = 1500                       # the standing figure, kept for other uses


def despill(im: Image.Image) -> Image.Image:
    """Neutralise the blue matte in partially transparent pixels.

    Only edge pixels are touched: a fully opaque pixel is real photograph and
    must not be colour-shifted, and a fully transparent one has no colour worth
    correcting. Blue is pulled down to the red/green average where it exceeds
    it, which turns a blue fringe grey without touching skin, shirt or coat.
    """
    r, g, b, a = im.split()
    rp, gp, bp, ap = r.load(), g.load(), b.load(), a.load()
    w, h = im.size
    touched = 0
    for y in range(h):
        for x in range(w):
            al = ap[x, y]
            if al == 0 or al == 255:
                continue
            rv, gv, bv = rp[x, y], gp[x, y], bp[x, y]
            cap = (rv + gv) // 2
            if bv > cap:
                bp[x, y] = cap
                touched += 1
    print(f"  despilled {touched:,} edge pixels")
    return Image.merge("RGBA", (r, g, b, a))


def erode_alpha(im: Image.Image, px: int) -> Image.Image:
    """Shrink the mask, eating the outermost ring of fringe.

    MinFilter is a true erosion for an 8-bit mask, and it is applied to alpha
    only — the colour planes keep their full resolution.
    """
    r, g, b, a = im.split()
    a = a.filter(ImageFilter.MinFilter(px * 2 + 1))
    return Image.merge("RGBA", (r, g, b, a))


def main() -> None:
    im = Image.open(SRC).convert("RGBA")
    print(f"source {im.size}")

    im = despill(im)
    im = erode_alpha(im, ERODE_PX)

    box = im.getchannel("A").getbbox()
    x0, y0, x1, y1 = box
    fw, fh = x1 - x0, y1 - y0
    print(f"  figure {fw}x{fh} at {box}")

    # ── hero: half-length, 4:5 ────────────────────────────────────────────
    # Figure fills ~72% of the crop width, leaving air for the stat chips that
    # the layout hangs outside this box on purpose.
    cw = round(fw / 0.72)
    ch = round(cw * 5 / 4)
    cx = x0 + fw // 2
    left = cx - cw // 2
    top = y0 - round(ch * 0.08)                  # headroom above the hair
    hero = im.crop((left, top, left + cw, top + ch))
    cut_at = (top + ch - y0) / fh
    print(f"  hero crop {cw}x{ch} — cuts at {cut_at:.0%} of the figure")
    hero = hero.resize((HERO_W, HERO_H), Image.LANCZOS)

    # ── full standing figure, trimmed ─────────────────────────────────────
    pad = round(fw * 0.06)
    full = im.crop((max(0, x0 - pad), max(0, y0 - pad),
                    min(im.size[0], x1 + pad), min(im.size[1], y1 + pad)))
    fw2, fh2 = full.size
    full = full.resize((round(fw2 * FULL_H / fh2), FULL_H), Image.LANCZOS)

    for name, img in (("dr-varada-hero", hero), ("dr-varada-standing", full)):
        for ext, kw in (("png", {"optimize": True}),
                        ("webp", {"quality": 90, "method": 6})):
            p = OUT / f"{name}.{ext}"
            img.save(p, **kw)                    # no metadata is carried over
            print(f"  {p.name:28} {img.size[0]}x{img.size[1]}  "
                  f"{p.stat().st_size / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
