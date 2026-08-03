"""Business card for Dr. (Lt Col) Khagendra Varada — 90 x 54 mm, two sides.

    python card.py     -> out/card.pdf, out/card-proof.png

FRONT is the person. BACK is how to reach the clinic without typing anything:
a QR that opens a WhatsApp chat, because WhatsApp is the clinic's only booking
path, and a card that still needs a number keyed in has made the patient do the
one step that loses them.

WHY THE ADDRESS IS IN ENGLISH ON A CARD THAT CARRIES TELUGU AND HINDI
    The two Indic lines here are the clinic NAME, and they are the exact
    strings a native speaker read and cleared for the signage on 2026-08-02
    — imported from `../signage/board.py`, not retyped. Retyping is how "Center" becomes
    "Centre" and nobody notices until it is printed.

    A translated street address would be new, uncleared text, and it would also
    be the wrong call: Indian postal addresses are written in English even on
    Telugu shopfronts, because that is what a courier, a maps search and an
    auto driver all read. So the name greets in three scripts and the address
    stays in the one that gets someone to the door.

WHY THE PHONE NUMBER AND THE QR ARE THE SAME NUMBER
    They are both `PHONE_SHOW` / `WHATSAPP` from `../site/chrome.py`, which
    resolve to +91 80088 55330. If those two ever disagree, the card offers two
    clinics. Same single-source rule as everything else in this project.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str((HERE / ".." / "site").resolve()))
sys.path.insert(0, str((HERE / ".." / "signage").resolve()))

import press                                                    # noqa: E402
from press import SHEETS, Gate, face, qr_svg                    # noqa: E402
from chrome import (                                            # noqa: E402
    CITY, FORMER_PLAIN, HOURS, PHONE_ALT_SHOW, PHONE_LANDLINE_SHOW,
    PHONE_SHOW, PINCODE, REVIEWER, SITE, STREET, WHATSAPP,
)
from board import HINDI, NATIVE_REVIEW, TELUGU                   # noqa: E402

BRAND_DIR = (HERE / ".." / "brand").resolve()

INK, NAVY, GREY = "#12202F", "#1E3A63", "#66707D"
MINT_SF, MINT_DP, MINT = "#DFF3EC", "#0B6353", "#8FDCC6"

# "Dr. (Lt Col) Khagendra Varada, MBBS, Dip. Practical Dermatology (Cardiff)"
# is one constant on the site because it is one credit line there. A card sets
# the name and the letters differently, so it splits rather than duplicating.
NAME, QUALS = REVIEWER.split(", ", 1)
ROLE = "Consultant Dermatologist & Dermatosurgeon"


def svg(rel: str) -> str:
    """Inline a brand SVG. Inline, so it stays vector all the way to the PDF.

    An <img src> to a file:// URL would rasterise at the proof's device scale
    and print at that resolution; the lockups' letterforms are already
    outlined, so inlining costs nothing and keeps the edges true at any size.
    """
    raw = (BRAND_DIR / rel).read_text(encoding="utf-8")
    return raw.split("?>")[-1].strip()


CSS = f"""
  .face {{ font-family: Manrope, 'Noto Sans Telugu', 'Noto Sans Devanagari',
           sans-serif; color: {INK}; -webkit-font-smoothing: antialiased; }}
  /* 8mm from the page edge is 5mm inside the trim — one more than `safe`
     demands. Safe is where the guillotine stops being a risk; 5mm is where a
     card stops looking like it was laid out to the edge of the allowed. */
  .pad {{ position: absolute; inset: 8mm; display: flex;
          flex-direction: column; justify-content: space-between; }}

  /* ---- front ---- */
  .lock svg {{ width: 44mm; height: auto; display: block; }}
  .who h1 {{ font-family: Gabarito, sans-serif; font-weight: 700;
             font-size: 5mm; line-height: 1.05; letter-spacing: -.02em;
             color: {INK}; }}
  .who .q {{ font-size: 2.5mm; line-height: 1.35; color: {GREY};
             margin-top: 1.4mm; }}
  .who .r {{ font-size: 2.5mm; font-weight: 700; color: {MINT_DP};
             margin-top: .8mm; letter-spacing: .01em; }}
  .rule {{ height: .45mm; width: 12mm; background: {MINT}; margin: 2.6mm 0; }}
  .foot {{ display: flex; justify-content: space-between;
           align-items: flex-end; font-size: 2.5mm; line-height: 1.45; }}
  .foot b {{ font-weight: 700; }}
  .foot .site {{ font-weight: 700; color: {NAVY}; }}

  /* ---- back ---- */
  .back .bleedbox {{ background: {MINT_SF}; }}
  .back .pad {{ flex-direction: row; align-items: center; gap: 5mm; }}
  .qr {{ width: 25mm; height: 25mm; flex: 0 0 25mm; background: #fff;
         padding: 1.6mm; border-radius: 1.2mm; }}
  .qr svg {{ display: block; }}
  .say {{ font-size: 2.7mm; font-weight: 800; color: {MINT_DP};
          letter-spacing: .02em; }}
  .te {{ font-size: 3.5mm; line-height: 1.5; margin-top: 1.6mm;
         color: {INK}; }}
  .hi {{ font-size: 3.3mm; line-height: 1.5; color: {INK}; }}
  .addr {{ font-size: 2.35mm; line-height: 1.42; color: {GREY};
           margin-top: 1.8mm; }}
  .hrs {{ font-size: 2.35mm; font-weight: 700; color: {INK};
          margin-top: 1mm; }}
"""

FRONT = f"""<div class="bleedbox"></div><div class="pad">
  <div class="lock">{svg("lockups/logo-horizontal-light.svg")}</div>
  <div class="who">
    <div class="rule"></div>
    <h1>{NAME}</h1>
    <div class="q">{QUALS}</div>
    <div class="r">{ROLE}</div>
  </div>
  <div class="foot">
    <div><b>{PHONE_SHOW}</b><br>{PHONE_ALT_SHOW} &middot;
         {PHONE_LANDLINE_SHOW}</div>
    <div class="site">{SITE.split("//")[1]}</div>
  </div>
</div>"""

BACK = f"""<div class="bleedbox"></div><div class="pad">
  <div class="qr">{qr_svg(WHATSAPP)}</div>
  <div>
    <div class="say">Scan to book on WhatsApp</div>
    <div class="te">{TELUGU}</div>
    <div class="hi">{HINDI}</div>
    <div class="addr">{STREET},<br>{CITY} {PINCODE}<br>
         Formerly {FORMER_PLAIN}</div>
    <div class="hrs">{HOURS}</div>
  </div>
</div>"""


def main() -> None:
    ok = press.render(
        "card", SHEETS["card"],
        [face(FRONT, "front"), face(BACK, "back", cls="back")],
        CSS, title=f"{NAME} — business card",
        gates=[
            # The Indic strings are the signage's, already cleared. The gate
            # names that provenance so the next person can see WHY this one is
            # green when the fliers' equivalent gate is not.
            Gate("Telugu & Hindi (clinic name, imported from signage)",
                 True, NATIVE_REVIEW.split(";")[0], "2026-08-02"),
        ])
    print(f"\n  {'press-ready' if ok else 'NOT press-ready'}"
          f" · give the printer out/card.pdf — 90x54mm trimmed, 3mm bleed,"
          f" 300+ dpi not applicable (vector)\n")


if __name__ == "__main__":
    main()
