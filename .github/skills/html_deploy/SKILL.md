---
name: html_deploy
description: >
  Publish a finished HTML page to WordPress — verbatim onto Elementor's canvas
  template (the default), or converted to native Elementor widgets when the page
  must stay hand-editable in WP. Works with any HTML, whatever produced it.
when_to_use: >
  User has an HTML page (from the site_generator skill, from a design system, or
  hand-written) and wants it live on a WordPress site.
authority: write
cost_tier: 2
version: 1.0.0
---

# HTML → WordPress

> Takes an HTML file. Puts it on the site. The file's origin is not this skill's
> business, which is exactly why it survived the retirement of the thing that
> used to produce those files.

## This skill was `open_design_integration`

Until 2026-07-30 page design happened in **Open Design**, a separate application
that had to be running, and this skill was the bridge between it and WordPress.
That dependency is gone. Four things replaced it, all in this repo:

| What Open Design did | What does it now |
|----------------------|------------------|
| Generated page HTML from a design system | [`site_generator`](../site_generator/SKILL.md) — data → HTML, plus a live visual editor |
| Held the design systems | `agent-data/design-systems/` — 152 vendored, see [`design_system_management`](../design_system_management/SKILL.md) |
| Version history for edits | `versions.py` in the site directory — a port of Open Design's own model |
| Visual editing of a rendered page | `editor.py` — click-to-edit over the real render |

**Do not start Open Design for new work.** If a task appears to need it, what it
actually needs is one of the four rows above. The one exception is an older
project whose source of truth still lives in an Open Design workspace; those are
read-only history now, and the `open-design-daemon-http-api` memory note covers
reaching one if you ever must.

The bridge script keeps its filename — `.tmp/scripts/open_design_bridge.py` — on
purpose. Renaming it would invalidate every command recorded in memory and in the
other skills for no behavioural gain. It has never needed Open Design running: it
reads an HTML file and writes to the WordPress REST API.

## Where the HTML comes from

Generate it in-repo. [`site_generator`](../site_generator/SKILL.md) has the full
flow; the short version is that pages are Python data, `build.py` renders them,
`verify.py` proves they render clean at four widths, and `editor.py` lets someone
edit the result visually with the edits going back into the source.

Pick a design system before designing anything from scratch —
`agent-data/design-systems/INDEX.md` lists all 152 and
`.tmp/scripts/design_systems.py` searches them.

If the page will take the **Elementor fallback** (§2 below — not the default),
author it to convert cleanly:

> No `::before`/`::after` for structural or decorative content (render real
> elements). No CSS Grid with non-uniform tracks like `2fr 1fr` (use flex rows
> with explicit % widths). Don't rely on `flex: 1` alone for fixed-width columns
> (set explicit width/flex-basis %). Images that must fill their container set
> `object-fit:cover` on the `<img>` itself. Use HTML entities (`&rarr;`,
> `&mdash;`) rather than raw UTF-8 arrows and dashes.

`agent-data/design-systems/fracktal-works/DESIGN.md` bakes this into its own
"Elementor-safe authoring" section. No other system does, so include the
instruction unless that system's DESIGN.md documents equivalent constraints.

## 1. `deploy-canvas` — THE DEFAULT

Publishes the HTML **verbatim** as a single Gutenberg Custom HTML block on
Elementor's chrome-free `elementor_canvas` template. One REST write: no widget
conversion, no kit globals, no per-post CSS regeneration, no manual editor step.

```bash
python .tmp/scripts/open_design_bridge.py deploy-canvas \
  --html outputs/design_pages/[slug].html \
  --title "Page Title" \
  --slug "page-slug"
# --id <page_id> to update an existing page; --status publish to go live
```

Why it is the default (full story in the `open-design-canvas-vs-elementor`
memory note):

- The HTML is already a complete, styled page. Converting it to Elementor's
  widget model is what loses fidelity and drags in the fragile kit-globals →
  CSS-regeneration → stale-render pipeline that eats hours.
- The admin app-password has `unfiltered_html`, so raw `<style>`/markup is stored
  and served intact (admin users, single-site WordPress only).
