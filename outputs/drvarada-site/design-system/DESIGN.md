---
name: "drvarada-skin-and-hair-center"
category: Brands
surface: web
colors:
  ground: "#F8F5F3"
  paper: "#FFFFFF"
  ink: "#12202F"
  navy: "#1E3A63"
  mint: "#8FDCC6"
  tint: "#EDF6F2"
  apricot: "#F5C09A"
  lilac: "#C9C4EA"
---

# Dr. Varada's Skin & Hair Center

> Category: Brands

> Surface: web

*A dermatology, trichology and aesthetics practice in Hyderabad, led by Dr. (Lt Col) Khagendra Varada — 45 years in practice, 25 of them in the Army Medical Corps. Vitiligo and psoriasis are the national specialisms.*

This document is the single source of truth for the brand. Bind the palette, typography,
spacing, radius and band rhythm below. Where a live page and this document disagree, this
document wins.

## Context

- **Brand:** Dr. Varada's Skin & Hair Center (formerly *BNR Skin & Vitiligo Hospital*)
- **Doctor:** Dr. (Lt Col) Khagendra Varada — 45 years, 25 in the Army Medical Corps
- **Location:** Hyderabad, India. Pan-India reach for vitiligo and psoriasis.
- **Surface:** web
- **Posture:** 26px radius on cards, 999px on pills, hairline borders at 10% ink, 4px base spacing
- **Booking:** every conversion path terminates in **Practo**. There is no parallel booking form.

## The one structural idea: band rhythm

The page is **light-committed**. Healthcare and skincare audiences expect light grounds,
and clinical before/after photography only reads truthfully on light. Dark is used as
**punctuation, not as a theme** — three dark bands in a long page, no more: the utility
bar at the very top, one specialty spotlight in the middle, and the footer.

Sections alternate between four surfaces so the page has a pulse rather than one flat
scroll:

| Band | Token | When to use |
| --- | --- | --- |
| `.band` | `--ground` `#F8F5F3` | Default. Warm porcelain, the resting state |
| `.band.paper` | `--paper` `#FFFFFF` | Where cards need to lift off the page |
| `.band.tinted` | `--tint` `#EDF6F2` | Process, reassurance, "how it works" |
| `.band.on-dark` | `--dark` `#12202F` | Punctuation only — maximum three per page |

Never place two dark bands adjacent. Never open a page on a dark band other than the
utility bar.

## Color Palette

- **Ground** `#F8F5F3`: primary background — warm porcelain, the default page surface
- **Paper** `#FFFFFF`: card surface — cards and white bands
- **Tint** `#EDF6F2`: secondary surface — process and reassurance bands
- **Dark** `#12202F`: section break — punctuation bands, utility bar, footer
- **Ink** `#12202F`: primary text — body and headings on light
- **Ink 2** `#53616D`: secondary text — descriptions and supporting copy
- **Ink 3** `#7C8794`: caption — metadata, eyebrows, captions
- **Navy** `#1E3A63`: brand mark — logo, icon tiles, signage and print only
- **Mint** `#8FDCC6`: primary cta — the booking band and every primary button
- **Apricot** `#F5C09A`: brand secondary — aesthetics and skin services
- **Lilac** `#C9C4EA`: tertiary brand — trichology and hair services
- **Line** `#E1E0DF`: hairline — dividers on light, authored as `rgba(18,32,47,.10)`

**Navy versus ink is deliberate, not a mistake.** `#1E3A63` is the identity colour: it
belongs to the logo, the icon tiles and anything printed. `#12202F` is the interface
colour: text, dark bands, footer. They are close but they do different jobs. Do not
"unify" them.

Each accent carries a **deep** variant for text on its own tint, and a **soft** variant
for fills. Never set body copy in a pastel — always use the deep pair.

| Accent | Base | Deep (text) | Soft (fill) |
| --- | --- | --- | --- |
| Mint | `#8FDCC6` | `#0B6353` | `#DFF3EC` |
| Apricot | `#F5C09A` | `#9A5320` | `#FCEBDD` |
| Lilac | `#C9C4EA` | `#514697` | `#EAE7F8` |

## Typography

- Display: Gabarito, "Segoe UI Variable Display", system-ui, sans-serif
- Body: Manrope, "Segoe UI Variable Text", system-ui, -apple-system, sans-serif
- Mono: ui-monospace, "Cascadia Mono", "SF Mono", Menlo, monospace

Gabarito ships weights 500–800; Manrope 400–700. Both are variable fonts and are inlined
as data URIs in `colors_and_type.css`, so nothing depends on a font CDN.

Gabarito carries every heading, statistic and label; Manrope carries every sentence a
patient actually reads. Headings sit at 600 rather than 700 — at display sizes Gabarito's
700 turns shouty, which is wrong for a medical practice.

