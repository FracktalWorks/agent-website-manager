# Provenance — vendored design-taste corpus

**Vendored read-only reference material. Do not hand-edit anything in this tree.**

| | |
|---|---|
| **Source repo** | [`Leonxlnx/taste-skill`](https://github.com/Leonxlnx/taste-skill) — the tasteskill.dev skill family |
| **Source version** | commit `ccbc156`, dated 2026-08-24 (plugin version 1.0.0) |
| **License** | MIT (`LICENSE` in this directory) |
| **Vendored on** | 2026-08-29 |
| **Vendored by** | `design_taste` skill ingest (see `.github/skills/design_taste/SKILL.md`) |
| **Status** | **Read-only.** Fixes belong upstream. Repo-specific adaptation lives in the `design_taste` SKILL.md, never in these files. |

## What this is

The "anti-slop" design-taste rulebooks from tasteskill.dev: a corpus of concrete,
testable rules for what makes AI-generated web design look templated, and how to
reach past the defaults. Upstream ships them as Claude/Codex skills; here they are
reference rulebooks orchestrated by `.github/skills/design_taste/SKILL.md`, which
also translates their React/Tailwind/Next idioms into this repo's static
`build.py` pipeline.

| File here | Upstream skill | What it carries |
|---|---|---|
| `core.md` | `skills/taste-skill` | The main rulebook: brief inference ("design read"), the three dials (variance / motion / density), brief→design-system map, typography & color calibration, layout discipline hard rules, AI-tells ban list, redesign protocol, 60-item pre-flight check |
| `aesthetics/minimalist.md` | `skills/minimalist-skill` | Warm-monochrome editorial minimalism protocol |
| `aesthetics/soft-premium.md` | `skills/soft-skill` | High-end agency / Awwwards-tier polish protocol |
| `aesthetics/brutalist.md` | `skills/brutalist-skill` | Industrial brutalism / tactical telemetry protocol |
| `redesign.md` | `skills/redesign-skill` | Audit-first upgrade path for existing sites |
| `brandkit.md` | `skills/brandkit` | Brand-kit / identity-board image-generation direction (⚠ image generation is gated in this repo — user must ask explicitly) |
| `output-enforcement.md` | `skills/output-skill` | Anti-truncation: complete output, no placeholder stubs |
| `stitch-designmd.md` | `skills/stitch-skill` | How to author a Stitch-format `DESIGN.md` (the format used by `agent-data/design-md/`) |
| `image-first/image-to-code.md` | `skills/image-to-code-skill` | Image-first design→implementation workflow |
| `image-first/imagegen-web.md` | `skills/imagegen-frontend-web` | One-image-per-section design-reference generation (web) |
| `image-first/imagegen-mobile.md` | `skills/imagegen-frontend-mobile` | Same, mobile |

## Deliberately NOT vendored

- `skills/taste-skill-v1/` — superseded by `core.md`'s version.
- `skills/gpt-tasteskill/` — a GPT-specific port of the same content.
- `research/laziness/` — LLM-laziness research notes; interesting, not operational.
- `assets/`, `scripts/`, README marketing, sponsor material.

## Keeping it fresh

Snapshot, not a submodule. To re-sync: shallow-clone upstream, re-copy the files
in the table above to the same names, update the version row, and re-read
`.github/skills/design_taste/SKILL.md` for adapter rules that may now be stale.
