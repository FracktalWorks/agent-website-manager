---
version: alpha
name: fracktal-works-design-analysis
description: |
  Fracktal Works is India's premier 3D printer manufacturer — an Original Additive Manufacturer based in Bangalore since 2013. The design system is dark-native, technical, and confident, built on a single red accent (`#F25E50`) against deep navy-black canvases (`#0a0a1a`). Typography is Montserrat at weights 700/400, creating an engineered, anti-decorative hierarchy. The system is flat — no shadows, no gradients, no decorative elements. Contrast between dark and light section bands creates the depth. Product imagery is treated as hero content: large, full-bleed photographs of real machines. The voice is direct and technical: write like an engineer, not a marketer.

colors:
  canvas: "#0a0a1a"
  canvas-light: "#FFFFFF"
  surface-dark: "#111133"
  surface-light: "#f8f8fc"
  ink: "#FFFFFF"
  ink-light: "#CFCFCF"
  ink-muted: "#CCCCCC"
  ink-dark: "#3c3c3c"
  body: "#666666"
  overline: "#5A5A5A"
  accent: "#F25E50"
  accent-hover: "#d94a3d"
  hairline: "rgba(255,255,255,0.08)"
  on-accent: "#FFFFFF"

typography:
  heading-display:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 48px
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: 0
  heading-lg:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: 0
  heading-md:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 22px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: 0
  heading-sm:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 20px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: 0
  body-lg:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: 0
  body-md:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: 0
  body-sm:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: 0
  button:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 15px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0
  button-sm:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0
  overline-sm:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  display-mobile:
    fontFamily: "Montserrat, system-ui, sans-serif"
    fontSize: 26px
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: 0

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 20px
  xl: 24px
  xxl: 32px
  section: 80px
  section-mobile: 60px
  card-gap: 30px
  card-padding: 32px
  hero: "5% 0 5% 8%"

rounded:
  none: 0px
  sm: 4px
  md: 8px
  full: 9999px

components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    typography: "{typography.button}"
    rounded: "{rounded.sm}"
    padding: "14px 28px"
    hover: "{colors.accent-hover}"
  button-outline:
    backgroundColor: transparent
    textColor: "{colors.ink}"
    border: "1px solid {colors.accent}"
    typography: "{typography.button}"
    rounded: "{rounded.sm}"
    padding: "14px 28px"
  button-white:
    backgroundColor: "{colors.canvas-light}"
    textColor: "{colors.accent}"
    typography: "{typography.button}"
    rounded: "{rounded.sm}"
    padding: "14px 28px"
  button-sm:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    typography: "{typography.button-sm}"
    rounded: "{rounded.sm}"
    padding: "10px 20px"
  card-dark:
    backgroundColor: "{colors.surface-dark}"
    rounded: "{rounded.md}"
    padding: "{spacing.card-padding}"
  card-light:
    backgroundColor: "{colors.surface-light}"
    rounded: "{rounded.md}"
    padding: "{spacing.card-padding}"
  product-card:
    backgroundColor: "{colors.surface-dark}"
    rounded: "{rounded.md}"
    padding: "0 0 30px 0"
    overflow: hidden
  hero-section:
    backgroundColor: "{colors.canvas}"
    minHeight: "90vh"
    layout: "55/45 split"
  section-header:
    textAlign: center
    marginBottom: 50px
  divider:
    width: 60px
    height: 3px
    backgroundColor: "{colors.accent}"
  cta-banner:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.ink}"
    padding: "60px {spacing.md}"
    textAlign: center
---

# Design System Inspired by Fracktal Works

> **Category**: Manufacturing & Industrial 3D Printing
> **Source**: https://fracktal.in/
> **Font**: Montserrat (Google Fonts)
> **Last updated**: 2026-06-30

## Overview

