# Fracktal Works — Applied UI Kit

A Claude-Design-style, component-split React kit for the Fracktal Works applied
product surface. It is the same applied interface as before — a sticky nav with a
working Products dropdown, a dark hero band, a filterable product grid, a Twin
Dragon datasheet, a red CTA band, and a dark footer — now modularized into one
runnable entry plus a folder of single-responsibility components. It follows the
DEFAULT THEME design language: rounded 6px corners, flat (no shadow), a single
brand accent (`#f25e50`) plus status colors, Montserrat, and Lucide icons. The
regions, real copy, real specs, and real image paths are preserved verbatim; only
the surface posture is refit to the rounded default theme. Every value binds to
`../../colors_and_type.css` via `var(--token)` and the `.fk-*` helpers, so the
corners round and the palette resolves straight from the tokens.

## Structure

- **`index.html`** — the runnable entry. It pins React 18.3.1, ReactDOM 18.3.1,
  and Babel Standalone 7.29.0 (with integrity hashes), loads **Lucide** from the
  CDN (`unpkg.com/lucide@latest`), binds the design tokens via
  `<link rel="stylesheet" href="../../colors_and_type.css">`, loads each
  component as a `type="text/babel"` script (`components/Icon.jsx` first, so
  `window.Icon` exists before any region renders), and mounts `<App/>` into
  `#root`.
  A small inline `<style>` holds layout-only helpers (page reset, the centered
  `.fk-wrap` container, responsive grid collapses, mobile-nav behavior) — it
  defines no brand color, type, or spacing; those come only from the tokens.
- **`components/`** — one file per region component (see below). Each file
  defines a component and exposes it as a browser global at the end
  (e.g. `window.TopNav = TopNav;`). No `import` / `export`, no `type="module"`.

## Components

- **`components/Icon.jsx`** — Lucide icons rendered as inline-SVG React
  components on the host `window.React` (no external icon dependency, no
  esm.sh / lucide-react / import maps). Exposes `window.Icon`; used as
  `<Icon name="…" size={…} />` inside the region components.
- **`components/TopNav.jsx`** — sticky top nav: dark wordmark, primary IA
  (Products · Manufacturing Services · Industries · Materials · Resources), a
  Products dropdown driven by `React.useState`, the red **Buy Now** CTA, and a
  mobile burger toggle (also `useState`).
- **`components/Hero.jsx`** — dark `#111111` hero band (`var(--canvas-dark)`):
  overline, the "India's premier 3D printer manufacturer" headline, one
  declarative subhead, red + on-dark CTAs, real product photography
  (`../../imagery/cover-0.webp`), and a mono stat row.
- **`components/ProductGrid.jsx`** — white product section with category filter
  tabs (`useState`: All / FDM / SLS / Services) over flat 1px cards for
  Snowflake, Julia, Twin Dragon, Volterra, Apollo 350, PrintStick, and
  Manufacturing Services. Each card carries a `data-od-id`.
- **`components/SpecTable.jsx`** — the Twin Dragon TD300 / TD500 / TD600
  datasheet, rendered with `--ff-mono` + `tabular-nums` so columns align.
