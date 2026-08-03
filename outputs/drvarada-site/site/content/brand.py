"""T3 — brand and utility pages: home, the doctor, the clinic, contact, results,
patient stories, blog index.

Copy rules that bind every line here (DESIGN.md § Voice, MASTER_PLAN § 5):
no cure claims, no guarantees, no superlatives, no named competitors, and every
number attributable. "45 years in practice" is verifiable. "Thousands of happy
patients" is not, so it does not appear.
"""

from chrome import (ADDRESS, FEE_CLINIC_SHOW, FEE_ONLINE_SHOW, FEE_TAX,
                    GOOGLE_LISTING, GOOGLE_LISTING_PLAIN, HOURS,
                    MAPS, PATIENTS, PHONE, PHONE_ALT_SHOW, PHONE_LANDLINE_SHOW,
                    PHONE_SHOW, PRACTO_REVIEWS, RATING, REGISTRATION,
                    REGISTRATION_COUNCIL, REVIEWS, WHATSAPP)
from content.cases import cases
from content.fees import FEE_FAQS, fees_block

# What the case-study blocks show while a case waits on its consent record.
# These are labelled empty frames, not stock photography — the results page
# says as much on the page itself, and that should stay true.
HOME_PLACEHOLDERS = [
    {"title": "Vitiligo: repigmentation",
     "cap": "Excimer phototherapy · duration on file",
     "meta": ["Excimer", "Reviewed 6-weekly"],
     "shots": ["Baseline", "Mid-course", "Latest"]},
    {"title": "Plaque psoriasis: clearance",
     "cap": "Topical and phototherapy protocol",
     "meta": ["Topical + NB-UVB"],
     "shots": ["Baseline", "Latest"]},
    {"title": "Acne: active lesion control",
     "cap": "Medical protocol and peels",
     "meta": ["Medical", "Peels"],
     "shots": ["Baseline", "Latest"]},
]

RESULTS_PLACEHOLDERS = [
    {"title": "Vitiligo: repigmentation",
     "cap": "Excimer phototherapy · duration on file",
     "meta": ["Segmental", "Excimer", "Reviewed 6-weekly"],
     "body": "Judged on where the border moved between reviews and on whether "
             "islands appeared around individual hairs, not on the area alone.",
     "shots": ["Baseline", "Week 8", "Week 16", "Week 24"]},
    {"title": "Plaque psoriasis: clearance",
     "cap": "Topical and phototherapy protocol",
     "meta": ["Plaque", "Topical + NB-UVB"],
     "body": "Measured by involved surface area alongside itch and sleep, which "
             "photographs cannot show and the notes record separately.",
     "shots": ["Baseline", "Week 6", "Week 12"]},
    {"title": "Acne: active lesion control",
     "cap": "Medical protocol and peels",
     "meta": ["Inflammatory", "Medical + peels"],
     "body": "Counted rather than eyeballed: inflammatory lesions at each review, "
             "with marks and scarring assessed separately once active acne settles.",
     "shots": ["Baseline", "Week 12"]},
]

