---
name: site_generator
description: >
  Build and maintain complete websites inside this repo: pages as Python data,
  one renderer, a validating builder that enforces SEO structure + domain
  compliance + design integrity on every build, a local preview server, and a
  browser-based live editor whose edits round-trip into the Python source.
  Distilled from Open Design's architecture; the reference implementation is
  outputs/drvarada-site/site/.
when_to_use: >
  User wants a new site or landing system built/maintained in-repo (not a quick
  one-off HTML file); wants to edit generated pages visually ("live edit",
  "edit in the browser"); or asks how the drvarada site build works.
authority: write
cost_tier: 2
version: 0.1.0
---

# Site Generator & Live Editor

Websites here are **generated, never hand-edited**. A site is a folder of
Python content modules plus one renderer; the builder validates everything on
every build; a live editor lets a human edit the *rendered* page while the
system rewrites the *source* underneath. This is the DOE loop applied to web
design: content-as-data is the directive layer, the agent's judgment shapes it,
and deterministic scripts do the rendering, validation and persistence.

## Reference implementation — `outputs/drvarada-site/site/`

| File | Role |
|------|------|
| `content/*.py` | Pages as data dicts — copy, sections, images, FAQs, links. **The only place content lives.** |
| `content/urls.py` | slug → production URL. The only place IA is defined. |
| `chrome.py` | ALL markup: header, nav, footer, block renderers, schema.org, `img()`/`slot()`/`at()`. One edit fixes every page. |
| `build.py` | Assembler + validator + sitemap/robots + `site-manifest.json`. Validation is not optional. |
| `datapatch.py` | Edits page data **by address** (`sections.4.items.0.before`) via AST spans — creates missing keys, reorders/duplicates/removes list items, rewrites module constants. |
| `resolver.py` | Edits copy **by value** — the fallback for text with no address. Also owns `char_col`, the UTF-8 byte→character column conversion every span write must use. |
| `media.py` | Upload pipeline: verify by decoding, bake EXIF orientation, strip all metadata, cap the long edge, re-encode, report dimensions. |
| `editor.py` | Live-edit server: injects the overlay, applies edits inside a transaction that reverts source *and deletes uploaded files* if the build fails, watches sources, SSE-reloads every tab. |
| `editor/editor.js\|css` | The injected overlay: hover-pick, in-place text editing, inspector panels (image/link/tokens/site), section toolbar, undo, open-in-code. Never part of a build. |
| `preview.py` | Plain build+serve, no editing. |
| `verify.py` | Renders every built page in real Chrome at 390/768/1040/1440px and fails on horizontal scroll or broken images. Measures inside an iframe of the exact width because Chrome on Windows clamps windows to ~500px, and ignores elements clipped by a scrolling ancestor so intentional marquees and scrollable tables don't false-positive. |

