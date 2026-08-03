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

import hashlib
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
from sources import SOURCES as REFERENCES        # noqa: E402
from sources import unknown as unknown_sources   # noqa: E402

chrome.URLS = URLS

import importlib                                # noqa: E402

import siteconf                                  # noqa: E402

# Which modules hold pages is declared once, in siteconf.py, because the same
# list used to be repeated here, in linkscan.py and in editor.py — and a module
# missing from one of them failed quietly rather than loudly.
_MODULES = [importlib.import_module(f"content.{n}") for n in siteconf.MODULES]
PAGES = [p for m in _MODULES for p in m.PAGES]

# each page remembers which content module authored it — the site manifest uses
# this to point future sessions (and the live editor) straight at the copy
for _mod in _MODULES:
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

# A corpus design system may be driving the site instead of the hand-tuned kit
# (see brandkit.py). Its stylesheet redefines every token and therefore loads
# last, which also makes it the highest-precedence source for the contrast gate.
BRAND_CSS = ROOT / "assets" / "brand.css"
BRAND_STATE = ROOT / "assets" / "brand.json"
_BRAND_META = (json.loads(BRAND_STATE.read_text(encoding="utf-8"))
               if BRAND_STATE.exists() and BRAND_CSS.exists() else {})
ACTIVE_BRAND = _BRAND_META.get("brand")
PAGE_IS_DARK = bool(_BRAND_META.get("page_is_dark"))
chrome.BRAND_SYSTEM = ACTIVE_BRAND
if _BRAND_META.get("theme_color"):
    chrome.THEME_COLOR = _BRAND_META["theme_color"]

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
    ("primary button label", "--mint-on", "--mint", 15.5, 600),
    ("booking heading", "--booking-ink", "--mint", 32, 600),
    ("booking body", "--booking-ink-2", "--mint", 16, 400),
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
              ROOT / "assets" / "site.css",
              BRAND_CSS):
        if not f.exists():
            continue
        # Later files override earlier ones, matching the cascade the browser
        # sees. brand.css is last for exactly that reason — checking the kit's
        # values while the browser renders the brand's would gate the wrong site.
        override = f == BRAND_CSS
        for root in re.finditer(r":root\s*\{(.*?)\}", f.read_text(encoding="utf-8"), re.S):
            for m in re.finditer(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;",
                                 root.group(1)):
                if override or m.group(1) not in tokens:
                    tokens[m.group(1)] = m.group(2)

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


def _all_images(page: dict):
    """Every image dict on a page, wherever it hangs.

    Kept separate from `lint_images` because that function reports *where* a
    problem is and therefore has to walk with addresses; this one only needs to
    know an image exists. A check that quietly missed a whole class of image —
    plates in a prose aside, say — would be worse than no check, so both walks
    live next to each other and gain new slots together.
    """
    if page.get("photo"):
        yield page["photo"]
    for sec in page.get("sections") or []:
        if sec.get("image"):
            yield sec["image"]
        for item in (sec.get("aside") or {}).get("items") or []:
            if not isinstance(item, dict):
                continue
            for slot in ("photo", "mark"):
                if item.get(slot):
                    yield item[slot]
        if sec.get("kind") == "ba":
            for item in sec["items"]:
                if not isinstance(item, dict):
                    continue
                for side in ("before", "after"):
                    if item.get(side):
                        yield item[side]
                for shot in item.get("shots") or []:
                    if isinstance(shot, dict):
                        yield shot


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
        # A credential emblem is not clinical, so it needs no consent — but it
        # still needs alt text and it still has to exist.
        for n, item in enumerate((sec.get("aside") or {}).get("items") or []):
            if not isinstance(item, dict):
                continue
            for slot in ("photo", "mark"):
                if item.get(slot):
                    check(item[slot], f"sections.{i}.aside.items.{n}.{slot}")
        if sec["kind"] == "ba":
            for n, item in enumerate(sec["items"]):
                if not isinstance(item, dict):
                    continue
                # A patient signs one publication consent for their case, not
                # one per photograph, so a `consent` on the case covers every
                # frame in it. A shot may still carry its own — a case built up
                # from separate visits can legitimately have separate consents,
                # and the narrower record should win when it exists.
                case_consent = (item.get("consent") or "").strip()
                shots = [(f"{side}", item[side]) for side in ("before", "after")
                         if item.get(side)]
                shots += [(f"shots.{k}", shot)
                          for k, shot in enumerate(item.get("shots") or [])
                          if isinstance(shot, dict)]
                for where, shot in shots:
                    if case_consent and not (shot.get("consent") or "").strip():
                        shot = {**shot, "consent": case_consent}
                    check(shot, f"sections.{i}.items.{n}.{where}", clinical=True)
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
        # 110-320 is what a description may be; 165 is what Google will SHOW.
        # Past that the tail is truncated, so a description that ends on its
        # point loses the point. It stays a warning rather than an error because
        # length is a display matter, not a ranking one — but a silent overrun
        # is how 41 pages ended up shipping snippets that cut off mid-sentence.
        if not 110 <= len(p.get("meta", "")) <= 320:
            errors.append(f"{s}: meta description {len(p.get('meta',''))} chars")
        elif len(p["meta"]) > 165:
            warnings.append(
                f"{s}: meta description {len(p['meta'])} chars — Google shows "
                "about 160, the rest is truncated")
        # A reference that does not resolve is worse than no reference at all —
        # it is a checkable claim that fails when checked. The library is the
        # only place a URL may be written, and every id must exist in it, so a
        # typo stops the build instead of shipping a dead citation.
        for bad_id in unknown_sources(p.get("sources", [])):
            errors.append(f"{s}: unknown source id {bad_id!r} — add it to sources.py")

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


