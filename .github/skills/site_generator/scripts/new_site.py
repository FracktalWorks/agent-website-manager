"""Scaffold a new site that builds, verifies and opens in the live editor.

WHY THIS EXISTS
  Until 2026-07-30, "start another site" meant copying `outputs/drvarada-site/`
  and deleting a clinic. That works exactly once, and it silently carries a
  Hyderabad dermatologist's navigation, schema and validator rules into whatever
  you build next. It was also the last thing anyone might have started Open
  Design for.

  So: the engine is copied verbatim (it is genuinely site-agnostic), and the
  three files that are NOT — `siteconf.py`, `chrome.py`, `content/` — are
  generated fresh and minimal. The result builds on the first run. That is the
  contract this script is worth having only if it keeps:

      python .github/skills/site_generator/scripts/new_site.py acme
      cd outputs/acme-site/site && python build.py && python verify.py --all

Usage:
    new_site.py <name> [--title "Acme Ltd"] [--url https://acme.com]
                       [--from outputs/drvarada-site/site] [--force]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]

# Site-agnostic. These are copied byte-for-byte; if one of them ever needs a
# project-specific edit, that is a bug in the module, not a reason to fork it.
ENGINE = ("versions.py", "datapatch.py", "resolver.py", "linkscan.py",
          "verify.py", "media.py", "preview.py", "editor.py", "brandkit.py")
ENGINE_DIRS = ("editor",)

SITECONF = '''"""What this particular site is made of.

Declared once and read by build.py, linkscan.py and editor.py. Adding a content
module means adding it here and nowhere else.
"""

from __future__ import annotations

MODULES = ("pages",)

EDITABLE_CONSTANTS = ("PHONE", "PHONE_SHOW", "EMAIL", "ADDRESS", "HOURS")
EDITABLE_URLS = ("PHONE", "EMAIL")
LINK_CONSTANTS = ("PHONE", "EMAIL")
'''

CHROME = '''"""Shared chrome and block renderers for {title}.

Every page is data (see `content/`); this module is the only place that emits
HTML. That split is deliberate: copy changes never touch markup, and a markup
fix lands on every page at once.

