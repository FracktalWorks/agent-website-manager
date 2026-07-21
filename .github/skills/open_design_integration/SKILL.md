---
name: open_design_integration
description: >
  Connect Open Design (open-design) with Agent Website Manager for design→deploy
  workflows. Generate production-quality web pages using Open Design skills +
  design systems, then deploy directly to WordPress via REST API.
when_to_use: >
  User wants to design/redesign pages using Open Design, generate pages from a
  design system, or create a design→deploy pipeline for WordPress sites.
authority: read
cost_tier: 2
version: 0.1.0
---

# Open Design Integration

> Design → Deploy pipeline: Open Design generates the pages, Agent Website
> Manager deploys them to WordPress.

## Architecture

```
┌──────────────────────┐     ┌─────────────────────────┐     ┌──────────────┐
│   Open Design         │────▶│  Agent Website Manager   │────▶│  WordPress   │
│   (design generation) │     │  (deployment pipeline)   │     │  (live site) │
│                       │     │                          │     │              │
│  • DESIGN.md          │     │  • open_design_bridge.py │     │  • Pages     │
│  • frontend-design    │     │    (deploy /             │     │  • Posts     │
│  • web-artifacts      │     │     deploy-elementor)    │     │  • Elementor │
└──────────────────────┘     └─────────────────────────┘     └──────────────┘
```

## Design Systems

Active design systems live in `agent-data/design-systems/`:

| System | Source | Site |
|--------|--------|------|
| fracktal-works | `open-design/design-systems/fracktal-works/` | fracktal.in |

## Workflow

### 1. Generate a Page Design with Open Design

Open Design uses the `frontend-design` skill + a design system to generate
production-quality HTML/CSS. Run Open Design and ask it to:

```
"Using the fracktal-works design system, design a [page type] page for [purpose].
Include [specific sections]. Output as a single self-contained HTML file."
```

The default deploy path (`deploy-canvas`, step 2) publishes the HTML verbatim, so it needs
no special authoring constraints — author the best design you can. **Only if the page will
use the Elementor fallback** (`deploy-elementor`, step 3 — not the default) include this in
the same request so the converter handles it cleanly on the first pass:

> "This will be converted to Elementor, so: no `::before`/`::after` for structural or
> decorative content (render real elements instead); no CSS Grid with non-uniform
> tracks like `2fr 1fr` (use flex rows/columns with explicit % widths); don't rely on
> `flex: 1` alone for fixed-width columns in a row (set explicit width/flex-basis %);
> images that must fill their container should set `object-fit:cover` directly on the
> `<img>`, not rely on a wrapper to stretch it; use HTML entities (`&rarr;`, `&mdash;`)
> instead of raw UTF-8 arrows/dashes."

`agent-data/design-systems/fracktal-works/DESIGN.md` already has this baked into its own
"Elementor-safe authoring" section, so it's redundant (but harmless) to repeat it for
that system specifically. Any *other* design system (the 130+ shipped with Open Design,
or a newly synced one) won't have it — always include the instruction above unless the
system's own DESIGN.md already documents equivalent constraints.

The output goes to Open Design's artifacts directory. Save the HTML to:
`outputs/design_pages/[slug].html`

### 2. Deploy to WordPress — `deploy-canvas` (THE DEFAULT)

**Publish the Open Design HTML directly.** One REST write embeds the design as a single
Gutenberg Custom HTML block on Elementor's chrome-free `elementor_canvas` template — no
widget conversion, no kit globals, no per-post CSS regeneration, no manual editor step:

```bash
python .tmp/scripts/open_design_bridge.py deploy-canvas \
  --html outputs/design_pages/[slug].html \
  --title "Page Title" \
  --slug "page-slug"
# add --id <page_id> to update an existing page; --status publish to go live
```

This is the highest-fidelity, fewest-moving-parts path — the page renders the design
**verbatim and is live immediately**. Why it's the default (see the
`open-design-canvas-vs-elementor` memory note for the full story):

- The design is already a complete, styled page. Converting it to Elementor's widget
  model is what loses fidelity and drags in the fragile kit-globals → CSS-regeneration →
  stale-render pipeline that eats hours.
- The admin app-password has `unfiltered_html`, so the raw `<style>`/markup is stored and
  served intact (this only works for **admin** users on **single-site** WordPress).
- No `uploads/elementor/css/post-N.css` is generated, so "CSS didn't regenerate / needs an
  editor Update / stale render" **cannot happen**. LiteSpeed purges the URL on the REST
  update like any normal page.

**Header/footer:** by default `deploy-canvas` uses the chrome-free `elementor_canvas`
template (no header/footer). To keep the site's Elementor header + footer (full-width
content), add **`--header-footer`**:

```bash
python .tmp/scripts/open_design_bridge.py deploy-canvas \
  --html outputs/design_pages/[slug].html --title "..." --slug "..." \
  --id <page_id> --status publish --header-footer
```

That switches the template to `elementor_header_footer` (the template your normal
full-width pages use) AND automatically **scopes every design selector under `.od-embed`**
(via `_scope_css`) so the design's generic rules (`body`, `h2`, `a`, `.wrap`…) can't
restyle the header/footer chrome. Verified: header links keep their own color, page body
keeps the theme font, and the design still renders correctly inside the wrapper. Use
`--header-footer` for normal site pages that should sit in the site nav; omit it for
full-bleed landing pages.

**Structured data (schema):** `deploy-canvas` strips `<style>`/`<script>` when embedding
the body, **but preserves `<script type="application/ld+json">`** blocks (re-emitted inside
the Custom HTML block). So to add FAQPage / Product / HowTo schema to a canvas page, put the
JSON-LD in the source HTML's `<head>` — it survives every redeploy. Yoast still emits the
page's WebPage/Organization/Breadcrumb graph on top. (Yoast can't auto-detect an FAQ inside
raw canvas HTML, so FAQPage must be added this way, not via a Yoast block.)

**Tradeoff:** the page is an opaque HTML blob in WordPress — not editable in the
Elementor/Gutenberg UI. The source of truth is the Open Design file; re-run `deploy-canvas`
to change it. That's the right trade for design-driven pages where Open Design is the
source of truth.

**Lazy-load:** images can flash as gray placeholders on first paint if LiteSpeed's
lazy-load JS is stale (site-wide `693.js` issue); a LiteSpeed *Purge All* fixes it. The
images do load on scroll regardless.

### 3. Fallback: `deploy-elementor` (ONLY when the page must be hand-editable in WP)

Use this **only** when someone genuinely needs to edit the page inside WordPress's
Elementor editor afterward. It converts the HTML to native Elementor widgets via
`html2elementor` (convert → import → kit-merge). It is lower-fidelity and **requires a
manual Elementor editor "Update" after deploy** to regenerate the per-post CSS and clear
the stale render (a REST write alone does not fire Elementor's save pipeline):

```bash
python .tmp/scripts/open_design_bridge.py deploy-elementor \
  --html outputs/design_pages/[slug].html --title "Page Title" --slug "page-slug"
# then: open the page in the Elementor editor and click Update, then verify:
python .github/skills/elementor_builder/scripts/verify_fidelity.py \
  --source outputs/design_pages/[slug].html --live https://fracktal.in/page-slug/
```

If `verify_fidelity.py` reports drift, patch via the `elementor_builder` skill's
fidelity-patch step (see the `elementor-fidelity-patch-workflow` memory note). The
converter now emits **direct colors, not kit-global refs** — global-color refs silently
fail to resolve on REST-deployed pages, so never reintroduce them.

### Editing Open Design project files directly

If iterating on the source design in Open Design itself (not just consuming its output),
use the `write_file` MCP tool for text/HTML/CSS edits — only fall back to a direct disk
copy for binary assets. See `open-design-file-editing` memory note.

## Quick Reference

| Task | Command / Action |
|------|-----------------|
| List design systems | `python .tmp/scripts/open_design_bridge.py list-systems` |
| Copy design system from OD | `python .tmp/scripts/open_design_bridge.py sync-system fracktal-works` |
| Generate page (via OD) | Ask Open Design with `frontend-design` skill |
| **Deploy page (DEFAULT)** | `python .tmp/scripts/open_design_bridge.py deploy-canvas --html <file> --title <title> --slug <slug>` |
| Deploy as Elementor (only if it must be hand-editable in WP) | `python .tmp/scripts/open_design_bridge.py deploy-elementor --html <file> --title <title>` |
| Check fidelity after an Elementor deploy | `python .github/skills/elementor_builder/scripts/verify_fidelity.py --source <file> --live <url>` |
| Deploy raw HTML into normal post_content (legacy, non-canvas) | `python .tmp/scripts/open_design_bridge.py deploy --html <file> --title <title>` |
| Update existing page | Add `--id <page_id>` to the deploy command; `--status publish` to go live |

## Design System Files

Each design system in `agent-data/design-systems/<name>/` contains:
- `DESIGN.md` — Brand contract: colors, typography, voice, components, layout
- `brand.json` — Machine-readable brand data
- `guide.md` — Human-readable brand guide

These are synced from `open-design/design-systems/` and kept as the source of
truth for all WordPress content generation.