def stamp_asset_hashes(root: Path) -> None:
    """Give every asset a `?v=` derived from its own bytes.

    Keyed by the same path `chrome.asset()` is called with, so the stylesheet a
    browser fetches and the file on disk can never disagree. Called against the
    assembled output directory, not the source tree — see the ordering note at
    the call site.
    """
    chrome.ASSET_HASH.clear()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            chrome.ASSET_HASH[p.relative_to(root).as_posix()] = hashlib.sha256(
                p.read_bytes()).hexdigest()[:10]


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

    if ACTIVE_BRAND:
        shutil.copy(BRAND_CSS, assets / "brand.css")
        n += 1
        fonts = ROOT / "assets" / "fonts"
        if fonts.is_dir():
            shutil.copytree(fonts, assets / "fonts", dirs_exist_ok=True)
            n += len(list(fonts.rglob("*.woff2")))

    # The logo is a brand asset — it belongs to the clinic and no token can
    # derive it. What CAN be derived is which cut of it stays legible: the navy
    # lockup disappears on a dark brand's near-black page. So the markup asks
    # for a stable alias and the readable variant is copied in behind it.
    # (Suffix convention: "-light" is drawn FOR a light background, "-dark" for
    # a dark one — the opposite of how it first reads.)
    header_cut = ("logo-horizontal-dark.svg" if PAGE_IS_DARK
                  else "logo-horizontal-light.svg")
    for alias, source in (("favicon.svg", "favicon.svg"),
                          ("logo-header.svg", header_cut),
                          # the footer band is dark under every brand
                          ("logo-footer.svg", "logo-horizontal-tagline-dark.svg")):
        for base in (LANDING / "logos", DS / "logos", DS / "kit" / "logos"):
            if (base / source).exists():
                shutil.copy(base / source, assets / "logos" / alias)
                n += 1
                break
        else:
            raise FileNotFoundError(
                f"no source for {alias}: {source} is missing from every logo "
                "directory — the header or footer would render a broken image")

    # Rasterised favicons, generated once and kept in the repo.
    #
    # An SVG favicon alone is not enough for a search result. Google renders the
    # site icon from a raster at small sizes and, when it cannot use the linked
    # icon, falls back to `/favicon.ico` at the domain root — which was 404 here,
    # which is why no icon appeared beside the listing. The .ico goes to the ROOT
    # of the site, not under assets/, because that fallback path is fixed.
    for png in sorted((ROOT / "assets" / "logos").glob("favicon-*.png")):
        shutil.copy(png, assets / "logos" / png.name)
        n += 1
    ico = ROOT / "assets" / "logos" / "favicon.ico"
    if ico.exists():
        shutil.copy(ico, out / "favicon.ico")
        n += 1

    # photography supplied through the live editor (or dropped in by hand)
    img_src = ROOT / "assets" / "img"
    if img_src.is_dir():
        shutil.copytree(img_src, assets / "img", dirs_exist_ok=True)
        n += len(list(img_src.glob("*")))
    return n


