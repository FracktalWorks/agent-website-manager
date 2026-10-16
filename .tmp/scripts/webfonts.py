# -*- coding: utf-8 -*-
r"""Webfont resolution for the design-system corpus — turn a named face into one we can ship.

WHY THIS EXISTS
  Every one of the 152 vendored design systems names a typeface in
  `--font-display` / `--font-body` / `--font-mono`, and not one of them ships a
  font file. 133 distinct families are named across the corpus and most are
  proprietary: Soehne, Circular, Canela, Druk Wide, GT Walsheim, Berkeley Mono.
  Pasting a brand's token block therefore produces a page that is *typeset in
  the fallback* — pick the `claude` system and you render in Georgia. The design
  reads as a different brand, and nothing warns you.

  This module closes that hole in the only way that is both legal and honest:

    1. If the named family is a system font (Arial, Georgia, Helvetica Neue,
       PingFang SC ...) it is already on the reader's machine. Leave it alone.
    2. If the named family is openly licensed (Inter, IBM Plex, JetBrains Mono,
       Source Serif ...) fetch the real thing and embed it. No substitution.
    3. Otherwise substitute an openly licensed face of the same classification
       and similar metrics, and SAY SO. `resolve()` returns the substitution in
       its report so a build can print it. A silent substitute is a lie about
       what the brand looks like; a declared one is a design decision.

  We never fetch, cache or ship a proprietary face. Substitution is not a
  workaround for licensing — it is the answer to it.

LICENCE OF WHAT WE CACHE
  Only families in OPEN_FAMILIES are ever downloaded, and each entry records its
  licence (OFL-1.1 or Apache-2.0). Both permit redistribution, so the cached
  woff2 files can live in the repo and be copied into a build. `fetch` writes a
  LICENCE.txt next to every family recording the licence and where it came from.

SUBSET NOTE
  Google's css2 endpoint returns one @font-face per unicode subset. We keep the
  subsets asked for and no more: a latin-only Inter is ~35 KB, the whole file
  with Cyrillic and Greek is several times that for glyphs an English clinic
  site will never render. Pages in Telugu or Devanagari need their own subset —
  pass `subsets=["telugu"]` and check the report, because most Latin families
  simply have no Telugu coverage to fetch.

Usage:
  python .tmp/scripts/webfonts.py list
  python .tmp/scripts/webfonts.py resolve "Soehne, Inter, sans-serif"
  python .tmp/scripts/webfonts.py fetch Inter "Source Serif 4"
  python .tmp/scripts/webfonts.py fetch --all
  python .tmp/scripts/webfonts.py fetch "Noto Sans Telugu" --subsets telugu,latin
  python .tmp/scripts/webfonts.py css Inter "JetBrains Mono"   # @font-face block
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.environ.get("WEBFONT_CACHE") or os.path.join(REPO_ROOT, "agent-data", "fonts")

# Google serves a different (older, wider) format to clients it does not
# recognise, and woff2 only to modern ones. Without a browser UA the css2
# endpoint answers with truetype URLs, which are 3-4x larger for the same glyphs.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# ─────────────────────────────────────────────────────────────────────────────
# What is already on the reader's machine
# ─────────────────────────────────────────────────────────────────────────────
# Substituting one of these would be actively wrong: the brand chose a face the
# reader already has, so there is nothing to fix and a download to avoid.
SYSTEM_FAMILIES = {
    "arial", "arial black", "helvetica", "helvetica neue", "times", "times new roman",
    "georgia", "courier", "courier new", "verdana", "tahoma", "trebuchet ms",
    "palatino", "palatino linotype", "book antiqua", "garamond", "cambria",
    "calibri", "candara", "corbel", "consolas", "cascadia mono", "cascadia code",
    "segoe ui", "segoe ui variable display", "segoe ui variable text", "comic sans ms",
    "impact", "lucida grande", "lucida console", "monaco", "menlo", "andale mono",
    "geneva", "optima", "futura", "gill sans", "didot", "baskerville", "charter",
    "hoefler text", "american typewriter", "avenir", "avenir next",
    "sf pro", "sf pro display", "sf pro text", "sf pro rounded", "sf mono",
    "pingfang sc", "hiragino sans", "yu gothic", "meiryo", "malgun gothic",
    "microsoft yahei", "noto sans cjk sc", "apple color emoji",
    # generic + CSS-defined keywords: never a download target
    "system-ui", "-apple-system", "blinkmacsystemfont", "ui-sans-serif",
    "ui-serif", "ui-monospace", "ui-rounded", "sans-serif", "serif", "monospace",
    "cursive", "fantasy", "emoji", "math", "inherit", "initial", "unset",
}

# ─────────────────────────────────────────────────────────────────────────────
# Families we may fetch and ship
# ─────────────────────────────────────────────────────────────────────────────
# `axes` is the css2 query fragment. Variable families get a weight range in one
# file, which is both smaller and better than four static weights.
OPEN_FAMILIES = {
    # ── neo-grotesque / UI sans ───────────────────────────────────────────
    "Inter":            {"axes": "wght@100..900", "class": "sans-grotesque", "licence": "OFL-1.1"},
    "Geist":            {"axes": "wght@100..900", "class": "sans-grotesque", "licence": "OFL-1.1"},
    "Archivo":          {"axes": "wght@100..900", "class": "sans-grotesque", "licence": "OFL-1.1"},
    "Libre Franklin":   {"axes": "wght@100..900", "class": "sans-grotesque", "licence": "OFL-1.1"},
    "Roboto":           {"axes": "wght@100..900", "class": "sans-neutral",   "licence": "Apache-2.0"},
    "Figtree":          {"axes": "wght@300..900", "class": "sans-neutral",   "licence": "OFL-1.1"},

    # ── geometric / rounded sans ──────────────────────────────────────────
    "Manrope":          {"axes": "wght@200..800", "class": "sans-geometric", "licence": "OFL-1.1"},
    "Jost":             {"axes": "wght@100..900", "class": "sans-geometric", "licence": "OFL-1.1"},
    "Outfit":           {"axes": "wght@100..900", "class": "sans-geometric", "licence": "OFL-1.1"},
    "Poppins":          {"axes": "wght@400;500;600;700", "class": "sans-geometric", "licence": "OFL-1.1"},
    "DM Sans":          {"axes": "wght@100..1000", "class": "sans-geometric", "licence": "OFL-1.1"},
    "Rubik":            {"axes": "wght@300..900", "class": "sans-rounded",   "licence": "OFL-1.1"},
    "Nunito":           {"axes": "wght@200..1000", "class": "sans-rounded",  "licence": "OFL-1.1"},
    "Gabarito":         {"axes": "wght@400..900", "class": "sans-display",   "licence": "OFL-1.1"},
    # Constellation Aerospace's display face (2026-09-26). Static weights only.
    "Chakra Petch":     {"axes": "wght@500;600;700", "class": "sans-display", "licence": "OFL-1.1"},

    # ── humanist sans ─────────────────────────────────────────────────────
    "IBM Plex Sans":    {"axes": "wght@100..700", "class": "sans-humanist",  "licence": "OFL-1.1"},
    "Source Sans 3":    {"axes": "wght@200..900", "class": "sans-humanist",  "licence": "OFL-1.1"},
    "Public Sans":      {"axes": "wght@100..900", "class": "sans-humanist",  "licence": "OFL-1.1"},

    # ── technical / wide display sans ─────────────────────────────────────
    "Space Grotesk":    {"axes": "wght@300..700", "class": "sans-technical", "licence": "OFL-1.1"},
    "Bricolage Grotesque": {"axes": "wght@200..800", "class": "sans-display", "licence": "OFL-1.1"},
    "Anton":            {"axes": "",              "class": "sans-condensed", "licence": "OFL-1.1"},

    # ── serif: text ───────────────────────────────────────────────────────
    "Source Serif 4":   {"axes": "wght@200..900", "class": "serif-text",     "licence": "OFL-1.1"},
    "Newsreader":       {"axes": "wght@200..800", "class": "serif-text",     "licence": "OFL-1.1"},
    "Lora":             {"axes": "wght@400..700", "class": "serif-text",     "licence": "OFL-1.1"},
    # Plex Serif and Plex Mono ship as static cuts on Google Fonts, unlike Plex
    # Sans — a `wght@100..700` *range* query 400s on them, a discrete list works.
    "IBM Plex Serif":   {"axes": "wght@400;500;600;700", "class": "serif-text", "licence": "OFL-1.1"},

    # ── serif: display ────────────────────────────────────────────────────
    "Fraunces":         {"axes": "wght@100..900", "class": "serif-display",  "licence": "OFL-1.1"},
    "Playfair Display": {"axes": "wght@400..900", "class": "serif-display",  "licence": "OFL-1.1"},
    "Instrument Serif": {"axes": "",              "class": "serif-display",  "licence": "OFL-1.1"},

    # ── monospace ─────────────────────────────────────────────────────────
    "JetBrains Mono":   {"axes": "wght@100..800", "class": "mono",           "licence": "OFL-1.1"},
    "IBM Plex Mono":    {"axes": "wght@400;500;600;700", "class": "mono",    "licence": "OFL-1.1"},
    "Fira Code":        {"axes": "wght@300..700", "class": "mono",           "licence": "OFL-1.1"},
    "Source Code Pro":  {"axes": "wght@200..900", "class": "mono",           "licence": "OFL-1.1"},
    "Roboto Mono":      {"axes": "wght@100..700", "class": "mono",           "licence": "Apache-2.0"},
    "Inconsolata":      {"axes": "wght@200..900", "class": "mono",           "licence": "OFL-1.1"},
    "Geist Mono":       {"axes": "wght@100..900", "class": "mono",           "licence": "OFL-1.1"},

    # ── novelty (named directly by a corpus system) ───────────────────────
    "Press Start 2P":   {"axes": "",              "class": "novelty",        "licence": "OFL-1.1"},

    # ── Indic: the te/hi pages of a Hyderabad site are not decoration ─────
    "Noto Sans Telugu":     {"axes": "wght@100..900", "class": "sans-indic", "licence": "OFL-1.1"},
    "Noto Serif Telugu":    {"axes": "wght@100..900", "class": "serif-indic", "licence": "OFL-1.1"},
    "Noto Sans Devanagari": {"axes": "wght@100..900", "class": "sans-indic", "licence": "OFL-1.1"},
    "Noto Serif Devanagari": {"axes": "wght@100..900", "class": "serif-indic", "licence": "OFL-1.1"},
}

# ─────────────────────────────────────────────────────────────────────────────
# Substitution: proprietary face -> open face of the same classification
# ─────────────────────────────────────────────────────────────────────────────
# Chosen on classification and metrics (x-height, width, terminal treatment),
# not on vibe. Keys are lowercased and matched after stripping weight/width
# words, so "BMWTypeNextLatin Light" and "sohne-var" both land.
SUBSTITUTE = {
    # neo-grotesques — the largest group by far
    "soehne": "Inter", "sohne": "Inter", "sohne-var": "Inter",
    "haas": "Inter", "haas groot disp": "Inter", "neuehaasgrotesk": "Inter",
    "unica77": "Inter", "unica77 cohere web": "Inter", "abc favorit": "Inter",
    "abcnormal": "Inter", "formular": "Inter", "matter": "Inter",
    "helvetica now text": "Inter", "helvetica now": "Inter",
    "larsseit": "Inter", "polysans": "Inter",
    "saans": "Inter", "signifier": "Fraunces", "exchange": "Source Serif 4",
    "mona sans": "Inter", "hashicorp sans": "Inter", "wise sans": "Inter",
    "notioninter": "Inter", "inter variable": "Inter", "geist sans": "Geist",
    "ant sans": "Inter", "canva sans": "Inter", "google sans": "Inter",
    "cohere text": "Inter", "coheretext": "Inter", "ubermovetext": "Inter",
    "ubermove": "Inter", "sst": "Inter", "sodosans": "Inter", "vodafone": "Inter",
    "spotifymixui": "Inter", "spotifymixuititle": "Inter", "renault group": "Inter",
    "nvidia-emea": "Inter", "markformc": "Inter", "markoffcformc": "Inter",
    "pin sans": "Inter", "super sans vf": "Inter", "optimistic vf": "Inter",
    "wf visual sans variable": "Inter", "camera plain variable": "Inter",
    "universal sans text": "Inter", "universalsans": "Inter",
    "figmasans": "Inter", "gg sans": "Inter", "waldenburg": "Inter",
    "basier-square": "Inter", "the future": "Inter", "cursorgothic": "Inter",
    "binanceplex": "Inter", "ciscosanstt": "Inter", "coinbasetext": "Inter",
    "franklin gothic": "Libre Franklin",

    # geometric / rounded
    "circular": "Manrope", "airbnb cereal vf": "Manrope", "cal sans": "Manrope",
    "euclid circular a": "Manrope", "gt walsheim framer medium": "Manrope",
    "gt walsheim": "Manrope", "degular": "Manrope", "rb-freigeist-neue": "Manrope",
    "nike futura nd": "Jost", "d-din": "Jost", "d-din-bold": "Jost",
    "ferrari sans": "Jost", "bmwtypenext": "Jost", "bmwtypenextlatin": "Jost",
    "feather bold": "Nunito", "dammit sans": "Nunito",

    # wide / display
    "druk wide": "Archivo", "universal sans display": "Archivo",
    "bugatti display": "Archivo", "lamborghini": "Archivo",
    "coinbasedisplay": "Archivo", "argent cf": "Playfair Display",

    # serif
    "canela": "Fraunces", "jjannon": "Newsreader",
    "anthropic serif": "Fraunces", "mongodb value serif": "Source Serif 4",
    "source serif pro": "Source Serif 4", "anthropic sans": "Inter",

    # mono
    "berkeley mono": "JetBrains Mono", "berkeleymono": "JetBrains Mono",
    "commit mono": "JetBrains Mono", "azeret mono": "JetBrains Mono",
    "pp neue montreal mono": "JetBrains Mono", "saansmono": "JetBrains Mono",
    "geistmono": "Geist Mono", "cohere mono": "JetBrains Mono",
    "coheremono": "JetBrains Mono", "anthropic mono": "JetBrains Mono",
    "gg mono": "JetBrains Mono", "figmamono": "JetBrains Mono",
    "soehne mono": "JetBrains Mono", "sohne mono": "JetBrains Mono",
    "jetbrains-mono": "JetBrains Mono", "sourcecodepro": "Source Code Pro",
    "ibm plex sans variable": "IBM Plex Sans",
    "source sans pro": "Source Sans 3",
}

# Words that describe a cut, not a family. Stripped before lookup so
# "BMWTypeNextLatin Light" and "Helvetica Now Text Medium" resolve.
_CUT_WORDS = re.compile(
    r"\b(variable|vf|var|latin|regular|book|light|medium|semibold|demibold|bold|"
    r"black|heavy|thin|italic|roman|text|display|web|std|pro|neue|new)\b", re.I)

# Generic fallbacks by class, appended so a page still typesets if a fetch
# never happened. Ordered widest-support first.
GENERIC_TAIL = {
    "sans": '"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif',
    "serif": 'Georgia, Cambria, "Times New Roman", serif',
    "mono": 'ui-monospace, "Cascadia Mono", "SF Mono", Menlo, Consolas, monospace',
    "novelty": "system-ui, sans-serif",
}


# System faces are not all sans. Getting this wrong appends a sans fallback tail
# behind Georgia, so a browser missing Georgia silently switches classification —
# the page stops being a serif design without anything having changed in the CSS.
SYSTEM_SERIFS = {
    "times", "times new roman", "georgia", "palatino", "palatino linotype",
    "book antiqua", "garamond", "cambria", "didot", "baskerville", "charter",
    "hoefler text", "american typewriter", "ui-serif", "serif",
}
SYSTEM_MONOS = {
    "courier", "courier new", "consolas", "cascadia mono", "cascadia code",
    "monaco", "menlo", "andale mono", "lucida console", "sf mono",
    "ui-monospace", "monospace",
}


def _fold(name: str) -> str:
    """Lowercase and strip diacritics so 'Söhne' and 'Soehne' hit the same rule.

    The corpus spells the same face three ways across three systems ('Söhne',
    'sohne-var', 'soehne'), which is exactly the sort of near-miss that makes a
    substitution table look like it works until the one system that spells it
    with an umlaut renders in Arial.
    """
    import unicodedata
    folded = unicodedata.normalize("NFKD", name.lower())
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return folded.replace("ß", "ss").strip()


def _tail_for(cls: str) -> str:
    if cls == "mono":
        return GENERIC_TAIL["mono"]
    if cls.startswith("serif"):
        return GENERIC_TAIL["serif"]
    if cls == "novelty":
        return GENERIC_TAIL["novelty"]
    return GENERIC_TAIL["sans"]


# ─────────────────────────────────────────────────────────────────────────────
# Cache
# ─────────────────────────────────────────────────────────────────────────────
def family_dir(family: str) -> str:
    return os.path.join(CACHE, re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-"))


def cached(family: str) -> dict | None:
    """Metadata for a family already in the cache, or None."""
    meta = os.path.join(family_dir(family), "meta.json")
    if not os.path.isfile(meta):
        return None
    with open(meta, encoding="utf-8") as fh:
        return json.load(fh)


def list_cached() -> list[dict]:
    if not os.path.isdir(CACHE):
        return []
    out = []
    for name in sorted(os.listdir(CACHE)):
        meta = os.path.join(CACHE, name, "meta.json")
        if os.path.isfile(meta):
            with open(meta, encoding="utf-8") as fh:
                out.append(json.load(fh))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Fetch
# ─────────────────────────────────────────────────────────────────────────────
def _get(url: str, binary: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    return data if binary else data.decode("utf-8")


def _blocks(css: str) -> list[dict]:
    """Split a css2 response into one dict per @font-face, keeping the subset comment.

    Google emits `/* latin */` immediately before the block it labels, and the
    subset name is not inside the block itself — so the comment is the only way
    to know which subset a URL covers.
    """
    out = []
    subset = None
    for chunk in re.split(r"(/\*\s*[a-z0-9-]+\s*\*/)", css):
        m = re.fullmatch(r"/\*\s*([a-z0-9-]+)\s*\*/", chunk.strip())
        if m:
            subset = m.group(1)
            continue
        for face in re.finditer(r"@font-face\s*\{(.*?)\}", chunk, re.S):
            body = face.group(1)
            url = re.search(r"url\((https://[^)]+\.woff2)\)", body)
            if not url:
                continue
            out.append({
                "subset": subset,
                "url": url.group(1),
                "style": (re.search(r"font-style:\s*([^;]+);", body) or [None, "normal"])[1].strip(),
                "weight": (re.search(r"font-weight:\s*([^;]+);", body) or [None, "400"])[1].strip(),
                "unicode_range": (re.search(r"unicode-range:\s*([^;]+);", body)
                                  or [None, ""])[1].strip(),
            })
    return out


def fetch(family: str, subsets=("latin",), force: bool = False) -> dict:
    """Download and cache the requested subsets of an openly licensed family.

    Refuses anything not in OPEN_FAMILIES. That refusal is the licensing
    safeguard: there is no code path that caches a proprietary face, so no
    later change can accidentally ship one.
    """
    if family not in OPEN_FAMILIES:
        raise ValueError(
            f"{family!r} is not in OPEN_FAMILIES — only openly licensed families "
            "may be cached. Add it with its licence, or use resolve() to pick a "
            "substitute.")
    spec = OPEN_FAMILIES[family]
    have = cached(family)
    if have and not force and set(subsets) <= set(have.get("subsets", [])):
        return have

    q = urllib.parse.quote(family.replace(" ", "+"), safe="+")
    axes = f":{spec['axes']}" if spec["axes"] else ""
    css = _get(f"https://fonts.googleapis.com/css2?family={q}{axes}&display=swap")

    wanted = [b for b in _blocks(css) if b["subset"] in subsets]
    if not wanted:
        found = sorted({b["subset"] for b in _blocks(css) if b["subset"]})
        raise LookupError(
            f"{family}: none of the requested subsets {list(subsets)} exist "
            f"upstream. Available: {found}. Latin families have no Telugu or "
            "Devanagari coverage to fetch — use a Noto family for those scripts.")

    out = family_dir(family)
    os.makedirs(out, exist_ok=True)
    faces = []
    for b in wanted:
        fname = f"{re.sub(r'[^A-Za-z0-9]+', '', family)}-{b['subset']}-{b['weight'].replace(' ', '_')}"
        fname = f"{fname}-{b['style']}.woff2" if b["style"] != "normal" else f"{fname}.woff2"
        path = os.path.join(out, fname)
        blob = _get(b["url"], binary=True)
        with open(path, "wb") as fh:
            fh.write(blob)
        faces.append({"file": fname, "bytes": len(blob), "subset": b["subset"],
                      "weight": b["weight"], "style": b["style"],
                      "unicode_range": b["unicode_range"]})

    meta = {
        "family": family,
        "class": spec["class"],
        "licence": spec["licence"],
        "source": "Google Fonts (fonts.gstatic.com)",
        "subsets": sorted({f["subset"] for f in faces}),
        "faces": faces,
    }
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    with open(os.path.join(out, "LICENCE.txt"), "w", encoding="utf-8") as fh:
        fh.write(
            f"{family}\nLicence: {spec['licence']}\n"
            "Retrieved from Google Fonts (fonts.gstatic.com) via the css2 API.\n\n"
            "Both OFL-1.1 and Apache-2.0 permit redistribution and embedding, "
            "which is why only families under those licences are cached here.\n"
            "Full licence text ships with the family upstream at\n"
            f"https://fonts.google.com/specimen/{family.replace(' ', '+')}/license\n")
    return meta


# ─────────────────────────────────────────────────────────────────────────────
# Resolve
# ─────────────────────────────────────────────────────────────────────────────
def split_stack(stack: str) -> list[str]:
    return [p.strip().strip("'\"") for p in stack.split(",") if p.strip()]


def _lookup_substitute(name: str) -> str | None:
    key = _fold(name)
    if key in SUBSTITUTE:
        return SUBSTITUTE[key]
    trimmed = " ".join(_CUT_WORDS.sub(" ", key).split())
    if trimmed and trimmed in SUBSTITUTE:
        return SUBSTITUTE[trimmed]
    # A trailing token like "-var" or camelCase joins ("figmaSans") — split and retry
    loose = " ".join(re.split(r"[-_]| (?=[a-z])", trimmed)).strip()
    if loose in SUBSTITUTE:
        return SUBSTITUTE[loose]
    # Last resort: the family's first word. "BMWTypeNextLatin Light" and
    # "Universal Sans Display" both carry their identity in the opening token.
    head = trimmed.split(" ")[0] if trimmed else ""
    return SUBSTITUTE.get(head)


def resolve(stack: str, role: str = "sans") -> dict:
    """Decide what a brand's font stack should actually be.

    Returns {family, stack, status, note, cached, class} where `status` is one of
    "system"    the brand named a face the reader already has — untouched
    "open"      the brand named an openly licensed face — we ship the real one
    "substitute" the brand named a proprietary face — we ship a stand-in
    "unmatched" we could not classify it — the stack is passed through with a
                generic tail added, and the caller should surface the warning
    """
    parts = split_stack(stack)
    first = parts[0] if parts else ""
    low = _fold(first)

    if not first:
        fam, status, note = "", "unmatched", "empty font stack"
    elif low in SYSTEM_FAMILIES:
        fam, status, note = first, "system", "already installed on the reader's machine"
    elif first in OPEN_FAMILIES:
        fam, status, note = first, "open", f"openly licensed ({OPEN_FAMILIES[first]['licence']})"
    else:
        sub = _lookup_substitute(first)
        bare = " ".join(_CUT_WORDS.sub(" ", low).split()).replace(" ", "").replace("-", "")
        if sub and _fold(sub).replace(" ", "") in (low.replace(" ", "").replace("-", ""), bare):
            # Same family, different spelling — "SourceCodePro", "jetbrains-mono",
            # "IBM Plex Sans Variable". Calling that a substitution would report a
            # design change where none happened.
            fam, status = sub, "open"
            note = (f"{first} is {sub} written without spaces — shipping the real "
                    f"family ({OPEN_FAMILIES[sub]['licence']})")
        elif sub:
            fam, status = sub, "substitute"
            note = (f"{first} is proprietary and cannot be shipped — substituted "
                    f"{sub}, same classification and comparable metrics")
        else:
            fam, status, note = first, "unmatched", (
                f"{first} is not a system font, not openly licensed, and has no "
                "substitution rule — the page will typeset in the fallback")

    cls = OPEN_FAMILIES.get(fam, {}).get("class")
    if not cls:
        cls = ("mono" if (low in SYSTEM_MONOS or role == "mono")
               else "serif-text" if (low in SYSTEM_SERIFS or role == "serif")
               else "sans")

    # Keep the brand's own fallbacks: they are a design decision, and if the
    # reader happens to have the real face installed it should still win.
    rest = [p for p in parts[1:] if _fold(p) not in {"sans-serif", "serif", "monospace"}]
    head = [fam] if fam else []
    if status == "substitute":
        head = [first, fam]          # real face first for anyone who owns it

    # De-duplicate case-insensitively, keeping first occurrence. Without this a
    # brand that already lists "Helvetica Neue" gets it twice once the generic
    # tail is appended, which is harmless but reads as a generated-file smell.
    ordered, seen = [], set()
    for p in head + rest + split_stack(_tail_for(cls)):
        key = _fold(p)
        if key and key not in seen:
            seen.add(key)
            ordered.append(p)
    css_stack = ", ".join(f'"{p}"' if " " in p else p for p in ordered)

    return {"family": fam, "requested": first, "stack": css_stack, "status": status,
            "note": note, "class": cls, "cached": cached(fam) is not None,
            "openly_licensed": fam in OPEN_FAMILIES}


def face_css(family: str, url_prefix: str = "assets/fonts/") -> str:
    """@font-face rules for a cached family, pointing at copied files."""
    meta = cached(family)
    if not meta:
        return ""
    d = re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")
    rules = []
    for f in meta["faces"]:
        rules.append(
            "@font-face{"
            f"font-family:'{family}';font-style:{f['style']};"
            f"font-weight:{f['weight']};font-display:swap;"
            f"src:url({url_prefix}{d}/{f['file']}) format('woff2');"
            + (f"unicode-range:{f['unicode_range']};" if f["unicode_range"] else "")
            + "}")
    return "\n".join(rules)


def copy_faces(family: str, dest_root: str) -> list[str]:
    """Copy a cached family's woff2 files into a build. Returns relative paths."""
    import shutil
    meta = cached(family)
    if not meta:
        return []
    d = re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")
    dest = os.path.join(dest_root, d)
    os.makedirs(dest, exist_ok=True)
    out = []
    for f in meta["faces"]:
        shutil.copy(os.path.join(family_dir(family), f["file"]),
                    os.path.join(dest, f["file"]))
        out.append(f"{d}/{f['file']}")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def cmd_list(args):
    have = {m["family"] for m in list_cached()}
    print(f"cache: {CACHE}")
    print(f"{len(OPEN_FAMILIES)} openly licensed families known, {len(have)} cached\n")
    by_class: dict[str, list[str]] = {}
    for fam, spec in OPEN_FAMILIES.items():
        by_class.setdefault(spec["class"], []).append(fam)
    for cls in sorted(by_class):
        print(f"  {cls}")
        for fam in sorted(by_class[cls]):
            mark = "*" if fam in have else " "
            size = ""
            if fam in have:
                m = cached(fam)
                kb = sum(f["bytes"] for f in m["faces"]) // 1024
                size = f"  {kb} KB  [{','.join(m['subsets'])}]"
            print(f"   {mark} {fam:22s} {OPEN_FAMILIES[fam]['licence']:11s}{size}")
    print("\n  * = cached locally and ready to embed")
    return 0


