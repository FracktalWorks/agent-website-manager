# -*- coding: utf-8 -*-
r"""Design-system corpus interface — the repo's front door to `agent-data/design-systems/`.

WHY THIS EXISTS
  We vendored Open Design's 152-package design-system corpus (see
  agent-data/design-systems/PROVENANCE.md) so this agent can build sites with the
  same design fidelity without Open Design installed. But 152 folders x ~27 files
  is not something an LLM can browse. This module is the deterministic layer that
  turns the corpus into three cheap answers:

    "which system fits this brief?"   -> list_systems() / search()
    "give me the binding contract"    -> load()   (DESIGN.md + tokens.css + USAGE.md)
    "is this package well-formed?"    -> validate() / tokens()

  Everything here is a port of Open Design's TypeScript guards, chosen because the
  guards encode knowledge that is *not* recoverable from the data alone:
    - design-systems/_schema/manifest.schema.ts     -> MANIFEST validation
    - scripts/check-design-system-manifests.ts      -> path/JSON/semantic guards
    - packages/contracts/src/.../token-schema.ts    -> TOKEN_SCHEMA tier model
    - scripts/check-design-system-package-quality.ts-> QUALITY_RUBRIC scoring

  Dependency-free stdlib only, so it runs anywhere the repo runs.

CRLF NOTE
  The corpus was copied onto Windows and git may check LF files out as CRLF. Every
  read normalizes CRLF->LF *before* parsing or comparing (this is the same fix
  Open Design's own guard carries — see normalizeEol / issue #5175 there).
  Skipping it makes `^##\s` heading counts and value comparisons silently wrong.

Usage:
  python .tmp/scripts/design_systems.py list
  python .tmp/scripts/design_systems.py list --json
  python .tmp/scripts/design_systems.py search "warm editorial serif"
  python .tmp/scripts/design_systems.py show claude
  python .tmp/scripts/design_systems.py show claude --design      # full DESIGN.md
  python .tmp/scripts/design_systems.py validate claude
  python .tmp/scripts/design_systems.py validate --all
  python .tmp/scripts/design_systems.py tokens claude
  python .tmp/scripts/design_systems.py quality claude
  python .tmp/scripts/design_systems.py craft                     # list _craft rulebooks
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# The corpus carries CJK/Arabic system names and typographic dashes. On Windows
# the console defaults to cp1252, so printing a name like "紙" raises
# UnicodeEncodeError mid-stream and silently truncates the listing. Force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - py<3.7 / non-tty
        pass

# ─────────────────────────────────────────────────────────────────────────────
# Corpus location
# ─────────────────────────────────────────────────────────────────────────────
# This file lives at <repo>/.tmp/scripts/design_systems.py, so the repo root is
# two levels up. DESIGN_SYSTEMS_DIR lets a caller point at another corpus copy
# (e.g. a temp copy under test) without editing code.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.environ.get("DESIGN_SYSTEMS_DIR") or os.path.join(REPO_ROOT, "agent-data", "design-systems")
CRAFT_DIR = os.path.join(CORPUS, "_craft")

# Directories inside the corpus that are infrastructure, not design systems.
# Open Design skips only `_schema`; we also vendored `_craft` alongside, hence
# the underscore convention: any leading-underscore folder is not a system.
RESERVED_DIRS = {"_schema", "_craft"}

SCHEMA_VERSION = "od-design-system-project/v1"


# ─────────────────────────────────────────────────────────────────────────────
# TOKEN TIER MODEL  (port of packages/contracts/src/design-systems/token-schema.ts)
# ─────────────────────────────────────────────────────────────────────────────
# Four tiers, distinguished by TWO questions: who decides the value, and what
# happens if the brand omits it.
#
#   A1-identity   brand decides; omission is fatal. The token *is* the brand.
#   A1-structure  brand decides; omission is fatal. Structural choice (type
#                 scale, section rhythm, container) with no cross-brand default.
#   A2            brand decides, but a defensible cross-brand `fallback` exists.
#                 STILL REQUIRED in the final tokens.css — see WHY below.
#   B-slot        brand decides OR copies the schema-suggested `alias_to` verbatim.
#                 Exists so cross-brand components can reference a richer tier
#                 (--fg-2, --meta, --surface-warm, --border-soft) and always resolve.
#   C-extension   brand-private token, NOT in this table; tracked in
#                 BRAND_EXTENSIONS / BRAND_EXTENSION_PREFIXES below.
#
# WHY A2 is "required-with-fallback" and not "optional":
#   Artifacts are produced by pasting ONE brand's `:root` block into a single
#   <style>. There is no global defaults stylesheet in the cascade. So a missing
#   --motion-fast makes `transition: var(--motion-fast)` resolve to nothing and
#   the whole declaration is dropped — a silent visual break, not an error. The
#   `fallback` therefore exists for an authoring/derive step, never at runtime.
#   Same argument applies to B-slot: `alias_to` is a suggested default to COPY,
#   not a runtime fallback.
TOKEN_SCHEMA = [
    # ── Surface ───────────────────────────────────────────────────────────
    {"name": "--bg", "layer": "A1-identity", "description": "Page background — defines the brand canvas."},
    {"name": "--surface", "layer": "A1-identity", "description": "Card / lifted container background."},
    {"name": "--surface-warm", "layer": "B-slot", "description": "Tertiary surface tier (kami warm-sand).",
     "alias_to": "var(--surface)"},

    # ── Foreground ────────────────────────────────────────────────────────
    {"name": "--fg", "layer": "A1-identity", "description": "Primary text color."},
    {"name": "--fg-2", "layer": "B-slot", "description": "Secondary text tier (kami dark-warm).",
     "alias_to": "var(--fg)"},
    {"name": "--muted", "layer": "A1-identity", "description": "Subtext / captions."},
    {"name": "--meta", "layer": "B-slot", "description": "Tertiary FG / metadata tier (kami stone).",
     "alias_to": "var(--muted)"},

    # ── Border ────────────────────────────────────────────────────────────
    {"name": "--border", "layer": "A1-identity", "description": "Default border / card edge."},
    {"name": "--border-soft", "layer": "B-slot",
     "description": "Inner row separator that should not visually compete.", "alias_to": "var(--border)"},

    # ── Accent ────────────────────────────────────────────────────────────
    {"name": "--accent", "layer": "A1-identity",
     "description": "Brand accent. <=2 visible uses per screen (lint enforced)."},
    {"name": "--accent-on", "layer": "A2", "description": "FG when --accent is the bg.",
     "fallback": "#ffffff"},
    {"name": "--accent-hover", "layer": "A2", "description": "Hover state for elements using --accent as bg.",
     "fallback": "color-mix(in oklab, var(--accent), black 8%)"},
    {"name": "--accent-active", "layer": "A2", "description": "Active state for elements using --accent as bg.",
     "fallback": "color-mix(in oklab, var(--accent), black 14%)"},

    # ── Semantic ──────────────────────────────────────────────────────────
    {"name": "--success", "layer": "A2", "description": "Success state.", "fallback": "#16a34a"},
    {"name": "--warn", "layer": "A2", "description": "Warning state.", "fallback": "#eab308"},
    {"name": "--danger", "layer": "A2", "description": "Danger state.", "fallback": "#dc2626"},

    # ── Typography — fonts ────────────────────────────────────────────────
    {"name": "--font-display", "layer": "A1-identity", "description": "Display / heading font stack."},
    {"name": "--font-body", "layer": "A1-identity", "description": "Body font stack."},
    {"name": "--font-mono", "layer": "A2",
     "description": "Monospace font stack — used by kbd, code, tabular metrics.",
     "fallback": 'ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Monaco, Consolas, monospace'},

    # ── Typography — type scale ───────────────────────────────────────────
    {"name": "--text-xs", "layer": "A1-structure", "description": "Type scale step — extra small (~11-12px)."},
    {"name": "--text-sm", "layer": "A1-structure", "description": "Type scale step — small (~12-14px)."},
    {"name": "--text-base", "layer": "A1-structure", "description": "Type scale step — body baseline."},
    {"name": "--text-lg", "layer": "A1-structure", "description": "Type scale step — H3 / featured body."},
    {"name": "--text-xl", "layer": "A1-structure", "description": "Type scale step — H2."},
    {"name": "--text-2xl", "layer": "A1-structure", "description": "Type scale step — section title."},
    {"name": "--text-3xl", "layer": "A1-structure", "description": "Type scale step — H1."},
    {"name": "--text-4xl", "layer": "A1-structure", "description": "Type scale step — display / hero."},

    # ── Typography — leading & tracking ───────────────────────────────────
    {"name": "--leading-body", "layer": "A1-structure", "description": "Line-height for reading body."},
    {"name": "--leading-tight", "layer": "A1-structure", "description": "Line-height for headings."},
    {"name": "--tracking-display", "layer": "A1-structure",
     "description": "Letter-spacing applied to display sizes."},

    # ── Spacing — base scale ──────────────────────────────────────────────
    {"name": "--space-1", "layer": "A2", "description": "Base spacing — 4px tier.", "fallback": "4px"},
    {"name": "--space-2", "layer": "A2", "description": "Base spacing — 8px tier.", "fallback": "8px"},
    {"name": "--space-3", "layer": "A2", "description": "Base spacing — 12px tier.", "fallback": "12px"},
    {"name": "--space-4", "layer": "A2", "description": "Base spacing — 16px tier.", "fallback": "16px"},
    {"name": "--space-5", "layer": "A2", "description": "Base spacing — 20px tier.", "fallback": "20px"},
    {"name": "--space-6", "layer": "A2", "description": "Base spacing — 24px tier.", "fallback": "24px"},
    {"name": "--space-8", "layer": "A2", "description": "Base spacing — 32px tier.", "fallback": "32px"},
    {"name": "--space-12", "layer": "A2", "description": "Base spacing — 48px tier.", "fallback": "48px"},

    # ── Section rhythm ────────────────────────────────────────────────────
    {"name": "--section-y-desktop", "layer": "A1-structure",
     "description": "Vertical padding between sections — desktop."},
    {"name": "--section-y-tablet", "layer": "A1-structure",
     "description": "Vertical padding between sections — tablet."},
    {"name": "--section-y-phone", "layer": "A1-structure",
     "description": "Vertical padding between sections — phone."},

    # ── Radius ────────────────────────────────────────────────────────────
    {"name": "--radius-sm", "layer": "A2", "description": "Small radius — buttons, inputs, chips.",
     "fallback": "8px"},
    {"name": "--radius-md", "layer": "A2", "description": "Medium radius — cards, modals.", "fallback": "12px"},
    {"name": "--radius-lg", "layer": "A2", "description": "Large radius — featured containers.",
     "fallback": "16px"},
    {"name": "--radius-pill", "layer": "A2", "description": "Pill radius — avatars, badges.",
     "fallback": "9999px"},

    # ── Elevation ─────────────────────────────────────────────────────────
    {"name": "--elev-flat", "layer": "A2", "description": "No elevation.", "fallback": "none"},
    {"name": "--elev-ring", "layer": "A2", "description": "Hairline ring (1px box-shadow border).",
     "fallback": "0 0 0 1px var(--border)"},
    {"name": "--elev-raised", "layer": "A2", "description": "Raised surface (blur or whisper).",
     "fallback": "0 2px 8px color-mix(in oklab, var(--fg), transparent 92%)"},

    # ── Focus ─────────────────────────────────────────────────────────────
    {"name": "--focus-ring", "layer": "A2", "description": "Keyboard focus indicator.",
     "fallback": "0 0 0 3px color-mix(in oklab, var(--accent), transparent 70%)"},

    # ── Motion ────────────────────────────────────────────────────────────
    {"name": "--motion-fast", "layer": "A2", "description": "Hover / micro-state duration.",
     "fallback": "150ms"},
    {"name": "--motion-base", "layer": "A2", "description": "General state-change duration.",
     "fallback": "200ms"},
    {"name": "--ease-standard", "layer": "A2", "description": "Standard easing curve.",
     "fallback": "cubic-bezier(0.2, 0, 0, 1)"},

    # ── Layout ────────────────────────────────────────────────────────────
    {"name": "--container-max", "layer": "A1-structure", "description": "Max content container width."},
    {"name": "--container-gutter-desktop", "layer": "A1-structure",
     "description": "Container side gutter — desktop."},
    {"name": "--container-gutter-tablet", "layer": "A1-structure",
     "description": "Container side gutter — tablet."},
    {"name": "--container-gutter-phone", "layer": "A1-structure",
     "description": "Container side gutter — phone."},
]

TOKEN_BY_NAME = {t["name"]: t for t in TOKEN_SCHEMA}
LAYER_ORDER = ["A1-identity", "A1-structure", "A2", "B-slot"]

# Layer C — brand-private tokens that are explicitly allowed for one brand.
# WHY an allowlist rather than "anything goes": without it a brand can ship a
# name that other brands' shared components silently miss. The allowlist forces
# a review when a new brand-only name appears, and makes the C -> B-slot -> A2
# promotion path an explicit edit rather than an accident.
BRAND_EXTENSIONS = {
    "default": ["--space-20"],
    "openai": ["--space-16"],
    "kami": [
        "--accent-light", "--text-md", "--leading-display", "--leading-dense",
        "--tracking-eyebrow", "--tracking-label", "--space-7", "--space-18",
        "--space-22", "--radius-xs", "--radius-xl", "--elev-ring-accent",
    ],
    "tom-modern": [
        "--tm-accent-soft", "--tm-shadow-hard", "--tm-shadow-soft", "--tm-shadow-code",
        "--tm-header-height", "--tm-code-bg", "--tm-code-panel", "--tm-code-text",
    ],
}

# Prefixes that whitelist a whole family for ANY brand (e.g. kami's pre-blended
# tag tints). To restrict a family to one brand, enumerate it in BRAND_EXTENSIONS.
BRAND_EXTENSION_PREFIXES = ["--tag-bg-"]

# ── Promotion rules (from design-systems/_schema/AGENTS.md) ────────────────
# A token earns promotion when a SECOND brand needs the same name:
#   C -> B-slot : >=2 brands declare the name AND a meaningful sibling exists to
#                 alias to for brands lacking the richer tier.
#   C -> A2     : >=2 brands declare the name AND a defensible cross-brand
#                 fallback exists (no aliasing needed). Mirror in defaults.css.
#   B-slot -> A2: a B-slot starts being INDEPENDENTLY bound by >=2 brands.
#                 Replace alias_to with fallback.
#   A2 -> A1    : rare — the defaultable value turns out to be brand-determining
#                 (e.g. a brand whose identity is "instant" redefines motion).
# Demotion is not supported: mark @deprecated for one release, then delete from
# every brand's tokens.css in a single change.
PROMOTION_RULES = {
    "C -> B-slot": ">=2 brands declare the name and a meaningful sibling exists to alias to",
    "C -> A2": ">=2 brands declare the name and a defensible cross-brand fallback exists",
    "B-slot -> A2": "a B-slot is independently bound (not aliased) by >=2 brands",
    "A2 -> A1": "the defaultable value turns out to be brand-determining",
}

# When NOT to add a token — schema growth forces every brand to declare/alias it.
DO_NOT_TOKENIZE = [
    "Component-internal: a .btn-primary offset no other component reads. Inline it.",
    "One-off: a single layout's hero crop ratio. Not a token.",
    "Speculative: 'we might want --motion-slow someday.' Add it when a real interaction needs it.",
    "Already expressible: --accent-tint-50 == color-mix(in oklab, var(--accent), transparent 50%). "
    "Inline the color-mix() until >=2 components need the same tint at the same alpha.",
]


# ─────────────────────────────────────────────────────────────────────────────
# Low-level helpers
# ─────────────────────────────────────────────────────────────────────────────
def _norm_eol(text):
    """CRLF -> LF. Every parse/compare goes through this; see CRLF NOTE up top."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_text(path):
    """Read a corpus file as normalized UTF-8 text, or None when absent."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return _norm_eol(fh.read())
    except (OSError, IOError):
        return None


def system_dir(sid):
    return os.path.join(CORPUS, sid)


def _system_ids():
    """Every design-system folder id, sorted. Leading-underscore dirs are infra."""
    try:
        names = os.listdir(CORPUS)
    except OSError:
        return []
    return sorted(
        n for n in names
        if not n.startswith("_") and n not in RESERVED_DIRS
        and os.path.isdir(os.path.join(CORPUS, n))
    )


def craft_slugs():
    """Craft rulebook slugs = _craft/*.md minus README.md (Open Design's rule).

    Manifests reference these in `craft.applies` / `.suggested` / `.exemptions`,
    and validate() rejects slugs that do not resolve to a file — a typo would
    otherwise silently drop a craft section from the prompt.
    """
    try:
        return sorted(
            n[:-3] for n in os.listdir(CRAFT_DIR)
            if n.endswith(".md") and n != "README.md"
        )
    except OSError:
        return []


def load_manifest(sid):
    """Return (manifest_dict_or_None, error_or_None). None/None means no manifest."""
    raw = read_text(os.path.join(system_dir(sid), "manifest.json"))
    if raw is None:
        return None, None  # legacy DESIGN.md-only package — not an error
    try:
        return json.loads(raw), None
    except ValueError as exc:
        return None, "manifest.json is not valid JSON: %s" % exc


# ─────────────────────────────────────────────────────────────────────────────
# tokens.css parsing  (port of parseRootTokenDeclarationDetails)
# ─────────────────────────────────────────────────────────────────────────────
# `:root(?!\[)` deliberately skips `:root[data-theme="dark"]` variants — the
# UNSCOPED :root block is the one an agent pastes, so it is the one that must be
# complete. `.*?}` stops at the first close brace, which is correct for the flat
# token blocks this contract mandates (and matches upstream behavior exactly).
_ROOT_BLOCK_RE = re.compile(r":root(?!\[)\s*\{(.*?)\}", re.S)
# A declaration must start a line (possibly indented). This is what lets a
# `/* comment */` sitting in front of a declaration be stripped cleanly.
_DECL_START_RE = re.compile(r"(^|\n)[^\S\n]*--[A-Za-z0-9_-]+\s*:")


def _normalize_value(value):
    """Collapse internal whitespace so `0 0 0  1px` == `0 0 0 1px` on compare."""
    return re.sub(r"\s+", " ", value.strip())


def parse_root_tokens(css):
    """Parse every unscoped `:root { }` block into {name: {"value","line"}}.

    Later blocks win, mirroring CSS cascade order and upstream's Map.set().
    """
    out = {}
    if not css:
        return out
    for block in _ROOT_BLOCK_RE.finditer(css):
        body = block.group(1)
        body_start = block.start() + block.group(0).index("{") + 1
        segment_start = 0
        for raw_segment in body.split(";"):
            m = _DECL_START_RE.search(raw_segment)
            if m:
                # Skip the leading newline the pattern consumed so `line` is right.
                decl_start = segment_start + m.start() + len(m.group(1))
                declaration = body[decl_start:segment_start + len(raw_segment)].strip()
                if ":" in declaration:
                    name, _, value = declaration.partition(":")
                    out[name.strip()] = {
                        "value": _normalize_value(value),
                        "line": css.count("\n", 0, body_start + decl_start) + 1,
                    }
            segment_start += len(raw_segment) + 1
    return out


def all_declared_token_names(css):
    """Every `--name:` in the file, INCLUDING scoped blocks (quality-rubric count).

    Open Design's package-quality check counts names file-wide, not just :root,
    so a brand that splits tokens across light/dark blocks is not penalized.
    """
    return set(m.group(0)[:-1].strip() for m in re.finditer(r"--[A-Za-z0-9_-]+\s*:", css or ""))


def is_allowed_extension(sid, name):
    if any(name.startswith(p) for p in BRAND_EXTENSION_PREFIXES):
        return True
    return name in BRAND_EXTENSIONS.get(sid, [])


# ─────────────────────────────────────────────────────────────────────────────
# DESIGN.md / USAGE.md parsing
# ─────────────────────────────────────────────────────────────────────────────
# Quote lines that are metadata, not character. Left in, they turn a good blurb
# into "Surface: web A cosmic-premium, glassmorphic dark system…".
_QUOTE_META_RE = re.compile(
    r"^(category|surface|mode|scenario|status|version|id|name|author|tags|"
    r"upstream|license|source)\s*:", re.I)


def design_blurb(design_md):
    """The corpus convention: an H1, then a `> ...` blockquote header.

        # Design System Inspired by Claude (Anthropic)
        > Category: AI & LLM
        > Anthropic's AI assistant. Warm terracotta accent, clean editorial layout.

    The non-metadata quote lines are the author's own one-line character summary
    — the single best discriminating description in the whole package. Returns
    (category_or_None, blurb_or_None).
    """
    if not design_md:
        return None, None
    category, parts, seen_quote = None, [], False
    for line in design_md.split("\n"):
        s = line.strip()
        if s.startswith(">"):
            seen_quote = True
            body = s.lstrip(">").strip()
            if not body:
                continue
            meta = _QUOTE_META_RE.match(body)
            if meta:
                if meta.group(1).lower() == "category":
                    category = body.split(":", 1)[1].strip()
                continue
            parts.append(body)
        elif seen_quote and s:
            break  # blockquote header ended
        elif s.startswith("#") and seen_quote:
            break
    return category, (" ".join(parts) or None)


def design_first_paragraph(design_md):
    """Fallback blurb: the first real prose paragraph (skip headings/quotes/lists)."""
    if not design_md:
        return None
    for para in re.split(r"\n\s*\n", design_md):
        p = para.strip()
        if not p or p.startswith(("#", ">", "-", "*", "|", "```")):
            continue
        return re.sub(r"\s+", " ", p)
    return None


