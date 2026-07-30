# Provenance — vendored design-system corpus

**Vendored read-only reference material. Do not hand-edit anything in this tree.**

| | |
|---|---|
| **Source repo** | [`nexu-io/open-design`](https://github.com/nexu-io/open-design) — local checkout `C:/Users/VijayRaghavVarada/Documents/Github/open-design` |
| **Source version** | `0.15.1` (`package.json`), commit `bb7f4fd9d`, dated 2026-07-26 |
| **License** | Apache License 2.0 (`open-design/LICENSE`) |
| **Vendored on** | 2026-07-30 |
| **Vendored by** | `design_system_management` skill ingest (see `.github/skills/design_system_management/SKILL.md`) |
| **Status** | **Read-only.** Edits belong upstream, or in a *new* system created under this tree by the documented authoring path. |

## What this is

Open Design's complete bundled design-system catalog, plus its brand-independent
craft rulebooks. Vendoring it means this agent can build sites at the same design
fidelity **without Open Design installed** — no daemon, no MCP, no network.

| Path | Contents |
|---|---|
| `<id>/` | 152 design-system packages (`manifest.json` + `DESIGN.md` + `tokens.css`, plus optional `USAGE.md`, `components.html`, `design-tokens.json`, `tailwind-v4.css`, `preview/`, `source/`, `assets/`) |
| `_schema/` | The contracts: `manifest.schema.ts`, `tokens.schema.ts`, `defaults.css` (A2 fallback mirror), `AGENTS.md` (the tier + promotion narrative — **read this before adding a token**) |
| `_craft/` | `open-design/craft/` — 12 universal, brand-independent craft rulebooks + README |
| `INDEX.md` | Generated chooser table. Regenerate with `python .tmp/scripts/build_ds_index.py` |

## Ingest log (2026-07-30)

Copied with `robocopy /E` (bulk, not per-file writes), two operations:

| Source | Destination | Result |
|---|---|---|
| `open-design/design-systems/` | `agent-data/design-systems/` | **4082 / 4082 files, 37.5 MB — complete** |
| `open-design/craft/` | `agent-data/design-systems/_craft/` | **13 / 13 files, 108 KB — complete** |

**Nothing was skipped.** The exclusion filters (`/XD node_modules .git`,
`/MAX:5242880`) were armed but matched nothing:

- No `node_modules/` or `.git/` directory exists anywhere under
  `open-design/design-systems/`.
- No file exceeds the 5 MB cap. The largest is
  `fracktal-works/assets/Wall-Graphics-Final-Revised.pdf` at 2.23 MB; the largest
  non-`fracktal-works` file is `tom-modern/preview/tom-modern-components.png`
  at 0.64 MB.

Verified by comparing the full recursive relative-path sets of source and
destination: **0 files missing, 0 mismatched.**

### ⚠ One local file was clobbered and restored — read before re-syncing

`agent-data/design-systems/fracktal-works/` **already existed in this repo** before
the ingest, tracked in git, with a locally-authored addition: a 28-line
`## Elementor-safe authoring (when the output will be converted to Elementor)`
section in its `DESIGN.md` that upstream does not have. Robocopy overwrote it; it was
restored with `git checkout`.

**On every re-sync, exclude or re-restore that file.** Its other tracked files
(`brand.json`, `guide.md`, `logos/*`) matched upstream byte-for-byte and were
unaffected. Upstream's additional `fracktal-works` files (`assets/`, `system/`,
`ui_kits/`, `context/`, `imagery/`, `preview/`, `brand.html`,
`colors_and_type.css`, `README.md`, `SKILL.md`) are new here and were added.

### `README.md` in this directory is upstream's, not ours

`agent-data/design-systems/README.md` came in with the copy — it is Open Design's own
catalog doc. Its authoring guidance and the **attribution section** (upstream sources:
`VoltAgent/awesome-design-md`, `bergside/awesome-design-skills`, `tw93/kami`,
`Tom-Opencart/tom-modern-html-style-rule`) are worth keeping, but its tooling
references do **not** apply in this repo. Translations:

