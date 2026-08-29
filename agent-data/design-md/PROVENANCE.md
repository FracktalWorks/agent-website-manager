# Provenance — vendored brand DESIGN.md corpus

**Vendored read-only reference material. Do not hand-edit anything in this tree.**

| | |
|---|---|
| **Source repo** | [`VoltAgent/awesome-design-md`](https://github.com/VoltAgent/awesome-design-md) |
| **Source version** | commit `8147538`, dated 2026-07-31 (badge count: 73 DESIGN.md) |
| **License** | MIT (`LICENSE` in this directory) |
| **Vendored on** | 2026-08-29 |
| **Vendored by** | `design_taste` skill ingest (see `.github/skills/design_taste/SKILL.md`) |
| **Status** | **Read-only.** Corrections belong upstream. |

## What this is

One `DESIGN.md` per famous production website (Apple, Linear, Stripe, Tesla,
Nike, …), each a Stitch-format design-language document: YAML frontmatter with
measured color/typography tokens, then prose sections for atmosphere, components,
layout, elevation, do's & don'ts, responsive behavior, and an agent prompt guide.
The tokens are extracted from the sites' publicly visible CSS.

**What it is for here:** design-direction *calibration*. When a brief says
"Linear-clean", "Apple-y", "Stripe-like", read that brand's file to know
precisely what those words mean, and to seed distinct direction mockups in the
`design_concepting` flow. **Never clone a real brand's identity onto a client
site** — these files inform a direction; the client's own design system (from
`agent-data/design-systems/` or authored) is what ships.

| Path | Contents |
|---|---|
| `<brand>/DESIGN.md` | 74 brand design-language files (dirs named by domain-ish slug: `linear.app`, `x.ai`, `dell-1996`, …) |
| `INDEX.md` | Generated chooser table — regenerate with `python .github/skills/design_taste/scripts/build_designmd_index.py` |
| `LICENSE` | Upstream MIT license |

## Relationship to `agent-data/design-systems/`

The 152-system corpus already credits `VoltAgent/awesome-design-md` as one of
its upstream sources, so *some* brands exist in both trees in older, reworked
form. This tree is the **current, direct** snapshot in the richer Stitch format
(YAML token frontmatter). For *building* a site, the design-systems corpus wins
(it has `tokens.css` contracts); for *describing a look* during concepting, this
tree wins.

## Ingest log (2026-08-29)

Copied per-brand `DESIGN.md` only (74 files) plus `LICENSE` from a shallow
clone. **Deliberately not vendored:** each brand's `README.md` (a one-line
redirect to getdesign.md), the repo README/CONTRIBUTING/marketing, and the
`.github/` templates. Nothing else exists upstream per-brand — the
`preview.html` catalogs the README mentions live on getdesign.md, not in git.

## Keeping it fresh

Snapshot, not a submodule. To re-sync: shallow-clone upstream, re-copy
`design-md/*/DESIGN.md` over this tree (new brands = new dirs), then regenerate
`INDEX.md` and update the version row above.
