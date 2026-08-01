---
name: elementor_builder
description: >
  Build and edit WordPress pages with Elementor page builder. Manage templates,
  global widgets, theme kits, responsive settings, and custom CSS. Works with
  Elementor's JSON data structure via the WordPress REST API.
when_to_use: "User asks to build or edit Elementor pages, templates, kits, or widgets"
authority: write
cost_tier: 2
version: 0.1.0
---

# Elementor Builder Skill

Build and edit WordPress pages visually using Elementor. Manipulate Elementor's
JSON data structures to create layouts, sections, columns, and widgets. Manage
Elementor templates, kits, global settings, and responsive breakpoints.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_elementor.py` | Elementor page builder operations — templates, kits, widgets, responsive |
| `scripts/html2elementor/` | Deterministic HTML+CSS → Elementor JSON converter (vendored from [dudaster/html2elementor](https://github.com/dudaster/html2elementor)) |
| `scripts/verify_fidelity.py` | Post-import computed-style diff (source HTML vs. live page) — run this instead of a manual Playwright inspection loop |

## Converting HTML/CSS mockups to Elementor (preferred path)

When the source is HTML+CSS — a page from `site_generator`, an AI-generated mockup, a
Tailwind page — **use `scripts/html2elementor/` instead of hand-building or
round-tripping through emcp-tools' `build-page`/`export-page`**. It parses the CSS
cascade locally (no LLM guessing at widget structure) and resolves Elementor's
non-obvious quirks automatically: shared system-color globals bleeding across pages,
lazy-load hiding below-the-fold backgrounds, row-container widths collapsing to 0,
and stale CSS cache after `_elementor_data` updates.

**One-command path (default):** for any HTML file
on disk you want deployed as a new/updated page), use
`.tmp/scripts/open_design_bridge.py deploy-elementor` — it calls this same converter
in-process and also does both import invariants below automatically. See
[html_deploy/SKILL.md](../html_deploy/SKILL.md) for the full
generate → deploy → verify flow. Only use the manual three-step flow below if you need
the intermediate `layout.json`/`kit.json` for inspection, or you're editing the converter
itself.

```bash
# 1. Convert (from repo root; PYTHONPATH must point at scripts/, set PYTHONUTF8=1 on Windows
#    to avoid a cp1252 console crash on the checkmark character in verify.py's output)
PYTHONUTF8=1 PYTHONPATH="./.github/skills/elementor_builder/scripts" \
  ./.venv/Scripts/python -m html2elementor path/to/input.html -o /tmp/layout.json
# add --upload if the HTML references local/relative images to pull into the WP media library

# 2. Verify (structural check: colors/fonts/spacing/max-width match the source cascade)
PYTHONUTF8=1 PYTHONPATH="./.github/skills/elementor_builder/scripts" \
  ./.venv/Scripts/python -m html2elementor.verify path/to/input.html /tmp/layout.json

# 3. Import — two invariants, always:
#    a) merge layout.kit.json's custom_colors/custom_typography into the active kit's
#       _elementor_page_settings (dedupe by _id) — otherwise widgets render with default
#       colors/fonts
#    b) flush Elementor's CSS cache after writing _elementor_data, or changes won't render
```

Full four-step flow, the widget-mapping rules it already handles (styled wrappers,
circular avatars, icon-lists, absolute-positioned overlays, CSS custom properties),
and the Elementor quirks list live in
[`scripts/html2elementor/README.md`](scripts/html2elementor/README.md) — read it
before a non-trivial conversion.

### After conversion: expect a fidelity patch pass

The converter gets structure and most styling right, but real-world source HTML almost
always leaves a residual visual gap against the live render. Don't rediscover this by
manually inspecting the page — run the verification script, which diffs computed styles
between the source and the live page in one deterministic pass:

```bash
python .github/skills/elementor_builder/scripts/verify_fidelity.py \
  --source outputs/design_pages/[slug].html \
  --live https://fracktal.in/[slug]/
```

It targets the 9 recurring drift categories documented in the `elementor-fidelity-patch-workflow`
memory note (heading font-size, counter widgets, button text color, image radius/shadow,
container-width flex-collapse, mojibake arrows, accordion tab typography, full-bleed card
images, CSS pseudo-element overlays) and prints a patch list. Fix via native widget
settings where a setting exists; fall back to scoped Custom CSS (targeted by element
ID/class, not global) only when it doesn't — see the memory note for the exact hybrid
rule and why container widths specifically need Custom CSS instead of native flex
settings.

**Don't use for:** editing pages that are already Elementor (use the REST API /
emcp-tools directly), or plain non-Elementor WordPress pages.

## Usage

```bash
# Check Elementor status
python .github/skills/elementor_builder/scripts/wp_elementor.py --action status

# List Elementor templates
python .github/skills/elementor_builder/scripts/wp_elementor.py --action list-templates

# Get a page's Elementor data
python .github/skills/elementor_builder/scripts/wp_elementor.py --action get-page --id 42

# Create a new Elementor page from a JSON layout
python .github/skills/elementor_builder/scripts/wp_elementor.py --action create-page \
  --title "Landing Page" --layout-file ./layouts/landing.json

# Update Elementor data on an existing page
python .github/skills/elementor_builder/scripts/wp_elementor.py --action update-page \
  --id 42 --layout-file ./layouts/updated.json

# Manage global kit
python .github/skills/elementor_builder/scripts/wp_elementor.py --action kit-export --output ./kit.json
python .github/skills/elementor_builder/scripts/wp_elementor.py --action kit-import --file ./kit.json

# Manage templates
python .github/skills/elementor_builder/scripts/wp_elementor.py --action create-template \
  --name "Hero Section" --type section --layout-file ./hero.json

# Responsive settings
python .github/skills/elementor_builder/scripts/wp_elementor.py --action responsive-check \
  --id 42 --breakpoint mobile
```

## Required Environment Variables

- `WORDPRESS_SITE_URL` — Your WordPress site URL
- `WORDPRESS_USERNAME` — WordPress admin username
- `WORDPRESS_APP_PASSWORD` — WordPress application password

## Elementor JSON Structure

Elementor stores page data as JSON in the `_elementor_data` post meta field.
The structure follows this hierarchy:

```
Page
├── Sections (flexbox rows)
│   ├── Columns (flexbox columns)
│   │   ├── Widgets (text, image, button, heading, etc.)
│   │   │   ├── Settings (content, style, advanced)
│   │   │   └── Elements (nested elements for complex widgets)
```

## Outputs

Writes operation results and layout files to `outputs/<project-slug>/elementor_*.json`.
