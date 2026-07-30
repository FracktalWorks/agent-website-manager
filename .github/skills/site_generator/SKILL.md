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
| `versions.py` | Version timeline, ported from Open Design's `project-file-versions.ts`: append-only, restore-writes-forward, content-addressed blobs, parent links so undo follows the edit lineage. |
| `linkscan.py` | Every link on the site by walking the *renderer's* positions in the page data. `where <target>` / `audit`; powers the inspector's this-one-or-all-N choice. |
| `resolver.py` | Edits copy **by value** — the fallback for text with no address. Also owns `char_col`, the UTF-8 byte→character column conversion every span write must use. |
| `media.py` | Upload pipeline: verify by decoding, bake EXIF orientation, strip all metadata, cap the long edge, re-encode, report dimensions. |
| `editor.py` | Live-edit server: injects the overlay, applies edits inside a transaction that reverts source *and deletes uploaded files* if the build fails, watches sources, SSE-reloads every tab. |
| `editor/editor.js\|css` | The injected overlay: hover-pick, in-place text editing, inspector panels (image/link/tokens/site), section toolbar, undo/redo, open-in-code. Never part of a build. |
| `brandkit.py` | Drives the site from any corpus design system: reads its canonical `:root`, derives this site's tokens in OKLCH, repairs contrast, writes `assets/brand.css`. `list` / `show <id>` / `apply <id>` / `apply --native` / `calibrate` / `check`. |
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
| Links and CTAs — including nav and footer | inspector on **any** anchor: label + destination + scope | the `(label, target)` tuple, a `chrome:NAV.0.2.1` address into a module constant, or the shared constant when the target is one |
| Sections and cards | hover toolbar: move ↑↓, duplicate, delete | element position in the Python list |
| Design tokens | Tokens panel with colour pickers | the design system's `:root` block |
| Site-wide details | Site panel: Practo links, phone, WhatsApp, reviewer | module constants in `chrome.py` |
| Any of it, undone | Undo/Redo (Ctrl+Z / Ctrl+Shift+Z) and a **Versions** panel | an append-only timeline under `site/.versions/`, surviving restarts |
| A link, everywhere | the Link inspector's scope: *just this one* or *all N pointing here* | every occurrence at once, found by walking the page data |

### Addressing reach — how much the editor can name exactly

Every renderer threads a data address through its item loops, so **69% of
text-bearing elements** carry an exact address (`sections.4.rows.2.1`,
`faqs.3.1.0`, `items.2.list.5`). That number matters because the fallback is
value matching: an unaddressed string that appears on sixteen pages produces an
ambiguity prompt, and an addressed one just edits. Two deliberate exclusions:

- **Template chrome** (nav, footer, byline, utility bar) is not page data at
  all — it lives in `chrome.py` constants, and editing it *should* change all
  45 pages at once. The Site panel is its surface.
- **The `"1.a|b|c"` ordered-list shorthand** packs several items into one
  string. No address can name a segment of a string, so those keep the
  value-based path rather than carrying an address that would rewrite the
  whole list.

Production HTML carries none of it — `at()` emits nothing when `links` is
`production`, and the build asserts it.

### Editing a link everywhere it appears

Open Design's inspector edits the one anchor you clicked (`set-link` in
`apps/web/src/edit-mode/source-patches.ts`) — correct for a single artifact,
wrong for a 45-page site where the Practo button appears 60 times. Because
pages are data, `linkscan.py` can answer a question OD cannot ask: *where else
does this destination appear?* The inspector then offers **this one** or **all
N**.

Three things make it trustworthy:

- **It walks the renderer's positions, never the text.** The slug `vitiligo`
  appears in the source as a link target, as a page's own `slug` key, and
  inside prose. A textual search would rewrite all three.
- **Rendered hrefs are normalised back to slugs.** The browser reports
  `vitiligo.html`; the source stores `vitiligo`. Skip that and the scan finds
  nothing and reports "used once" — the worst possible failure for a control
  offering to change everything.
- **The scan re-reads from disk every time.** It runs inside a long-lived
  process that has already imported the content modules, and Python caches
  them; without a reload every scan answers from startup state.

Nav and footer links are addressed as `chrome:NAV.0.2.1` — into the module
constant where they actually live — so those 64 links became editable too.
`datapatch.set_in_constant` writes them with the same read-back verification
page addresses get.

### Version history (ported from Open Design)

`versions.py` is a port of Open Design's `apps/daemon/src/project-file-versions.ts`.
The model is what was worth copying, and three rules carry it:

1. **Append-only.** Versions number from 1 and are never renumbered, reordered
   or deleted.
2. **Restore is a write, not a rewind.** Going back to v3 writes v3's content
   and appends it as a *new* version labelled `Version 9 · restored from v3`
   (upstream's `nextLabel`). Nothing you have seen can be lost, because no
   operation removes anything.
3. **Seed the current state.** `ensure_current()` captures whatever is on disk
   as v1 when the store is empty or has drifted (upstream
   `ensureCurrentProjectFileVersion`). In a git working tree this is the rule
   that matters: check out a branch, edit once, and without it the branch state
   has no version to return to.

Also lifted: defensive manifest reads (a record that does not parse is skipped,
not raised on — history is a convenience and must never block editing), and an
atomic manifest write.

Three deliberate departures, each for a reason upstream does not face:

- **The unit is the tracked set, not one file.** An edit here can touch a
  content module, the design system and an upload at once.
- **Content is content-addressed.** Upstream stores a full copy per version;
  our tracked set is ~540 KB, so unchanged files would dominate. Blobs are
  shared, `read()` is still a direct lookup, and there is no diff chain.
- **Undo follows parent links, not array order.** Upstream has no undo — every
  move is a restore. With undo, a flat array puts abandoned states between you
  and your earlier work, so the next Ctrl+Z jumps into a branch you left. Each
  entry records the version it was made from, so undo means what it says while
  the abandoned branch stays reachable from the Versions panel.

Undo, redo and restore all pass the same build gate as a forward edit: a jump
that would not build is put back and reported.

## Re-branding a site from the design-system corpus

`python brandkit.py apply stripe` makes any of the 152 vendored systems drive
the whole site. It is a **token bridge**, not a rename table:

- The corpus speaks 54 shared names (`--bg`, `--fg`, `--accent`); a site speaks
  its own (`--ground`, `--ink`, `--mint`). Aliasing alone leaves a third of the
  site undefined, because the site needs colours the schema has no name for —
  a dark punctuation band, a ramp for text on it, category pastels, a gold.
  Those are **derived in OKLCH from the brand's own hue** (never HSL: HSL's
  "lightness" is not perceptual, so a hue-rotated palette built in it comes out
  with one washed-out member and one muddy one).
- Every derived text colour is walked along its lightness axis until it meets
  WCAG AA on the surfaces it actually appears on. A brand whose `--meta` is a
  decorative 3:1 grey cannot reintroduce a contrast failure.
- `apply` **refuses** a brand whose palette cannot reach AA, and says which
  pairing fails. 150 of the 152 systems pass; the two that do not declare a
  dark page background behind white cards, which a single body-copy token
  cannot serve — a real structural mismatch, not a tuning problem.
- `calibrate` feeds the site's *own* hand-tuned kit back through the same
  derivation and diffs the result. That is the only test that separates "the
  rules are sound" from "the rules produce something plausible". On the
  reference site 18 of 20 colours land within perceptual tolerance.
- `check` fails the build if any `var()` the CSS reads is undefined. Without
  it a bad bridge renders a **grey page and no error** — an undefined custom
  property silently drops the declaration that used it.

Fonts go through `.tmp/scripts/webfonts.py`. All 152 systems name a typeface
and none ship one, so a brand's own tokens typeset in the fallback unless
something intervenes: a system face is left alone, an openly licensed face is
fetched and embedded for real, and a proprietary face is substituted by
classification **and the substitution is reported**. A silent substitute is a
lie about what the brand looks like. Nothing proprietary is ever cached —
`fetch` refuses any family not in the licensed allowlist.

What this buys, stated honestly: the brand's **palette, type and geometry** in
this site's idiom. Not the brand's layout language — Stripe's dense data panels
are markup, not tokens. A Stripe build looks like this site drawn in Stripe's
colours and typeface.

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

Also ported since: the token tier model (A1/A2/slot/extension) and a
derive step — `brandkit.py` derives a full site palette from a brand's
canonical tokens, which is Open Design's seed→derive idea applied at the
consumer end rather than the authoring end, and adds a contrast-repair pass
they do not have.

Worth porting when needed: authoring-side **seed → derive** (a ~20-field
seed.json that derives a design system's own palette ladders, type scale and
dark mode, so rebranding a *system* is a one-field edit); design-jury critique loop
(5 weighted panelists, threshold 8/10, max 3 rounds, ship-best fallback);
stub-regression guard at the write boundary; a `tweaks` panel binding CSS
custom properties to a localStorage control strip.