Fracktal Works is India's premier 3D printer manufacturer — an Original Additive Manufacturer based in Bangalore since 2013. The design system is dark-native, technical, and confident. A near-black canvas (`{colors.canvas}`) serves as the primary surface, with content emerging through high-contrast white (`{colors.ink}`) and cool gray (`{colors.ink-light}`) text. The brand's signature red (`{colors.accent}`) is the **sole chromatic accent** — reserved exclusively for CTAs, section dividers, and key emphasis points. White sections (`{colors.canvas-light}`) provide breathing room between dark content bands.

The typography system is built entirely on **Montserrat** — a geometric sans-serif that communicates precision and engineering discipline. Headings use weight 700 at large sizes; body text uses weight 400 at 14–16px. The typographic hierarchy feels engineered rather than decorative.

The system is **flat** — no shadows, no gradients, no decorative elements. Depth comes from color contrast: dark sections alternating with light sections. Product imagery is treated as hero content — large, full-bleed photographs of real machines dominate the visual landscape. Cards are distinguished by background color alone, not by elevation.

**Voice**: Confident, technical, direct. Write like an engineer, not a marketer. Active voice. Short declarative sentences. Own the category: "India's premier 3D printer manufacturer."

## Colors

### Canvas & Surfaces
- `{colors.canvas}` (`#0a0a1a`): Hero sections, dark content bands. The primary canvas.
- `{colors.canvas-light}` (`#FFFFFF`): Light section backgrounds. Breathing room between dark bands.
- `{colors.surface-dark}` (`#111133`): Elevated cards on dark backgrounds.
- `{colors.surface-light}` (`#f8f8fc`): Subtle card backgrounds on light sections.

### Brand Accent
- `{colors.accent}` (`#F25E50`): **The only chromatic color.** CTAs, section dividers, H3 headings on dark backgrounds, button backgrounds.
- `{colors.accent-hover}` (`#d94a3d`): Button hover state — darken by 10%.
- `{colors.on-accent}` (`#FFFFFF`): Text on accent backgrounds.

### Text
- `{colors.ink}` (`#FFFFFF`): Primary text on dark backgrounds. Not pure white — minimal eye strain.
- `{colors.ink-light}` (`#CFCFCF`): Secondary/body text on dark backgrounds. Cool silver-gray.
- `{colors.ink-muted}` (`#CCCCCC`): Card body text on dark backgrounds. Most subdued readable gray.
- `{colors.ink-dark}` (`#3c3c3c`): Primary heading color on light backgrounds. Near-black.
- `{colors.body}` (`#666666`): Body text on light backgrounds.
- `{colors.overline}` (`#5A5A5A`): Section overline labels.

### Dividers
- `{colors.accent}` (`#F25E50`): 60px × 3px centered section dividers.
- `{colors.hairline}`: 1px semi-transparent borders on outline buttons.

## Typography

| Token | Font | Size | Weight | Line | Use |
|---|---|---|---|---|---|
| `{typography.heading-display}` | Montserrat | 48px | 700 | 1.15 | H1 — hero headlines, dark backgrounds. `{typography.display-mobile}` (26px) on mobile. |
| `{typography.heading-lg}` | Montserrat | 32px | 700 | 1.2 | H2 — section titles, both light and dark backgrounds. |
| `{typography.heading-md}` | Montserrat | 22px | 700 | 1.3 | H3 — card titles on dark backgrounds. Color: `{colors.accent}`. |
| `{typography.heading-sm}` | Montserrat | 20px | 700 | 1.3 | H3 — card titles on light backgrounds. Color: `{colors.ink-dark}`. |
| `{typography.body-lg}` | Montserrat | 16px | 400 | 1.7 | Large body — hero descriptions, CTA sections. |
| `{typography.body-md}` | Montserrat | 15px | 400 | 1.6 | Standard body — section descriptions, story text. |
| `{typography.body-sm}` | Montserrat | 14px | 400 | 1.6 | Small body — card descriptions, fine print. |
| `{typography.button}` | Montserrat | 15px | 600 | 1.0 | Primary and outline button text. |
| `{typography.button-sm}` | Montserrat | 13px | 600 | 1.0 | Small button text — product card CTAs. |
| `{typography.overline-sm}` | Montserrat | 14px | 400 | 1.4 | Section overline labels. Color: `{colors.overline}`. |
| `{typography.display-mobile}` | Montserrat | 26px | 700 | 1.15 | H1 — mobile breakpoint. |

