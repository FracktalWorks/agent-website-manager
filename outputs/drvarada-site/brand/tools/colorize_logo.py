"""Colourise the client-supplied flat logo SVG into a full brand variant set.

Input : outputs/drvarada-site/brand/source/varadas-logo-source.svg  (single-colour, 37 paths)
Output: light / dark / flat-navy / mono-dark / mono-light / adaptive

Square app/favicon assets are NOT built here -- see icon_system.py, which keeps the
full mark at every size instead of reducing it to the follicle.

Classification is derived from each path's own geometry, not guessed:
  * path 0  -> hair shaft + bulb   (primary colour)
  * path 1  -> follicle sheath     (secondary, mid grey)
  * others  -> centroid x < SPLIT  => molecular dot field (primary)
               centroid x >= SPLIT => cell/hexagon field  (grey ramp)

Cell tone is assigned by distance from the follicle axis: cells nearest the follicle are
darkest and fade outward, so the field reads as radiating from the follicle rather than random.
"""
import re, math, pathlib

ROOT = pathlib.Path(r"c:\Users\VijayRaghavVarada\Documents\Github\agent-website-manager\outputs\drvarada-site\brand")
SRC = ROOT / "source" / "varadas-logo-source.svg"

SPLIT = 520.0        # x that separates dot field from cell field (verified against path bboxes)
AXIS = 520.0         # follicle axis, for the cell-tone gradient
PAD = 14.0

NUM = re.compile(r"-?\d+(?:\.\d+)?")


def paths(svg):
    return re.findall(r'<path[^>]*?\sd="\s*([^"]+)"', svg, re.S)


def compress(d, nd=2):
    """Round path coordinates. viewBox is ~474 units wide, so 0.01u is 0.002% of the
    artwork width - visually lossless, and it roughly halves the file size."""
    def r(m):
        v = round(float(m.group()), nd)
        return f"{v:g}"
    d = NUM.sub(r, d)
    return " ".join(d.split())


def bbox(d):
    n = [float(x) for x in NUM.findall(d)]
    xs, ys = n[0::2], n[1::2]
    return min(xs), min(ys), max(xs), max(ys)


PALETTES = {
    # slot 0 = primary (follicle + dots), slot 1 = sheath, slots 2..6 = cell ramp dark->light
    "light":      ["#1E3A63", "#7C8A99", "#5F6E7F", "#71808F", "#8592A0", "#98A4B1", "#ADB7C1"],
    "dark":       ["#FFFFFF", "#8397AF", "#C6D3E1", "#B3C2D3", "#A2B3C7", "#93A6BC", "#8399B2"],
    "flat-navy":  ["#1E3A63"] * 7,
    "mono-dark":  ["#12202F"] * 7,
    "mono-light": ["#FFFFFF"] * 7,
}
VARS = ["--c1", "--c-sheath", "--c2a", "--c2b", "--c2c", "--c2d", "--c2e"]


def classify(ds):
    """-> list of (path_d, slot_index, layer_name)"""
    out = []
    cells = []
    for i, d in enumerate(ds):
        x0, y0, x1, y1 = bbox(d)
        cx = (x0 + x1) / 2
        if i == 0:
            out.append([d, 0, "follicle"])
        elif i == 1:
            out.append([d, 1, "follicle"])
        elif cx < SPLIT:
            out.append([d, 0, "molecular-field"])
        else:
            out.append([d, None, "cell-field"])
            cells.append((len(out) - 1, cx - AXIS))
    # cell ramp: nearest the follicle = darkest (slot 2) -> farthest = lightest (slot 6)
    if cells:
        dmin = min(c[1] for c in cells)
        dmax = max(c[1] for c in cells)
        span = (dmax - dmin) or 1.0
        for idx, dist in cells:
            t = (dist - dmin) / span
            out[idx][1] = 2 + min(4, int(t * 5))
    return out


def art_bbox(ds):
    bs = [bbox(d) for d in ds]
    return (min(b[0] for b in bs) - PAD, min(b[1] for b in bs) - PAD,
            max(b[2] for b in bs) + PAD, max(b[3] for b in bs) + PAD)


def render(items, vb, paint, style="", svg_id="", title=""):
    x0, y0, x1, y1 = vb
    idattr = f' id="{svg_id}"' if svg_id else ""
    s = (f'<svg xmlns="http://www.w3.org/2000/svg"{idattr} '
         f'viewBox="{x0:.0f} {y0:.0f} {x1 - x0:.0f} {y1 - y0:.0f}" '
         f'role="img" aria-label="{title}">\n')
    if style:
        s += f"  <style>\n{style}  </style>\n"
    for layer in ("molecular-field", "follicle", "cell-field"):
        members = [(d, slot) for d, slot, lay in items if lay == layer]
        if not members:
            continue
        s += f'  <g id="{layer}">\n'
        for d, slot in members:
            s += f'    <path fill="{paint(slot)}" d="{d.strip()}"/>\n'
        s += "  </g>\n"
    return s + "</svg>\n"


def main():
    svg = SRC.read_text(encoding="utf-8")
    ds = paths(svg)
    ds = [compress(d) for d in ds]
    items = classify(ds)
    vb = art_bbox(ds)
    print(f"paths: {len(ds)}   viewBox: {[round(v) for v in vb]}")
    counts = {}
    for _, _, lay in items:
        counts[lay] = counts.get(lay, 0) + 1
    print("layers:", counts)

    made = []
    for name, pal in PALETTES.items():
        title = f"Dr. Varada&apos;s Skin &amp; Hair Center logo ({name})"
        out = ROOT / f"logo-mark-{name}.svg"
        out.write_text(render(items, vb, lambda i: pal[i], title=title), encoding="utf-8")
        made.append(out)

    # adaptive — CSS vars scoped to the svg's own id so they cannot leak into a host page
    sid = "dv-logo"
    decl = lambda pal: " ".join(f"{v}:{c};" for v, c in zip(VARS, pal))
    style = (f"    #{sid} {{ {decl(PALETTES['light'])} }}\n"
             f"    @media (prefers-color-scheme: dark) {{ #{sid} {{ {decl(PALETTES['dark'])} }} }}\n"
             f"    #{sid}[data-theme='dark'] {{ {decl(PALETTES['dark'])} }}\n"
             f"    #{sid}[data-theme='light'] {{ {decl(PALETTES['light'])} }}\n")
    out = ROOT / "logo-mark-adaptive.svg"
    out.write_text(render(items, vb, lambda i: f"var({VARS[i]})", style=style, svg_id=sid,
                          title="Dr. Varada&apos;s Skin &amp; Hair Center adaptive logo"), encoding="utf-8")
    made.append(out)


    for p in made:
        print(f"  {p.name:28} {p.stat().st_size:>6} bytes")


main()
