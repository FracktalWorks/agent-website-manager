"""Fetch the Indic webfonts the board needs.

Noto Sans Telugu and Noto Sans Devanagari, both SIL Open Font License — free to
use in commercial work including fabricated signage, which the Windows system
font (Nirmala UI) is not. Downloaded as woff2 and served from disk so the render
never depends on the network, and so the PDF embeds a subset of exactly these
files rather than whatever the fabricator happens to have installed.
"""
import re, urllib.request, pathlib

# A modern UA is required: Google Fonts serves ttf to anything it doesn't
# recognise, and ttf in a print PDF is a much larger embed for no gain.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
FAMS = ["Noto+Sans+Telugu:wght@400;600;700", "Noto+Sans+Devanagari:wght@400;600;700"]
here = pathlib.Path(__file__).parent
out, css = here / "fonts", []

for fam in FAMS:
    url = f"https://fonts.googleapis.com/css2?family={fam}&display=block"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    sheet = urllib.request.urlopen(req).read().decode()
    for href in dict.fromkeys(re.findall(r"url\((https://[^)]+\.woff2)\)", sheet)):
        name = href.rsplit("/", 2)[-2] + "-" + href.rsplit("/", 1)[-1]
        (out / name).write_bytes(urllib.request.urlopen(
            urllib.request.Request(href, headers={"User-Agent": UA})).read())
        sheet = sheet.replace(href, f"fonts/{name}")
    css.append(sheet)

(here / "fonts.css").write_text("\n".join(css), encoding="utf-8")
print(f"{len(list(out.glob('*.woff2')))} woff2 files, fonts.css written")