This is the starter chrome. Grow it by adding block renderers to BLOCKS — the
key is the `kind` a section declares. Whatever you add, keep emitting `at(...)`
addresses: they are what lets the live editor name the exact value behind a
piece of rendered markup, and a block without them can be looked at but not
edited.
"""

from __future__ import annotations

import re

SITE = "{url}"
BRAND = "{title}"
BRAND_PLAIN = "{title}"

PHONE = "tel:+910000000000"
PHONE_SHOW = "+91 00000 00000"
EMAIL = "mailto:hello@example.com"
ADDRESS = "TODO — street address"
HOURS = "TODO — opening hours"

NAV = [
    ("Home", "index", None),
]

FOOTER = [
    ("Site", [("Home", "index")]),
]

URLS: dict[str, str] = {{}}


def e(s: str) -> str:
    """Escape text from content data, leaving deliberate entities alone."""
    return re.sub(r"&(?!#?\\w+;)", "&amp;", s)


def href(slug: str, links: str = "preview") -> str:
    if slug.startswith(("http", "tel:", "mailto:", "#")):
        return slug
    if links == "production":
        return URLS.get(slug, "/")
    return "index.html" if slug == "index" else f"{{slug}}.html"


def asset(path: str, links: str) -> str:
    return f"assets/{{path}}" if links == "preview" else f"/assets/{{path}}"


def at(address: str, links: str, kind: str = "od") -> str:
    """The live editor's data address for a value — preview builds only.

    Production HTML carries none of this. An address is an editing affordance,
    not content, and shipping it would leak the source layout to every visitor.
    """
    return f' data-{{kind}}="{{address}}"' if links == "preview" else ""


def _head(s: dict, links: str, a: str) -> str:
    out = ""
    if s.get("eyebrow"):
        out += f'<div class="eyebrow"{{at(f"{{a}}.eyebrow", links)}}>{{e(s["eyebrow"])}}</div>'
    if s.get("h2"):
        out += f'<h2{{at(f"{{a}}.h2", links)}}>{{e(s["h2"])}}</h2>'
    return f'<div class="head-block">{{out}}</div>' if out else ""


def blk_prose(s, links, a=""):
    body = "".join(
        f'<p{{at(f"{{a}}.body.{{i}}", links)}}>{{e(p)}}</p>'
        for i, p in enumerate(s.get("body") or []))
    return _head(s, links, a) + f'<div class="prose">{{body}}</div>'


def blk_cards(s, links, a=""):
    cards = []
    for i, it in enumerate(s.get("items") or []):
        rows = "".join(
            f'<li{{at(f"{{a}}.items.{{i}}.list.{{j}}", links)}}>{{e(r)}}</li>'
            for j, r in enumerate(it.get("list") or []))
        cards.append(
            f'<div class="card">'
            f'<h3{{at(f"{{a}}.items.{{i}}.title", links)}}>{{e(it.get("title", ""))}}</h3>'
            f'<p{{at(f"{{a}}.items.{{i}}.body", links)}}>{{e(it.get("body", ""))}}</p>'
            f'<ul>{{rows}}</ul></div>')
    return _head(s, links, a) + f'<div class="cols">{{"".join(cards)}}</div>'


BLOCKS = {{"prose": blk_prose, "cards": blk_cards}}


def header(links: str) -> str:
    items = "".join(
        f'<a href="{{href(slug, links)}}"{{at(f"chrome:NAV.{{i}}.1", links, "od-link")}}>'
        f'{{label}}</a>'
        for i, (label, slug, _panel) in enumerate(NAV))
    return f'<header class="head"><div class="wrap">' \\
           f'<a class="logo" href="{{href("index", links)}}">{{BRAND}}</a>' \\
           f'<nav aria-label="Main">{{items}}</nav></div></header>'


def footer(links: str) -> str:
    cols = []
    for i, (title, rows) in enumerate(FOOTER):
        links_html = "".join(
            f'<a href="{{href(s, links)}}"'
            f'{{at(f"chrome:FOOTER.{{i}}.1.{{j}}.1", links, "od-link")}}>{{l}}</a>'
            for j, (l, s) in enumerate(rows))
        cols.append(f"<div><h4>{{title}}</h4>{{links_html}}</div>")
    return f'<footer><div class="wrap"><div class="cols">{{"".join(cols)}}</div>' \\
           f'<div class="legal">© {{BRAND}}</div></div></footer>'


def render(page: dict, links: str = "preview") -> str:
    acts = "".join(
        f'<a class="btn" href="{{href(link, links)}}"'
        f'{{at(f"acts.{{n}}", links, "od-link")}}>{{e(label)}}</a>'
        for n, (label, link) in enumerate(page.get("acts") or []))
    sections = "".join(
        f'<section class="band">'
        f'<div class="wrap">{{BLOCKS[s["kind"]](s, links, f"sections.{{i}}")}}</div>'
        f'</section>'
        for i, s in enumerate(page.get("sections") or [])
        if s.get("kind") in BLOCKS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{page["title"]}}</title>
<meta name="description" content="{{page.get("meta", "")}}">
<link rel="canonical" href="{{SITE}}{{URLS.get(page["slug"], "/")}}">
<link rel="stylesheet" href="{{asset("site.css", links)}}">
</head>
<body>
{{header(links)}}
<main>
  <section class="band hero"><div class="wrap">
    <h1{{at("h1", links)}}>{{page["h1"]}}</h1>
    <p class="lede"{{at("lede", links)}}>{{e(page.get("lede", ""))}}</p>
    <div class="acts">{{acts}}</div>
  </div></section>
  {{sections}}
</main>
{{footer(links)}}
</body>
</html>"""
'''

PAGES = '''"""Page data for {title}. One dict per page; `chrome.py` turns them into HTML.

An address like `sections.0.body.1` in the rendered HTML points straight back
into this structure, which is how the live editor writes an edit to the right
line without guessing.
"""

