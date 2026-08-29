# Agent Data — Index

This folder contains permanent reference data used by the agent at runtime.
Every asset must be listed here.

| Path | Purpose | Usage |
|------|---------|-------|
| `BRAND_LAUNCH_RUNBOOK.md` | The order a brand goes live in — scaffold, concept round, design system, content, verify, deploy, search presence, platform assets, profiles — with the gate for each step | Read at the start of any new brand or site launch |
| `design-systems/` | 152 vendored design systems + `_craft/` rulebooks | Start at `design-systems/INDEX.md` |
| `design-taste/` | Vendored tasteskill.dev anti-slop rulebooks (core dials + AI-tells, aesthetic protocols, redesign, image-first, output enforcement) | Orchestrated by `.github/skills/design_taste/SKILL.md`; provenance in `design-taste/PROVENANCE.md` |
| `design-md/` | 74 brand design-language references (Stitch-format DESIGN.md with measured tokens: Apple, Linear, Stripe, …) | Start at `design-md/INDEX.md`; direction calibration only, never identity cloning |
| `templates/` | Document templates | Referenced by document generation scripts |
| `images/` | Product images and renders | Embedded in outputs |
| `specs/` | Technical specification PDFs | Parsed by research skills |

## Adding Assets

1. Place the file in the appropriate subfolder
2. Add an entry to this index with path, purpose, and usage notes
3. Commit the asset to git

## Rules

- All assets are **read-only** at runtime — never modify them programmatically
- Do NOT place user-provided files here — use `inputs/` instead
- Reference via `AGENT_DIR / "agent-data" / ...` in scripts