def usage_section(usage_md, heading):
    """Body of a `## <heading>` section in USAGE.md, or None."""
    if not usage_md:
        return None
    pat = re.compile(r"^##\s+%s\s*$" % re.escape(heading), re.M)
    m = pat.search(usage_md)
    if not m:
        return None
    rest = usage_md[m.end():]
    nxt = re.search(r"^##\s+", rest, re.M)
    return (rest[:nxt.start()] if nxt else rest).strip()


def has_usage_h2(usage_md, heading):
    return bool(usage_md) and bool(
        re.search(r"^##\s+%s\s*$" % re.escape(heading), usage_md, re.M)
    )


def count_h2(markdown):
    return len(re.findall(r"^##\s+\S", markdown or "", re.M))


# ─────────────────────────────────────────────────────────────────────────────
# Public API — list / search / load
# ─────────────────────────────────────────────────────────────────────────────
# Canonical v1 filenames. The contract FIXES these names (see FILES_LITERALS in
# validation) so nothing downstream has to guess from folder contents.
_OPTIONAL_FILES = [
    ("usage", "USAGE.md"),
    ("components", "components.html"),
    ("components_manifest", "components.manifest.json"),
    ("design_tokens", "design-tokens.json"),
    ("tailwind", "tailwind-v4.css"),
]
_OPTIONAL_DIRS = [("assets", "assets"), ("preview", "preview"),
                  ("source", "source"), ("fonts", "fonts")]


