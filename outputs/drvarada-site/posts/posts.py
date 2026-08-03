"""Render Google Business Profile post cards, and the text to go with them.

    python posts.py            # -> out/*.png and out/posts.md

WHY THESE ARE DRAWN AND NOT PHOTOGRAPHED OR GENERATED.

A Business Profile is a record of a real place. Photographs on it are read —
by patients and by Google's own photo guidelines — as depicting THIS clinic.
So the two easy options are both wrong: a stock photo of someone else's clinic
misrepresents the premises, and an AI-generated interior invents a room that
does not exist. For a medical practice that is not a style choice, it is a
claim about a building.

What is honest is a graphic that is obviously a graphic. These cards use the
practice's own brand — Gabarito and Manrope, the porcelain and navy from the
fascia board — and the practice's own 46 commissioned medical illustrations.
Nothing here depicts a place or a person. The photographs of the actual clinic
still have to be taken; these are not a substitute for them and the sheet in
outputs/profile-sheet.md still says so.

THE ILLUSTRATIONS ARE USED UNLABELLED ON PURPOSE. On the site their labels are
HTML positioned over the artwork, not baked into the file, so the raw .webp is
the clean drawing. That is the right form here anyway: label text sized for a
web page is illegible in a 1200x900 card seen on a phone.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
DIAGRAMS = HERE.parent / "site" / "assets" / "img" / "diagrams"
FONTS = HERE.parent / "signage" / "fonts"
BRAND = HERE.parent / "brand"

# Google's recommended post image is 1200x900. Rendered at 2x so the type is
# crisp after Google's own downscale, which is unsharpened and unforgiving.
W, H = 1200, 900
SCALE = 2

PAPER = "#F8F5F3"        # porcelain, and the illustrations' own background —
INK = "#1E3A63"          # so artwork meets card with no visible seam
SITE = "drvarada.com"

# IN THESE FILENAMES "light" AND "dark" NAME THE BACKGROUND, NOT THE INK.
#
# `logo-mark-light.svg` is filled #1E3A63 — it is the navy mark FOR a light
# background. Reading it as "the light-coloured one" and putting it on the navy
# band gives navy on navy: only the anti-aliased edges survive, which does not
# look like a missing logo, it looks like a broken one.
#
# The footer mark is the MONO white rather than the multi-tone `-dark` variant
# on purpose. At 40px the six tints in that file collapse into mush; one flat
# colour holds its shape.
FOOT_MARK = "logo-mark-mono-light.svg"     # white — for the navy band
ART_MARK = "logo-mark-flat-navy.svg"       # navy  — for the porcelain panel

# Each card is a headline and one supporting line. The POST body — the longer
# text a reader sees under the image — is `body`, and it is not drawn on the
# card: text baked into an image cannot be read by a screen reader, cannot be
# translated, and is not indexed.
POSTS = [
    {
        "id": "1-name-change",
        "art": None,              # brand card: the mark, not a diagram
        # New name first, former name under it — the same order as the
        # fascia board and the listing title. Leading with "Formerly" made
        # the retired name the headline, which is the one thing this post
        # exists to stop doing.
        "head": "Dr. Varada's\nSkin & Hair Center",
        "sub": "Formerly BNR Skin & Vitiligo Hospital. "
               "Same doctor, same address.",
        "body": (
            "Dr. Varada's Skin & Hair Center is the practice formerly known "
            "as BNR Skin & Vitiligo Hospital. Same doctor, same address in "
            "Karkhana, same records. Dr. (Lt Col) Khagendra Varada has "
            "practised dermatology for 45 years, including 25 in the Army "
            "Medical Corps. Appointments on WhatsApp."),
        "cta": "Learn more",
        "url": "https://drvarada.com/about/dr-khagendra-varada/",
    },
    {
        "id": "2-vitiligo-surgery",
        "art": "D3-melanocyte-transplant.webp",
        "head": "Vitiligo surgery",
        "sub": "For stable patches that have stopped responding to light.",
        "body": (
            "For vitiligo that has stayed stable, surgery can move pigment "
            "cells into patches that have stopped responding to light "
            "treatment — including melanocyte transplantation. Stability "
            "matters more than how long you have had it. Assessed case by "
            "case at the clinic in Karkhana."),
        "cta": "Learn more",
        "url": "https://drvarada.com/vitiligo/graft-surgery/",
    },
    {
        "id": "3-phototherapy",
        "art": "D1-phototherapy.webp",
        "head": "Narrowband UVB\nphototherapy",
        "sub": "A course, not a single visit.",
        "body": (
            "Narrowband UVB phototherapy is a course, not a single visit — "
            "usually two or three sessions a week over several months, done "
            "at the clinic. It is used for vitiligo and for psoriasis. We "
            "will tell you at the first consultation roughly how long a "
            "course is likely to run."),
        "cta": "Learn more",
        "url": "https://drvarada.com/vitiligo/phototherapy/",
    },
    {
        "id": "4-online-consultation",
        "art": "E1-examination.webp",
        "head": "Online consultations",
        "sub": "For patients outside Secunderabad.",
        "body": (
            "Video consultations are available for patients outside "
            "Secunderabad, at \u20b9699 plus GST. Where an online "
            "consultation turns out to need an in-person examination, only "
            "the difference in fee is charged. Booked on WhatsApp."),
        "cta": "Learn more",
        "url": "https://drvarada.com/online-consultation/",
    },
    {
        "id": "5-scalp-psoriasis",
        "art": "C4-seborrhoeic-dermatitis.webp",
        "head": "Scalp psoriasis,\nor dandruff?",
        "sub": "They look similar. They are treated differently.",
        "body": (
            "Persistent scalp flaking is not always dandruff. Scalp psoriasis "
            "is thicker, better defined at the edges, and often extends past "
            "the hairline — and it is treated differently. Worth having "
            "looked at rather than treated with shampoo indefinitely."),
        "cta": "Learn more",
        "url": "https://drvarada.com/psoriasis/scalp/",
    },
]


def chrome() -> str:
    """Same discovery order as verify.py and signage/render.py, so every tool
    in this project agrees on which browser drew the thing."""
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files\BraveSoftware\Brave-Browser\Application"
              r"\brave.exe",
              "google-chrome", "chromium"):
        if pathlib.Path(c).exists() or shutil.which(c):
            return c
    raise SystemExit("Chrome not found — install it or set the path here.")


def card_html(p: dict) -> str:
    if p["art"]:
        art = (f'<img src="../site/assets/img/diagrams/{p["art"]}" alt="">')
    else:
        art = f'<img class="mark" src="../brand/{ART_MARK}" alt="">'
    head = p["head"].replace("\n", "<br>")
    return f"""<meta charset="utf-8">
