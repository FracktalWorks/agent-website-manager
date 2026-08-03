"""Lay out the label rail beneath every `rail: True` diagram in content/.

WHAT IT DECIDES
  Only `row` and `side`. Anchors (`x`/`y`) are read off a grid sheet and are
  never touched — this tool moves WORDS, not rings.

THE CONSTRAINT THAT IS NOT OBVIOUS
  A rail chip's words run rightward from its own anchor, over the anchors of
  its neighbours. A riser that has to travel PAST that chip's row would cut
  straight through those words. So a label whose anchor is covered by another
  label's words must sit on the SHALLOWER row — which forces the sweep to run
  right to left. Sweeping left to right sees only the risers placed so far,
  and iterating that to a fixed point diverges: rows just march downward
  (one figure reached eighteen).

  A chip that would run off the right-hand edge is REVERSED, not dragged
  inward. Dragging leaves its own riser coming down through its own text, and
  leaving it puts the whole page into horizontal scroll — which `verify.py`
  reports as an overflow, so it is caught either way.

WHEN IT REFUSES
  If no arrangement satisfies all three constraints, the figure is
  geometrically impossible as written: its texts are wider than the gaps
  between its anchors. The cure is editorial — shorten the words. They are
  legend entries; the intro and caption carry the explanation.

USAGE
  python diagram_rail.py            # lay out every rail diagram
  python diagram_rail.py --check    # report only, change nothing
"""
import argparse
import pathlib
import re
import sys
import unicodedata

# This prints Telugu and Devanagari label text. A Windows console defaults to
# cp1252 and raises on the first non-Latin character, killing the run partway
# through a file — so the stream is reconfigured rather than the output made
# ASCII-safe, which would hide which label the message is about.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTENT = pathlib.Path("content")

STAGE_PX = 640     # narrowest stage above the 720px breakpoint — the worst case
DISC = 22          # the number disc, from .dg-n
GAP = 8            # disc-to-text gap, from .dg-rlab
CH = 6.6           # ~1 character of 13px semibold
WRAP = 24          # .dg-rail .dg-t max-width, in ch
PAD = 10           # px of clear air demanded between neighbours

LABEL_RE = re.compile(r'\{"text": "(?P<t>[^"]*)"(?P<rest>[^}]*)\}')
# Comment lines are allowed between `rail` and `labels`, and are stepped over
# rather than matched, so the rewrite leaves them untouched. Without this the
# pattern simply stopped matching when a figure grew a note explaining why its
# coordinates had moved — the tool then reported success over a smaller set of
# figures than it had the run before, which is the worst way for a gate to fail.
SEC_RE = re.compile(
    r'"rail": True,\n(?:[ \t]*#[^\n]*\n)*(?P<labels>\s*"labels": \[.*?\n\s*\],\n)',
    re.S)


def glyphs(text):
    """Rendered glyph count — combining marks do not take their own width.

    `len()` is wrong for the Telugu and Hindi labels: a Telugu cluster like
    మెలనోసైట్ is nine codepoints but renders as about five glyphs, because the
    vowel signs and the virama attach to the consonant they follow. Counting
    codepoints over-measures those chips by half, which invents rail rows and
    reports crossings that are not there.
    """
    return sum(1 for ch in text if unicodedata.category(ch) != "Mn")


def chip_pct(text):
    """How wide a rail chip renders, as a percentage of the narrowest stage."""
    n = glyphs(text)
    # Indic glyphs carry more ink per advance than Latin at the same size.
    wide = 1.15 if any(ord(ch) > 0x0900 for ch in text) else 1.0
    return (DISC + GAP + min(n, WRAP) * CH * wide) / STAGE_PX * 100


def lay_out(labels):
    """Return (rows, sides, crossings) for one figure's labels."""
    half = (DISC / 2) / STAGE_PX * 100
    pad = PAD / STAGE_PX * 100
    spans, sides = {}, [False] * len(labels)
    for i, lab in enumerate(labels):
        x, w = lab["x"], chip_pct(lab["text"])
        sides[i] = x + w - half > 100
        spans[i] = ((x + half - w - pad, x + half) if sides[i]
                    else (x - half, x - half + w + pad))

    rows, placed = [0] * len(labels), []
    for i in sorted(range(len(labels)), key=lambda k: -labels[k]["x"]):
        left, right = spans[i]
        floor = max((rows[j] for j in placed if left <= labels[j]["x"] <= right),
                    default=0)
        r = floor
        while any(rows[j] == r and spans[j][0] < right and left < spans[j][1]
                  for j in placed):
            r += 1
        rows[i], _ = r, placed.append(i)

    bad = []
    for i, (left, right) in spans.items():
        for j, lab in enumerate(labels):
            if i != j and rows[j] > rows[i] and left <= lab["x"] <= right:
                bad.append(f'riser {j + 1} crosses "{labels[i]["text"]}"')
    return rows, sides, bad


def parse(block):
    out = []
    for m in LABEL_RE.finditer(block):
        lab = {"text": m["t"],
               "x": int(re.search(r'"x": (\d+)', m["rest"])[1]),
               "y": int(re.search(r'"y": (\d+)', m["rest"])[1])}
        # `find` is what `diagram_anchors.py` checks the anchor against. This
        # emitter rewrites the label source wholesale, so anything it does not
        # read here is destroyed on the next run — and a declaration that
        # silently disappears is worse than never having made one, because the
        # gate then reports the label as unchecked rather than as broken.
        found = re.search(r'"find": "([^"]+)"', m["rest"])
        if found:
            lab["find"] = found[1]
        out.append(lab)
    return out


def render(labels, rows, sides, indent):
    out = [f'{indent}"labels": [\n']
    for lab, r, left in zip(labels, rows, sides):
        extra = ', "side": "left"' if left else ""
        extra += f', "row": {r}' if r else ""
        extra += f', "find": "{lab["find"]}"' if lab.get("find") else ""
        out.append(f'{indent}    {{"text": "{lab["text"]}", "x": {lab["x"]}, '
                   f'"y": {lab["y"]}{extra}}},\n')
    out.append(f'{indent}],\n')
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args()

    figures = crossings = 0
    for path in sorted(CONTENT.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        out, at = [], 0
        for m in SEC_RE.finditer(text):
            block = m.group("labels")
            indent = " " * (len(block) - len(block.lstrip("\n").lstrip()) - 1)
            labels = parse(block)
            if not labels:
                continue
            rows, sides, bad = lay_out(labels)
            figures += 1
            crossings += len(bad)
            name = re.search(r'img/diagrams/([\w.-]+)\.webp',
                             text[m.end():m.end() + 900])
            print(f'  {path.name:<22} {(name[1] if name else "?"):<28} '
                  f'rows={max(rows) + 1} ({", ".join(map(str, rows))})'
                  f'{"  left-run" if any(sides) else ""}')
            for b in bad:
                print(f'     !! {b} — shorten it')
            out.append(text[at:m.start("labels")])
            out.append(render(labels, rows, sides, indent))
            at = m.end("labels")
        out.append(text[at:])
        new = "".join(out)
        if new != text and not args.check:
            path.write_text(new, encoding="utf-8")

    print(f"\n{figures} rail figure(s), {crossings} riser/label crossing(s)")
    return 1 if crossings else 0


if __name__ == "__main__":
    sys.exit(main())
