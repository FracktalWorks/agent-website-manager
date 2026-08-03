# Print collateral — directory contract (DOX)

Anything that gets **manufactured**: business cards, fliers, standees. One-way
output. Read this before editing here.

## What lives here

| File | Owns |
|---|---|
| `press.py` | the engine — sheet sizes, bleed/trim/safe, fonts, QR, Chrome→PDF, `audit()`, `Gate` |
| `card.py` | the business card, 90×54mm |
| `leaflet.py` | **the A4 single-fold leaflet** — the format patient handouts use. Copy and diagrams imported live from `content/vitiligo.py` |
| `fliers.py` | flier copy, four conditions × three languages. No markup |
| `flier.py` | the A5 flier layout — **superseded by `leaflet.py`**, kept only until the leaflet covers the other three conditions |
| `standee.py` | the two entrance roll-ups |
| `out/` | generated. `*.pdf` goes to the press, `*-proof.png` goes to a human |

`../signage/` is the same engine at fabrication scale and came first; it owns
the fascia board and the Indic webfonts that `press.fonts_css()` reads. Do not
duplicate those fonts here.

## Placement rules (decide BEFORE writing)

| You are adding… | It belongs in |
|---|---|
| A new physical size | `press.SHEETS` |
| Words a patient will read | a content module (`fliers.py`-shaped), never in a layout file |
| A new artefact | its own `<thing>.py` that imports `press` |
| A brand fact (phone, address, hours, name) | **nowhere here** — import it from `../site/chrome.py` |
| A logo or mark | `../brand/`, inlined via `card.svg()` |

## Invariants that break silently if you skip them

- **Nothing is retyped.** Every name, number, address and Indic string is
  imported from `../site/chrome.py` or `../signage/board.py`. Retyping is how
  "Center" becomes "Centre" and nobody notices until it is cut in acrylic or
  boxed in thousands.
- **`audit()` reads the PDF back.** Page count, MediaBox in millimetres, and
  `/CharProcs` present with no `/FontFile` — that last one is what makes Telugu
  survive a press with no Indic font installed. Never bypass it.
- **A `Gate` is a person and a date**, not a boolean. An open gate stamps the
  proof and refuses to write the print PDF, because a file that exists is a
  file someone can email to a printer.
- **CSS `content` cannot hold a literal newline** — it invalidates the whole
  rule, and an unapproved proof then renders with no stamp and looks finished.
  Use `\A` with `white-space: pre-line`.
- **The proof body is pinned to one face wide.** Otherwise `margin: auto`
  centres the artwork inside a wider body and half of it leaves the screenshot.
- **Indic line-height is set per script.** A leading tuned on Latin collides in
  Telugu; `.te`/`.hi` overrides exist for every text class.
- **A folded piece is composed against the CREASE, not the trim.** On an A4
  bifold the front cover is the RIGHT half of the outside sheet and the back is
  the left; get it backwards and the leaflet is inside out. Pass
  `folds=(148.5,)` so the proof draws the crease, then check every headline
  against it.
- **A panel is a fixed rectangle and content silently runs past its bottom
  edge.** `overflow: hidden` hides the evidence, so look at the proof. Cut with
  `leaflet.first(text, n)` — whole sentences off the front of the published
  paragraph — rather than rewriting, or the leaflet becomes a second source
  needing its own review.
- **A callout pin is a percentage of its parent, so the parent must BE the
  picture.** With `object-fit: contain` a wide diagram letterboxes inside a
  full-width box and every pin lands short of the artwork. `callouts.py`
  shrink-wraps the stage; do not put a width on it.
- **Callout coordinates are never re-authored for print.** `callouts.py` reads
  the same `labels` the site's diagram sections carry, so a label moved on the
  site moves here on the next build. Two coordinate sets drift silently.
- **Everything vertical is a multiple of the baseline** (`leaflet.BASE`,
  4.5mm), expressed in millimetres, not ratios. A ratio drifts off the grid the
  moment a size changes and the two inside panels stop ruling off level.
- **Layout hierarchy follows `agent-data/design-systems/_craft/`.** Editorial
  display sits 3–5× body, not 2× — the first A5 fliers ran 9mm over 3.9mm and
  read as forms. See `typography-hierarchy-editorial.md` and `anti-ai-slop.md`.

## Gates

- Any change: re-run the artefact's script and **look at `out/*-proof.png`**.
  The audit proves the file is well-formed, not that the layout is right.
- Changing `press.py`: re-run `card.py`, `flier.py` and `standee.py` — they
  are the only tests it has.
- Changing flier copy: the clinical gate reopens. Medical claims are reviewed
  by Dr. Varada before anything prints, same rule as the diagrams.
- Changing an Indic string: the language gate reopens. Rendering correctly is
  not reading correctly.

## Open

- **Standee size is a guess.** 850×2000mm is the Indian roll-up standard, not a
  measurement of your fabricator's hardware. Get it, set it, re-run.
- **The clinic standee reserves a band for a portrait** shot for print. A web
  hero upscaled to 600mm is a blurred doctor.
- Telugu and Hindi for hair-loss and acne were written here and have never been
  read by a native speaker.