| It says | Here, use |
|---|---|
| `pnpm guard` / `pnpm typecheck` | `python .tmp/scripts/design_systems.py validate --all` and `quality --all` |
| `docs/design-systems.md` | `.github/skills/design_system_management/SKILL.md` |
| `od design-systems import-*`, `/api/design-systems`, daemon restart | nothing — this corpus is read from disk, there is no daemon |
| "151 packages" | 152 folders, 151 with a `manifest.json` (see census below) |

Only two files in this tree are ours: `INDEX.md` (generated) and this file.

Composition after ingest (4096 files, 37.6 MB — the delta vs. 4082 is `_craft/`
and this file):

| Extension | Files | | Extension | Files |
|---|---:|---|---|---:|
| `.html` | 1972 | | `.png` | 12 |
| `.json` | 924 | | `.jsx` | 7 |
| `.md` | 866 | | `.pdf` | 4 |
| `.css` | 305 | | `.webp` | 3 |
| | | | `.ts` / `.mjs` | 3 |

Almost pure text: 4067 of 4096 files (99.3%) are html/json/md/css.

## Package census

| | Count |
|---|---:|
| Design systems | **152** |
| With `manifest.json` (v1 project packages) | 151 |
| With `tokens.css` (a pasteable token contract) | 151 |
| With `DESIGN.md` | 152 |
| With `USAGE.md` (agent-facing router) | 150 |
| With `components.html` | 151 |
| Legacy `DESIGN.md`-only | **1** — `fracktal-works` |
| Validating clean (`validate --all`) | **152 / 152** |

`fracktal-works` is a legacy folder: no `manifest.json`, no `tokens.css` (it
carries `colors_and_type.css` + `brand.json` + a `system/` brand-engine output
instead). Open Design keeps such folders valid on purpose as a compatibility path,
so `validate` reports it `OK (legacy)` with a note rather than failing. It has
**prose guidance but no token contract to paste** — treat it as brand reference,
not as a design system you can build against directly.

## Upstream files deliberately NOT vendored

- `open-design/design-templates/` — packaged artifact shapes (saas-landing,
  pricing-page). Adjacent axis; out of scope for this ingest.
- `open-design/skills/` — 170+ Open Design skills. The two that matter for
  design-system *authoring* (`brand-extract`, and the brand engine's
  `seed → derive` pipeline) are summarized in this repo's
  `design_system_management` SKILL.md rather than copied, because they depend on
  Open Design's daemon, `agent-browser` tool, and `od` CLI.
- `open-design/packages/contracts/` — the TypeScript runtime. The parts this repo
  needs (`token-schema.ts`, `manifest.schema.ts`, the guard scripts) are ported to
  Python in `.tmp/scripts/design_systems.py`; the porting gaps are documented in
  the SKILL.md's "Not ported" section.

## Keeping it fresh

This is a snapshot, not a submodule. To re-sync:

```bash
robocopy <open-design>/design-systems agent-data/design-systems /E \
         /XD node_modules .git /XF DESIGN.md /MAX:5242880   # see the clobber warning above
robocopy <open-design>/craft         agent-data/design-systems/_craft /E
git checkout -- agent-data/design-systems/fracktal-works/DESIGN.md   # belt and braces
python .tmp/scripts/design_systems.py validate --all      # expect 0 failures
python .tmp/scripts/build_ds_index.py                     # regenerate INDEX.md
git diff --stat -- agent-data/design-systems/                # review every M before committing
```

`/XF DESIGN.md` is too blunt for a real refresh (it also skips legitimately updated
prose). The honest sequence is: copy without the exclusion, then
`git diff -- agent-data/design-systems/` and hand-merge any file that shows local
additions. Then update the version/commit/date rows at the top of this file.