CREDS = [
    "MBBS · Osmania Medical College",
    "25 yrs · Army Medical Corps",
    "Dip. Practical Dermatology · Cardiff, UK",
    "Dip. Dermatology · AAAM",
    # The only entry on this list a reader can check against a public register,
    # which is exactly why it belongs on it.
    f"Reg. No. {REGISTRATION} · {REGISTRATION_COUNCIL}",
]

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "index", "template": "T3",
    "title": "Dermatologist in Hyderabad & Secunderabad | Dr. Varada's",
    "meta": "Vitiligo, psoriasis, acne, hair loss and modern aesthetics with Dr. (Lt Col) "
            "Khagendra Varada. 45 years in practice, 10,000+ patients treated.",
    "eyebrow": "Dermatology · Trichology · Aesthetics",
    "h1": "Skin that's <em>understood</em><br>before it's treated.",
    "lede": "Vitiligo, psoriasis, acne, hair loss and modern aesthetics, with Dr. (Lt Col) "
            "Khagendra Varada, a dermatologist and dermatosurgeon of 45 years, 25 of them in "
            "the Indian Army Medical Corps.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Find the clinic", "locations-secunderabad")],
    "creds": CREDS,
    "portrait": [(PATIENTS, "patients treated"),
                 (RATING, "rated on Practo", "stars"),
                 ("45", "years in service")],
    "photo": {"src": "img/dr-varada-hero.webp", "w": 880, "h": 1100,
              "cutout": True,
              "alt": "Dr. (Lt Col) Khagendra Varada, dermatologist and dermatosurgeon, at the clinic in Karkhana, Secunderabad"},
    "ticker": True,

    "sections": [
        {"kind": "chips", "eyebrow": "Start here", "h2": "What brings you in?",
         "intro": "You don't need to know the name of the condition. Pick what you're seeing.",
         "items": [
             ("White patches on skin", "vitiligo", "mint"),
             ("Red, scaly, flaking patches", "psoriasis", "mint"),
             ("Dry, itchy skin that flares", "eczema-atopic-dermatitis-treatment", "mint"),
             ("A rash that came on suddenly", "skin-allergy-rashes-treatment", "mint"),
             ("Breakouts and marks", "acne-treatment-hyderabad", "mint"),
             ("Pitted scars from old acne", "acne-scar-treatment-hyderabad", "mint"),
             ("A ring-shaped, spreading rash", "fungal-infection-treatment-hyderabad", "mint"),
             ("A raised, growing scar", "keloid-treatment-hyderabad", "mint"),
             ("Hair falling more than usual", "hair-loss-treatment-hyderabad", "lilac"),
             ("Patchy bald spots", "alopecia-treatment-hyderabad", "lilac"),
             ("Flaking, itchy scalp", "dandruff-treatment", "lilac"),
             ("Greying early", "premature-greying-treatment", "lilac"),
             ("Fine lines and laxity", "anti-aging-botox-hyderabad", "apricot"),
             ("Dull, dehydrated skin", "skin-boosters-hyderabad", "apricot"),
             ("Unwanted hair", "laser-hair-reduction-hyderabad", "apricot"),
             ("A mole or skin tag", "dermatosurgery-hyderabad", "apricot"),
         ]},

        # Placed immediately after "pick what you're seeing", because the answer
        # to picking something is that someone then looks at it properly, and
        # that is the whole claim in the H1. It is also the first picture on the
        # page after the portrait: everything between here and the footer used
        # to be text in boxes.
        {"kind": "diagram", "eyebrow": "Before anything is prescribed",
         "h2": "Someone looks at it first.",
         "intro": "A patch of skin tells you more under a lens than it does across a desk. "
                  "The dermatoscope shows the pigment network — where it is intact, where it "
                  "has gone, and whether the border is advancing — which is what decides "
                  "the diagnosis and, after it, the plan.",
         "caption": "This is what the first appointment is: an examination, a name for what "
                    "you have, and a timeline you are told before anything starts.",
         "rail": True,
        "labels": [
            {"text": "The patch", "x": 26, "y": 58, "row": 1, "find": "pale"},
            {"text": "The dermatoscope", "x": 31, "y": 53, "find": "metal"},
            {"text": "Where pigment stops", "x": 66, "y": 16, "row": 1,
             "find": "edge:pale|skin"},
            {"text": "Pigment network", "x": 75, "y": 25, "find": "skin"},
        ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/E1-examination.webp", "w": 1820, "h": 1024,
             "alt": "A dermatologist's hands examining a patient's forearm. One hand steadies "
                    "the skin while the other rests a handheld dermatoscope on a pale patch. "
                    "A magnified circle above shows the view through the lens: brown skin "
                    "with a fine honeycomb network of pigment on one side, and plain pale "
                    "skin where that network has gone on the other."}},

        {"kind": "pillars", "anchor": "treatments", "eyebrow": "What we treat",
         "h2": "Three practices, one dermatologist.",
         "intro": "Medical dermatology for conditions that need answers. Aesthetics that "
                  "stay subtle and physician-led. Hair care that starts with a diagnosis, "
                  "not a package.",
         "items": [
             {"accent": "mint", "title": "Medical",
              "body": "Chronic and acute skin conditions, worked up properly and managed "
                      "for the long term.",
              "list": [
                  ("Vitiligo &amp; leucoderma", "vitiligo-treatment-hyderabad", "Specialty"),
                  ("Psoriasis", "psoriasis-treatment-hyderabad", "Specialty"),
                  ("Eczema &amp; atopic dermatitis", "eczema-atopic-dermatitis-treatment"),
                  ("Acne &amp; acne scarring", "acne-treatment-hyderabad"),
                  ("Allergies &amp; rashes", "skin-allergy-rashes-treatment"),
                  ("Fungal infections", "fungal-infection-treatment-hyderabad"),
              ],
              "go": ("Vitiligo &amp; psoriasis in depth", "vitiligo")},
             {"accent": "apricot", "title": "Aesthetic",
              "body": "Performed by the dermatologist, not a technician. Conservative "
                      "dosing, honest expectations.",
              "list": [
                  ("Anti-ageing &amp; botulinum", "anti-aging-botox-hyderabad"),
                  ("Dermal fillers", "dermal-fillers-hyderabad"),
                  ("Thread lift", "thread-lift-hyderabad"),
                  ("Skin boosters &amp; mesotherapy", "mesotherapy-hyderabad"),
                  ("RF skin tightening", "rf-skin-tightening-hyderabad"),
                  ("Bespoke peels", "chemical-peels-hyderabad"),
              ],
              "go": ("How we approach aesthetics", "anti-aging-botox-hyderabad")},
             {"accent": "lilac", "title": "Hair",
              "body": "Hair fall has causes: thyroid, iron, hormones, genetics. We find yours "
                      "before treating.",
              "list": [
                  ("Hair fall &amp; pattern loss", "hair-loss-treatment-hyderabad"),
                  ("Alopecia areata, totalis &amp; universalis",
                   "alopecia-treatment-hyderabad"),
                  ("PRP &amp; microneedling", "prp-hair-treatment-hyderabad"),
                  ("Hair grafting surgery", "hair-grafting-hyderabad"),
                  ("Dandruff &amp; scalp care", "dandruff-treatment"),
                  ("Premature greying", "premature-greying-treatment"),
              ],
              "go": ("Start with a diagnosis", "hair-loss-treatment-hyderabad")},
         ]},

        {"kind": "split", "anchor": "specialisms", "eyebrow": "The specialisms",
         "h2": "Vitiligo and psoriasis, treated for four decades.",
         "body": ["The practice began as a vitiligo hospital, and that remains the deepest part "
                  "of it, including surgical repigmentation, which comparatively few centres in "
                  "India offer. Patients travel from outside Telangana for it.",
                  "Because these are lifelong conditions, both have their own reference "
                  "sections on this site: what the disease actually is, what each treatment "
                  "can and cannot do, and what it costs before you commit to it."],
         "cta": ("Read the vitiligo section", "vitiligo"),
         "items": [
             {"title": "Vitiligo",
              "body": "Medical repigmentation, narrowband UVB, excimer laser and melanocyte "
                      "grafting for stable disease. The first appointment is a diagnosis and a "
                      "realistic timeline. Not a package."},
             {"title": "Psoriasis",
              "body": "Long-term control rather than a one-off clearance: topical and "
                      "systemic therapy, phototherapy, and the triggers worth changing."},
         ]},

        # Directly under the claim it is evidence for. The paragraph above says
        # surgical repigmentation is offered here and at few other centres in
        # India; a reader has no way to picture what that means, and "melanocyte
        # transplant" is not a phrase that explains itself. Four panels do.
        {"kind": "diagram", "eyebrow": "The surgery few centres do",
         "h2": "What a melanocyte transplant actually is.",
         "intro": "Not a graft of skin onto skin. A very thin shaving is taken from the "
                  "patient's own pigmented skin, the colour-making cells are separated out "
                  "of it, and that suspension is laid onto the patch once its surface has "
                  "been prepared. The cells are the patient's own, which is why there is "
                  "nothing to reject.",
         "caption": "Offered only where the disease has been stable for a defined period, "
                    "which is a clinical judgement made at the first visit. Being told the "
                    "surgery is not appropriate yet is a common and correct outcome.",
         "label_col": 0,
         "labels": [
             {"text": "Donor skin shaved", "x": 9, "y": 82, "lead": 2},
             {"text": "Cells separated out", "x": 30, "y": 82, "lead": 2},
             {"text": "Patch surface prepared", "x": 48, "y": 82, "lead": 2},
             {"text": "Colour returns", "x": 71, "y": 82, "lead": 2},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D3-melanocyte-transplant.webp", "w": 1820, "h": 1024,
             "alt": "Four stages of a melanocyte transplant shown left to right: a thin "
                    "sheet of pigmented skin lifted from a donor site, the pigment cells "
                    "separated into a suspension in a dish, the depigmented patch prepared, "
                    "and colour returning across it."}},

        # Reads INTO the case studies below: what a dermatologist looks at when
        # judging one of those series is the border, not the size, and a reader
        # who knows that gets more out of the photographs than one who does not.
        {"kind": "diagram", "eyebrow": "Judging progress",
         "h2": "What we actually look at.",
         "intro": "Whether a patch is spreading or has stopped is read from its edge, not "
                  "from its size. A border that fades gradually into normal skin belongs to "
                  "active disease. A border you could draw around means it has settled, and "
                  "that is the point at which repigmentation, and surgery, become worth "
                  "discussing.",
         "caption": "This is the judgement the first appointment exists to make. Photographs "
                    "of real treated patients, taken under standardised lighting and "
                    "published only with written consent, are on the results page.",
         "rail": True,
       "labels": [
           {"text": "Border fades out", "x": 15, "y": 44, "row": 2, "find": "edge:pale|skin"},
           {"text": "Confetti spots", "x": 33, "y": 30, "find": "spot:pale@skin"},
           {"text": "A scratch line", "x": 23, "y": 66, "row": 1, "find": "spot:pale@skin"},
           {"text": "A border you can draw", "x": 56, "y": 45, "row": 1, "find": "edge:pale|skin"},
           {"text": "Pigment at each hair", "x": 69, "y": 32, "find": "spot:skin@pale"},
       ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/B4-active-vs-stable.webp", "w": 1820, "h": 1024,
             "alt": "Two areas of brown skin seen from above. The left patch has a soft "
                    "ill-defined border fading gradually into the surrounding skin, with "
                    "scattered small pale spots and a pale line along an old scratch. The "
                    "right patch has a sharp border and small islands of returning colour "
                    "around individual hairs."}},

        # PLACEHOLDERS UNTIL THE CLINIC SENDS THE PHOTOGRAPHS — that is the
        # intended state, not an unfinished one, and the intro says so on the
        # page rather than leaving a reader to guess. `shots` names the frames
        # each case will have, so the series is staged before the images exist
        # and dropping them in is a one-line change per frame.
        #
        # Nothing here may be filled with a stock photograph or an illustration.
        # `build.py` refuses to build a clinical image without a consent record,
        # which is the only reason that rule is reliable.
        {"kind": "ba", "anchor": "results", "eyebrow": "Results",
         "h2": "Progress, documented.",
         "intro": "Real patients, photographed at the clinic, published with their "
                  "written consent. Results differ from person to person: these are "
                  "what happened to these patients, not a promise about you.",
         "cta": ("See all case studies", "results"),
         # Three headline cases, chosen by title rather than by index so that
         # inserting a case in cases.py cannot silently change which three the
         # home page shows. `frames=2` keeps every picture on the row the same
         # size — the three-frame alopecia series runs in full on the results
         # page, where there is room for it.
         "items": cases("Alopecia totalis", "Psoriasis: a thick plaque",
                        "Vitiligo: colour back",
                        frames=2) or HOME_PLACEHOLDERS},

        # Five, not four: the fee step was added 2026-08-02 and the heading has
        # to be counted, not assumed. A page that says "four" above five boxes
        # is exactly the kind of small wrongness that costs a reader's trust in
        # everything else on it.
        {"kind": "steps", "eyebrow": "How it works", "h2": "Five steps, no surprises.",
         "items": [
             {"title": "Message on WhatsApp",
              "body": "One number, answered by the clinic team. Say what you're seeing and "
                      "send a photograph if you have one; they come back with a time."},
             {"title": "Bring your history",
              "body": "Old prescriptions, photographs of a flare, anything you've already "
                      "tried. It shortens the diagnosis."},
             {"title": "Know the fee first",
              "body": f"{FEE_ONLINE_SHOW} {FEE_TAX} for a video consultation, "
                      f"{FEE_CLINIC_SHOW} {FEE_TAX} in person. Consult online first and "
                      f"only the difference is charged if you then need to come in."},
             {"title": "Get a plan, not a package",
              "body": "What it is, how long it takes, and what it will cost, before anything "
                      "begins."},
             {"title": "Review honestly",
              "body": "Chronic conditions are reviewed on a schedule. If something isn't "
                      "working, it changes."},
         ]},

        {"kind": "stats", "anchor": "doctor", "eyebrow": "The doctor",
         "h2": "Dr. (Lt Col) Khagendra Varada",
         "intro": "Forty-five years in dermatology, twenty-five of them serving in the Indian "
                  "Army Medical Corps, where you treat what walks in, and you learn to be "
                  "certain before you act.",
         "items": [("45", "years in practice", "clock"),
                   ("25", "in the Army Medical Corps", "medal"),
                   (PATIENTS, "patients treated", "chat"),
                   ("5.0", "rating on Practo", "star")]},

        # Sits directly under the doctor's figures because it is the argument
        # those figures are evidence FOR — the numbers say how long he has
        # practised, this says what he practises. It also states the site's
        # whole premise, which the H1 only gestures at.
        {"kind": "quote",
         "text": "A patient who understands what is happening to their skin will follow the "
                 "plan. A patient who has only been sold a package will stop at the first "
                 "month that looks like nothing is changing."},

        {"kind": "cards", "anchor": "visit", "eyebrow": "Visit",
         "h2": "One clinic, in Secunderabad.",
         "intro": "The same address the practice has held for years, until recently under the "
                  "name BNR Skin & Vitiligo Hospital. The doctor, the rooms and the patient "
                  "records are unchanged.",
         "items": [
             {"title": "Where it is", "icon": "pin",
              "body": ADDRESS + ".",
              "list": ["Off Wellington Road, a short way from Trimulgherry",
                       "Formerly BNR Skin & Vitiligo Hospital",
                       "Consulting hours: " + HOURS]},
             {"title": "What runs here", "icon": "light",
              "body": "Everything, in one place: the medical clinic, the phototherapy and "
                      "laser room, and the dermatosurgery list.",
              "list": ["Medical dermatology and trichology",
                       "Phototherapy, excimer and laser",
                       "Vitiligo grafting and dermatosurgery"]},
         ]},

        {"kind": "quotes", "anchor": "stories", "eyebrow": "Patient stories",
         "h2": "In their words.",
         "items": [
             ("I consulted him online for my relative's skin problems. Many doctors "
              "couldn't help before, but he listened carefully and gave a friendly, "
              "effective consultation.", "Verified patient · online consultation", "stars"),
             ("He communicates all points of the treatment and welcomes feedback for "
              "the follow-up. He delivers good service to patients.",
              "Verified patient · Practo", "stars"),
             ("The appointment was timely. He was nice and explained things well. The "
              "treatment was effective, and overall I am satisfied.",
              "Verified patient · Practo", "stars"),
             # Read from the live Google listing on 2026-07-30 (4.6 across 31
             # reviews). Reproduced as written apart from trimming; nothing here
             # is paraphrased, and none of it is solicited.
             ("The doctor takes time to carefully identify the root cause of skin "
              "issues rather than just treating symptoms. I really appreciate the "
              "patience shown in listening to all my concerns.",
              "Mani Kumar · Google", "stars"),
             ("Doctor is very patient and understanding. He actually listens to us "
              "and doesn't belittle us. You instantly feel at ease to share your "
              "issues honestly. He is very determined to give us a solution and it "
              "shows in his diagnosis and treatment.",
              "Sandeep Bondugula · Google", "stars"),
             ("Treatment with care and sensitivity. Treat the cause, not the "
              "symptom, is the driving force.",
              "Deepak Sharma · Google", "stars"),
             ("Explains the entire condition faced by the patient really well and "
              "is actively involved in the progress. Always open to answering all "
              "queries. Even the support staff are kind and take care of the "
              "patient well.",
              "Soumya Aketi · Google", "stars"),
             ("Dr Varada and his team go the extra mile in ensuring that patients "
              "get the right solution, with modern medicines. They are very "
              "approachable and caring in their engagement with patients.",
              "Sajjita Mohapatra · Google", "stars"),
             ("Dr Varada is very experienced and friendly, doing great work. I got "
              "myself treated for eczema. Thank you very much.",
              "Shivraj Kumar · Google", "stars"),
         ]},
    ],
    "faq_h2": "Before you come in",
    "faqs": [
        ("Can vitiligo be cured?",
         ["No treatment cures vitiligo. What treatment can do, and often does, is repigment "
          "affected skin and stop the spread.",
          "How much repigments depends on the site, how long the patch has been there, "
          "and whether the disease is stable. You'll be told which of those apply to you "
          "at the first visit."]),
        ("How long before I see a change?",
         "For chronic conditions, months rather than weeks, and the first review is usually "
         "at six to eight weeks. Anything promising faster than that is promising something "
         "it cannot deliver."),
        ("Do I need a referral?",
         "No. Message the clinic on WhatsApp and bring whatever prescriptions or "
         "photographs you already have."),
        ("Is this the same place as BNR Skin & Vitiligo Hospital?",
         ["Yes. BNR Skin & Vitiligo Hospital is the name this practice traded under until "
          "recently. It is the same doctor at the same clinic in Secunderabad, with the "
          "same patient records. Only the name on the door has changed.",
          "If you were treated here before, nothing about your file or your treatment plan "
          "has moved. The Google listing carries both names, so searching for either one "
          "finds the same clinic."]),
        ("Do you treat patients from outside Hyderabad?",
         "Yes. Particularly for vitiligo surgery, where patients travel from across Telangana "
         "and beyond. Send photographs before travelling so we can tell you whether the "
         "procedure is appropriate for your case."),
        ("How do I book?",
         "On WhatsApp. One number, answered by the clinic team, who confirm a time and tell you "
         "what to bring. There is no booking form and no separate app. A single conversation is "
         "the whole process."),
    ],
    "related_h2": "Where most people start",
    "related": [
        ("vitiligo", "Vitiligo treatment",
         "What the disease is, what each treatment does, and what repigmentation "
         "realistically looks like."),
        ("psoriasis", "Psoriasis treatment",
         "Types, triggers, and the difference between clearing a flare and controlling "
         "the disease."),
        ("about-dr-khagendra-varada", "The doctor",
         "Forty-five years in dermatology, and the reason the practice is built around "
         "diagnosis first."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "about-dr-khagendra-varada", "template": "T3", "schema_type": "Physician",
    "crumbs": [("About", None), ("Dr. Khagendra Varada", None)],
    "title": "Dr. (Lt Col) Khagendra Varada: Dermatologist, Hyderabad",
    "meta": "Dr. (Lt Col) Khagendra Varada. MBBS, Dip. Practical Dermatology (Cardiff). 45 "
            "years in dermatology, 25 in the Army Medical Corps, 10,000+ patients.",
    "eyebrow": "The doctor",
    "h1": "Dr. (Lt Col) Khagendra Varada",
    "lede": "A dermatologist and dermatosurgeon of forty-five years. Twenty-five of them in "
            "uniform, where you treat whatever walks in and you learn to be certain before you "
            "act.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Read patient stories", "patient-stories")],
    # The page whose own meta description lists these qualifications was the one
    # page not showing them. They also fill the column beside the portrait,
    # which was carrying two figures against a full-height photograph.
    "creds": CREDS,
    # The rating sits at `b` rather than `c` deliberately: `c` is hidden on a
    # phone to keep the chips off the portrait's face, and the rating is the one
    # figure a patient checking a doctor actually looks for.
    "portrait": [("45", "years in practice"),
                 (RATING, "rated on Practo", "stars"),
                 (PATIENTS, "patients treated")],
    "photo": {"src": "img/dr-varada-hero.webp", "w": 880, "h": 1100,
              "cutout": True,
              "alt": "Dr. (Lt Col) Khagendra Varada, dermatologist and dermatosurgeon, at the clinic in Karkhana, Secunderabad"},
    "sections": [
        {"kind": "prose", "eyebrow": "Background", "h2": "Trained where certainty matters.",
         "body": [
             "Dr. Varada qualified MBBS from Osmania Medical College and spent twenty-five "
             "years as a medical officer in the Indian Army Medical Corps, retiring as a "
             "Lieutenant Colonel. Army dermatology is unglamorous and broad: you see the "
             "whole spectrum, often late, frequently without the option of referring on.",
             "That shaped how the practice runs today. Diagnosis comes before treatment, and "
             "treatment comes with a timeline you are told in advance. Where a condition cannot "
             "be cured, it is described as controllable, not curable, which is the honest word "
             "and, in vitiligo and psoriasis, the accurate one.",
             "Post-service, he built the practice that patients still know as BNR Skin & "
             "Vitiligo Hospital, adding formal training in practical dermatology at Cardiff "
             "University and in aesthetic dermatology through the AAAM. The clinic in "
             "Secunderabad is the same one, under the name Dr. Varada's Skin & Hair Center.",
         ],
         # Fills the empty right-hand column beside the background copy. Each
         # plate is the qualification itself with an emblem beside it — NOT a
         # picture of the certificate, because an invented certificate on a
         # named doctor's page is a forged credential however it is captioned;
         # a reader cannot tell an illustration of a diploma from a scan of one.
         "aside": {
             # NOT "Qualifications" — the section immediately below this one is
             # eyebrowed "Qualifications" and headed "Credentials", and the same
             # word twice in a column is what made this read as two halves of
             # one section that had come apart.
             "title": "Certifications",
             # INDICATIVE EMBLEMS — published deliberately (user's decision,
             # 2026-08-02), still to be replaced with whatever the clinic
             # settles on. None of them is Osmania's, Cardiff's, the AAAM's, the
             # Army's or the IMA's mark: those belong to those bodies and are
             # theirs to grant. These are generic credential badges in the
             # site's own two colours, carrying no lettering of any kind, and
             # the foot line below says so on the page — which is the thing that
             # makes publishing them honest rather than merely defensible.
             "items": [
                 {"award": "MBBS",
                  "where": "Osmania Medical College, Hyderabad",
                  "mark": {"src": "img/emblems/M1-emblem-medicine.webp",
                           "w": 746, "h": 743,
                           "alt": "Indicative emblem: a staff and serpent within "
                                  "a laurel wreath"}},
                 {"award": "Diploma in Practical Dermatology",
                  "where": "Cardiff University, United Kingdom",
                  "mark": {"src": "img/emblems/M2-emblem-university.webp",
                           "w": 872, "h": 872,
                           "alt": "Indicative emblem: a plain shield above an "
                                  "open book"}},
                 {"award": "Diploma in Dermatology",
                  "where": "American Academy of Aesthetic Medicine",
                  "mark": {"src": "img/emblems/M3-emblem-academy.webp",
                           "w": 874, "h": 874,
                           "alt": "Indicative emblem: a starburst within a "
                                  "guilloche ring"}},
                 {"award": "Lieutenant Colonel",
                  "where": "Indian Army Medical Corps",
                  "note": "25 years as a serving medical officer",
                  "mark": {"src": "img/emblems/M4-emblem-service.webp",
                           "w": 772, "h": 772,
                           "alt": "Indicative emblem: a star and chevrons "
                                  "between laurel sprays"}},
                 {"award": "Member",
                  "where": "Indian Medical Association",
                  "mark": {"src": "img/emblems/M5-emblem-association.webp",
                           "w": 748, "h": 751,
                           "alt": "Indicative emblem: a rosette within a "
                                  "hexagon and rope ring"}},
             ],
             "foot": "The emblems above are indicative marks, not the badges of the "
                     "institutions named. The qualifications themselves are on record, "
                     "and the certificates hang at the clinic.",
         }},

        {"kind": "cards", "eyebrow": "Qualifications", "h2": "Credentials",
         "items": [
             {"title": "Medical", "list": [
                 "MBBS: Osmania Medical College",
                 "Diploma in Practical Dermatology: Cardiff University, UK",
                 "Diploma in Dermatology: AAAM",
             ]},
             {"title": "Service", "list": [
                 "Lieutenant Colonel, Indian Army Medical Corps",
                 "25 years as a serving medical officer",
                 "Field and station hospital dermatology",
             ]},
             {"title": "Professional", "list": [
                 "Member, Indian Medical Association",
                 "Dermatosurgery: grafting and excision lists",
                 "Consulting at one clinic, in Secunderabad",
             ]},
         ]},

        {"kind": "quote",
         "text": "A patient who understands what is happening to their skin will follow the "
                 "plan. A patient who has only been sold a package will stop at the first "
                 "month that looks like nothing is changing."},

        {"kind": "split", "eyebrow": "Special interest",
         "h2": "Vitiligo, and the surgery most centres don't offer.",
         "body": ["The practice began as a vitiligo hospital. Four decades on, it remains the "
                  "area with the most depth, including melanocyte transplant and punch grafting "
                  "for stable disease, which relatively few centres in India perform.",
                  "Surgical repigmentation is not for everyone and is not offered to "
                  "everyone. It requires disease that has been stable for a defined period, "
                  "and the assessment for that is a clinical decision made at the first "
                  "visit, not a booking made online."],
         "cta": ("How graft surgery works", "vitiligo-graft-surgery"),
         "items": [
             {"title": "Assessed before it's offered",
              "body": "Stability, site and duration decide whether surgery is appropriate. "
                      "Being told no is a common and correct outcome."},
             {"title": "Patients travel for it",
              "body": "People come from across Telangana and beyond. Send photographs "
                      "before booking travel so the trip is worth making."},
         ]},

        {"kind": "checklist", "eyebrow": "How he works",
         "h2": "What a first appointment is, and isn't.",
         "items": [
             "<b>Is</b> a diagnosis, examined and named",
             "<b>Is</b> a timeline, with a review date",
             "<b>Is</b> the cost of the plan, before it begins",
             "<b>Isn't</b> a package sold on the spot",
             "<b>Isn't</b> a guarantee of a result",
             "<b>Isn't</b> a prescription without an examination",
         ]},
    ],
    "faq_h2": "About the doctor",
    "faqs": [
        ("What are Dr. Varada's qualifications?",
         "MBBS from Osmania Medical College, a Diploma in Practical Dermatology from "
         "Cardiff University in the UK, and a Diploma in Dermatology from the AAAM. He is a "
         "member of the Indian Medical Association and retired from the Indian Army Medical "
         "Corps as a Lieutenant Colonel."),
        ("How many years has he been practising?",
         "Forty-five years in dermatology, twenty-five of which were spent as a serving "
         "medical officer in the Army Medical Corps."),
        ("Is this the same doctor as BNR Skin & Vitiligo Hospital?",
         "Yes. BNR Skin & Vitiligo Hospital is the practice's former name. It is the same "
         "doctor, the same clinic in Secunderabad, the same clinical records and the same "
         "specialism in vitiligo. Now practising as Dr. Varada's Skin & Hair Center."),
        ("Where does he see patients?",
         "At one clinic, in Karkhana, Secunderabad: the address the practice has held for "
         "years. Everything runs there: consultations, phototherapy, laser and the "
         "dermatosurgery list."),
        ("Can I consult him online?",
         "Yes. Video consultations are arranged over WhatsApp and suit second opinions, "
         "chronic condition reviews and patients outside Hyderabad. Anything requiring a "
         "procedure will need an in-person visit."),
    ],
    "related": [
        ("locations-secunderabad", "The clinic in Secunderabad",
         "Where he consults, what runs there, and how to find it."),
        ("contact", "Contact and directions",
         "The WhatsApp number, the phones, and the way in."),
        ("patient-stories", "Patient stories",
         "What patients have written on Practo, reproduced without editing."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "locations-secunderabad", "template": "T3",
    "schema_type": "MedicalClinic", "clinic_index": 0,
    "crumbs": [("Locations", None), ("Secunderabad", None)],
    "title": "Dermatologist in Secunderabad | Dr. Varada's Clinic",
    "meta": "Dr. Varada's Skin & Hair Center, Karkhana, Secunderabad: formerly BNR Skin & "
            "Vitiligo Hospital. Vitiligo, psoriasis, eczema, hair loss. Book on WhatsApp.",
    "eyebrow": "The clinic",
    "h1": "Dermatologist in Secunderabad",
    "lede": "One clinic, in Secunderabad: the consulting rooms, the phototherapy and laser "
            "equipment and the surgical list, all at the same address. The practice you may "
            "know as BNR Skin & Vitiligo Hospital.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Get directions", MAPS)],
    "glance": [
        ("Address", ADDRESS),
        ("Hours", HOURS),
        ("Consultation", f"{FEE_CLINIC_SHOW} {FEE_TAX} in person"),
        ("Formerly", "BNR Skin & Vitiligo Hospital"),
        ("Booking", "WhatsApp. " + PHONE_SHOW),
        ("Serves", "Karkhana, Trimulgherry, West Marredpally, Bowenpally, Alwal"),
        ("Closed", "Sunday"),
    ],
    "sections": [
        {"kind": "callout", "title": "You may know this clinic as BNR Skin & Vitiligo Hospital.",
         "body": "That is the name it traded under until recently, and the Google listing "
                 "still carries it alongside the new one. Nothing else changed: the same "
                 "doctor, the same rooms in Secunderabad, the same patient files. If you "
                 "were treated here before, your history is already on record."},

        {"kind": "prose", "eyebrow": "What runs here",
         "h2": "Everything in one place, deliberately.",
         "body": [
             "A skin clinic that sends you elsewhere for the procedure it just recommended "
             "wastes a visit and, often, a diagnosis. So the consulting room, the phototherapy "
             "and excimer equipment, and the dermatosurgery list are at one address. The one "
             "you are reading about.",
             "That matters most for the work this practice is deepest in. Vitiligo is assessed, "
             "phototherapy is started, stability is judged over months and, when surgery is "
             "appropriate, grafting is done, without a handover in the middle.",
             "It also means a first consultation frequently ends with something being done "
             "the same day: a dermatoscopic look, a scraping, a photograph for the baseline "
             "record against which everything later is compared.",
         ]},

        # The prose above argues that a clinic which sends you elsewhere for the
        # procedure it just recommended wastes a visit. This is that argument in
        # one line of sight: the four things that would otherwise be four
        # addresses, standing together.
        {"kind": "diagram", "eyebrow": "Under one roof",
         "h2": "What is actually in the building.",
         "intro": "A phototherapy cabinet for whole-body treatment, a laser for one patch at "
                  "a time, the lens a diagnosis is made with, and the instruments for the "
                  "surgical list. All at the address above, which is why a consultation here "
                  "often ends with something being done the same day.",
         "caption": "Drawn to scale against each other. Not a photograph of these rooms — "
                    "the equipment, not the premises, is what this shows.",
         "rail": True,
        "labels": [
            {"text": "Phototherapy cabinet", "x": 10, "y": 45, "row": 3, "find": "artwork"},
            {"text": "Excimer and laser", "x": 42, "y": 62, "row": 2, "find": "artwork"},
            {"text": "Dermatoscope", "x": 60, "y": 58, "row": 1, "find": "artwork"},
            {"text": "Dermatosurgery", "x": 77, "y": 80, "find": "artwork"},
        ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/E2-clinic-equipment.webp", "w": 1820, "h": 1024,
             "alt": "Four pieces of dermatology equipment drawn side by side to scale: a "
                    "full-height upright phototherapy cabinet with its doors open and its "
                    "tubes lit, a wheeled trolley carrying a handheld laser, a dermatoscope "
                    "standing on a block, and a shallow tray of clean surgical instruments."}},

        # "Phototherapy runs here" is a claim about equipment, and a list of
        # equipment is the least persuasive form a claim can take. What the
        # cabinet does — and how shallowly it works, which is why it is safe to
        # run for months — is the part a patient is actually weighing up.
        {"kind": "diagram", "eyebrow": "In the light room",
         "h2": "What phototherapy reaches, and what it doesn't.",
         "intro": "Narrowband ultraviolet is not a heat treatment and it does not act on "
                  "the whole body. It penetrates the epidermis and the top of the dermis "
                  "and stops there, which is both why it can be given twice a week for "
                  "months and why it does nothing for anything deeper.",
         "caption": "Sessions are a few minutes each and are given at the clinic, so a "
                    "course does not require a second address. Vitiligo and psoriasis are "
                    "the two conditions it is used most for here.",
         "labels": [
             {"text": "Ultraviolet enters here", "x": 47, "y": 23, "lead": 10, "find": "artwork"},
             {"text": "Pigment cells reactivated", "x": 29, "y": 40, "lead": 29, "find": "artwork"},
             {"text": "Immune cells suppressed, and no deeper", "x": 38, "y": 52, "lead": 20, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D1-phototherapy.webp", "w": 1820, "h": 1024,
             "alt": "A block of skin with a band of fine parallel light rays entering from "
                    "above. The rays penetrate the epidermis and the upper dermis, where "
                    "pigment cells and immune cells are drawn, and stop before the fat "
                    "layer beneath."}},

        {"kind": "cards", "eyebrow": "Available here", "h2": "What you can book",
         "items": [
             {"eyebrow": "Chronic", "title": "Medical dermatology", "list": [
                 "Vitiligo: medical and surgical",
                 "Psoriasis", "Eczema and atopic dermatitis",
                 "Skin allergy and rashes", "Acne and acne scarring"]},
             {"eyebrow": "Aesthetic", "title": "Aesthetic dermatology", "list": [
                 "Botulinum toxin and anti-ageing", "Skin boosters",
                 "RF skin tightening", "Chemical peels", "Laser hair reduction"]},
             {"eyebrow": "Trichology", "title": "Hair", "list": [
                 "Pattern hair loss", "Alopecia areata",
                 "Hair grafting surgery", "Dandruff and scalp disease"]},
         ]},

        fees_block(online_first=False,
                   h2="What an appointment costs",
                   intro="The consultation fee is fixed and is the same for everyone. "
                         "What treatment costs is not, and is quoted after the "
                         "examination — those are two different questions and only "
                         "one of them can honestly be answered in advance."),

        {"kind": "steps", "eyebrow": "Your visit", "h2": "What to expect",
         "items": [
             {"title": "Message on WhatsApp",
              "body": "Say what you're seeing and send a photograph if you have one. The "
                      "clinic team replies with a time. That is the whole booking process."},
             {"title": "Bring what you've tried",
              "body": "Previous prescriptions, biopsy or blood reports, and photographs of "
                      "the condition at its worst."},
             {"title": "Get examined, then quoted",
              "body": f"The consultation is {FEE_CLINIC_SHOW} {FEE_TAX}, known in advance. "
                      f"What treatment costs is given after the examination, when there is "
                      f"something real to cost."},
             {"title": "Leave with a written plan",
              "body": "What was diagnosed, what it needs, and when you're next expected."},
         ]},

        {"kind": "checklist", "eyebrow": "Finding it",
         "h2": "Getting to the clinic.",
         "items": [
             "<b>Karkhana, Secunderabad</b>: off Wellington Road",
             "<b>Plot D13B</b>, Vikrampuri Colony, on Wellington Road",
             "<b>Karkhana</b>, a short way from Trimulgherry and Marredpally",
             f"<b>Listed on Google</b> as {GOOGLE_LISTING}",
             "<b>Parking</b>: outside the clinic gate",
             "<b>Message first</b> if you are travelling any distance",
         ]},

        {"kind": "map", "eyebrow": "On the map",
         "h2": "Where the clinic is.",
         "intro": "Karkhana, off Wellington Road. The pin is the clinic's own Google "
                  "listing, so the directions you get here are the directions the "
                  "clinic gives on the phone."},
    ],
    "faq_h2": "Visiting the clinic",
    "faqs": [
        ("Is this the same place as BNR Skin & Vitiligo Hospital?",
         "Yes. BNR Skin & Vitiligo Hospital is the former name of this practice. Same "
         "doctor, same address in Secunderabad, same records. The Google listing carries "
         "both names, so either one finds the clinic."),
        ("Where exactly is the clinic?",
         "Plot No D13B, Wellington Rd, Vikrampuri Colony, Karkhana, Secunderabad, Telangana "
         "500009. Off Wellington Road, a short way from Trimulgherry and West Marredpally."),
        ("What are the consulting hours?",
         "Monday to Saturday, 11:30 am to 5:00 pm. The clinic is closed on Sunday."),
        ("Do you take walk-ins?",
         "Appointments are arranged on WhatsApp. Walk-ins are seen only if there is a gap, "
         "so messaging first is strongly advised."),
        ("Which procedures are done at this clinic?",
         "Phototherapy and excimer sessions, chemical peels, laser hair reduction, RF "
         "tightening, botulinum toxin, skin boosters, and the dermatosurgery list including "
         "vitiligo grafting and mole, wart and skin tag removal."),
        ("Is parking available?",
         "Yes. There is parking outside the clinic's gate."),
    ],
    "related": [
        ("contact", "Contact and directions",
         "The WhatsApp number, the phones, and what to send before you travel."),
        ("about-dr-khagendra-varada", "The doctor",
         "Forty-five years in dermatology, twenty-five in the Army Medical Corps."),
        ("vitiligo-treatment-hyderabad", "Vitiligo treatment in Hyderabad",
         "The specialism this clinic was built around."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "contact", "template": "T3",
    "crumbs": [("Contact", None)],
    "title": "Contact & Book on WhatsApp | Dr. Varada's, Secunderabad",
    "meta": "Book an appointment at Dr. Varada's Skin & Hair Center, Karkhana, Secunderabad. "
            "Formerly BNR Skin & Vitiligo Hospital.",
    "eyebrow": "Contact",
    "h1": "One number. One conversation.",
    "lede": "Appointments are arranged on WhatsApp: message the clinic, say what you're seeing, "
            "and the team comes back with a time. One conversation, and the fee is on this "
            "page before you start it.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "glance": [
        ("WhatsApp", PHONE_SHOW),
        ("Phone", PHONE_SHOW + " · " + PHONE_ALT_SHOW),
        ("Landline", PHONE_LANDLINE_SHOW),
        ("Consultation", f"{FEE_ONLINE_SHOW} online · {FEE_CLINIC_SHOW} in person, {FEE_TAX}"),
        ("Address", ADDRESS),
        ("Hours", HOURS),
        ("Formerly", "BNR Skin & Vitiligo Hospital"),
    ],
    "sections": [
        {"kind": "cards", "eyebrow": "Three ways in", "h2": "Which one you want",
         "items": [
             {"eyebrow": "Primary", "title": "WhatsApp: " + PHONE_SHOW, "icon": "chat",
              "body": "The clinic's diary is worked from this one conversation. Send what "
                      "you're seeing and a photograph if you have one; the team replies "
                      "with a time and tells you what to bring.",
              "list": ["Appointments and reschedules", "Photographs before you travel",
                       "Video consultation arranged here"]},
             {"eyebrow": "If you'd rather talk", "title": "Call: " + PHONE_SHOW,
              "icon": "phone",
              "body": "For directions, timing or what to bring. A time agreed on the phone "
                      "is confirmed back to you on WhatsApp, so there is one record of it "
                      "and not two.",
              "list": ["Same number as WhatsApp, or " + PHONE_ALT_SHOW,
                       "Landline " + PHONE_LANDLINE_SHOW,
                       "No prescriptions by phone"]},
             {"eyebrow": "Before you decide", "title": "Read the reviews", "icon": "star",
              "body": "Verified reviews on Practo are attached to real appointments and cannot "
                      "be edited by the clinic, which is what makes them worth reading before "
                      "you message anyone.",
              "list": [REVIEWS + " verified reviews on Practo",
                       RATING + " rating · 97% recommend",
                       "More on the Google listing"]},
         ]},

        fees_block(
            h2="What it costs before you message",
            intro="Two fees, both fixed. Knowing them before you start a conversation "
                  "is the point — nobody should have to ask what a consultation costs "
                  "after they have already described their problem to a stranger."),

        {"kind": "cards", "eyebrow": "The clinic", "h2": "Karkhana, Secunderabad",
         "intro": "One consulting location. The address the practice has held for years, under "
                  "the name BNR Skin & Vitiligo Hospital until recently.",
         "items": [
             {"title": "Where to come", "icon": "pin",
              "body": ADDRESS + ".",
              "list": ["On Wellington Road, Vikrampuri Colony",
                       "Listed on Google as " + GOOGLE_LISTING_PLAIN,
                       "Serves Trimulgherry, West Marredpally, Bowenpally, Alwal"]},
             {"title": "When", "icon": "clock",
              "body": HOURS + ". Closed on Sunday.",
              "list": ["Message before travelling any distance",
                       "Walk-ins seen only if there is a gap",
                       "Video consultation if you are out of the city"]},
         ]},

        {"kind": "map", "eyebrow": "Finding us",
         "h2": "The clinic on a map.",
         "intro": "Off Wellington Road in Karkhana. Tap through for turn-by-turn "
                  "directions, or message on WhatsApp if you are close and lost."},

        {"kind": "callout", "warn": True, "title": "This is not an emergency service",
         "body": "For a rapidly spreading rash with fever, blistering across large areas, "
                 "or swelling of the lips or tongue, go to a hospital emergency department. "
                 "Do not wait for a clinic appointment."},

        {"kind": "checklist", "eyebrow": "Travelling to Hyderabad",
         "h2": "Coming from outside the city.",
         "items": [
             "<b>Send photographs first</b>, before booking travel",
             "<b>Say what you've tried</b>, with dates",
             "<b>Ask specifically</b> whether the procedure suits your case",
             "<b>Expect a staged visit</b>: assessment, then procedure",
             "<b>Allow for review</b>: grafting needs follow-up",
             "<b>Consider a video consult</b> for the first opinion",
         ]},
    ],
    "faq_h2": "Getting an appointment",
    "faqs": [
        ("How do I book an appointment?",
         "Message the clinic on WhatsApp at " + PHONE_SHOW + ". Say what you're seeing, "
         "attach a photograph if you have one, and the team replies with a time. That is "
         "the whole process."),
        *FEE_FAQS,
        ("Why is there no booking form on this website?",
         "Because a form is a second queue, and a second queue is where appointments get lost. "
         "One WhatsApp conversation holds the booking, the photographs, the reschedule and the "
         "reminder, in one place both sides can see."),
        ("I found you on Practo. Should I book there?",
         "Message on WhatsApp instead. Practo is used inside the clinic and its reviews are "
         "worth reading, but appointments made there are not the queue the team works from. "
         "WhatsApp is."),
        ("Can I get a prescription without being seen?",
         "No. Repeat prescriptions for an existing plan can be reviewed at a consultation, "
         "including a video consultation, but nothing is prescribed without an examination."),
        ("Do you offer online consultations?",
         "Yes. Ask on WhatsApp and a video consultation is arranged. It suits second "
         "opinions, chronic condition reviews and patients outside Hyderabad."),
        ("What if I need to cancel?",
         "Send a message on the same WhatsApp thread. Doing it there frees the slot "
         "immediately for someone else."),
        ("Is this BNR Skin & Vitiligo Hospital?",
         "Yes: that is the clinic's former name, and it is still what the Google listing shows. "
         "The doctor, the address in Secunderabad and the patient records "
         "are unchanged."),
    ],
    "related": [
        ("locations-secunderabad", "The clinic in Secunderabad",
         "The address, what runs there, and how to find it."),
        ("patient-stories", "Patient stories",
         "Verified Practo reviews, reproduced without editing."),
        ("vitiligo-online-consultation", "Consult online from anywhere in India",
         "How a video consultation for vitiligo actually works."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "results", "template": "T3",
    "crumbs": [("Results", None)],
    "title": "Treatment Results: What Change Looks Like | Dr. Varada's",
    "meta": "How treatment progress is measured and photographed at Dr. Varada's Skin & Hair "
            "Center: vitiligo repigmentation, psoriasis control, acne and hair.",
    "eyebrow": "Results",
    "h1": "What change actually looks like.",
    "lede": "Every image on this page is a real patient who signed a consent form for it to be "
            "published. Where no consented image exists, there is no image — nothing here is "
            "stock photography and nothing here is an illustration.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Read patient stories", "patient-stories")],
    "glance": [
        ("Images", "Consent-documented only"),
        ("Photography", "Standardised lighting and distance"),
        ("Vitiligo", "Repigmentation measured by area and site"),
        ("Psoriasis", "Measured by involved area and symptoms"),
        ("Interval", "Reviewed every 6–8 weeks"),
        ("Guarantee", "None: results vary by person"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The rule", "h2": "Consent first, image second.",
         "body": [
             "Before-and-after photographs are the most persuasive thing a dermatology "
             "practice can publish, and the easiest thing to misuse. Indian Medical Council "
             "advertising rules are strict about it, and rightly so.",
             "The rule here is simple and absolute: an image appears on this site only if the "
             "patient signed a written consent for that specific use. Not a general clinical "
             "consent. A publication consent. Withdrawal is honoured immediately, no reason "
             "required.",
             "That means this page fills in slowly. It also means everything on it is real.",
         ]},

        # The full case studies. A case is a SERIES, not a pair — a chronic
        # condition is judged on whether a change held, which only a sequence
        # can show. The photographs are real, from the clinic; the frames are
        # cropped and matched but never retouched or relit. See content/cases.py.
        {"kind": "ba", "eyebrow": "Documented in clinic",
         "h2": "Progress, photographed at fixed intervals",
         "intro": "Every case the clinic has consent to show. Each one is photographed "
                  "in the same position at every visit, so the two pictures can be "
                  "compared honestly. Results differ from person to person, and a few "
                  "cases have no starting photograph — those say so.",
         # Falls back to labelled empty frames while a case waits on its consent
         # record, because a placeholder is more honest than a stock photograph
         # — which is what this page says about itself either way.
         "items": cases() or RESULTS_PLACEHOLDERS},

        # The page's argument is that measurement, not photography, is what
        # tells you whether treatment is working — but until here it asserts
        # that in prose while the only visual on the page is an empty frame. A
        # Wood's lamp is the plainest possible demonstration: the same skin,
        # twice, with the second showing what the first could not.
        {"kind": "diagram", "eyebrow": "Measuring, not photographing",
         "h2": "The extent is often larger than it looks.",
         "intro": "A vitiligo patch does not end where the eye says it ends. Under a Wood's "
                  "lamp the affected skin fluoresces and the true border appears, along with "
                  "patches that ordinary light does not show at all. That is the baseline "
                  "everything later is compared against.",
         "caption": "Which is also why a course judged by photographs alone can look like it "
                    "is doing nothing while it is working, or the reverse. The lamp is used "
                    "at the first visit and at reviews.",
         "rail": True,
       "labels": [
           {"text": "Two faint patches", "x": 20, "y": 42, "find": "artwork"},
           {"text": "Under the lamp", "x": 66, "y": 12, "row": 1, "find": "artwork"},
           {"text": "The same two, sharp", "x": 56, "y": 49, "row": 2, "find": "artwork"},
           {"text": "Three more", "x": 74, "y": 34, "find": "artwork"},
       ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/B13-woods-lamp.webp", "w": 1820, "h": 1024,
             "alt": "The same patch of brown forearm skin shown twice. In ordinary daylight "
                    "two pale patches are faint and low in contrast. Under the violet light "
                    "of a Wood's lamp the same two patches glow with sharp borders, and "
                    "three further patches appear that were not visible before."}},

        {"kind": "cards", "eyebrow": "How progress is measured",
         "h2": "What is being tracked, condition by condition",
         "items": [
             {"eyebrow": "Chronic", "title": "Vitiligo",
              "body": "Repigmentation is scored by the proportion of the patch that has "
                      "recoloured and where it started from. Perifollicular islands, or inward "
                      "from the edge.",
              "list": ["Patch area and site", "Whether spread has stopped",
                       "Colour match at the margin"]},
             {"eyebrow": "Chronic", "title": "Psoriasis",
              "body": "Measured by how much body surface is involved and how much it is "
                      "affecting sleep, work and itch. Not by photographs alone.",
              "list": ["Involved surface area", "Scale, redness, thickness",
                       "Time between flares"]},
             {"eyebrow": "Aesthetic", "title": "Acne, hair and aesthetics",
              "body": "Lesion counts for acne, pull tests and trichoscopy for hair, and "
                      "standardised photographs for aesthetic work.",
              "list": ["Inflammatory lesion count", "Trichoscopy imaging",
                       "Fixed-angle photography"]},
         ]},

        {"kind": "callout", "warn": True, "title": "No result here is a promise",
         "body": "Individual outcomes vary with the condition, its duration, the site, and "
                 "how consistently treatment is followed. A photograph of one patient's "
                 "result is evidence that it happened for them, not a prediction for you."},

        {"kind": "split", "eyebrow": "Why this matters",
         "h2": "Honest photography is also better medicine.",
         "body": ["A standardised photograph taken at the first visit is the only reliable "
                  "way to answer the question every chronic patient eventually asks: is this "
                  "actually better, or do I just want it to be?",
                  "Memory is a poor instrument over six months. The camera is not. Baseline "
                  "photographs are taken for the clinical record whether or not they are ever "
                  "published, and they are only ever published with consent."],
         "cta": ("Book on WhatsApp", WHATSAPP),
         "items": [
             {"title": "Photographed at baseline",
              "body": "Same distance, same light, same angle, so the comparison means "
                      "something."},
             {"title": "Reviewed on a schedule",
              "body": "Every six to eight weeks for chronic disease. If nothing has moved, "
                      "the plan changes."},
         ]},
    ],
    "faq_h2": "About results",
    "faqs": [
        ("Why are there so few before-and-after photographs?",
         "Because only images with a signed publication consent are used. Building that "
         "library takes time, and no image is added without it."),
        ("Will I get the same result as the photographs show?",
         "Not necessarily. Results vary with the condition, how long it has been present, "
         "the body site and how consistently treatment is followed. No result shown here is "
         "a prediction of yours."),
        ("Are the photographs edited?",
         "No retouching, no relighting, no change of angle between the two images. The "
         "point of a standardised photograph is that it can be trusted."),
        ("Will my photographs be published?",
         "Only if you sign a specific written consent for publication. Clinical photographs "
         "taken for your record are not publication consent, and you can decline either "
         "without affecting your treatment."),
        ("Can I withdraw consent later?",
         "Yes, at any time and without giving a reason. The image is removed."),
    ],
    "related": [
        ("patient-stories", "Patient stories", "What patients wrote themselves, on Practo."),
        ("vitiligo", "Vitiligo treatment", "What repigmentation realistically looks like."),
        ("psoriasis", "Psoriasis treatment", "Control, measured properly."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "patient-stories", "template": "T3",
    "crumbs": [("Patient stories", None)],
    "title": "Patient Stories & Reviews | Dr. Varada's Skin & Hair Center",
    "meta": "What patients have written about Dr. (Lt Col) Khagendra Varada. Reproduced from "
            "verified reviews on Practo and Google, unedited.",
    "eyebrow": "In their words",
    "h1": "What patients wrote themselves.",
    "lede": "More than 10,000 patients have been treated here. Sixty-five of them left a "
            "verified review, on platforms the clinic does not control and cannot edit. Those "
            "are the ones you can read. Unsolicited, reproduced as written.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Read them on Practo", PRACTO_REVIEWS)],
    "glance": [
        ("Patients treated", PATIENTS),
        ("Verified reviews", REVIEWS),
        ("Rating", RATING + " on Practo"),
        ("Edited", "No: reproduced as written"),
        ("Updated", "Synced from Practo"),
        ("Incentives", "None offered for reviews"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Where these come from",
         "h2": "Reviews the clinic cannot edit.",
         "body": [
             "Testimonials written for a clinic's own website are worth very little, because "
             "the clinic chooses which ones appear. Practo reviews are attached to a "
             "verified appointment and sit on someone else's platform.",
             "So that is what this page shows. The rating and the count are pulled from the "
             "Practo profile and refreshed automatically rather than typed in by hand, which "
             "means the number here is the number there, including on the days it goes down.",
             "Individual stories are reproduced without editing for tone or length. Where a "
             "story names a condition or an outcome, it is that patient's experience and "
             "not a claim about what treatment does generally.",
         ]},

        {"kind": "quotes", "eyebrow": "From Practo", "h2": "The stories themselves",
         "intro": "Reproduced as written, from both platforms. The full sets live on "
                  "Practo and Google, where the clinic cannot edit them.",
         "items": [
             ("I consulted him online for my relative's skin problems. Many doctors "
              "couldn't help before, but he listened carefully and gave a friendly, "
              "effective consultation.", "Verified patient · online consultation", "stars"),
             ("He communicates all points of the treatment and welcomes feedback for "
              "the follow-up. He delivers good service to patients.",
              "Verified patient · Practo", "stars"),
             ("The appointment was timely. He was nice and explained things well. The "
              "treatment was effective, and overall I am satisfied.",
              "Verified patient · Practo", "stars"),
             # Read from the live Google listing on 2026-07-30 (4.6 across 31
             # reviews). Reproduced as written apart from trimming; nothing here
             # is paraphrased, and none of it is solicited.
             ("The doctor takes time to carefully identify the root cause of skin "
              "issues rather than just treating symptoms. I really appreciate the "
              "patience shown in listening to all my concerns.",
              "Mani Kumar · Google", "stars"),
             ("Doctor is very patient and understanding. He actually listens to us "
              "and doesn't belittle us. You instantly feel at ease to share your "
              "issues honestly. He is very determined to give us a solution and it "
              "shows in his diagnosis and treatment.",
              "Sandeep Bondugula · Google", "stars"),
             ("Treatment with care and sensitivity. Treat the cause, not the "
              "symptom, is the driving force.",
              "Deepak Sharma · Google", "stars"),
             ("Explains the entire condition faced by the patient really well and "
              "is actively involved in the progress. Always open to answering all "
              "queries. Even the support staff are kind and take care of the "
              "patient well.",
              "Soumya Aketi · Google", "stars"),
             ("Dr Varada and his team go the extra mile in ensuring that patients "
              "get the right solution, with modern medicines. They are very "
              "approachable and caring in their engagement with patients.",
              "Sajjita Mohapatra · Google", "stars"),
             ("Dr Varada is very experienced and friendly, doing great work. I got "
              "myself treated for eczema. Thank you very much.",
              "Shivraj Kumar · Google", "stars"),
         ]},

        {"kind": "callout", "title": "Why reviews are asked for, but never bought",
         "body": "Patients are asked once, at reception, with a card. There is no discount, "
                 "no free session and no follow-up chasing. A review that had to be paid "
                 "for tells you nothing about the medicine."},

        {"kind": "checklist", "eyebrow": "Reading reviews well",
         "h2": "What is actually worth reading in them.",
         "items": [
             "<b>Whether the condition matches yours</b>: vitiligo reviews say little about "
             "acne",
             "<b>How long they'd been treated</b>: a first visit rates the manner, not the "
             "result",
             "<b>What they say about being told no</b>",
             "<b>Whether costs were explained upfront</b>",
             "<b>The negative ones</b>, and how they were answered",
             "<b>The dates</b>: a practice can change",
         ]},
    ],
    "faq_h2": "About these reviews",
    "faqs": [
        ("Are these reviews verified?",
         "They are Practo reviews, which are tied to an appointment recorded on Practo. The "
         "clinic cannot add, edit or delete them, which is the point of citing them rather than "
         "testimonials chosen by us."),
        ("Does the clinic offer anything in return for a review?",
         "No. Patients are asked once, at reception. There is no incentive, and offering one "
         "would make the reviews worthless."),
        ("Why not publish testimonials directly on the site?",
         "Because a testimonial the clinic selects is a marketing asset, not evidence. "
         "Reviews on a third-party platform are harder to curate and therefore worth more."),
        ("Can I leave a review after an online consultation?",
         "Yes. A video consultation can be reviewed in the same way as an in-person "
         "visit."),
        ("Do reviews say anything about what results I'll get?",
         "No. A review describes one person's experience. Treatment outcomes vary with the "
         "condition, its duration and the individual, and nothing here should be read as a "
         "prediction."),
    ],
    "related": [
        ("results", "Treatment results", "How progress is measured and photographed."),
        ("about-dr-khagendra-varada", "The doctor", "Forty-five years, and how he works."),
        ("contact", "Book an appointment", "Both clinics, and the three ways to reach them."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "blog", "template": "T4",
    "crumbs": [("Journal", None)],
    "title": "Skin & Hair Journal: Dermatology Notes | Dr. Varada's",
    "meta": "Plain-language notes on skin and hair from Dr. Varada's Skin & Hair Center, "
            "Hyderabad: what conditions are, what treatments do, what advice to ignore.",
    "eyebrow": "Journal",
    "h1": "Notes on skin and hair.",
    "lede": "Short, plain pieces on what patients ask in the consulting room. Written to be "
            "read by the person with the condition, not by another dermatologist.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Browse conditions", "vitiligo")],
    "glance": [
        ("Written by", "Dr. (Lt Col) Khagendra Varada"),
        ("Cadence", "Two pieces a week"),
        ("Reviewed", "Every piece, dated"),
        ("Topics", "Vitiligo, psoriasis, hair, acne, aesthetics"),
        ("Languages", "English now · Telugu next"),
        ("Claims", "No cures, no guarantees"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What this is",
         "h2": "The answers that don't fit in a consultation.",
         "body": [
             "A consultation has fifteen minutes in it. Some questions need more than that: why "
             "a diet change did nothing for the vitiligo, why the psoriasis came back in "
             "December, why the hair fall got worse three months after the fever.",
             "Those answers go here, at the length they actually need, and each one links "
             "back to the condition page it belongs to.",
             "Every piece carries a review date. Dermatology moves. JAK inhibitors in vitiligo "
             "were not a real option a decade ago, and an undated medical article is a "
             "liability.",
         ]},

        {"kind": "cards", "eyebrow": "Sections", "h2": "What gets written about",
         "items": [
             {"eyebrow": "Chronic", "title": "Vitiligo and psoriasis",
              "body": "The two conditions the practice has the most depth in, and the two "
                      "where the internet is least reliable.",
              "list": ["Myths worth killing", "What new treatments actually do",
                       "Living with a visible condition"]},
             {"eyebrow": "Trichology", "title": "Hair and scalp",
              "body": "Hair loss questions outnumber every other category, and most of them "
                      "have the same three causes.",
              "list": ["Shedding versus thinning", "What blood tests are worth doing",
                       "Why a product changed nothing"]},
             {"eyebrow": "Aesthetic", "title": "Skin, honestly",
              "body": "What aesthetic treatments do, what they cost, and where the "
                      "marketing outruns the evidence.",
              "list": ["Peels and pigmentation", "Sunscreen, properly",
                       "When not to have a procedure"]},
         ]},

        {"kind": "media", "eyebrow": "Latest", "h2": "Recent pieces",
         "body": "[ Post grid. Populated once the editorial calendar starts. Two pieces a week, "
                 "each linking up to its condition page. ]"},

        {"kind": "callout", "title": "General information, not your diagnosis",
         "body": "Everything written here is general. It cannot account for your history, your "
                 "medication or what your skin actually looks like, and it is not a substitute "
                 "for being examined."},
    ],
    "faq_h2": "About the journal",
    "faqs": [
        ("Who writes these pieces?",
         "They are written and medically reviewed by Dr. (Lt Col) Khagendra Varada. Each "
         "piece carries the reviewer's name and the date it was last checked."),
        ("How often is it updated?",
         "Two pieces a week, with older pieces re-reviewed on a rolling basis. The review "
         "date on each piece tells you when it was last checked."),
        ("Can I ask for a topic?",
         "Yes. The questions asked most often in clinic are where most of these come from. Send "
         "a suggestion by WhatsApp."),
        ("Will there be Telugu articles?",
         "Yes. Telugu versions of the most-read condition pieces are planned, because there "
         "is real search demand and almost no reliable clinical content in the language."),
        ("Can I rely on this instead of seeing a doctor?",
         "No. These are general explanations. A rash that looks identical in two people can "
         "be two different diseases, which is exactly why examination exists."),
    ],
    "related": [
        ("vitiligo", "Vitiligo treatment", "The full reference section."),
        ("psoriasis", "Psoriasis treatment", "Types, triggers and control."),
        ("hair-loss-treatment-hyderabad", "Hair loss", "Diagnosed before it's treated."),
    ],
},

]
