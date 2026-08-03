"""Patient case studies — the real, consented series.

CONSENT IS THE WHOLE POINT OF THIS FILE
  `build.py` refuses to build a page carrying a clinical photograph with no
  consent record. Not a warning — the site does not build, and there is no flag
  to turn it off. So every case here carries a `consent` string, and that string
  has to be TRUE: it is the audit trail. Writing a plausible-looking date into
  it to make the build pass would be worse than having no gate at all, because
  it manufactures a record that someone later will trust.

  A patient signs once for the case, not once per frame, so `consent` on the
  case covers every shot in it. See CASES.md.

WHAT WAS DONE TO THE PHOTOGRAPHS
  Nothing that changes what they show. `cases_ingest.py` corrects orientation,
  crops, resizes to a matched 4:5 and strips EXIF. It does not retouch, relight,
  colour-correct or straighten, because every one of those is a way of making a
  result look better than it was. Two frames of a pair get the same treatment or
  the comparison is not a comparison.

  What the crops DO remove: faces, burned-in date stamps and camera watermarks.
  Two of these cases are children, and their frames are cut above the brow.

ALT TEXT
  Written to describe the photograph, not to caption the outcome. A reader on a
  screen reader gets the same clinical description a sighted reader can see, and
  no claim that a sighted reader could not verify from the picture.
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# THE CONSENT RECORD.
#
# What these strings say is exactly what was attested and nothing more. The
# clinic confirmed on 2026-08-02 that written publication consent is held for
# all ten cases, and that the two paediatric cases carry a parent or guardian's.
# The individual signing DATES were not supplied, so they are not written here —
# a per-patient date invented to make the record look thorough is worse than an
# honest record of what is actually known, because someone later will trust it.
#
# If the clinic wants a fuller audit trail, replace a case's string with its own
# signed date. Anything non-empty satisfies the build, so accuracy here is a
# matter of discipline rather than enforcement — which is why it is spelled out.
#
# Withdrawal is honoured immediately and needs no reason: delete the case, or
# blank its `consent`, and it disappears from the site at the next build.
# ─────────────────────────────────────────────────────────────────────────────
CONSENT = ("Written publication consent held at the clinic; "
           "confirmed by the clinic 2026-08-02")

CONSENT_GUARDIAN = ("Written publication consent given by the patient's parent "
                    "or guardian, held at the clinic; confirmed by the clinic "
                    "2026-08-02")

# WRITING THE CAPTIONS
#   These are read by someone deciding whether to book, not by a colleague.
#   So each `body` is one or two plain sentences answering the two questions a
#   patient actually has — what changed, and what should I expect — and nothing
#   else. Mechanism, measurement protocol and review intervals belong on the
#   condition pages, where a reader has already chosen to go deeper.
#
#   Where an honest caption has to disappoint, it does: colour outlasting a
#   cleared plaque, a nail that can only grow out, a change that cannot be
#   reversed. That is the part worth reading.
CASES = [
    {"title": "Alopecia totalis: hair back across the scalp",
     "cap": "Immunotherapy and topical treatment · child",
     "meta": ["Alopecia totalis", "Paediatric"],
     # NOT "the middle photograph". This case has three shots on the results
     # page and two on the home page, where `cases(frames=2)` keeps only the
     # first and the last — so a caption naming the middle frame described a
     # picture that was not on screen. Say what early regrowth looks like
     # instead of pointing at the frame that happens to show it, and the
     # sentence is true wherever the case is used.
     "body": "Hair came back over months, not weeks. Early regrowth is fine, pale "
             "and patchy long before it thickens, so the first months can look "
             "like very little is happening.",
     "consent": CONSENT_GUARDIAN,
     "shots": [
         {"label": "Before", "src": "img/cases/alopecia-2-before.webp",
          "w": 1200, "h": 1500,
          "alt": "A child's scalp seen from the side, completely bald, with smooth "
                 "skin and no visible hair follicles."},
         {"label": "During", "src": "img/cases/alopecia-2-during.webp",
          "w": 1200, "h": 1500,
          "alt": "The back of the same scalp, now covered in short, fine, sparse "
                 "hair of uneven density."},
         {"label": "After", "src": "img/cases/alopecia-2-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The top of the same scalp with a full head of dense, dark, "
                 "curly hair. The frame is cropped above the brow."},
     ]},

    {"title": "Alopecia areata: patches filled back in",
     "cap": "Immunotherapy and topical treatment · child",
     "meta": ["Alopecia areata", "Paediatric"],
     "body": "The bare patches filled in from their edges inwards. The parting is "
             "the place to compare the two photographs.",
     "consent": CONSENT_GUARDIAN,
     "shots": [
         {"label": "Before", "src": "img/cases/alopecia-1-before.webp",
          "w": 1200, "h": 1500,
          "alt": "A child's scalp from above with widespread thinning, bare skin "
                 "showing through across the crown and only wispy hair remaining."},
         {"label": "After", "src": "img/cases/alopecia-1-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The same scalp with thick dark hair covering the crown and a "
                 "clean parting. The frame is cropped above the brow."},
     ]},

    {"title": "Psoriasis: plaques cleared on both shins",
     "cap": "Creams and light treatment",
     "meta": ["Plaque psoriasis", "Topical + NB-UVB"],
     "body": "The raised, scaly plaques cleared. The darker marks left behind are "
             "not the disease coming back — colour fades more slowly than the "
             "plaque does, and it does fade.",
     "consent": CONSENT,
     "shots": [
         {"label": "Before", "src": "img/cases/psoriasis-1-before.webp",
          "w": 1200, "h": 1500,
          "alt": "Both lower legs with numerous raised, scaly, dark plaques "
                 "scattered from knee to ankle."},
         {"label": "After", "src": "img/cases/psoriasis-1-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The same lower legs with the raised plaques gone, leaving flat "
                 "areas of darker skin where they had been."},
     ]},

    {"title": "Psoriasis: a thick plaque on one leg",
     "cap": "Creams and light treatment",
     "meta": ["Plaque psoriasis", "Topical + NB-UVB"],
     "body": "A thick, cracked plaque covering most of one shin. The scale settles "
             "first and the colour underneath takes longer to even out.",
     "consent": CONSENT,
     "shots": [
         {"label": "Before", "src": "img/cases/psoriasis-2-before.webp",
          "w": 1200, "h": 1500,
          "alt": "One lower leg largely covered by a thick, cracked, silvery-white "
                 "scaling plaque from below the knee to the ankle."},
         {"label": "After", "src": "img/cases/psoriasis-2-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The same lower leg with the scale gone and the skin flat, "
                 "showing faint residual marking where the plaque had been."},
     ]},

    # DEPIGMENTATION, NOT REPIGMENTATION — the two are opposites and this case is
    # the second one. The dark spots in the first frame are the patient's
    # REMAINING natural colour, not colour coming back.
    {"title": "Vitiligo: evening out the last of the colour",
     "cap": "Depigmentation · near-total vitiligo",
     "meta": ["Vitiligo", "Depigmentation", "Does not reverse"],
     "body": "Vitiligo had already taken almost all of this skin. Rather than chase "
             "colour back into the rest, the few patches of natural colour still "
             "left were removed so the skin is one even shade. It is a considered "
             "choice and not a routine one: it does not reverse, and skin without "
             "pigment needs sun protection for life.",
     "consent": CONSENT,
     "shots": [
         {"label": "Before", "src": "img/cases/vitiligo-arm-before.webp",
          "w": 1200, "h": 1500,
          "alt": "A forearm that is almost entirely pale, scattered with freckle-like "
                 "islands and patches of the patient's remaining brown pigment."},
         {"label": "After", "src": "img/cases/vitiligo-arm-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The same forearm in one even pale shade, the remaining brown "
                 "islands no longer present."},
     ]},

    {"title": "Vitiligo: colour back across both forearms",
     "cap": "Immunotherapy",
     "meta": ["Vitiligo", "Immunotherapy"],
     "body": "Colour returned across both forearms. Vitiligo this widespread is "
             "judged over months rather than weeks, and the same arm can respond "
             "well in one place and slowly in another.",
     "consent": CONSENT,
     "shots": [
         {"label": "Before", "src": "img/cases/vitiligo-immuno-before.webp",
          "w": 320, "h": 401,
          "alt": "Both forearms, largely pale and densely stippled with small dark "
                 "spots, with larger white patches towards the wrists."},
         {"label": "After", "src": "img/cases/vitiligo-immuno-after.webp",
          "w": 280, "h": 350,
          "alt": "The same forearms in an even brown skin tone, with only faint "
                 "pale marking left."},
     ]},

    {"title": "Vitiligo: grafting for a stable patch",
     "cap": "Punch grafting · ankle",
     "meta": ["Vitiligo", "Grafting", "No before photograph"],
     "body": "Small grafts are placed into the pale patch, and colour then spreads "
             "outwards from each one — which is why the later photograph looks "
             "speckled before it evens out. There is no before photograph for this "
             "case; the first frame is the procedure.",
     "consent": CONSENT,
     "shots": [
         {"label": "During surgery", "src": "img/cases/fue-vitiligo-during.webp",
          "w": 1200, "h": 1500,
          "alt": "A pale patch on an ankle with a regular grid of small dark "
                 "punch grafts set into it."},
         {"label": "After", "src": "img/cases/fue-vitiligo-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The same ankle patch with pigment spread out from each graft "
                 "site, the pale area much reduced and mottled with darker skin."},
     ]},

    {"title": "Morphea: tight skin softened",
     "cap": "Medical treatment · hand and wrist",
     "meta": ["Morphea", "Localised scleroderma"],
     "body": "The tight, tethered bands running across the wrist softened, and the "
             "skin moved normally again. Morphea is judged by how the skin moves "
             "as much as by how it looks.",
     "consent": CONSENT,
     "shots": [
         {"label": "Before", "src": "img/cases/morphea-before.webp",
          "w": 1200, "h": 1500,
          "alt": "The back of a hand and wrist with taut, shiny, tethered skin "
                 "drawn into linear bands running towards the fingers."},
         {"label": "After", "src": "img/cases/morphea-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The same hand with the skin lying flat and slack, the linear "
                 "tethering no longer visible."},
     ]},

    {"title": "Eczema: thickened, scaling ankle",
     "cap": "Medical treatment · lower leg",
     "meta": ["Eczema", "Long-standing"],
     "body": "Years of scratching had thickened the skin. The scaling settled; the "
             "darker colour it leaves behind fades slowly and is not a flare.",
     "consent": CONSENT,
     "shots": [
         {"label": "Before", "src": "img/cases/eczema-before.webp",
          "w": 1200, "h": 1500,
          "alt": "An ankle and foot with thickened, dry, heavily scaling skin "
                 "broken into a coarse cracked pattern."},
         {"label": "After", "src": "img/cases/eczema-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The same ankle with the scaling resolved and the skin smooth, "
                 "leaving darker discolouration where it had been."},
     ]},

    {"title": "Nail infection: growing out a damaged nail",
     "cap": "Antifungal course · great toenail",
     "meta": ["Fungal nail", "Nine to twelve months"],
     "body": "A nail cannot be cleared, only grown out. Treatment stops the "
             "infection at the root, and the damaged nail then takes nine to twelve "
             "months to reach the tip. Expect that timescale from the start.",
     "consent": CONSENT,
     "shots": [
         {"label": "Before", "src": "img/cases/nail-before.webp",
          "w": 1200, "h": 1500,
          "alt": "A great toenail thickened and crumbling, discoloured brown and "
                 "yellow, lifted away from the nail bed."},
         {"label": "After", "src": "img/cases/nail-after.webp",
          "w": 1200, "h": 1500,
          "alt": "Both great toenails at follow-up, flat and attached to the nail "
                 "bed with the crumbling resolved and some discolouration left."},
     ]},

    {"title": "Hair grafting: rebuilding a hairline",
     "cap": "Follicular unit grafting",
     "meta": ["Hair grafting", "No before photograph"],
     "body": "The red line is the hairline agreed before anything was placed — the "
             "decision the result depends on most. There is no before photograph "
             "for this case; the first frame is the planning.",
     "consent": CONSENT,
     "shots": [
         {"label": "Hairline agreed", "src": "img/cases/hair-graft-during.webp",
          "w": 1200, "h": 1500,
          "alt": "A forehead with a proposed hairline drawn across it in red "
                 "surgical marker, hair below. Cropped above the eyes."},
         {"label": "After", "src": "img/cases/hair-graft-after.webp",
          "w": 1200, "h": 1500,
          "alt": "The temple and hairline at follow-up, with grafted hair growing "
                 "along the front edge."},
     ]},
]


def cases(*titles_start_with: str, frames: int | None = None) -> list[dict]:
    """Consented cases, optionally filtered to titles with the given prefixes.

    A CASE WITHOUT CONSENT IS NOT RETURNED AT ALL.
      This is not a way around the build gate — it is the same rule, one step
      earlier and with a better failure mode. Without it, a single unconsented
      case takes the whole site down: no preview, no deploy, nothing to look at
      while the clinic finds the paperwork. With it, the pages keep building and
      fall back to the placeholder frames they carried before, which is what the
      results page already tells the reader it is doing.

      The gate in `build.py` stays exactly as it was and is still the thing that
      would catch a photograph reaching a page unconsented. This only decides
      whether a case is offered to a page in the first place. Fill in `consent`
      on a case and it appears; both halves have to agree before anything ships.

    Selecting by prefix rather than by index means the home page's short set
    cannot silently become a different set when a case is inserted above it.

    `frames` TRIMS EACH CASE TO ITS FIRST AND LAST SHOT.
      The frames of a case divide the width of its card, so a three-frame case
      sitting beside two-frame ones gets visibly smaller pictures — the row
      looks mis-set, and a reader reads that as carelessness before reading a
      word. The results page is where a series can run long; the home page
      shows the two frames that carry the comparison, and says where the rest
      are. First and last, never a middle pair, because the endpoints ARE the
      comparison.
    """
    ready = [c for c in CASES if (c.get("consent") or "").strip()]
    if titles_start_with:
        ready = [c for c in ready
                 if c["title"].startswith(tuple(titles_start_with))]
    out = [dict(c) for c in ready]
    if frames:
        for c in out:
            shots = c.get("shots") or []
            if len(shots) > frames:
                if _FRAME_TALK.search(c["body"]):
                    raise ValueError(
                        f"{c['title']!r}: the caption names a specific frame, "
                        f"but frames={frames} drops one of "
                        f"{len(shots)}. Rewrite the caption to describe what is "
                        f"visible rather than which picture shows it.")
                c["shots"] = [shots[0], *shots[-(frames - 1):]]
    return out


# A caption that points at a numbered frame is only true for the frame count it
# was written against. The alopecia case said "the middle photograph is what
# early regrowth looks like"; the home page trims to two frames, so on the page
# most people see, it pointed at a picture that was not there. Nothing caught
# it — the build passed, the images were all real and consented, and the prose
# was simply describing a different layout.
#
# So trimming a case whose caption talks about frame POSITION is now an error
# rather than a silent edit. The fix is always to rewrite the caption: prose
# that survives any frame count is better prose anyway.
_FRAME_TALK = re.compile(
    r"\b(first|second|third|middle|last|left|right)\s+"
    r"(photograph|picture|image|frame|shot)\b", re.I)


def awaiting_consent() -> list[str]:
    """Titles of cases that are built and waiting on a consent record."""
    return [c["title"] for c in CASES if not (c.get("consent") or "").strip()]
