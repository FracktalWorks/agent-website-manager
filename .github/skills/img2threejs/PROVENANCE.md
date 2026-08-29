# Provenance — vendored img2threejs skill

**Vendored third-party skill. Upstream files are read-only; only this file and
REPO-NOTES.md are ours.**

| | |
|---|---|
| **Source repo** | [`hoainho/img2threejs`](https://github.com/hoainho/img2threejs) — img2threejs.org |
| **Source version** | v1.5.1, commit `441af85`, dated 2026-08-26 |
| **License** | Apache-2.0 (`LICENSE` in this directory) |
| **Vendored on** | 2026-08-29 |
| **Vendored by** | design-capability ingest alongside `design_taste` / `design_concepting` |
| **Status** | Upstream tree read-only. Fixes belong upstream. |

## What this is

A staged image→procedural-Three.js reconstruction pipeline: `SKILL.md` is the
router, `forge/` the Python stdlib tooling (stage1 intake → stage2 spec →
stage3 build → stage4 review → stage5 rig, driven by `forge/next.py`),
`grimoire/` the per-stage contracts, `integrations/` the vision/GLB adapters.
It rebuilds the object in a reference photo as code-only Three.js primitives
with screenshot-vs-reference review gates.

## Vendored vs not

| Kept | Dropped (and why) |
|---|---|
| `SKILL.md`, `CLAUDE.md`, `LICENSE` | `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `CONTRIBUTING.md` — marketing/meta |
| `forge/` (complete, incl. tests) | `assets/` — logos and sponsor art |
| `grimoire/` (complete) | `scripts/` — upstream's README-asset tooling |
| `integrations/` (complete) | most of `docs/` — only the files `SKILL.md` references were kept (`ARCHITECTURE.md`, `TOKEN_COST.md`, `HAIR_PIPELINE.md`, `cs2/`, `integrations/`, `materials/`, `specs/`) |
| upstream `skills/` → `subskills/` (renamed: `skills/` would read as a nested house-skill tree) | |

## Keeping it fresh

Shallow-clone upstream, re-copy the kept set, update the version row. Check
`SKILL.md`'s referenced paths still resolve (`grep -oE '(docs|grimoire|forge)/[A-Za-z0-9_./-]+' SKILL.md`).