## Layout

### Spacing System
- **Base unit**: 4px (8px primary increment).
- **Tokens**: `{spacing.xxs}` (4px) · `{spacing.xs}` (8px) · `{spacing.sm}` (12px) · `{spacing.md}` (16px) · `{spacing.lg}` (20px) · `{spacing.xl}` (24px) · `{spacing.xxl}` (32px) · `{spacing.section}` (80px) · `{spacing.section-mobile}` (60px).
- **Section rhythm**: Every major content band uses `{spacing.section}` (80px) vertical padding on desktop, `{spacing.section-mobile}` (60px) on mobile. Sections never butt against each other — the white/light alternating bands create natural visual separation.
- **Card grids**: `{spacing.card-gap}` (30px) between cards in a row. Cards internally padded at `{spacing.card-padding}` (32px).
- **Hero padding**: `{spacing.hero}` — 5% top, 0 right, 5% bottom, 8% left on the text column.

### Max Width & Grid
- **Max content width**: 1200px for boxed containers. Hero sections are full-width.
- **Hero grid**: 55% text column / 45% image column. Flexbox, `flex-direction: row` on desktop, `column` on mobile.
- **Card grid**: 3-column on desktop (>900px), 2-column on tablet (600–900px), 1-column on mobile (<600px).
- **Story grid**: 50/50 two-column with `{spacing.xxl}` gap.

### Whitespace Philosophy
Whitespace is structural, not decorative. Sections are separated by alternating background colors (dark → light → dark) rather than empty bands. Cards are distinguished by background-color contrast, not by shadows or elevation. The sense of air comes from generous `{spacing.section}` padding and the breathing room of `{colors.canvas-light}` bands between dark chapter blocks.

### Alignment
- Hero text: left-aligned on desktop, center-aligned on mobile.
- Section headers: centered (H2 + divider + optional subtitle).
- Card content: centered within cards.
- Buttons in hero: left-aligned row on desktop, stacked full-width column on mobile.

## Elevation & Depth

Fracktal's design is **entirely flat**. There is no shadow system, no elevation scale, no layered depth.
- Cards are distinguished by background color alone: `{colors.surface-dark}` against `{colors.canvas}`, or `{colors.surface-light}` against `{colors.canvas-light}`.
- Section dividers (`{colors.accent}`, 60px × 3px) mark transitions, not drop shadows.
- Depth is created through **color contrast**: the alternation of dark and light section bands.
- If forced to use elevation: `box-shadow: 0 2px 8px rgba(0,0,0,0.1)` sparingly, never on hero sections.

## Shapes

| Token | Value | Use |
|---|---|---|
| `{rounded.none}` | 0 | Hero sections, full-width banners |
| `{rounded.sm}` | 4px | All buttons — primary, outline, white, small |
| `{rounded.md}` | 8px | Cards — dark, light, product. Story images. |
| `{rounded.full}` | 9999px | Not used — the design is angular and technical |

## Components

### Top Navigation
Not defined — Fracktal's WordPress theme provides the navigation shell. Generated pages are embedded within WordPress and inherit its header, footer, and menu.

### Buttons

**`button-primary`** — The main CTA. Red fill, white text.
- Background `{colors.accent}`, text `{colors.on-accent}`, rounded `{rounded.sm}`, padding 14px 28px, type `{typography.button}`.
- Hover: `{colors.accent-hover}`. Transition: 200ms ease.

**`button-outline`** — Secondary CTA on dark backgrounds. Transparent with red border.
- Background transparent, text `{colors.ink}`, border `1px solid {colors.accent}`, rounded `{rounded.sm}`, padding 14px 28px, type `{typography.button}`.
- Hover: background `rgba(242,94,80,0.1)`.

