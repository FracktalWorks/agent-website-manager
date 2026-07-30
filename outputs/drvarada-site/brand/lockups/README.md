# Lockups — Dr. Varada's Skin & Hair Center

The symbol, the wordmark and the tagline, combined. Thirty-six SVGs: six forms × six
colourways. Every letterform is **outlined** — the artwork carries no font dependency,
so it renders identically on a machine that has never seen the typefaces.

## Forms

| Form | Shape | Use it for |
|------|-------|------------|
| `horizontal` | 3.3 : 1 | The default. Site header, letterhead, email signature, anything in a wide strip |
| `horizontal-tagline` | 2.8 : 1 | Same, where there is room to say what you do — ads, brochure covers, presentation title slides |
| `stacked` | 1.2 : 1 | Square-ish spaces: signage, a clinic board, a social post, a stamp |
| `stacked-tagline` | 1.1 : 1 | The fullest expression. Reception wall, front of a brochure, poster |
| `wordmark` | 4.2 : 1 | Where the symbol already appears nearby, or where it is too small to survive |
| `wordmark-tagline` | 3.4 : 1 | Document footers, certificates, anywhere the name must carry the tagline alone |

For favicons, profile pictures and app icons use the symbol on its own — see
[`../icons/README.md`](../icons/README.md). Never shrink a lockup into an avatar slot.

## Colourways

| Suffix | Use |
|--------|-----|
| `-light` | The primary. Navy name, grey descriptor, full-colour symbol, on white or porcelain |
| `-dark` | Navy, ink or photographic backgrounds. A considered re-step, not an inversion |
| `-flat-navy` | One-colour brand navy: signage, embroidery, screen print, stamps |
| `-mono-dark` | One-colour ink: fax, forms, engraving, newspaper |
| `-mono-light` | One-colour knockout white: dark print, etched glass, merchandise |
| `-adaptive` | Web only. Follows the viewer's colour scheme and honours `data-theme` |

## Minimum sizes

Measured by rendering and reading, not by rule of thumb. Below these the descriptor's
letterspacing closes up and the tagline turns to grey mush.

| Form | Minimum width |
|------|---------------|
| `horizontal`, `wordmark` | 160 px / 40 mm |
| `horizontal-tagline`, `wordmark-tagline` | 260 px / 62 mm |
| `stacked` | 170 px / 42 mm |
| `stacked-tagline` | 260 px / 62 mm |

Below the tagline's floor, drop to the form without a tagline rather than shrinking further.

## Clear space

Keep clear on all four sides by **the cap height of the "D" in "Dr."** — nothing else sits
inside that margin. Each file already carries about a third of it inside its own viewBox,
so it never sits flush against its container even when placed carelessly.

## Construction

Proportions are expressed in cap units: the name's cap height is 100 and everything else
is a ratio of it, so the system rescales without drifting.

- Name — Gabarito 700, cap 100, tracking −0.006 em
- Descriptor — Manrope 600, tracking 0.44 em, **letterspaced out to exactly the width of
  the name**. That is what turns the wordmark into a clean rectangle instead of a ragged
  two-line stack, and it is why the descriptor's size is computed rather than chosen.
- Hairline — 2.4 units thick, full block width, sitting 31 units below the descriptor
  baseline. It separates what the clinic *is* from what it *promises*, and it gives the
  tagline an edge to hang from instead of floating.
- Tagline — Manrope 500, cap 25, **also justified to the name width**, but by letter
  spacing rather than by growing the type, so it stays quieter than the descriptor above
  it. The words are separated by middots rather than full stops: three sentences ending
  in periods read as an abrupt list, while middots read as a sequence and give the
  spacing somewhere to breathe. Tracking lands near 0.38 em.
- Symbol — beside the text, its height is 1.85× the text block; above the text, its width
  is 0.42× the wordmark. Same mark, measured against whichever neighbour it has

All three lines are the same width. That is the point: the wordmark is a rectangle, and
the hairline is the only horizontal that is drawn rather than implied.

Colour follows the symbol's own palette: the name takes `--c1`, the descriptor and tagline
take `--c-sheath`, which is the same navy/grey split the follicle already uses.

## Don'ts

- Don't re-set the type live — the outlines exist precisely so nobody has to have the fonts
- Don't restack, re-space or re-align the lines; use the form that fits
- Don't recolour outside the six colourways
- Don't stretch — always scale both dimensions together
- Don't place `-light` on a dark ground, or `-dark` on a light one; there is a file for each
- Don't add shadows, outlines, gradients or bevels

## PNG exports

`png/` holds raster versions for email signatures, Office documents, WhatsApp and print
submissions. Everything else should use the SVG.

## Typeface note

The wordmark is set in the brand's own faces — Gabarito for the name, Manrope for the
descriptor and tagline — matching the website's display/text pairing. **If the original
logo artwork used a different typeface, send the font and rerun `tools/lockup.py`**; only
the face constants change and every one of the 36 files regenerates.

## Rebuilding

From `brand/`:

```
python tools/lockup.py       # all 36 SVGs
python tools/lockup_png.py   # the raster exports
```

`tools/type_outline.py` does the shaping and outlining: it instances the variable fonts at
the required weight, shapes each line with HarfBuzz so kerning is real, and converts every
glyph to outlines.
