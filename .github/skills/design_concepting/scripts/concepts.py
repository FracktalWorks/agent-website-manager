"""Design-concept scaffolding and compare-page generation.

A concept is a throwaway single-file HTML mockup of a design direction, living
at outputs/<project>/concepts/<direction>/index.html. This script owns the
deterministic parts of the flow; the mockups themselves are authored work.

    python concepts.py new <project> <direction> --title "Calm editorial"
    python concepts.py compare <project>          # (re)writes concepts/compare.html
    python concepts.py decide <project> <direction>
    python concepts.py list <project>

<project> is the folder name under outputs/ (e.g. drvarada-site, acme-site).
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
OUTPUTS = REPO / "outputs"

NOTES_TEMPLATE = """\
# {title}

**Direction:** `{slug}`
**Design read:** <page kind> for <audience>, with a <vibe> language.
**Dials:** variance ? / motion ? / density ?
**Foundation:** <design-system id from agent-data/design-systems, or the
brand DESIGN.md files this direction is calibrated against>

## What to look at

- <the one move that makes this direction itself>

## If chosen

- <what carries into the real build: tokens, hero paradigm, section rhythm>
"""

DECISION_TEMPLATE = """\
# Decision — {date}

**Chosen:** `{slug}`

## Why

- <the user's words, not a paraphrase>

## Carried over from other directions

- <anything to merge in, or "nothing">

## Handoff

