#!/usr/bin/env python
"""Render the Google Business Profile logo — full colour, opaque white, square.

    python google_logo.py     -> google/ (PNG + JPG, 1024px)

WHY NOT JUST UPLOAD profile-512.png
  Three reasons, each of which shows up only after the upload:

  · It is transparent. Google composites an alpha PNG onto whatever the surface
    happens to be, which in dark mode is black — a navy mark on black.
  · The `-light` SVG sits on porcelain inside a 112-unit rounded rect. Google
    applies its OWN circular mask, and a rounded square inside a circle reads as
    a mistake rather than a shape.
  · 512 px clears Google's 250 minimum but is under its 720 recommendation.

WHICH TIER, AND WHY IT IS NOT THE DETAILED ONE
  `icons/README.md` is explicit: pick the tier by the size the icon is DISPLAYED
  at, not the size of the file uploaded. Google takes a 512+ upload and shows it
  at 40-96 px using its own downscaler; hand it the `full` tier and the 36-element
  field mashes into grey. So this uses `compact` — a large file drawn for a small
  destination.

CENTRING IS MEASURED, NOT ASSUMED
  Placing the SVG by its viewBox put the mark low and right of centre: the
  artwork does not sit symmetrically inside its own 512 box. So it is rendered
  on transparency first, its INK bounding box measured, and that box centred.
  The result is independent of whatever padding the source file happens to
  carry, which also means a future re-cut of the icon cannot silently
  de-centre this.

CIRCLE SAFETY
  Google applies its own circular mask. A box of w x h has a bounding circle of
  radius sqrt(w^2 + h^2)/2, and that is what must fit — not the width or the
  height. The mark is scaled until its bounding circle is 92% of the frame's
  inscribed circle, so a corner of the artwork cannot clip when the mask lands,
  while still filling the square version.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "google"
FRAME = 1024
MARK_H = 660            # keeps the bounding circle inside the inscribed circle


def ink(svg_path: pathlib.Path, px: int):
    """Render an SVG on transparency and crop to its actual ink.

    Shared by the square logo and the wide lockup, for the reason the logo
    needed it: these files do not sit symmetrically inside their own viewBox,
    so anything positioned by the box lands visibly off-centre.
    """
    from PIL import Image
    svg = svg_path.read_text(encoding="utf-8").split("?>")[-1].strip()
    page = OUT / "_r.html"
    page.write_text(
        f'<!doctype html><meta charset="utf-8">'
        f'<style>html,body{{margin:0;background:transparent}}'
        f'.w{{width:{px}px;height:{px}px;display:flex;align-items:center;'
        f'justify-content:center}}.w svg{{width:{int(px * .94)}px;height:auto;'
        f'display:block}}</style><div class="w">{svg}</div>', encoding="utf-8")
    raw = (OUT / "_r.png").resolve()
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars",
                    "--default-background-color=00000000",
                    f"--screenshot={raw}", f"--window-size={px},{px}",
                    page.resolve().as_uri()], capture_output=True, timeout=180)
    page.unlink(missing_ok=True)
    if not raw.exists():
        raise SystemExit(f"chrome produced no screenshot for {svg_path.name}")
    art = Image.open(raw).convert("RGBA")
    box = art.getbbox()
    art = art.crop(box) if box else art
    art.load()
    raw.unlink(missing_ok=True)
    return art


def cover() -> None:
    """The wide lockup — name, descriptor and tagline — for a cover slot.

    16:9 at 2048x1152. Google's cover photo is re-cropped differently on
    Search, Maps and mobile, so the artwork is held to 60% of the width and
    centred: the margin is what survives a crop nobody gets to preview.
    """
    from PIL import Image
    art = ink(HERE / "lockups" / "logo-horizontal-tagline-light.svg", 2400)
    W, H = 2048, 1152
    scale = (W * 0.60) / art.width
    if art.height * scale > H * 0.62:              # tall crops are the risk
        scale = (H * 0.62) / art.height
    art = art.resize((round(art.width * scale), round(art.height * scale)),
                     Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(art, ((W - art.width) // 2, (H - art.height) // 2), art)
    canvas.save(OUT / "google-cover-2048x1152.jpg", quality=95, subsampling=0)
    canvas.save(OUT / "google-cover-2048x1152.png")

    # The lockup on its own, at print resolution, for anything that is not a
    # cover slot — letterhead, a slide, an email footer.
    pad = round(art.width * 0.06)
    flat = Image.new("RGB", (art.width + pad * 2, art.height + pad * 2),
                     (255, 255, 255))
    flat.paste(art, (pad, pad), art)
    flat.save(OUT / "logo-tagline-wide.png")
    print(f"  cover {W}x{H}, lockup {art.width}x{art.height} "
          f"({art.width / W:.0%} of width)")
    print(f"  logo-tagline-wide.png {flat.size[0]}x{flat.size[1]}")


def square_lockup() -> None:
    """The stacked lockup — symbol, name, descriptor, tagline — in a square.

    NOT a substitute for `google-logo-1024`. Google masks the logo slot to a
    circle and renders it at 40-96 px; a lockup there loses its corners and its
    words are illegible besides. This is for square slots that do NOT crop to a
    circle: WhatsApp Business, a social post, a stamp, print.

    The clipping figure is measured and printed rather than asserted, so the
    decision about where this can safely go rests on a number.
    """
    from PIL import Image
    art = ink(HERE / "lockups" / "logo-stacked-tagline-light.svg", 2400)
    for size in (1024, 2048):
        s = (size * 0.86) / max(art.width, art.height)
        a = art.resize((round(art.width * s), round(art.height * s)),
                       Image.LANCZOS)
        canvas = Image.new("RGB", (size, size), (255, 255, 255))
        canvas.paste(a, ((size - a.width) // 2, (size - a.height) // 2), a)
        canvas.save(OUT / f"logo-square-text-{size}.jpg", quality=95,
                    subsampling=0)
        if size == 1024:
            canvas.save(OUT / "logo-square-text-1024.png")
            import numpy as np
            arr = np.asarray(canvas)
            m = arr.sum(2) < 720
            ys, xs = np.nonzero(m)
            r = np.sqrt((xs - size / 2) ** 2 + (ys - size / 2) ** 2)
            out = int((r > size / 2).sum())
            print(f"  square-with-text {size}: artwork {a.width}x{a.height}")
            print(f"    under a CIRCULAR mask {out:,} ink px would be cut "
                  f"({out / max(m.sum(), 1):.0%}) — do not use in the "
                  f"Google logo slot")


def portrait_cover() -> None:
    """A cover photo built from the REAL portrait, not a generated scene.

    Google requires photos to represent the business as it actually is, and a
    clinic is a place a patient then has to find and walk into. An invented
    exterior or waiting room would be a picture of somewhere that does not
    exist — misleading in a way that matters more for a medical practice than
    for most businesses, and removable by Google on those grounds.

    A keyed photograph of the actual doctor on a plain brand field is the
    opposite of that: nothing about it is fabricated, it is just a portrait on
    a background.

    Composition is held inside the middle 80% because Google re-crops covers
    per surface and never shows the author which crop it chose.
    """
    from PIL import Image
    W, H = 2048, 1152

    src = HERE.parent.parent.parent / "inputs" / "portraits" / \
        "_source-keyed-3712x5568.png"
    if not src.exists():
        raise SystemExit(f"missing portrait: {src}")
    doc = Image.open(src).convert("RGBA")
    doc = doc.crop(doc.getbbox())
    # UPPER BODY, NOT FULL LENGTH.
    #   A cover is judged at a few hundred pixels wide. The full-length figure
    #   is 1:3.3, so at cover height his face was about 40 px across — the one
    #   element doing the trust work, rendered too small to read. Cropping to
    #   the top 58% roughly doubles the face and fills the frame properly.
    #   The cut is placed at the bottom EDGE of the canvas, so he bleeds off it
    #   like a photograph rather than floating like a severed cutout.
    doc = doc.crop((0, 0, doc.width, round(doc.height * 0.58)))
    tmp = (OUT / "_doc.png").resolve()
    doc.save(tmp)

    mark = HERE / "logo-mark-flat-navy.svg"
    svg = mark.read_text(encoding="utf-8").split("?>")[-1].strip()
    fonts = (HERE / "source" / "fonts").resolve().as_uri()

    # COMPOSED FOR THE CROP, NOT FOR THIS RECTANGLE.
    #   Google re-crops covers per surface and shows some of them square. The
    #   first version put the lockup hard left and the doctor hard right, so a
    #   centre crop lost both and kept the empty middle. Everything that has to
    #   survive — his face, the name, the credential line — is inside the
    #   central square (x 448-1600), and the frame's outer eighth carries
    #   nothing but background.
    html = f"""<!doctype html><meta charset="utf-8">
