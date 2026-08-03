"""The two entrance standees — 850 x 2000 mm roll-ups.

    python standee.py     -> out/standee-clinic.pdf, out/standee-booking.pdf

ONE ASKS "should I go in", THE OTHER ANSWERS "how do I book"
    Those are the only two questions someone standing at a clinic door has.
    Splitting them means each standee can be read in the four seconds a person
    gives it, from about two metres away, which is the constraint that sets
    every type size here.

THE BOTTOM 140 MM IS EMPTY ON PURPOSE
    A roll-up's banner feeds out of a cassette and the lowest stretch sits
    below knee height, behind the foot of whoever is reading it. Anything put
    there is paid for and never seen. `press.FOOT_MM` is that band; the layout
    reserves it rather than trusting a designer to remember.

NO FEES ON THESE
    The clinic's fees are published on the site and quoted in the WhatsApp
    conversation, both of which can be changed in a minute. A number printed
    2 metres tall can only be changed by reprinting the standee, and the day
    it stops being true it is a standee that argues with the receptionist.
    Same rule as prices in the WhatsApp catalogue artwork.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str((HERE / ".." / "site").resolve()))
sys.path.insert(0, str((HERE / ".." / "signage").resolve()))

import press                                                    # noqa: E402
from press import FOOT_MM, SHEETS, Gate, face, qr_svg           # noqa: E402
from chrome import (                                            # noqa: E402
    BRAND_PLAIN, CITY, FORMER_PLAIN, HOURS, PHONE_SHOW, PINCODE, REVIEWER,
    SITE, STREET, WHATSAPP,
)
from board import HINDI, NATIVE_REVIEW, TELUGU                   # noqa: E402
from card import svg                                             # noqa: E402

INK, NAVY, GREY = "#12202F", "#1E3A63", "#66707D"
MINT_SF, MINT_DP, MINT = "#DFF3EC", "#0B6353", "#8FDCC6"
NAME, QUALS = REVIEWER.split(", ", 1)

TREATS = ["Vitiligo", "Psoriasis", "Hair loss & grafting",
          "Acne & scarring", "Eczema & allergy", "Dermatosurgery"]

CSS = f"""
  .face {{ font-family: Manrope, 'Noto Sans Telugu', 'Noto Sans Devanagari',
           sans-serif; color: {INK}; }}
  .pad {{ position: absolute; top: 90mm; left: 70mm; right: 70mm;
          bottom: {FOOT_MM}mm; display: flex; flex-direction: column; }}
  .grow {{ flex: 1 1 auto; }}
  .lock svg {{ width: 300mm; height: auto; display: block; }}

  h1 {{ font-family: Gabarito, sans-serif; font-weight: 700; font-size: 78mm;
       line-height: 1.03; letter-spacing: -.025em; margin-top: 60mm; }}
  .sub {{ font-size: 26mm; line-height: 1.35; color: {GREY};
          margin-top: 22mm; font-weight: 600; }}
  .eyebrow {{ font-size: 18mm; font-weight: 800; letter-spacing: .08em;
              text-transform: uppercase; color: {MINT_DP}; }}

  .who {{ margin-top: 40mm; border-top: 3mm solid {INK}; padding-top: 22mm; }}
  .who .n {{ font-family: Gabarito, sans-serif; font-weight: 700;
             font-size: 38mm; line-height: 1.1; }}
  .who .q {{ font-size: 20mm; color: {GREY}; margin-top: 8mm;
             line-height: 1.4; }}

  .treats {{ display: flex; flex-wrap: wrap; gap: 10mm 14mm;
             margin-top: 34mm; }}
  .treats span {{ font-size: 24mm; font-weight: 700; background: {MINT_SF};
                  color: {MINT_DP}; padding: 9mm 16mm; border-radius: 99mm; }}

  .foot {{ border-top: 3mm solid {INK}; padding-top: 22mm; }}
  .foot .te {{ font-size: 30mm; line-height: 1.6; }}
  .foot .hi {{ font-size: 28mm; line-height: 1.6; }}
  .foot .ad {{ font-size: 19mm; line-height: 1.5; color: {GREY};
               margin-top: 10mm; }}
  .foot .hr {{ font-size: 22mm; font-weight: 800; margin-top: 8mm; }}

  /* ---- booking ---- */
  .booking .bleedbox {{ background: {MINT_SF}; }}
  .qr {{ width: 340mm; height: 340mm; background: #fff; padding: 20mm;
         border-radius: 12mm; margin: 46mm auto 0; }}
  .steps {{ margin-top: 46mm; }}
  .step {{ display: flex; gap: 16mm; align-items: baseline;
           padding: 12mm 0; border-bottom: 1mm solid rgba(11,99,83,.22); }}
  .step b {{ font-family: Gabarito, sans-serif; font-size: 34mm;
             color: {MINT}; flex: 0 0 40mm; }}
  .step span {{ font-size: 26mm; font-weight: 600; line-height: 1.3; }}
  .ph {{ font-family: Gabarito, sans-serif; font-weight: 700;
         font-size: 46mm; margin-top: 34mm; }}
  .ph small {{ display: block; font-family: Manrope, sans-serif;
               font-size: 18mm; font-weight: 700; color: {MINT_DP};
               letter-spacing: .06em; text-transform: uppercase;
               margin-bottom: 6mm; }}