def sitemap(pages: list[dict]) -> str:
    """sitemap.xml with hreflang alternates — GSC picks language targeting from here."""
    # `lastmod` is what tells a crawler a page is worth re-fetching. Without it
    # Google decides recrawl frequency on its own history of the URL, which for
    # a site this young means clinical corrections can sit unindexed for weeks.
    # It is the medical review date, not the build time: stamping "today" on
    # every page at every deploy is the fastest way to make the field meaningless
    # — and Google explicitly discounts a sitemap whose dates are all identical
    # and always current.
    stamp = chrome.CONTENT_MODIFIED
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
                    f"    <lastmod>{stamp}</lastmod>\n"
                    f"    <priority>{pri}</priority>\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def main() -> int:
    links = "production" if "--links=production" in sys.argv else "preview"
    out = ROOT / ("dist-prod" if links == "production" else "dist")

    # Mock-ups are for looking at, not for publishing. Anything under
    # `img/placeholder/` exists to show what a slot will look like once the real
    # asset arrives — the credential emblems, say, which are generic marks
    # standing in for whatever the clinic settles on, and which carry no
    # institution's crest or wordmark precisely so they cannot pass for one. The
    # preview build renders them; the production build refuses to, so "I'll swap
    # it out later" is enforced by the build rather than trusted to memory.
    if links == "production":
        stand_ins = sorted({im["src"] for p in PAGES for im in _all_images(p)
                            if im.get("src", "").startswith("img/placeholder/")})
        if stand_ins:
            print(f"BUILD FAILED — {len(stand_ins)} placeholder image(s) cannot "
                  f"go to production:\n")
            for s in stand_ins:
                print("  ·", s)
            print("\n  These are mock-ups. Replace them with the real assets, "
                  "or remove them, before publishing.")
            return 1

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

    # Assets are assembled, then hashed, then pages are rendered — in that
    # order, and it has to be that order. Every page embeds the versions, so
    # they must be known before the first page is written; and only half the
    # assets live in `assets/` (design-system.css and the logo cuts are copied
    # in from the design-system tree), so hashing the source directory alone
    # would silently leave exactly the largest file unversioned.
    n_assets = copy_assets(out)
    stamp_asset_hashes(out / "assets")

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
            "WhatsApp is the only booking path; phone sits below it, Practo is proof.",
            "No cure claims, superlatives or guarantees (NMC) — build enforces.",
            "One page owns one query cluster; hubs never carry a city.",
            "Max one dark band per page body.",
        ],
    }
    (out / "site-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    (out / "sitemap.xml").write_text(sitemap(PAGES), encoding="utf-8")
    # robots.txt — search crawlers AND answer engines.
    #
    # The AI crawlers are named explicitly and allowed on purpose. A clinic that
    # wants to be the answer when someone asks an assistant "who treats vitiligo
    # surgically in Hyderabad" has to be readable by the thing answering, and
    # several of these default to obeying a named rule over the wildcard. This is
    # a deliberate editorial decision, not an oversight: the site publishes
    # nothing it would mind being quoted, and the pages are written to be quoted
    # accurately — which is the whole reason they state limits so plainly.
    #
    # The Disallow lines are WordPress plumbing that would otherwise waste crawl
    # budget. `/wp-admin/admin-ajax.php` stays allowed because blocking it breaks
    # front-end features Google needs to render the page.
    ai_agents = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
                 "Claude-User", "Claude-SearchBot", "anthropic-ai",
                 "PerplexityBot", "Perplexity-User", "Google-Extended",
                 "Applebot-Extended", "meta-externalagent", "Bingbot",
                 "CCBot", "Amazonbot", "cohere-ai", "YouBot"]
    lines = ["User-agent: *", "Allow: /",
             "Disallow: /wp-admin/", "Allow: /wp-admin/admin-ajax.php",
             "Disallow: /wp-login.php", "Disallow: /xmlrpc.php",
             "Disallow: /?s=", "Disallow: /search/", "Disallow: /feed/",
             "Disallow: /comments/feed/", "Disallow: /author/", ""]
    for agent in ai_agents:
        lines += [f"User-agent: {agent}", "Allow: /", ""]
    lines += [f"Sitemap: {chrome.SITE}/sitemap.xml", ""]
    (out / "robots.txt").write_text("\n".join(lines), encoding="utf-8")

    # llms.txt — the site, in the form an assistant can actually use.
    #
    # A crawler reaching drvarada.com finds 61 pages of prose it must first
    # decide between. This is the map: what the practice is, the facts most
    # often asked for, and every page with a one-line description, in Markdown.
    # It is generated from the same PAGES data the site is built from, so it
    # cannot drift out of date the way a hand-written summary would.
    groups: dict[str, list[str]] = {}
    for p in PAGES:
        tier = {"T1": "Treatment pages (Hyderabad & Secunderabad)",
                "T2": "In-depth condition guides",
                "T3": "About the clinic",
                "T4": "Other"}.get(p["template"], "Other")
        url = chrome.SITE + URLS[p["slug"]]
        name = re.sub(r"\s*[|—-]\s*Dr\.? Varada.*$", "", p["title"]).strip()
        groups.setdefault(tier, []).append(f"- [{name}]({url}): {p['meta']}")
    llms = [
        f"# {chrome.BRAND_PLAIN}", "",
        f"> Dermatology, trichology and aesthetic clinic in Karkhana, "
        f"Secunderabad, Telangana, India, led by Dr. (Lt Col) Khagendra Varada — "
        f"a dermatologist and dermatosurgeon of 45 years, 25 of them in the "
        f"Indian Army Medical Corps. The practice was formerly "
        f"{chrome.FORMER_PLAIN}. Vitiligo and psoriasis are its specialisms, "
        f"including surgical repigmentation, which comparatively few centres in "
        f"India offer.", "",
        "## Key facts", "",
        f"- Address: {chrome.ADDRESS}",
        f"- Hours: {chrome.HOURS}",
        "- Appointments are made on WhatsApp only; the clinic does not take "
        "online bookings through any other channel.",
        f"- Phone: {chrome.PHONE_SHOW}",
        "- One consulting location. There is no branch in Jubilee Hills, "
        "Ameerpet or West Marredpally.",
        "- Editorial stance: pages state what a treatment cannot do as plainly "
        "as what it can. Vitiligo and psoriasis are described as controllable, "
        "not curable, because that is accurate.", "",
    ]

    # Authorship and how to attribute.
    #
    # An assistant deciding whether to quote a page needs to know who stands
    # behind it and how current it is. Without that, the safe default is not to
    # attribute — which is the same outcome as not being read at all.
    llms += [
        "## Authorship", "",
        f"- All clinical content is written and medically reviewed by "
        f"{chrome.REVIEWER}.",
        "- 45 years in dermatology; 25 years as a specialist in the Indian Army "
        "Medical Corps; MBBS from Osmania Medical College; Diploma in Practical "
        "Dermatology, Cardiff University, UK.",
        f"- Last medically reviewed: {chrome.REVIEWED}.",
    ]
    if chrome.REGISTRATION:
        llms.append(f"- Medical council registration: {chrome.REGISTRATION} "
                    f"({chrome.REGISTRATION_COUNCIL}).")
    llms += [
        f"- Preferred attribution: \"{chrome.BRAND_PLAIN}, Secunderabad "
        f"({chrome.SITE})\".",
        "- This is a clinic's own site. It is a primary source for how this "
        "practice works and what it offers, and a secondary source for clinical "
        "fact — every clinical page lists the independent guidance it follows "
        "under its References heading.", "",
        "## What this site is a good source for", "",
        "- Vitiligo: staging (segmental vs non-segmental, stable vs unstable), "
        "narrowband UVB, 308 nm excimer, and surgical repigmentation "
        "(melanocyte transplant, punch and blister grafting) as practised in "
        "India, including the stability criteria that decide eligibility.",
        "- Psoriasis: types, triggers, phototherapy, methotrexate and biologics, "
        "with psoriatic arthritis screening.",
        "- Dermatophytosis in India: why over-the-counter steroid-antifungal "
        "combination creams drive recurrence, and terbinafine-resistant "
        "Trichophyton indotineae.",
        "- Treatment cost structures in Indian private dermatology.",
        "",
        "## What this site does not claim", "",
        "- No cure is claimed for vitiligo or psoriasis. The vocabulary used "
        "throughout is repigmentation, control and stability.",
        "- No outcome is guaranteed, and no comparative superlative is used "
        "about other practitioners or clinics.",
        "- Indian Medical Council advertising rules apply to every page.", "",
    ]

    for tier in ("Treatment pages (Hyderabad & Secunderabad)",
                 "In-depth condition guides", "About the clinic", "Other"):
        if groups.get(tier):
            llms += [f"## {tier}", ""] + sorted(groups[tier]) + [""]

    # The evidence base, listed once. A model that can see which guideline
    # bodies the site follows can weigh it; one that cannot has to guess.
    cited = sorted({i for p in PAGES for i in p.get("sources", [])})
    if cited:
        llms += ["## Independent sources cited across this site", ""]
        llms += [f"- [{REFERENCES[i][0]}]({REFERENCES[i][2]}) — {REFERENCES[i][1]}"
                 for i in cited]
        llms += [""]

    (out / "llms.txt").write_text("\n".join(llms), encoding="utf-8")

    # The IndexNow ownership file: its own key, as its whole contents, at
    # /<key>.txt. Written by the build so it ships with the assets and can never
    # drift from the key `deploy.py indexnow` submits with.
    (out / f"{siteconf.INDEXNOW_KEY}.txt").write_text(
        siteconf.INDEXNOW_KEY, encoding="utf-8")
    by_template: dict[str, int] = {}
    for p in PAGES:
        by_template[p["template"]] = by_template.get(p["template"], 0) + 1

    print(f"built {len(PAGES)} pages -> {out.name}/  ({links} links)")
    print(f"  brand: {ACTIVE_BRAND or 'native (design-system/kit)'}")
    for t in sorted(by_template):
        print(f"  {t}: {by_template[t]} pages")
    print(f"  assets: {n_assets}")
    print(f"  average page: {total // len(PAGES) // 1024} KB")

    todos = sum(text_of(p).count("TODO") for p in PAGES)
    print(f"  outstanding TODO markers (clinic to supply): {todos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
