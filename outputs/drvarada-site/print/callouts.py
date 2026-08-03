"""Leader-line callouts on a printed figure, from the site's own label data.

The website's diagrams carry authored labels:

    {"text": "Pigment cap over each nucleus", "x": 40, "y": 33, "lead": 21}

`x` and `y` are percentages of the figure. `lead` is the length of the leader
line — and for every label on a given diagram **x + lead lands on the same
value** (61% on both vitiligo figures). That is not a coincidence: the
illustrator left a column of empty space in the artwork and the labels are
authored to terminate against it. The diagrams were drawn to be labelled.

TWO TREATMENTS, AND THE DATA PICKS
    `chrome.py` does not use one renderer for every figure, and neither does
    this. The content says which it was drawn for:

      labels carry `lead`   -> PLATE. The illustrator left a clear column and
                               authored every leader to terminate against it.
      `rail: true`, no lead -> KEYED. The artwork fills its frame edge to edge
                               (usually two sub-panels), so there is no clear
                               space, the words go BELOW, and only numbers
                               sit on the picture.

    Forcing a plate onto a rail figure is what put "Confetti spots" across the
    second sub-panel of the active-vs-stable diagram: with no `lead` the rail
    fell back to a guessed 62%, which on that image is the middle of the right
    panel. The absent `lead` was the data saying "not this treatment".

WHAT THE PLATE REPLACES, AND WHY
    The first print version put a 3.6mm numbered disc ON the artwork at (x, y)
    with a key underneath. It covered the thing it pointed at — a disc is
    forty times the area of the feature it marks, and on the repigmentation
    figure it sat squarely over the follicles that are the whole subject.

    A disc is what you use when there is nowhere for a word to go. Here there
    is somewhere: the space the illustrator left. So this is the anatomical
    plate convention instead —

        a 1.2mm ring on the point   (marks without hiding)
        a 0.25mm hairline out       (the authored `lead`)
        the words in the clear space, set against a common rail

    Nothing larger than a full stop sits on the artwork.

DE-COLLISION
    Two labels closer in `y` than a line of type will overlap once the words
    are set. The site can let them sit where they were authored because its
    figure is 700px tall; at 46mm they touch. `_rows()` pushes each label down
    to clear the one above and the leader becomes a two-segment elbow, so the
    line still lands exactly on the feature while the words sit where they fit.

READ THE DROP NOTE
    If a figure has more labels than the panel can hold, the surplus is
    reported on stderr rather than silently trimmed. A dropped label is a fact
    the reader does not get; which ones go is an editorial decision.
"""

from __future__ import annotations

MAX_LABELS = 5
RAIL_FALLBACK = 62          # % across, when a label carries no `lead`