"""

CLINIC = f"""<div class="bleedbox"></div><div class="pad">
  <div class="lock">{svg("lockups/logo-horizontal-light.svg")}</div>
  <h1>45 years of<br>dermatology,<br>in Karkhana.</h1>
  <div class="grow"></div>
  <!-- The band this opens up sits at chest height on a 2m banner, which is
       where a portrait of Dr. Varada belongs. It stays empty until there is
       photography shot for print: a web hero upscaled to 600mm is a blurred
       doctor, which is worse than no doctor. -->
  <div class="who">
    <div class="n">{NAME}</div>
    <div class="q">{QUALS}<br>Consultant Dermatologist &amp;
        Dermatosurgeon</div>
  </div>
  <div class="treats">{"".join(f"<span>{t}</span>" for t in TREATS)}</div>
  <div class="grow"></div>
  <div class="foot">
    <div class="te">{TELUGU}</div>
    <div class="hi">{HINDI}</div>
    <div class="ad">{STREET}, {CITY} {PINCODE}<br>
        Formerly {FORMER_PLAIN} &middot; {SITE.split("//")[1]}</div>
    <div class="hr">{HOURS}</div>
  </div>
</div>"""

BOOKING = f"""<div class="bleedbox"></div><div class="pad">
  <div class="eyebrow">Consult from anywhere</div>
  <h1 style="margin-top:26mm">Book on<br>WhatsApp.</h1>
  <div class="sub">Video consultation with Dr. Varada, or an
      appointment at the clinic. Both start the same way.</div>
  <div class="qr">{qr_svg(WHATSAPP)}</div>
  <div class="steps">
    <div class="step"><b>1</b><span>Scan with your phone camera</span></div>
    <div class="step"><b>2</b><span>Tell us what the problem is</span></div>
    <div class="step"><b>3</b><span>We reply with the next
        available time</span></div>
  </div>
  <div class="grow"></div>
  <div class="ph"><small>Or call</small>{PHONE_SHOW}</div>
</div>"""


def main() -> None:
    lang_gate = Gate("Telugu & Hindi (clinic name, imported from signage)",
                     True, NATIVE_REVIEW.split(";")[0], "2026-08-02")
    size_gate = Gate("Fabricator's banner size confirmed", False)
    ok = 0
    for stem, art, cls, gates in (
            ("standee-clinic", CLINIC, "", [lang_gate, size_gate]),
            ("standee-booking", BOOKING, "booking", [size_gate])):
        ok += press.render(stem, SHEETS["standee"],
                           [face(art, stem.split("-")[1], cls=cls)],
                           CSS, title=f"{BRAND_PLAIN} — {stem}",
                           gates=gates, proof_px=900)
    print(f"\n  {ok}/2 press-ready. 850x2000mm is the Indian roll-up standard "
          f"and a GUESS for your\n  fabricator - get the banner size from them,"
          f" set it in press.SHEETS['standee'],\n  and re-run. The layout "
          f"re-proportions; nothing needs redrawing.\n")


if __name__ == "__main__":
    main()
