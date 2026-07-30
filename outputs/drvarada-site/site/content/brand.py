"""T3 — brand and utility pages: home, the doctor, both clinics, contact, results,
patient stories, blog index.

Copy rules that bind every line here (DESIGN.md § Voice, MASTER_PLAN § 5):
no cure claims, no guarantees, no superlatives, no named competitors, and every
number attributable. "45 years in practice" is verifiable. "Thousands of happy
patients" is not, so it does not appear.
"""

from chrome import PRACTO, PRACTO_JH, PRACTO_ONLINE, PRACTO_WM, PHONE, WHATSAPP

CREDS = [
    "MBBS · Osmania Medical College",
    "25 yrs · Army Medical Corps",
    "Dip. Practical Dermatology · Cardiff, UK",
    "Dip. Dermatology · AAAM",
]

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "index", "template": "T3",
    "title": "Dermatologist in Hyderabad — 45 Years | Dr. Varada's",
    "meta": "Vitiligo, psoriasis, acne, hair loss and modern aesthetics with Dr. (Lt Col) "
            "Khagendra Varada — 45 years in practice, 25 in the Army Medical Corps. Two "
            "clinics in Hyderabad. Book on Practo.",
    "eyebrow": "Dermatology · Trichology · Aesthetics",
    "h1": "Skin that's <em>understood</em><br>before it's treated.",
    "lede": "Vitiligo, psoriasis, acne, hair loss and modern aesthetics — with "
            "Dr. (Lt Col) Khagendra Varada, a dermatologist and dermatosurgeon of 45 years, "
            "25 of them in the Indian Army Medical Corps.",
    "acts": [("Book on Practo", PRACTO), ("See both clinics", "contact")],
    "creds": CREDS,
    "portrait": [("45", "years in practice"), ("5.0", "65 patient stories")],
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
             ("Hair falling more than usual", "hair-loss-treatment-hyderabad", "lilac"),
             ("Patchy bald spots", "alopecia-treatment-hyderabad", "lilac"),
             ("Flaking, itchy scalp", "dandruff-treatment", "lilac"),
             ("Greying early", "premature-greying-treatment", "lilac"),
             ("Fine lines and laxity", "anti-aging-botox-hyderabad", "apricot"),
             ("Dull, dehydrated skin", "skin-boosters-hyderabad", "apricot"),
             ("Unwanted hair", "laser-hair-reduction-hyderabad", "apricot"),
             ("A mole or skin tag", "dermatosurgery-hyderabad", "apricot"),
         ]},

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
              ],
              "go": ("Vitiligo &amp; psoriasis in depth", "vitiligo")},
             {"accent": "apricot", "title": "Aesthetic",
              "body": "Performed by the dermatologist, not a technician. Conservative "
                      "dosing, honest expectations.",
              "list": [
                  ("Anti-ageing &amp; botulinum", "anti-aging-botox-hyderabad"),
                  ("Skin boosters", "skin-boosters-hyderabad"),
                  ("RF skin tightening", "rf-skin-tightening-hyderabad"),
                  ("Bespoke peels", "chemical-peels-hyderabad"),
                  ("Laser hair reduction", "laser-hair-reduction-hyderabad"),
              ],
              "go": ("How we approach aesthetics", "anti-aging-botox-hyderabad")},
             {"accent": "lilac", "title": "Hair",
              "body": "Hair fall has causes — thyroid, iron, hormones, genetics. We find "
                      "yours before treating.",
              "list": [
                  ("Hair fall &amp; pattern loss", "hair-loss-treatment-hyderabad"),
                  ("Alopecia areata, totalis &amp; universalis",
                   "alopecia-treatment-hyderabad"),
                  ("Hair grafting surgery", "hair-grafting-hyderabad"),
                  ("Dandruff &amp; scalp care", "dandruff-treatment"),
                  ("Premature greying", "premature-greying-treatment"),
              ],
              "go": ("Start with a diagnosis", "hair-loss-treatment-hyderabad")},
         ]},

        {"kind": "split", "anchor": "specialisms", "eyebrow": "The specialisms",
         "h2": "Vitiligo and psoriasis, treated for four decades.",
         "body": ["The practice began as a vitiligo hospital, and that remains the deepest "
                  "part of it — including surgical repigmentation, which comparatively few "
                  "centres in India offer. Patients travel from outside Telangana for it.",
                  "Because these are lifelong conditions, both have their own reference "
                  "sections on this site: what the disease actually is, what each treatment "
                  "can and cannot do, and what it costs before you commit to it."],
         "cta": ("Read the vitiligo section", "vitiligo"),
         "items": [
             {"title": "Vitiligo",
              "body": "Medical repigmentation, narrowband UVB, excimer laser and melanocyte "
                      "grafting for stable disease. The first appointment is a diagnosis and "
                      "a realistic timeline — not a package."},
             {"title": "Psoriasis",
              "body": "Long-term control rather than a one-off clearance: topical and "
                      "systemic therapy, phototherapy, and the triggers worth changing."},
         ]},

        {"kind": "ba", "anchor": "results", "eyebrow": "Results",
         "h2": "Progress, documented.",
         "intro": "Photographs taken in clinic under the same lighting, shared with "
                  "patient consent. Results differ between individuals — these are "
                  "examples, not promises.",
         "items": [
             ("Vitiligo — repigmentation", "Excimer phototherapy · duration on file"),
             ("Plaque psoriasis — clearance", "Topical and phototherapy protocol"),
             ("Acne — active lesion control", "Medical protocol and peels"),
         ]},

        {"kind": "steps", "eyebrow": "How it works", "h2": "Four steps, no surprises.",
         "items": [
             {"title": "Book on Practo",
              "body": "Pick a clinic and a time. The whole team works from Practo, so your "
                      "slot is real the moment you take it."},
             {"title": "Bring your history",
              "body": "Old prescriptions, photographs of a flare, anything you've already "
                      "tried. It shortens the diagnosis."},
             {"title": "Get a plan, not a package",
              "body": "What it is, how long it takes, and what it will cost — before "
                      "anything begins."},
             {"title": "Review honestly",
              "body": "Chronic conditions are reviewed on a schedule. If something isn't "
                      "working, it changes."},
         ]},

        {"kind": "stats", "anchor": "doctor", "eyebrow": "The doctor",
         "h2": "Dr. (Lt Col) Khagendra Varada",
         "intro": "Forty-five years in dermatology, twenty-five of them serving in the "
                  "Indian Army Medical Corps — where you treat what walks in, and you learn "
                  "to be certain before you act.",
         "items": [("45", "years in practice"), ("25", "in the Army Medical Corps"),
                   ("2", "clinics in Hyderabad"), ("5.0", "rating on Practo")]},

        {"kind": "cards", "anchor": "visit", "eyebrow": "Visit",
         "h2": "Two clinics, different hours.",
         "intro": "Morning consultations in West Marredpally, afternoons and evenings in "
                  "Jubilee Hills.",
         "items": [
             {"title": "Jubilee Hills",
              "body": "The full clinic — dermatology, trichology and aesthetics. "
                      "Mon–Sat, 1:30 – 8:00 pm.",
              "list": ["Aesthetic procedures", "Phototherapy and laser",
                       "Dermatosurgery lists"]},
             {"title": "West Marredpally",
              "body": "Early consultations before work. Mon–Sat, 7:00 – 9:00 am.",
              "list": ["Medical dermatology", "Chronic condition reviews",
                       "Follow-ups and prescriptions"]},
         ]},

        {"kind": "quotes", "anchor": "stories", "eyebrow": "Patient stories",
         "h2": "In their words.",
         "items": [
             ("I consulted him online for my relative's skin problems. Many doctors "
              "couldn't help before, but he listened carefully and gave a friendly, "
              "effective consultation.", "Verified patient · online consultation"),
             ("He communicates all points of the treatment and welcomes feedback for "
              "the follow-up. He delivers good service to patients.",
              "Verified patient · Practo"),
             ("The appointment was timely. He was nice and explained things well. The "
              "treatment was effective, and overall I am satisfied.",
              "Verified patient · Practo"),
         ]},
    ],
    "faq_h2": "Before you come in",
    "faqs": [
        ("Can vitiligo be cured?",
         ["No treatment cures vitiligo. What treatment can do — and often does — is "
          "repigment affected skin and stop the spread.",
          "How much repigments depends on the site, how long the patch has been there, "
          "and whether the disease is stable. You'll be told which of those apply to you "
          "at the first visit."]),
        ("How long before I see a change?",
         "For chronic conditions, months rather than weeks, and the first review is usually "
         "at six to eight weeks. Anything promising faster than that is promising something "
         "it cannot deliver."),
        ("Do I need a referral?",
         "No. Book directly on Practo and bring whatever prescriptions or photographs you "
         "already have."),
        ("Do you treat patients from outside Hyderabad?",
         "Yes — particularly for vitiligo surgery, where patients travel from across "
         "Telangana and beyond. Send photographs before travelling so we can tell you "
         "whether the procedure is appropriate for your case."),
        ("Which clinic should I book?",
         "Book West Marredpally for a morning medical consultation, and Jubilee Hills for "
         "anything procedural or aesthetic. If you book the wrong one, the team will move "
         "you rather than turn you away."),
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
         "Forty-five years, two clinics, and the reason the practice is built around "
         "diagnosis first."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "about-dr-khagendra-varada", "template": "T3", "schema_type": "Physician",
    "crumbs": [("About", None), ("Dr. Khagendra Varada", None)],
    "title": "Dr. (Lt Col) Khagendra Varada — Dermatologist, Hyderabad",
    "meta": "Dr. (Lt Col) Khagendra Varada, MBBS, Dip. Practical Dermatology (Cardiff) — "
            "45 years in dermatology and dermatosurgery, 25 in the Indian Army Medical "
            "Corps. Vitiligo and psoriasis are the deepest part of the practice.",
    "eyebrow": "The doctor",
    "h1": "Dr. (Lt Col) Khagendra Varada",
    "lede": "A dermatologist and dermatosurgeon of forty-five years — twenty-five of them "
            "in uniform, where you treat whatever walks in and you learn to be certain "
            "before you act.",
    "acts": [("Book a consultation", PRACTO), ("See both clinics", "contact")],
    "portrait": [("45", "years in practice"), ("25", "in the Army Medical Corps")],
    "sections": [
        {"kind": "prose", "eyebrow": "Background", "h2": "Trained where certainty matters.",
         "body": [
             "Dr. Varada qualified MBBS from Osmania Medical College and spent twenty-five "
             "years as a medical officer in the Indian Army Medical Corps, retiring as a "
             "Lieutenant Colonel. Army dermatology is unglamorous and broad: you see the "
             "whole spectrum, often late, frequently without the option of referring on.",
             "That shaped how the practice runs today. Diagnosis comes before treatment, "
             "and treatment comes with a timeline you are told in advance. Where a "
             "condition cannot be cured, it is described as controllable, not curable — "
             "which is the honest word and, in vitiligo and psoriasis, the accurate one.",
             "Post-service, he built the practice that patients still know as BNR Skin & "
             "Vitiligo Hospital, adding formal training in practical dermatology at Cardiff "
             "University and in aesthetic dermatology through the AAAM. He practises as a "
             "dermatologist and dermatosurgeon across both Hyderabad clinics.",
         ]},

        {"kind": "cards", "eyebrow": "Qualifications", "h2": "Credentials",
         "items": [
             {"title": "Medical", "list": [
                 "MBBS — Osmania Medical College",
                 "Diploma in Practical Dermatology — Cardiff University, UK",
                 "Diploma in Dermatology — AAAM",
             ]},
             {"title": "Service", "list": [
                 "Lieutenant Colonel, Indian Army Medical Corps",
                 "25 years as a serving medical officer",
                 "Field and station hospital dermatology",
             ]},
             {"title": "Professional", "list": [
                 "Member, Indian Medical Association",
                 "Dermatosurgery — grafting and excision lists",
                 "Practising across two Hyderabad clinics",
             ]},
         ]},

        {"kind": "quote",
         "text": "A patient who understands what is happening to their skin will follow the "
                 "plan. A patient who has only been sold a package will stop at the first "
                 "month that looks like nothing is changing."},

        {"kind": "split", "eyebrow": "Special interest",
         "h2": "Vitiligo, and the surgery most centres don't offer.",
         "body": ["The practice began as a vitiligo hospital. Four decades on, it remains "
                  "the area with the most depth — including melanocyte transplant and "
                  "punch grafting for stable disease, which relatively few centres in India "
                  "perform.",
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
         "doctor, the same clinical records and the same specialism in vitiligo — now "
         "practising as Dr. Varada's Skin & Hair Center."),
        ("Does he see patients at both clinics?",
         "Yes. West Marredpally runs early mornings, Mon–Sat 7–9 am, for medical "
         "consultations. Jubilee Hills runs Mon–Sat 1:30–8 pm and carries the procedural "
         "and aesthetic work."),
        ("Can I consult him online?",
         "Yes, through Practo's video consultation. It suits second opinions, chronic "
         "condition reviews and patients outside Hyderabad. Anything requiring a procedure "
         "will need an in-person visit."),
    ],
    "related": [
        ("locations-jubilee-hills", "Jubilee Hills clinic",
         "Afternoons and evenings — the full clinic, including procedures."),
        ("locations-west-marredpally", "West Marredpally clinic",
         "Early mornings, before work — medical dermatology and reviews."),
        ("patient-stories", "Patient stories",
         "What patients have written on Practo, reproduced without editing."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "locations-jubilee-hills", "template": "T3",
    "schema_type": "MedicalClinic", "clinic_index": 0,
    "crumbs": [("Locations", None), ("Jubilee Hills", None)],
    "title": "Dermatologist in Jubilee Hills — Skin & Hair Clinic | Dr. Varada's",
    "meta": "Dr. Varada's Skin & Hair Center in Jubilee Hills, Hyderabad. Dermatology, "
            "trichology and aesthetics, Mon–Sat 1:30–8 pm. Vitiligo, psoriasis, acne, hair "
            "loss, botox, peels and laser. Book on Practo.",
    "eyebrow": "Locations",
    "h1": "Dermatologist in Jubilee Hills",
    "lede": "The full clinic — medical dermatology, trichology and aesthetics, plus the "
            "procedure lists. Afternoons and evenings, Monday to Saturday.",
    "acts": [("Book this clinic", PRACTO_JH), ("Call the clinic", PHONE)],
    "glance": [
        ("Hours", "Mon–Sat, 1:30 – 8:00 pm"),
        ("Closed", "Sunday"),
        ("Best for", "Procedures, aesthetics, first consultations"),
        ("Serves", "Jubilee Hills, Banjara Hills, Madhapur, Gachibowli, Film Nagar"),
        ("Booking", "Practo — no walk-in queue"),
        ("Address", "TODO — to be supplied by the clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What runs here",
         "h2": "The clinic that carries the equipment.",
         "body": [
             "Jubilee Hills is where the procedural work happens: phototherapy and excimer "
             "sessions, chemical peels, laser hair reduction, RF tightening, botulinum "
             "toxin, skin boosters, and the dermatosurgery list — mole, wart and skin tag "
             "removal, and vitiligo grafting.",
             "It is also the clinic most first-time patients are booked into, because a "
             "first consultation frequently ends with something being done the same day: "
             "a dermatoscopic look, a scraping, a photograph for the baseline record.",
             "Afternoon and evening hours are deliberate. Aesthetic and procedural "
             "appointments run better when nobody is trying to get to an office afterwards.",
         ]},

        {"kind": "cards", "eyebrow": "Available here", "h2": "What you can book",
         "items": [
             {"eyebrow": "Chronic", "title": "Medical dermatology", "list": [
                 "Vitiligo — medical and surgical",
                 "Psoriasis", "Eczema and atopic dermatitis",
                 "Skin allergy and rashes", "Acne and acne scarring"]},
             {"eyebrow": "Aesthetic", "title": "Aesthetic dermatology", "list": [
                 "Botulinum toxin and anti-ageing", "Skin boosters",
                 "RF skin tightening", "Chemical peels", "Laser hair reduction"]},
             {"eyebrow": "Trichology", "title": "Hair", "list": [
                 "Pattern hair loss", "Alopecia areata",
                 "Hair grafting surgery", "Dandruff and scalp disease"]},
         ]},

        {"kind": "callout", "title": "Coming from Banjara Hills, Madhapur or Gachibowli?",
         "body": "Jubilee Hills is the nearer of the two clinics for the western corridor. "
                 "There is one practice with two locations, not separate teams — your "
                 "records follow you between them."},

        {"kind": "steps", "eyebrow": "Your visit", "h2": "What to expect",
         "items": [
             {"title": "Book a slot on Practo",
              "body": "The clinic runs entirely on Practo, so a booked time is a real time. "
                      "There is no separate waiting list."},
             {"title": "Bring what you've tried",
              "body": "Previous prescriptions, biopsy or blood reports, and photographs of "
                      "the condition at its worst."},
             {"title": "Get examined, then quoted",
              "body": "Costs are given after the examination, when there is something real "
                      "to cost. Not before."},
             {"title": "Leave with a written plan",
              "body": "What was diagnosed, what it needs, and when you're next expected."},
         ]},
    ],
    "faq_h2": "Visiting Jubilee Hills",
    "faqs": [
        ("What are the Jubilee Hills clinic hours?",
         "Monday to Saturday, 1:30 pm to 8:00 pm. The clinic is closed on Sundays. "
         "For a morning appointment, book the West Marredpally clinic instead."),
        ("Do you take walk-ins?",
         "Appointments are booked through Practo. Walk-ins are seen only if there is a gap, "
         "so booking is strongly advised — particularly for evening slots."),
        ("Which procedures are done at this clinic?",
         "Phototherapy and excimer sessions, chemical peels, laser hair reduction, RF "
         "tightening, botulinum toxin, skin boosters, and the dermatosurgery list including "
         "vitiligo grafting and mole, wart and skin tag removal."),
        ("Is parking available?",
         "TODO — to be confirmed by the clinic before this page goes live."),
        ("Can I be seen at one clinic and followed up at the other?",
         "Yes. It is one practice with two locations and one set of records. Many patients "
         "have their first consultation in Jubilee Hills and their reviews in West "
         "Marredpally, or the reverse."),
    ],
    "related": [
        ("locations-west-marredpally", "West Marredpally clinic",
         "Early morning consultations, Mon–Sat 7–9 am."),
        ("contact", "Contact and directions",
         "Both clinics, hours, and how to reach the team."),
        ("about-dr-khagendra-varada", "The doctor",
         "Forty-five years in dermatology, twenty-five in the Army Medical Corps."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "locations-west-marredpally", "template": "T3",
    "schema_type": "MedicalClinic", "clinic_index": 1,
    "crumbs": [("Locations", None), ("West Marredpally", None)],
    "title": "Dermatologist in West Marredpally, Secunderabad | Dr. Varada's",
    "meta": "Dr. Varada's Skin & Hair Center in West Marredpally, Secunderabad. Early "
            "morning dermatology consultations, Mon–Sat 7–9 am. Vitiligo, psoriasis, "
            "eczema, acne and hair loss. Book on Practo.",
    "eyebrow": "Locations",
    "h1": "Dermatologist in West Marredpally",
    "lede": "Early morning consultations in Secunderabad — 7 to 9 am, Monday to Saturday. "
            "Medical dermatology, chronic condition reviews and second opinions, before "
            "the working day starts.",
    "acts": [("Book this clinic", PRACTO_WM), ("Call the clinic", PHONE)],
    "glance": [
        ("Hours", "Mon–Sat, 7:00 – 9:00 am"),
        ("Closed", "Sunday"),
        ("Best for", "Medical dermatology, reviews, second opinions"),
        ("Serves", "West Marredpally, Secunderabad, Trimulgherry, Bowenpally, Alwal"),
        ("Booking", "Practo — no walk-in queue"),
        ("Address", "TODO — to be supplied by the clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What runs here",
         "h2": "A consulting hour that fits around work.",
         "body": [
             "The West Marredpally clinic exists for a specific problem: chronic skin "
             "disease needs regular review, and regular review is exactly what people stop "
             "doing when the only appointment available is at 6 pm on a working day.",
             "Seven to nine in the morning solves that. It is the clinic where psoriasis, "
             "eczema, vitiligo and long-running hair problems are followed month to month, "
             "and where most second opinions are heard.",
             "Procedures and aesthetic work are done at Jubilee Hills, where the equipment "
             "is. If something you need has to be done there, it is booked for you rather "
             "than left to you to arrange.",
         ]},

        {"kind": "cards", "eyebrow": "Available here", "h2": "What you can book",
         "items": [
             {"eyebrow": "First visits", "title": "New consultations", "list": [
                 "Diagnosis of an undiagnosed rash",
                 "Vitiligo and psoriasis assessment",
                 "Hair loss assessment", "Second opinions"]},
             {"eyebrow": "Ongoing", "title": "Chronic reviews", "list": [
                 "Psoriasis flare management", "Eczema control reviews",
                 "Repigmentation progress checks", "Prescription reviews"]},
             {"eyebrow": "Referred on", "title": "Booked at Jubilee Hills", "list": [
                 "Phototherapy and excimer", "Dermatosurgery and grafting",
                 "Peels, laser and aesthetics"]},
         ]},

        {"kind": "callout", "title": "Coming from Secunderabad, Trimulgherry or Alwal?",
         "body": "West Marredpally is the nearer clinic for the northern corridor. Both "
                 "clinics share one set of records, so a review here can follow a procedure "
                 "done at Jubilee Hills without repeating your history."},

        {"kind": "checklist", "eyebrow": "Bring with you",
         "h2": "What makes a morning appointment count.",
         "items": [
             "<b>Previous prescriptions</b> — including what didn't work",
             "<b>Photographs</b> of the condition at its worst",
             "<b>Reports</b> — biopsy, blood work, thyroid panels",
             "<b>A list</b> of every cream and supplement currently in use",
             "<b>Dates</b> — when it started, when it flares",
             "<b>Questions</b>, written down, because mornings are brisk",
         ]},
    ],
    "faq_h2": "Visiting West Marredpally",
    "faqs": [
        ("What are the West Marredpally clinic hours?",
         "Monday to Saturday, 7:00 am to 9:00 am. The clinic is closed on Sundays. "
         "For afternoon or evening appointments, book Jubilee Hills."),
        ("Are procedures done at this clinic?",
         "No. Phototherapy, laser, peels, aesthetic treatments and surgery are done at "
         "Jubilee Hills where the equipment is. If you need one, it is booked for you at "
         "the time of consultation."),
        ("Is this clinic good for a second opinion?",
         "Yes — it is where most second opinions are heard. Bring the previous diagnosis, "
         "the prescriptions, and any reports. A second opinion without the first opinion's "
         "paperwork is guesswork."),
        ("Is it the same doctor at both clinics?",
         "Yes. Dr. Varada consults at both. It is one practice with two locations, sharing "
         "one set of patient records."),
        ("How early should I arrive?",
         "The two-hour window is tight. Arrive at the booked time rather than early — the "
         "team works strictly to the Practo schedule so the last slot is not squeezed."),
    ],
    "related": [
        ("locations-jubilee-hills", "Jubilee Hills clinic",
         "Afternoons and evenings — the full clinic, including procedures."),
        ("psoriasis-treatment-hyderabad", "Psoriasis in Hyderabad",
         "The condition most often reviewed in the morning clinic."),
        ("contact", "Contact and directions",
         "Both clinics, hours, and how to reach the team."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "contact", "template": "T3",
    "crumbs": [("Contact", None)],
    "title": "Contact & Book — Dr. Varada's Skin & Hair Center, Hyderabad",
    "meta": "Book an appointment at Dr. Varada's Skin & Hair Center. Two clinics in "
            "Hyderabad — Jubilee Hills (Mon–Sat 1:30–8 pm) and West Marredpally "
            "(Mon–Sat 7–9 am). Book on Practo, WhatsApp photos, or call.",
    "eyebrow": "Contact",
    "h1": "Book, ask, or send photographs.",
    "lede": "Every appointment is booked through Practo — that is where the clinic team "
            "works, so a slot taken there is a slot that exists. WhatsApp and phone are for "
            "questions, not for holding a time.",
    "acts": [("Book on Practo", PRACTO), ("WhatsApp your photos", WHATSAPP)],
    "glance": [
        ("Jubilee Hills", "Mon–Sat, 1:30 – 8:00 pm"),
        ("West Marredpally", "Mon–Sat, 7:00 – 9:00 am"),
        ("Sunday", "Both clinics closed"),
        ("Booking", "Practo"),
        ("Phone", "TODO — clinic number"),
        ("WhatsApp", "TODO — clinic number"),
    ],
    "sections": [
        {"kind": "cards", "eyebrow": "Three ways in", "h2": "Which one you want",
         "items": [
             {"eyebrow": "Primary", "title": "Book on Practo",
              "body": "Choose the clinic, choose the time, done. The team's diary is "
                      "Practo, so nothing is double-booked and nothing is lost.",
              "list": ["Both clinics", "Online video consultation",
                       "Reschedules handled in-app"]},
             {"eyebrow": "Before you travel", "title": "WhatsApp your photographs",
              "body": "Useful if you are coming from outside Hyderabad and need to know "
                      "whether a procedure is even appropriate before booking travel.",
              "list": ["Photographs in daylight", "A one-line history",
                       "Staff reply with a Practo link"]},
             {"eyebrow": "Questions only", "title": "Call the clinic",
              "body": "For directions, timing, or what to bring. Appointments are not "
                      "held over the phone — they are taken on Practo.",
              "list": ["Clinic hours only", "No prescriptions by phone"]},
         ]},

        {"kind": "cards", "eyebrow": "Locations", "h2": "Two clinics in Hyderabad",
         "items": [
             {"title": "Jubilee Hills",
              "body": "The full clinic — dermatology, trichology, aesthetics and the "
                      "procedure lists. Mon–Sat, 1:30 – 8:00 pm.",
              "list": ["Address: TODO", "Phone: TODO",
                       "Serves Banjara Hills, Madhapur, Gachibowli"]},
             {"title": "West Marredpally",
              "body": "Early morning medical dermatology and chronic condition reviews. "
                      "Mon–Sat, 7:00 – 9:00 am.",
              "list": ["Address: TODO", "Phone: TODO",
                       "Serves Secunderabad, Trimulgherry, Alwal"]},
         ]},

        {"kind": "callout", "warn": True, "title": "This is not an emergency service",
         "body": "For a rapidly spreading rash with fever, blistering across large areas, "
                 "or swelling of the lips or tongue, go to a hospital emergency department. "
                 "Do not wait for a clinic appointment."},

        {"kind": "checklist", "eyebrow": "Travelling to Hyderabad",
         "h2": "Coming from outside the city.",
         "items": [
             "<b>Send photographs first</b> — before booking travel",
             "<b>Say what you've tried</b>, with dates",
             "<b>Ask specifically</b> whether the procedure suits your case",
             "<b>Expect a staged visit</b> — assessment, then procedure",
             "<b>Allow for review</b> — grafting needs follow-up",
             "<b>Consider a video consult</b> for the first opinion",
         ]},
    ],
    "faq_h2": "Getting an appointment",
    "faqs": [
        ("How do I book an appointment?",
         "Through Practo. Pick the clinic and the time. The clinic team runs its diary on "
         "Practo, so that is the only place a slot can be genuinely reserved."),
        ("Why is there no booking form on this website?",
         "Because a second queue would break the clinic's workflow. One diary, one source "
         "of truth, no double-bookings — that is a deliberate decision, not an oversight."),
        ("Can I get a prescription without being seen?",
         "No. Repeat prescriptions for an existing plan can be reviewed at a consultation, "
         "including a video consultation, but nothing is prescribed without an examination."),
        ("Do you offer online consultations?",
         "Yes, through Practo video consultation. It suits second opinions, chronic "
         "condition reviews and patients outside Hyderabad."),
        ("What if I need to cancel?",
         "Cancel or reschedule in the Practo app. Doing it there frees the slot immediately "
         "for someone else."),
    ],
    "related": [
        ("locations-jubilee-hills", "Jubilee Hills clinic", "Hours, services and what runs there."),
        ("locations-west-marredpally", "West Marredpally clinic", "Early morning consultations in Secunderabad."),
        ("vitiligo-online-consultation", "Consult online from anywhere in India",
         "How a video consultation for vitiligo actually works."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "results", "template": "T3",
    "crumbs": [("Results", None)],
    "title": "Treatment Results — What Change Looks Like | Dr. Varada's",
    "meta": "How treatment progress is measured and photographed at Dr. Varada's Skin & "
            "Hair Center — vitiligo repigmentation, psoriasis control, acne and hair. "
            "Consent-documented images only.",
    "eyebrow": "Results",
    "h1": "What change actually looks like.",
    "lede": "Every image on this page is a real patient who signed a consent form for it to "
            "be published. Where no consented image exists, there is no image — a placeholder "
            "is more honest than a stock photograph.",
    "acts": [("Book a consultation", PRACTO), ("Read patient stories", "patient-stories")],
    "glance": [
        ("Images", "Consent-documented only"),
        ("Photography", "Standardised lighting and distance"),
        ("Vitiligo", "Repigmentation measured by area and site"),
        ("Psoriasis", "Measured by involved area and symptoms"),
        ("Interval", "Reviewed every 6–8 weeks"),
        ("Guarantee", "None — results vary by person"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The rule", "h2": "Consent first, image second.",
         "body": [
             "Before-and-after photographs are the most persuasive thing a dermatology "
             "practice can publish, and the easiest thing to misuse. Indian Medical Council "
             "advertising rules are strict about it, and rightly so.",
             "The rule here is simple and absolute: an image appears on this site only if "
             "the patient signed a written consent for that specific use. Not a general "
             "clinical consent — a publication consent. Withdrawal is honoured immediately, "
             "no reason required.",
             "That means this page fills in slowly. It also means everything on it is real.",
         ]},

        {"kind": "ba", "eyebrow": "Documented in clinic",
         "h2": "Progress, photographed at fixed intervals",
         "intro": "Placeholders until each consented series is supplied — a placeholder "
                  "is more honest than a stock photograph.",
         "items": [
             ("Vitiligo — repigmentation", "Excimer phototherapy · duration on file"),
             ("Plaque psoriasis — clearance", "Topical and phototherapy protocol"),
             ("Acne — active lesion control", "Medical protocol and peels"),
         ]},

        {"kind": "cards", "eyebrow": "How progress is measured",
         "h2": "What is being tracked, condition by condition",
         "items": [
             {"eyebrow": "Chronic", "title": "Vitiligo",
              "body": "Repigmentation is scored by the proportion of the patch that has "
                      "recoloured and where it started from — perifollicular islands, or "
                      "inward from the edge.",
              "list": ["Patch area and site", "Whether spread has stopped",
                       "Colour match at the margin"]},
             {"eyebrow": "Chronic", "title": "Psoriasis",
              "body": "Measured by how much body surface is involved and how much it is "
                      "affecting sleep, work and itch — not by photographs alone.",
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
                  "photographs are taken for the clinical record whether or not they are "
                  "ever published — and they are only ever published with consent."],
         "cta": ("Book a first consultation", PRACTO),
         "items": [
             {"title": "Photographed at baseline",
              "body": "Same distance, same light, same angle — so the comparison means "
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
    "meta": "What patients have written about Dr. (Lt Col) Khagendra Varada — reproduced "
            "from verified Practo reviews, unedited. 5.0 rating across 65 patient stories.",
    "eyebrow": "In their words",
    "h1": "What patients wrote themselves.",
    "lede": "These come from verified Practo reviews — written by people who booked and "
            "attended, and published on a platform the clinic does not control. Nothing "
            "here is solicited copy.",
    "acts": [("Read them on Practo", PRACTO), ("Book a consultation", PRACTO)],
    "glance": [
        ("Source", "Practo verified reviews"),
        ("Rating", "5.0"),
        ("Stories", "65"),
        ("Edited", "No — reproduced as written"),
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
             "Practo profile and refreshed automatically rather than typed in by hand — "
             "which means the number here is the number there, including on the days it "
             "goes down.",
             "Individual stories are reproduced without editing for tone or length. Where a "
             "story names a condition or an outcome, it is that patient's experience and "
             "not a claim about what treatment does generally.",
         ]},

        {"kind": "quotes", "eyebrow": "From Practo", "h2": "The stories themselves",
         "intro": "Three recent stories, reproduced as written. The full set lives on "
                  "Practo, where the clinic cannot edit it.",
         "items": [
             ("I consulted him online for my relative's skin problems. Many doctors "
              "couldn't help before, but he listened carefully and gave a friendly, "
              "effective consultation.", "Verified patient · online consultation"),
             ("He communicates all points of the treatment and welcomes feedback for "
              "the follow-up. He delivers good service to patients.",
              "Verified patient · Practo"),
             ("The appointment was timely. He was nice and explained things well. The "
              "treatment was effective, and overall I am satisfied.",
              "Verified patient · Practo"),
         ]},

        {"kind": "callout", "title": "Why reviews are asked for, but never bought",
         "body": "Patients are asked once, at reception, with a card. There is no discount, "
                 "no free session and no follow-up chasing. A review that had to be paid "
                 "for tells you nothing about the medicine."},

        {"kind": "checklist", "eyebrow": "Reading reviews well",
         "h2": "What is actually worth reading in them.",
         "items": [
             "<b>Whether the condition matches yours</b> — vitiligo reviews say little about acne",
             "<b>How long they'd been treated</b> — a first visit rates the manner, not the result",
             "<b>What they say about being told no</b>",
             "<b>Whether costs were explained upfront</b>",
             "<b>The negative ones</b>, and how they were answered",
             "<b>The dates</b> — a practice can change",
         ]},
    ],
    "faq_h2": "About these reviews",
    "faqs": [
        ("Are these reviews verified?",
         "They are Practo reviews, which are tied to a booking made through Practo. The "
         "clinic cannot add, edit or delete them."),
        ("Does the clinic offer anything in return for a review?",
         "No. Patients are asked once, at reception. There is no incentive, and offering one "
         "would make the reviews worthless."),
        ("Why not publish testimonials directly on the site?",
         "Because a testimonial the clinic selects is a marketing asset, not evidence. "
         "Reviews on a third-party platform are harder to curate and therefore worth more."),
        ("Can I leave a review after an online consultation?",
         "Yes. Video consultations booked through Practo can be reviewed in the same way as "
         "an in-person visit."),
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
    "title": "Skin & Hair Journal — Dermatology Notes | Dr. Varada's",
    "meta": "Plain-language notes on skin and hair from Dr. Varada's Skin & Hair Center, "
            "Hyderabad — what conditions actually are, what treatments do, and which "
            "internet advice to ignore.",
    "eyebrow": "Journal",
    "h1": "Notes on skin and hair.",
    "lede": "Short, plain pieces on what patients ask in the consulting room — written to "
            "be read by the person with the condition, not by another dermatologist.",
    "acts": [("Book a consultation", PRACTO), ("Browse conditions", "vitiligo")],
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
             "A consultation has fifteen minutes in it. Some questions need more than that "
             "— why a diet change did nothing for the vitiligo, why the psoriasis came back "
             "in December, why the hair fall got worse three months after the fever.",
             "Those answers go here, at the length they actually need, and each one links "
             "back to the condition page it belongs to.",
             "Every piece carries a review date. Dermatology moves — JAK inhibitors in "
             "vitiligo were not a real option a decade ago — and an undated medical article "
             "is a liability.",
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
         "body": "[ Post grid — populated once the editorial calendar starts. Two pieces a "
                 "week, each linking up to its condition page. ]"},

        {"kind": "callout", "title": "General information, not your diagnosis",
         "body": "Everything written here is general. It cannot account for your history, "
                 "your medication or what your skin actually looks like — and it is not a "
                 "substitute for being examined."},
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
         "Yes — the questions asked most often in clinic are where most of these come from. "
         "Send a suggestion by WhatsApp."),
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
