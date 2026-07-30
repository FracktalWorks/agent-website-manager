# drvarada.com — site build

The whole site is generated. **Nobody edits HTML by hand** — pages are data in
`content/`, markup lives once in `chrome.py`, and `build.py` assembles and validates
everything. One edit to a block renderer fixes all 45 pages at once.

This repo is the single source of truth. Open Design was used earlier as a review
mirror; it has been retired for this project — the copies still sitting there are
stale and safe to delete. Preview locally instead (below).

## Commands

| Command | Does |
|---|---|
| `python build.py` | Validate + build preview site → `dist/` (flat `.html` links) |
| `python build.py --links=production` | Same, with real WordPress URLs → `dist-prod/` |
| `python preview.py` | Build, serve `dist/` at http://127.0.0.1:8788, open browser |
| `python editor.py` | **Live editor** — serve `dist/` at http://127.0.0.1:8789 with in-page editing |
| `python verify.py` | Render the pages in real Chrome at 4 widths; fail on sideways scroll or broken images (`--all` for all 45) |

The build **fails** (non-zero exit) on: broken internal links, more than one dark
band per page, missing title/meta/FAQ/related, meta descriptions out of range,
NMC/IMC advertising violations (superlatives, guarantees, cure claims — a negation
window keeps compliant statements like "no treatment cures vitiligo" legal), filler
copy or unattributable metrics, AI-default accent colours, and raw colour values in
`site.css` outside its `:root` token block. It **warns** on titles over 60 chars and
three consecutive sections of the same kind.

`build.py` proves the data is right; it cannot prove the page *renders*.
`verify.py` does that — it loads each built page in real Chrome at 390 / 768 /
1040 / 1440px and fails on horizontal scroll or images that didn't load. It found
a live bug the day it was written: the footer carried an inline
`grid-template-columns` with five columns, which outranks any stylesheet media
query, so every one of the 45 pages scrolled sideways on a phone. Run it before
any deploy.

## Live editing — edit the page, not the code

```
python editor.py
```

Then in VS Code: `Ctrl+Shift+P` → **Simple Browser: Show** → paste
`http://127.0.0.1:8789/`. (Any browser works too; Simple Browser just keeps it
beside the source.) Click **✎ Edit** and the rendered page becomes the editing
surface.

| What you click | What you get |
|---|---|
| Text | edit in place — **Enter** saves, **Esc** cancels |
| An image or an empty image slot | inspector: drag-drop a file, alt text, focal point, consent |
| A button or CTA | inspector: label + destination (slug autocomplete or URL) |
| Hovering a section | toolbar: move ↑ ↓, duplicate ⧉, delete ✕ |
| **Tokens** in the toolbar | the design system's 42 tokens, with colour pickers |
| **Site** in the toolbar | Practo links, phone, WhatsApp, reviewer byline — one form |
| **Alt**+click anything | jumps VS Code to the source line behind it |
| Ctrl+Z / **Undo** | undo the last change (session stack, 40 deep) |

Everything is written back into the Python that produced it, then the site
rebuilds. Nothing lives in a database or a draft state — the repo is the
document.

### How it finds what to change

The preview build stamps a **data address** onto the markup it renders
(`data-od="sections.4.h2"`, `data-od-img="sections.6.items.0.before"` — see
`chrome.at`), so the browser names the exact value it edited and the server
patches that value via the AST. Production HTML carries none of these
attributes.

Copy nested inside a prose paragraph has no address, so it falls back to
matching on its text (`resolver.py`). That is the only path that can be
ambiguous — "Book on Practo" exists in 16 places, so the editor offers *change
all 16* or *cancel* rather than guessing.

Text assembled by an f-string in `chrome.py` belongs to the template, not the
content. The editor says so and points at the file instead of pretending.

### Things worth knowing

- **The validator reviews every edit at the moment you make it.** A superlative,
  a link to a slug that doesn't exist, a patient photo with no consent record —
  the change is **reverted**, uploaded files are deleted, and the build's own
  objection appears in the browser. The source never holds an illegal claim.
- **Uploads are processed, not just stored.** EXIF orientation is baked into the
  pixels and then all metadata is stripped (which removes GPS and capture time —
  a requirement for clinical photography, not an optimisation), the long edge is
  capped at 1600px, and the result is re-encoded as progressive JPEG. A 6 MB
  phone photo becomes a ~100 KB asset with `width`/`height` recorded so the
  browser reserves the right box.
- **Before/after items promote themselves.** An unphotographed case is authored
  as a `(title, caption)` tuple; supplying its first image rewrites it as a dict
  so it has somewhere to put the photo.
- **Tokens instead of per-element styling.** Open Design's editor offers 33
  inline style properties per element, which is right for a standalone artifact.
  Here it would be pure drift — so the editor edits *design tokens* instead,
  which restyle every page consistently and cannot detach from the design
  system.
- The editor watches `content/*.py`, `chrome.py`, `assets/*.css` and the design
  system: when the agent (or you) edits code, the site rebuilds and every open
  tab reloads with scroll position kept. `editor/` holds the injected overlay and
  is never part of a build.

## Layout

```
site/
├── build.py            assembler + validator + sitemap/robots/site-manifest.json
├── chrome.py           ALL markup: header, nav, footer, block renderers, schema.org
├── preview.py          local preview server
├── verify.py           renders each page in real Chrome at 4 widths
├── editor.py           live-edit server (serve, apply edits, watch, reload)
├── datapatch.py        edit page data BY ADDRESS (sections.4.items.0.before)
├── resolver.py         edit copy BY VALUE — the fallback for unaddressed text
├── media.py            uploads: orientation, metadata strip, downscale, encode
├── editor/             injected overlay (editor.js + editor.css) — never built
├── assets/site.css     layout only — every colour/type/radius token comes from the
│                       design system (../design-system/), never hardcoded here
├── assets/img/         photography supplied through the editor
└── content/
    ├── urls.py         slug → production URL (the only place IA is defined)
    ├── brand.py        T3: home, doctor, locations, contact, results, stories, blog
    ├── vitiligo.py     T2: national hub + 8 cluster pages
    ├── psoriasis.py    T2: national hub + 7 cluster pages
    ├── hyderabad_medical.py   T1: chronic conditions + trichology pillars
    └── hyderabad_skin.py      T1: inflammatory skin + aesthetics pillars
```

The design system source is `../design-system/` (DESIGN.md + system/variables.css +
its own build.py). The site copies its compiled CSS in at build time as
`assets/design-system.css`.

## Rules that bind every page (do not relax in copy edits)

1. **Practo is the only booking path.** Every CTA terminates in Practo; phone and
   WhatsApp sit below it, never beside it as an equal choice. No booking forms.
2. **No cure claims** for vitiligo/psoriasis/eczema/alopecia; no superlatives, no
   guarantees, no named competitors; every number attributable. The linter enforces
   this, but write compliantly rather than around the linter.
3. **One page owns one query cluster** (see `content/urls.py` and
   `../seo/KEYWORD_MAP.md`). National hubs never carry a city; city pages always do.
4. **Band rhythm**: max one dark section per page — the utility bar and footer
   already spend two of the three allowed.

## Deploy

WordPress on Hostinger via deploy-canvas (direct HTML, `elementor_canvas` template),
per `outputs/drvarada-master-plan/MASTER_PLAN.md` §7. Deploy from `dist-prod/`.

Outstanding before production: clinic phone/WhatsApp numbers, street addresses
(`TODO` markers — `build.py` counts them), portrait of Dr. Varada, consented
before/after images, Practo deep links (currently practo.com root).
