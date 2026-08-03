# Fascia signage — Karkhana clinic

Telugu, English and Hindi on one board, generated from the site's own constants.

```bash
python getfonts.py     # once — Noto Sans Telugu + Devanagari (OFL)
python board.py        # writes fascia.html, reports the fit
python render.py       # writes out/fascia-signage.pdf and out/fascia-proof.png
```

**`out/fascia-signage.pdf` is the deliverable.** The PNG is for approving on a
screen. Never send the PNG to be fabricated — it is a raster at a quarter scale.

## Before anything is cut

One left.

**The board dimensions are a guess.** 2600 × 1175 mm is the proportion this
content wants, not a survey. Set `BOARD_W` / `BOARD_H` to what the fabricator
measures and re-render — the wordmark is derived from the height budget, so the
layout re-proportions itself rather than needing a redraw. `natural_height()`
reports the height at which the English name exactly fills its column, and
`board.py` prints it whenever the set height differs by more than 20 mm.

## Language sign-off — cleared 2026-08-02

Both script lines were read by a native speaker and confirmed, including the two
judgement calls put to them: the `డా.` / `डॉ.` abbreviation for "Dr.", and the
transliterated conjunction `అండ్` / `एंड` in preference to the translated
`మరియు` / `और`. (Hindi writes brand names as जॉनसन एंड जॉनसन, not जॉनसन और जॉनसन.)

`NATIVE_REVIEW` in `board.py` records this as a dated attestation rather than a
bare boolean, for the same reason the case studies carry a consent string: the
question six months from now is *who checked this, and when*, and `True` cannot
answer it.

**The sign-off covers these exact words, not the language in general.** If either
line is ever edited, set `NEEDS_NATIVE_REVIEW = True` again — while it is set,
every proof carries a "do not fabricate" stamp.

The Telugu and Hindi *diagram labels* on the website are a separate outstanding
check and were not covered by this pass.

## The registration number is omitted, not forgotten

`SHOW_REGISTRATION = False`, set on the clinic's instruction on 2026-08-02. The
NMC code expects a practitioner's board to carry the council registration, so
this is a deferral rather than a decision. When the number lands in
`REGISTRATION` in `../site/chrome.py`, flip the flag and re-render; it slots into
the credential line and appears on the site and in the schema from the same
constant.

## The former name

"Formerly BNR Skin & Vitiligo Hospital", imported from `FORMER_PLAIN`. It is set
larger than the credentials on purpose: for a patient who has known this place
for years it is the line that says the clinic did not move or close.

Note there is a **second, near-identical name** — "BNR Skin and Vitiligo Centre"
— which belongs to a different, unclaimed Google listing at D/13A that is marked
Temporarily closed. That is not the former name of this practice and must not go
on the board; putting it there would point the rename at a dead listing. This is
why the name is imported rather than typed.

## Why the name is imported, not typed

Every word comes from `../site/chrome.py`. The board is now the legal source of
truth for the Google Business Profile name — a rename is judged against
real-world signage, so a board that disagrees with the listing gets the rename
refused, and a board that disagrees with the website costs local ranking the same
way a differing address string does. Retyping is how `Center` quietly becomes
`Centre` and nobody notices until it is cut in acrylic.

The English name is not set in type at all: it is `logo-wordmark-*.svg` from
`../brand/lockups/`, which is outlined artwork. So the letterforms on the board
are the same letterforms as the site header, not a re-setting of them.

## Why a browser renders it

Telugu and Devanagari need real text shaping. PIL on this machine reports
`raqm: False`, so it would set glyphs in codepoint order and produce
confident-looking nonsense. Chrome shapes through HarfBuzz, and `--print-to-pdf`
then writes the result as Type 3 fonts whose glyph procedures are vector paths.

The practical consequence, confirmed by reading the PDF back rather than assumed:
**there is no font program in the file and no font dependency at all.** The
shaping is already resolved and the letterforms are outlines. A sign shop with no
Indic font installed still gets correct Telugu — which is the single most common
reason one of these comes out wrong. `render.py` asserts this on every run and
refuses to pass a PDF that has lost it.

## For the fabricator

- **One colour.** Both colourways use the brand's designated signage artwork
  (`-flat-navy`, `-mono-light`). A quote for a two-colour cut is a quote for a
  different, dearer job.
- **Page 1** — porcelain face `#F8F5F3`, artwork in brand navy `#1E3A63`. Matches
  the website.
- **Page 2** — navy face `#1E3A63`, white knockout. Reads harder at dusk and
  suits a backlit face.
- The PDF page is the board: a 2600 × 1000 mm page is a 2600 × 1000 mm sign.
  Artwork can be measured off it with a ruler.
- Clear space and minimum sizes for the lockup are in
  [`../brand/lockups/README.md`](../brand/lockups/README.md).

## Still to confirm

- **The Telangana requirement for Telugu on commercial name boards.** The layout
  puts Telugu on the top line at a size that holds its own against the English on
  the assumption that prominence is expected. If GHMC requires Telugu to be
  *larger* than the other scripts rather than equal, raise `TELUGU_SIZE` and
  re-render — the wordmark gives way automatically. Your fabricator deals with
  this weekly; ask them.
- **Whether the signage permission covers this size.** Not a design question, but
  it decides `BOARD_W`.
