---
name: brand_assets
description: >
  Produce the square, circular and wide artwork every platform demands from a
  brand — favicons, Google Business logo and cover, WhatsApp profile and
  catalogue tiles, social cards, signage — by rendering from the brand's own
  SVG lockups, then measuring each asset at the size the platform draws it.
when_to_use: >
  The user asks for a logo/tile/cover/icon "for WhatsApp / Google / the app
  store / social", sets up a business profile, or an existing asset looks
  wrong small, cropped round, or illegible in a grid.
authority: write
cost_tier: 1
version: 1.0.0
---

# Brand asset studio

Platforms do not want "the logo". They want a specific rectangle, cropped a
specific way, read at a specific size — and they will crop, downscale and
circle-mask whatever you give them without asking.

## The one rule everything else follows from

**Judge the asset at the size it is consumed, never at the size it is
uploaded.** A 1024px tile is not the deliverable; the 150px cell in a
catalogue grid is. A favicon is not a 512px PNG; it is 16 pixels beside a
search result. Every failure in this skill's history was invisible at full
size and obvious at consumption size.

So: render a contact sheet at the consumption size and look at it before
delivering anything.

```bash
python .github/skills/brand_assets/scripts/asset_check.py <dir> \
       --spec whatsapp-catalogue --bleed 20 --sheet /tmp/sheet.png
```

The checker measures margins, circle spill and platform spec, and writes that
sheet. Its `--bleed` flag excludes a deliberate edge rule from the margin
measurement — an asset that bleeds to the edge on purpose is not the same as
one that has run out of room.

## Platform specs worth knowing before designing

| Slot | Shape | Minimum | Drawn at | Watch for |
|---|---|---|---|---|
| Favicon (`/favicon.ico`) | square | side a multiple of **48** | 16–24px | must sit at the site root; see `search_presence` |
| Google Business logo | square, **circle-cropped** | 250px (720 ideal) | 48–96px | corners are discarded |
| Google Business cover | 16:9 | 1024×576 | wide, centre-cropped | keep type off the outer 10% |
| WhatsApp profile | square, **circle-cropped** | 192px | 40–64px | corners discarded |
| WhatsApp catalogue item | square | 500px (640 common) | **~150px** | ≤5MB, JPG/PNG, ≤10 images per item |
| Open Graph card | 1.91:1 | 1200×630 | varies | must be an absolute URL and reachable cold |

**Circle-cropped slots need a different file from square ones.** A lockup with
a wordmark under the mark is correct in a square tile and loses its ends in a
circle. Keep both, and let the checker's `spill` figure decide which goes
where — it reports how much ink falls outside the inscribed circle.

## Rules learned the expensive way

**Never bake mutable data into artwork.** Prices, hours, phone numbers and
offers all have their own fields in every platform. A fee rendered into the
picture is a second copy that cannot be edited from the app, so the day the
fee changes the picture starts lying and nobody notices. Same failure class as
a caption naming a photograph that is no longer on the page.

**Items in a set must not look the same.** A catalogue of nine near-identical
logo squares forces the customer to read the captions, which defeats having
pictures. Name the thing in type large enough to survive the grid, and vary
the wording *shape* between items, not just the words — two tiles ending in
"…consultation" read as one tile at 150px. Reserve the plain logo tile for the
one slot that is genuinely about the practice rather than a service.

**Do not repeat the caption.** The platform already prints the item name under
the image. A tile that repeats it spends its whole surface on information the
customer can already see; use the surface for what the name leaves out (where,
when, who).

**Leave real margin.** 88% of the frame for artwork is generous; 92% put a
wordmark 4% from the edge, which is fine only if no surface ever trims. The
extra 4% of linear scale is invisible; a clipped wordmark is visible to
everyone. Below ~3% the checker fails it.

**One headline is the budget.** At grid size a tile says one thing. Subtitle
and chip are for the card and detail views, where there is room.

## Rendering pipeline

Two paths, both deterministic and both re-runnable:

1. **Vector → raster** for pure logo work: rasterise the brand SVG lockup at
   high resolution, then compose onto the frame with Pillow (`ink()` /
   `raster.py` in the reference implementation).
2. **HTML/CSS → headless Chrome → PNG** when the asset has type, layout or
   gradients. Write the HTML to a temp file, screenshot at the exact frame
   size, then re-encode to JPG and PNG.

For path 2, embed fonts as `@font-face` with local `woff2` files **and
`font-display: block`**. Without it the screenshot can win the race against
the font and you get a silently mis-set tile in the fallback face.

Always emit both **JPG (for upload) and PNG (for the contact sheet and for
further composition)**. Save JPG at `quality=95, subsampling=0` — chroma
subsampling is what smears coloured type at small sizes.

Keep the generator as a script in the brand directory, not as a one-off. Every
asset gets regenerated when the brand shifts, and a script that produced the
whole set is the only thing that makes that a five-minute job.

## Profile copy has hard limits — check before writing

Limits differ between a platform's app and its API for the *same* field, and
writing to the wrong one wastes the draft:

| Field | Limit |
|---|---|
| WhatsApp Business **app** description | **256** characters |
| WhatsApp Business **API** description | 512 |
| WhatsApp **About** line | 139 |
| Google Business description | 750 |

Write to the smaller limit when a migration is likely, and keep the longer
version alongside it.

## Reference implementation

`outputs/drvarada-site/brand/` is a complete worked example:

| File | What it shows |
|---|---|
| `tools/lockup.py`, `tools/raster.py` | SVG lockup generation and rasterising |
| `tools/icon_system.py` | one mark, every icon size and treatment |
| `google_logo.py` | circle-safe square logo + 16:9 cover, with previews |
| `whatsapp_assets.py` | catalogue tiles via headless Chrome + the 150px grid preview |
| `../signage/board.py` | the same pipeline at physical scale (mm, print) |

Each carries its reasoning in the docstring, including the sizes that were
tried and rejected. Read the docstring before changing a number in it.
