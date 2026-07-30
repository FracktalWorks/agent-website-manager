"""Turn a line of text into a single outlined SVG path.

Logos must not carry live text: a machine without the font installed renders something
else entirely. So each line is shaped with HarfBuzz -- real kerning, real ligatures --
and every glyph is converted to outlines, exactly what a designer means by
"convert to outlines" before sending artwork to a printer.

The two brand faces are variable fonts, so they are first instanced at the weight the
lockup asks for; after instancing the outlines are static and safe to extract.
"""
import base64
import io
import pathlib
import re
from functools import lru_cache

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = pathlib.Path(__file__).resolve().parent
FONTDIR = HERE.parent / "source" / "fonts"


def extract_fonts(css_path):
    """Pull the base64 woff2 payloads out of an inlined @font-face stylesheet."""
    css = pathlib.Path(css_path).read_text(encoding="utf-8")
    FONTDIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for fam, b64 in re.findall(
            r"font-family:'([^']+)'.*?url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)",
            css, re.S):
        p = FONTDIR / f"{fam}.woff2"
        p.write_bytes(base64.b64decode(b64))
        out[fam] = p
    return out


@lru_cache(maxsize=None)
def _face(family, weight):
    """A static instance of a variable brand face, as (TTFont, harfbuzz font, upem)."""
    src = FONTDIR / f"{family}.woff2"
    tt = TTFont(io.BytesIO(src.read_bytes()))
    if "fvar" in tt:
        instantiateVariableFont(tt, {"wght": weight}, inplace=True, updateFontNames=False)
    buf = io.BytesIO()
    tt.flavor = None
    tt.save(buf)
    data = buf.getvalue()
    hbf = hb.Font(hb.Face(data))
    return tt, hbf, tt["head"].unitsPerEm


def cap_height(family, weight=400):
    tt, _, upem = _face(family, weight)
    if "OS/2" in tt and getattr(tt["OS/2"], "sCapHeight", 0):
        return tt["OS/2"].sCapHeight / upem
    glyphs = tt.getGlyphSet()
    return glyphs["H"]._glyph.yMax / upem if "H" in glyphs else 0.7


def outline(text, family, weight, size, tracking=0.0, y=0.0, x=0.0):
    """Shaped, outlined text as (svg path data, total advance width).

    `size` is the em size in output units; `tracking` is extra letter spacing in ems,
    applied after every glyph the way a design tool applies it. Coordinates come back
    already flipped into SVG's y-down space and offset to (x, y) on the baseline.
    """
    tt, hbf, upem = _face(family, weight)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": True, "calt": True})

    order = tt.getGlyphOrder()
    glyphs = tt.getGlyphSet()
    scale = size / upem
    track = tracking * size

    parts, pen_x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        gx = x + pen_x + pos.x_offset * scale
        gy = y - pos.y_offset * scale
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{round(v, 2):g}")
        # y is negated: font units run upward, SVG units run downward
        glyphs[name].draw(TransformPen(pen, Transform(scale, 0, 0, -scale, gx, gy)))
        d = pen.getCommands()
        if d:
            parts.append(d)
        pen_x += pos.x_advance * scale + track
    if buf.glyph_infos:
        pen_x -= track          # no trailing letter space on the last glyph
    return " ".join(parts), pen_x


def measure(text, family, weight, size, tracking=0.0):
    return outline(text, family, weight, size, tracking)[1]


if __name__ == "__main__":
    import sys
    found = extract_fonts(sys.argv[1])
    for fam, p in found.items():
        print(f"  {fam:10} {p.stat().st_size:>7} B  cap-height {cap_height(fam):.3f} em")
