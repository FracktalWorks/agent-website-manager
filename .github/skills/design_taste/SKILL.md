---
name: design_taste
description: >
  Anti-slop design judgment for every page this agent designs. Orchestrates the
  vendored tasteskill.dev corpus (agent-data/design-taste/) and the 74-brand
  DESIGN.md corpus (agent-data/design-md/): the design read, the three dials
  (variance / motion / density), the AI-tells ban list, aesthetic-direction
  protocols, and the pre-flight check — all translated from upstream's
  React/Tailwind idiom into this repo's static build.py pipeline.
when_to_use: >
  Before designing or restyling ANY page: a new site, a new section, a landing
  page, a concept mockup (design_concepting loads this first), or a redesign of
  an existing site. Also when output "looks AI-generated", "looks templated",
  "needs to feel more modern/premium", or when calibrating what a vibe word
  ("Linear-style", "Apple-y", "brutalist") concretely means.
authority: read
cost_tier: 1
version: 0.1.0
---

# Design Taste

Two vendored corpora, one adapter. The corpora say what good looks like; this
file says how to apply them in a repo where pages are Python data rendered by
`build.py`, styled by design-system tokens, and gated by `verify.py`/`slop.py`.

## The corpora

| Read | When |
|---|---|
| `agent-data/design-taste/core.md` | **Always, before designing.** The main rulebook: §0 design read, §1 dials, §4 typography/color/layout hard rules, §9 AI-tells ban list, §11 redesign protocol, §14 pre-flight check |
| `agent-data/design-taste/aesthetics/minimalist.md` · `soft-premium.md` · `brutalist.md` | When the design read lands on that aesthetic family |
| `agent-data/design-taste/redesign.md` | Restyling an existing live site (audit first, never break IA) |
| `agent-data/design-taste/image-first/*` | Composing section-by-section visual direction before implementation (the design_concepting flow uses the *composition* rules; see image policy below) |
| `agent-data/design-taste/brandkit.md` | Brand-identity boards — only when the user explicitly asks for generated imagery |
| `agent-data/design-taste/stitch-designmd.md` | Authoring a DESIGN.md for a client brand in the Stitch format |
| `agent-data/design-taste/output-enforcement.md` | Any large deliverable at risk of truncation/placeholder stubs |
| `agent-data/design-md/INDEX.md` → `<brand>/DESIGN.md` | Calibrating a vibe word to measured tokens ("Linear-clean" = `#010102` canvas, `#5e6ad2` single accent, -3px tracked 80px display). Reference for *direction*, never identity cloning |

Provenance and licenses: `agent-data/design-taste/PROVENANCE.md`,
`agent-data/design-md/PROVENANCE.md`. Both trees are read-only.

## The workflow the corpus enforces

1. **Design read first** (core.md §0). One line before any code: *"Reading this
   as: <page kind> for <audience>, with a <vibe> language, leaning toward
   <design system or aesthetic family>."* If genuinely ambiguous, ask **one**
   question, never a question dump.
2. **Set the three dials** (core.md §1): `DESIGN_VARIANCE`, `MOTION_INTENSITY`,
   `VISUAL_DENSITY`, reasoned from the read — never silently defaulted.
3. **Pick the foundation**: a design system from `agent-data/design-systems/`
   (the 152 corpus — see design_system_management) or an honest aesthetic
   family. One system per site.
4. **Design under the hard rules** (core.md §4): hero fits the viewport,
   eyebrow rationing, no zigzag runs, section-layout families don't repeat,
   color/shape/theme locks, content density caps.
5. **Pre-flight** (core.md §14) before calling any page done — plus this
   repo's own gates (below), which run *after* it and win on conflict.

## Adapter — upstream idiom → this repo

Upstream assumes React/Next/Tailwind/Motion. Translate:

| Upstream says | Here, do |
|---|---|
| Tailwind utilities (`text-6xl tracking-tighter`) | Real CSS in the site's `assets/site.css` **layout classes**; all color/type/radius values come from design-system tokens in `:root` (raw hex outside `:root` fails the build) |
| Motion / GSAP / `motion/react` | CSS-only first: transitions, `@keyframes`, scroll-driven animations where supported. Behaviour that needs JS goes in `assets/chrome.js` — **never inline `<script>`** (WordPress escapes `&&`/`<` and silently kills it) |
| `next/font`, "never link Google Fonts" | Same conclusion, our pipeline: `python .tmp/scripts/webfonts.py` — self-hosted, licence-checked, subsetted (₹ needs latin-ext) |
| npm icon libraries (Phosphor etc.) | No npm here. One consistent icon voice per site: either a single downloaded open-licence SVG set vendored into `assets/`, or the site's own drawn line-art style (fracktal precedent). The *rule that survives*: one family, one stroke width, never mixed |
| `prefers-reduced-motion` via `useReducedMotion()` | `@media (prefers-reduced-motion: reduce)` blocks in CSS — still mandatory above dial 3 |
| Dark mode mandatory, dual-theme | **Per-brand decision.** Our sites ship one locked theme unless the brief says otherwise; the rule that survives is the Theme Lock (no section flips mid-page) and AA contrast, which `brandkit.py` enforces |
| "Image-gen tool first" for visual assets | **House rule overrides (memory: higgsfield-usage-rule, generated-image-review): never auto-generate images.** Use the client's real photography/media library first, the site's diagram pipeline (`diagrams.py`) only when the user asks, honest labeled placeholder slots otherwise. The *composition* guidance (right aspect per section, no div-based fake screenshots, no pure-text minimalism) fully applies |
| Lighthouse / Core Web Vitals | `python verify.py --all` (4 widths, overflow, broken images) + the imgfit/imghalo/band-colour gates already in the repo |
| React empty/loading/error states | Mostly N/A for static marketing pages; applies to forms and any WhatsApp-CTA fallback states |

## Precedence on conflict

1. **This repo's gates and recorded lessons** — build.py BANNED/SLOP, brandkit
   AA refusal, image-fit contract, band-colour contract, slop.py rhythm rules.
2. **The client's own design system / brand kit** (e.g. Atlas Wild's brand kit
   is the source of truth; a taste rule never overrides a client's brand).
3. **Taste corpus rules** (core.md, aesthetics).
4. **Brand DESIGN.md references** — inspiration only, lowest authority.

Upstream's em-dash ban (core.md §9.G) applies to **display/UI strings**
(headlines, labels, buttons, eyebrows). For body copy, `slop.py` and the
AI-copy-detector discipline remain the authority.

## What this skill deliberately is not

Not a build tool (site_generator), not a token manager (design_system_management),
not the mockup flow (design_concepting — which loads this skill first). It is
the judgment layer those three call into.
