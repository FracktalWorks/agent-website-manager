"""Render the fascia board to a fabricator-ready PDF and an on-screen proof.

    python board.py && python render.py

PDF is the deliverable. Chrome writes the page at the physical size declared in
`@page` and converts the shaped Indic text to outlines, so the file can be
scaled, measured and cut without a font install at the other end. PNG is only
for approving on a screen; never send it to be fabricated.

`audit()` checks all of that by reading the PDF back. It is not ceremony: the
first render silently emitted a blank third page, which a fabricator would
reasonably read as a third board, and a PDF that has quietly fallen back to
un-outlined text looks identical here and wrong at the sign shop.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
PX_PER_MM = 96 / 25.4          # CSS millimetre, the unit Chrome lays out in


def chrome() -> str:
    """Same discovery order as verify.py, so both tools agree on the browser."""
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "google-chrome", "chromium"):
        if pathlib.Path(c).exists() or shutil.which(c):
            return c
    raise SystemExit("Chrome not found — install it or set the path here.")


def run(exe: str, *args: str) -> None:
    proc = subprocess.run([exe, "--headless=new", "--disable-gpu",
                           "--no-sandbox", "--hide-scrollbars", *args],
                          capture_output=True, text=True, timeout=180)
    # Chrome exits 0 while writing nothing if a flag is wrong, so the caller
    # checks the artefact rather than the return code. Surface stderr anyway.
    if proc.returncode != 0:
        print(proc.stderr[-600:], file=sys.stderr)


def audit(pdf: pathlib.Path, pages: int, w_mm: int, h_mm: int) -> list[str]:
    """Read the written PDF back and check it is what a fabricator needs.

    Three properties, each of which has a silent failure mode:
      · page count — a stray `page-break-after` adds a blank page that reads as
        an extra board;
      · MediaBox — the page must BE the sign, so it can be measured with a ruler;
      · outlined text — Chrome writes Type 3 fonts whose glyph procedures are
        vector paths (`/CharProcs`, no `/FontFile`). If it ever falls back to an
        embedded or referenced font program, the file looks identical on this
        machine and sets tofu at a sign shop with no Telugu font.
    """
    raw = pdf.read_bytes()
    bad, pt = [], 72 / 25.4
    got = len(re.findall(rb"/Type\s*/Page[^s]", raw))
    if got != pages:
        bad.append(f"{got} pages, expected {pages}")
    for box in {b.decode() for b in set(re.findall(rb"/MediaBox\s*\[([^\]]*)\]", raw))}:
        x0, y0, x1, y1 = (float(v) for v in box.split())
        mm = (round((x1 - x0) / pt), round((y1 - y0) / pt))
        if mm != (w_mm, h_mm):
            bad.append(f"page is {mm[0]}x{mm[1]}mm, expected {w_mm}x{h_mm}mm")
    if not raw.count(b"/CharProcs"):
        bad.append("text is not outlined — no /CharProcs in the PDF")
    if raw.count(b"/FontFile"):
        bad.append("a font program is embedded — text may not be outlined")
    return bad


def main() -> None:
    import board                                   # geometry, in millimetres

    src = HERE / "fascia.html"
    if not src.exists():
        raise SystemExit("fascia.html missing — run `python board.py` first.")
    OUT.mkdir(exist_ok=True)
    exe, url = chrome(), src.resolve().as_uri()

    pdf = OUT / "fascia-signage.pdf"
    run(exe, f"--print-to-pdf={pdf}", "--no-pdf-header-footer", url)

    # The proof. Full artwork is 11,338 px wide at CSS scale — far past what is
    # useful to look at, so the device scale factor takes it down rather than a
    # CSS transform, which would resample the type and misrepresent the edges.
    pages = len(board.WAYS)
    w = round(board.BOARD_W * PX_PER_MM)
    h = round(board.BOARD_H * PX_PER_MM * pages)
    scale = 2600 / w
    png = OUT / "fascia-proof.png"
    run(exe, f"--screenshot={png}", f"--window-size={w},{h}",
        f"--force-device-scale-factor={scale:.4f}", url)

    for f in (pdf, png):
        print(f"{f.name:24} {f.stat().st_size // 1024:>6} KB"
              if f.exists() else f"{f.name:24}  NOT WRITTEN")

    faults = audit(pdf, pages, board.BOARD_W, board.BOARD_H)
    print(f"\nBoard {board.BOARD_W}x{board.BOARD_H} mm · {pages} colourways")
    if faults:
        for f in faults:
            print(f"  FAIL  {f}")
        raise SystemExit("PDF is not fit to send to a fabricator.")
    print(f"  ok    {pages} pages, each {board.BOARD_W}x{board.BOARD_H} mm")
    print("  ok    text outlined — no font dependency at the sign shop")
    if board.NEEDS_NATIVE_REVIEW:
        print("PROOF ONLY — Telugu and Hindi unverified. Do not fabricate.")


if __name__ == "__main__":
    main()
