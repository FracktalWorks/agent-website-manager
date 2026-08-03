# Illustrative diagrams — plan, prompt system and asset list

Status: **plan only. Nothing generated yet.** Approve the list and the style
anchor before any credits are spent.

The site is 61 pages and currently carries **one** image (the portrait). Every
explanation on it is carried by prose, tables and callouts. Diagrams are the
single largest available quality gain — and the single largest available way to
publish something medically wrong under a doctor's name. The rules below exist
because of the second half of that sentence.

---

## 1. The two decisions that shape everything else

### 1.1 Higgsfield draws artwork. It must never draw information.

Every diagram is generated **with no text in it at all** — no labels, no
numbers, no arrows carrying words. Labels are added afterwards in HTML, over
the image, as positioned text.

Why this is not a compromise but the better design:

| Text baked into the image | Text as an HTML overlay |
|---|---|
| Garbles ("MELANOCTYE", "EPIDREMIS") — the top failure mode of every image model | Always correct |
| Untranslatable — the four Telugu/Hindi pages would need re-generated artwork | One artwork, three languages |
| Uneditable — a wording fix is a new generation | Editable in the live editor like any other text |
| Invisible to search engines and screen readers | Indexed, selectable, accessible |
| Fixed type that fights the design system | Uses the site's own type tokens |

One consequence worth stating plainly: this means **one artwork can serve
several pages with different labels**, which is why the list below has 42
artworks covering ~120 placements rather than 120 generations.

### 1.2 Brown skin is the default, not an option.

Every inspiration reference is pink/white European skin. This clinic's patients
are Fitzpatrick IV–V, and on this site skin tone is not representation politics
— it is clinical accuracy. Post-inflammatory hyperpigmentation, vitiligo
contrast, laser targeting and peel risk all behave differently on brown skin,
and the site's own copy already says so ("Why acne marks last longer in India",
"The device is chosen for your pigment, not for its brochure"). A stock-looking
pink cross-section would contradict the page it sits on.

---

## 2. The prompt system

### 2.0 Generation runs against OpenAI directly (switched 2026-08-01)

Higgsfield was the first route and hit *"the daily generation limit for your
grace period"* — an account cap, not a credit shortage. Generation now goes
straight to OpenAI's `gpt-image-2`, driven by **`diagrams.py`** in this
directory:

```
python diagrams.py list          # what is queued, and what already exists
python diagrams.py gen A2        # one item
python diagrams.py gen --all     # everything unfinished in the batch
python diagrams.py gen A3 --quality high --size 2k   # escalate one image
```

It reads `.diagram-queue/batch-NN.json`, POSTs to `v1/images/edits` with the
style anchor attached, keeps the raw PNG in `.diagram-queue/out/` and writes a
cropped WebP into `assets/img/diagrams/`. `OPENAI_API_KEY` comes from the repo
`.env`.

**Why a script and not an MCP server.** The work is deterministic — read a
prompt, POST it, crop, write a file — so wrapping it in an MCP server would cost
a process and a tool schema every session to buy nothing. Same reasoning that
retired the `site-feedback` MCP server. It also batches, retries and does the
crop, which a chain of tool calls does badly.

**The crop matters.** `gpt-image-2` offers square and 3:2 sizes, never 16:9, but
the `media wide` slot is `aspect-ratio: 16/9` with `object-fit: cover`. Shipping
3:2 would let the browser crop it blindly at whatever width the viewport is.
`diagrams.py` crops 1536×1024 → **1536×864** using a content-aware window: it
samples the corner for the flat background colour, finds the bounding box of the
drawing, and centres the crop on that rather than on the middle of the frame.

### 2.1 Model and settings — LOCKED (verified by test, 2026-08-01)

**Every diagram: `gpt_image_2`, `resolution: "1k"`, `quality: "low"`. 0.5 credits,
~15 seconds.** Drafts and finals are the same call — there is no separate final
tier.

This was settled empirically, not assumed. The same prompt was run at
`quality: "medium"` / `2k` (3 credits, 6× the cost) and the output was **not
better** — see §2.2b. Costs measured on this account:

| Model | Resolution | Quality | Cost |
|---|---|---|---|
| **`gpt_image_2`** | **1k** | **low** | **0.5 cr** ← use this |
| `gpt_image_2` | 2k | medium | 3 cr |
| `gpt_image_2` | 2k | high | 7 cr |
| `nano_banana` | 1k | — | 1 cr |
| `nano_banana_pro` | 1k or 2k | — | 2 cr |

Output at these settings is **1344×752**. The site's widest render of a
`media wide` slot is ~1180 CSS px, so 1344 covers 1× comfortably and falls a
little short of 2× retina. If a specific diagram looks soft in place, run the
dedicated `upscale_image` tool on that one file rather than re-generating the
whole set at a higher tier — upscaling a keeper is far cheaper than paying 6×
on every generation for detail that mostly is not visible.

**Budget consequence.** At ~3 attempts per diagram this is ~1.5 credits each, so
the entire 42-artwork library costs roughly **65 credits**. Against a balance of
185, cost is no longer a reason to phase the work.

### 2.2 The seven-block prompt

Only **block 2 changes** between diagrams. Blocks 1 and 3–7 are constant, which
is what makes 42 images look like one commissioned set instead of 42 stock
purchases.