| Role | Size | Face | Weight | Notes |
| --- | --- | --- | --- | --- |
| Hero | `clamp(42px, 6.5vw, 76px)` | Gabarito | 600 | One per page. `letter-spacing: -.03em` |
| Section head | `clamp(30px, 4.2vw, 46px)` | Gabarito | 600 | `text-wrap: balance` |
| Sub head | `clamp(28px, 3.6vw, 42px)` | Gabarito | 600 | |
| Card title | 20px | Gabarito | 600 | |
| Eyebrow | 12px | Manrope | 600 | uppercase, `letter-spacing: .14em`, `--ink-3` |
| Body | 16px / 1.65 | Manrope | 400 | Cap running text near 65 characters |
| Small | 14.5px | Manrope | 400 | Captions, footnotes |
| Statistic | 26–62px | Gabarito | 700 | `letter-spacing: -.04em`, tabular numerals |

Digits that line up in columns get `font-variant-numeric: tabular-nums`. Always.

## Logo system

Forty-two permutations exist so nobody has to improvise: six lockup forms across six
colourways, plus the symbol alone in the same six. Every letterform is **outlined**, so
the artwork carries no font dependency.

| Form | Ratio | Use it for | Min width |
| --- | --- | --- | --- |
| `horizontal` | 3.3 : 1 | The default — header, letterhead, email signature | 160 px |
| `horizontal-tagline` | 2.7 : 1 | Where there is room for the promise — ads, covers | 260 px |
| `stacked` | 1.2 : 1 | Square-ish spaces — signage, a social post | 170 px |
| `stacked-tagline` | 1.1 : 1 | The fullest expression — reception wall, poster | 260 px |
| `wordmark` | 4.2 : 1 | Where the symbol is already nearby, or too small | 160 px |
| `wordmark-tagline` | 3.3 : 1 | Document footers, certificates | 260 px |

Colourways: `-light` (white or porcelain), `-dark` (navy, ink, photography),
`-flat-navy` (one-colour print, signage, embroidery), `-mono-dark` (ink: fax, engraving),
`-mono-light` (knockout on dark), `-adaptive` (web, follows the viewer's scheme).

**The site header uses the horizontal lockup, not the symbol alone** — a mark without the
name earns no recall on a first visit.

**Never use a lockup as an avatar or favicon.** The icon ladder exists for that: four
tiers — `full` (128 px+), `compact` (44–96), `micro` (24–40), `nano` (16–20). Pick the
tier by the size the icon is *displayed* at, not the size of the file you upload; a
512 px profile picture that Practo shows at 48 px must come from the compact tier.

Clear space on all four sides is the cap height of the "D" in "Dr." If you are about to
modify the artwork, the answer is a different file, not an edit.

## Spacing, radius and elevation

Base unit **4px**. Section padding runs `clamp(64px, 9vw, 128px)` vertically.

| Token | Value | Applies to |
| --- | --- | --- |
| `--r` | `26px` | Cards, bento cells, images |
| `--r-pill` | `999px` | Buttons, chips, the mobile dock |
| `--line` | `rgba(18,32,47,.10)` | Hairlines |
| `--line-2` | `rgba(18,32,47,.16)` | Emphasised dividers |
| `--shadow` | `0 1px 2px rgba(18,32,47,.04), 0 14px 34px -16px rgba(18,32,47,.18)` | Lifted cards |

One shadow, used sparingly. Depth comes from the band rhythm, not from stacking shadows.

## Components

- **Primary CTA** — mint fill, `--mint-dp` text, pill radius. Always labelled with the
  destination, never "Submit". Always links to Practo.
- **Secondary CTA** — hairline border, ink text, pill radius, transparent fill.
- **Bento card** — `--paper`, `--r`, hairline border. Accent belongs to the *category*:
  mint for chronic conditions, apricot for aesthetics, lilac for trichology.
- **Symptom finder** — the page's opening interaction. Chips, not a dropdown; a patient
  recognises "patchy white skin" and does not recognise "vitiligo" yet.
- **Ticker** — condition names scrolling once under the hero. Pauses on
  `prefers-reduced-motion`.
- **Mobile dock** — fixed bottom bar, one Practo button and one call button. Appears
  below 720px only.

## Voice & Tone

- **Adjectives:** measured, plain, senior, unhurried, factual
- Write the way a senior consultant speaks in a consulting room: short declarative
  sentences, no hedging, no hype.
- Lead with the patient's own words. A patient searches "white patches on skin", not
  "vitiligo management protocol".
- **Never** claim a cure, guarantee a result, use superlatives ("best", "No.1",
  "world-class"), or compare the practice to a named competitor. Indian Medical Council
  advertising rules prohibit all of these and the site must stay compliant.
- Numbers must be attributable. "45 years in practice" is verifiable; "thousands of happy
  patients" is not — do not write it.
- Before/after images require written patient consent. No consent, no image.

## Booking

Every call to action ends at **Practo**. The clinic team already runs on Practo, so a
parallel booking form would split the queue and break their workflow. Phone and WhatsApp
are the only alternatives offered, and they sit below the Practo button, never beside it
as an equal choice.
