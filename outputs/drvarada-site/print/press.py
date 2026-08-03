"""press.py — the print engine. Physical millimetres in, press-ready PDF out.

Every piece of print collateral in this directory is built the same way: HTML
and CSS laid out in real millimetres, rendered by Chrome to a PDF whose page IS
the artwork, then read back and checked before anyone is allowed to send it to
a printer.

WHY A BROWSER, AND WHY THE PDF IS READ BACK
    Inherited from `../signage/`, where it was proven at fabrication scale.
    Telugu and Devanagari need real text shaping — conjuncts, matras,
    reordering — and Chrome shapes through HarfBuzz, then writes the result as
    Type 3 fonts whose glyph procedures are vector outlines. There is no font
    program in the file, so a press with no Indic font installed still gets
    correct Telugu. That property is invisible on this machine and catastrophic
    at the other end, so `audit()` verifies it by reading the bytes back rather
    than trusting that it happened.

    The other two things `audit()` catches have both actually happened: a stray
    `page-break-after` adding a blank page (which a printer reasonably reads as
    a blank side to print), and a MediaBox that is not the size anybody asked
    for (which gets silently scaled to fit at the press).

BLEED, TRIM AND SAFE — the three rectangles
    The PDF page is TRIM + bleed on all four sides. Anything meant to reach the
    finished edge must run to the page edge, because the guillotine wanders by
    a millimetre or two and white slivers are the result of artwork that stops
    exactly at the trim line. Nothing that must be read may sit outside SAFE,
    for the same wander in the other direction.

    `.trim` and `.safe` are real elements, so a layout positions against them
    rather than against arithmetic. The proof PNG draws both as guides; the
    print PDF does not.

REVIEW GATES ARE PART OF THE ARTEFACT
    Print is one-way. A file that has not been cleared carries a visible stamp
    on the proof and refuses to write a print PDF at all — see `Gate`. A clinic
    flier states medical facts in three languages; "we thought it was checked"
    is not a recoverable position once a thousand of them are boxed.
"""

from __future__ import annotations

import dataclasses
import io
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
SITE = (HERE / ".." / "site").resolve()
SIGNAGE = (HERE / ".." / "signage").resolve()
OUT = HERE / "out"

PX_PER_MM = 96 / 25.4        # the CSS millimetre, the unit Chrome lays out in
PT_PER_MM = 72 / 25.4        # PDF points, the unit a MediaBox is written in
PROOF_GAP_MM = 6             # daylight between proof faces, not in print


# --------------------------------------------------------------- sheet sizes

@dataclasses.dataclass(frozen=True)
class Sheet:
    """A trimmed size plus the two margins every press job needs.

    `bleed` is how far artwork runs past the trim; `safe` is how far inside the
    trim the last readable thing may sit. Both are in millimetres and both are
    conventions, not laws — a large-format standee is guillotined far less
    precisely than a business card, which is why its numbers are bigger.
    """
    id: str
    w: float                 # trimmed width, mm
    h: float                 # trimmed height, mm
    bleed: float
    safe: float
    note: str = ""

    @property
    def page_w(self) -> float:
        return self.w + 2 * self.bleed

    @property
    def page_h(self) -> float:
        return self.h + 2 * self.bleed


SHEETS = {
    # 90x54 is the Indian/most-of-the-world business card. (The US is 89x51;
    # a card cut to that here comes back subtly short in every card holder.)
    "card": Sheet("card", 90, 54, 3, 4, "business card"),
    "a5": Sheet("a5", 148, 210, 3, 10, "A5 flier / handout"),
    # A4 folded once down the middle: four 148.5x210 panels on one sheet.
    # The press prints it flat, so the artwork is 297 wide and the FOLD, not
    # the trim, is what the layout is composed against.
    "a4-bifold": Sheet("a4-bifold", 297, 210, 3, 10, "A4 single-fold leaflet"),
    "a4": Sheet("a4", 210, 297, 3, 12, "A4 sheet"),
    # The Indian roll-up standard. The bottom ~120mm disappears into the
    # cassette and the top ~60mm curls at the rail, so `safe` is generous and
    # layouts must additionally keep the lower band clear — see FOOT_MM.
    "standee": Sheet("standee", 850, 2000, 10, 40, "roll-up standee"),
}
FOOT_MM = 140                # of a standee, eaten by the base. Keep it empty.


