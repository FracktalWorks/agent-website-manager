"""Render the procedure fliers — A5, two sides, one PDF per condition+language.

    python flier.py                 -> all twelve
    python flier.py vitiligo        -> the three vitiligo fliers
    python flier.py vitiligo te     -> one

FRONT is the condition: what it is, what it is not, and the five facts a
patient needs before they can ask a sensible question. BACK is what the clinic
does about it, the honest limit, and a QR that opens a WhatsApp chat.

WHY THE HONEST LIMIT GETS ITS OWN TITLED SECTION
    Every clinic flier in this category ends with a disclaimer in 6pt grey. The
    clinic's position — on the site, on the signage and here — is the opposite:
    that vitiligo and psoriasis cannot be cured is not the small print, it is
    the reason to trust the rest of the page. So `truth` is set at the same
    size as the treatments and given a heading, on a mint field that the eye
    lands on before the treatment list.

WHY SOME OF THESE WILL NOT WRITE A PRINT PDF
    The Telugu and Hindi for hair loss and acne were written for this flier and
    have never been read by a native speaker (see `fliers.py`). They render
    correctly, which is not the same as reading correctly, and print is
    one-way. Those six get a stamped proof to circulate for review and no
    press file. The six whose copy came from pages already published
    in-language are press-ready.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str((HERE / ".." / "site").resolve()))
sys.path.insert(0, str((HERE / ".." / "signage").resolve()))

import fliers                                                   # noqa: E402
import press                                                    # noqa: E402
from press import SHEETS, Gate, face, qr_svg                    # noqa: E402
from chrome import (                                            # noqa: E402
    BRAND_PLAIN, CITY, HOURS, PHONE_SHOW, PINCODE, REVIEWER, SITE, STREET,
    WHATSAPP,
)
from board import NATIVE_REVIEW                                  # noqa: E402
from card import svg                                             # noqa: E402

INK, NAVY, GREY = "#12202F", "#1E3A63", "#66707D"
MINT_SF, MINT_DP, MINT, GROUND = "#DFF3EC", "#0B6353", "#8FDCC6", "#F5F7F8"
NAME = REVIEWER.split(", ", 1)[0]
QUALS = REVIEWER.split(", ", 1)[1]

CSS = f"""
  .face {{ font-family: Manrope, 'Noto Sans Telugu', 'Noto Sans Devanagari',
           sans-serif; color: {INK}; -webkit-font-smoothing: antialiased; }}
  .pad {{ position: absolute; inset: 15mm 14mm; display: flex;
          flex-direction: column; }}
  .grow {{ flex: 1 1 auto; }}

  .lock svg {{ width: 46mm; height: auto; display: block; }}
  .eyebrow {{ font-size: 3.1mm; font-weight: 800; letter-spacing: .06em;
              text-transform: uppercase; color: {MINT_DP}; margin-top: 9mm; }}
  h1 {{ font-family: Gabarito, sans-serif; font-weight: 700; font-size: 9mm;
        line-height: 1.08; letter-spacing: -.02em; margin-top: 2.5mm; }}
  /* Indic scripts carry ascenders and descenders that Latin does not, so a
     line height tuned on English collides in Telugu. Per script, not once. */
  .te h1, .hi h1 {{ font-size: 7.6mm; line-height: 1.42; letter-spacing: 0; }}
  .lede {{ font-size: 3.9mm; line-height: 1.55; color: {INK};
           margin-top: 4mm; }}
  .te .lede, .hi .lede {{ line-height: 1.72; }}

  .glance {{ margin-top: 8mm; border-top: .3mm solid {MINT}; }}
  .g {{ display: flex; gap: 4mm; padding: 2.6mm 0;
        border-bottom: .2mm solid #E3E8EA; }}
  .g dt {{ flex: 0 0 34mm; font-size: 3mm; font-weight: 800; color: {GREY};
           line-height: 1.4; }}
  .g dd {{ font-size: 3.2mm; line-height: 1.4; font-weight: 600; }}
  .te .g dt, .hi .g dt {{ line-height: 1.6; }}
  .te .g dd, .hi .g dd {{ line-height: 1.6; }}

  .sec {{ font-size: 3.1mm; font-weight: 800; letter-spacing: .06em;
          text-transform: uppercase; color: {MINT_DP}; }}
  .t {{ display: flex; gap: 4mm; padding: 3mm 0;
        border-bottom: .2mm solid #E3E8EA; }}
  .t b {{ flex: 0 0 36mm; font-size: 3.3mm; font-weight: 800; }}
  .t span {{ font-size: 3.1mm; line-height: 1.45; color: {GREY}; }}
  .te .t span, .hi .t span {{ line-height: 1.62; }}

  .truth {{ background: {MINT_SF}; padding: 6mm; margin-top: 8mm;
            border-radius: 2mm; }}
  .truth p {{ font-size: 3.3mm; line-height: 1.55; margin-top: 2.5mm;
              font-weight: 600; }}
  .te .truth p, .hi .truth p {{ line-height: 1.72; }}

  .book {{ display: flex; gap: 6mm; align-items: center; margin-top: 8mm;
           border-top: .5mm solid {INK}; padding-top: 6mm; }}
  .book .qr {{ width: 30mm; height: 30mm; flex: 0 0 30mm; }}
  .book .say {{ font-size: 3.4mm; font-weight: 800; color: {MINT_DP}; }}
  .book .who {{ font-size: 3mm; font-weight: 800; margin-top: 2.5mm; }}
  .book .q {{ font-size: 2.7mm; color: {GREY}; line-height: 1.4; }}
  .book .addr {{ font-size: 2.7mm; color: {GREY}; line-height: 1.45;
                 margin-top: 2mm; }}
  .book .ph {{ font-size: 3.6mm; font-weight: 800; margin-top: 1.5mm; }}
  .url {{ font-size: 2.7mm; color: {NAVY}; font-weight: 700; margin-top: 4mm;
          text-align: center; }}
  .fstrip {{ display: flex; justify-content: space-between;
             align-items: baseline; border-top: .5mm solid {INK};
             padding-top: 3mm; font-size: 2.9mm; }}
  .fstrip b {{ font-weight: 800; }}
  .fstrip span {{ color: {GREY}; }}
"""


def front(f: dict, ui: dict) -> str:
    rows = "".join(f'<div class="g"><dt>{k}</dt><dd>{v}</dd></div>'
                   for k, v in f["glance"])
    return f"""<div class="bleedbox"></div><div class="pad">
  <div class="lock">{svg("lockups/logo-horizontal-light.svg")}</div>
  <div class="eyebrow">{f["eyebrow"]}</div>
  <h1>{f["h1"]}</h1>
  <p class="lede">{f["lede"]}</p>
  <div class="sec" style="margin-top:9mm">{ui["at"]}</div>
  <dl class="glance">{rows}</dl>
  <div class="grow"></div>
  <div class="fstrip">
    <b>{BRAND_PLAIN}</b><span>{SITE.split("//")[1]} · {PHONE_SHOW}</span>
  </div>
</div>"""


def back(f: dict, ui: dict) -> str:
    rows = "".join(f'<div class="t"><b>{n}</b><span>{d}</span></div>'
                   for n, d in f["treat"])
    return f"""<div class="bleedbox"></div><div class="pad">
  <div class="sec">{ui["offer"]}</div>
  <div class="list">{rows}</div>
  <div class="grow"></div>
  <div class="truth">
    <div class="sec">{ui["truth"]}</div>
    <p>{f["truth"]}</p>
  </div>
  <div class="book">
    <div class="qr">{qr_svg(WHATSAPP)}</div>
    <div>
      <div class="say">{ui["book"]}</div>
      <div class="who">{NAME}</div>
      <div class="q">{QUALS}</div>
      <div class="addr">{STREET},<br>{CITY} {PINCODE} &middot; {HOURS}</div>
      <div class="ph">{PHONE_SHOW}</div>
    </div>
  </div>
  <div class="url">{ui["more"]}: {f["url"].split("//")[1]}</div>
</div>"""


def build(f: dict) -> bool:
    ui = fliers.UI[f["lang"]]
    lang = f["lang"]
    reviewed = f["source"] is fliers.PUBLISHED
    gates = []
    if lang != "en":
        gates.append(Gate(
            f"{fliers.LANG_NAME[lang]} copy",
            reviewed,
            (NATIVE_REVIEW.split(";")[0] if reviewed else ""),
            "already published in-language on drvarada.com" if reviewed
            else ""))
    # Every flier states what a treatment does and does not do, so the clinical
    # sign-off is a separate question from the language one and is asked of a
    # different person. Same rule as the diagrams: Dr. Varada reads it first.
    gates.append(Gate("Clinical review (Dr. Varada)", False))
    return press.render(
        f"flier-{f['slug']}-{lang}", SHEETS["a5"],
        [face(front(f, ui), f"{f['slug']} {lang} · front", cls=lang),
         face(back(f, ui), f"{f['slug']} {lang} · back", cls=lang)],
        CSS, title=f"{f['slug']} flier ({fliers.LANG_NAME[lang]})",
        gates=gates, proof_px=1400)


def main() -> None:
    want = sys.argv[1:]
    chosen = [f for f in fliers.FLIERS
              if (not want)
              or (f["slug"] == want[0]
                  and (len(want) < 2 or f["lang"] == want[1]))]
    if not chosen:
        raise SystemExit(f"no flier matches {want}")
    ready = sum(build(f) for f in chosen)
    print(f"\n  {ready}/{len(chosen)} press-ready. The rest are proofs "
          f"awaiting sign-off - circulate out/*-proof.png, not the PDFs.\n")


if __name__ == "__main__":
    main()
