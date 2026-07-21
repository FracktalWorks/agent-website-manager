---
name: "fracktal-works-design-analysis"
category: Brands
surface: web
colors:
  canvas: "#ffffff"
  ink-body: "#3c3c3c"
  fracktal-red: "#f25e50"
  dark-band: "#111111"
  ink-muted: "#5a5a5a"
  hairline: "#e6e6e6"
---

# fracktal-works-design-analysis

> Category: Brands

> Surface: web

*Fracktal Works is India's premier 3D printer manufacturer — an Original Additive Manufacturer based in Bangalore since 2013.*

Fracktal Works is India's premier 3D printer manufacturer — an Original Additive Manufacturer based in Bangalore since 2013. We design and build every machine in-house, from desktop precision to production-grade SLS. The voice is confident, direct, and technical — write like an engineer, not a marketer. Use active voice and short declarative sentences. Own the category: "India's premier 3D printer manufacturer." Emphasize indigenous capability: "built in Bangalore," "in-house," "from the ground up," "OAM," "Make in India." Never use words like "cutting-edge," "revolutionary," "ecosystem," "leveraging," or "seamless," and never describe Fracktal as a startup. Every page should pass one test: would an engineer at a world-class manufacturing company trust this?

## Context

**One design language — the default theme.** This document defines a single, consistent language for every Fracktal artifact: a **light canvas**, **Montserrat**, **rounded 6px** corners, **flat** color (no shadows, no gradients), and a single Fracktal-red primary plus standard success / warning / error status colors. The registered **default theme** — `system/kit.html` / `system/tokens.default.json` — is the visual basis; `colors_and_type.css` is the reusable, flat distillation every asset binds to. Where the live site (built by several developers over time) and this document disagree, **this document wins** — rounded, flat, one accent, Montserrat.

**Company.** Fracktal Works (fracktal.in) is a Bangalore additive-manufacturing OEM, founded 2013. It designs and builds its own machines and runs a Bangalore service bureau (FDM, SLS, SLA, MJF, vacuum casting) for automotive, aerospace, medical, dental, and engineering-education customers. Product line: Snowflake (desktop precision FDM), Julia (advanced industrial FDM), Twin Dragon (dual-extruder IDEX FDM), Volterra (high-temperature FFF), Apollo 350 (production-grade SLS, CO₂ laser), and PrintStick (bed adhesion).

**Where it is used.** Marketing site, product pages, spec sheets, IMTEX exhibition collateral, decks, and email. Nav IA: Products · Manufacturing Services · Industries · Materials · Resources.

**Provenance.** Palette and type mirror `system/tokens.default.json` and were cross-checked against the live-site raw HTML (frequency-ranked literals) and the IMTEX brochures. Values not directly measurable are labelled *(inferred)*.

## Color Palette

