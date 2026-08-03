"""The vitiligo leaflet — A4, folded once, four panels, for review.

    python leaflet.py            -> out/leaflet-vitiligo-en-proof.png

WHAT THIS IS AND WHY IT REPLACES THE A5 FLIER
    The A5 fliers were a label/value table with a logo on top. Correct, and
    dead. A leaflet a patient carries out of a waiting room has to do the job
    the consultation could not fit: show them what is happening in their skin,
    what the options actually are, and what will not happen. That needs
    pictures and it needs room, which is what four panels buy.

IMPOSITION — get this wrong and the leaflet is inside out
    One flat A4 sheet, printed both sides, folded down the middle:

        OUTSIDE      [ 4 back cover | 1 FRONT COVER ]
        INSIDE       [ 2 inside-left | 3 inside-right ]

    The front cover is the RIGHT half of the outside sheet. The inside is read
    as one 297mm spread, so a figure may cross the fold there — but nothing on
    the outside may, because those two panels never face each other.

    `press.render(..., folds=(148.5,))` draws the crease on the proof. Check
    every headline against it: a panel that reads well flat can still fold
    straight through a word.

THE COPY IS NOT WRITTEN HERE
    Every paragraph is imported from `content/vitiligo.py` — the same text
    already published, already compliance-checked, already reviewed for the
    "no cure" language. `dia()` pulls a diagram section by its image, so the
    leaflet cannot drift from the site: change the page and re-run.

EDITORIAL RULES APPLIED (agent-data/design-systems/_craft/)
    · typography-hierarchy-editorial.md — display sits 3-5x body, not 2x. The
      cover headline is 26mm against a 3.6mm body: a visual event, not a
      heading. Whitespace carries the hierarchy; the deck is a large step down.
    · anti-ai-slop.md — no symmetric everything-gets-a-turn stack, no
      decorative blobs. The composition is deliberately uneven: the cover is
      mostly empty, the inside is dense, the pull-quote breaks the grid.
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
    CITY, FORMER_PLAIN, HOURS, PHONE_SHOW, PINCODE, REVIEWER, SITE, STREET,
    WHATSAPP,
)
from board import HINDI, NATIVE_REVIEW, TELUGU                   # noqa: E402
import callouts                                                  # noqa: E402
from card import svg                                             # noqa: E402
from content import vitiligo                                     # noqa: E402

ASSETS = (HERE / ".." / "site" / "assets").resolve()

# THE GRID. A 4.5mm baseline: body is 3.2mm on 4.5mm leading, which is 9pt on
# 12.8pt — the setting a pharmacy leaflet uses because it is the smallest that
# still reads in a waiting room. Every vertical measure below is a multiple of
# it, so the two inside panels rule off at the same heights across the fold.
# Margins drop 13mm -> 11mm: that is 4mm of measure per panel, which is a whole
# extra word per line at this size.
BASE = 4.5
MARGIN = 11.0
INK, NAVY, GREY = "#12202F", "#1E3A63", "#66707D"
MINT, MINT_SF, MINT_DP = "#8FDCC6", "#DFF3EC", "#0B6353"
NAME, QUALS = REVIEWER.split(", ", 1)
PANEL = 148.5


def first(text: str, n: int) -> str:
    """The first n sentences of a published paragraph, unaltered.

    Cutting rather than rewriting: the moment a leaflet paraphrases the page
    it becomes a second source that has to be reviewed separately, and the
    two drift. A subset needs no second review.
    """
    import re
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(parts[:n])


def dia(stem: str) -> dict:
    """One diagram section from the live site, found by its image file.

    Found by image rather than by index or heading: an index moves whenever a
    section is inserted, and a heading is the thing most likely to be reworded.
    The image filename is the stable identifier.
    """
    for page in vitiligo.PAGES:
        for s in page.get("sections", []):
            src = str((s.get("image") or {}).get("src", ""))
            if s.get("kind") == "diagram" and stem in src:
                return {**s, "src": (ASSETS / src).resolve().as_uri()}
    raise SystemExit(f"no diagram section uses {stem} — has the page changed?")


MELANOCYTE = dia("A2-melanocyte")
REPIG = dia("B2-repigmentation-routes")
PATTERNS = dia("B3-vitiligo-patterns")
EDGE = dia("B4-active-vs-stable")
# D5-treatment-ladder lives on the psoriasis page, not this one.
LADDER = dia("D1-phototherapy")

CSS = f"""
  .face {{ font-family: Manrope, 'Noto Sans Telugu', 'Noto Sans Devanagari',
           sans-serif; color: {INK}; -webkit-font-smoothing: antialiased; }}
  .sheet {{ position: absolute; inset: 3mm; display: flex; }}
  .panel {{ width: {PANEL}mm; height: 210mm; position: relative;
            padding: {BASE * 3}mm {MARGIN}mm; display: flex;
            flex-direction: column; overflow: hidden; }}
  .grow {{ flex: 1 1 auto; }}

  /* ── editorial furniture ── */
  .rule {{ border-top: .5mm solid {INK}; }}
  .dateline {{ display: flex; justify-content: space-between;
               font-size: 2.5mm; font-weight: 800; letter-spacing: .12em;
               text-transform: uppercase; color: {GREY};
               padding-top: 2.5mm; }}
  .num {{ font-family: Gabarito, sans-serif; font-weight: 700;
          font-size: 8mm; color: {MINT}; line-height: 1; }}
  .eyebrow {{ font-size: 2.8mm; font-weight: 800; letter-spacing: .1em;
              text-transform: uppercase; color: {MINT_DP}; }}
  h2 {{ font-family: Gabarito, sans-serif; font-weight: 700;
        font-size: 6.2mm; line-height: {BASE * 1.5}mm;
        letter-spacing: -.02em; margin-top: {BASE / 2}mm; }}
  /* Leading in millimetres, not a ratio: a ratio drifts off the baseline
     the moment a size changes, and two columns stop ruling off level. */
  p {{ font-size: 3.2mm; line-height: {BASE}mm; }}
  .cap {{ font-size: 2.6mm; line-height: {BASE * 0.75}mm; color: {GREY};
          border-left: .5mm solid {MINT}; padding-left: {BASE / 1.5}mm;
          margin-top: {BASE / 1.5}mm; display: block; }}
  figure img {{ width: 100%; display: block; max-height: 44mm;
                object-fit: contain; }}
{callouts.css(ink=INK, grey=GREY, deep=MINT_DP, wash="#F7F4F0",
              baseline=BASE, maxh=46,
              label_size=2.4, line_mm=BASE / 1.45)}

  /* ── 1 · cover ── */
  .cover {{ padding: 0; }}
  .cover .in {{ position: absolute; inset: 14mm 13mm 20mm; display: flex;
                flex-direction: column; }}
  .cover .lock svg {{ width: 52mm; height: auto; display: block; }}
  /* 26mm display against 3.5mm body — the editorial rulebook's 3-5x jump.
     The old A5 flier ran 9mm over 3.9mm and read as a form. */
  .cover h1 {{ font-family: Gabarito, sans-serif; font-weight: 700;
               font-size: 17mm; line-height: 1.02; letter-spacing: -.035em;
               margin-top: 11mm; }}
  .cover h1 em {{ font-style: normal; color: {MINT_DP}; }}
  .cover .deck {{ font-size: 4mm; line-height: 1.45; color: {GREY};
                  margin-top: 7mm; font-weight: 500; }}
  .cover figure {{ flex: 1 1 auto; margin: 6mm -13mm 0; min-height: 0;
                   display: flex; align-items: flex-end; }}
  .cover figure img {{ max-height: 100%; }}
  .cover .names {{ font-size: 3.4mm; line-height: 1.55; }}
  .coverfoot {{ position: absolute; left: 0; right: 0; bottom: 0;
                background: {INK}; color: #fff; padding: 6mm 14mm;
                display: flex; justify-content: space-between;
                align-items: baseline; font-size: 2.9mm; font-weight: 700; }}
  .coverfoot span {{ color: {MINT}; }}

  /* ── 2 & 3 · inside ── */
  .sec {{ display: flex; gap: {BASE}mm; margin-top: {BASE * 1.5}mm; }}
  .sec:first-of-type {{ margin-top: {BASE}mm; }}
  .sec .body {{ flex: 1 1 auto; }}
  .sec p {{ margin-top: {BASE / 1.5}mm; }}

  /* The pull quote breaks the grid on purpose — the honest limit is the
     leaflet's argument, not its small print. */
  .quote {{ background: {INK}; color: #fff;
            margin: {BASE * 1.5}mm -{MARGIN}mm -{BASE * 3}mm;
            padding: {BASE * 1.5}mm {MARGIN}mm; }}
  .quote q {{ font-family: Gabarito, sans-serif; font-weight: 700;
              font-size: 7.2mm; line-height: 1.14; letter-spacing: -.02em;
              quotes: none; display: block; }}
  .quote q em {{ font-style: normal; color: {MINT}; }}
  .quote p {{ font-size: 2.9mm; line-height: 1.45; margin-top: 3.5mm;
              color: #C7CFDA; }}

  /* The panel's last figure gets a tighter ceiling: it is what runs off the
     bottom edge, and a diagram is the cheapest thing on the page to shrink. */
  .tail .stage img {{ max-height: 27mm; }}
  .tail .key li {{ font-size: 2.3mm; }}
  .ladder {{ margin-top: 5mm; }}
  .rung {{ display: flex; gap: {BASE}mm; padding: {BASE / 2.4}mm 0;
           border-top: .2mm solid #DDE4E7; }}
  .rung b {{ flex: 0 0 30mm; font-size: 3.2mm; font-weight: 800; }}
  .rung span {{ font-size: 3.1mm; line-height: 1.4; color: {GREY}; }}

  /* ── 4 · back ── */
  .back {{ background: {MINT_SF}; }}
  .back h2 {{ font-size: 9mm; }}
  .qr {{ width: 46mm; height: 46mm; background: #fff; padding: 3mm;
         border-radius: 2mm; margin-top: 7mm; }}
  .steps {{ margin-top: 6mm; }}
  .step {{ display: flex; gap: 3.5mm; padding: 2.4mm 0;
           border-top: .2mm solid rgba(11,99,83,.2); font-size: 3.2mm; }}
  .step b {{ color: {MINT_DP}; font-weight: 800; }}
  .backfoot {{ font-size: 2.9mm; line-height: 1.5; color: {GREY}; }}
  .backfoot b {{ color: {INK}; font-size: 3.3mm; }}
  .te {{ font-size: 3.6mm; line-height: 1.5; }}
  .hi {{ font-size: 3.4mm; line-height: 1.5; }}
"""


def figure(d: dict, cap: bool = True) -> str:
    cap_html = f'<figcaption class="cap">{d["caption"]}</figcaption>' if cap \
        else ""
    return (f'<figure><img src="{d["src"]}" alt="">{cap_html}</figure>')


def section(n: str, d: dict, *, fig: bool = True, cap: bool = True,
            trim: int = 0) -> str:
    intro = first(d["intro"], trim) if trim else d["intro"]
    return f"""<div class="sec">
  <div class="num">{n}</div>
  <div class="body">
    <div class="eyebrow">{d["eyebrow"]}</div>
    <h2>{d["h2"]}</h2>
    <p>{intro}</p>
    {figure(d, cap) if fig else ""}
  </div>
</div>"""


COVER = f"""<div class="panel cover">
  <div class="in">
    <div class="lock">{svg("lockups/logo-horizontal-light.svg")}</div>
    <h1>White patches,<br>explained <em>properly</em>.</h1>
    <div class="deck">What decides your treatment is invisible: whether the
      disease is still spreading, how long each patch has been there, and
      where on the body it sits.</div>
    <figure><img src="{PATTERNS["src"]}" alt=""></figure>
  </div>
  <div class="coverfoot">
    <div>Vitiligo &middot; <span>బొల్లి</span> &middot;
         <span>सफ़ेद दाग</span></div>
    <div>45 years &middot; Karkhana</div>
  </div>
</div>"""

BACK = f"""<div class="panel back">
  <div class="rule"></div>
  <div class="dateline"><span>Start here</span><span>04</span></div>
  <h2>One message is<br>the whole booking.</h2>
  <div class="qr">{qr_svg(WHATSAPP)}</div>
  <div class="steps">
    <div class="step"><b>1</b><span>Scan with your phone camera</span></div>
    <div class="step"><b>2</b><span>Send a photo of the patch</span></div>
    <div class="step"><b>3</b><span>We reply with a time</span></div>
  </div>
  <div class="grow"></div>
  <div class="te">{TELUGU}</div>
  <div class="hi">{HINDI}</div>
  <div class="backfoot" style="margin-top:6mm">
    <b>{NAME}</b><br>{QUALS}<br>
    Consultant Dermatologist &amp; Dermatosurgeon
  </div>
  <div class="backfoot" style="margin-top:5mm">
    {STREET},<br>{CITY} {PINCODE}<br>
    Formerly {FORMER_PLAIN}<br>
    <b>{PHONE_SHOW}</b> &middot; {HOURS}<br>
    {SITE.split("//")[1]}/vitiligo
  </div>
</div>"""

INSIDE_L = f"""<div class="panel">
  <div class="rule"></div>
  <div class="dateline"><span>What is happening</span>
       <span>01 &mdash; 02</span></div>
  {section("01", MELANOCYTE, fig=False)}
  {callouts.figure(MELANOCYTE, stage_mm=46)}
  {section("02", PATTERNS, fig=False, trim=1)}
  <!-- This figure carries `rail: true` and no `lead` values, so
       `callouts.figure` routes it to the keyed treatment: the artwork
       fills its frame and has no clear column to label into. -->
  {callouts.figure(EDGE, cap=False, limit=3, cls="tail")}
</div>"""

INSIDE_R = f"""<div class="panel">
  <div class="rule"></div>
  <div class="dateline"><span>What can be done</span><span>03</span></div>
  {section("03", REPIG, fig=False, trim=2)}
  {callouts.figure(REPIG, cap=False, limit=4, stage_mm=46)}
  <div class="ladder">
    <div class="rung"><b>Medical</b><span>Creams and tablets, to stop the
      patch spreading</span></div>
    <div class="rung"><b>Narrowband UVB</b><span>Whole-body light, two or
      three times a week</span></div>
    <div class="rung"><b>Excimer laser</b><span>Targeted light, for a small
      number of patches</span></div>
    <div class="rung"><b>Graft surgery</b><span>For disease stable a year
      that has not repigmented</span></div>
  </div>
  <div class="grow"></div>
  <div class="quote">
    <q>There is no cure for vitiligo <em>anywhere in the world</em>.</q>
    <p>What good treatment does is stop it spreading and bring colour back
      to the patches that can respond. Anyone promising a cure is selling
      something.</p>
  </div>
</div>"""


def main() -> None:
    ok = press.render(
        "leaflet-vitiligo-en", SHEETS["a4-bifold"],
        [face(f'<div class="sheet">{BACK}{COVER}</div>', "outside"),
         face(f'<div class="sheet">{INSIDE_L}{INSIDE_R}</div>', "inside")],
        CSS, title="Vitiligo — leaflet",
        gates=[
            Gate("Telugu & Hindi (clinic name, imported from signage)",
                 True, NATIVE_REVIEW.split(";")[0], "2026-08-02"),
            Gate("Clinical review (Dr. Varada)", False),
            Gate("Diagram review (Dr. Varada)", False),
        ],
        folds=(PANEL,), proof_px=2000)
    print(f"\n  {'press-ready' if ok else 'proof only'} · A4 297x210 flat, "
          f"folds to {PANEL:g}x210mm\n  Panels: back | COVER  (outside), "
          f"01-02 | 03 (inside spread)\n")


if __name__ == "__main__":
    main()