def list_systems():
    """Every system with id, name, category and which contract files it declares.

    Cheap: reads manifest.json (1.4KB) + the DESIGN.md blockquote header only.
    `legacy=True` marks a DESIGN.md-only folder with no manifest — still usable
    for prose, but it has no token contract to paste.
    """
    out = []
    for sid in _system_ids():
        d = system_dir(sid)
        manifest, err = load_manifest(sid)
        design_md = read_text(os.path.join(d, "DESIGN.md"))
        cat_from_design, blurb = design_blurb(design_md)

        files = []
        for label, fname in [("design", "DESIGN.md"), ("tokens", "tokens.css")] + _OPTIONAL_FILES:
            if os.path.isfile(os.path.join(d, fname)):
                files.append(label)
        for label, dname in _OPTIONAL_DIRS:
            if os.path.isdir(os.path.join(d, dname)):
                files.append(label + "/")

        preview_pages = []
        if isinstance(manifest, dict):
            preview = manifest.get("preview")
            if isinstance(preview, dict) and isinstance(preview.get("pages"), list):
                preview_pages = [p.get("role") or p.get("path")
                                 for p in preview["pages"] if isinstance(p, dict)]

        out.append({
            "id": sid,
            "name": (manifest or {}).get("name") or sid,
            "category": (manifest or {}).get("category") or cat_from_design or "",
            "description": (manifest or {}).get("description") or "",
            "blurb": blurb or "",
            "files": files,
            "preview_roles": preview_pages,
            "craft": (manifest or {}).get("craft") or {},
            "import_mode": (manifest or {}).get("importMode") or "",
            "source_type": ((manifest or {}).get("source") or {}).get("type", ""),
            "legacy": manifest is None,
            "manifest_error": err,
        })
    return out