# ------------------------------------------------------------------- gating

@dataclasses.dataclass(frozen=True)
class Gate:
    """One named sign-off, with who gave it and when — never a bare boolean.

    `True` cannot answer the only question that matters six months later, which
    is *who checked this and when*. Same reason the case studies carry a
    consent string rather than a flag.
    """
    name: str
    cleared: bool
    by: str = ""
    on: str = ""

    def line(self) -> str:
        return (f"{self.name}: cleared by {self.by}, {self.on}" if self.cleared
                else f"{self.name}: NOT CLEARED")


def gate_report(gates: list[Gate]) -> tuple[bool, list[str]]:
    return all(g.cleared for g in gates), [g.line() for g in gates]


# -------------------------------------------------------------------- fonts

def fonts_css() -> str:
    """Latin + Telugu + Devanagari, all from disk, all absolute.

    The Indic faces are the ones `../signage/getfonts.py` already fetched (both
    SIL OFL, so they may be used in commercial print — the Windows system font
    Nirmala UI may not). They are referenced where they are rather than copied
    here: two copies of a font file is two answers to "which one shipped".
    """
    sheet = (SIGNAGE / "fonts.css").read_text(encoding="utf-8")
    sheet = sheet.replace("url(fonts/", f"url({(SIGNAGE / 'fonts').as_uri()}/")
    latin = (SIGNAGE / "fonts").as_uri()
    return f"""
@font-face {{ font-family: Gabarito; src: url({latin}/Gabarito.woff2)
             format('woff2'); font-weight: 400 700; font-display: block; }}
@font-face {{ font-family: Manrope; src: url({latin}/Manrope.woff2)
             format('woff2'); font-weight: 400 800; font-display: block; }}
{sheet}"""


def qr_svg(data: str, dark: str = "#12202F", border: int = 0) -> str:
    """An inline SVG QR. Vector, so it stays crisp at any physical size.

    Error correction M, not L: a card lives in a wallet and a standee gets
    scuffed, and M tolerates ~15% damage for about 10% more modules. Not Q or
    H — those make the modules smaller, which is the thing that actually stops
    a phone reading it across a waiting room.
    """
    import segno
    q = segno.make(data, error="m")
    buf = io.BytesIO()
    q.save(buf, kind="svg", xmldecl=False, svgns=True, border=border,
           dark=dark, svgclass=None, lineclass=None, unit="")
    svg = buf.getvalue().decode()
    # segno writes width/height in module units and no viewBox, which pins the
    # QR to 25px on the page. Swapping in a viewBox hands the physical size to
    # the CSS, where it is expressed in millimetres like everything else here.
    n = q.symbol_size(border=border)[0]
    return re.sub(r'width="\d+" height="\d+"',
                  f'viewBox="0 0 {n} {n}" width="100%" height="100%"', svg, 1)


# ------------------------------------------------------------------ documents

