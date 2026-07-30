"""Build a size-tiered icon system from the FULL logo mark.

The mark is never replaced by a fragment. The same composition -- follicle, molecular
field left, cell field right -- is re-engineered per size band so it survives the pixel
budget it is given:

  full     128 px+   all 36 paths, 7-tone ramp, generous safe area
  compact  44-96 px  sub-pixel specks culled, ramp flattened to 3 tones, light dilation
  micro    24-40 px  field normalised to 14 discs, 2 tones, follicle dilated
  nano     16-20 px  field normalised to 9 discs, 2 tones, heaviest dilation

Why discs below 40 px: the source dots and hexagons are irregular, so at small sizes
their outlines anti-alias into grey mush (verified by rasterising -- see contact sheets).
Equal discs placed at each element's own centroid land cleanly on the pixel grid and
read as deliberate. Above 40 px the true outlines survive, so they are used.

Selection is never arbitrary: elements are taken largest-first, and any element whose
centre falls within `sep` of one already kept is skipped, because two dilated neighbours
that close would fuse into a single blob.

Input : outputs/drvarada-site/brand/source/varadas-logo-source.svg
Output: outputs/drvarada-site/brand/icons/
"""
import re
import pathlib

ROOT = pathlib.Path(
    r"c:\Users\VijayRaghavVarada\Documents\Github\agent-website-manager"
    r"\outputs\drvarada-site\brand")
SRC = ROOT / "source" / "varadas-logo-source.svg"
OUT = ROOT / "icons"
OUT.mkdir(exist_ok=True)

SPLIT = 520.0     # x separating the molecular field from the cell field
AXIS = 520.0      # follicle axis, for the cell-tone ramp
TILE = 512.0      # every icon is authored on a 512 square

NUM = re.compile(r"-?\d+(?:\.\d+)?")


# ------------------------------------------------------------------ source

def compress(d, nd=2):
    return " ".join(
        NUM.sub(lambda m: f"{round(float(m.group()), nd):g}", d).split())


