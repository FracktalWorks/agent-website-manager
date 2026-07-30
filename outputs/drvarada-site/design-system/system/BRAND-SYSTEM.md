# Brand system — the short version

What to keep in your head while building a page. The long version is `../DESIGN.md`.

## Surfaces, in order of frequency

`--ground` `#F8F5F3` → `--paper` `#FFFFFF` → `--tint` `#EDF6F2` → `--dark` `#12202F`

Alternate them. A long page with one surface reads as a wall; the rhythm is what makes it
scannable. Dark is punctuation — three per page maximum, never two adjacent, never the
opening band except the utility bar.

## Type

Gabarito 600 for headings, Manrope 400 for everything a patient reads. Headings are 600,
not 700 — Gabarito's 700 shouts at display sizes, which is wrong for a medical practice.

Eyebrows are 12px Manrope 600, uppercase, `.14em` tracking, `--ink-3`. Statistics are
Gabarito 700 with `tabular-nums`.

## Colour decisions you don't get to make

- **Accent follows category.** Mint = chronic conditions. Apricot = aesthetics.
  Lilac = trichology. The content type picks the colour, not the designer.
- **Navy is not ink.** `--navy` `#1E3A63` is the logo and print. `--ink` `#12202F` is
  text and dark bands. Close on purpose, different jobs.
- **Pastels never carry text.** Each accent has a `-dp` deep pair for words and a `-sf`
  soft pair for fills. Use them as a pair.

## Geometry

4px base unit. 26px card radius, 999px pills, 1px hairlines at 10% ink. One shadow token,
used sparingly — depth comes from the band rhythm, not from stacked elevations.

## Conversion

One path: **Practo**. Label the button with its destination. Phone and WhatsApp live
below it, never beside it as an equal choice. No booking forms, ever.

## Words

Write the way a senior consultant speaks in a consulting room. Short declarative
sentences. Lead with the patient's own words — someone searches "white patches on skin",
not "vitiligo management protocol".

Forbidden: cure claims, guarantees, superlatives ("best", "No. 1", "world-class"), named
comparisons, and any number you cannot attribute. Before/after images need written
consent.