- **`components/SiteFooter.jsx`** — the red CTA banner ("Built in Bangalore. From
  the ground up.") followed by the dark `#111111` footer band: light wordmark,
  nav columns, and contact (+91 94296 91256, info@fracktal.in, www.fracktal.in).
- **`components/App.jsx`** — the composition root; reads the region components off
  `window` and renders `<TopNav/><Hero/><ProductGrid/><SpecTable/><SiteFooter/>`,
  ending with `window.App = App;`. Most icons render directly as inline-SVG
  `window.Icon` components, but a few glyphs outside that set
  (`sliders-horizontal`, `gauge`, `globe`) still ship as CDN `<i data-lucide="…">`
  placeholders; App runs a `React.useEffect` that calls
  `window.lucide.createIcons()` after mount to swap those for their SVG, and the
  regions that hold them run their own `createIcons()` effect too (e.g.
  `ProductGrid` re-runs on filter change) so re-rendered cards stay covered.

## Usage

1. **Copy** the `ui_kits/app/` folder somewhere the relative paths still resolve
   — `index.html` references `../../colors_and_type.css`, `../../imagery/*`, and
   `../../logos/*`, so keep it two levels under the project root (or repoint the
   `<link>` and the `src` paths).
2. There is no build step and nothing to **import** at the tooling level: open
   `index.html` in a browser. It loads React + ReactDOM + Babel from the pinned
   CDN scripts, then Babel compiles each `components/*.jsx` file in the browser.
3. Each component file **uses** plain function-component code and **exposes** its
   component as a `window` global (`window.TopNav`, `window.Hero`,
   `window.ProductGrid`, `window.SpecTable`, `window.SiteFooter`,
   `window.App`). `App` **composes** them by reading those globals off `window`,
   so load order in `index.html` is: the five region components first, then
   `App.jsx`, then the mount script.
4. To retheme, edit `../../colors_and_type.css`. The components consume tokens
   via `className` + the `.fk-*` helpers + `var(--token)` inline styles and never
   hardcode the brand palette, so changing a token re-skins the whole kit.

## Design Notes

This kit is sourced from the prior single-file applied UI kit and the Fracktal
Works design system; it modularizes that surface without redesigning it.

- **Source basis.** IA + the **Buy Now** CTA and the footer contact/logos are
  measured from fracktal.in. The hero headline/voice and the red CTA-banner copy
  come from the brand brief / DESIGN.md (the indigenous-capability pillar). The
  Twin Dragon spec values are measured from the product brief / brochure data.
  Product names and one-line specs come from the product range. Card layout and
  category filtering are an inferred composition over that measured content.
- **Layout.** Alternating bands — light product/datasheet sections against
  near-black (`#111111`) hero and footer bands; depth is color contrast, not
  elevation. A 1200px centered `.fk-wrap` container, a 3-column product grid that
  collapses to 2 then 1, and a mobile nav that stacks under 920px.
- **Colors.** One brand accent (`--accent` #f25e50, hover `--accent-hover`
  #ff8d7d, pressed `--accent-active` #cc4139) reserved for CTAs, section rules,
  the active tab, and key emphasis only — never decoration. State uses the status
  colors (`--ok` / `--warn` / `--error`). Everything else is ink / neutral. These
  hex values are named here for provenance only; the active styles reference the
  tokens, never literal hex.
- **Typography.** Montserrat throughout (`--ff-display` / `--ff-body`), with
  `--ff-mono` + `tabular-nums` for engineering numerics so the spec table and the
  card spec rows read like a datasheet.
- **Icons.** [Lucide](https://lucide.dev) inline SVG, 14–18px at `currentColor`.
  Icons: Lucide, rendered as inline-SVG React components in `components/Icon.jsx`
  (no external icon dependency). The core set —
  `menu` / `x` / `chevron-down` / `shopping-cart` (nav), `arrow-right` /
  `file-text` (hero), `arrow-right` (product grid), and
  `phone` / `mail` / `arrow-right` (footer) — renders directly via `<Icon name="…" />`
  on the host `window.React`. A few remaining glyphs outside that set
  (`sliders-horizontal` in the product grid, `gauge` in the datasheet, `globe` in
  the footer) still ship as CDN `<i data-lucide="…">` placeholders converted by
  `lucide.createIcons()`.
- **Tokens.** All brand color, type, spacing, radius (`--radius` 6px, **rounded**),
  and shadow (`--shadow` `none`, **flat**) come from `../../colors_and_type.css`;
  the components only add layout and never hardcode the radius or brand hex.
  Rounded 6px / flat (no shadow) / single-accent posture is enforced everywhere.
- **Imagery provenance.** All product photography is **real**, shipped in
  `../../imagery/`, and must **never be AI-generated**. Used: `cover-0.webp`
  (machine family lineup), `hero-1.webp` (PrintStick), `hero-2.png`, `hero-3.png`,
  and `hero-6.webp` (real machine/material photos). `hero-4.png`, `hero-5.png`,
  and `hero-7.png` are **government / partner logos, not product photos**, and are
  deliberately not used as product-card images. Logos:
  `logos/Website-Header_black.png` (dark wordmark on the light nav) and
  `logos/Websitesd-Header.png` (light wordmark on the dark footer).