def bbox(d):
    n = [float(x) for x in NUM.findall(d)]
    xs, ys = n[0::2], n[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def load():
    svg = SRC.read_text(encoding="utf-8")
    ds = [compress(x) for x in
          re.findall(r'<path[^>]*?\sd="\s*([^"]+)"', svg, re.S)]
    items, cells = [], []
    for i, d in enumerate(ds):
        x0, y0, x1, y1 = bbox(d)
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        if i < 2:
            layer, slot = "follicle", i       # 0 shaft+bulb, 1 sheath
        elif cx < SPLIT:
            layer, slot = "molecular-field", 0
        else:
            layer, slot = "cell-field", None
        it = dict(d=d, layer=layer, slot=slot, size=max(w, h),
                  area=w * h, ctr=(cx, cy))
        items.append(it)
        if slot is None:
            cells.append(it)
    lo = min(c["ctr"][0] - AXIS for c in cells)
    span = (max(c["ctr"][0] - AXIS for c in cells) - lo) or 1.0
    for c in cells:                          # nearest the follicle darkest
        c["slot"] = 2 + min(4, int(((c["ctr"][0] - AXIS) - lo) / span * 5))
    return items


# ------------------------------------------------------------------ colour

RAMP7 = {
    "light": ["#1E3A63", "#7C8A99", "#5F6E7F", "#71808F",
              "#8592A0", "#98A4B1", "#ADB7C1"],
    "dark":  ["#FFFFFF", "#8397AF", "#C6D3E1", "#B3C2D3",
              "#A2B3C7", "#93A6BC", "#8399B2"],
}
RAMP3 = {
    "light": ["#1E3A63", "#778593", "#657486", "#657486",
              "#8B97A4", "#8B97A4", "#8B97A4"],
    "dark":  ["#FFFFFF", "#8FA3BC", "#C6D3E1", "#C6D3E1",
              "#98ABC3", "#98ABC3", "#98ABC3"],
}
RAMP2 = {
    "light": ["#1E3A63"] + ["#7A8895"] * 6,
    "dark":  ["#FFFFFF"] + ["#A9BCD2"] * 6,
}

GROUNDS = {                     # name -> (tile fill, palette key, corner radius)
    "navy":        ("#1E3A63", "dark",  112),
    "light":       ("#F8F5F3", "light", 112),
    "transparent": (None,      "light", 0),
}

TIERS = {
    "full":    dict(mode="paths", cull=0.0,  ramp=RAMP7,
                    dilate=0.0, pad=0.085, band="128 px and up"),
    "compact": dict(mode="paths", cull=30.0, ramp=RAMP3,
                    dilate=3.0, pad=0.065, band="44 - 96 px"),
    "micro":   dict(mode="disc", keep=7, sep=90.0,  r=26.0, ramp=RAMP2,
                    dilate=8.0, pad=0.050, band="24 - 40 px"),
    "nano":    dict(mode="disc", keep=5, sep=115.0, r=34.0, ramp=RAMP2,
                    dilate=10.0, pad=0.045, band="16 - 20 px"),
}

VARS = ["--c1", "--c-sheath", "--c2a", "--c2b", "--c2c", "--c2d", "--c2e"]


def thin(group, sep, limit):
    """Biggest-first, but never two centres closer than `sep`."""
    kept = []
    for i in group:
        if len(kept) >= limit:
            break
        if all((i["ctr"][0] - k["ctr"][0]) ** 2
               + (i["ctr"][1] - k["ctr"][1]) ** 2 >= sep * sep for k in kept):
            kept.append(i)
    return kept


def select(items, t):
    fol = [i for i in items if i["layer"] == "follicle"]
    mol = sorted([i for i in items if i["layer"] == "molecular-field"],
                 key=lambda i: -i["area"])
    cel = sorted([i for i in items if i["layer"] == "cell-field"],
                 key=lambda i: -i["area"])
    if t["mode"] == "disc":
        mol, cel = thin(mol, t["sep"], t["keep"]), thin(cel, t["sep"], t["keep"])
    elif t["cull"]:
        mol = [i for i in mol if i["size"] >= t["cull"]]
        cel = [i for i in cel if i["size"] >= t["cull"]]
    return fol, mol, cel


def build(items, tier_name, ground, radius=None, svg_id=None, adaptive=False):
    t = TIERS[tier_name]
    fill_bg, pal_key, rx = GROUNDS[ground]
    if radius is not None:
        rx = radius
    fol, mol, cel = select(items, t)
    disc = t["mode"] == "disc"

    # extent of what will actually be drawn, dilation and disc radius included
    g = t["dilate"] / 2
    xs = [b for i in fol for b in (bbox(i["d"]),)]
    x0 = min(b[0] for b in xs) - g
    y0 = min(b[1] for b in xs) - g
    x1 = max(b[2] for b in xs) + g
    y1 = max(b[3] for b in xs) + g
    for i in mol + cel:
        if disc:
            cx, cy = i["ctr"]
            bx = (cx - t["r"], cy - t["r"], cx + t["r"], cy + t["r"])
        else:
            b = bbox(i["d"])
            bx = (b[0] - g, b[1] - g, b[2] + g, b[3] + g)
        x0, y0 = min(x0, bx[0]), min(y0, bx[1])
        x1, y1 = max(x1, bx[2]), max(y1, bx[3])

    w, h = x1 - x0, y1 - y0
    sc = (TILE * (1 - 2 * t["pad"])) / max(w, h)
    tx = TILE / 2 - (x0 + w / 2) * sc
    ty = TILE / 2 - (y0 + h / 2) * sc

    pal = t["ramp"][pal_key]
    paint = (lambda s: f"var({VARS[s]})") if adaptive else (lambda s: pal[s])

    idattr = f' id="{svg_id}"' if svg_id else ""
    s = (f'<svg xmlns="http://www.w3.org/2000/svg"{idattr} '
         f'viewBox="0 0 512 512" role="img" '
         f'aria-label="Dr. Varada&apos;s Skin &amp; Hair Center">\n')
    if adaptive:
        def decl(p):
            return " ".join(f"{v}:{c};" for v, c in zip(VARS, p))
        s += ("  <style>\n"
              f"    #{svg_id} {{ {decl(t['ramp']['light'])} }}\n"
              f"    @media (prefers-color-scheme: dark) {{"
              f" #{svg_id} {{ {decl(t['ramp']['dark'])} }} }}\n"
              f"    #{svg_id}[data-theme='dark'] {{ {decl(t['ramp']['dark'])} }}\n"
              f"    #{svg_id}[data-theme='light'] {{"
              f" {decl(t['ramp']['light'])} }}\n"
              "  </style>\n")
    if fill_bg:
        s += f'  <rect width="512" height="512" rx="{rx}" fill="{fill_bg}"/>\n'
    s += f'  <g transform="translate({tx:.2f} {ty:.2f}) scale({sc:.5f})">\n'

    for name, group in (("molecular-field", mol), ("follicle", fol),
                        ("cell-field", cel)):
        if not group:
            continue
        s += f'    <g id="{name}">\n'
        for i in group:
            c = paint(i["slot"])
            if disc and name != "follicle":
                cx, cy = i["ctr"]
                s += (f'      <circle cx="{cx:.1f}" cy="{cy:.1f}" '
                      f'r="{t["r"]:g}" fill="{c}"/>\n')
            else:
                st = (f' stroke="{c}" stroke-width="{t["dilate"]:g}"'
                      f' stroke-linejoin="round" stroke-linecap="round"'
                      if t["dilate"] else "")
                s += f'      <path fill="{c}"{st} d="{i["d"]}"/>\n'
        s += "    </g>\n"
    return s + "  </g>\n</svg>\n", len(fol) + len(mol) + len(cel)


def main():
    items = load()
    made = []
    for tier in TIERS:
        for ground in GROUNDS:
            svg, n = build(items, tier, ground)
            p = OUT / f"icon-{tier}-{ground}.svg"
            p.write_text(svg, encoding="utf-8")
            made.append((p, n))

    # iOS applies its own mask, so the Apple asset must be a hard square
    svg, n = build(items, "compact", "navy", radius=0)
    p = OUT / "icon-compact-navy-square.svg"
    p.write_text(svg, encoding="utf-8")
    made.append((p, n))

    # one adaptive file for the browser tab; a single favicon.svg cannot know
    # what size it is being drawn at, so compact is the safe compromise
    svg, n = build(items, "compact", "transparent",
                   svg_id="dv-favicon", adaptive=True)
    p = OUT / "favicon.svg"
    p.write_text(svg, encoding="utf-8")
    made.append((p, n))

    for p, n in made:
        print(f"  {p.name:34} {n:>2} elements  {p.stat().st_size:>6} B")


if __name__ == "__main__":
    main()
