#!/usr/bin/env python
"""Render the WhatsApp Business assets — catalogue tiles and the profile photo.

    python whatsapp_assets.py     -> whatsapp/

WHY NOT REUSE google/logo-square-text-1024.jpg
  Its own docstring offers it for "WhatsApp Business", and for a profile or a
  post it is right. For a CATALOGUE it is not, and the reason only shows up at
  the size the catalogue actually renders.

  A catalogue grid draws each item at roughly 150 px on a phone. Downscaled
  there, the stacked lockup gives: "Dr. VARADA's" legible, "SKIN & HAIR CENTER"
  marginal, and "Regenerate · Restore · Reveal" a grey smudge. The tagline is
  not merely small, it is noise occupying a fifth of the tile — and it pushes
  the mark and the name smaller to make room for itself. So the catalogue tiles
  are built from the NO-TAGLINE stacked lockup, with the artwork filling more of
  the frame.

EVERY ITEM IN A CATALOGUE MUST NOT LOOK THE SAME
  The failure mode of a logo-per-item catalogue is a grid of nine identical
  squares that a patient has to read the captions of to tell apart, which
  defeats having pictures at all. So the service tiles name the service in type
  large enough to survive the grid, and the logo tile is reserved for the one
  slot that is genuinely about the practice rather than a service.

NO PRICE IN THE PICTURE
  WhatsApp catalogue items carry their own price field. A fee baked into the
  artwork is a second copy that cannot be edited from the app, so the day the
  fee changes the picture starts lying and nobody notices — the same failure as
  a caption naming a photograph that is no longer on the page. The fee goes in
  the field; the tile says what the thing is.

LEGIBILITY IS MEASURED, NOT ASSUMED
  Every tile is re-rendered at 150 px into `preview-catalogue-grid.png`, which
  is the artefact to judge these by. If a line cannot be read there, it does not
  belong on the tile.
"""

from __future__ import annotations

import pathlib
import subprocess

import google_logo
from google_logo import chrome, ink

HERE = pathlib.Path(__file__).parent
OUT = HERE / "whatsapp"
FRAME = 1024
FONTS = (HERE / "source" / "fonts").resolve().as_uri()

INK = "#12202F"          # --ink
NAVY = "#1E3A63"         # the wordmark navy
GREY = "#66707D"         # --ink-3
MINT_SF = "#DFF3EC"      # --mint-sf
MINT_DP = "#0B6353"      # --mint-dp