def document(sheet: Sheet, faces: list[str], css: str, *,
             title: str = "", proof: bool = False,
             stamp: str = "", folds: tuple[float, ...] = ()) -> str:
    """One HTML file holding every face of one artefact, one face per page.

    The SAME document builds the print PDF and the proof; only `proof` differs.
    Two documents would drift, and the drift would be invisible until the thing
    that was approved is not the thing that was printed.
    """
    s = sheet
    guides = f"""
  /* The proof body is pinned to exactly one face wide. Left to itself the
     body is as wide as its widest content, and `margin: auto` then centres
     the face inside THAT — which puts the artwork half off the screenshot
     and looks like a layout bug in the card rather than in the proof. */
  html, body {{ width: {s.page_w}mm; overflow-x: hidden; }}
  body {{ background: #E9E9EC; }}
  .face {{ margin: 0 0 {PROOF_GAP_MM}mm 0; }}
  .face:last-child {{ margin-bottom: 0; }}
  .guide {{ position: absolute; inset: 0; pointer-events: none; z-index: 90; }}
  .guide i {{ position: absolute; display: block; }}
  .guide .t {{ inset: {s.bleed}mm; outline: .25mm dashed rgba(214,40,40,.6); }}
  .guide .s {{ inset: {s.bleed + s.safe}mm;
               outline: .25mm dashed rgba(30,58,99,.35); }}
  .guide .f {{ top: 0; bottom: 0; width: 0;
               border-left: .4mm dashed rgba(47,109,246,.75); }}
  .trim {{ outline: .3mm dashed rgba(214,40,40,.55); }}
  .safe {{ outline: .3mm dashed rgba(30,58,99,.4); }}
  .face::after {{ content: attr(data-label); position: absolute;
      left: 0; top: 0; font: 600 3mm Manrope, sans-serif; color: #D62828;
      background: #fff; padding: .8mm 1.6mm; }}
""" if proof else ""
    # A real newline inside a CSS string literal is a parse error, and the
    # browser drops the WHOLE rule — so an unapproved proof rendered with no
    # stamp at all and looked finished. `\\A` is the escape CSS accepts, and
    # `white-space: pre-line` below is what turns it back into a line break.
    stamped = f"""
  .face::before {{ content: "{stamp.replace(chr(10), chr(92) + 'A ')}";
      position: absolute; z-index: 99;
      left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-24deg);
      font: 800 {max(6, s.w / 12):.1f}mm Manrope, sans-serif;
      letter-spacing: .04em;
      color: rgba(214,40,40,.30); text-align: center; white-space: pre-line;
      pointer-events: none; }}
""" if stamp else ""
    return f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>{title}</title>
