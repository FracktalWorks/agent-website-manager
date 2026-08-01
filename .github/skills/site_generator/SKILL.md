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
| `siteconf.py` | What THIS site is made of: content modules, editable constants, link constants. Read by `build.py`, `linkscan.py`, `editor.py` and `resolver.py` — it exists because that list used to be written out in all four, and a module missing from one of them failed silently. |
| `chrome.py` | ALL markup: header, nav, footer, block renderers, schema.org, `img()`/`slot()`/`at()`. One edit fixes every page. |
| `build.py` | Assembler + validator + sitemap/robots + `site-manifest.json`. Validation is not optional. |
| `datapatch.py` | Edits page data **by address** (`sections.4.items.0.before`) via AST spans — creates missing keys, reorders/duplicates/removes list items, rewrites module constants. |
| `versions.py` | Version timeline, ported from Open Design's `project-file-versions.ts`: append-only, restore-writes-forward, content-addressed blobs, parent links so undo follows the edit lineage. Also a recovery CLI — `where` / `list` / `show <n>` / `restore <n> [--dry-run]` / `export <n> <dir>` — which works with the editor stopped, because that is usually why you want it. |
| `linkscan.py` | Every link on the site by walking the *renderer's* positions in the page data. `where <target>` / `audit`; powers the inspector's this-one-or-all-N choice. |
| `resolver.py` | Edits copy **by value** — the fallback for text with no address. Also owns `char_col`, the UTF-8 byte→character column conversion every span write must use. |
| `media.py` | Upload pipeline: verify by decoding, bake EXIF orientation, strip all metadata, cap the long edge, re-encode, report dimensions. |
| `editor.py` | Live-edit server: injects the overlay, applies edits inside a transaction that reverts source *and deletes uploaded files* if the build fails, watches sources, SSE-reloads every tab. |
| `editor/editor.js\|css` | The injected overlay: hover-pick, in-place text editing, inspector panels (image/link/tokens/site/pages), section toolbar, undo/redo, open-in-code, and a device preview (Screen button — phone/tablet/laptop/wide/desktop at verify.py's exact widths, in a scaled iframe so media queries are honest; editing keeps working inside it). Never part of a build. |
| `brandkit.py` | Drives the site from any corpus design system: reads its canonical `:root`, derives this site's tokens in OKLCH, repairs contrast, writes `assets/brand.css`. `list` / `show <id>` / `apply <id>` / `apply --native` / `calibrate` / `check`. |
| `preview.py` | Plain build+serve, no editing. |
| `verify.py` | Renders every built page in real Chrome at 390/768/1040/1440px and fails on horizontal scroll or broken images. Measures inside an iframe of the exact width because Chrome on Windows clamps windows to ~500px, and ignores elements clipped by a scrolling ancestor so intentional marquees and scrollable tables don't false-positive. |

Run: `python build.py` (preview), `python build.py --links=production`,
`python editor.py` (live editing at http://127.0.0.1:8789; `--port N` for a
non-default port), `python preview.py` (plain preview at http://127.0.0.1:8788).

**The workspace shell** — `python hub.py` at the repo root
(http://127.0.0.1:8780, VS Code task "workspace hub (preview in VS Code)") —
is the app window Open Design used to be, with its navigation model: a
persistent tab bar whose pinned ⌂ Home is always one click away, one tab per
opened project or design system (kept-alive iframes — switching tabs never
reloads an editor mid-edit), hash routing so browser back/forward walks tabs,
and tabs restored across reloads from localStorage. Home shows every
`outputs/*/site` as a card (live scaled-iframe thumbnail via OD's
`100cqw/1280px` 16/9 trick, sorted by last build, relative updated-at) with
Start&nbsp;&amp;&nbsp;open spawning that site's editor on its own port (drvarada keeps
8789, others 8791+), plus the searchable 152-package design-system corpus. A
project tab gets a filterable sidebar of every page from
`site-manifest.json` — the editor announces its current page to the shell
over cross-origin postMessage — and a design-system tab gets the package's
`components.html` with its colour/type/spacing previews and an all-systems
quick switcher. **Ctrl+P / Ctrl+K** (or the ⌕ button) opens a quick switcher
across every page, project and design system, with recents. Site-owned
design systems (`outputs/<site>/design-system/`, see
[design_system_management §4b](../design_system_management/SKILL.md)) appear
first badged **yours**, swatches read live from `system/variables.css`;
vendored systems offer an **Apply to project** action that runs the site's
`brandkit.py apply` from the shell. The editor's device stage also carries
zoom presets (Fit / 50–200%). The shell's **+ New project** scaffolds a real
site via `new_site.py` (with an optional corpus brand applied on creation),
and **+ Create** (design systems) writes an agent brief to `inputs/briefs/`.

### Feedback loop — right-click a reference, or Note a change

Two gestures, both producing something an agent can act on without searching:

- **Right-click any element** (edit mode or not) → a reference block on the
  clipboard, ready to paste into a chat:

  ```
  [site-ref] drvarada-site · page index · sections.0.h2
  source: outputs/drvarada-site/site/content/brand.py:45
  kind: text
  current: "What brings you in?"
  ```

  Use it to talk about one element right now. Nothing is stored.

- **Note** (toolbar) → pin "what should change here" to an element. Pin as
  many as you like across as many pages as you like, then **⚑ Agent** turns
  the whole queue into a single numbered prompt — every element with its
  address, source line, current value and requested change — to paste into
  any chat. Pins render on the page with a Resolve button.

Notes land in `<site>/.feedback/notes.jsonl` (`status: open|done`). The source
file and line are resolved **at pin time** and stored, because an address is
only meaningful against the data it was written from. **Agent contract: read
`.feedback/` before improving a site; mark items `done` after acting** (see
the site's AGENTS.md).

**Mark** (drawing on the page) and **Shot** (server-side screenshots) were
removed 2026-07-31, along with `shot-*.png` and the `get_screenshot` MCP tool.
Both existed to show the agent the user's view, which a normal screenshot
pasted into chat does with fewer moving parts. What survives is the half no
image can supply: which value, in which file, on which line.

**How feedback reaches the chat sidebars:**

- **Push, Claude Code only**: a `UserPromptSubmit` hook
  (`.claude/hooks/feedback_context.py`, wired in `.claude/settings.json`)
  injects all open items into every prompt — the user annotates in the
  browser, switches to the Claude sidebar, and just types "fix these".
  Silent (zero tokens) when nothing is open; caps at 15 items.
- **Pull, any agent**: the editor's **⚑ Agent** bar chip shows the open count
  and opens a panel with every item, a Resolve button each, and **Copy prompt
  for all N** — the whole queue as one numbered brief. Clipboard degrades
  clipboard API → `execCommand("copy")` over a selected textarea → leave the
  textarea up for a manual Ctrl+C. VS Code's Simple Browser webview refuses
  `clipboard-write` AND swallows `window.prompt`, so never use a blocking
  modal as the fallback.

A `site-feedback` MCP server (`.tmp/scripts/feedback_mcp.py`) used to front
this folder for both sidebars. **Unregistered 2026-07-31** — its two tools
were a process and two tool schemas per session wrapping a JSONL file any
agent can already read and edit. Reading and resolving are file operations.
The script is still on disk if it is ever wanted back; re-add it to
`.mcp.json` and `.vscode/mcp.json`.

**In VS Code:** run the task **"drvarada: live editor (preview in VS Code)"**
(Terminal → Run Task) — it starts the server if needed and opens the page in
VS Code's own browser pane in one step. The mechanism, since no CLI can invoke
an editor command: a `tasks.json` input of `"type": "command"` running
`simpleBrowser.show` with the URL as args, referenced as the task's
`${input:…}` command. `editor.py` cooperates by binding its port *before* the
first build (an instantly-opened pane gets a self-refreshing "building…" page,
never a connection refused) and by exiting 0 with a message when another
instance already serves the port — so the task is safe to re-run. Manual
route: `Ctrl+Shift+P → "Simple Browser: Show" → http://127.0.0.1:8789/`.
When `editor.py` detects a VS Code terminal (`TERM_PROGRAM=vscode`) it prints
these hints instead of yanking focus to the OS browser (`--open` forces it).
The user edits the page in the editor pane; saved edits land in `content/*.py`
in the same window. Alt+click anything jumps VS Code to the exact source line.

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

### Device preview (ported from Open Design's FileViewer)

The **⛶ Screen** button previews the page at phone 390×844, tablet 768×1024,
laptop 1040×800, wide 1240×800 or desktop 1440×900 — the widths `verify.py`
tests, because they are where this stylesheet makes its decisions. The
mechanism is Open Design's three-layer stage: an iframe laid out at *true*
device pixels inside a clip sized at *scaled* pixels, `transform: scale()`
fitted to the window and never upscaled — so media queries, `vw` units and
`innerWidth` inside the frame are all honest, and scrolling behaves like the
real device. Additions OD does not have: a rotate button, a live "scrolls
sideways" warning (verify.py's key measurement, computed on every load), and
**editing keeps working inside the frame** — the framed overlay hides its
toolbar and hands reload/mode control to the host page via `window.__odApi`,
while the host holds the single SSE connection and reloads only the frame on
rebuilds. The chosen device survives reloads (sessionStorage), and the
**Pages** panel navigates within the frame while it is up.

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

**Scaffold it — do not copy a folder by hand.**

```bash
python .github/skills/site_generator/scripts/new_site.py acme --title "Acme Ltd"
cd outputs/acme-site/site && python build.py && python verify.py --all
```

That produces a site which **builds, verifies, edits and versions on the first
run**. The engine modules are copied verbatim (they are genuinely site-agnostic);
the three things that are not — `siteconf.py`, `chrome.py`, `content/` — are
generated fresh and minimal, so you are not deleting a dermatology clinic out of
your new client's navigation. `PORTING.md` in the new directory lists what to
replace, in order.

Then:

1. **Design system first.** Either pick one from the 152-package corpus or
   author one — see [design_system_management](../design_system_management/SKILL.md)
   (`python .tmp/scripts/design_systems.py search "<brief>"`, then `show <id>
   --root` for the `:root` block to paste). The site's own CSS is layout-only;
   raw colours outside a `:root` component-token block fail the build.
2. Write `content/urls.py` from the keyword/IA map FIRST — one page, one query
   cluster.
3. Add domain compliance rules to `build.py` (`BANNED`/`NEGATION`) for the
   client's regulatory reality; keep the `SLOP` list as is. The reference site's
   `build.py` is where to copy the richer gates from.
4. Author content as data, applying `references/craft.md` and the fuller
   rulebooks in `agent-data/design-systems/_craft/`. Brand tokens win on value
   conflicts; craft rules cover everything the brand does not override.
5. Run `python verify.py --all` before shipping, and screenshot-verify the
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

**Open Design itself is retired** (2026-07-30). Nothing in this skill requires it
to be running, and no new work should start it. What it used to provide lives
here: page generation (this skill), design systems (`agent-data/design-systems/`,
152 vendored), version history (`versions.py`), visual editing (`editor.py`).
Publishing to WordPress is [html_deploy](../html_deploy/SKILL.md), which was
called `open_design_integration` and never needed the app either.

The engine gate is `python -m pytest tests/test_site_engine.py` — run it after
touching `versions.py`, `datapatch.py`, `resolver.py` or `linkscan.py`.
`tests/live_editor_parity.py` covers the HTTP surface against a running editor.

Ported: content/renderer split, always-validating builder, anti-slop
constants + token-scope CSS lint (`lint-artifact.ts`), layout-rhythm caps
(taste-skill §4.7), `site-manifest.json` (design-manifest idea), live-edit
loop (manual-edit-mode, rebuilt source-first: they re-serialize the DOM, we
rewrite the authored literal — ours diffs cleaner), craft references.

Also ported since: the token tier model (A1/A2/slot/extension) and a
derive step — `brandkit.py` derives a full site palette from a brand's
canonical tokens, which is Open Design's seed→derive idea applied at the
consumer end rather than the authoring end, and adds a contrast-repair pass
they do not have. And (2026-07-30) the FileViewer device preview — their
scaled-iframe stage at our verify.py widths, plus rotation, a live overflow
warning and in-frame editing, none of which upstream has; their draggable
inspector card; and a Pages navigator. Upstream has **no** VS Code
integration at all — the Simple Browser task in `.vscode/tasks.json` is
original (see "In VS Code" above).

Worth porting when needed: authoring-side **seed → derive** (a ~20-field
seed.json that derives a design system's own palette ladders, type scale and
dark mode, so rebranding a *system* is a one-field edit); design-jury critique loop
(5 weighted panelists, threshold 8/10, max 3 rounds, ship-best fallback);
stub-regression guard at the write boundary; a `tweaks` panel binding CSS
custom properties to a localStorage control strip.