def search(query, limit=20, deep=True):
    """Rank systems against a free-text brief.

    Cheap fields (id/name/category/blurb) score high; DESIGN.md + USAGE.md full
    text score low but are what make briefs like "warm editorial serif" work at
    all — the character words only exist in the prose. `deep=False` skips the
    ~3MB prose read when only names matter.
    """
    terms = [t for t in re.split(r"[^a-z0-9#+.-]+", (query or "").lower()) if t]
    if not terms:
        return []

    results = []
    for row in list_systems():
        sid = row["id"]
        d = system_dir(sid)
        haystacks = [
            (sid.lower(), 60),
            (row["name"].lower(), 40),
            (row["category"].lower(), 25),
            (row["blurb"].lower(), 20),
            (row["description"].lower(), 8),
        ]
        prose = ""
        if deep:
            prose = "\n".join(filter(None, [
                read_text(os.path.join(d, "DESIGN.md")) or "",
                read_text(os.path.join(d, "USAGE.md")) or "",
                read_text(os.path.join(d, "tokens.css")) or "",
            ])).lower()

        score, hits = 0, []
        for term in terms:
            matched = False
            if term == sid.lower():
                score += 200
                matched = True
            for hay, weight in haystacks:
                if term in hay:
                    score += weight
                    matched = True
                    break
            if prose:
                n = prose.count(term)
                if n:
                    score += min(n, 8) * 2  # cap so a long DESIGN.md can't dominate
                    matched = True
            if matched:
                hits.append(term)

        # Require at least half the query terms so unrelated systems drop out.
        if score and len(hits) >= max(1, (len(terms) + 1) // 2):
            results.append({"score": score, "matched": hits, **row})

    results.sort(key=lambda r: (-r["score"], r["id"]))
    return results[:limit]


def load(sid):
    """Everything a build needs, in one dict. THIS is what goes into a build's context.

    Returns design_md / tokens_css / usage_md as text and the manifest as a dict.
    `tokens_root_block` is the verbatim unscoped `:root { ... }` text — paste it,
    do not re-type it: retyping is where invented tokens and raw hex creep in.
    """
    d = system_dir(sid)
    if not os.path.isdir(d):
        raise ValueError("unknown design system: %s (see INDEX.md)" % sid)
    manifest, err = load_manifest(sid)
    tokens_css = read_text(os.path.join(d, "tokens.css"))
    root_blocks = _ROOT_BLOCK_RE.findall(tokens_css or "")
    return {
        "id": sid,
        "dir": d,
        "manifest": manifest,
        "manifest_error": err,
        "legacy": manifest is None,
        "design_md": read_text(os.path.join(d, "DESIGN.md")),
        "tokens_css": tokens_css,
        "usage_md": read_text(os.path.join(d, "USAGE.md")),
        "components_html_path": (os.path.join(d, "components.html")
                                 if os.path.isfile(os.path.join(d, "components.html")) else None),
        "design_tokens": _maybe_json(os.path.join(d, "design-tokens.json")),
        "tokens_root_block": ("\n".join(":root {%s}" % b for b in root_blocks) or None),
        "declared_tokens": parse_root_tokens(tokens_css),
        "craft": (manifest or {}).get("craft") or {},
    }


def _maybe_json(path):
    raw = read_text(path)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return {"_parse_error": True}


# ─────────────────────────────────────────────────────────────────────────────
# MANIFEST VALIDATION  (port of manifest.schema.ts + check-design-system-manifests.ts)
# ─────────────────────────────────────────────────────────────────────────────
# The v1 contract's whole trick is that filenames are FIXED literals, not free
# strings. `files.design` may only be "DESIGN.md". That is why discovery code
# never has to sniff folder contents, and why unknown keys are rejected outright
# rather than ignored — an ignored key is a silently-dropped intention.
ALLOWED_TOP_LEVEL_KEYS = {
    "schemaVersion", "id", "name", "category", "description", "source", "files",
    "assetsDir", "previewDir", "usage", "componentsManifest", "importMode",
    "craft", "fonts", "preview", "sourceFiles",
}
ALLOWED_SOURCE_KEYS = {
    "bundled": {"type", "origin"},
    "local": {"type", "path", "importedAt"},
    "github": {"type", "url", "branch", "commit", "importedAt"},
    "shadcn": {"type", "reference", "registryUrl", "item", "homepage", "importedAt"},
}
ALLOWED_FILES_KEYS = {"design", "tokens", "designTokens", "tailwind", "components"}
ALLOWED_CRAFT_KEYS = {"applies", "suggested", "exemptions"}
ALLOWED_FONT_KEYS = {"family", "file", "weight", "style"}
ALLOWED_PREVIEW_KEYS = {"dir", "pages"}
ALLOWED_PREVIEW_PAGE_KEYS = {"path", "role", "title"}
ALLOWED_SOURCE_FILES_KEYS = {"scanned", "evidence", "tokens", "report", "snippets"}

FILES_LITERALS = {
    "design": "DESIGN.md",
    "tokens": "tokens.css",
    "designTokens": "design-tokens.json",
    "tailwind": "tailwind-v4.css",
    "components": "components.html",
}
IMPORT_MODES = {"normalized", "hybrid", "verbatim"}
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$")


def _reject_unknown_keys(errors, label, obj, allowed):
    for key in obj:
        if key not in allowed:
            errors.append("%s.%s is not part of the v1 schema" % (label, key))


def _expect_literal(errors, label, value, expected):
    if value != expected:
        errors.append("%s must be %s" % (label, json.dumps(expected)))


def _expect_nonempty_str(errors, label, value):
    if not isinstance(value, str) or not value.strip():
        errors.append("%s must be a non-empty string" % label)


def _expect_slug(errors, label, value):
    if not isinstance(value, str) or not _SLUG_RE.match(value):
        errors.append("%s must be a lowercase slug matching /^[a-z0-9]+(?:-[a-z0-9]+)*$/" % label)


def _expect_slug_array(errors, label, value):
    if not isinstance(value, list):
        errors.append("%s must be an array of lowercase slugs" % label)
        return
    for i, entry in enumerate(value):
        if not isinstance(entry, str) or not _SLUG_RE.match(entry):
            errors.append("%s[%d] must be a lowercase slug matching "
                          "/^[a-z0-9]+(?:-[a-z0-9]+)*$/" % (label, i))


def _expect_iso(errors, label, value):
    if not isinstance(value, str) or not _ISO_RE.match(value.strip()):
        errors.append("%s must be an ISO-like datetime string" % label)


def _expect_safe_relative_path(errors, label, value):
    """A declared path must not escape the package or carry OS-specific syntax.

    Rejects: absolute POSIX paths, drive letters, backslashes (a Windows-authored
    path breaks every non-Windows consumer), and empty / "." / ".." segments.
    """
    if not isinstance(value, str) or not value.strip():
        errors.append("%s must be a non-empty relative path" % label)
        return False
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value) or "\\" in value:
        errors.append("%s must be a safe relative path" % label)
        return False
    if any(seg in ("", ".", "..") for seg in value.split("/")):
        errors.append('%s must be a safe relative path without empty, "." or ".." segments' % label)
        return False
    return True