- No `uploads/elementor/css/post-N.css` is generated, so "CSS didn't regenerate /
  needs an editor Update / stale render" **cannot happen**. LiteSpeed purges the
  URL on the REST update like any normal page.

**Header/footer.** Default is the chrome-free canvas. To keep the site's Elementor
header and footer, add `--header-footer`:

```bash
python .tmp/scripts/open_design_bridge.py deploy-canvas \
  --html outputs/design_pages/[slug].html --title "..." --slug "..." \
  --id <page_id> --status publish --header-footer
```

That switches to `elementor_header_footer` AND scopes every design selector under
`.od-embed` (via `_scope_css`) so the design's generic rules (`body`, `h2`, `a`,
`.wrap`) cannot restyle the chrome. Verified: header links keep their colour, the
page body keeps the theme font, and the design still renders correctly inside the
wrapper. Use it for pages that sit in the site nav; omit it for full-bleed
landing pages.

**Structured data.** `deploy-canvas` strips `<style>`/`<script>` when embedding
the body but **preserves `<script type="application/ld+json">`**, re-emitting it
inside the Custom HTML block. So put FAQPage / Product / HowTo schema in the
source HTML's `<head>` and it survives every redeploy. Yoast still emits the
WebPage/Organization/Breadcrumb graph on top. Yoast cannot auto-detect an FAQ
inside raw canvas HTML, so FAQPage must be added this way rather than via a Yoast
block.

**The tradeoff.** The page is an opaque HTML blob in WordPress — not editable in
the Elementor or Gutenberg UI. The source of truth is the file in this repo;
re-run `deploy-canvas` to change it. For design-driven pages that is the right
trade, and now that the source lives in-repo with its own visual editor and
version history, it costs less than it used to.

**Lazy-load.** Images can flash as grey placeholders on first paint if
LiteSpeed's lazy-load JS is stale (site-wide `693.js` issue); a LiteSpeed *Purge
All* fixes it. They load on scroll regardless.

## 2. `deploy-elementor` — fallback, only when WP-editable is required

Use this **only** when someone genuinely needs to edit the page inside Elementor
afterwards. It converts the HTML to native widgets via `html2elementor`
(convert → import → kit-merge). Lower fidelity, and it **requires a manual
Elementor "Update" after deploy** to regenerate the per-post CSS and clear the
stale render — a REST write alone does not fire Elementor's save pipeline.

```bash
python .tmp/scripts/open_design_bridge.py deploy-elementor \
  --html outputs/design_pages/[slug].html --title "Page Title" --slug "page-slug"
# then: open in the Elementor editor, click Update, then verify:
python .github/skills/elementor_builder/scripts/verify_fidelity.py \
  --source outputs/design_pages/[slug].html --live https://fracktal.in/page-slug/
```

If `verify_fidelity.py` reports drift, patch via the `elementor_builder` skill's
fidelity-patch step (`elementor-fidelity-patch-workflow` memory note). The
converter emits **direct colours, not kit-global refs** — global-colour refs
silently fail to resolve on REST-deployed pages, so never reintroduce them.

## Quick reference

| Task | Command |
|------|---------|
| Generate the HTML | [`site_generator`](../site_generator/SKILL.md) — `python build.py` in the site directory |
| List design systems | `python .tmp/scripts/design_systems.py list` |
| **Deploy (DEFAULT)** | `python .tmp/scripts/open_design_bridge.py deploy-canvas --html <file> --title <title> --slug <slug>` |
| Deploy keeping site chrome | add `--header-footer` |
| Deploy as Elementor widgets | `python .tmp/scripts/open_design_bridge.py deploy-elementor --html <file> --title <title>` |
| Check fidelity after Elementor deploy | `python .github/skills/elementor_builder/scripts/verify_fidelity.py --source <file> --live <url>` |
| Update an existing page | add `--id <page_id>`; `--status publish` to go live |
| Legacy raw HTML into post_content | `python .tmp/scripts/open_design_bridge.py deploy --html <file> --title <title>` |