from chrome import PHONE

PAGES = [
    {{
        "slug": "index",
        "title": "{title}",
        "meta": "TODO — 150 characters describing this page for search results.",
        "h1": "{title}",
        "lede": "Say what this site is for, in one sentence a stranger understands.",
        "acts": [("Get in touch", PHONE)],
        "sections": [
            {{"kind": "prose", "eyebrow": "About", "h2": "What we do",
             "body": ["Replace this paragraph.",
                      "And this one. Keep one idea per paragraph."]}},
            {{"kind": "cards", "eyebrow": "Services", "h2": "What you can ask for",
             "items": [
                 {{"title": "First thing", "body": "One sentence.",
                  "list": ["A detail", "Another detail"]}},
                 {{"title": "Second thing", "body": "One sentence.",
                  "list": ["A detail", "Another detail"]}},
             ]}},
        ],
    }},
]
'''

URLS_PY = '''"""slug → production URL.

The build writes flat files so a preview resolves without a server; this map is
the bridge to the real information architecture. Canonical tags and every schema
`@id` use these paths, and `build.py --links=production` rewrites internal hrefs
to them.
"""

URLS = {
    "index": "/",
}
'''

CSS = """/* Tokens first. Every colour in this file lives in :root and nowhere else —
   that rule is what lets brandkit.py restyle the whole site by rewriting one
   block, and what stops a hardcoded hex surviving a rebrand. */
:root {
  --bg: #ffffff;
  --fg: #14171a;
  --muted: #5b6570;
  --accent: #1f6feb;
  --line: #e4e8ec;
  --r: 12px;
  --wrap: 1080px;
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
       font: 16px/1.6 system-ui, sans-serif; }
.wrap { max-width: var(--wrap); margin: 0 auto; padding: 0 24px; }
.band { padding-block: 56px; }
.head { border-bottom: 1px solid var(--line); padding-block: 16px; }
.head .wrap { display: flex; gap: 24px; align-items: center;
              justify-content: space-between; }
.logo { font-weight: 700; text-decoration: none; color: var(--fg); }
nav a { margin-left: 20px; color: var(--muted); text-decoration: none; }
h1 { font-size: clamp(32px, 5vw, 52px); line-height: 1.1; margin: 0 0 16px; }
h2 { font-size: clamp(24px, 3vw, 34px); margin: 0 0 12px; }
.lede { font-size: 19px; color: var(--muted); max-width: 60ch; }
.eyebrow { text-transform: uppercase; letter-spacing: .08em; font-size: 12px;
           color: var(--muted); margin-bottom: 8px; }
.acts { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 24px; }
.btn { display: inline-block; padding: 12px 20px; border-radius: var(--r);
       background: var(--accent); color: #fff; text-decoration: none; }
.cols { display: grid; gap: 20px;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.card { border: 1px solid var(--line); border-radius: var(--r); padding: 20px; }
.card ul { padding-left: 18px; color: var(--muted); }
.prose p { max-width: 68ch; }
footer { border-top: 1px solid var(--line); padding-block: 40px; margin-top: 40px; }
footer a { display: block; color: var(--muted); text-decoration: none; }
.legal { margin-top: 24px; color: var(--muted); font-size: 14px; }
img { max-width: 100%; height: auto; }
"""

BUILD = '''"""Render every page to dist/. The only thing that writes HTML files.

    python build.py                  → dist/       (flat filenames, for preview)
    python build.py --links=production → dist-prod/ (real URLs, for deploy)

The validator runs first and refuses to write anything if a page is broken —
a link to a slug that does not exist, a missing title, a duplicate slug. A build
that fails loudly beats 40 pages with one dead link in the footer.
"""

