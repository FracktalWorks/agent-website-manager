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
