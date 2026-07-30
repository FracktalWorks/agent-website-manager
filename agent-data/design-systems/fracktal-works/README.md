# Fracktal Works — Design System

A versioned, reusable brand design-system package for **Fracktal Works**, India's premier 3D printer manufacturer. This package bundles tokens, typography, components, preview cards, an applied UI kit, provenance, and the real source assets needed to drive a new, on-brand HTML deliverable without re-asking for direction.

- **Slug:** `fracktal-works-design-analysis` (`user:fracktal-in`)
- **Source:** https://www.fracktal.in/ (re-measured 2026-06-30) + IMTEX brochures in `assets/`
- **Surface:** web · **Category:** Brands
- **Canonical truth:** [`DESIGN.md`](DESIGN.md) for rules, [`colors_and_type.css`](colors_and_type.css) for tokens.

## Product Overview

Fracktal Works (Bangalore, founded 2013) is an **Original Additive Manufacturer (OAM)** — it designs and builds every machine in-house, from the ground up. It also runs a Bangalore service bureau offering FDM, SLS, SLA, MJF, and vacuum casting for automotive, aerospace, medical, dental, and engineering-education customers.

**Product line** (used as real copy throughout the kit):

| Product | Class | Note |
| --- | --- | --- |
| Snowflake | Desktop precision FDM | Entry / education |
| Julia | Advanced industrial FDM | Workhorse |
| Twin Dragon | Dual-extruder IDEX FDM | 300/500/600 variants, up to 600×600×400mm, 500 mm/sec |
| Volterra | High-temperature FFF | Engineering polymers |
| Apollo 350 | Production-grade SLS | CO₂ laser; "India's most advanced SLS 3D Printer"; MHI Capital Goods Scheme w/ IISc + FSID |
| PrintStick | Bed adhesion | Accessory |

**Voice:** confident, technical, direct — write like an engineer, not a marketer. Own the category ("India's premier 3D printer manufacturer"), emphasize indigenous capability ("built in Bangalore," "in-house," "from the ground up," "Make in India"). The test for every page: *would an engineer at a world-class manufacturing company trust this?*

## The design system in one paragraph

**Light canvas, Montserrat, rounded and flat, one brand red + status colors.** White (`#ffffff`) is the primary surface, with an optional near-black (`#111111`) band for footers/heroes. Fracktal red (`#f25e50`, hover `#ff8d7d`, active `#cc4139`) is the brand primary; standard success/warning/error colors cover state. Typography is Montserrat — **700** headings, **400** body — with monospace tabular numerics for specs. The system is **rounded (6px)** and **flat**: no shadows, no gradients, **1px** rules. This is the registered **default theme** (`system/kit.html` / `tokens.default.json`); `colors_and_type.css` is its reusable distillation.

> The design language is the registered **default theme** — rounded (6px), flat, light, Montserrat. An earlier exploration matched the live site's sharper, higher-contrast look; it is superseded. The website mixes styles (built by several developers); this document does not. See `DESIGN.md → Context`.

## Package contents

```
DESIGN.md                 Canonical rules: context, color, type, layout, components, motion, voice, imagery, anti-patterns, provenance
colors_and_type.css       Reusable tokens (color, type, spacing, radius, motion) + helper classes. Import this first.
brand.json                Machine-readable brand record (colors+OKLCH, type, voice, vocabulary, imagery, layout)
guide.md                  Short brand guide
README.md                 This file
SKILL.md                  Agent-facing usage instructions

preview/                  Focused review cards (see Preview Manifest)
ui_kits/app/              Applied product interface + README, binds to ../../colors_and_type.css

logos/                    Real wordmarks + favicons (Website-Header_black.png, Websitesd-Header.png, favicon-*.png)
imagery/                  Real product photography (cover-0.webp, hero-1..7) — never AI-generated
assets/                   Source collateral — assets/Fracktal-IMTEX-Brochures-A5---Twin-Dragon.pdf, stall/wall graphics PDFs (preserved brand evidence)
context/                  Source notes + original input analysis (provenance)
system/                   Generated antd kit + tokens (kit.html, variables*.css, tokens.*.json, artifacts/). Retained for reference; see caveat below.
```

## Preview Manifest

Open any card directly in a browser; each links `../colors_and_type.css`.

| Card | Shows |
| --- | --- |
| `preview/colors-primary.html` | Accent + functional palette, with provenance per swatch |
| `preview/colors-neutrals.html` | Canvas, ink ramp, and the near-black dark band |
| `preview/typography-specimens.html` | Montserrat scale display→overline, weights 400/500/600/700, mono numerics |
| `preview/spacing-tokens.html` | 4px-base spacing scale + section/card rhythm, to scale |
| `preview/radius-shadows.html` | Rounded radius scale (2/4/6/8); flat — no shadows |
| `preview/components-buttons.html` | Buttons, cards (light/dark), input/select, status pills, spec table |
| `preview/brand-assets.html` | Real preserved logos + product photography via `<img>` |

## Applied UI kit

`ui_kits/app/index.html` composes a real Fracktal product surface — sticky nav (Products · Manufacturing Services · Industries · Materials · Resources), a dark hero band, a product grid with category filtering, a Twin Dragon spec table, a red CTA banner, and a dark footer — all bound to `../../colors_and_type.css`. See `ui_kits/app/README.md` for structure and source basis.

## Reuse workflow

1. **Import tokens first:** `<link rel="stylesheet" href="colors_and_type.css">` (or `@import`). Use `var(--accent)`, `var(--ink-body)`, `var(--canvas-dark)`, the spacing/type scales, and the `.fk-*` helpers.
2. **Read `DESIGN.md`** for posture and the do/don't rules (rounded 6px, flat, accent budget, voice, imagery).
3. **Reference `ui_kits/app/`** for an assembled example and `preview/*` for isolated token specimens.
4. **Use real assets** from `logos/` and `imagery/` — never substitute AI-generated product imagery.
5. **Stay on voice:** use the `brand.json → voice.vocabulary` use/avoid lists.

## Provenance & caveats

- **Measured** (live-site raw HTML, frequency-ranked literals; IMTEX brochures): palette literals, Montserrat dominance (~397× vs Inter 57×), product names/specs, site IA.
- **Inferred** (labelled in `DESIGN.md`): hairline `#e6e6e6`, accent tint, functional status colors, exact component radii/padding — the live site renders client-side (Wix), so its computed component CSS was not directly readable.
- **Fonts:** Montserrat is bound via Google Fonts in `colors_and_type.css`; the source exposed no local font files, so there is no `fonts/` directory.
- **No `build/` or `source_examples/`:** the evidence included no runtime build assets or substantial app/component source to preserve.
- **`system/` default theme is the styling reference:** `system/kit*.html`, `system/variables*.css`, and `system/tokens.*.json` define the rounded (6px) antd `default theme` this package aligns to; `colors_and_type.css` is its flat (no-shadow) distillation. `brand.html` is a separate scaffold that uses an off-brand red (`#c96442`) — ignore it.