def cmd_resolve(args):
    for stack in args.stack:
        r = resolve(stack, role=args.role)
        print(f"  requested : {r['requested']}")
        print(f"  status    : {r['status']}  ({'cached' if r['cached'] else 'not cached'})")
        print(f"  family    : {r['family']}   [{r['class']}]")
        print(f"  note      : {r['note']}")
        print(f"  stack     : {r['stack']}\n")
    return 0


def cmd_fetch(args):
    subsets = tuple(s.strip() for s in args.subsets.split(",") if s.strip())
    names = list(OPEN_FAMILIES) if args.all else args.family
    ok = failed = 0
    for fam in names:
        want = subsets
        # Noto Indic families exist precisely for their script; fetching only
        # latin from them would cache the one subset they are not needed for.
        if fam.startswith("Noto ") and subsets == ("latin",):
            script = fam.rsplit(" ", 1)[-1].lower()
            want = (script, "latin")
        try:
            meta = fetch(fam, subsets=want, force=args.force)
            kb = sum(f["bytes"] for f in meta["faces"]) // 1024
            print(f"  ok    {fam:24s} {kb:4d} KB  {','.join(meta['subsets'])}")
            ok += 1
        except (urllib.error.URLError, LookupError, ValueError, OSError) as exc:
            print(f"  FAIL  {fam:24s} {type(exc).__name__}: {exc}")
            failed += 1
    print(f"\n{ok} cached, {failed} failed")
    return 1 if failed and not ok else 0


def cmd_css(args):
    for fam in args.family:
        css = face_css(fam, url_prefix=args.prefix)
        if not css:
            print(f"/* {fam}: not cached — run `webfonts.py fetch \"{fam}\"` */")
        else:
            print(css)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="known open families and what is cached").set_defaults(fn=cmd_list)

    p = sub.add_parser("resolve", help="what would we actually ship for this stack")
    p.add_argument("stack", nargs="+")
    p.add_argument("--role", default="sans", choices=["sans", "serif", "mono"])
    p.set_defaults(fn=cmd_resolve)

    p = sub.add_parser("fetch", help="download and cache an openly licensed family")
    p.add_argument("family", nargs="*")
    p.add_argument("--all", action="store_true")
    p.add_argument("--subsets", default="latin")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_fetch)

    p = sub.add_parser("css", help="@font-face block for a cached family")
    p.add_argument("family", nargs="+")
    p.add_argument("--prefix", default="assets/fonts/")
    p.set_defaults(fn=cmd_css)

    args = ap.parse_args(argv)
    if args.cmd == "fetch" and not args.family and not args.all:
        ap.error("fetch needs family names or --all")
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