def validate_manifest_shape(value):
    """Pure shape validation. Returns a list of JSONPath-style error strings."""
    errors = []
    if not isinstance(value, dict):
        return ["manifest must be a JSON object"]

    _reject_unknown_keys(errors, "$", value, ALLOWED_TOP_LEVEL_KEYS)
    _expect_literal(errors, "$.schemaVersion", value.get("schemaVersion"), SCHEMA_VERSION)
    _expect_slug(errors, "$.id", value.get("id"))
    _expect_nonempty_str(errors, "$.name", value.get("name"))
    _expect_nonempty_str(errors, "$.category", value.get("category"))
    if "description" in value:
        _expect_nonempty_str(errors, "$.description", value["description"])

    # ── source ──
    source = value.get("source")
    if not isinstance(source, dict):
        errors.append("$.source must be an object")
    else:
        stype = source.get("type")
        if stype not in ALLOWED_SOURCE_KEYS:
            errors.append("$.source.type must be one of bundled, local, github, shadcn")
        else:
            _reject_unknown_keys(errors, "$.source", source, ALLOWED_SOURCE_KEYS[stype])
            required = {"bundled": [], "local": ["path"], "github": ["url"], "shadcn": ["reference"]}[stype]
            for key in required:
                _expect_nonempty_str(errors, "$.source.%s" % key, source.get(key))
            for key in ("origin", "branch", "commit", "registryUrl", "item", "homepage"):
                if key in source:
                    _expect_nonempty_str(errors, "$.source.%s" % key, source[key])
            if "importedAt" in source:
                _expect_iso(errors, "$.source.importedAt", source["importedAt"])

    # ── files (fixed literals) ──
    files = value.get("files")
    if not isinstance(files, dict):
        errors.append("$.files must be an object")
    else:
        _reject_unknown_keys(errors, "$.files", files, ALLOWED_FILES_KEYS)
        _expect_literal(errors, "$.files.design", files.get("design"), FILES_LITERALS["design"])
        _expect_literal(errors, "$.files.tokens", files.get("tokens"), FILES_LITERALS["tokens"])
        for key in ("designTokens", "tailwind", "components"):
            if key in files:
                _expect_literal(errors, "$.files.%s" % key, files[key], FILES_LITERALS[key])

    if "assetsDir" in value:
        _expect_literal(errors, "$.assetsDir", value["assetsDir"], "assets")
    if "previewDir" in value:
        _expect_literal(errors, "$.previewDir", value["previewDir"], "preview")
    if "usage" in value:
        _expect_safe_relative_path(errors, "$.usage", value["usage"])
    if "componentsManifest" in value:
        _expect_safe_relative_path(errors, "$.componentsManifest", value["componentsManifest"])
    if "importMode" in value and value["importMode"] not in IMPORT_MODES:
        errors.append("$.importMode must be one of normalized, hybrid, verbatim")

    # ── craft ──
    craft = value.get("craft")
    if craft is not None:
        if not isinstance(craft, dict):
            errors.append("$.craft must be an object")
        else:
            _reject_unknown_keys(errors, "$.craft", craft, ALLOWED_CRAFT_KEYS)
            for key in ("applies", "suggested", "exemptions"):
                _expect_slug_array(errors, "$.craft.%s" % key, craft.get(key))

    # ── fonts ──
    if "fonts" in value:
        fonts = value["fonts"]
        if not isinstance(fonts, list):
            errors.append("$.fonts must be an array")
        else:
            for i, font in enumerate(fonts):
                label = "$.fonts[%d]" % i
                if not isinstance(font, dict):
                    errors.append("%s must be an object" % label)
                    continue
                _reject_unknown_keys(errors, label, font, ALLOWED_FONT_KEYS)
                _expect_nonempty_str(errors, "%s.family" % label, font.get("family"))
                _expect_safe_relative_path(errors, "%s.file" % label, font.get("file"))
                if "weight" in font and not isinstance(font["weight"], (int, float, str)):
                    errors.append("%s.weight must be a number or string" % label)
                if "style" in font:
                    _expect_nonempty_str(errors, "%s.style" % label, font["style"])

    # ── preview ──
    if "preview" in value:
        preview = value["preview"]
        if not isinstance(preview, dict):
            errors.append("$.preview must be an object")
        else:
            _reject_unknown_keys(errors, "$.preview", preview, ALLOWED_PREVIEW_KEYS)
            _expect_safe_relative_path(errors, "$.preview.dir", preview.get("dir"))
            if not isinstance(preview.get("pages"), list):
                errors.append("$.preview.pages must be an array")
            else:
                for i, page in enumerate(preview["pages"]):
                    label = "$.preview.pages[%d]" % i
                    if not isinstance(page, dict):
                        errors.append("%s must be an object" % label)
                        continue
                    _reject_unknown_keys(errors, label, page, ALLOWED_PREVIEW_PAGE_KEYS)
                    _expect_safe_relative_path(errors, "%s.path" % label, page.get("path"))
                    for key in ("role", "title"):
                        if key in page:
                            _expect_nonempty_str(errors, "%s.%s" % (label, key), page[key])

    # ── sourceFiles ──
    if "sourceFiles" in value:
        sf = value["sourceFiles"]
        if not isinstance(sf, dict):
            errors.append("$.sourceFiles must be an object")
        else:
            _reject_unknown_keys(errors, "$.sourceFiles", sf, ALLOWED_SOURCE_FILES_KEYS)
            for key in sorted(ALLOWED_SOURCE_FILES_KEYS):
                if key in sf:
                    _expect_safe_relative_path(errors, "$.sourceFiles.%s" % key, sf[key])

    return errors


