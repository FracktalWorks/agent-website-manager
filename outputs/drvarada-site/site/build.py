#!/usr/bin/env python
"""Assemble drvarada.com from content data + the design system.

    python build.py                     # preview build (flat hrefs) -> dist/
    python build.py --links=production  # WordPress build (real URLs) -> dist-prod/

Validation is not optional and runs on every build. A site of forty pages fails in
ways nobody notices by eye: a link to a slug that was renamed, a page that quietly
asks for two dark bands, a title tag that Google will truncate, a superlative that
breaches NMC advertising rules. All of those are caught here and abort the build.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import chrome                                    # noqa: E402
from content.urls import URLS                    # noqa: E402

chrome.URLS = URLS

from content import (brand, hyderabad_medical, hyderabad_skin,   # noqa: E402
                     languages, psoriasis, vitiligo)

PAGES = (brand.PAGES + vitiligo.PAGES + psoriasis.PAGES
         + hyderabad_medical.PAGES + hyderabad_skin.PAGES + languages.PAGES)

# each page remembers which content module authored it — the site manifest uses
# this to point future sessions (and the live editor) straight at the copy
for _mod in (brand, vitiligo, psoriasis, hyderabad_medical, hyderabad_skin,
             languages):
    for _p in _mod.PAGES:
        _p["__module__"] = _mod.__name__.rsplit(".", 1)[-1]

# hreflang runs both ways: the English hubs must point at their language siblings,
# and declaring it here (rather than inside vitiligo.py) keeps the language layer
# removable without touching the English content.
_HUB_LANGS = {
    "vitiligo": [("en", "vitiligo"), ("te-IN", "te-vitiligo"),
                 ("hi-IN", "hi-vitiligo")],
    "psoriasis": [("en", "psoriasis"), ("te-IN", "te-psoriasis"),
                  ("hi-IN", "hi-psoriasis")],
}
for _p in PAGES:
    if _p["slug"] in _HUB_LANGS:
        _p.setdefault("langs", _HUB_LANGS[_p["slug"]])

# Design system assets. The site consumes the published kit rather than re-declaring
# tokens — if a colour is wrong, it is wrong in the design system.
DS = ROOT.parent / "design-system"
LANDING = ROOT.parent / "pages" / "landing" / "assets"

# NMC / Indian Medical Council advertising ethics. These are claims a medical practice
# may not make, and they are also claims that damage trust — so the build refuses them.
BANNED = [
    (r"\bbest\s+(dermatolog|skin|hair|clinic|doctor|treatment)", "superlative claim"),
    (r"\bno\.?\s*1\b", "ranking claim"),
    (r"\bworld[- ]class\b", "superlative claim"),
    (r"\bguarantee[ds]?\b", "outcome guarantee"),
    (r"\b100%\s*(result|success|cure|safe)", "absolute claim"),
    (r"\bpermanent(ly)?\s+cure", "cure claim"),
    (r"\bmiracle\b", "unsubstantiated claim"),
    (r"\bcures?\s+(vitiligo|psoriasis|eczema|alopecia)", "cure claim"),
    (r"\bpainless\b", "absolute claim"),
    (r"\bside[- ]effect[- ]free\b", "absolute claim"),
]
# A banned word inside a negation is usually the *compliant* statement — "no treatment
# cures vitiligo" is exactly what these pages are supposed to say. So the linter looks
# at a window either side of the match for a negation or a disclaimer cue before
# raising. This is far more robust than maintaining a list of allowed phrasings, which
# grows forever and silently stops matching when copy is edited.
NEGATION = re.compile(
    r"\b(no|not|never|none|nothing|cannot|can't|isn't|aren't|don't|doesn't|without|"
    r"neither|nor|any clinic|anyone|overstat\w+|myth|folklore|unfounded|distrust|"
    r"unsupported|claim\w* it cannot|promis\w+|misleading|worth distrusting)\b"
)

# Quality gates ported from Open Design's artifact linter (lint-artifact.ts) and
# taste-skill layout discipline. Unlike the NMC rules these are design-integrity
# rules: they catch the reflexes generated copy and CSS drift toward.
AI_DEFAULT_ACCENTS = ["#6366f1", "#4f46e5", "#4338ca", "#3730a3",
                      "#8b5cf6", "#7c3aed", "#a855f7"]        # canonical LLM indigos
SLOP = [
    (r"\blorem ipsum\b", "filler copy"),
    (r"\bplaceholder text\b|\bsample content\b|\bfeature (one|two|three)\b",
     "filler copy"),
    (r"\b\d+[×x]\s*(faster|better|more)\b", "invented metric"),
    (r"\b99\.9%|zero[- ]downtime\b", "invented metric"),
]
RAW_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")


# Text colour / background pairings that actually occur, with the rendered size
# and weight. Maintained by hand because only a browser could infer it, and a
# wrong pairing here is worse than none — see PAIRS entries as claims to verify.
CONTRAST_PAIRS = [
    ("body copy", "--ink-2", "--ground", 16, 400),
    ("body copy on cards", "--ink-2", "--paper", 15, 400),
    ("body copy on tint", "--ink-2", "--tint", 16, 400),
    ("eyebrow / table head", "--ink-3", "--ground", 12, 600),
    ("eyebrow on cards", "--ink-3", "--paper", 12, 600),
    ("eyebrow on tint", "--ink-3", "--tint", 12, 600),
    ("headings", "--ink", "--ground", 32, 700),
    ("footer headings", "--on-dark-3", "--dark", 11.5, 600),
    ("accent text on soft mint", "--mint-dp", "--mint-sf", 15, 500),
    ("accent text on soft apricot", "--apr-dp", "--apr-sf", 15, 500),
    ("accent text on soft lilac", "--lil-dp", "--lil-sf", 15, 500),
]


def _luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    parts = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    parts = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
             for c in parts]
    return 0.2126 * parts[0] + 0.7152 * parts[1] + 0.0722 * parts[2]


def lint_contrast() -> list[str]:
    """WCAG 2.1 AA contrast on the pairings the site actually renders.

    This exists because a design system can be internally consistent and still
    illegible: `--ink-3` shipped at 3.36:1 on every page as the colour of every
    section kicker and every table header, which is a Level AA failure on the
    most-repeated text style on the site. Nothing caught it — the token was used
    exactly as intended, and the intent was wrong.
    """
    tokens: dict[str, str] = {}
    for f in (DS / "kit" / "colors_and_type.css",
              LANDING / "design-system.css",
              ROOT / "assets" / "site.css"):
        if not f.exists():
            continue
        root = re.search(r":root\s*\{(.*?)\}", f.read_text(encoding="utf-8"), re.S)
        if root:
            for m in re.finditer(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;",
                                 root.group(1)):
                tokens.setdefault(m.group(1), m.group(2))

    errors = []
    for label, fg, bg, size, weight in CONTRAST_PAIRS:
        if fg not in tokens or bg not in tokens:
            continue                     # token renamed; the token lint covers it
        lf, lb = _luminance(tokens[fg]), _luminance(tokens[bg])
        ratio = (max(lf, lb) + 0.05) / (min(lf, lb) + 0.05)
        large = size >= 24 or (size >= 18.66 and weight >= 700)
        need = 3.0 if large else 4.5
        if ratio < need:
            errors.append(
                f"contrast: {label} — {fg} ({tokens[fg]}) on {bg} ({tokens[bg]}) "
                f"is {ratio:.2f}:1, needs {need} at {size}px/{weight}")
    return errors


def lint_images(page: dict) -> list[str]:
    """Every image must be findable, described, and — if clinical — consented.

    The consent rule is the important one. A before/after photograph of a
    patient may only be published with written consent (NMC ethics, and simple
    decency), so the data model carries a consent record and the build refuses
    the image without it. That makes the safeguard structural: someone dropping
    a photo into the live editor cannot skip it, because the page will not build.
    """
    errors: list[str] = []
    slug = page["slug"]

    def check(im, where: str, clinical: bool = False):
        if not isinstance(im, dict):
            errors.append(f"{slug}: {where} is not an image dict")
            return
        if not im.get("src"):
            errors.append(f"{slug}: {where} has no src")
        elif not (ROOT / "assets" / im["src"]).exists():
            errors.append(f"{slug}: {where} → assets/{im['src']} is missing")
        alt = (im.get("alt") or "").strip()
        if len(alt) < 8:
            errors.append(f"{slug}: {where} needs real alt text "
                          "(screen readers and image search both read it)")
        if clinical and not (im.get("consent") or "").strip():
            errors.append(f"{slug}: {where} is a patient photograph with no "
                          "consent record — add consent: '<how and when it was "
                          "obtained>' or remove the image")

    if page.get("photo"):
        check(page["photo"], "photo")
    for i, sec in enumerate(page["sections"]):
        if sec.get("image"):
            check(sec["image"], f"sections.{i}.image")
        if sec["kind"] == "ba":
            for n, item in enumerate(sec["items"]):
                if not isinstance(item, dict):
                    continue
                for side in ("before", "after"):
                    if item.get(side):
                        check(item[side], f"sections.{i}.items.{n}.{side}",
                              clinical=True)
    return errors


def lint_css(path: Path) -> list[str]:
    """Raw colour values are legal only inside :root token blocks.

    site.css declares itself layout-only; this makes that self-description
    enforceable instead of aspirational. Token-scope awareness is what keeps
    the rule trustworthy — a hex in the token layer is a declaration, a hex in
    a component rule is drift.
    """
    css = re.sub(r"/\*.*?\*/", " ", path.read_text(encoding="utf-8"), flags=re.S)
    errors = []
    for hex_ in AI_DEFAULT_ACCENTS:
        if hex_ in css.lower():
            errors.append(f"{path.name}: AI-default accent {hex_} — pick from the "
                          "design system instead")
    body = re.sub(r":root\s*\{[^}]*\}", " ", css)
    for m in RAW_COLOR.finditer(body):
        snippet = " ".join(body[max(0, m.start() - 40):m.end() + 20].split())
        errors.append(f"{path.name}: raw colour outside :root tokens — …{snippet}…")
    return errors


def compliant(body: str, start: int, end: int) -> bool:
    """True when the flagged phrase sits inside a negation or a debunking."""
    return bool(NEGATION.search(body[max(0, start - 70):end + 70]))


def text_of(page: dict) -> str:
    """Flatten every string in a page so the linter sees all copy, not just the HTML."""
    out: list[str] = []

    def walk(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)

    walk(page)
    return " ".join(out)


def validate(pages: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    slugs = {p["slug"] for p in pages}

    missing = set(URLS) - slugs
    extra = slugs - set(URLS)
    if missing:
        errors.append(f"URLS has slugs with no page: {sorted(missing)}")
    if extra:
        errors.append(f"pages with no URL entry: {sorted(extra)}")
    if len(slugs) != len(pages):
        errors.append("duplicate slug")

    known = slugs | {"#book", "#faq"}
    for p in pages:
        s = p["slug"]

        for field in ("title", "meta", "h1", "lede", "template"):
            if not p.get(field):
                errors.append(f"{s}: missing {field}")
        if len(p.get("title", "")) > 60:
            warnings.append(
                f"{s}: title {len(p['title'])} chars — may truncate in results")
        if not 110 <= len(p.get("meta", "")) <= 320:
            errors.append(f"{s}: meta description {len(p.get('meta',''))} chars")
        if not p.get("faqs"):
            errors.append(f"{s}: no FAQ block — every page needs FAQPage schema")
        if not p.get("related"):
            errors.append(f"{s}: no related links — orphan risk")

        # internal links must resolve
        links = [l for _, l in p.get("acts", [])]
        links += [slug for slug, _, _ in p.get("related", [])]
        for sec in p["sections"]:
            if sec.get("cta"):
                links.append(sec["cta"][1])
            if sec["kind"] == "chips":
                links += [x[1] for x in sec["items"]]
            if sec["kind"] == "pillars":
                for it in sec["items"]:
                    links += [entry[1] for entry in it["list"]]
                    links.append(it["go"][1])
        for link in links:
            if link.startswith(("http", "tel:", "mailto:")):
                continue
            if link not in known:
                errors.append(f"{s}: link to unknown slug '{link}'")

        # band rhythm — the design system allows one dark section per page
        try:
            chrome.assign_surfaces([x for x in p["sections"]
                                    if x["kind"] not in ("callout", "quote")])
        except ValueError as exc:
            errors.append(f"{s}: {exc}")

        # advertising compliance
        body = re.sub(r"<[^>]+>", " ", text_of(p).lower())
        for pattern, why in BANNED:
            for m in re.finditer(pattern, body):
                if compliant(body, m.start(), m.end()):
                    continue
                ctx = " ".join(body[max(0, m.start() - 50):m.end() + 50].split())
                errors.append(f"{s}: {why} — …{ctx}…")

        errors.extend(lint_images(p))

        # slop — filler copy and unattributable metrics never ship
        for pattern, why in SLOP:
            for m in re.finditer(pattern, body):
                ctx = " ".join(body[max(0, m.start() - 40):m.end() + 40].split())
                errors.append(f"{s}: {why} — …{ctx}…")

        # layout rhythm: three of the same section kind in a row reads as a
        # template, not a page (taste-skill zigzag cap)
        kinds = [x["kind"] for x in p["sections"]]
        run = 1
        for a, b in zip(kinds, kinds[1:]):
            run = run + 1 if a == b else 1
            if run == 3:
                warnings.append(f"{s}: three consecutive '{b}' sections — vary "
                                "the layout")
                break

    errors.extend(lint_css(ROOT / "assets" / "site.css"))
    errors.extend(lint_contrast())
    return errors, warnings


def copy_assets(out: Path) -> int:
    assets = out / "assets"
    (assets / "logos").mkdir(parents=True, exist_ok=True)
    n = 0

    for src, dst in [(DS / "kit" / "colors_and_type.css", assets / "design-system.css"),
                     (LANDING / "design-system.css", assets / "design-system.css")]:
        if src.exists() and not (assets / "design-system.css").exists():
            shutil.copy(src, dst)
            n += 1
    shutil.copy(ROOT / "assets" / "site.css", assets / "site.css")
    n += 1

    for name in ("favicon.svg", "logo-horizontal-light.svg",
                 "logo-horizontal-tagline-dark.svg"):
        for base in (LANDING / "logos", DS / "logos"):
            if (base / name).exists():
                shutil.copy(base / name, assets / "logos" / name)
                n += 1
                break

    # photography supplied through the live editor (or dropped in by hand)
    img_src = ROOT / "assets" / "img"
    if img_src.is_dir():
        shutil.copytree(img_src, assets / "img", dirs_exist_ok=True)
        n += len(list(img_src.glob("*")))
    return n


def sitemap(pages: list[dict]) -> str:
    """sitemap.xml with hreflang alternates — GSC picks language targeting from here."""
    rows = []
    for p in pages:
        url = chrome.SITE + URLS[p["slug"]]
        alts = ""
        if p.get("langs"):
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{lang}" '
                f'href="{chrome.SITE}{URLS[slug]}"/>'
                for lang, slug in p["langs"])
        pri = "1.0" if p["slug"] == "index" else (
            "0.9" if p["template"] in ("T1", "T2") and "-" not in p["slug"][:3]
            else "0.8" if p["template"] in ("T1", "T2") else "0.5")
        rows.append(f"  <url>\n    <loc>{url}</loc>{alts}\n"
                    f"    <priority>{pri}</priority>\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def main() -> int:
    links = "production" if "--links=production" in sys.argv else "preview"
    out = ROOT / ("dist-prod" if links == "production" else "dist")

    errors, warnings = validate(PAGES)
    if errors:
        print(f"BUILD FAILED — {len(errors)} problem(s):\n")
        for e in errors:
            print("  ·", e)
        return 1
    for w in warnings:
        print("  warn:", w)

    # Windows: a concurrent reader (the live-editor server mid-request, an
    # antivirus scan) briefly locks files and rmtree dies with WinError 5.
    # A short retry outlasts any of those handles.
    for attempt in range(4):
        try:
            if out.exists():
                shutil.rmtree(out)
            out.mkdir(parents=True)
            break
        except PermissionError:
            if attempt == 3:
                raise
            time.sleep(0.5)

    total = 0
    for page in PAGES:
        name = "index.html" if page["slug"] == "index" else f"{page['slug']}.html"
        html = chrome.render(page, links)
        (out / name).write_text(html, encoding="utf-8")
        total += len(html)

    # Machine-readable site index (Open Design's design-manifest idea): an agent
    # starting a later session reads this instead of re-deriving the IA by
    # globbing, and the per-page module pointer says where the copy lives.
    manifest = {
        "schema": "drvarada-site-manifest/v1",
        "site": chrome.SITE,
        "entry": "index.html",
        "pages": [{
            "slug": p["slug"],
            "file": ("index.html" if p["slug"] == "index"
                     else f"{p['slug']}.html"),
            "url": URLS[p["slug"]],
            "template": p["template"],
            "title": p["title"],
            "module": f"content/{p['__module__']}.py",
        } for p in PAGES],
        "rules": [
            "Practo is the only booking path; phone/WhatsApp sit below it.",
            "No cure claims, superlatives or guarantees (NMC) — build enforces.",
            "One page owns one query cluster; hubs never carry a city.",
            "Max one dark band per page body.",
        ],
    }
    (out / "site-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    (out / "sitemap.xml").write_text(sitemap(PAGES), encoding="utf-8")
    (out / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {chrome.SITE}/sitemap.xml\n", encoding="utf-8")
    n_assets = copy_assets(out)

    by_template: dict[str, int] = {}
    for p in PAGES:
        by_template[p["template"]] = by_template.get(p["template"], 0) + 1

    print(f"built {len(PAGES)} pages -> {out.name}/  ({links} links)")
    for t in sorted(by_template):
        print(f"  {t}: {by_template[t]} pages")
    print(f"  assets: {n_assets}")
    print(f"  average page: {total // len(PAGES) // 1024} KB")

    todos = sum(text_of(p).count("TODO") for p in PAGES)
    print(f"  outstanding TODO markers (clinic to supply): {todos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