| Role | Name | Hex | Usage |
| --- | --- | --- | --- |
| background | Canvas | `#ffffff` | primary page surface (light) — measured x91 |
| foreground | Ink body | `#3c3c3c` | body text — measured x21 |
| accent | Fracktal red | `#f25e50` | CTAs, dividers, emphasis only — measured x16 |
| surface | Dark band | `#111111` | near-black technical bands, footer, hero (corrected from phantom #111133) |
| muted | Ink muted | `#5a5a5a` | secondary text, metadata, overline — measured x4 |
| border | Hairline | `#e6e6e6` | dividers on white (inferred) |

## Typography
- **Display:** Montserrat — weights 400, 700 — fallbacks: system-ui, -apple-system, Segoe UI, Helvetica Neue, Arial, sans-serif
- **Body:** Montserrat — weights 400, 700 — fallbacks: system-ui, -apple-system, Segoe UI, Helvetica Neue, Arial, sans-serif

## Voice & Tone

- **Adjectives:** confident, technical, direct, indigenous, precise, understated
- **Tone:** Confident, direct, and technical — write like an engineer, not a marketer. Active voice, short declarative sentences.

### Messaging pillars
- Indigenous OEM — Fracktal designs and builds every machine in-house in Bangalore since 2013, from desktop precision (Snowflake) to production-grade SLS (Apollo 350). No imported kits, no rebadging.
- Production-grade, proven — real specs over adjectives: build volumes, speeds, temperatures, and named programs (MHI Capital Goods Scheme, IISc/FSID). Every page passes one test: would an engineer at a world-class manufacturing company trust this?

### Vocabulary
- **Use:** India's premier 3D printer manufacturer, Original Additive Manufacturer (OAM), built in Bangalore, in-house, from the ground up, Make in India, production-grade, indigenous engineering
- **Avoid:** cutting-edge, revolutionary, ecosystem, leveraging, seamless, unprecedented, game-changing, startup

## Imagery

- **Style:** real product photography of actual machines — never AI-generated, never stock illustration
- **Subjects:** Fracktal 3D printers (Snowflake, Julia, Twin Dragon, Volterra, Apollo 350), printed parts, Bangalore facility, IMTEX exhibition stand
- **Treatment:** large, full-bleed, high-contrast, often on near-black/industrial backgrounds so the machine reads as hero content; minimal retouching; light wordmark on dark imagery, dark wordmark on white
- **Avoid:** AI-generated renders, glossy 3D mockups, generic gradient hero art, stock illustration, emoji or clip-art icons

## Layout

- **Radius:** 6px
- **Border weight:** 1px
- **Spacing:** 4px

### Posture rules
- Component kit should cover: button-primary, button-outline, button-white, button-sm, card-dark, card-light, product-card, hero-section, section-header, divider, cta-banner, Background.

## Components

Rounded (6px), flat, default-theme kit (states: default · hover · active · focus · disabled). Reference: `colors_and_type.css`, `preview/components-buttons.html`, `ui_kits/app/`. UI + status icons come from **Lucide**.

- **button-primary** — accent fill `#f25e50`, white text, 6px radius; hover `#ff8d7d`, active `#cc4139`; disabled `#f3f3f3` fill / `#919191` text.
- **button-outline** (default) — white fill, 1px `#e6e6e6` border, ink text; hover → accent border + text.
- **button-dashed / text / link** — secondary affordances; link uses accent text.
- **button-white / on-dark** — for use on a dark band.
- **button-sm / lg** — 28px / 44px control heights (36px default).
- **alert** — success / warning / error / info: status-tinted background, 1px status border, 6px radius, a **Lucide** status icon (`circle-check`, `triangle-alert`, `circle-x`, `info`).
- **progress** — rounded pill track (`#f3f3f3`) + accent or status fill.
- **card-light** — white, 1px `#e6e6e6`, 6px radius, flat. **card-dark** — near-black band, white text.
- **product-card**, **hero-section**, **section-header** (overline + heading + accent rule), **divider**, **cta-banner**.
- **input / select** — 36px height, 6px radius, 1px border, accent focus ring. **tag / pill**, **spec table** (ruled rows, mono tabular numerics).

## Motion

Restrained and conventional — quick, decisive transitions on state change; nothing decorative.

- **Durations:** fast `100ms` (hover/press), base `200ms` (toggles, dropdowns), slow `300ms` (reveals / progress).
- **Easing:** `cubic-bezier(0.645, 0.045, 0.355, 1)` — the default theme's ease.
- **Animate:** color/border on interactive states, dropdown and mobile-nav open/close, progress fills. Honor `prefers-reduced-motion`.
- **Do not animate:** no parallax, no auto-playing carousels, no decorative looping.

## Anti-patterns

- Never add drop shadows or gradients — the system is flat. Depth is borders + color.
- Keep rounding at 6px (scale 2/4/6/8); do not reintroduce hard 0px corners and do not pill-round cards/buttons.
- The brand red is the only decorative accent; status colors (green / amber / red) are functional only — alerts, progress, validation — never a decorative wash.

## Elementor-safe authoring (when the output will be converted to Elementor)

Every page built from this design system eventually gets converted to an Elementor page
via `html2elementor`. That converter parses CSS deterministically but cannot represent
everything HTML/CSS can — using the patterns below produces layouts that need little to
no post-import patching; using their alternatives guarantees a fidelity-patch pass.

- **No `::before`/`::after` for structural or decorative content** (texture overlays,
  icon insertion, decorative bars). Elementor widgets have no pseudo-element concept —
  render the element directly in the markup instead (a real `<div>`/`<img>` in the DOM).
- **No CSS Grid with non-uniform tracks** (e.g. `grid-template-columns: 2fr 1fr`).
  Use nested flex rows/columns with explicit `%` widths instead — this is what the
  converter maps to Elementor's native row/column model.
- **Avoid relying on flex `grow`/`shrink` alone for fixed-width columns in a row.**
  Elementor's row-container width calculation collapses in this case (a documented
  converter/Elementor limitation). Set explicit `flex-basis`/`width` percentages on
  each column instead of `flex: 1`.
- **Images that must fill their container** (full-bleed card thumbnails) should set
  `width:100%; height:100%; object-fit:cover` on the `<img>` itself, not rely on a
  wrapper `div` to stretch it — Elementor's image-widget wrapper stays content-width.
- **No `@media` queries for anything beyond simple stacking** (row → column below a
  breakpoint). The converter does not read responsive breakpoints; author the desktop
  layout as the source of truth and let Elementor's own responsive controls handle
  mobile, or keep breakpoint logic to a single stack/no-stack toggle.
- **Use real HTML entities for typographic punctuation** (`&rarr;`, `&mdash;`, `&nbsp;`)
  rather than raw UTF-8 arrow/dash characters — avoids double-encoding (mojibake) across
  the HTML → JSON → REST API round trip.
- Montserrat only; ship the declared fallback stack; never let the font silently fall back to Arial.
- Engineer's voice — no marketing adjectives or the avoid-words list, and never call Fracktal a "startup."
- Real product photography only; never AI-generated; never use the partner-logo images (`hero-4`, `hero-5`, `hero-7`) as product shots. Use Lucide icons, not emoji.
