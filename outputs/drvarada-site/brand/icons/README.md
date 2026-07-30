# Icon system — Dr. Varada's Skin & Hair Center

The icon is always **the full mark**: follicle, molecular field on the left, cell field
on the right. There is no separate reduced symbol. What changes with size is how much
detail the mark can physically carry, so the same composition is re-engineered into four
tiers.

## The one rule

**Pick the tier by the size the icon is *displayed* at, not the size of the file you upload.**

Practo, Google Business, Instagram and WhatsApp all want a 512 px upload, then show it at
40–96 px using their own downscaler. Upload the `full` tier and their downscaler mashes
the 34-element field into grey. `profile-512.png` is deliberately built from the **compact**
tier for exactly this reason — it is a 512 px file drawn for a 48 px destination.

## Tiers

| Tier | Display size | Elements | Colour | How it is built |
|------|--------------|----------|--------|-----------------|
| `full` | 128 px and up | 36 | 7-tone ramp | Every path of the source artwork, untouched |
| `compact` | 44 – 96 px | 32 | 3 tones | Sub-pixel specks culled; ramp flattened; 3-unit dilation |
| `micro` | 24 – 40 px | 14 | 2 tones | Field normalised to 14 discs; follicle dilated 8 units |
| `nano` | 16 – 20 px | 9 | 2 tones | Field normalised to 9 discs; follicle dilated 10 units |

Two techniques do the work:

- **Dilation** — each path is stroked in its own fill colour, growing it outward by half
  the stroke width. Without it a 23-unit dot renders at 0.5 px and disappears.
- **Disc normalisation** (micro and nano) — below ~40 px the irregular dot and hexagon
  outlines anti-alias into grey mush. Replacing each surviving element with an equal disc
  at its own centroid lands it cleanly on the pixel grid, so the field reads as deliberate
  rather than noisy. Verified by rasterising and inspecting at true size.

Elements are chosen largest-first, and any element whose centre falls within a minimum
distance of one already kept is skipped — two dilated neighbours that close would fuse
into a single blob.

## Files

### Vector

| File | Use |
|------|-----|
| `icon-{tier}-navy.svg` | Brand navy tile, rounded — the default for avatars and app icons |
| `icon-{tier}-light.svg` | Porcelain tile, rounded — light UI surfaces |
| `icon-{tier}-transparent.svg` | No tile — when the host surface supplies its own background |
| `icon-compact-navy-square.svg` | Hard square — iOS applies its own mask, so the corners must not be pre-rounded |
| `favicon.svg` | Adaptive browser-tab icon; follows the viewer's colour scheme. Compact tier, since a single SVG cannot know what size it is being drawn at |

### Raster

| File | Built from | Use |
|------|-----------|-----|
| `favicon.ico` | nano 16 + micro 32 + micro 48 | Legacy browser tab. Each size is its own purpose-built render, not one image resampled three times |
| `favicon-16/32/48.png` | nano / micro | Individual tab icons |
| `apple-touch-icon.png` (180) | compact, square | iOS home screen |
| `icon-192.png` | compact | Android / PWA |
| `icon-512.png` | full | App stores, high-DPI, anywhere shown large |
| `profile-512.png` | **compact** | **Practo, Google Business Profile, Instagram, WhatsApp Business, Facebook** — displayed small |
| `profile-light-512.png` | compact, light tile | Same, where a platform surrounds avatars with dark chrome |

## Where each platform asset goes

| Platform | Upload | Displayed at |
|----------|--------|--------------|
| Practo profile photo | `profile-512.png` | ~64 px in search results |
| Google Business Profile logo | `profile-512.png` | 40–120 px |
| Instagram / Facebook | `profile-512.png` | 32–110 px |
| WhatsApp Business | `profile-512.png` | 48 px |
| Browser tab | `favicon.svg` + `favicon.ico` | 16–20 px |
| iOS home screen | `apple-touch-icon.png` | 60–180 px |
| Website nav | the full lockup, `../logo-mark-adaptive.svg` | 46 px tall |

## HTML head

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="manifest" href="/icons/site.webmanifest">
<meta name="theme-color" content="#1E3A63">
```

`favicon.ico` must sit at the site root — some crawlers and older browsers request
`/favicon.ico` directly and ignore the `<link>`.

## Rebuilding

Nothing here is hand-edited. From `brand/`:

```
python tools/colorize_logo.py   # the six full lockups
python tools/icon_system.py     # every tiered icon SVG
python tools/deliver.py         # PNGs + favicon.ico, via headless Chrome
```

All three read `source/varadas-logo-source.svg`. If the artwork is ever revised, rerun
them in that order. `tools/raster.py` holds the Chrome wrapper and expects Chrome at the
default Windows install path; intermediate renders land in `tools/_work/`.