def validate(sid):
    """Full package validation: shape + semantics + every declared path exists.

    Returns {"ok", "id", "legacy", "errors", "notes"}.
    A legacy DESIGN.md-only folder is ok=True with a note — Open Design keeps
    those valid on purpose (compatibility path for older/user-installed folders),
    they are simply outside the manifest guard.
    """
    d = system_dir(sid)
    if not os.path.isdir(d):
        return {"ok": False, "id": sid, "legacy": False,
                "errors": ["design system folder does not exist: %s" % d], "notes": []}

    errors, notes = [], []
    manifest, parse_err = load_manifest(sid)

    if parse_err:
        return {"ok": False, "id": sid, "legacy": False, "errors": [parse_err], "notes": []}

    if manifest is None:
        if not os.path.isfile(os.path.join(d, "DESIGN.md")):
            errors.append("no manifest.json and no DESIGN.md — not a design system")
        notes.append("legacy DESIGN.md-only package: outside the manifest guard "
                     "(no token contract to paste)")
        return {"ok": not errors, "id": sid, "legacy": True, "errors": errors, "notes": notes}

    errors.extend(validate_manifest_shape(manifest))
    if errors:
        # Semantics below assume a well-shaped manifest; report shape first.
        return {"ok": False, "id": sid, "legacy": False, "errors": errors, "notes": notes}

    # ── id must equal the folder slug (the picker keys off the folder) ──
    if manifest.get("id") != sid:
        errors.append('$.id must match folder slug "%s"' % sid)

    # ── craft slugs must resolve, and cannot be both applied and exempted ──
    known_craft = set(craft_slugs())
    craft = manifest.get("craft") or {}
    for field in ("applies", "suggested", "exemptions"):
        for slug in craft.get(field) or []:
            if slug not in known_craft:
                errors.append('$.craft.%s references unknown craft "%s"' % (field, slug))
    exempt = set(craft.get("exemptions") or [])
    for slug in craft.get("applies") or []:
        if slug in exempt:
            errors.append('craft "%s" cannot be both applied and exempted' % slug)

    # ── import-mode semantics: a non-bundled import must show its evidence ──
    mode, stype = manifest.get("importMode"), (manifest.get("source") or {}).get("type")
    sf = manifest.get("sourceFiles")
    if mode == "hybrid" and stype != "bundled" and sf is None:
        errors.append("hybrid imports must declare sourceFiles evidence")
    if mode == "verbatim" and stype != "bundled":
        if not (sf or {}).get("tokens"):
            errors.append("verbatim imports must declare sourceFiles.tokens")
        if not (sf or {}).get("snippets"):
            errors.append("verbatim imports must declare sourceFiles.snippets")

    # ── every declared path must exist ──
    files = manifest.get("files") or {}
    declared = [files.get("design"), files.get("tokens"), files.get("designTokens"),
                files.get("tailwind"), files.get("components"),
                manifest.get("usage"), manifest.get("componentsManifest")]
    declared += [f.get("file") for f in (manifest.get("fonts") or []) if isinstance(f, dict)]
    declared += [p.get("path") for p in ((manifest.get("preview") or {}).get("pages") or [])
                 if isinstance(p, dict)]
    declared += list((sf or {}).values())
    for rel in [x for x in declared if isinstance(x, str)]:
        if not os.path.exists(os.path.join(d, rel)):
            errors.append("%s is declared but does not exist" % rel)

    for key in ("assetsDir", "previewDir"):
        if key in manifest and not os.path.isdir(os.path.join(d, manifest[key])):
            errors.append("%s is declared but %s/ does not exist" % (key, manifest[key]))
    pv = manifest.get("preview")
    if isinstance(pv, dict) and isinstance(pv.get("dir"), str) \
            and not os.path.isdir(os.path.join(d, pv["dir"])):
        errors.append("preview.dir is declared but %s/ does not exist" % pv["dir"])

    # ── declared JSON indexes must parse ──
    for key in ("scanned", "tokens", "report", "snippets"):
        rel = (sf or {}).get(key)
        if isinstance(rel, str) and os.path.isfile(os.path.join(d, rel)):
            if read_text(os.path.join(d, rel)) is not None:
                try:
                    json.loads(read_text(os.path.join(d, rel)))
                except ValueError as exc:
                    errors.append("%s is declared as JSON but could not be parsed: %s" % (rel, exc))

    # ── design-tokens.json envelope + agreement with tokens.css ──
    errors.extend(_validate_design_tokens(d, manifest))
    # ── tailwind-v4.css must not reference tokens tokens.css does not declare ──
    errors.extend(_validate_tailwind(d, manifest))

    if not os.path.isfile(os.path.join(d, "components.manifest.json")) \
            and manifest.get("componentsManifest") is None:
        notes.append("no components.manifest.json (component inventory cache absent)")

    return {"ok": not errors, "id": sid, "legacy": False, "errors": errors, "notes": notes}


def _validate_design_tokens(d, manifest):
    """Envelope check + report/tokens.css agreement.

    NOT ported: upstream re-renders design-tokens.json from the report and
    byte-compares (staleness). That needs their renderDesignTokensJson formatter,
    which is presentation, not contract. What we DO check is the part that can
    actually break a build: every token the report claims must exist in
    tokens.css with the same value, and every schema token must be in the report.
    """
    errors = []
    files = manifest.get("files") or {}
    dt_rel = files.get("designTokens")
    if not dt_rel:
        return errors
    dt_path = os.path.join(d, dt_rel)
    if not os.path.isfile(dt_path):
        return errors  # already reported as a missing declared path
    try:
        dt = json.loads(read_text(dt_path))
    except ValueError as exc:
        return ["%s could not be parsed: %s" % (dt_rel, exc)]
    if not isinstance(dt, dict):
        return ["%s must be a JSON object" % dt_rel]
    if dt.get("format") != "od-design-tokens/v1":
        errors.append("%s format must be od-design-tokens/v1" % dt_rel)
    if dt.get("contract") != "TOKEN_SCHEMA":
        errors.append("%s contract must be TOKEN_SCHEMA" % dt_rel)
    if not isinstance(dt.get("tokens"), list):
        errors.append("%s tokens must be an array" % dt_rel)
        return errors

    report_rel = (manifest.get("sourceFiles") or {}).get("report")
    if not report_rel:
        errors.append("%s requires sourceFiles.report" % dt_rel)
        return errors
    report_path = os.path.join(d, report_rel)
    try:
        report = json.loads(read_text(report_path) or "")
    except (ValueError, TypeError) as exc:
        return errors + ["%s could not be parsed while validating %s: %s" % (report_rel, dt_rel, exc)]
    if not isinstance(report, dict) or not isinstance(report.get("tokens"), list) \
            or "generatedAt" not in report or not isinstance(report.get("summary"), dict):
        return errors + ["%s must contain generatedAt, summary, and token contract bindings" % report_rel]

    report_names = set(t.get("name") for t in report["tokens"] if isinstance(t, dict))
    for spec in TOKEN_SCHEMA:
        if spec["name"] not in report_names:
            errors.append("%s is missing %s" % (report_rel, spec["name"]))

    declared = parse_root_tokens(read_text(os.path.join(d, files.get("tokens", "tokens.css"))) or "")
    for binding in report["tokens"]:
        if not isinstance(binding, dict):
            continue
        name, value = binding.get("name"), binding.get("value")
        got = declared.get(name)
        if got is None:
            errors.append("%s token %s is missing from tokens.css" % (report_rel, name))
        elif isinstance(value, str) and got["value"] != _normalize_value(value):
            errors.append("%s token %s value does not match tokens.css" % (report_rel, name))
    return errors