from __future__ import annotations

import importlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import chrome                                    # noqa: E402
import siteconf                                  # noqa: E402
from content.urls import URLS                    # noqa: E402

chrome.URLS = URLS

_MODULES = [importlib.import_module(f"content.{n}") for n in siteconf.MODULES]
PAGES = [p for m in _MODULES for p in m.PAGES]
for _mod in _MODULES:
    for _p in _mod.PAGES:
        _p["__module__"] = _mod.__name__.rsplit(".", 1)[-1]


def text_of(page: dict) -> str:
    return json.dumps(page, ensure_ascii=False, default=str)


def validate(pages: list[dict]) -> tuple[list[str], list[str]]:
    errors, warnings, seen = [], [], set()
    slugs = {p["slug"] for p in pages}
    for p in pages:
        if p["slug"] in seen:
            errors.append(f"{p['slug']}: duplicate slug")
        seen.add(p["slug"])
        if p["slug"] not in URLS:
            errors.append(f"{p['slug']}: no entry in content/urls.py")
        for field in ("title", "h1"):
            if not p.get(field):
                errors.append(f"{p['slug']}: missing {field}")
        if len(p.get("title", "")) > 60:
            warnings.append(f"{p['slug']}: title {len(p['title'])} chars — may truncate")
        for _label, link in p.get("acts") or []:
            if not link.startswith(("http", "tel:", "mailto:", "#")) and link not in slugs:
                errors.append(f"{p['slug']}: link to unknown slug {link!r}")
    return errors, warnings


def sitemap(pages: list[dict]) -> str:
    urls = "".join(f"  <url><loc>{chrome.SITE}{URLS[p['slug']]}</loc></url>\\n"
                   for p in pages)
    return ('<?xml version="1.0" encoding="UTF-8"?>\\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
            f"{urls}</urlset>\\n")