Run: `python build.py` (preview), `python build.py --links=production`,
`python editor.py` (live editing at http://127.0.0.1:8789),
`python preview.py` (plain preview at http://127.0.0.1:8788).

**In VS Code:** start `python editor.py`, then `Ctrl+Shift+P → "Simple
Browser: Show" → http://127.0.0.1:8789/`. The user edits the page in the
editor pane; saved edits land in `content/*.py` in the same window. Alt+click
anything jumps VS Code to the exact source line.

### What the editor can change

| Target | Surface | Persists to |
|---|---|---|
| Copy | click to edit in place | the string literal in `content/*.py` |
| Images + empty slots | inspector: drag-drop, alt, focal point, consent | an image dict in the page data + a processed file in `assets/img/` |
| Links and CTAs | inspector: label + destination, with slug autocomplete | the `(label, target)` tuple — or the shared constant, when the target is one |
| Sections and cards | hover toolbar: move ↑↓, duplicate, delete | element position in the Python list |
| Design tokens | Tokens panel with colour pickers | the design system's `:root` block |
| Site-wide details | Site panel: Practo links, phone, WhatsApp, reviewer | module constants in `chrome.py` |

## Why this shape (the load-bearing decisions)

1. **Pages are data, markup lives once.** 45 pages is past the point where
   hand-edited HTML stays consistent. A block renderer bug fixed once fixes
   every page; a design-system change re-skins the whole site on rebuild.
2. **The builder is the review loop.** Structural SEO (titles, metas, FAQ
   schema, internal links, orphans), domain compliance (for medical sites:
   NMC advertising rules with a negation window so "no treatment cures
   vitiligo" passes), design integrity (anti-slop constants, token-scope CSS,
   layout rhythm), and image discipline (real alt text, consent on patient
   photography) — all fail the build with a precise message. The agent's
   stderr *is* the design review; no second model call needed.
3. **Address the data, not the DOM.** Preview builds stamp the *data address* of
   each value into the markup (`data-od="sections.4.h2"`,
   `data-od-img="sections.6.items.0.before"`). Open Design computes a
   child-index DOM path at serve time; a data address is strictly better — it
   survives markup changes and is unambiguous by construction, so the "appears
   in 16 places" prompt only arises for unaddressed inline copy. Production HTML
   carries none of these attributes.
4. **Every edit is a transaction.** Snapshot the source, apply, rebuild; on
   failure restore the source *and delete any uploaded file*, then show the
   build's own objection in the browser. Type "best dermatologist" into a
   headline and you get the compliance error, not a published claim.
5. **Verify the write, not just the syntax.** After a span write, re-read the
   address and confirm it holds what was asked for. A span that swallows one
   character too many turns `{...},\n(...)` into a valid *call expression*: it
   parses cleanly while having silently destroyed the next list item. A syntax
   check misses that; a read-back does not. Related trap — `ast` reports
   `col_offset` in UTF-8 **bytes**, so any line containing an em dash corrupts
   naive slicing. Always go through `resolver.char_col`.
6. **Tokens instead of per-element inline styles.** Open Design offers 33 style
   properties per element, which is right for a standalone artifact. In a
   token-driven generated site it is pure drift — so the editor edits the design
   system instead: one change, every page, no detachment.
7. **Structural edits work here and were a documented non-goal there.** Open
   Design left move/duplicate out because its target is an HTML file. A section
   is a Python list element here, so reordering is exact and the diff reviewable.
8. **Uploads are processed, never just stored.** Verify by decoding (a renamed
   file is not an image), bake EXIF orientation into the pixels, then strip all
   metadata — which removes GPS and capture time, a requirement for clinical
   photography rather than an optimisation — cap the long edge, re-encode
   progressive, and record `w`/`h` so the browser reserves the box.

## Building a NEW site with this pattern

1. **Design system first.** Either pick one from the 152-package corpus or
   author one — see [design_system_management](../design_system_management/SKILL.md)
   (`python .tmp/scripts/design_systems.py search "<brief>"`, then `show <id>
   --root` for the `:root` block to paste). The site's own CSS is layout-only;
   raw colours outside a `:root` component-token block fail the build.
2. Copy the reference `site/` folder; empty the `content/` modules; write
   `urls.py` from the keyword/IA map FIRST (one page, one query cluster).
3. Rewrite the domain compliance list in `build.py` (`BANNED`/`NEGATION`)
   for the client's regulatory reality; keep the `SLOP` list as is.
4. Author content as data, applying `references/craft.md` and the fuller
   rulebooks in `agent-data/design-systems/_craft/`. Brand tokens win on value
   conflicts; craft rules cover everything the brand does not override.
5. Two edits wire the editor to the new site: `resolver.SEARCH_FILES` and
   `datapatch.CONTENT_FILES` (the latter derives from the former).
6. Run `python verify.py --all` before shipping, and screenshot-verify the
   result. Static checks pass pages that render broken: Open Design learned
   this when a 5-phase static audit reported "42/45 requirements, 0 defects"
   and live rendering then found three runtime bugs, one of which blanked the
   page. `verify.py` earned its keep immediately — it caught an inline
   `grid-template-columns` on the footer that outranked every media query and
   made all 45 pages scroll sideways on a phone.

## Quality gates catalog (what build.py enforces)

| Gate | Failure mode it kills | Severity |
|------|----------------------|----------|
| URLS ↔ slugs bijection, link resolution | renamed slug orphans a page | error |
| title/meta/FAQ/related presence, meta 110–320 | thin or schema-less pages | error |
| Band rhythm (max 1 dark body section) | design-system violation | error |
| Domain compliance (NMC + negation window) | illegal medical claims | error |
| SLOP list: filler copy, invented metrics | "lorem ipsum", "10× faster" | error |
| AI-default accents (7 indigo hexes) | LLM regression to the mean | error |
| Raw colour outside `:root` token scope | design-system drift in CSS | error |
| Image file exists + alt text ≥ 8 chars | broken images, inaccessible pages | error |
| Consent record on before/after photography | publishing a patient without consent | error |
| 3 consecutive same-kind sections | template monotony | warning |
| Title > 60 chars | SERP truncation | warning |

Honest enforcement (Open Design's rule): anything not in this table is
**guidance** — see `references/craft.md`, which labels each rule
auto-checked vs guidance so the contract with the linter stays honest.

## Ported from / still to port (Open Design provenance)

Ported: content/renderer split, always-validating builder, anti-slop
constants + token-scope CSS lint (`lint-artifact.ts`), layout-rhythm caps
(taste-skill §4.7), `site-manifest.json` (design-manifest idea), live-edit
loop (manual-edit-mode, rebuilt source-first: they re-serialize the DOM, we
rewrite the authored literal — ours diffs cleaner), craft references.

Worth porting when needed: **seed → derive** for design systems (~20-field
seed.json deterministically derives palette ladders, type scale, dark mode —
rebranding becomes a one-field edit); token tiers (A1/A2/slot/extension) with
a parity-checked human-readable defaults file; design-jury critique loop
(5 weighted panelists, threshold 8/10, max 3 rounds, ship-best fallback);
stub-regression guard at the write boundary; a `tweaks` panel binding CSS
custom properties to a localStorage control strip.
