# Patient case studies — what to send, and what the build will refuse

Case studies live in the `ba` section kind. They are the only place on this site
where a photograph of a patient appears, and the only place where an image can
be blocked by the build.

## The rule the build enforces

`build.py` **refuses to build** a page carrying a clinical photograph with no
consent record. Not a warning — the site does not build. That is deliberate:
publishing a treatment result without written consent is a medical-ethics
breach, not a content mistake, and a safeguard that can be skipped under time
pressure is not a safeguard. There is no flag to turn it off.

The consent wanted is a **publication** consent for that specific use, not a
general clinical consent. Withdrawal is honoured immediately and needs no
reason, which in practice means deleting the shot from the case.

Nothing else may fill these frames. Not stock photography, not an illustration,
not a diagram. If no consented image exists, the placeholder stays — that is
what the results page says on the page itself, and it should stay true.

## A case is a series, not a pair

A pair says "it changed". A chronic condition is judged on whether the change
*held*, which only a sequence can answer — and vitiligo in particular is read
from how a border moved between reviews rather than from its endpoints. So send
however many frames the case actually has. Two is the short case, not the norm.

Several frames of several sites is also a series; label them by site instead of
by week.

## What each case needs

```python
{"title":  "Vitiligo: repigmentation, left hand",
 "cap":    "Excimer phototherapy · 24 weeks",
 "meta":   ["Segmental", "Excimer", "Reviewed 6-weekly"],   # optional chips
 "body":   "One or two sentences of clinical narrative.",   # optional
 "consent": "Written publication consent, 2026-07-14",      # covers every shot
 "shots": [
     {"label": "Baseline", "src": "img/cases/vit-01-base.webp",
      "w": 1200, "h": 1500,
      "alt": "The back of a left hand with a pale patch across the knuckles, "
             "its border soft and ill-defined."},
     {"label": "Week 12",  "src": "img/cases/vit-01-w12.webp",  …},
     {"label": "Week 24",  "src": "img/cases/vit-01-w24.webp",  …},
 ]}
```

- **`consent` on the case covers every shot in it** — a patient signs once for
  the case, not once per frame. A shot may carry its own `consent` to override,
  which is right when a case was built up across visits with separate consents.
- **`alt` is not optional and must describe the image**, under 8 characters
  fails the build. Screen readers and image search both read it, and on a
  clinical photograph it is also the only description a reader gets if the
  image fails to load.
- **`shots` may be plain strings** while you are waiting: `["Baseline",
  "Week 12"]` stages the case with labelled empty frames, so dropping the real
  photographs in later is a one-line change per frame.
- `before`/`after` still works as the two-frame shorthand.

## Photographing them

The page claims "the same lighting and the same distance", so that has to be
true. Same room, same light, same distance, same framing, same background,
patient in the same position. A series shot at three different distances shows
the camera moving, not the skin changing, and a reader who notices that stops
believing the rest of the page.

Portrait crops sit best — the frames are `4/5`. Send the largest files you
have; they are resized here, and an upscaled small file cannot be undone.

## Where they appear

| Page | Section |
|------|---------|
| `index` | "Progress, documented." — the shortest version, a few headline cases |
| `results` | "Progress, photographed at fixed intervals" — the full case studies |

The home page's set should stay short. The results page is where a case can run
to five frames and carry its narrative.

---

## The first ten cases (2 August 2026)

Ten cases are live, built from the clinic's folder of 22 photographs.
`content/cases.py` holds them; `cases_ingest.py` turns camera-roll files into
frames the site can carry.

### What the ingest does, and does not do

It corrects orientation, crops, resizes to a matched 4:5 and strips EXIF. It
does **not** retouch, relight, colour-correct or straighten — every one of those
is a way of making a result look better than it was, and two frames of a pair
must get identical treatment or the comparison is not a comparison.

What the crops **do** remove, and why each is non-negotiable:

- **Faces.** Cropped out, never blurred. A blur says "there was a face here" and
  invites the reader to wonder whose. One source was a full frontal photograph
  of a patient having a hairline marked; only the forehead and the marked line
  survive, which was the whole clinical content of the frame anyway.
- **Burned-in date stamps.** A stamp in the corner is not evidence, it is
  metadata that survived into the picture — and on a published case it dates a
  specific patient's specific visit.
- **Camera watermarks.** Same reason, plus a duller one: "REDMI NOTE 8 AI QUAD
  CAMERA" across a clinical result looks like stock photography.
- **EXIF.** Phone photographs carry GPS, device serial and capture time, all of
  which survive a naive re-save.

Crops are fractions of the corrected image, so re-shot originals at a different
resolution need no new numbers. A frame marked `strict` treats its box as a hard
boundary the crop may never leave; every face, stamp and watermark is held out
by one. **Run `python cases_ingest.py --proof` and look at the sheet before
trusting a new crop** — it draws the kept region over the original with the
discarded part dimmed, and it is what caught the first version silently growing
a crop back over a face to satisfy the aspect ratio.

### Two cases are children

Both alopecia cases are paediatric, cropped above the brow so no face appears,
and their consent records are the parent's or guardian's rather than the
patient's. Treat any future paediatric case the same way.

### What was held back, and why

| File | Why |
|------|-----|
| `nail fungus/before left toe.jpg` | 112×150 — a thumbnail, not a photograph |

`VITILIGO POST IMMUNOTHERAPY` was held back at first and should not have been.
The two files are small (455×607 and 280×607 exports rather than originals) and
a 4:5 crop of the *after* frame cut the hands off while the *before* kept them —
so the answer was not to drop the case but to **stop forcing the shape**. A case
may now set its own `ratio`; this one is `1/2`, both frames cut to the same span
from elbow to fingertip. Higher-resolution originals would still be welcome, but
the case reads correctly at the size it is shown.

**The lesson: when a frame does not fit, question the frame before the case.**

## A caption was clinically wrong, and it was live

The `converting 95% to 100% VITILIGO` folder was written up as *repigmentation*.
It is the opposite — **depigmentation**. The patient has near-total vitiligo, and
the dark spots in the baseline frame are the *remaining* normal pigment, not
pigment coming back; the treatment removes those so the skin is one even shade.
It was published wrong and corrected the same day, on the clinic's reading.

Two things follow, and both are now rules:

1. **A folder name plus a photograph is not a clinical reading.** "95% to 100%"
   is unambiguous to the doctor who wrote it and says nothing to anyone else.
   Where a case is written up from the images, the write-up is a *guess* until a
   clinician confirms it.
2. **Every case caption needs Dr. Varada's sign-off before it is published**,
   the same as the diagrams. One caption on this page was the exact inverse of
   the treatment given, which is worse than no caption: it is a medical claim,
   on a doctor's own site, about a real patient's photograph.

A useful discriminator for the vitiligo cases specifically, since the site now
carries both: **look at the colour of the "after".** Normal brown means colour
came back. Uniform pale means the remaining colour was deliberately removed.

### If a patient withdraws

Blank that case's `consent`, or delete the case. It disappears at the next
build, and `cases()` will not offer it to a page. No reason is required and
none should be asked for.
