"""Build a contact sheet of every diagram on the site, for review in one place.

Label positions are percentages chosen by eye against the artwork, so the only
honest way to check them is to look. Hunting six figures across six built pages
to do that is slow and easy to do incompletely; this lifts each `<figure
class="diagram">` out of `dist/` and stacks them on one page with the real
stylesheet, so a placement error is visible in a single scroll.

    python diagram_sheet.py            # -> .diagram-queue/review.html

It reads the BUILT pages rather than the content modules, so what it shows is
what the browser will show, including anything the build changed on the way.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
DIST = SITE / "dist"
OUT = SITE / ".diagram-queue" / "review.html"

FIGURE = re.compile(r'<figure class="diagram">.*?</figure>', re.S)
HEAD = re.compile(r'<div class="head-block">')


def collect() -> list[tuple[str, str, str]]:
    """Every diagram figure in `dist/`, with the heading block above it.

    The heading is found by scanning backwards from the figure rather than by
    one regex spanning both. A `head-block` contains nested `</div>`s, so
    `head-block.*?</div>\\s*<figure` does not stop at the end of the heading —
    it stretches from the first heading on the page to the figure and drags
    every section in between onto the sheet. A review tool that quietly shows
    the wrong thing is worse than no review tool.
    """
    found = []
    for page in sorted(DIST.glob("*.html")):
        markup = page.read_text(encoding="utf-8")
        for m in FIGURE.finditer(markup):
            before = markup[:m.start()]
            starts = [h.start() for h in HEAD.finditer(before)]
            head = before[starts[-1]:] if starts else ""
            # Stacking six figures makes every one of them below the fold, and
            # a lazily loaded image that never enters view never loads — a
            # headless screenshot of the sheet then shows an empty stage with
            # labels floating on it, which reads as a broken diagram.
            fig = m.group(0).replace('loading="lazy"', 'loading="eager"')
            found.append((page.stem, head, fig))
    return found


def main() -> None:
    items = collect()
    blocks = []
    for slug, head, fig in items:
        blocks.append(
            f'<section class="sheet-item">'
            f'<p class="sheet-slug">{html.escape(slug)}</p>'
            f'{head}{fig}</section>')

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diagram contact sheet — {len(items)} figures</title>
<!-- The lifted markup carries dist-relative asset paths. Without this the
     sheet renders every figure as broken alt text and looks like a bug in the
     diagrams rather than in the sheet. -->
<base href="../dist/">
<link rel="stylesheet" href="assets/design-system.css">
<link rel="stylesheet" href="assets/site.css">
<style>
  body {{ background: var(--ground); margin: 0; }}
  .sheet {{ max-width: 1180px; margin: 0 auto; padding: 40px 24px 80px; }}
  .sheet h1 {{ font-size: 28px; margin: 0 0 8px; }}
  .sheet-lede {{ color: var(--ink-2); margin: 0 0 40px; }}
  .sheet-item {{ background: var(--paper); border-radius: var(--r);
    padding: 28px; margin-bottom: 32px; border: 1px solid var(--line); }}
  .sheet-slug {{ font: 600 12px/1 var(--body); letter-spacing: .1em;
    text-transform: uppercase; color: var(--ink-3); margin: 0 0 18px; }}
</style></head>
<body><div class="sheet">
<h1>Diagram contact sheet</h1>
<p class="sheet-lede">{len(items)} figures, lifted from the built pages with the
live stylesheet. Check that every numbered dot sits on the structure it names
and that no two labels overlap.</p>
{"".join(blocks)}
</div></body></html>""", encoding="utf-8")
    print(f"{len(items)} figure(s) -> {OUT.relative_to(SITE)}")
    for slug, _, _ in items:
        print(f"  {slug}")


if __name__ == "__main__":
    main()