**`button-white`** — Used on `{colors.accent}` CTA banners. White fill, red text.
- Background `{colors.canvas-light}`, text `{colors.accent}`, rounded `{rounded.sm}`, padding 14px 28px, type `{typography.button}`.
- Hover: background `#f0f0f0`.

**`button-sm`** — Small CTA for product cards and link cards.
- Background `{colors.accent}`, text `{colors.on-accent}`, rounded `{rounded.sm}`, padding 10px 20px, type `{typography.button-sm}`.

### Cards & Containers

**`card-dark`** — Standard card on dark backgrounds.
- Background `{colors.surface-dark}`, rounded `{rounded.md}`, padding `{spacing.card-padding}` (32px). Text centered.
- Icon (64px square) at top, H3 in `{typography.heading-md}` color `{colors.accent}`, body in `{typography.body-sm}` color `{colors.ink-muted}`.

**`card-light`** — Standard card on light backgrounds.
- Background `{colors.surface-light}`, rounded `{rounded.md}`, padding `{spacing.card-padding}` (32px). Text centered.
- H3 in `{typography.heading-sm}` color `{colors.ink-dark}`, body in `{typography.body-sm}` color `{colors.body}`.

**`product-card`** — Product showcase card on dark backgrounds.
- Background `{colors.surface-dark}`, rounded `{rounded.md}`, overflow hidden. No top padding — product image sits flush with card top.
- Top: product image, `width: 100%`, `aspect-ratio: 1`, `object-fit: cover`.
- Body padding: 25px 20px 30px. H3 in `{typography.heading-sm}` color `{colors.ink}`, body in `{typography.body-sm}` color `{colors.ink-light}`, `{button-sm}` CTA.

**`hero-section`** — Full-width hero block.
- Background `{colors.canvas}`, min-height 90vh. Flexbox row, content-position middle.
- Left column (55%): H1 `{typography.heading-display}` color `{colors.ink}`, body `{typography.body-lg}` color `{colors.ink-light}`, 2 CTA buttons in a row with `{spacing.md}` gap.
- Right column (45%): hero image, `width: 100%`, `height: 100%`, `object-fit: cover`.
- Mobile: stacked vertically. Text column padding `15% 5% 5% 5%`, text centered.

**`section-header`** — Universal section heading block.
- Text align center, margin bottom 50px.
- H2 in `{typography.heading-lg}` color `{colors.ink}` (dark bg) or `{colors.ink-dark}` (light bg).
- `{divider}`: 60px × 3px `{colors.accent}`, centered.
- Optional subtitle in `{typography.body-md}` color `{colors.ink-light}` or `{colors.body}`.

**`cta-banner`** — Full-width call-to-action strip.
- Background `{colors.accent}`, padding 60px `{spacing.md}`, text centered.
- H2 in `{typography.heading-lg}` color `{colors.ink}`, body in `{typography.body-lg}` color `{colors.ink}` (85% opacity), `{button-white}` CTA.

**`story-section`** — Split image + text layout on light background.
- Background `{colors.canvas-light}`, padding `{spacing.section}` `{spacing.md}`.
- Two-column grid: 50/50 with `{spacing.xxl}` gap, `align-items: center`.
- Left: large image, `width: 100%`, rounded `{rounded.md}`.
- Right: H2 `{typography.heading-lg}` color `{colors.ink-dark}`, `{divider}` (left-aligned), body `{typography.body-md}` color `{colors.body}`, `{button-primary}` CTA.
- Mobile: single column, image above text.

### Links
**`link-card`** — Navigation link card on dark backgrounds.
- Background `{colors.surface-dark}`, rounded `{rounded.md}`, padding 30px 20px, text centered.
- H3 in `{typography.heading-sm}` color `{colors.ink}`, body in `{typography.body-sm}` color `{colors.ink-muted}`, `{button-sm}` CTA linking to target page.