<style>
  @font-face {{ font-family: Gabarito;
    src: url(../signage/fonts/Gabarito.woff2) format('woff2'); }}
  @font-face {{ font-family: Manrope;
    src: url(../signage/fonts/Manrope.woff2) format('woff2'); }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: {W}px; height: {H}px; }}
  .card {{ width: {W}px; height: {H}px; display: flex;
           flex-direction: column; overflow: hidden; }}

  /* Artwork sits on the SAME porcelain the illustrations were drawn on, so
     there is no seam between the file and the card. `contain` because the 46
     drawings are not one aspect ratio and cropping a diagram loses the part
     that carries the meaning. */
  /* `min-height: 0` is load-bearing. A flex item defaults to
     `min-height: auto`, so this one refuses to shrink below the intrinsic
     height of the illustration inside it — and the band, which shrinks by
     default, silently absorbs the difference. That is what cut the footer
     off: the band was authored 360px tall and rendered about 264px, taking
     the logo and drvarada.com with it. Pin BOTH — art shrinks, band does
     not — or the card's identity depends on the aspect ratio of whichever
     drawing it happens to carry. */
  .art {{ flex: 1 1 0; min-height: 0; background: {PAPER}; display: flex;
          align-items: center; justify-content: center; padding: 34px; }}
  .art img {{ max-width: 92%; max-height: 100%; object-fit: contain; }}
  .art img.mark {{ max-width: 300px; max-height: 300px; }}

  /* Band height is set against the TALLEST card — a two-line headline plus a
     subline plus the footer rule. It was 322px and the footer overflowed off
     the bottom edge, which a PNG reports as success: the file is valid, the
     right size, and silently missing the only two elements that identify
     whose clinic this is. Measured, not guessed: 78 padding + 123 headline
     + 50 subline + 61 footer = 312, inside 360. */
  .band {{ flex: 0 0 360px; background: {INK}; color: #fff;
           padding: 42px 58px 36px; display: flex; flex-direction: column; }}
  h1 {{ font-family: Gabarito, sans-serif; font-weight: 700;
        font-size: 56px; line-height: 1.1; letter-spacing: -.5px; }}
  p {{ font-family: Manrope, sans-serif; font-weight: 500; font-size: 27px;
       line-height: 1.35; margin-top: 14px; color: rgba(255,255,255,.80); }}
  .foot {{ margin-top: auto; padding-top: 22px; display: flex;
           align-items: center; gap: 15px;
           border-top: 1px solid rgba(255,255,255,.22); }}
  /* Height only. The mark's viewBox is 473x662 — portrait, not square — so
     pinning both axes to 38px squashed it horizontally by nearly a third.
     Let width follow. */
  .foot img {{ height: 42px; width: auto; }}
  .foot span {{ font-family: Manrope, sans-serif; font-weight: 700;
                font-size: 25px; letter-spacing: .2px; }}