<style>
{fonts_css()}
  @page {{ size: {s.page_w}mm {s.page_h}mm; margin: 0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ background: #fff; }}
  .face {{ position: relative; overflow: hidden; background: #fff;
           width: {s.page_w}mm; height: {s.page_h}mm;
           page-break-after: always; break-after: page; }}
  /* The last face must NOT break, or the PDF gains a blank final page that a
     printer reads as a blank side to print. audit() re-checks this. */
  .face:last-child {{ page-break-after: auto; break-after: auto; }}
  .trim {{ position: absolute; inset: {s.bleed}mm; }}
  .safe {{ position: absolute; inset: {s.bleed + s.safe}mm; }}
  .bleedbox {{ position: absolute; inset: 0; }}
{css}
{guides}
{stamped}
</style>
<body>
{"".join(f.replace("<!--guide-->",
                   guide_html(sheet, folds) if proof else "") for f in faces)}
</body></html>"""


def guide_html(sheet: "Sheet", folds: tuple[float, ...] = ()) -> str:
    """Trim, safe and any fold lines — proof only.

    A fold is drawn because a folded piece is composed against the CREASE, not
    against the trim, and a panel that reads well flat can put a headline
    straight down the fold. The line is the only way to see that before it is
    500 copies of a leaflet that creases through a word.
    """
    marks = "".join(
        f'<i class="f" style="left:{sheet.bleed + f}mm"></i>' for f in folds)
    return ('<div class="guide"><i class="t"></i><i class="s"></i>'
            f'{marks}</div>')


def face(inner: str, label: str = "", cls: str = "") -> str:
    """One printed side. The guide marker is replaced only in proof mode."""
    return (f'<section class="face {cls}" data-label="{label}">'
            f'{inner}<!--guide--></section>')


# ------------------------------------------------------------------ rendering

def chrome() -> str:
    """Same discovery order as verify.py and signage/render.py."""
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "google-chrome", "chromium"):
        if pathlib.Path(c).exists() or shutil.which(c):
            return c
    raise SystemExit("Chrome not found - install it or set the path here.")


def run(exe: str, *args: str) -> None:
    proc = subprocess.run([exe, "--headless=new", "--disable-gpu",
                           "--no-sandbox", "--hide-scrollbars", *args],
                          capture_output=True, text=True, timeout=300)
    # Chrome exits 0 while writing nothing when a flag is wrong, so callers
    # check the artefact, never the return code. Surface stderr regardless.
    if proc.returncode != 0:
        print(proc.stderr[-600:], file=sys.stderr)


def audit(pdf: pathlib.Path, pages: int, sheet: Sheet) -> list[str]:
    """Read the written PDF back. Three properties, three silent failures."""
    raw = pdf.read_bytes()
    bad: list[str] = []
    got = len(re.findall(rb"/Type\s*/Page[^s]", raw))
    if got != pages:
        bad.append(f"{got} pages, expected {pages}")
    want = (round(sheet.page_w), round(sheet.page_h))
    for box in {b.decode() for b in
                set(re.findall(rb"/MediaBox\s*\[([^\]]*)\]", raw))}:
        x0, y0, x1, y1 = (float(v) for v in box.split())
        mm = (round((x1 - x0) / PT_PER_MM), round((y1 - y0) / PT_PER_MM))
        if mm != want:
            bad.append(f"page is {mm[0]}x{mm[1]}mm, "
                       f"expected {want[0]}x{want[1]}mm incl. bleed")
    if not raw.count(b"/CharProcs"):
        bad.append("text is not outlined - no /CharProcs in the PDF")
    if raw.count(b"/FontFile"):
        bad.append("a font program is embedded - text may not be outlined")
    return bad


def render(stem: str, sheet: Sheet, faces: list[str], css: str, *,
           title: str = "", gates: list[Gate] | None = None,
           proof_px: int = 1800, folds: tuple[float, ...] = ()) -> bool:
    """Write <stem>.pdf and <stem>-proof.png, then audit. True if press-ready.

    When a gate is open the proof is still written — stamped, so it can be
    circulated for the very review it is waiting on — and the print PDF is not
    written at all. A file that exists is one someone can email to a press.
    """
    OUT.mkdir(exist_ok=True)
    gates = gates or []
    cleared, lines = gate_report(gates)
    exe = chrome()
    pages = len(faces)

    stamp = "" if cleared else "NOT FOR PRINT\nawaiting sign-off"
    proof_html = OUT / f"_{stem}-proof.html"
    proof_html.write_text(
        document(sheet, faces, css, title=title, proof=True, stamp=stamp,
                 folds=folds),
        encoding="utf-8")

    w = round(sheet.page_w * PX_PER_MM)
    h = round((sheet.page_h * pages + PROOF_GAP_MM * (pages - 1)) * PX_PER_MM)
    # Scales UP as well as down. A business card is 363 CSS px across, and a
    # proof at 1:1 is too small to judge anything on — which is the whole job
    # of a proof. Capped at 4 so a standee does not try to raster a mural.
    scale = max(0.04, min(4.0, proof_px / w))
    png = OUT / f"{stem}-proof.png"
    png.unlink(missing_ok=True)
    run(exe, f"--screenshot={png}", f"--window-size={w},{h}",
        f"--force-device-scale-factor={scale:.4f}",
        proof_html.resolve().as_uri())

    print(f"\n  {stem}  ·  {sheet.w:g}x{sheet.h:g}mm trimmed, "
          f"{sheet.bleed:g}mm bleed  ·  {pages} face(s)")
    for line in lines:
        print(f"    {'ok  ' if 'NOT CLEARED' not in line else 'WAIT'}  {line}")
    kb = png.stat().st_size // 1024 if png.exists() else 0
    print(f"    {'ok  ' if png.exists() else 'FAIL'}  "
          f"proof {png.name} ({kb} KB)")

    pdf = OUT / f"{stem}.pdf"
    pdf.unlink(missing_ok=True)
    if not cleared:
        print("    HELD  print PDF not written while a sign-off is open")
        return False

    print_html = OUT / f"_{stem}.html"
    print_html.write_text(document(sheet, faces, css, title=title),
                          encoding="utf-8")
    run(exe, f"--print-to-pdf={pdf}", "--no-pdf-header-footer",
        print_html.resolve().as_uri())
    if not pdf.exists():
        print("    FAIL  Chrome wrote no PDF")
        return False
    faults = audit(pdf, pages, sheet)
    for f in faults:
        print(f"    FAIL  {f}")
    if faults:
        return False
    print(f"    ok    {pdf.name} ({pdf.stat().st_size // 1024} KB) - "
          f"{pages} page(s), {sheet.page_w:g}x{sheet.page_h:g}mm, "
          "text outlined")
    return True
