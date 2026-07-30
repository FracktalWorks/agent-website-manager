---
name: fracktal-works-design-analysis
description: Brand design system for Fracktal Works (India's premier 3D printer manufacturer). Light canvas, Montserrat, rounded (6px) and flat, with a single Fracktal-red primary plus standard success/warning/error status colors. Use when designing any Fracktal web page, product page, spec sheet, deck, or email so color, type, voice, and components stay on-brand.
user-invocable: true
---

# Fracktal Works — Design System Skill

## What is inside

A complete, reusable brand package:

- **`DESIGN.md`** — canonical rules: context, color palette (with OKLCH + provenance), typography, layout/spacing, component kit with states, motion, voice & vocabulary, imagery, best practices, anti-patterns, and a provenance/caveats log.
- **`colors_and_type.css`** — import-first token sheet: color, type scale, spacing, radius, motion tokens, and `.fk-*` helper classes (buttons, cards, overline, rule). Binds Montserrat via Google Fonts.
- **`brand.json`** — machine-readable record (colors+OKLCH, typography, voice adjectives/tone/vocabulary, imagery rules, layout).
- **`preview/`** — seven focused review cards (colors, neutrals, typography, spacing, radius, components, brand assets).
- **`ui_kits/app/`** — an assembled Fracktal product interface that consumes the tokens, plus its own README.
- **`logos/`, `imagery/`, `assets/`** — real wordmarks, real product photography, and source collateral (IMTEX brochures).
- **`README.md`** — package overview, Preview Manifest, and reuse workflow.

## Source context

- **Brand:** Fracktal Works — Original Additive Manufacturer, Bangalore, since 2013. Designs and builds its own machines (Snowflake, Julia, Twin Dragon, Volterra, Apollo 350, PrintStick) and runs a service bureau (FDM, SLS, SLA, MJF, vacuum casting).
- **Source:** https://www.fracktal.in/ (re-measured 2026-06-30) + IMTEX brochures in `assets/`.
- **Canonical posture:** this package adopts the registered **default theme** — light canvas, Montserrat, rounded **6px**, flat (no shadows/gradients), brand red primary plus success/warning/error status colors. (An earlier exploration used a sharp 0px / dark-contrast look from the live site; it is superseded.)

## When to use this skill

Use it for **any Fracktal Works artifact**: marketing/product pages, spec sheets, landing pages, decks, emails, or UI mockups. It answers, without re-asking: what colors, what type, what radius/spacing, what the voice is, which words to avoid, and what imagery is allowed.

Do **not** use it to invent a full dark page background, a second decorative accent hue, shadowed or gradient-filled cards, or AI-generated product imagery — those are explicit anti-patterns. (Rounded 6px corners are correct; shadows are not.)

## How to use

1. **Bind tokens first:** `<link rel="stylesheet" href="colors_and_type.css">` (path-adjust as needed). Reference `var(--accent)`, `var(--ink-body)`, `var(--canvas-dark)`, the `--space-*` / `--fs-*` scales, and `.fk-btn` / `.fk-card` / `.fk-overline` / `.fk-rule`.
2. **Read `DESIGN.md`** for posture and do/don't rules (rounded 6px, flat, accent budget, voice, imagery).
3. **Copy patterns from `ui_kits/app/index.html`** and isolate tokens from `preview/*`.
4. **Use real assets** from `logos/` (light wordmark on dark, dark wordmark on white) and `imagery/`. Note: `imagery/hero-4.png`, `hero-5.png`, `hero-7.png` are **government/partner logos, not product photos** — do not use them as product imagery.
5. **Stay on voice** with `brand.json → voice.vocabulary` (use/avoid).

## Design system highlights

- **Color:** white canvas `#ffffff`; optional dark band `#111111`; ink ramp `#252525 / #3c3c3c / #5a5a5a`; one brand accent `#f25e50` (hover `#ff8d7d`, active `#cc4139`) plus standard success/warning/error status colors.
- **Type:** Montserrat — 700 headings, 400 body; monospace tabular numerics for specs.
- **Geometry:** rounded 6px (scale 2/4/6/8), 1px rules, no shadows, no gradients (flat). Depth = borders + color.
- **Spacing:** 4px base; 80/60px section rhythm; 32px card padding.
- **Voice:** confident, technical, direct — engineer, not marketer. Real specs over adjectives.
- **Imagery:** real product photography only — never AI-generated.