## Do's and Don'ts

### Do
- Use `{colors.accent}` **only** for CTAs, dividers, and accent headings — never for body text or backgrounds outside CTA banners
- Use `{colors.canvas}` (dark) for heroes and product sections
- Use `{colors.canvas-light}` (white) for story sections and breathing room between dark bands
- Use real Fracktal product photography — never stock or AI-generated imagery. Reference images from the WordPress media library at `https://fracktal.in/wp-content/uploads/`
- Left-align hero text on desktop (center on mobile)
- Use `{typography.heading-display}` / `{typography.body-lg}` pairing in heroes
- Keep cards flat — `{rounded.md}` maximum
- Use active voice: "We design, engineer, and manufacture"
- Use the exact WordPress-hosted image URLs listed in Agent Prompt Guide — they are on the same domain, no CORS issues

### Don't
- Don't use multiple accent colors — `{colors.accent}` is the ONLY chromatic accent in the system
- Don't use light backgrounds for hero sections — always `{colors.canvas}`
- Don't use gradients, heavy box-shadows, or decorative overlays
- Don't center-align hero text on desktop — left-aligned only
- Don't use border-radius larger than `{rounded.md}` (8px)
- Don't describe Fracktal as a "startup" or "small company" — position as India's premier manufacturer
- Don't use AI-generated product imagery
- Don't use these words: "cutting-edge", "revolutionary", "ecosystem", "leveraging", "seamless", "unprecedented"

## Responsive Behavior

### Breakpoints
- **Desktop**: >900px — hero 55/45 split, 3-column card grids, full `{spacing.section}` padding
- **Tablet**: 600–900px — hero stacked, 2-column card grids, `{spacing.section-mobile}` padding
- **Mobile**: <600px — single column, buttons full-width, `{typography.display-mobile}` for H1, reduced section padding

### Touch Targets
- Minimum 44×44px for all interactive elements (buttons, links)
- Buttons expand to full width on mobile

### Collapsing Strategy
- Hero: 55/45 split → stacked (text above image)
- Card grids: 3-col → 2-col → 1-col
- Button rows: side-by-side → stacked full-width
- Navigation: inherited from WordPress theme (not defined here)

### Image Behavior
- Images: always `width: 100%`, `object-fit: cover`
- Hero images: `min-height: 90vh` on desktop → `min-height: 40vh` on mobile
- Product card images: `aspect-ratio: 1`
- Story section images: `border-radius: {rounded.md}`

## Iteration Guide

When extending or modifying pages built with this system:
1. **Start from the design tokens** — every component references `{colors.xxx}`, `{spacing.xxx}`, `{typography.xxx}`. Change the token, change everywhere.
2. **Add new components below** — define them with token references, not hardcoded values.
3. **Keep the accent pure** — `{colors.accent}` is the only chromatic color. If you need a new color, it should be a neutral (gray, white, black).
4. **Test on dark and light** — every component should work on both `{colors.canvas}` and `{colors.canvas-light}`.
5. **Image quality** — product images should be WebP format, from the WordPress media library, at least 1080px wide.
6. **Voice consistency** — every heading and body copy should pass the filter: "Would an engineer at an Indian manufacturing company trust this?"

## Known Gaps

- **Navigation**: Header, footer, and menu are inherited from the WordPress theme — not defined in this design system. Generated pages embed within WordPress via Elementor HTML widgets.
- **Forms & Inputs**: Not yet defined. Fracktal primarily uses Contact Form 7 or third-party form solutions.
- **Data Tables**: Not defined. Product comparison tables follow the general card and typography rules.
- **Animation**: Minimal — only 200ms button hover transitions. No page-load animations, scroll effects, or motion design defined.
- **Dark mode toggle**: Not supported. The system is dark-native with light section bands for contrast — there is no alternative color scheme.
- **Multi-language**: The WordPress site supports English only. No RTL or i18n design considerations.