def _lines(text: str, width_mm: float, size_mm: float) -> int:
    """How many lines this label will set to.

    Measured off an average advance of 0.52em, which is what Manrope actually
    runs at for mixed-case English. It only has to be right to the line, and a
    wrong answer here shows up as two labels touching — which is precisely the
    bug the first version shipped, because it assumed every label was one line.
    """
    per_line = max(8, int(width_mm / (size_mm * 0.52)))
    return max(1, -(-len(text) // per_line))


def _rows(labs: list[dict], stage_mm: float, line_mm: float,
          width_mm: float, size_mm: float) -> list[float]:
    """A y position per label, in %, with no two overlapping once set.

    Greedy from the top: keep the authored y where it fits, push down where it
    does not. Pushing down rather than spreading evenly means a label that had
    room keeps the position the illustrator chose for it.
    """
    if stage_mm <= 0:
        return [lab.get("y", 50) for lab in labs]
    out: list[float] = []
    floor = 0.0
    for lab in labs:
        y = max(float(lab.get("y", 50)), floor)
        out.append(y)
        # The NEXT label must clear this one's full set height, not one line.
        tall = _lines(lab["text"], width_mm, size_mm) * line_mm
        floor = y + 100 * (tall + 0.8) / stage_mm
    # If the stack has run off the bottom, lift the whole thing rather than
    # letting the last label leave the figure. Measured against the LAST
    # label's own set height — `gap` no longer exists now that each label
    # reserves its own.
    if not out:
        return out
    last = _lines(labs[-1]["text"], width_mm, size_mm) * line_mm
    over = out[-1] + 100 * (last / 2) / stage_mm - 100
    return [y - over for y in out] if over > 0 else out


def plate(d: dict, *, cap: bool = True, limit: int = MAX_LABELS,
          cls: str = "", stage_mm: float = 46, line_mm: float = 3.1,
          measure_mm: float = 126.5, size_mm: float = 2.4) -> str:
    """A figure with leader-line callouts set into the artwork's own space.

    The label column is DERIVED, not chosen. The image is capped by height, so
    its rendered width is `height x aspect`; the rail sits at `x + lead` across
    that; the words get what is left, plus the white the centred figure leaves
    beside it. Picking a width by hand is how the first version put a 40mm
    label in 32mm of room and let it hang off the picture.
    """
    labs = [lab for lab in (d.get("labels") or []) if lab.get("text")]
    labs.sort(key=lambda lab: lab.get("y", 0))
    if len(labs) > limit:
        print(f"    note  {d.get('eyebrow', '?')}: "
              f"{len(labs) - limit} label(s) not shown (cap {limit})")
        labs = labs[:limit]

    im = d.get("image") or {}
    aspect = (im.get("w") or 16) / (im.get("h") or 9)
    stage_w = min(measure_mm, stage_mm * aspect)
    rail_pct = min((float(lab.get("x", 0)) + float(lab.get("lead", 0))
                    for lab in labs), default=RAIL_FALLBACK) or RAIL_FALLBACK
    slack = max(0.0, (measure_mm - stage_w) / 2 - 1)
    label_w = max(18.0, stage_w * (100 - rail_pct) / 100 + slack - 2)
    rows = _rows(labs, stage_mm, line_mm, label_w, size_mm)

    marks, leaders, words = [], [], []
    for i, (lab, yr) in enumerate(zip(labs, rows), 1):
        x, y = float(lab.get("x", 50)), float(lab.get("y", 50))
        rail = x + float(lab["lead"]) if lab.get("lead") else RAIL_FALLBACK
        marks.append(f'<i class="dot" style="left:{x}%;top:{y}%"></i>')
        # Elbow: straight out of the mark first, then across to the row. The
        # straight start is what makes it read as pointing AT something.
        elbow = max(x + 2.5, rail - 6)
        leaders.append(
            f'<polyline points="{x},{y} {elbow},{y} {rail},{yr}" '
            f'vector-effect="non-scaling-stroke"/>')
        words.append(
            f'<span class="lab" style="left:{rail}%;top:{yr}%;'
            f'width:{label_w:.1f}mm">'
            f'<b>{i}</b>{lab["text"]}</span>')

    caption = (f'<figcaption class="cap">{d["caption"]}</figcaption>'
               if cap else "")
    return f"""<figure class="fig {cls}">
  <div class="stage">
    <img src="{d["src"]}" alt="">
    <svg class="leads" viewBox="0 0 100 100" preserveAspectRatio="none">
      {"".join(leaders)}
    </svg>
    {"".join(marks)}{"".join(words)}
  </div>
  {caption}
</figure>"""


CSS = """
  .fig {{ margin-top: {gap}mm; }}
  /* THE STAGE MUST BE THE PICTURE, NOT A BOX THE PICTURE SITS IN.
     Every callout is placed at a percentage of this element. With
     `object-fit: contain` a wide diagram letterboxes inside a full-width box
     and every percentage lands short of the artwork. */
  .stage {{ position: relative; background: {wash}; width: fit-content;
            max-width: 100%; margin: 0 auto; }}
  .stage img {{ display: block; width: auto; height: auto;
                max-height: {maxh}mm; max-width: 100%; }}
  /* preserveAspectRatio: none makes the viewBox a plain percentage grid, so a
     point is where the label data says it is. It also scales the stroke, which
     `vector-effect` on each polyline undoes — without it the hairline is
     thicker across than down. */
  .leads {{ position: absolute; inset: 0; width: 100%; height: 100%;
            fill: none; stroke: {ink}; stroke-width: .25mm;
            stroke-opacity: .6; }}
  .dot {{ position: absolute; width: 1.2mm; height: 1.2mm;
          transform: translate(-50%, -50%); border-radius: 50%;
          background: {ink}; box-shadow: 0 0 0 .3mm rgba(255,255,255,.85); }}
  /* width is set per label, from the space the artwork actually leaves */
  .lab {{ position: absolute; transform: translateY(-50%);
          font-size: {labsz}mm; line-height: {line}mm;
          color: {ink}; font-weight: 600; padding-left: 1.4mm; }}
  .lab b {{ color: {deep}; font-weight: 800; margin-right: 1mm; }}

  .pin {{ position: absolute; width: 2.6mm; height: 2.6mm;
          transform: translate(-50%, -50%); border-radius: 50%;
          background: {ink}; color: #fff; font-style: normal;
          font-size: 1.7mm; font-weight: 800; line-height: 2.6mm;
          text-align: center; box-shadow: 0 0 0 .3mm rgba(255,255,255,.9); }}
  .key {{ list-style: none; columns: 2; column-gap: {gap}mm;
          margin-top: {line}mm; }}
  .key li {{ font-size: 2.3mm; line-height: {line}mm; color: {grey};
             break-inside: avoid; padding-left: 4mm; text-indent: -4mm; }}
  .key b {{ display: inline-block; width: 3.2mm; color: {deep};
            font-weight: 800; text-indent: 0; }}
"""


def css(*, ink: str, grey: str, deep: str, wash: str, baseline: float,
        maxh: float, label_size: float = 2.4, line_mm: float = 3.1) -> str:
    return CSS.format(ink=ink, grey=grey, deep=deep, wash=wash, gap=baseline,
                      maxh=maxh, labsz=label_size, line=line_mm)


# ── keyed: numbers on the picture, words beneath ────────────────────────────

def keyed(d: dict, *, cap: bool = True, limit: int = MAX_LABELS,
          cls: str = "", **_ignored) -> str:
    """For figures with no clear space of their own.

    The pin is 2.6mm, not the 3.6mm the first attempt used: it has to be read,
    not to dominate, and on a two-panel figure it is landing on artwork that
    matters. Numbers run top-to-bottom, left-to-right — the key has no leader
    for the eye to follow, so the numbering has to be the reading order itself.
    """
    labs = [lab for lab in (d.get("labels") or []) if lab.get("text")]
    labs.sort(key=lambda lab: (round(lab.get("y", 0) / 12), lab.get("x", 0)))
    if len(labs) > limit:
        print(f"    note  {d.get('eyebrow', '?')}: "
              f"{len(labs) - limit} label(s) not shown (cap {limit})")
        labs = labs[:limit]
    discs = "".join(
        f'<i class="pin" style="left:{lab["x"]}%;top:{lab["y"]}%">{i}</i>'
        for i, lab in enumerate(labs, 1))
    keys = "".join(f'<li><b>{i}</b>{lab["text"]}</li>'
                   for i, lab in enumerate(labs, 1))
    caption = (f'<figcaption class="cap">{d["caption"]}</figcaption>'
               if cap else "")
    return f"""<figure class="fig {cls}">
  <div class="stage"><img src="{d["src"]}" alt="">{discs}</div>
  <ol class="key">{keys}</ol>
  {caption}
</figure>"""


def figure(d: dict, **kw) -> str:
    """Render a diagram the way its own data says it was drawn to be read."""
    labs = [lab for lab in (d.get("labels") or []) if lab.get("text")]
    if d.get("rail") or not any(lab.get("lead") for lab in labs):
        return keyed(d, **kw)
    return plate(d, **kw)