<style>
  @font-face {{ font-family: Gabarito; src: url({fonts}/Gabarito.woff2)
               format('woff2'); font-weight: 400 700; font-display: block; }}
  @font-face {{ font-family: Manrope; src: url({fonts}/Manrope.woff2)
               format('woff2'); font-weight: 400 800; font-display: block; }}
  * {{ margin: 0; box-sizing: border-box; }}
  .c {{ width: {W}px; height: {H}px; background: #F8F5F3; position: relative;
        overflow: hidden; font-family: Manrope, sans-serif; }}
  /* A calm brand field rather than flat paper — the mint is the site's own
     accent at low opacity, which reads as considered at thumbnail size where
     a flat rectangle reads as unfinished. */
  .wash {{ position: absolute; inset: 0;
     background: radial-gradient(120% 90% at 78% 106%,
        rgba(143,220,198,.40) 0%, rgba(143,220,198,.12) 42%,
        rgba(143,220,198,0) 68%); }}
  .rule {{ position: absolute; left: 0; right: 0; bottom: 0; height: 14px;
           background: #1E3A63; }}
  .txt {{ position: absolute; left: 460px; top: 50%;
          transform: translateY(-50%); width: 700px; }}
  .id {{ display: flex; align-items: center; gap: 22px; margin-bottom: 34px; }}
  .id svg {{ height: 96px; width: auto; display: block; }}
  .nm {{ font-family: Gabarito, sans-serif; font-weight: 700; font-size: 54px;
         line-height: 1.02; color: #1E3A63; letter-spacing: -.015em; }}
  .sub {{ font-size: 21px; font-weight: 700; letter-spacing: .22em;
          color: #7C8A99; margin-top: 8px; }}
  h1 {{ font-family: Gabarito, sans-serif; font-weight: 700; font-size: 68px;
        line-height: 1.06; color: #12202F; letter-spacing: -.02em; }}
  .who {{ margin-top: 26px; font-size: 27px; line-height: 1.45;
          color: #41506B; font-weight: 600; }}
  .who b {{ color: #12202F; font-weight: 800; }}
  .meta {{ margin-top: 30px; display: flex; gap: 14px; flex-wrap: wrap; }}
  .meta span {{ font-size: 21px; font-weight: 700; color: #0B4A3E;
     background: rgba(143,220,198,.34); padding: 11px 20px;
     border-radius: 999px; white-space: nowrap; }}
  .doc {{ position: absolute; right: 380px; bottom: 14px; height: 1105px; }}
</style>
<div class="c">
  <div class="wash"></div>
  <img class="doc" src="{tmp.as_uri()}">
  <div class="txt">
    <div class="id">{svg}
      <div><div class="nm">Dr. VARADA&rsquo;s</div>
           <div class="sub">SKIN &amp; HAIR CENTER</div></div>
    </div>
    <h1>Skin, hair and vitiligo,<br>in Secunderabad.</h1>
    <div class="who"><b>Dr. (Lt Col) Khagendra Varada</b><br>
      Dermatologist &amp; dermatosurgeon</div>
    <div class="meta"><span>45 years in practice</span>
      <span>Karkhana</span><span>Mon&ndash;Sat</span></div>
  </div>
  <div class="rule"></div>
</div>"""
    page = OUT / "_cov.html"
    page.write_text(html, encoding="utf-8")
    shot = (OUT / "_cov.png").resolve()
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", f"--screenshot={shot}",
                    f"--window-size={W},{H}", page.resolve().as_uri()],
                   capture_output=True, timeout=180)
    page.unlink(missing_ok=True)
    if not shot.exists():
        raise SystemExit("chrome produced no cover")
    im = Image.open(shot).convert("RGB")
    im.save(OUT / "google-cover-doctor-2048x1152.jpg", quality=95,
            subsampling=0)
    im.save(OUT / "google-cover-doctor-2048x1152.png")
    # The square centre crop Google may show, saved so the composition can be
    # judged against it rather than hoped about.
    im.crop(((W - H) // 2, 0, (W + H) // 2, H)).save(
        OUT / "preview-cover-square-crop.png")
    shot.unlink(missing_ok=True)
    tmp.unlink(missing_ok=True)
    print(f"  doctor cover {W}x{H} + square-crop preview")


def chrome() -> str:
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "google-chrome", "chromium"):
        if pathlib.Path(c).exists() or shutil.which(c):
            return c
    raise SystemExit("Chrome not found")


def main() -> None:
    src = HERE / "icons" / "icon-compact-transparent.svg"
    if not src.exists():
        raise SystemExit(f"missing {src}")
    svg = src.read_text(encoding="utf-8").split("?>")[-1].strip()
    OUT.mkdir(exist_ok=True)

    # Render oversized and on transparency, so the ink can be measured. 2x the
    # final frame leaves enough resolution that the downscale after cropping is
    # still sharper than rendering at final size would have been.
    big = FRAME * 2
    html = f"""<!doctype html><meta charset="utf-8">
<style>
  html,body {{ margin:0; padding:0; background:transparent; }}
  .m {{ width:{big}px; height:{big}px; display:flex;
        align-items:center; justify-content:center; }}
  .m svg {{ height:{int(big * 0.92)}px; width:auto; display:block; }}
</style>
<div class="m">{svg}</div>"""
    page = OUT / "_logo.html"
    page.write_text(html, encoding="utf-8")

    raw = OUT / "_raw.png"
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--default-background-color=00000000",
                    f"--screenshot={raw}", f"--window-size={big},{big}",
                    page.resolve().as_uri()],
                   capture_output=True, timeout=120)
    page.unlink(missing_ok=True)
    if not raw.exists():
        raise SystemExit("chrome produced no screenshot")

    from PIL import Image
    art = Image.open(raw).convert("RGBA")
    box = art.getbbox()                     # the ink, not the viewBox
    if not box:
        raise SystemExit("rendered artwork is empty")
    art = art.crop(box)
    w, h = art.size

    # Scale so the artwork's BOUNDING CIRCLE fits inside the frame's inscribed
    # circle with a margin — the diagonal is the constraint under a round mask.
    target_r = FRAME / 2 * 0.92
    scale = target_r / ((w * w + h * h) ** 0.5 / 2)
    art = art.resize((max(1, round(w * scale)), max(1, round(h * scale))),
                     Image.LANCZOS)

    canvas = Image.new("RGB", (FRAME, FRAME), (255, 255, 255))
    canvas.paste(art, ((FRAME - art.width) // 2, (FRAME - art.height) // 2), art)
    png = OUT / "google-logo-1024.png"
    canvas.save(png)
    # A JPG too. Google accepts both, but a JPG cannot carry an alpha channel at
    # all — which makes it the safer of the two here, since transparency is the
    # failure this whole script exists to avoid.
    canvas.save(OUT / "google-logo-1024.jpg", quality=95, subsampling=0)
    raw.unlink(missing_ok=True)
    im = canvas
    print(f"  ink {w}x{h} -> {art.width}x{art.height} centred in {FRAME}")

    corners = [im.getpixel(p) for p in ((2, 2), (FRAME - 3, 2),
                                        (2, FRAME - 3), (FRAME - 3, FRAME - 3))]
    ok = all(c == (255, 255, 255) for c in corners)
    print(f"{png.name}  {im.size}")
    print(f"{(OUT / 'google-logo-1024.jpg').name}  "
          f"{(OUT / 'google-logo-1024.jpg').stat().st_size // 1024} KB")
    print(f"  corners pure white: {ok}  {corners[0]}")
    if not ok:
        sys.exit("background is not white — check --default-background-color")
    cover()
    square_lockup()
    portrait_cover()


if __name__ == "__main__":
    main()