## Agent Prompt Guide

### Quick Token Reference
```
Canvas: {colors.canvas} (#0a0a1a) | Light bg: {colors.canvas-light} (#FFFFFF)
Cards: {colors.surface-dark} (#111133) | Light cards: {colors.surface-light} (#f8f8fc)
Red: {colors.accent} (#F25E50) | Red hover: {colors.accent-hover} (#d94a3d)
Text on dark: {colors.ink} (#FFF) | Secondary: {colors.ink-light} (#CFCFCF)
Text on light: {colors.ink-dark} (#3c3c3c) | Body: {colors.body} (#666)
Spacing: section={spacing.section} card-gap={spacing.card-gap}
Font: Montserrat 700/400 | H1=48px | H2=32px | Body=15-16px
```

### Ready-to-use prompts (copy-paste these into any coding agent)
```
1. "Build a hero section: {hero-section} with H1 '{typography.heading-display}' in
   '{colors.ink}', body '{typography.body-lg}' in '{colors.ink-light}', two buttons
   — {button-primary} and {button-outline} side by side. Right column: product image."

2. "Create {card-dark} ×3 in a row on {colors.canvas} bg with {spacing.card-gap}
   gap. Each card: 64px icon, H3 in {typography.heading-md} color {colors.accent},
   body in {typography.body-sm} color {colors.ink-muted}."

3. "Build {cta-banner}: H2 '{typography.heading-lg}' in {colors.ink}, body
   '{typography.body-lg}', {button-white} CTA."

4. "Create {product-card} for [product name]: {colors.surface-dark} bg,
   image on top (aspect-ratio 1, object-fit cover), H3 in {typography.heading-sm}
   color {colors.ink}, body in {typography.body-sm}, {button-sm} CTA."

5. "Build {story-section}: 50/50 grid on {colors.canvas-light}, large image
   (rounded {rounded.md}) left, H2 {typography.heading-lg} {colors.ink-dark} +
   {divider} + body {typography.body-md} {colors.body} + {button-primary} right."
```

### WordPress Image Assets (exact URLs — use these, not stock photos)
```
Hero lineup:     https://fracktal.in/wp-content/uploads/2025/05/All-Printers-Cover-7-machines-Processed-2048x995-1.webp
Founders photo:  https://fracktal.in/wp-content/uploads/2020/11/1400567_354647701348120_1157476431_o-scaled-e1606386500766.jpg
Snowflake:       https://fracktal.in/wp-content/uploads/2021/11/Snowflake-Menu-Menu-Widgets.93.webp
Julia:           https://fracktal.in/wp-content/uploads/2021/11/Julia-Advanced-squre.96.webp
Twin Dragon:     https://fracktal.in/wp-content/uploads/2021/11/Twin-Dragon-Frontv-v2.106.webp
Volterra:        https://fracktal.in/wp-content/uploads/2021/11/Volterra_inventor_XR.97.webp
Apollo SLS:      https://fracktal.in/wp-content/uploads/2021/11/Apollo-SLS-Front.webp
PrintStick:      https://fracktal.in/wp-content/uploads/2021/11/Printstick-W25.107.webp
3D printer icon: https://fracktal.in/wp-content/uploads/2025/10/3d-printer.png
```

### Site Links
```
Homepage:         https://fracktal.in/
3D Printers:      https://fracktal.in/3dprinters/
About Us:         https://fracktal.in/home/about-us/
Contact:          https://fracktal.in/contact-us/
Manufacturer:     https://fracktal.in/3d-printer-manufacturer-india/
Snowflake:        https://fracktal.in/snowflake/
Julia:            https://fracktal.in/julia/
Twin Dragon:      https://fracktal.in/twindragon/
Apollo SLS:       https://fracktal.in/apollo-sls-landing-page/
PrintStick:       https://fracktal.in/printstick/
3DP Services:     https://fracktal.in/3d-printing-services/
```