- [ ] Foundation applied (design_system_management / brandkit.py)
- [ ] Mockup kept as reference; real pages built as data (site_generator)
"""


def project_dir(name: str) -> Path:
    d = OUTPUTS / name
    if not d.is_dir():
        sys.exit(f"no such project: {d} (scaffold it first: new_site.py)")
    return d


def directions(croot: Path) -> list[Path]:
    return sorted(
        p.parent for p in croot.glob("*/index.html")
        if not p.parent.name.startswith(("_", "."))
    )


def notes_meta(ddir: Path) -> dict[str, str]:
    """Title (first # heading) and the **Key:** lines from NOTES.md."""
    meta = {"title": ddir.name.replace("-", " ").title()}
    notes = ddir / "NOTES.md"
    if notes.is_file():
        text = notes.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if m:
            meta["title"] = m.group(1).strip()
        for key in ("Design read", "Dials", "Foundation"):
            km = re.search(rf"\*\*{key}:\*\*\s*(.+)", text)
            if km:
                meta[key.lower().replace(" ", "_")] = km.group(1).strip()
    return meta


def chosen_slug(croot: Path) -> str | None:
    dec = croot / "DECISION.md"
    if dec.is_file():
        m = re.search(r"\*\*Chosen:\*\*\s*`?([\w-]+)`?",
                      dec.read_text(encoding="utf-8", errors="replace"))
        if m:
            return m.group(1)
    return None


def cmd_new(args: argparse.Namespace) -> None:
    croot = project_dir(args.project) / "concepts"
    ddir = croot / args.direction
    if ddir.exists() and not args.force:
        sys.exit(f"{ddir} exists (use --force to keep going)")
    ddir.mkdir(parents=True, exist_ok=True)
    title = args.title or args.direction.replace("-", " ").title()
    notes = ddir / "NOTES.md"
    if not notes.exists() or args.force:
        notes.write_text(
            NOTES_TEMPLATE.format(title=title, slug=args.direction),
            encoding="utf-8", newline="\n")
    print(f"scaffolded {ddir}")
    print(f"author the mockup at {ddir / 'index.html'} "
          "(single file, inline CSS, no engine deps), fill NOTES.md, "
          "then run: concepts.py compare " + args.project)


def cmd_compare(args: argparse.Namespace) -> None:
    croot = project_dir(args.project) / "concepts"
    dirs = directions(croot)
    if not dirs:
        sys.exit(f"no directions with an index.html under {croot}")
    picked = chosen_slug(croot)
    cards = []
    for d in dirs:
        meta = notes_meta(d)
        badge = ('<span class="badge chosen">chosen</span>'
                 if d.name == picked else "")
        sub = " · ".join(
            html.escape(meta[k]) for k in ("dials", "foundation") if k in meta)
        cards.append(f"""\
  <figure class="card{' is-chosen' if d.name == picked else ''}">
    <figcaption>
      <strong>{html.escape(meta['title'])}</strong> {badge}
      <span class="sub">{sub}</span>
      <a href="{d.name}/index.html" target="_blank">open full ↗</a>
    </figcaption>
    <div class="stage"><iframe src="{d.name}/index.html" loading="lazy"
      title="{html.escape(meta['title'])}"></iframe></div>
  </figure>""")
    n = len(dirs)
    state = (f"Direction chosen: <strong>{html.escape(picked)}</strong>"
             if picked else f"{n} direction{'s'[:n != 1]}, no decision yet")
    page = COMPARE_SHELL.format(
        project=html.escape(args.project), state=state, cards="\n".join(cards))
    out = croot / "compare.html"
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {out} ({n} directions"
          + (f", chosen: {picked})" if picked else ", no decision yet)"))


def cmd_decide(args: argparse.Namespace) -> None:
    croot = project_dir(args.project) / "concepts"
    if not (croot / args.direction / "index.html").is_file():
        sys.exit(f"no such direction: {croot / args.direction}")
    dec = croot / "DECISION.md"
    if dec.exists() and not args.force:
        sys.exit(f"{dec} exists (use --force to overwrite)")
    dec.write_text(
        DECISION_TEMPLATE.format(slug=args.direction, date=date.today()),
        encoding="utf-8", newline="\n")
    print(f"wrote {dec} - fill in the user's why, then re-run compare")


def cmd_list(args: argparse.Namespace) -> None:
    croot = project_dir(args.project) / "concepts"
    picked = chosen_slug(croot)
    for d in directions(croot):
        meta = notes_meta(d)
        # ASCII on purpose: a cp1252 console (Windows default) dies on ●/○.
        mark = "[x]" if d.name == picked else "[ ]"
        print(f"{mark} {d.name}: {meta['title']}"
              + (f"  [{meta['dials']}]" if "dials" in meta else ""))
    if not directions(croot):
        print(f"(no directions under {croot})")


# The compare page is self-contained: works opened from disk, and through the
# hub's /art/<project>/concepts/compare.html static route. Width toggle scales
# every iframe to preview phone/tablet/laptop/desktop composition.
COMPARE_SHELL = """\
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Concepts — {project}</title>
<style>
  :root {{ --bg:#101114; --panel:#1a1c20; --ink:#e8e9eb; --sub:#9aa0a8;
          --line:#2a2d33; --ok:#3fb96b; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
         font:14px/1.5 system-ui, sans-serif; }}
  header {{ display:flex; gap:16px; align-items:center; padding:14px 20px;
           border-bottom:1px solid var(--line); position:sticky; top:0;
           background:var(--bg); z-index:2; flex-wrap:wrap; }}
  header h1 {{ font-size:15px; margin:0; }}
  header .state {{ color:var(--sub); }}
  .widths {{ margin-left:auto; display:flex; gap:6px; }}
  .widths button {{ background:var(--panel); color:var(--ink);
    border:1px solid var(--line); border-radius:8px; padding:5px 12px;
    cursor:pointer; }}
  .widths button.on {{ border-color:var(--ok); color:var(--ok); }}
  main {{ display:grid; gap:20px; padding:20px;
         grid-template-columns:repeat(auto-fit, minmax(420px, 1fr)); }}
  .card {{ margin:0; background:var(--panel); border:1px solid var(--line);
          border-radius:12px; overflow:hidden; }}
  .card.is-chosen {{ border-color:var(--ok); }}
  figcaption {{ display:flex; gap:10px; align-items:baseline; padding:10px 14px;
               flex-wrap:wrap; }}
  figcaption .sub {{ color:var(--sub); font-size:12px; }}
  figcaption a {{ color:var(--ink); margin-left:auto; font-size:12px; }}
  .badge.chosen {{ color:var(--ok); border:1px solid var(--ok);
    border-radius:99px; padding:1px 8px; font-size:11px; }}
  .stage {{ height:560px; overflow:hidden; background:#fff;
           border-top:1px solid var(--line); }}
  .stage iframe {{ border:0; width:1440px; height:2000px;
    transform-origin:0 0; }}
</style>
<header>
  <h1>Concepts — {project}</h1>
  <span class="state">{state}</span>
  <div class="widths">
    <button data-w="390">phone</button>
    <button data-w="768">tablet</button>
    <button data-w="1040">laptop</button>
    <button data-w="1440" class="on">desktop</button>
  </div>
</header>
<main>
{cards}
</main>
<script>
  var W = 1440;
  function fit() {{
    document.querySelectorAll('.stage').forEach(function (s) {{
      var f = s.querySelector('iframe'), k = s.clientWidth / W;
      f.style.width = W + 'px';
      f.style.height = (s.clientHeight / k) + 'px';
      f.style.transform = 'scale(' + k + ')';
    }});
  }}
  document.querySelectorAll('.widths button').forEach(function (b) {{
    b.onclick = function () {{
      W = +b.dataset.w;
      document.querySelectorAll('.widths button').forEach(function (x) {{
        x.classList.toggle('on', x === b);
      }});
      fit();
    }};
  }});
  addEventListener('resize', fit);
  fit();
</script>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new", help="scaffold a direction folder")
    p.add_argument("project")
    p.add_argument("direction")
    p.add_argument("--title")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_new)
    p = sub.add_parser("compare", help="(re)write concepts/compare.html")
    p.add_argument("project")
    p.set_defaults(fn=cmd_compare)
    p = sub.add_parser("decide", help="record the chosen direction")
    p.add_argument("project")
    p.add_argument("direction")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_decide)
    p = sub.add_parser("list", help="list directions and state")
    p.add_argument("project")
    p.set_defaults(fn=cmd_list)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
