"""Build the full logo lockups: symbol + wordmark (+ tagline).

Every letterform is outlined, so the artwork carries no font dependency. Metrics are
expressed in cap units -- the name's cap height is 100 and everything else is a ratio of
it -- so the whole system rescales cleanly and the proportions stay intentional rather
than accidental.

Typeface note: the wordmark is set in the brand's own faces, Gabarito for the name and
Manrope for the descriptor and tagline, matching the website's display/text pairing.
If the original artwork used a different face, hand over the font and rerun -- only the
two constants below change.

Output: outputs/drvarada-site/brand/lockups/
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from icon_system import load, RAMP7, bbox            # noqa: E402
from type_outline import outline, cap_height          # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lockups"
OUT.mkdir(exist_ok=True)

NAME = "Dr. VARADA’s"
DESC = "SKIN & HAIR CENTER"
TAG = "Regenerate · Restore · Reveal"

# --- type spec, in cap units (name cap height = 100) ------------------------
NAME_FACE, NAME_WT, NAME_CAP, NAME_TRACK = "Gabarito", 700, 100.0, -0.006
DESC_FACE, DESC_WT, DESC_TRACK = "Manrope", 600, 0.44
TAG_FACE, TAG_WT, TAG_CAP = "Manrope", 500, 25.0

BL_DESC = 48.0      # descriptor baseline, below the name baseline
RULE_Y = 31.0       # hairline, below the descriptor baseline
RULE_W = 2.4        # hairline thickness
BL_TAG = 33.0       # tagline baseline, below the hairline

MARK_RATIO = 1.85       # horizontal: mark height as a multiple of text block height
MARK_W_FRAC = 0.42      # stacked: mark width as a fraction of the wordmark width
MARK_GAP = 0.44     # space between mark and text, in name cap units
STACK_GAP = 0.36    # space between mark and wordmark when stacked
PAD = 0.34          # clear space around the whole lockup, in name cap units

PALETTES = {
    "light": RAMP7["light"],
    "dark": RAMP7["dark"],
    "flat-navy": ["#1E3A63"] * 7,
    "mono-dark": ["#12202F"] * 7,
    "mono-light": ["#FFFFFF"] * 7,
}
VARS = ["--c1", "--c-sheath", "--c2a", "--c2b", "--c2c", "--c2d", "--c2e"]


def em(face, weight, cap):
    return cap / cap_height(face, weight)


def justified_em(text, face, weight, track, target_w):
    """Em size at which `text`, letterspaced by `track`, is exactly `target_w` wide.

    Width is linear in em at fixed tracking, so one measurement gives the answer. This
    is what sets the descriptor: it is letterspaced out to match the name exactly, which
    turns the wordmark into a clean rectangle instead of a ragged two-line stack.
    """
    probe = 100.0
    return probe * target_w / outline(text, face, weight, probe, track)[1]


def justified_track(text, face, weight, em_size, target_w):
    """Letter spacing at which `text` set at `em_size` is exactly `target_w` wide.

    Width is linear in tracking, so two measurements pin it exactly. The tagline is
    justified this way rather than by growing its size: the separators want air around
    them, and the line has to stay quieter than the descriptor above it.
    """
    lo, hi = 0.0, 1.0
    w0 = outline(text, face, weight, em_size, lo)[1]
    w1 = outline(text, face, weight, em_size, hi)[1]
    return lo + (hi - lo) * (target_w - w0) / (w1 - w0)


def text_block(tagline, align):
    """Lines of the wordmark, the hairline rule, and the block's own measurements.

    Everything is measured from the name's baseline at y = 0.
    """
    name_em = em(NAME_FACE, NAME_WT, NAME_CAP)
    name_w = outline(NAME, NAME_FACE, NAME_WT, name_em, NAME_TRACK)[1]
    desc_em = justified_em(DESC, DESC_FACE, DESC_WT, DESC_TRACK, name_w)
    spec = [
        ("name", 0, NAME, NAME_FACE, NAME_WT, name_em, NAME_TRACK, 0.0),
        ("descriptor", 1, DESC, DESC_FACE, DESC_WT, desc_em, DESC_TRACK, BL_DESC),
    ]
    rule = None
    if tagline:
        tag_em = em(TAG_FACE, TAG_WT, TAG_CAP)
        tag_track = justified_track(TAG, TAG_FACE, TAG_WT, tag_em, name_w)
        spec.append(("tagline", 1, TAG, TAG_FACE, TAG_WT, tag_em, tag_track,
                     BL_DESC + RULE_Y + BL_TAG))
        rule = (0.0, BL_DESC + RULE_Y - RULE_W / 2, name_w, RULE_W)

    widths = [outline(t, f, w, e, tr)[1] for _, _, t, f, w, e, tr, _ in spec]
    block_w = max(widths)
    lines = []
    for (sid, slot, t, f, w, e, tr, bl), lw in zip(spec, widths):
        x = (block_w - lw) / 2 if align == "center" else 0.0
        d, _ = outline(t, f, w, e, tr, y=bl, x=x)
        lines.append((sid, slot, d))
    return lines, rule, block_w, -NAME_CAP, spec[-1][-1]


def mark_paths():
    items = load()
    bs = [bbox(i["d"]) for i in items]
    x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
    x1, y1 = max(b[2] for b in bs), max(b[3] for b in bs)
    return items, (x0, y0, x1 - x0, y1 - y0)


def compose(form, tagline):
    """-> (elements, width, height); elements are (kind, payload, slot)."""
    items, (mx, my, mw, mh) = mark_paths()
    align = "center" if form == "stacked" else "left"
    lines, rule, block_w, cap_top, last_bl = text_block(tagline, align)
    block_h = last_bl - cap_top
    pad = PAD * NAME_CAP
    els = []
    if rule:
        els.append(("rule", rule, 1))

    if form == "wordmark":
        for sid, slot, d in lines:
            els.append(("path", d, slot))
        return els, block_w + 2 * pad, block_h + 2 * pad, (pad, pad - cap_top)

    # horizontal: the mark is measured against the height of the text beside it.
    # stacked: against the width of the text beneath it. Same mark, different neighbour.
    if form == "horizontal":
        scale = (block_h * MARK_RATIO) / mh
    else:
        scale = (block_w * MARK_W_FRAC) / mw
    mark_w, mark_h = mw * scale, mh * scale

    if form == "horizontal":
        gap = MARK_GAP * NAME_CAP
        total_w = mark_w + gap + block_w
        total_h = max(mark_h, block_h)
        mark_x = 0.0
        mark_y = (total_h - mark_h) / 2
        text_dx = mark_w + gap
        text_dy = (total_h - block_h) / 2 - cap_top
    else:                                    # stacked
        gap = STACK_GAP * NAME_CAP
        total_w = max(mark_w, block_w)
        total_h = mark_h + gap + block_h
        mark_x = (total_w - mark_w) / 2
        mark_y = 0.0
        text_dx = (total_w - block_w) / 2
        text_dy = mark_h + gap - cap_top

    els.append(("mark", (items, mx, my, scale, mark_x + pad, mark_y + pad), None))
    for sid, slot, d in lines:
        els.append(("path", d, slot))
    return els, total_w + 2 * pad, total_h + 2 * pad, (text_dx + pad, text_dy + pad)


def render(form, tagline, palette_name, svg_id=None, adaptive=False):
    els, W, H, (tdx, tdy) = compose(form, tagline)
    pal = PALETTES[palette_name]
    paint = (lambda s: f"var({VARS[s]})") if adaptive else (lambda s: pal[s])
    label = "Dr. Varada&apos;s Skin &amp; Hair Center"

    idattr = f' id="{svg_id}"' if svg_id else ""
    s = (f'<svg xmlns="http://www.w3.org/2000/svg"{idattr} '
         f'viewBox="0 0 {W:.1f} {H:.1f}" role="img" aria-label="{label}">\n')
    if adaptive:
        def decl(p):
            return " ".join(f"{v}:{c};" for v, c in zip(VARS, p))
        s += ("  <style>\n"
              f"    #{svg_id} {{ {decl(PALETTES['light'])} }}\n"
              f"    @media (prefers-color-scheme: dark) {{"
              f" #{svg_id} {{ {decl(PALETTES['dark'])} }} }}\n"
              f"    #{svg_id}[data-theme='dark'] {{ {decl(PALETTES['dark'])} }}\n"
              f"    #{svg_id}[data-theme='light'] {{ {decl(PALETTES['light'])} }}\n"
              "  </style>\n")

    for kind, payload, slot in els:
        if kind != "mark":
            continue
        items, mx, my, sc, ox, oy = payload
        s += (f'  <g id="mark" transform="translate({ox:.2f} {oy:.2f}) '
              f'scale({sc:.5f}) translate({-mx:.2f} {-my:.2f})">\n')
        for layer in ("molecular-field", "follicle", "cell-field"):
            group = [i for i in items if i["layer"] == layer]
            if not group:
                continue
            s += f'    <g id="{layer}">\n'
            for i in group:
                s += f'      <path fill="{paint(i["slot"])}" d="{i["d"]}"/>\n'
            s += "    </g>\n"
        s += "  </g>\n"

    s += f'  <g id="wordmark" transform="translate({tdx:.2f} {tdy:.2f})">\n'
    for kind, payload, slot in els:
        if kind == "path":
            s += f'    <path fill="{paint(slot)}" d="{payload}"/>\n'
        elif kind == "rule":
            rx, ry, rw, rh = payload
            s += (f'    <rect x="{rx:.2f}" y="{ry:.2f}" width="{rw:.2f}" '
                  f'height="{rh:.2f}" fill="{paint(slot)}"/>\n')
    return s + "  </g>\n</svg>\n"


FORMS = [
    ("horizontal", False), ("horizontal-tagline", True),
    ("stacked", False), ("stacked-tagline", True),
    ("wordmark", False), ("wordmark-tagline", True),
]


def main():
    made = []
    for form_name, tag in FORMS:
        form = form_name.replace("-tagline", "")
        for pal in PALETTES:
            p = OUT / f"logo-{form_name}-{pal}.svg"
            p.write_text(render(form, tag, pal), encoding="utf-8")
            made.append(p)
        sid = f"dv-{form_name}"
        p = OUT / f"logo-{form_name}-adaptive.svg"
        p.write_text(render(form, tag, "light", svg_id=sid, adaptive=True),
                     encoding="utf-8")
        made.append(p)

    for form_name, tag in FORMS:
        _, W, H, _ = compose(form_name.replace("-tagline", ""), tag)
        print(f"  {form_name:22} {W:7.1f} x {H:6.1f}  ratio {W / H:5.2f}")
    print(f"  {len(made)} files")


if __name__ == "__main__":
    main()
