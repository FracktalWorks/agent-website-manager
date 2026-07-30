# Using this design system

`DESIGN.md` is the source of truth. Read it first; everything else renders or encodes it.

## Read order

1. `DESIGN.md` — palette, typography, band rhythm, components, voice, booking rule.
2. `colors_and_type.css` — link it, or paste it into the first `<style>` block of a
   generated artifact. It carries the tokens, the two brand faces as data URIs, and the
   band and component classes.
3. `brand.json` — the same system machine-readable, when you need roles rather than prose.
4. `preview/*.html` — what each part is supposed to look like.

## Do

- Alternate section surfaces: `--ground` → `--paper` → `--tint`, with `--dark` as
  punctuation only.
- Let the content type pick the accent: mint = chronic, apricot = aesthetics,
  lilac = trichology.
- Send every call to action to Practo.
- Keep running text near 65 characters and give digits `tabular-nums`.
- Pick a logo file, never modify one — there are 42 permutations.

## Avoid

- More than three dark bands in a page, or two adjacent.
- Body copy set on a pastel — use the `-dp` deep pair on the `-sf` soft fill.
- Unifying `--navy` and `--ink`. Navy is the logo; ink is the interface.
- A lockup in an avatar slot — that is what the icon ladder is for.
- Cure claims, guarantees, superlatives, or any number you cannot attribute. Indian
  Medical Council advertising rules apply to every page.