def main() -> int:
    links = "production" if "--links=production" in sys.argv else "preview"
    out = ROOT / ("dist-prod" if links == "production" else "dist")

    errors, warnings = validate(PAGES)
    if errors:
        print(f"BUILD FAILED — {len(errors)} problem(s):\\n")
        for err in errors:
            print("  ·", err)
        return 1
    for w in warnings:
        print("  warn:", w)

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for page in PAGES:
        name = "index.html" if page["slug"] == "index" else f"{page['slug']}.html"
        (out / name).write_text(chrome.render(page, links), encoding="utf-8")

    (out / "sitemap.xml").write_text(sitemap(PAGES), encoding="utf-8")
    (out / "robots.txt").write_text(
        f"User-agent: *\\nAllow: /\\n\\nSitemap: {chrome.SITE}/sitemap.xml\\n",
        encoding="utf-8")
    assets = out / "assets"
    assets.mkdir()
    for f in (ROOT / "assets").glob("*"):
        if f.is_file():
            shutil.copy2(f, assets / f.name)

    (out / "site-manifest.json").write_text(json.dumps({
        "schema": "site-manifest/v1",
        "site": chrome.SITE,
        "entry": "index.html",
        "pages": [{"slug": p["slug"], "url": URLS[p["slug"]],
                   "title": p["title"], "module": f"content/{p['__module__']}.py"}
                  for p in PAGES],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"built {len(PAGES)} pages -> {out.name}/  ({links} links)")
    todos = sum(text_of(p).count("TODO") for p in PAGES)
    print(f"  outstanding TODO markers: {todos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

PORTING = """# {title} — what to do next

The site builds. Everything below is yours to replace.

    cd outputs/{name}-site/site
    python build.py            # renders dist/
    python verify.py --all     # proves it renders clean at four widths
    python editor.py           # http://127.0.0.1:8789 — edit the rendered page
    python linkscan.py audit   # every link, by destination

## In order

1. **`chrome.py` constants** — `SITE`, `BRAND`, `PHONE`, `EMAIL`, `ADDRESS`,
   `HOURS`. These end up on every page; the editor's site-details form writes
   them, so get the names right in `siteconf.py` at the same time.
2. **`content/urls.py`** — the real information architecture. One page owns one
   query cluster. If you are adding a second URL for a term already listed,
   merge instead.
3. **`content/pages.py`** — the copy. Split into several modules when it grows
   and list them in `siteconf.MODULES`; nothing else needs to know.
4. **`NAV` / `FOOTER` in `chrome.py`** — these carry more links than any single
   page, and `linkscan.py` addresses them as `chrome:NAV.0.1`.
5. **`assets/site.css`** — every colour lives in `:root` and nowhere else. That
   rule is what lets `brandkit.py apply <id>` restyle the whole site from the
   152-system corpus. Break it and a rebrand leaves hardcoded hexes behind.
6. **Block renderers** — add to `BLOCKS` in `chrome.py`. Emit `at(...)` addresses
   for every editable value or the block will be unreachable from the editor.

## The rules worth keeping

- **Read before write.** The editor snapshots the source, applies, rebuilds, and
  restores on failure. Do not add a write path that skips the rebuild.
- **Addresses are preview-only.** Production HTML carries no `data-od`.
- **Version history is append-only.** `python versions.py list` shows it;
  `restore <n>` writes a version back and appends it rather than rewinding.
"""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("name", help="short slug, e.g. acme")
    ap.add_argument("--title", help="brand name (default: the slug, titled)")
    ap.add_argument("--url", default=None, help="production origin")
    ap.add_argument("--from", dest="src", default="outputs/drvarada-site/site",
                    help="site to copy the engine from")
    ap.add_argument("--force", action="store_true", help="overwrite an existing site")
    args = ap.parse_args(argv)

    title = args.title or args.name.replace("-", " ").title()
    url = args.url or f"https://{args.name}.com"
    src = (REPO / args.src).resolve()
    dest = REPO / "outputs" / f"{args.name}-site"
    site = dest / "site"

    if not src.is_dir():
        raise SystemExit(f"no engine to copy from at {src}")
    if dest.exists() and not args.force:
        raise SystemExit(f"{dest} already exists — pass --force to overwrite")

    (site / "content").mkdir(parents=True, exist_ok=True)
    (site / "assets").mkdir(exist_ok=True)

    missing = [f for f in ENGINE if not (src / f).exists()]
    if missing:
        raise SystemExit(f"engine incomplete in {src}: {', '.join(missing)}")
    for f in ENGINE:
        shutil.copy2(src / f, site / f)
    for d in ENGINE_DIRS:
        if (src / d).is_dir():
            shutil.copytree(src / d, site / d, dirs_exist_ok=True)

    (site / "build.py").write_text(BUILD, encoding="utf-8")
    (site / "siteconf.py").write_text(SITECONF, encoding="utf-8")
    (site / "chrome.py").write_text(
        CHROME.format(title=title, url=url), encoding="utf-8")
    (site / "content" / "__init__.py").write_text("", encoding="utf-8")
    (site / "content" / "urls.py").write_text(URLS_PY, encoding="utf-8")
    (site / "content" / "pages.py").write_text(
        PAGES.format(title=title), encoding="utf-8")
    (site / "assets" / "site.css").write_text(CSS, encoding="utf-8")
    (dest / "PORTING.md").write_text(
        PORTING.format(title=title, name=args.name), encoding="utf-8")

    print(f"scaffolded {dest.relative_to(REPO)}")
    print(f"  engine   {len(ENGINE)} modules copied from {src.relative_to(REPO)}")
    print("  yours    chrome.py · siteconf.py · content/ · assets/site.css")
    print(f"\nnext:  cd {(site).relative_to(REPO)} && python build.py")
    print(f"       read {(dest / 'PORTING.md').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
