# Site engine — directory contract (DOX)

What this directory owns and where a change belongs. Read this before editing
here; update it if your change moves a boundary.

## What lives here

The **site generation engine** plus the drvarada site's content. The engine
files are copied verbatim by `new_site.py` into every new site — so an engine
change here changes every future site, and site-specific values must never
leak into engine files.

## Placement rules (decide BEFORE writing)

| You are adding… | It belongs in |
|---|---|
| Page copy, sections, FAQs, images | `content/<module>.py` (data only, no markup) |
| A new page | `content/urls.py` first (slug → URL), then its module's `PAGES` |
| Markup, a new block renderer, schema.org | `chrome.py` (the ONLY place HTML lives) |
| A build-time validation gate | `build.py` (`BANNED`/`NEGATION`/`SLOP` or a new check) |
| Which modules/constants exist for THIS site | `siteconf.py` (the single seam — never re-list in engine files) |
| Editing behavior (server routes, transactions) | `editor.py` |
| Editing UI (overlay, panels, device preview) | `editor/editor.js` + `editor/editor.css` |
| Address-based source patching | `datapatch.py` (AST spans; read-back verify is mandatory) |
| Value-based text matching | `resolver.py` (owns `char_col` — UTF-8 byte→char columns) |
| Link discovery/retargeting | `linkscan.py` (walks renderer positions, never text) |
| Version history semantics | `versions.py` (append-only; restore writes forward) |
| Image processing | `media.py` (decode-verify, EXIF bake, strip, cap, re-encode) |
| Brand/design-system application | `brandkit.py` (OKLCH derivation, AA repair) |
| Cross-project workspace UI | **not here** — `hub.py` at the repo root |

## Invariants that break silently if you skip them

- Every span write **reads the address back** and rolls back on mismatch.
- `ast` col_offsets are UTF-8 **bytes**; always convert via `resolver.char_col`.
- Preview builds stamp `data-od*` addresses; production builds must not
  (build asserts it).
- The editor's tracked set (`tracked()`) must include every file an edit can
  touch — a file outside it survives rollbacks half-changed.
- Port-in-use is detected by **connect probe**, never bind failure (Windows
  SO_REUSEADDR lets a double bind succeed).

## User feedback — read `.feedback/` FIRST when asked to improve the site

The live editor's **Note** tool pins "change this to that" to an element and
writes it here for you:

- `.feedback/notes.jsonl` — one JSON object per line. `status: "open"` items
  are unactioned requests. Each carries `slug`, a `data-od` address (`addr`)
  or CSS path (`sel`), the element's `value` at the time it was pinned, and
  `file` + `line` — the source location the address resolved to **then**.
  Treat the location as a strong lead, not a promise: confirm it before
  editing, because the file may have moved on since.

Patch the address, not the text. An address is unambiguous; a string is not.

After acting on an item, set its `status` to `"done"` (add a `resolved`
timestamp) — the editor shows open items as pins, so stale entries mislead.

How this reaches you (don't duplicate it): a **UserPromptSubmit hook**
(`.claude/hooks/feedback_context.py`) injects open items into every Claude
Code prompt, and the editor's **⚑ Agent** button turns the whole queue into
one prompt the user can paste into any chat. Reading and resolving are plain
file operations on `notes.jsonl` — no tool needed.

A `site-feedback` MCP server used to front this folder. It was unregistered
2026-07-31: `list_feedback` and `resolve_note` were a process and two tool
schemas per session wrapping a file you can already Read and Edit. The script
is still at `.tmp/scripts/feedback_mcp.py` if it is ever wanted back.

Two things were removed on 2026-07-31 and should not come back without a
reason: **Mark** (drawing on the page) and **Shot** (server-side screenshots,
`kind: "shot"` entries, `shot-*.png`, the `get_screenshot` MCP tool). Both
existed to show the agent what the user was looking at, which the user can do
by screenshotting their own screen and pasting it. Neither could say *which
value in which file* a pixel came from — that is what the address carries, and
it is the part worth maintaining.

## Gates

- Engine change (`versions.py`, `datapatch.py`, `resolver.py`, `linkscan.py`):
  `python -m pytest tests/test_site_engine.py` (repo root)
- Editor HTTP surface: `python tests/live_editor_parity.py` against a running
  editor (it restores from its own byte copies — never from the store).
- Rendering: `python verify.py --all` (real Chrome, 5 widths, overflow +
  broken images). Static checks pass pages that render broken.
