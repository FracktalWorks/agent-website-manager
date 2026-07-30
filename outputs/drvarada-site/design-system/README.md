# Design system — Dr. Varada's Skin & Hair Center

The source of truth is [`DESIGN.md`](DESIGN.md). Everything else in this folder is either
generated from it or renders it.

## What's here

| Path | What it is |
| --- | --- |
| `DESIGN.md` | **Entry file.** Palette, typography, band rhythm, components, voice, booking rule |
| `brand.json` | The same system, machine-readable — colours with roles, accent triples, voice rules |
| `system/variables.css` | The stylesheet the site actually loads. Tokens plus band and component classes |
| `system/fonts.css` | Gabarito and Manrope inlined as data URIs, so nothing depends on a CDN |
| `system/tokens.default.json` | Tokens as JSON, **generated** from `variables.css` |
| `system/theme.json`, `system/seed.json` | Ant-Design-shaped seed for tools that expect one |
| `system/BRAND-SYSTEM.md` | The short version — what to remember when building a page |
| `preview/*.html` | Design System cards: colour, typography, band rhythm, components, geometry |
| `logos/` | The lockups, symbol and icons this system references |

## Rebuilding

```
python build.py
```

Assembles `kit/` — the folder Open Design consumes — from the files above: eight preview
cards, the token JSON, the merged `colors_and_type.css`, `metadata.json` and the logos.
Nothing in `kit/` is hand-edited, so it cannot drift from `system/variables.css`.

## Two things about `DESIGN.md` that are not obvious

Open Design parses `DESIGN.md` to drive its own showcase and preview views, and its
parser is narrow:

- **Colours must be `- **Name** \`#hex\`: role description` lines.** A markdown colour
  table parses to *nothing* and the showcase silently falls back to a default blue on
  white. The role prose also has to contain the phrase the parser hints on —
  `primary background`, `primary text`, `primary cta`, `brand secondary`,
  `secondary text`, `hairline`, `secondary surface`.
- **Fonts must be `- Display: Family, fallbacks`.** The `- **Display:** …` shape leaks
  the asterisks into the parsed value.

That is why the palette and typography sections are written as bullet lists rather than
the tables you would otherwise reach for.

Each preview card also needs a sibling `preview/<name>.html.artifact.json`; without it
the HTML is just a loose file rather than a card. `build.py` writes them.

## The three rules that matter most

1. **Light-committed, dark as punctuation.** Three dark bands per page, maximum: the
   utility bar, one spotlight, the footer. Clinical before/after photography only reads
   truthfully on light.
2. **Every CTA ends at Practo.** The clinic team already runs on Practo. A parallel
   booking form would split the queue and break their workflow.
3. **No cure claims, no guarantees, no superlatives.** Indian Medical Council advertising
   rules, and the site must stay compliant. Every number must be attributable.

## Relationship to the brand folder

`../brand/` holds the logo system itself — the source vector, the six lockup forms, the
four-tier icon ladder, and the scripts that regenerate all of it. This folder consumes
those assets; it does not own them. If the artwork changes, rerun the brand tools first,
then re-copy into `logos/`.