def _validate_tailwind(d, manifest):
    """Every `var(--x)` in tailwind-v4.css must be declared in tokens.css.

    NOT ported: upstream regenerates the whole file and byte-compares. That check
    is direction-sensitive (a brand's C-extensions legitimately do not appear in
    the @theme block), so the containment check in the *safe* direction is the
    portable half — and it is the half that catches a real broken reference.
    """
    errors = []
    files = manifest.get("files") or {}
    tw_rel = files.get("tailwind")
    if not tw_rel:
        return errors
    tw = read_text(os.path.join(d, tw_rel))
    if tw is None:
        return errors
    declared = all_declared_token_names(read_text(os.path.join(d, files.get("tokens", "tokens.css"))) or "")
    referenced = set(re.findall(r"var\((--[A-Za-z0-9_-]+)\)", tw))
    for name in sorted(referenced - declared):
        errors.append("%s references %s which tokens.css does not declare" % (tw_rel, name))
    return errors


# ─────────────────────────────────────────────────────────────────────────────
# TOKENS — declared values + missing-tier report
# ─────────────────────────────────────────────────────────────────────────────
def tokens(sid):
    """Parse tokens.css `:root` and report tier coverage.

    Returns:
      declared   {name: value} from the UNSCOPED :root block(s) — the pasteable set
      missing    {layer: [{name, description, fallback|alias_to}]}  <- the gaps
      extensions {"allowed": [...], "unreviewed": [...]}  <- C-tier candidates
      aliased / bound  which B-slots collapse to a sibling vs. bind independently
      scoped_only  names declared ONLY in a scoped block (e.g. :root[data-theme])
                   — these look present but DO NOT resolve in a pasted artifact
    """
    d = system_dir(sid)
    css = read_text(os.path.join(d, "tokens.css"))
    if css is None:
        return {"id": sid, "error": "no tokens.css (legacy DESIGN.md-only package?)",
                "declared": {}, "missing": {}, "extensions": {}, "counts": {}}

    root = parse_root_tokens(css)
    declared = {name: info["value"] for name, info in root.items()}
    every = all_declared_token_names(css)

    missing = {layer: [] for layer in LAYER_ORDER}
    for spec in TOKEN_SCHEMA:
        if spec["name"] not in declared:
            missing[spec["layer"]].append({
                "name": spec["name"],
                "description": spec["description"],
                "fallback": spec.get("fallback"),
                "alias_to": spec.get("alias_to"),
            })

    aliased, bound = [], []
    for spec in TOKEN_SCHEMA:
        if spec["layer"] != "B-slot":
            continue
        value = declared.get(spec["name"])
        if value is None:
            continue
        (aliased if value.replace(" ", "") == (spec.get("alias_to") or "").replace(" ", "")
         else bound).append(spec["name"])

    extra = sorted(n for n in every if n not in TOKEN_BY_NAME)
    return {
        "id": sid,
        "declared": declared,
        "missing": {k: v for k, v in missing.items() if v},
        "extensions": {
            "allowed": [n for n in extra if is_allowed_extension(sid, n)],
            "unreviewed": [n for n in extra if not is_allowed_extension(sid, n)],
        },
        "b_slot": {"aliased": aliased, "bound": bound},
        "scoped_only": sorted(every - set(declared)),
        "counts": {
            "declared_root": len(declared),
            "declared_file": len(every),
            "schema_total": len(TOKEN_SCHEMA),
            "schema_present": len([s for s in TOKEN_SCHEMA if s["name"] in declared]),
            "missing_total": sum(len(v) for v in missing.values()),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# QUALITY RUBRIC  (port of check-design-system-package-quality.ts)
# ─────────────────────────────────────────────────────────────────────────────
def quality(sid):
    """Score a "rich" package against Open Design's minimums.

    A package counts as rich (and therefore scoreable) once it declares any of
    usage / componentsManifest / preview / sourceFiles. Score is
    (checks - failures) / checks, so it reads as a percentage.
    """
    d = system_dir(sid)
    manifest, err = load_manifest(sid)
    if manifest is None:
        return {"id": sid, "rich": False, "score": 0, "checks": [], "violations": [],
                "reason": err or "no manifest.json (legacy DESIGN.md-only package)"}

    rich = any(manifest.get(k) is not None
               for k in ("usage", "componentsManifest", "preview", "sourceFiles"))
    if not rich:
        return {"id": sid, "rich": False, "score": 0, "checks": [], "violations": [],
                "reason": "minimal package (DESIGN.md + tokens.css only)"}

    design_md = read_text(os.path.join(d, "DESIGN.md")) or ""
    tokens_css = read_text(os.path.join(d, "tokens.css")) or ""
    usage_md = read_text(os.path.join(d, manifest.get("usage") or "USAGE.md")) or ""

    checks, violations = [], []

    def record(label, passed):
        checks.append(label)
        if not passed:
            violations.append(label)

    record("DESIGN.md has >=7 H2 sections", count_h2(design_md) >= 7)
    record("tokens.css declares >=26 tokens", len(all_declared_token_names(tokens_css)) >= 26)

    if manifest.get("usage") is not None:
        for heading in ("Read Order", "Design Highlights", "Do", "Avoid"):
            record("USAGE.md includes '%s'" % heading, has_usage_h2(usage_md, heading))
    else:
        violations.append("rich packages must declare usage")
        checks.append("rich packages must declare usage")

    if manifest.get("componentsManifest") is not None and \
            os.path.isfile(os.path.join(d, "components.html")):
        # Upstream re-derives components.manifest.json here. We read the committed
        # cache instead (see the NOT-PORTED note in the skill) — same thresholds.
        cm = _maybe_json(os.path.join(d, manifest["componentsManifest"])) or {}
        fixture = cm.get("fixture") or {}
        toks = cm.get("tokens") or {}
        groups = cm.get("groups") or []
        record("component fixture >=10 selectors", (fixture.get("selectorCount") or 0) >= 10)
        record("component fixture >=8 token refs", len(toks.get("referenced") or []) >= 8)
        record("component groups present >=4",
               len([g for g in groups if isinstance(g, dict) and g.get("present")]) >= 4)
    else:
        checks.append("rich packages must declare componentsManifest and components.html")
        violations.append("rich packages must declare componentsManifest and components.html")

    pages = ((manifest.get("preview") or {}).get("pages")) or []
    record("preview has >=3 pages", len(pages) >= 3)
    for role in ("colors", "typography", "spacing"):
        record("preview includes role '%s'" % role,
               any(isinstance(p, dict) and p.get("role") == role for p in pages))

    if (manifest.get("source") or {}).get("type") != "bundled":
        record("imported package has source evidence", manifest.get("sourceFiles") is not None)
        record("imported package has token evidence",
               (manifest.get("sourceFiles") or {}).get("tokens") is not None)

    score = 0 if not checks else round((len(checks) - len(violations)) / float(len(checks)) * 100)
    return {"id": sid, "rich": True, "score": int(score), "checks": checks,
            "violations": violations, "reason": ""}


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def _print_json(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False))


def _clip(text, n):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= n else text[:n - 1].rsplit(" ", 1)[0] + "…"


def cmd_list(args):
    rows = list_systems()
    if args.json:
        _print_json(rows)
        return 0
    for r in rows:
        flag = "L" if r["legacy"] else " "
        print("%s %-26s %-30s %-22s %s" % (
            flag, r["id"], _clip(r["name"], 29), _clip(r["category"], 21),
            ",".join(r["files"])))
    return 0


def cmd_search(args):
    rows = search(" ".join(args.query), limit=args.limit, deep=not args.shallow)
    if args.json:
        _print_json(rows)
        return 0
    if not rows:
        print("no match")
        return 1
    for r in rows:
        print("%5d  %-24s %-28s %s" % (r["score"], r["id"], _clip(r["name"], 27),
                                       _clip(r["blurb"] or r["description"], 70)))
    return 0


def cmd_show(args):
    pkg = load(args.id)
    if args.json:
        _print_json({k: v for k, v in pkg.items() if k != "design_tokens"})
        return 0
    if args.design:
        print(pkg["design_md"] or "(no DESIGN.md)")
        return 0
    if args.tokens_css:
        print(pkg["tokens_css"] or "(no tokens.css)")
        return 0
    if args.root:
        print(pkg["tokens_root_block"] or "(no :root block)")
        return 0
    if args.usage:
        print(pkg["usage_md"] or "(no USAGE.md)")
        return 0

    m = pkg["manifest"] or {}
    cat, blurb = design_blurb(pkg["design_md"])
    print("%s — %s" % (pkg["id"], m.get("name") or pkg["id"]))
    print("category   : %s" % (m.get("category") or cat or "-"))
    print("character  : %s" % _clip(blurb or design_first_paragraph(pkg["design_md"]) or "-", 200))
    print("dir        : %s" % pkg["dir"])
    print("import mode: %s   source: %s   legacy: %s" % (
        m.get("importMode") or "-", (m.get("source") or {}).get("type", "-"), pkg["legacy"]))
    craft = pkg["craft"]
    if craft:
        print("craft      : applies=%s suggested=%s exemptions=%s" % (
            craft.get("applies") or [], craft.get("suggested") or [], craft.get("exemptions") or []))
    print("root tokens: %d" % len(pkg["declared_tokens"]))
    hl = usage_section(pkg["usage_md"], "Design Highlights")
    if hl:
        print("\nDesign Highlights\n%s" % hl)
    for label, key in (("Do", "Do"), ("Avoid", "Avoid")):
        sec = usage_section(pkg["usage_md"], key)
        if sec:
            print("\n%s\n%s" % (label, sec))
    print("\n(--design | --tokens-css | --root | --usage for full text)")
    return 0


def cmd_validate(args):
    targets = _system_ids() if args.all else [args.id]
    results = [validate(t) for t in targets]
    if args.json:
        _print_json(results)
        return 0 if all(r["ok"] for r in results) else 1
    bad = 0
    for r in results:
        if r["ok"] and not args.verbose and args.all:
            continue
        mark = "OK  " if r["ok"] else "FAIL"
        print("%s %s%s" % (mark, r["id"], "  (legacy)" if r["legacy"] else ""))
        for note in r["notes"]:
            print("     note: %s" % note)
        for err in r["errors"]:
            print("     - %s" % err)
        if not r["ok"]:
            bad += 1
    if args.all:
        print("\n%d systems checked, %d failed, %d legacy DESIGN.md-only" % (
            len(results), bad, len([r for r in results if r["legacy"]])))
    return 0 if bad == 0 else 1


def cmd_tokens(args):
    rep = tokens(args.id)
    if args.json:
        _print_json(rep)
        return 0
    if rep.get("error"):
        print("%s: %s" % (rep["id"], rep["error"]))
        return 1
    c = rep["counts"]
    print("%s — %d tokens in :root (%d in file); schema coverage %d/%d" % (
        rep["id"], c["declared_root"], c["declared_file"], c["schema_present"], c["schema_total"]))
    print("\nDECLARED (:root — paste this block verbatim)")
    for name, value in rep["declared"].items():
        tier = TOKEN_BY_NAME.get(name, {}).get("layer", "C-extension")
        print("  %-28s %-46s %s" % (name, _clip(value, 45), tier))
    if rep["missing"]:
        print("\nMISSING schema tokens (%d) — var() refs to these resolve to NOTHING "
              "in a pasted artifact" % c["missing_total"])
        for layer in LAYER_ORDER:
            for item in rep["missing"].get(layer, []):
                default = item.get("fallback") or item.get("alias_to") or "(brand must author)"
                print("  [%-13s] %-28s %s" % (layer, item["name"], _clip(default, 60)))
    else:
        print("\nMISSING: none — every A1/A2/B-slot token is declared.")
    bs = rep["b_slot"]
    print("\nB-SLOT: %d aliased to a sibling, %d independently bound" % (
        len(bs["aliased"]), len(bs["bound"])))
    ext = rep["extensions"]
    if ext["allowed"]:
        print("C-EXTENSIONS (allowlisted): %s" % ", ".join(ext["allowed"]))
    if ext["unreviewed"]:
        print("C-EXTENSIONS (not in the allowlist — brand-private, do not reference "
              "from shared components): %d" % len(ext["unreviewed"]))
        print("  %s" % _clip(", ".join(ext["unreviewed"]), 300))
    if rep["scoped_only"]:
        print("\nSCOPED-ONLY (declared outside the unscoped :root — will NOT resolve "
              "if you paste only :root): %s" % _clip(", ".join(rep["scoped_only"]), 200))
    return 0


def cmd_quality(args):
    targets = _system_ids() if args.all else [args.id]
    results = [quality(t) for t in targets]
    if args.json:
        _print_json(results)
        return 0
    for r in results:
        if not r["rich"]:
            print("--   %-24s %s" % (r["id"], r["reason"]))
            continue
        print("%3d%% %-24s %d/%d checks" % (r["score"], r["id"],
                                            len(r["checks"]) - len(r["violations"]), len(r["checks"])))
        for v in r["violations"]:
            print("       fail: %s" % v)
    return 0


def cmd_craft(args):
    slugs = craft_slugs()
    if args.json:
        _print_json(slugs)
        return 0
    print("_craft/ rulebooks (brand-independent; brand tokens win on value conflicts):")
    for slug in slugs:
        first = ""
        text = read_text(os.path.join(CRAFT_DIR, slug + ".md")) or ""
        for line in text.split("\n"):
            s = line.strip()
            if s and not s.startswith("#"):
                first = s
                break
        print("  %-34s %s" % (slug, _clip(first, 90)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corpus", help="override the design-systems directory")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("list", help="every system: id, name, category, declared files")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("search", help="rank systems against a free-text brief")
    p.add_argument("query", nargs="+")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--shallow", action="store_true", help="skip DESIGN.md full-text scan")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser("show", help="load one system (summary, or full text with a flag)")
    p.add_argument("id")
    p.add_argument("--design", action="store_true", help="print DESIGN.md")
    p.add_argument("--tokens-css", action="store_true", help="print tokens.css")
    p.add_argument("--root", action="store_true", help="print just the :root block(s)")
    p.add_argument("--usage", action="store_true", help="print USAGE.md")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("validate", help="manifest shape + semantics + declared paths exist")
    p.add_argument("id", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--verbose", action="store_true", help="with --all, also print passes")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("tokens", help="parsed :root values + missing A1/A2/B-slot report")
    p.add_argument("id")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_tokens)

    p = sub.add_parser("quality", help="score a rich package against the minimums")
    p.add_argument("id", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_quality)

    p = sub.add_parser("craft", help="list the brand-independent _craft rulebooks")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_craft)

    args = ap.parse_args(argv)
    if not getattr(args, "fn", None):
        ap.print_help()
        return 2
    if args.corpus:
        global CORPUS, CRAFT_DIR
        CORPUS = os.path.abspath(args.corpus)
        CRAFT_DIR = os.path.join(CORPUS, "_craft")
    if args.cmd in ("validate", "quality") and not args.all and not args.id:
        ap.error("%s needs an <id> or --all" % args.cmd)
    try:
        return args.fn(args)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