```
[1] FORM
Flat vector medical illustration in a clean editorial infographic style.
Semi-realistic anatomical accuracy with simplified forms. Smooth gradients,
soft cel shading, crisp uniform 1.5px outlines. Not photorealistic, not 3D
render, not hand-sketched, no cross-hatching, no textured brush strokes.

[2] SUBJECT                                    <-- the only variable block
<what structure, what is happening to it, how it is arranged in the frame,
 what the viewer's eye should land on first>

[3] SKIN
Skin shown as South Asian, Fitzpatrick type IV to V: warm mid-brown surface,
richly pigmented basal layer, dark brown-black hair.

[4] PALETTE
Strict limited palette. Background warm porcelain #F8F5F3. Tissue in muted
rose-clay tones. Healthy or resolved states in mint #8FDCC6 with deep teal
#0B6353. Inflammation, damage or caution in apricot #F5C09A with #9A5320.
Secondary structures in lilac #C9C4EA with #514697. Outlines and darkest
values in ink #12202F. No neon, no saturated primary red, no medical blue.

[5] COMPOSITION
16:9 landscape. Subject centred and completely inside the frame, nothing
cropped at the edges. Generous empty background margin on the <side> for
annotation. Flat #F8F5F3 background. No vignette, no drop shadow behind the
whole scene, no border, no frame, no background pattern.

[6] EXCLUDE
No text, no letters, no numbers, no labels, no captions, no arrows containing
words, no watermark, no signature, no logo, no scale bar, no ruler. No human
face, no blood, no gore, no surgical realism, no clinical photography look,
no white lab coat, no branded medical device, no stock-photo styling.

[7] ANCHOR
Match the reference image exactly for line weight, palette, shading style and
background.        [reference: <A1 media_id>]
```

### 2.2b Test log — A1 anchor, four iterations

Total spend: 5 credits. **Approved artwork: `assets/img/diagrams/A1-skin-cross-section.webp`**
(v4, 1344×752, 113 KB). Unreviewed clinically — Rule 6 still applies before publish.