def catalogue_logo() -> None:
    """The practice itself, as one catalogue tile — mark and name, no tagline.

    Held to 88% of the frame rather than the 86% the Google square uses: nothing
    crops this to a circle, so the corners are free.

    Not larger. At 92% the ends of "SKIN & HAIR CENTER" sat 45 px from the edge
    — 4% — which is fine if the tile is shown exactly as uploaded and ruins the
    wordmark if any surface trims a few percent. The extra 4% of linear scale is
    about three pixels of cap height in the grid, which nobody can see; a
    clipped wordmark is visible to everybody.
    """
    from PIL import Image
    art = ink(HERE / "lockups" / "logo-stacked-light.svg", 2400)
    s = (FRAME * 0.88) / max(art.width, art.height)
    a = art.resize((round(art.width * s), round(art.height * s)), Image.LANCZOS)
    canvas = Image.new("RGB", (FRAME, FRAME), (255, 255, 255))
    canvas.paste(a, ((FRAME - a.width) // 2, (FRAME - a.height) // 2), a)
    canvas.save(OUT / "wa-catalogue-logo-1024.jpg", quality=95, subsampling=0)
    canvas.save(OUT / "wa-catalogue-logo-1024.png")
    print(f"  logo tile      {FRAME}x{FRAME}  artwork {a.width}x{a.height}")


def service_tile(slug: str, head: str, sub: str, chip: str) -> None:
    """One service, named in type that survives the grid.

    The headline is the only element required to read at 150 px; `sub` and
    `chip` are for the card and detail views, where there is room. That is why
    the headline gets a whole line to itself and the rest is deliberately quiet
    — a tile that tries to say three things at grid size says none of them.
    """
    from PIL import Image
    mark = (HERE / "icons" / "icon-compact-transparent.svg"
            ).read_text(encoding="utf-8").split("?>")[-1].strip()
    html = f"""<!doctype html><meta charset="utf-8">
<style>
  @font-face {{ font-family: Gabarito; src: url({FONTS}/Gabarito.woff2)
               format('woff2'); font-weight: 400 700; font-display: block; }}
  @font-face {{ font-family: Manrope; src: url({FONTS}/Manrope.woff2)
               format('woff2'); font-weight: 400 800; font-display: block; }}
  * {{ margin: 0; box-sizing: border-box; }}
  .c {{ width: {FRAME}px; height: {FRAME}px; background: #FFFFFF;
        position: relative; overflow: hidden; font-family: Manrope, sans-serif;
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; padding: 70px 62px 88px; text-align: center; }}
  /* The same mint wash as the Google cover, so the two read as one brand.
     A flat white square looks unfinished in a grid of them; this gives the
     tile a corner to be recognised by at thumbnail size. */
  .wash {{ position: absolute; inset: 0; background:
     radial-gradient(115% 85% at 82% 108%, rgba(143,220,198,.46) 0%,
       rgba(143,220,198,.14) 44%, rgba(143,220,198,0) 70%); }}
  .rule {{ position: absolute; left: 0; right: 0; bottom: 0; height: 16px;
           background: {NAVY}; }}
  .in {{ position: relative; }}
  .mk svg {{ height: 224px; width: auto; display: block; margin: 0 auto 46px; }}
  h1 {{ font-family: Gabarito, sans-serif; font-weight: 700; font-size: 122px;
        line-height: 1.01; color: {INK}; letter-spacing: -.028em; }}
  .sub {{ margin-top: 32px; font-size: 34px; line-height: 1.4; font-weight: 600;
          color: {GREY}; }}
  .chip {{ margin-top: 34px; display: inline-block; font-size: 27px;
     font-weight: 800; letter-spacing: .04em; color: {MINT_DP};
     background: {MINT_SF}; padding: 15px 30px; border-radius: 999px; }}
</style>
<div class="c">
  <div class="wash"></div>
  <div class="in">
    <div class="mk">{mark}</div>
    <h1>{head}</h1>
    <div class="sub">{sub}</div>
    <div class="chip">{chip}</div>
  </div>
  <div class="rule"></div>
</div>"""
    page = OUT / "_t.html"
    page.write_text(html, encoding="utf-8")
    shot = (OUT / "_t.png").resolve()
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", f"--screenshot={shot}",
                    f"--window-size={FRAME},{FRAME}", page.resolve().as_uri()],
                   capture_output=True, timeout=180)
    page.unlink(missing_ok=True)
    if not shot.exists():
        raise SystemExit(f"chrome produced no tile for {slug}")
    im = Image.open(shot).convert("RGB")
    im.save(OUT / f"wa-catalogue-{slug}-1024.jpg", quality=95, subsampling=0)
    im.save(OUT / f"wa-catalogue-{slug}-1024.png")
    shot.unlink(missing_ok=True)
    print(f"  service tile   {slug}")


def grid_preview(names: list[str]) -> None:
    """The tiles at the size the catalogue grid draws them.

    This is the artefact these are judged by. A tile that reads here reads on a
    phone; a tile that does not is not fixed by uploading a bigger file, because
    the grid downscales whatever it is given.
    """
    from PIL import Image
    cell, gap, pad = 150, 18, 22
    w = pad * 2 + cell * len(names) + gap * (len(names) - 1)
    sheet = Image.new("RGB", (w, cell + pad * 2), (237, 237, 240))
    for i, n in enumerate(names):
        t = Image.open(OUT / f"{n}-1024.png").convert("RGB")
        sheet.paste(t.resize((cell, cell), Image.LANCZOS),
                    (pad + i * (cell + gap), pad))
    sheet.save(OUT / "preview-catalogue-grid.png")
    print(f"  grid preview   {len(names)} tile(s) at {cell}px "
          f"-> preview-catalogue-grid.png")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    google_logo.OUT.mkdir(exist_ok=True)      # ink() stages its temps there
    catalogue_logo()
    service_tile("online-consultation", "Online<br>consultation",
                 "Video call with Dr. (Lt&nbsp;Col) Khagendra Varada",
                 "Mon&ndash;Sat")
    service_tile("clinic-consultation", "At the<br>clinic",
                 "In person with Dr. (Lt&nbsp;Col) Khagendra Varada",
                 "Karkhana, Secunderabad")
    grid_preview(["wa-catalogue-logo", "wa-catalogue-online-consultation",
                  "wa-catalogue-clinic-consultation"])
    print(f"\n  -> {OUT}")


if __name__ == "__main__":
    main()