</style>
<div class="card">
  <div class="art">{art}</div>
  <div class="band">
    <h1>{head}</h1>
    <p>{p["sub"]}</p>
    <div class="foot">
      <img src="../brand/{FOOT_MARK}" alt="">
      <span>{SITE}</span>
    </div>
  </div>
</div>"""


def render(exe: str, p: dict) -> pathlib.Path:
    html = HERE / f"_{p['id']}.html"
    html.write_text(card_html(p), encoding="utf-8")
    png = OUT / f"{p['id']}.png"
    if png.exists():
        png.unlink()
    subprocess.run(
        [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--force-device-scale-factor={SCALE}",
         f"--window-size={W},{H}",
         f"--screenshot={png}", html.as_uri()],
        check=True, capture_output=True, timeout=120)
    html.unlink(missing_ok=True)
    return png


def audit(png: pathlib.Path) -> None:
    """Read the rendered card back and prove the footer is actually in it.

    A clipped card is a VALID PNG of the right dimensions and a plausible file
    size — the first version of this script made five of them, each missing
    the logo and drvarada.com, and nothing in the run said so. File size cannot
    see it; only the pixels can.

    So: crop the strip the footer occupies and count light pixels on the navy.
    White type and a white logo mark put a few percent of bright pixels there.
    A clipped card leaves the strip flat navy, or navy plus a hairline rule.
    """
    from PIL import Image                                    # noqa: PLC0415

    with Image.open(png) as im:
        if im.size != (W * SCALE, H * SCALE):
            raise SystemExit(f"{png.name}: {im.size}, expected "
                             f"{(W * SCALE, H * SCALE)}")
        # The footer row, in device pixels: above the 36px bottom padding,
        # about 44px tall to take in the mark and the wordmark.
        top = (H - 36 - 44) * SCALE
        strip = im.convert("L").crop((0, top, im.size[0], (H - 30) * SCALE))
        # `histogram()` rather than `getdata()`: same answer, stable API, and
        # it does not materialise a million-element list per card.
        bins = strip.histogram()
        light = sum(bins[151:]) / max(1, sum(bins))
    if light < 0.005:
        raise SystemExit(
            f"{png.name}: footer strip is {light:.3%} light pixels — the "
            "logo and drvarada.com are missing, almost certainly clipped by "
            "the band shrinking. The PNG is otherwise valid, which is why "
            "this check exists.")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    OUT.mkdir(parents=True, exist_ok=True)

    # Gate: a missing drawing renders a broken-image glyph, and a card with a
    # grey box where the artwork should be looks fine in a directory listing
    # and wrong on the profile. Fail before Chrome runs, not after.
    missing = [p["art"] for p in POSTS
               if p["art"] and not (DIAGRAMS / p["art"]).exists()]
    if missing:
        raise SystemExit(f"missing illustration(s): {', '.join(missing)}")

    # Gate: each mark must be inked to CONTRAST with the panel it sits on.
    # The filenames say "light"/"dark" meaning the background, and reading them
    # the other way puts navy on navy — which renders as a broken-looking
    # logo, not an absent one, so the footer pixel check still passes.
    for name, panel, want in ((FOOT_MARK, "navy band", "#FFFFFF"),
                              (ART_MARK, "porcelain panel", "#1E3A63")):
        svg = BRAND / name
        if not svg.exists():
            raise SystemExit(f"missing brand mark: {svg}")
        if want not in svg.read_text(encoding="utf-8"):
            raise SystemExit(
                f"{name} carries no {want} fill, so it will not read on the "
                f"{panel}. In these filenames 'light'/'dark' name the "
                "BACKGROUND, not the ink.")

    exe = chrome()
    print(f"\n  rendering {len(POSTS)} card(s) at {W}x{H} @{SCALE}x")
    for p in POSTS:
        png = render(exe, p)
        kb = png.stat().st_size / 1024
        # A card that failed to lay out is still a valid PNG, just a tiny one.
        if kb < 12:
            raise SystemExit(f"{png.name} is {kb:.0f} KB — no render")
        audit(png)
        print(f"    {png.name:<28} {kb:>7.0f} KB   footer ok")

    sheet = ["# Google Business Profile — posts", "",
             "Generated by `python posts.py`. Images in `out/`.", "",
             "Post under **Posts -> Add update** on the profile panel.",
             "image, paste the text, then **Add a button -> Learn more** and",
             "the URL. One every two weeks; they expire after ~6 months.",
             ""]
    for i, p in enumerate(POSTS, 1):
        sheet += [f"## {i}. {p['head'].replace(chr(10), ' ')}", "",
                  f"**Image:** `out/{p['id']}.png`  ",
                  f"**Button:** {p['cta']} -> {p['url']}", "",
                  "```", p["body"], "```", ""]
    (OUT / "posts.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    print(f"\n    text -> {OUT / 'posts.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