**v1** — `low`/1k. Zero text on the first attempt; composition, framing and
anatomy all correct; brown skin correct. Failed on palette: fat came back
marigold, dermis salmon, the whole image reading warm-orange against a
porcelain site.
→ **Lesson: a hex bound to an abstract category ("healthy structures in mint")
is treated as mood. Bind every colour to a named structure.** Rewrote block 4 as
an explicit structure→colour assignment list. Also rewrote block 1 to describe
the wanted style positively ("modern anatomy textbook plate, semi-realistic
volumetric forms, soft airbrushed shading") instead of as a pile of negatives —
v1 ignored "flat vector" entirely and produced a painted plate, which matches
the user's own reference images and is the better look. That is now house style.

**v2** — palette fixed and on-brand. Two anatomical errors appeared: the
sebaceous gland floated detached in the dermis, and a hair grew out of the
**sweat duct**.
→ **Lesson: the model renders structures but not their connections. Every
adjacency must be stated as an explicit requirement** ("ATTACHED to", "must
physically touch", "NO hair grows from the sweat duct"). Also reduced to exactly
one hair — orphan hairs with no follicle beneath them were the source of the
confusion.

**v3** — all anatomy correct: gland attached by its duct, sweat duct opening at
its own surface pore, arrector pili touching follicle and epidermis, papilla
indenting the bulb, nerve rooted in the deep bundle. One fault left: the hair
shaft ran off the top edge of the frame.
→ **Lesson: "nothing cropped" is not enough — a long thin element will still
exit the frame. Constrain the element itself** ("the hair is SHORT, its tip ends
well inside the picture with clear empty space above it").

**v4 — approved.** Everything correct, nothing cropped, nerve legible, palette
on-brand, zero text.

**Resolution test.** v4's prompt re-run at `quality: "medium"` / `2k` (3 credits,
6×) was **not an improvement** — detail rose slightly but the palette drifted
back the wrong way: the skin surface came out pinker and less brown, and the
dermal fibres became busier than the design wants. Higher tiers cost more and
loosen palette adherence. **`low`/1k is the production setting.**

**Transferable rules for the remaining 41.** Expect ~3 attempts each, and expect
the failures to be these three, in this order: palette drift (fix by naming
structures), missing connections between structures (fix by asserting adjacency
as a requirement), and long elements escaping the frame (fix by constraining the
element, not the frame).

### 2.3 Size and shape contract

**Generate 3:2. Ship 1820×1024 — reached by PADDING, never cropping.**
`gpt-image-2` has no 16:9 size, so `diagrams.py` requests `1536x1024` and
**pads** the sides with the measured background colour to reach 16:9.

This replaced a content-aware crop, and the reason is worth keeping: cropping
1024 rows down to 864 removes 160 rows, and an illustration that fills its
frame loses the top and bottom of the drawing — the skin block ends flush
against the edge of the figure and reads as a rendering fault. That is exactly
what batch 1 looked like on the page. Padding is safe here only because the
artwork sits on a flat porcelain field, so extending that field is invisible.

`RIGHT_BIAS = 0.78` puts most of the new width on the right, where the label
chips go, so padding to the right shape and opening the label gutter are one
operation. `python diagrams.py refit --all` re-derives every shipped WebP from
the kept raw PNGs — **no API calls** — which is why a framing change like this
one costs nothing. Raw output is kept for exactly this.

The `diagram` block takes the stage's ratio from the image's own `w`/`h`, so a
diagram is **never cropped by the browser** — a different shape would render
correctly rather than silently lose its edges. 16:9 is still the default,
because the page column is wide and most of these subjects are wider than they
are tall. A body map or a treatment ladder that genuinely wants portrait can
ship at 3:4; nothing in the block needs changing.

**Compose for the labels, because the labels are real.** The prompt's
composition block reserves empty background, and that space is what the label
chips occupy:

| Diagram shape | Reserve | Labels land |
|---|---|---|
| Single subject (cross-section, cell, follicle) | right third empty | chips in the right margin, leader lines crossing to each structure |
| Left/right comparison (B5) | no margin available | chips overlay the artwork on their own white scrim |
| Left-to-right sequence (D3) | bottom band empty | one numbered chip under each stage |

This is the fix for what batch 1 looked like on first embed: the artwork
reserved 40% of the frame for annotation, the `media` block had no annotation
to put there, and the result read as a large blank gap.

### 2.3b Labelling

Labels are page data, not pixels. On a `diagram` section:

```python
{"kind": "diagram", "eyebrow": …, "h2": …, "intro": …,
 "image": {"src": "img/diagrams/A2-melanocyte.webp", "w": 1536, "h": 864,
           "alt": "…"},
 "labels": [
     {"text": "Pigment cap over each nucleus", "x": 44, "y": 30, "lead": 20},
     {"text": "Melanocyte", "x": 33, "y": 78, "lead": 31},
 ],
 "caption": "…", "note": "Illustration, not a photograph."}
```

- `x` / `y` — percentages of the image box. A hollow **ring** sits there, and
  the numbered chip sits at the far end of the connector. A filled numbered
  disc on the anchor point hides the structure it is naming, which is worst on
  a phone where the words are gone and the disc is all that remains. The ring
  is also what stays put when the words get longer.
- `lead` — connector length as a percentage of stage width (`cqw`), so it is
  the same proportion at 390px and at 1440px. To put a chip in the right
  margin: `lead ≈ 64 − x`.
- `side: "left"` — text runs leftward, for a structure near the right edge.
- Keep labels **≥ 8% apart in `y`** when their chips share a column, or they
  overlap.
- Under 720px the words move to the numbered key, but the **connector stays** —
  shortened to a fixed `7cqw` — because it is what carries the number off the
  structure. Hiding it would put the number back on top of what it names.
- Every label is `data-od` addressed, so it is editable in the live editor and
  can be translated for the `te-`/`hi-` pages without touching the artwork.

#### Which mode a picture gets — decide this BEFORE generating it

Label placement is a property of the **composition**, not an afterthought. Pick
the mode from what the artwork is, write block [5] of the prompt to reserve the
space that mode needs, and the labels then fit by construction instead of being
negotiated afterwards.

| Picture type | Reserve in the prompt | Mode | Label data |
|---|---|---|---|
| **Single subject in section** — one block of skin, one follicle, one joint. A2, A3, B7, D1, D8, D13 | "Generous empty background margin on the **right** for annotation." Subject sits left of centre. | **column** | `x`/`y` on the structure, `lead = (edge + 5) − x − 2`, `label_col` left at its default 86 |
| **Left-to-right sequence** — the same thing at 3–4 stages. A4, B10, C1, D3, D14 | "Stages evenly spaced across the frame, aligned on a common baseline, with an **empty band across the bottom** for annotation." | **row** | all labels share one `y` inside that band, `lead: 2`, `label_col: 0` |
| **Side-by-side comparison** — two states at the same scale. A5, B5, B8, B11, C5 | Nothing. Two panels fill the frame; that is the point of them. | **rail** | `rail: True`, `row` per label |
| **Frame-filling scene** — a staircase, a nail unit plus three plates, a face with vessels. C3, C6, D5, D9, D10 | Nothing. | **rail** | `rail: True`, `row` per label |

The measurement is the arbiter, not the intention — a composition that was
*meant* to leave a gutter sometimes does not. After the artwork lands, measure
its content bounding box and let the number decide:

- right edge ≤ 72% **and the labels differ in `y`** → **column mode**
  (`lead = (edge + 5) − x − 2`)
- otherwise → **rail mode** (`rail: True`, no `lead` at all)

That second clause is not decoration. D6 leaves a clear right third, so it
measured as a column — but every structure in it sits at the same height, and
a column would have stacked all four chips on one point. **A gutter is only
usable if the anchors are spread down the frame.** When they are spread across
it instead, the rail is the right answer whatever the edge measures.

A sequence is the other exception: it keeps **row mode** whatever it measures,
because its labels belong under their own stages.

**Row-mode chips must be SHORT — 15 characters or so.** They sit inside the
picture at a fixed `x`, so nothing rescues them if they collide or run off the
edge; at the narrowest desktop stage a 26-character chip is over 30% wide. Rail
chips are free to be longer because `diagram_rail.py` will row them, reverse
them, or refuse. Put the explanation in the caption either way.

**Labelling in Telugu and Hindi.** One artwork carries three label sets, which
is the whole reason nothing is baked into the drawing. Two things bite:

- `len()` over-measures Indic text. A Telugu cluster like మెలనోసైట్ is nine
  codepoints but renders as about five glyphs, because vowel signs and the
  virama attach to the consonant before them. `diagram_rail.py` counts only
  non-`Mn` characters and then applies ~1.15 for Indic ink density; counting
  codepoints invents rail rows and reports crossings that are not there.
- The `note` disclaimer defaults to English. On a translated page it has to be
  translated with everything else — it is the one line a reader of that page
  cannot check for themselves.

Coordinates are NOT translated. They belong to the artwork, so the Telugu and
Hindi placements reuse the calibrated English `x`/`y` verbatim.

The two useful tools:

- **`python diagram_grid.py <ids>`** burns a percentage grid INTO the artwork
  at one scale and writes one sheet per image. Read the numbers off it. Never
  estimate coordinates from a montage — doing that produced positions that were
  ~15% low in `y`, then uniformly 1.45× small in `x`.
- **`python diagram_rail.py`** lays out every `rail: True` figure — and only
  `row`/`side`, never the anchors. Run it after any embed. Panel centres for
  multi-panel artwork are worth measuring too (columns of pure background
  separate the panels) rather than eyeballing.

**Overlay mode is retired.** It was the old answer for artwork that fills its
frame: put the chip on the drawing, on its own white scrim. It is the wrong
answer, because a solid chip hides the thing it is naming — and on a
left-to-right sequence it lands squarely on the *next* stage along. Rail mode
replaces it on all ten such figures.

What survives is the **row-under-a-sequence** placement (`label_col: 0`,
`lead: 2`, all labels sharing one `y`), used by A4, B10, C1, D14 and D3. Those
chips sit inside the picture, but in a band the artwork deliberately left
empty — they cover nothing. Composing *for* the labels is still the first
move; the rail is what to reach for when the artwork did not leave room.

#### Rail mode

The words leave the picture. They sit in a rail beneath the stage, and each one
reaches back to its ring with a 1px riser. Nothing but a hairline and a hollow
ring ever touches the artwork, at any width — a leader crossing a drawing
occludes almost nothing, which is how anatomy plates have always been labelled.

```python
{"kind": "diagram", …,
 "rail": True,
 "labels": [
     {"text": "Creams", "x": 18, "y": 54},
     {"text": "Targeted injections", "x": 66, "y": 19, "row": 1},
     {"text": "A single dark band", "x": 77, "y": 80, "side": "left"},
 ]}
```

- `row` — which rail row the chip sits on. `side: "left"` runs the words back
  the other way, which is what a label near the right edge needs: dragging such
  a chip inward instead leaves its own riser coming down through its own text,
  and letting it run off the edge puts the whole page into horizontal scroll
  (the render gate catches that one).
- **Which label goes on which row is forced, not free.** A chip's words run
  rightward over its neighbours' anchors, and a riser that must travel past
  that chip's row would cut straight through them. So a label covered by
  another's words has to sit on the *shallower* row — which means laying the
  rail out right to left, taking each chip's floor from every anchor its span
  covers. Sweeping left to right instead only sees the risers placed so far,
  and iterating that to a fixed point **diverges** (rows just march downward).
- When no arrangement works, the figure is geometrically impossible as written:
  its label texts are wider than the gaps between its anchors. The cure is
  editorial, not algorithmic — **shorten the words**. They are legend entries;
  the intro and caption carry the explanation.
- Riser length is computed in Python, not CSS, because it depends on the
  artwork's own aspect: at width `100cqw` the stage is `100·h/w` tall, so an
  anchor at `y` stands `(100−y)·h/w` above the artwork's foot.
- **Rail chips never wrap** (`white-space: nowrap`). That is not typographic
  taste — `diagram_rail.py` measures every chip as a *single line* when it
  assigns rows, so a chip that wrapped was 42px tall where the model said 22.
  It then reached into the row below, and its own disc — centred against the
  taller text — sank 5px past the foot of the riser pointing at it. There is
  room to run sideways out here; that is what the rail is for.
- On a phone the rail **stays** and only its words are hidden — the numbers
  still ride their risers out of the picture, and the numbered key beneath
  carries the text. This is the one mode where a phone loses nothing.
- **The narrow rail is one row, and it is not the authored rows.** Those rows
  exist to keep one chip's WORDS off a neighbour's riser. Below the breakpoint
  the words are gone, so the rows are solving a collision that is no longer
  happening — and a figure that needed three rows of text rendered three rows
  of *discs*, sprawling the figure and scrambling the reading order into
  2, 1, 5, 3, 4. `_rail_spread()` in `chrome.py` re-solves it from the anchors:
  one row, each disc under its own ring unless a neighbour forces it along, and
  the minimum displacement when one does. Where a disc has moved, its leader
  becomes an **elbow** — down from the ring, across at a turn line that clears
  every disc, down onto the number. Axis-aligned throughout, because a diagonal's
  angle depends on the container width and CSS cannot compute that from a
  percentage and a pixel offset in one expression.

**Read coordinates off `grid*.png`, never off a montage.** Positions estimated
from a review montage came out systematically wrong twice: once ~15% low in `y`,
then uniformly **1.45× too small in `x`** — because the pixel positions were
read from a *downscaled preview* while the grid numbers were burned in at full
size. Read the printed grid numbers, not pixel offsets, or measure from a
rendered screenshot whose geometry you control.

Check placement with **`python diagram_sheet.py`** → `.diagram-queue/review.html`,
which stacks every figure on one page with the live stylesheet, and with
**`python diagram_shot.py <slug> <width>`** for a screenshot at a *true*
viewport width — `--window-size` below ~500px silently lays the page out at
512px and crops the picture, which makes correct labels look misplaced.

#### The two gates, and why one is not enough

| Run | Answers |
|-----|---------|
| `python diagram_audit.py --all-widths` | *Does every label render where it was told to?* Measures each ring, leader, disc and chip in a real browser at all five widths, and fails on drift, a broken leader, an overlap, a leader crossing someone else's number, or anything escaping the figure. **This is a build gate** — exit 1 on any finding. |
| `python diagram_review.py` | *Was the coordinate right in the first place?* Draws every ring straight onto its own artwork at full size, one sheet per distinct placement, and leaves the looking to a person. |

They catch different failures and neither substitutes for the other. A ring can
sit at exactly (38%, 19%) in every browser at every width and still be naming
six percent of empty background above the structure it points at — which is
what "Active scaly border" did on `C3-fungal-infection`, its leader running down
*through* the very lesion it was labelling. No DOM measurement finds that.

The audit's first run over the finished site returned **1,147 findings**, of
which **1,111 were one bug**: every ring on the site sat exactly 1.5px left of
its structure, because the pin was shifted by 6px when the ring it was centring
is 9px wide under `box-sizing: border-box`. Uniform, invisible on any single
figure, wrong on all three hundred. The lesson is not about that constant —
it is that a systematic error in shared geometry is precisely what eyes cannot
see and measurement finds instantly.

#### Narrow figures ask the STAGE, not the window

Whether a chip fits is a fact about the stage. A chip is sized in px (13px
type, 10px padding) but positioned in `cqw`, so as the stage narrows the chips
converge while staying the same size, and below some stage width they collide.
Which *viewport* produces that width depends on the page's gutters.

Asking the viewport was off by a whole breakpoint: at 768px the stage is 708px
and chips overlapped by up to 15px, but `@media (max-width: 720px)` had already
decided that was a desktop and left them on. It is now
`@container (max-width: 860px)` against `figure.diagram`, measured rather than
guessed, and it also holds if a diagram is ever dropped into a narrower column.

#### `label_col` is derived, not authored

`_phone_columns()` in `chrome.py` decides where each number waits once the words
leave the picture, from the label coordinates: two labels closer in `y` than a
disc is tall cannot share a column, so the second goes to a shorter one, and
labels that are a horizontal *row* get no column at all.

It is derived because the hand-set version failed exactly as you would predict.
`C1-miniaturisation` is a sequence with all four labels at y=80. On the page
that remembered `label_col: 0` it read correctly; on the page that copied the
figure without it, all four numbers were sent to the same point in the margin
and rendered as a single disc. The information needed to prevent that was in
the coordinates the whole time.

### 2.4 The nine rules

1. **No text in any image, ever.** Labels are HTML. (§1.1)
2. **Brown skin, always.** (§1.2)
3. **Style anchor first — done.** A1 is approved and lives at
   `assets/img/diagrams/A1-skin-cross-section.webp`. Pass it as the reference
   image (`medias: [{role: "image", value: <media_id>}]`) on every subsequent
   generation. Upload it once with `media_upload` and reuse the id.
4. **One idea per image.** If a diagram needs two sentences to explain what it
   shows, it is two diagrams.
5. **One tier for everything:** `gpt_image_2`, `low`, `1k` (§2.1). Higher tiers
   cost up to 14× and measurably loosen palette adherence. Upscale a specific
   keeper with `upscale_image` if it ever looks soft in place.
6. **Clinical review gate.** Dr. Varada approves every diagram before publish.
   An anatomically wrong illustration under a dermatologist's byline is worse
   than an empty placeholder — the placeholder is honest.
7. **Never generate a before/after, a patient result, or anything a visitor
   could read as evidence of an outcome.** The `ba` blocks stay real, consented
   photography; `build.py` already refuses a patient photo without a consent
   record, and that rule must not be routed around with an illustration.
8. **Diagrams explain mechanism, anatomy, sequence or comparison.** They never
   decorate. A page that has nothing mechanical to explain gets no diagram.
9. **Process and journey graphics are not Higgsfield's job.** The four-step
   appointment flow, the online-consult flow, the travel timeline and the
   12-month stability clock are typographic information graphics — build them
   in HTML/SVG from design tokens, where they stay editable and translatable.

---

## 3. Engine work this needs first

The `media` block renders a bare image band with no caption and no label layer.
Before the first diagram ships, `chrome.py` needs a **`diagram` section kind**:

- `figure` + `figcaption` (caption and a source/review note),
- a label layer: positioned chips with leader lines, each addressed with
  `data-od` so the live editor can reword and reposition them,
- labels stored in the page data, so `te-`/`hi-` pages carry their own,
- `alt` text mandatory — the build should refuse a diagram without it,
- artwork stored once in `assets/img/diagrams/<id>-<slug>.webp` and referenced
  by id, so a re-generated artwork updates every page that uses it.

Image dicts keep the existing shape: `{src, alt, w, h, focus}`.

---

## 4. The asset list — 42 artworks

IDs are stable; placements are `page-slug §section-index`.

### Tier A — Foundation (5 artworks, ~28 placements)

The most-reused images on the site. A1 is also the style anchor.

| ID | Artwork | Subject core | Placements |
|----|---------|--------------|-----------|
| **A1** | **Skin cross-section, healthy** — the style anchor | Epidermis / dermis / hypodermis block, follicle, sebaceous gland, sweat gland with duct, capillary loop, nerve ending, fat lobules | eczema §0 · chemical-peels §0 · rf-skin-tightening §0 · skin-boosters §0 · dermal-fillers §0 · acne-scar §1 · mesotherapy §0 |
| **A2** | **Melanocyte at work** | Basal-layer melanocyte with dendrites handing melanosomes to surrounding keratinocytes, pigment rising through the layers | vitiligo §0 · te-vitiligo §0 · hi-vitiligo §0 · premature-greying §0 · laser-hair-reduction §0 · acne §3 |
| **A3** | **Hair follicle anatomy** | Follicle in section — bulb, dermal papilla, matrix, inner/outer sheath, sebaceous gland, arrector pili, shaft emerging | hair-loss-hyderabad §0 · prp §0 · hair-grafting §0 · dandruff §0 · laser-hair-reduction §1 |
| **A4** | **Hair growth cycle** | Four follicles in a row — anagen, catagen, telogen, exogen — with the same follicle regressing and regrowing | hair-loss-hyderabad §3 · alopecia-areata-india §0 · prp §2 · laser-hair-reduction §1 · hair-grafting §3 |
| **A5** | **Epidermal turnover clock** | Two-panel: keratinocyte migrating basal→surface over 28 days, beside the same journey compressed to 4 days with cells still nucleated at the surface | psoriasis §0 · te-psoriasis §0 · hi-psoriasis §0 · psoriasis-treatment-hyderabad §0 |

### Tier B — Condition mechanism (12 artworks, ~30 placements)

| ID | Artwork | Subject core | Placements |
|----|---------|--------------|-----------|
| **B1** | Vitiligo: the immune attack | T-lymphocytes converging on basal melanocytes; pigment present on one side, absent on the other, the boundary visible in the epidermis | vitiligo §0 · vitiligo-treatment-hyderabad §0 · te/hi-vitiligo §0 |
| **B2** | **Repigmentation routes** ★ | Depigmented patch repigmenting two ways: perifollicular pigment islands spreading outward from each follicle, and pigment creeping in from the margin | vitiligo §2 (*"Why the hair inside a patch matters"*) · vitiligo-phototherapy §2 (*why lips and fingertips respond poorly — no follicular reservoir*) · vitiligo-excimer-laser §3 |
| **B3** | Segmental vs non-segmental | Two body silhouettes — one with patches respecting a dermatomal band on one side, one with symmetrical patches at hands, face, knees | vitiligo-types §0 · vitiligo-types §1 |
| **B4** | Active vs stable disease | Patch margin comparison — ill-defined advancing edge with confetti lesions and koebner line, beside a sharp stable border with pigment islands | vitiligo-types §2/§3 · vitiligo-graft-surgery §3 · vitiligo-types §4 (12-month clock) |
| **B5** | Psoriasis plaque in section | Thickened epidermis, elongated rete ridges, retained nuclei, silvery scale, dilated dermal capillaries — beside a normal block for scale | psoriasis §0 · psoriasis-types §2 · psoriasis-treatment-hyderabad §0 |
| **B6** | Psoriasis types, body map | Five silhouettes — plaque, guttate, inverse/flexural, pustular, erythrodermic — each with characteristic distribution | psoriasis §2 · psoriasis-types §0/§1 |
| **B7** | Psoriatic arthritis link | Finger joint in section — enthesis inflammation, swollen DIP joint, with the matching nail pitting above it | the *"Joint pain is not a coincidence"* callout, which appears on **6 pages**: psoriasis §1 · psoriasis-types §3 · psoriasis-scalp §4 · psoriasis-triggers §4 · psoriasis-biologics §5 · psoriasis-online §3 |
| **B8** | Eczema: the leaky barrier | Corneocyte "bricks" with depleted ceramide "mortar", water escaping upward, irritant and allergen entering, inflammatory cells below | eczema §0 · skin-allergy-rashes §1 |
| **B9** | Itch–scratch cycle | Circular sequence: itch → scratch → barrier damage → inflammation → itch, drawn as a loop over a skin section | eczema §2 |
| **B10** | Acne lesion formation | Four follicles in sequence: normal → microcomedone with sebum and keratin plug → inflamed papule/pustule with bacteria → deep nodule | acne-treatment-hyderabad §1 |
| **B11** | **Mark vs scar** ★ | Cross-section pair on brown skin: post-inflammatory hyperpigmentation (pigment deposit, intact contour) beside a true atrophic scar (collagen loss, depressed contour) | acne §2 · acne-scar §0 · acne §3 (*"Why acne marks last longer in India"*) |
| **B12** | Acne scar morphology | Three scars in section — ice pick (narrow deep tract), boxcar (sharp-walled crater), rolling (tethered undulating surface) | acne-scar §1 |

★ = highest teaching value on the site; these two explain things the prose has
to work hardest to convey.

### Tier C — Further conditions (7 artworks, ~14 placements)

| ID | Artwork | Subject core | Placements |
|----|---------|--------------|-----------|
| **C1** | Androgenetic alopecia miniaturisation | Same follicle across four stages, progressively thinner shaft and shallower bulb; beside it male and female pattern maps | hair-loss-hyderabad §1 · prp §2 · hair-loss-secunderabad §1 · hair-grafting §0 |
| **C2** | Alopecia areata | Immune cells swarming the bulb of an otherwise intact follicle, with an exclamation-mark hair at the patch edge | alopecia-treatment-hyderabad §0 · alopecia-areata-india §0 |
| **C3** | Dermatophyte infection | Fungal hyphae threading through the stratum corneum; the advancing scaly ring edge with clearing centre; a third panel showing what a steroid combination cream does to it | fungal-infection §1 · fungal-infection §0 (the *stop the combination cream* callout) · fungal-infection §4 |
| **C4** | Seborrhoeic dermatitis | Scalp section — active sebaceous gland, Malassezia at the surface, inflammatory scale between hairs | dandruff §0 · psoriasis-scalp §0 (*scalp psoriasis or dandruff?* — paired with B5) |
| **C5** | Keloid vs normal scar | Wound in section healing two ways: organised collagen inside the original margin, versus disorganised collagen bulging past it | keloid §0 |
| **C6** | Nail unit anatomy + three states | Nail in section — matrix, lunula, plate, bed, folds — with three plates above it: onychomycosis, psoriatic pitting, and a longitudinal dark streak | nail-treatment §0 · nail-treatment §1 · nail-treatment §3 (dark streak callout) |
| **C7** | Urticaria: the wheal | Mast cell degranulating, histamine release, dermal oedema lifting a wheal, the surrounding flare | skin-allergy-rashes §3 (chronic urticaria) |

### Tier D — Treatment mechanism (18 artworks, ~40 placements)

The pages that most need these are the procedure pages, where the prose is
currently doing all the work of explaining a physical process.

| ID | Artwork | Subject core | Placements |
|----|---------|--------------|-----------|
| **D1** | NB-UVB phototherapy | 311nm light entering the skin, penetration depth through epidermis into upper dermis, T cells being suppressed, melanocytes stimulated | vitiligo-phototherapy §0 · psoriasis-phototherapy §0 |
| **D2** | Excimer vs cabinet | Targeted 308nm handpiece over one patch, beside a full-body cabinet — coverage and dose contrast | vitiligo-excimer-laser §0 · vitiligo-excimer-laser §1 |
| **D3** | **Melanocyte transplant (NCES)** ★ | Four-step sequence: donor skin shave → enzymatic cell suspension → dermabraded recipient patch → repigmented result | vitiligo-graft-surgery §0 · vitiligo §5 · vitiligo-treatment-hyderabad §0 |
| **D4** | The four vitiligo operations | Mini-punch, suction-blister, split-thickness and cell-suspension grafting compared in one frame | vitiligo-graft-surgery §1 |
| **D5** | The treatment ladder | Staircase — topicals → phototherapy → conventional systemics → biologics — with monitoring burden rising alongside | psoriasis §3 · psoriasis-biologics §0 · vitiligo §3 · te/hi-psoriasis §1 |
| **D6** | Biologics: cytokine blockade | Immune signalling chain with an antibody intercepting TNF / IL-17 / IL-23 before it reaches its receptor | psoriasis-biologics §1 · psoriasis-biologics §2 |
| **D7** | Laser hair reduction | Laser energy absorbed by melanin in the shaft and bulb, heat destroying the follicle — and why only anagen follicles are vulnerable | laser-hair-reduction §0 · laser-hair-reduction §1 |
| **D8** | Peel depths | Skin section with three shaded depths — superficial, medium, deep — against the layers each reaches | chemical-peels §1 · chemical-peels §2 |
| **D9** | Botox mechanism | Neuromuscular junction with vesicle release blocked, muscle relaxed; beside it an upper-face muscle map | anti-aging-botox §0 · anti-aging-botox §1 |
| **D10** | Filler layers and danger zones | HA placed at its correct tissue depths in one panel; facial arterial anatomy and the high-risk zones in the other | dermal-fillers §0 · dermal-fillers §2 · dermal-fillers §3 |
| **D11** | Booster vs filler | Same section twice: dispersed hydrating micro-deposits through the dermis, versus a structural bolus lifting a contour | skin-boosters §0 · skin-boosters §2 |
| **D12** | RF remodelling over time | Dermal heating, collagen fibres contracting, then progressive reorganisation across three time points | rf-skin-tightening §0 · rf-skin-tightening §2 |
| **D13** | Microneedling depth | Needle array creating controlled channels to a set dermal depth, with the healing response below | mesotherapy §1 · acne-scar §2 · skin-boosters §1 |
| **D14** | PRP preparation | Blood draw → centrifuge with separated layers → plasma fraction drawn off → injection depth in the scalp | prp §1 · prp §3 |
| **D15** | FUE vs FUT | Donor safe zone on the scalp; strip harvest and closure beside punch extraction; grafts placed at the recipient angle | hair-grafting §2 |
| **D16** | The fixed donor supply | Donor reserve as a finite bank being redistributed to the recipient area — why coverage has a ceiling | hair-grafting §0 · hair-grafting §5 |
| **D17** | Ear lobe repair | Split lobe → excision of the tract → layered closure → healed lobe with the new piercing site | ear-lobe-repair §1 · ear-lobe-repair §3 |
| **D18** | Removal methods compared | Shave, excision and RF cautery shown at their respective depths, with what each leaves behind | dermatosurgery §1 · dermatosurgery §2 · keloid §1 |

★ D3 is the single most commercially important diagram on the site — surgical
repigmentation is the practice's stated differentiator and no page currently
shows what it is.

### Deliberately excluded

| Page / block | Why no diagram |
|---|---|
| `results`, `patient-stories`, the `ba` blocks everywhere | Real consented photography only — Rule 7 |
| `contact`, `locations-secunderabad`, `areas-we-serve` | Wants a drawn clinic map and route graphic, not a medical illustration |
| `about-dr-khagendra-varada` | Portrait and credentials; illustration would dilute it |
| `blog` | Per-article images later |
| All `steps` blocks (appointment flow, travel timeline, stability clock) | Typographic information graphics — Rule 9, build in SVG |
| All `cost` pages | Numbers; a diagram would imply precision that pricing does not have |

---

## 5. Suggested phasing

**Working rhythm (set by the user, 2026-08-01): five diagrams at a time,
embedded on the site, reviewed, then the next five.** First pass is always
`low`/1k; a specific diagram is re-run at `2k`/`high` only if that one looks
poor in place.

At 0.5 credits a generation the whole library costs ~65 credits against a 185
balance, so **cost no longer drives the phasing** — review capacity does. Dr.
Varada has to look at every one of these, and 42 diagrams arriving at once is a
worse review than eight batches of five.

**Batch 1 delivered 2026-08-01** — A2, A3, B2, B5, D3, generated through
`diagrams.py` after the Higgsfield cap forced the switch to OpenAI direct. Seven
generations for five keepers.

Two needed a second attempt, and both failures were new modes worth adding to
the list in §2.2b:

- **A3 v1** drew the surrounding tissue as a rounded, organ-shaped blob instead
  of a block of skin. *Naming what a thing is does not constrain its silhouette.*
  Fixed by describing the container explicitly — "a clean rectangular
  three-dimensional block, flat top, straight vertical sides, straight bottom …
  NOT rounded, oval, blob-shaped or organ-shaped".
- **D3 v1** rendered the final stage as ordinary untreated skin, so the sequence
  had no payoff. *A stage that means "the same thing, later" needs a stated
  visual link to the earlier stage* — fixed by asking for a faint pale hairline
  still tracing the old patch border.

Known imperfections, accepted rather than re-run: **B5** fills nearly the whole
frame, leaving no side margin for annotation (labels will have to sit over the
artwork), and its plaque is not warmer in tone than the normal block. **D3**
crops the scalpel handle at the left edge. **B2** does not show pigment cells in
the follicle wall in its cut-away, so the diagram shows *that* islands form
around hairs but not *why*.

| Phase | Contents | Artworks | ~Credits |
|---|---|---|---|
| **0** | **A1** — anchor, approved | 1 | 5 (spent) |
| **1** | The differentiators and highest-traffic mechanisms: A2, A3, A4, A5, B1, B2, B5, B7, B11, C1, D1, D3 | 12 | ~18 |
| **2** | Remaining condition mechanisms: B3, B4, B6, B8, B9, B10, B12, C2–C7 | 13 | ~20 |
| **3** | Remaining procedure mechanisms: D2, D4–D18 | 16 | ~24 |

---

## 6. Non-diagram artwork: credential emblems (batch 7, 2026-08-02)

Not everything the pipeline generates is a diagram, and the qualifications
panel on `about-dr-khagendra-varada` is the case that proved the pipeline had
two assumptions baked in that only anatomy wants.

**What these are.** Five round emblems, one per credential, sitting as a 52px
disc beside each qualification. They are *indicative*: generic credential marks
in the site's own slate-and-gold, carrying no lettering at all and no crest,
seal or wordmark belonging to Osmania, Cardiff, the AAAM, the Army or the IMA.
Those marks are those bodies' to grant, and the emblems are stand-ins until the
clinic settles what goes there.

**Why an emblem and not a picture of the certificate.** The panel first tried a
drawn frame, then framed specimen certificates. Both were wrong for the same
reason: a framed rectangle beside a named qualification reads as a photograph of
that certificate, and the moment a reader takes it for one, an illustration has
become a claim they cannot check. A badge stands *for* a qualification; a
certificate purports to *be* it. The emblem sidesteps the problem instead of
captioning around it.

They live under `assets/img/placeholder/`, which `build.py --links=production`
refuses to copy — the preview renders them, the live site cannot.

### Two pipeline changes this needed

Both hang off an optional `fit` block on a queue item, so anatomy is untouched:

```json
"fit": {"ratio": 1.0, "right_bias": 0.5, "trim": true}
```

- **`ratio` / `right_bias`** — anatomy is padded to 16:9 with 78% of the new
  width on the right, because that is the label gutter. An emblem has no labels
  and is cropped to a circle on the page, so it wants 1:1, centred. Shape is a
  property of the item, not of the run.
- **`trim`** — `trim_to_subject()` crops the flat field away before padding,
  measured against the *field colour* rather than against white so it survives
  the warm porcelain these are drawn on. This is not cosmetic: the model returns
  a circle filling ~60% of its frame, so shown whole the emblem lands at ~40px
  in a 52px badge and a guilloche ring stops being line work and becomes grey
  mush. Trimming is the difference between a mark you can read and a smudge.

Also fixed: `generate()` made only `ASSETS`, not the target's parent, so an item
whose `target_file` named a subdirectory generated successfully, cost credits,
and then died on write with nowhere to land. `out.parent.mkdir(parents=True)`
now runs in both `generate()` and `refit()`.

**Prompting.** The seven-block form carries over unchanged; the EXCLUDE block is
where the work is. Alongside the standing no-text rules it must name what is
*institutionally* forbidden — no real crest, wordmark, regimental badge,
national or state emblem, no lion capital, no coat of arms of any real body, and
no red cross or crescent. All five came back clean on the first pass.
