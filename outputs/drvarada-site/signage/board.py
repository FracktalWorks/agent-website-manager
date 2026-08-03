"""Fascia signboard artwork for the Karkhana clinic — Telugu, English, Hindi.

WHY THIS IS GENERATED AND NOT DRAWN
    The board is now the legal source of truth for the Google Business Profile
    name: a rename is judged against real-world signage, so the moment the board
    and the listing disagree, the rename is refused. It has to agree with the
    website too, for the same reason a locally-differing address string sinks a
    local ranking. So every word on it is imported from `site/chrome.py` rather
    than retyped here. Retyping is exactly how "Center" becomes "Centre" and
    nobody notices until it is cut in acrylic.

WHY A BROWSER RENDERS IT
    Telugu and Devanagari need real text shaping — conjuncts, matras, reordering.
    PIL on this machine reports `raqm: False`, so it would set the glyphs in
    codepoint order and produce confident-looking nonsense. Chrome shapes through
    HarfBuzz, and then — verified by reading the PDF back, not assumed — writes
    the result as Type 3 fonts whose glyph procedures are vector outlines. So the
    shaping is resolved at render time and baked; there is no font program in the
    file and nothing for the fabricator's machine to substitute. A signboard
    shop with no Indic font installed still gets correct Telugu, which is the
    single most common way one of these comes out wrong.

THE INDIC LINES ARE UNVERIFIED
    Transliterations, written from the English. They are rendered correctly; that
    is not the same as reading correctly. A sign is fabricated once and a wrong
    conjunct is permanent, so `NEEDS_NATIVE_REVIEW` stays True until a Telugu and
    a Hindi speaker have both signed off, and `render.py` stamps every proof
    until it is cleared.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str((HERE / ".." / "site").resolve()))

from chrome import (  # noqa: E402  — path set above
    BRAND_PLAIN, FORMER_PLAIN, PHONE_ALT_SHOW, PHONE_LANDLINE_SHOW, PHONE_SHOW,
    REGISTRATION, REVIEWER, SITE,
)

# THE FORMER NAME IS `FORMER_PLAIN`, NOT THE OTHER ONE
#   "BNR Skin & Vitiligo Hospital" is what the practice traded under, what the
#   claimed Google listing carries along with its reviews, and what all 61 pages
#   say. There is a SECOND, unclaimed Google listing reading "BNR Skin and
#   Vitiligo Centre" (D/13A, marked Temporarily closed) — a near-identical
#   string for a different, dead entity. Putting that one on the board would
#   point the rename at the wrong listing, so the name is imported rather than
#   typed and the two cannot be confused here.
FORMERLY = f"Formerly {FORMER_PLAIN}"

# The council registration is held back at the clinic's instruction (2026-08-02).
# The NMC code expects it on a practitioner's board, so this is a deferral and
# not a decision — flip it back on when the number arrives in chrome.py.
SHOW_REGISTRATION = False

WEBSITE = SITE.split("//", 1)[-1]                   # drvarada.com, no protocol

# ── the three names ──────────────────────────────────────────────────────────
# Transliterated, not translated: the descriptor is sounded out rather than
# turned into చర్మ/त्वचा. A Telugu speaker asking for this clinic says "skin",
# because that is the word they use and the word they search. Translating it
# would give the board a third name that matches neither the listing nor how
# anyone refers to the place.
#
# The English line is NOT set in type here — it is the outlined wordmark from
# brand/lockups, so the board carries the identical letterforms as the site
# header rather than a re-set approximation of them.
# THE CONJUNCTION IS TRANSLITERATED TOO
#   An ampersand is a Latin typographic convention, so it sat oddly in both
#   script lines. The fix is `एंड` / `అండ్` — "and", sounded out — and NOT the
#   translated conjunction `और` / `మరియు`. A translated conjunction inside a
#   transliterated name makes the line a hybrid, and it reads as prose rather
#   than as a name: Hindi writes Johnson & Johnson as जॉनसन एंड जॉनसन, essentially
#   never जॉनसन और जॉनसन. The English line keeps its ampersand because the
#   wordmark is outlined artwork and says "&" by design.
TELUGU = "డా. వరద స్కిన్ అండ్ హెయిర్ సెంటర్"
HINDI = "डॉ. वरदा स्किन एंड हेयर सेंटर"

# Cleared 2026-08-02: both lines read by a native speaker via the clinic and
# confirmed correct, including the two judgement calls that were flagged for
# them — the `డా.` / `डॉ.` abbreviation, and the transliterated conjunction
# `అండ్` / `एंड` in preference to the translated `మరియు` / `और`.
#
# Recorded as a string rather than just a flipped boolean, for the same reason
# the case studies carry a consent attestation instead of a `True`: six months
# from now the question will be "who checked this, and when", and a boolean
# cannot answer it. Re-set NEEDS_NATIVE_REVIEW if either line is ever edited —
# this sign-off covers these exact words, not the language in general.
NATIVE_REVIEW = ("Telugu and Hindi read and confirmed by a native speaker; "
                 "relayed by the clinic 2026-08-02")
NEEDS_NATIVE_REVIEW = False

# ── geometry, in millimetres ─────────────────────────────────────────────────
# Every dimension below is real-world size. The PDF page is set to BOARD_W ×
# BOARD_H mm, so the fabricator can measure the artwork with a ruler and get the
# fabricated dimension. Change these two numbers to the surveyed board and
# re-render; nothing else needs touching.
# Height grew from 1000 when the former name and the contact line were added:
# two more rows have to come out of the same budget, and at 1000 they came out
# of the wordmark, which shrank to 1284 mm and left a third of the face empty.
# `natural_height()` reports the height at which the English name exactly fills
# its column — that is where this number came from, and where it should be
# re-derived if the content changes again.
BOARD_W, BOARD_H = 2600, 1175          # replace with the surveyed board
PAD = 70

MARK_H = 560                            # the symbol, left of the text column
MARK_RATIO = 473 / 662                  # from logo-mark viewBox
GAP = 90                                # symbol to text column

# These were set by rendering and measuring, not by picking round numbers. The
# first pass overflowed the face by 112 mm — the Telugu clipped against the top
# edge and the navy board lost its credential line entirely — because the stack
# is seven elements deep and each one's line-height compounds. If any size below
# changes, re-render and look at the proof before believing it fits.
TELUGU_SIZE = 100
HINDI_SIZE = 86
# The former name is set larger than the credentials on purpose. For a patient
# walking past who has known this place for years, it is the line that tells
# them the clinic did not move or close — arguably the most load-bearing text on
# the board, and it should not read as small print.
FORMER_SIZE = 58
CRED_SIZE = 34                          # sized to hold the credential on ONE line
CONTACT_SIZE = 38                       # phones and website; a passer-by acts on it
WORD_RATIO = 907.5 / 216.0              # from logo-wordmark viewBox

# ── the wordmark is DERIVED, not typed ───────────────────────────────────────
# The English name is the one element with slack in it, so it absorbs whatever
# height the other five leave behind. Typing its width instead would mean every
# future change of board size is a hand-tuning session that ends, as the first
# render did, with artwork hanging off the edge.
#
# Height is what binds here, not width. Setting the Indic lines by the wordmark
# instead would be the wrong way round: Telugu has to hold its own against the
# English at a size a passer-by reads, and Telangana expects it prominent — so
# the Indic sizes are fixed and the Latin gives way.
_MARK_W = MARK_H * MARK_RATIO
_COL_W = BOARD_W - 2 * PAD - _MARK_W - GAP          # the text column
_WORD_MARGIN = TELUGU_SIZE * .30
_FORMER_MARGIN = 20
_CONTACT_GAP = 10
_FIXED = (TELUGU_SIZE * 1.22                        # Telugu line box
          + 2 * _WORD_MARGIN                        # air around the wordmark
          + HINDI_SIZE * 1.30                       # Hindi line box
          + _FORMER_MARGIN + FORMER_SIZE * 1.35     # "Formerly BNR …"
          + CRED_SIZE * .85 + 2.5 + CRED_SIZE * .62  # rule and its margins
          + CRED_SIZE * 1.35                        # credential line box
          + _CONTACT_GAP + CONTACT_SIZE * 1.35)     # phones and website
# Held back from the height budget. Without it the wordmark is sized to consume
# every remaining millimetre and the face fits by construction with zero
# tolerance — so any drift between this arithmetic and what Chrome actually lays
# out becomes a crop, and a crop at this scale reads as a design decision rather
# than a fault.
RESERVE = 10
WORDMARK_W = min((BOARD_H - 2 * PAD - _FIXED - RESERVE) * WORD_RATIO, _COL_W)


def fit() -> dict:
    """What the derived geometry actually came out as — printed on every build.

    A board that overflows is not a visible failure in a PDF; it is a crop, and
    a crop at this size looks deliberate. So the numbers get stated rather than
    trusted, and `slack` going negative is the thing to watch for.
    """
    stack = _FIXED + WORDMARK_W / WORD_RATIO
    return {"column_mm": round(_COL_W), "wordmark_mm": round(WORDMARK_W),
            "stack_mm": round(stack), "inner_mm": round(BOARD_H - 2 * PAD),
            "slack_mm": round(BOARD_H - 2 * PAD - stack),
            "fills_column": WORDMARK_W >= _COL_W - 1,
            "natural_h_mm": natural_height()}


def natural_height() -> int:
    """The board height at which the English name exactly fills its column.

    Below this the wordmark is height-starved and shrinks away from the edge,
    leaving the face looking under-set; above it the stack floats in dead space.
    It is the number to quote when someone asks what proportion this content
    wants, and the one to re-check after adding a line to the board.
    """
    return round(_FIXED + _COL_W / WORD_RATIO + RESERVE + 2 * PAD)

# ── colourways ───────────────────────────────────────────────────────────────
# `-flat-navy` is the brand's designated signage colourway (one-colour navy, for
# vinyl, acrylic and screen print). `-mono-light` is the knockout for a dark
# face. Both are one-colour by design: a fabricator quoting a two-colour cut is
# quoting a different, dearer job.
WAYS = [
    {"id": "porcelain", "bg": "#F8F5F3", "fg": "#1E3A63", "rule": "rgba(30,58,99,.22)",
     "sub": "#41506B", "mark": "logo-mark-flat-navy.svg",
     "word": "logo-wordmark-flat-navy.svg",
     "note": "Porcelain face, brand navy artwork — matches the website"},
    {"id": "navy", "bg": "#1E3A63", "fg": "#FFFFFF", "rule": "rgba(255,255,255,.28)",
     "sub": "rgba(255,255,255,.82)", "mark": "logo-mark-mono-light.svg",
     "word": "logo-wordmark-mono-light.svg",
     "note": "Navy face, white knockout — reads harder at dusk and backlit"},
]


def svg(name: str) -> str:
    """Inline a lockup so the PDF carries no external reference.

    The lockups are outlined artwork, so this contributes no font dependency —
    it is the one part of the board that is already immune to the fabricator's
    font library, and inlining keeps it that way through the PDF step.
    """
    src = (HERE / ".." / "brand" / name)
    if not src.exists():
        src = (HERE / ".." / "brand" / "lockups" / name)
    return src.read_text(encoding="utf-8").split("?>")[-1].strip()


def registration_line() -> str:
    """The council registration, or a placeholder that cannot be fabricated.

    `REGISTRATION` is empty in chrome.py — deliberately never invented, because
    it is the one credential a reader can check against a public register. The
    NMC code requires it on a practitioner's board, so an empty value is a
    blocker, not a blank. It renders as magenta here for the same reason
    build.py fails the production build on a placeholder image: a missing thing
    must look missing, from across the room, in a proof nobody read closely.
    """
    if not SHOW_REGISTRATION:
        return ""
    if REGISTRATION:
        return f'<i>·</i><span>Reg. No. {REGISTRATION}</span>'
    return '<i>·</i><span class="todo">REG. NO. — TO BE SUPPLIED</span>'


def face(way: dict) -> str:
    cred = f'<span>{REVIEWER}</span>{registration_line()}'
    # Website first: it is the booking route the clinic wants used, and it is
    # the only line here that still works after the board is out of sight.
    # WhatsApp is labelled because that number is the actual booking path —
    # unlabelled it reads as one more phone number among three.
    contact = ('<span class="www">' + WEBSITE + '</span><i>·</i>'
               f'<span>WhatsApp {PHONE_SHOW}</span><i>·</i>'
               f'<span>{PHONE_ALT_SHOW}</span><i>·</i>'
               f'<span>{PHONE_LANDLINE_SHOW}</span>')
    # The proof tag lives in the top-right corner because that corner is the one
    # part of this layout that is always empty — the stack is left-aligned and
    # its longest line is the wordmark. A banner across the foot would sit on
    # the credential line, hiding the registration placeholder it exists to
    # draw attention to.
    stamp = ('<div class="stamp">PROOF · Telugu and Hindi unverified · '
             'do not fabricate</div>') if NEEDS_NATIVE_REVIEW else ""
    return f'''
  <section class="board {way['id']}">
    {stamp}
    <div class="mark">{svg(way['mark'])}</div>
    <div class="stack">
      <p class="te">{TELUGU}</p>
      <div class="word">{svg(way['word'])}</div>
      <p class="hi">{HINDI}</p>
      <p class="former">{FORMERLY}</p>
      <div class="rule"></div>
      <p class="cred">{cred}</p>
      <p class="contact">{contact}</p>
    </div>
  </section>'''


def html() -> str:
    faces = "".join(face(w) for w in WAYS)
    return f'''<!doctype html>
<meta charset="utf-8">
<title>{BRAND_PLAIN} — fascia signage</title>
<link rel="stylesheet" href="fonts.css">
<style>
  /* The page IS the board. Chrome writes the PDF at this physical size, so
     every millimetre below is a millimetre of fabricated sign. */
  @page {{ size: {BOARD_W}mm {BOARD_H}mm; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; }}
  html, body {{ background: #fff; }}

  @font-face {{ font-family: Gabarito; src: url(fonts/Gabarito.woff2) format('woff2');
                font-weight: 400 700; font-display: block; }}
  @font-face {{ font-family: Manrope; src: url(fonts/Manrope.woff2) format('woff2');
                font-weight: 400 800; font-display: block; }}

  .board {{ width: {BOARD_W}mm; height: {BOARD_H}mm; padding: {PAD}mm;
    display: flex; align-items: center; gap: {GAP}mm;
    page-break-after: always; position: relative; overflow: hidden; }}
  /* Without this the trailing break emits a blank third page, which a
     fabricator reasonably reads as a third board. */
  .board:last-of-type {{ page-break-after: auto; }}
  .porcelain {{ background: {WAYS[0]['bg']}; color: {WAYS[0]['fg']}; }}
  .navy      {{ background: {WAYS[1]['bg']}; color: {WAYS[1]['fg']}; }}

  .mark {{ flex: none; height: {MARK_H}mm; width: {MARK_H * MARK_RATIO:.1f}mm; }}
  .mark svg {{ width: 100%; height: 100%; display: block; }}

  .stack {{ flex: 1; min-width: 0; display: flex; flex-direction: column;
            justify-content: center; }}
  .word {{ width: {WORDMARK_W}mm; margin: {TELUGU_SIZE * .30:.0f}mm 0; }}
  .word svg {{ width: 100%; height: auto; display: block; }}

  /* Indic lines. Optical sizing, not nominal: Noto's Telugu and Devanagari sit
     on different vertical metrics from the Latin wordmark between them, so the
     sizes below were set by looking at the render, not by matching numbers. */
  /* `nowrap` on both: a name line that quietly reflows to two lines would push
     the stack off the bottom edge and crop, which at this scale reads as a
     design decision rather than a fault. Overflow must be visible in the proof.
     It matters more since the conjunction became a word — these lines grew. */
  .te {{ font-family: 'Noto Sans Telugu', sans-serif; font-weight: 600;
         font-size: {TELUGU_SIZE}mm; line-height: 1.22; letter-spacing: -.005em;
         white-space: nowrap; }}
  .hi {{ font-family: 'Noto Sans Devanagari', sans-serif; font-weight: 600;
         font-size: {HINDI_SIZE}mm; line-height: 1.30; white-space: nowrap; }}

  /* The former name. Set in the display face rather than the body face so it
     reads as part of the identity — which it is — instead of as a footnote. */
  .former {{ font-family: Gabarito, sans-serif; font-weight: 500;
             font-size: {FORMER_SIZE}mm; line-height: 1.35;
             margin-top: {_FORMER_MARGIN}mm; white-space: nowrap; }}
  .porcelain .former {{ color: {WAYS[0]['sub']}; }}
  .navy .former {{ color: {WAYS[1]['sub']}; }}

  .rule {{ height: 2.5mm; margin: {CRED_SIZE * .85:.0f}mm 0 {CRED_SIZE * .62:.0f}mm; }}
  .porcelain .rule {{ background: {WAYS[0]['rule']}; }}
  .navy .rule {{ background: {WAYS[1]['rule']}; }}

  /* One line, always. `nowrap` is the assertion: if the credential no longer
     fits the column it must overflow visibly in the proof rather than quietly
     reflow to two lines and push the whole stack off the bottom edge, which is
     exactly what the first render did. */
  .cred {{ font-family: Manrope, sans-serif; font-weight: 600;
           font-size: {CRED_SIZE}mm; line-height: 1.35;
           display: flex; flex-wrap: nowrap; align-items: baseline;
           white-space: nowrap; gap: 0 {CRED_SIZE * .45:.0f}mm; }}
  .porcelain .cred {{ color: {WAYS[0]['sub']}; }}
  .navy .cred {{ color: {WAYS[1]['sub']}; }}
  .cred i, .contact i {{ font-style: normal; opacity: .45; }}

  /* Contact. Full brand colour, not the muted `sub` used for the credentials:
     this is the line a passer-by is meant to act on. */
  .contact {{ font-family: Manrope, sans-serif; font-weight: 700;
              font-size: {CONTACT_SIZE}mm; line-height: 1.35;
              margin-top: {_CONTACT_GAP}mm;
              display: flex; flex-wrap: nowrap; align-items: baseline;
              white-space: nowrap; gap: 0 {CONTACT_SIZE * .45:.0f}mm; }}
  .contact .www {{ font-family: Gabarito, sans-serif; }}

  /* A missing registration number must look missing from across the room. */
  .todo {{ background: #FF00A0; color: #fff; padding: 2mm 6mm; border-radius: 3mm;
           font-weight: 800; }}

  .stamp {{ position: absolute; top: 0; right: 0; z-index: 9;
    background: #FF00A0; color: #fff; font: 700 22mm/1.35 Manrope, sans-serif;
    padding: 10mm 22mm; border-radius: 0 0 0 8mm; letter-spacing: .03em; }}
</style>
{faces}
'''


if __name__ == "__main__":
    (HERE / "fascia.html").write_text(html(), encoding="utf-8")
    print(f"fascia.html — {BOARD_W}x{BOARD_H}mm, {len(WAYS)} colourways")
    f = fit()
    print(f"  text column {f['column_mm']}mm · wordmark {f['wordmark_mm']}mm"
          f"{' (fills column)' if f['fills_column'] else ''}")
    print(f"  stack {f['stack_mm']}mm in {f['inner_mm']}mm · "
          f"slack {f['slack_mm']}mm")
    if f["slack_mm"] < 0:
        raise SystemExit("OVERFLOW: the stack is taller than the board face.")
    # Only when it is worth acting on. A note that fires over a rounding
    # difference is a note people learn to scroll past.
    if abs(f["natural_h_mm"] - BOARD_H) > 20:
        print(f"  note: this content wants {BOARD_W}x{f['natural_h_mm']}mm "
              f"for the English name to fill its column")
    if NEEDS_NATIVE_REVIEW:
        print("PROOF ONLY: Telugu/Hindi await a native reader.")
    else:
        print(f"  language: {NATIVE_REVIEW}")
    if not SHOW_REGISTRATION:
        print("note: council registration omitted at the clinic's instruction "
              "(NMC code expects it — set SHOW_REGISTRATION to restore).")
