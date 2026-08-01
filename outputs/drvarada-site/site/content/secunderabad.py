"""Secunderabad local pages — the twin city the clinic is actually in.

WHY THESE ARE NOT COPIES OF THE HYDERABAD PAGES
  Sixteen `*-treatment-hyderabad` pages already answer "can this clinic treat my
  problem". Cloning them with the city swapped would be a doorway set: same
  intent, same answer, two URLs competing for one another. Google has treated
  that as spam for a decade, and it is also just dishonest.

  The Secunderabad intent is genuinely different, and the difference is
  logistics. Narrowband UVB runs two to three sessions a week for four to eight
  months. Excimer runs twice a week. Grafting needs review visits. A course that
  needs sixty trips is decided by how far the clinic is, not by how good it is —
  and a patient in Trimulgherry choosing a clinic in Gachibowli will stop coming
  in month two. So these pages are about distance, timing and adherence, which
  is what someone typing "vitiligo treatment Secunderabad" is actually weighing.

  `areas-we-serve` then covers the whole twin-city footprint without minting a
  page per colony.
"""

from chrome import ADDRESS, HOURS, MAPS, PHONE, PHONE_SHOW, WHATSAPP

# The clinic sits in Karkhana. These are the localities within a realistic
# repeat-visit radius, which is the only thing that matters for a course of
# phototherapy — and the reason this list is not simply "Hyderabad".
NEAR = [
    ("Karkhana", "the clinic's own locality"),
    ("Vikrampuri Colony", "walking distance"),
    ("Trimulgherry", "about 2 km"),
    ("West &amp; East Marredpally", "about 3 km"),
    ("Bowenpally", "about 4 km"),
    ("Bolarum", "about 5 km"),
    ("Alwal", "about 6 km"),
    ("Tarnaka", "about 7 km"),
    ("Begumpet", "about 7 km"),
    ("Malkajgiri", "about 8 km"),
    ("Kompally", "about 9 km"),
    ("Sainikpuri &amp; A.S. Rao Nagar", "about 10 km"),
]

CRED = ["45 years in dermatology", "Dermatologist &amp; dermatosurgeon",
        "Karkhana, Secunderabad", "Booking on WhatsApp"]

# One shared band. The argument is the same whichever condition brought you
# here, and repeating it three times in three voices would be worse writing.
COURSE = {
    "kind": "split", "eyebrow": "Why the address matters",
    "h2": "A light course is decided by the traffic, not the technology.",
    "body": ["Narrowband UVB is two to three sessions a week. Excimer is usually "
             "twice a week. Both run for months, not weeks. That means somewhere "
             "between forty and eighty separate trips before the course is "
             "finished, and the single commonest reason a course is abandoned "
             "is not that it stopped working. It is that the journey stopped "
             "being possible.",
             "Which is why this page leads with the address rather than the "
             "equipment. If you live on the Secunderabad side, a clinic in "
             "Karkhana is a fifteen-minute problem. The same course booked "
             "across the city is a ninety-minute problem twice a week, and the "
             "difference between those two numbers decides how much of your "
             "skin repigments."],
    "cta": ("Every locality, and how far", "areas-we-serve"),
    "items": [
        {"title": "Short trips get finished",
         "body": "Adherence is the variable a patient controls most and hears "
                 "about least. Distance is most of it."},
        {"title": "Sessions fit around a working day",
         "body": "Consulting runs " + HOURS.lower() + ", so a session slots into "
                 "a lunch break rather than costing an afternoon."},
    ],
}

VISIT = {
    "kind": "cards", "eyebrow": "Finding the clinic",
    "h2": "Karkhana, Secunderabad",
    "intro": "One consulting location, formerly BNR Skin &amp; Vitiligo Hospital. "
             "The practice has held this address for years.",
    "items": [
        {"title": "Where", "icon": "pin",
         "body": ADDRESS + ".",
         "list": ["Off Wellington Road, Vikrampuri Colony",
                  "Listed on Google as BNR Skin &amp; Vitiligo Hospital",
                  "Consulting " + HOURS.lower() + ", closed Sunday"]},
        {"title": "How to book", "icon": "chat",
         "body": "On WhatsApp: one number, answered by the clinic team, who "
                 "confirm a time and say what to bring.",
         "list": ["WhatsApp " + PHONE_SHOW,
                  "Photographs welcome before your first visit",
                  "Video consultation if you are out of the city"]},
    ],
}


def _areas_rows():
    return [[name, note, "Yes"] for name, note in NEAR]


PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-treatment-secunderabad", "template": "T1",
    "condition": "Vitiligo",
    "crumbs": [("Vitiligo treatment in Secunderabad", None)],
    "title": "Vitiligo Treatment in Secunderabad | Dr. Varada",
    "meta": "Vitiligo treatment in Secunderabad: narrowband UVB, excimer laser and melanocyte "
            "graft surgery in Karkhana, near Trimulgherry, Marredpally and Alwal.",
    "eyebrow": "Secunderabad",
    "h1": "Vitiligo treatment in Secunderabad",
    "lede": "Phototherapy for vitiligo is a course, not an appointment. Two or three sessions a "
            "week for months. This clinic is in Karkhana, which for most of Secunderabad makes "
            "that course something you can actually finish.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["niams-vitiligo", "aad-vitiligo-tx", "dermnet-vitiligo", "nhs-vitiligo"],
    "glance": [
        ("Where", "Karkhana, Secunderabad"),
        ("Available here", "Topicals, NB-UVB, excimer, graft surgery"),
        ("Course length", "Months: reviewed every 6–8 weeks"),
        ("Session frequency", "Light therapy 2–3 times a week"),
        ("Surgery", "For disease stable about 12 months"),
        ("Curable", "No, but repigmentation is often substantial"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Start here",
         "h2": "What the first visit settles.",
         "body": [
             "Vitiligo is treated in two halves, and which half you are in decides everything "
             "that follows. Active disease (new patches, existing ones spreading), is quietened "
             "first. Repigmenting skin while fresh patches keep appearing is effort spent "
             "against a moving target.",
             "Stable disease is the one that responds to light. Narrowband UVB for "
             "widespread patches, excimer where there are only a few, usually alongside a "
             "topical. You are told at the first visit which category you are in, roughly "
             "how long a fair trial takes, and which of your patches are unlikely to "
             "respond to light at all.",
             "That last part matters more than it sounds. Patches on the lips, the "
             "fingertips, and any patch whose hairs have gone white have lost the pigment "
             "reservoir that light works by recruiting. Being told so at the start is more "
             "useful than six months of finding out.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "How a course actually runs",
         "items": [
             {"title": "Assess activity",
              "body": "Wood's lamp, patch margins, a history of new patches, and baseline "
                      "photographs. Active or stable decides the whole plan."},
             {"title": "Stop the spread",
              "body": "Topicals, occasionally a short oral course. This comes before any "
                      "attempt at repigmentation."},
             {"title": "Repigment with light",
              "body": "NB-UVB two to three times a week, or excimer twice a week for a few "
                      "patches. Reviewed at six to eight weeks with photographs."},
             {"title": "Operate if it stays quiet",
              "body": "Patches that will not answer light, on disease settled for about "
                      "twelve months, are assessed for melanocyte transplant or punch "
                      "grafting."},
         ]},

        COURSE,

        {"kind": "table", "eyebrow": "Coming from", "h2": "Getting here for a course",
         "head": ["Locality", "Distance", "Practical for 2–3 visits a week"],
         "rows": _areas_rows(),
         "note": "Distances are approximate road distances to Karkhana. If you are further out "
                 "(Kukatpally, Gachibowli, LB Nagar), phototherapy two or three times a week is "
                 "worth thinking about honestly before you commit to it, and a unit closer to "
                 "home may serve you better even if you are assessed here."},

        {"kind": "callout", "title": "Travelling in for surgery rather than a course?",
         "body": "Grafting is a different proposition from phototherapy. A staged visit rather "
                 "than a standing weekly commitment, which is why patients come for it from "
                 "outside Telangana. Send photographs on WhatsApp before booking travel so you "
                 "know whether your disease is settled enough to operate on."},

        VISIT,
    ],
    "faq_h2": "Vitiligo treatment in Secunderabad",
    "faqs": [
        ("Where exactly is the clinic in Secunderabad?",
         "Plot No D13B, Wellington Rd, Vikrampuri Colony, Karkhana, Secunderabad 500009. The "
         "practice formerly known as BNR Skin & Vitiligo Hospital. Consulting is Monday to "
         "Saturday, 11:30 am to 5:00 pm."),
        ("Is phototherapy done at this clinic or referred elsewhere?",
         "Here. Narrowband UVB and excimer are on site, along with the consultation and the "
         "surgical list, so a course does not mean travelling between places."),
        ("How often would I have to come?",
         "Narrowband UVB is typically two to three sessions a week; excimer is usually "
         "twice a week. Courses run for months, with a review every six to eight weeks."),
        ("I live in Trimulgherry / Marredpally / Alwal. Is that close enough?",
         "Yes: all three are within about six kilometres, which is the range where twice- or "
         "thrice-weekly sessions stay realistic. That is the practical test, and it matters "
         "more than most people expect."),
        ("Can vitiligo be cured?",
         "No. No treatment anywhere cures vitiligo. What treatment does reliably do is stop the "
         "spread in active disease and repigment a meaningful proportion of affected skin in "
         "many patients: best on the face and trunk, least on hands, feet and lips."),
        ("Do you see patients from the Hyderabad side as well?",
         "Yes. The clinical work is identical wherever you travel from; the only thing that "
         "changes is whether a twice-weekly course is practical for you. That is discussed "
         "honestly at the first visit."),
    ],
    "related": [
        ("vitiligo-treatment-hyderabad", "Vitiligo treatment in Hyderabad",
         "The same clinic, written for patients travelling from the Hyderabad side."),
        ("vitiligo", "The full vitiligo section",
         "What the disease is, every treatment explained, and what each costs."),
        ("areas-we-serve", "Areas we serve",
         "Every locality across Secunderabad and Hyderabad, with distances."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-treatment-secunderabad", "template": "T1",
    "condition": "Psoriasis",
    "crumbs": [("Psoriasis treatment in Secunderabad", None)],
    "title": "Psoriasis Treatment in Secunderabad | Dr. Varada",
    "meta": "Psoriasis treatment in Secunderabad: topicals, narrowband UVB, methotrexate and "
            "biologics with joint screening, in Karkhana near Trimulgherry.",
    "eyebrow": "Secunderabad",
    "h1": "Psoriasis treatment in Secunderabad",
    "lede": "Psoriasis is managed over years, which makes the review appointment the one that "
            "decides the outcome, and a review you can reach in fifteen minutes is a review you "
            "keep.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["niams-psoriasis", "aad-psoriasis", "dermnet-psoriasis", "nice-psoriasis"],
    "glance": [
        ("Where", "Karkhana, Secunderabad"),
        ("Available here", "Topicals, NB-UVB, systemics, biologics"),
        ("Screened for", "Psoriatic arthritis, metabolic risk"),
        ("Flare plan", "Written, at the first visit"),
        ("Review", "Every 6–8 weeks while active"),
        ("Curable", "No, but often well controlled"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The approach",
         "h2": "Clearing a flare is easy. Month four is the job.",
         "body": [
             "Almost any potent steroid will flatten a plaque. What separates good psoriasis "
             "care from the other kind is what happens once it has: whether there was a "
             "step-down plan, or whether treatment was simply stopped and the disease "
             "rebounded, sometimes worse than it began.",
             "So a first consultation here produces three things: what clears the current "
             "flare, what holds it afterwards, and a written plan for what to start at the "
             "first sign of the next one. Patients who leave with that third thing flare less, "
             "because they act in week one rather than week six.",
             "It also produces a joint assessment. Up to a third of people with psoriasis "
             "develop psoriatic arthritis, the damage it causes does not reverse, and the "
             "early symptoms are routinely dismissed as unrelated aches.",
         ]},

        {"kind": "checklist", "eyebrow": "Bring with you",
         "h2": "What makes a first psoriasis visit count.",
         "items": [
             "<b>Every prescription</b> you have used, including what stopped working",
             "<b>Photographs</b> of the skin at its worst, not on a good day",
             "<b>Blood results</b>: liver, lipids, sugar, if you have them",
             "<b>A note of your joints</b>: stiffness, swelling, heel or back pain",
             "<b>Dates</b>, when it started, what triggers a flare",
             "<b>Your questions</b>, written down",
         ]},

        COURSE,

        {"kind": "table", "eyebrow": "Coming from", "h2": "Getting here for reviews",
         "head": ["Locality", "Distance", "Practical for 2–3 visits a week"],
         "rows": _areas_rows(),
         "note": "Psoriasis reviews are usually every six to eight weeks rather than weekly, so "
                 "distance matters less than it does for vitiligo, until phototherapy enters "
                 "the plan, at which point it matters just as much."},

        {"kind": "callout", "title": "Second opinions are welcome",
         "body": "Bring the previous diagnosis, every prescription and any blood results. The "
                 "commonest finding in a psoriasis second opinion is not a wrong diagnosis. It "
                 "is a potent steroid that has been running for months with no maintenance plan "
                 "and no review date."},

        VISIT,
    ],
    "faq_h2": "Psoriasis treatment in Secunderabad",
    "faqs": [
        ("Where is the clinic?",
         "Plot No D13B, Wellington Rd, Vikrampuri Colony, Karkhana, Secunderabad 500009. "
         "Formerly BNR Skin & Vitiligo Hospital. Monday to Saturday, 11:30 am to 5:00 pm."),
        ("Is phototherapy available in Secunderabad?",
         "Yes, narrowband UVB on site. A course typically runs 20 to 36 sessions at two to "
         "three a week, so it is worth checking the timings suit you before starting."),
        ("Can psoriasis be cured?",
         "No. It is a long-term immune condition. Treatment aims at remission: skin that is "
         "clear or nearly clear, held there with maintenance, sometimes for years."),
        ("I have joint pain along with psoriasis. Is that related?",
         "It may well be. Up to a third of people with psoriasis develop psoriatic arthritis, "
         "and catching it early matters because joint damage does not reverse. Raise it at your "
         "appointment. It will be asked about anyway."),
        ("Do you prescribe biologics?",
         "Yes, where conventional systemics have failed or are unsuitable, and after TB and "
         "hepatitis screening. They are not a first step and are not offered as one."),
        ("How do I book?",
         "On WhatsApp at " + PHONE_SHOW + ". Say what you are seeing, send a photograph if "
         "you have one, and the clinic team come back with a time."),
    ],
    "related": [
        ("psoriasis-treatment-hyderabad", "Psoriasis treatment in Hyderabad",
         "The same clinic, written for patients travelling from the Hyderabad side."),
        ("psoriasis", "The full psoriasis section",
         "Types, triggers, phototherapy, systemics and what each costs."),
        ("areas-we-serve", "Areas we serve",
         "Every locality across Secunderabad and Hyderabad, with distances."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "hair-loss-treatment-secunderabad", "template": "T1",
    "crumbs": [("Hair loss treatment in Secunderabad", None)],
    "title": "Hair Loss Treatment in Secunderabad | Dr. Varada",
    "meta": "Hair loss treatment in Secunderabad: diagnosis first, with thyroid, iron and "
            "hormone workup, in Karkhana near Trimulgherry, Marredpally and Alwal.",
    "eyebrow": "Secunderabad",
    "h1": "Hair loss treatment in Secunderabad",
    "lede": "Hair falls for reasons: thyroid, iron, hormones, a fever three months ago, "
            "genetics. Find the reason and the treatment is obvious. Skip that step and you are "
            "buying a package and hoping.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["aad-hair-loss", "dermnet-mphl", "dermnet-fphl", "nhs-hair-loss"],
    "glance": [
        ("Where", "Karkhana, Secunderabad"),
        ("First visit", "Diagnosis and bloods, not a package"),
        ("Tested for", "Thyroid, ferritin, vitamin D, B12"),
        ("Available here", "Medical therapy, grafting surgery"),
        ("First review", "8–12 weeks: hair is slow"),
        ("Not offered", "Course packages sold before a diagnosis"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Why the workup",
         "h2": "Four conditions, one symptom.",
         "body": [
             "Most people arriving with hair fall have one of four things, and they need "
             "opposite treatments. Telogen effluvium: a shed following a fever, a surgery, a "
             "crash diet or childbirth. Resolves on its own once the cause is corrected. "
             "Pattern hair loss is progressive and needs long-term therapy. Alopecia areata is "
             "autoimmune and patchy. Scarring alopecias destroy the follicle and are the one "
             "group where delay costs you permanently.",
             "Telling them apart is a consultation, a scalp examination and, usually, a small "
             "blood panel: thyroid, ferritin, vitamin D and B12. Iron deficiency in particular "
             "is common, easy to correct and routinely missed.",
             "It is also the reason nothing is quoted before you are examined. What a plan "
             "costs depends on what the diagnosis turns out to be.",
         ]},

        {"kind": "cards", "eyebrow": "What it might be", "h2": "The four common patterns",
         "items": [
             {"eyebrow": "Reversible", "title": "Telogen effluvium", "list": [
                 "Sudden, diffuse shed", "Follows illness, surgery, childbirth",
                 "Usually 3 months after the trigger", "Corrects with the cause"]},
             {"eyebrow": "Progressive", "title": "Pattern hair loss", "list": [
                 "Gradual thinning at crown or hairline",
                 "Family history common", "Long-term medical therapy",
                 "Grafting where medical therapy plateaus"]},
             {"eyebrow": "Autoimmune", "title": "Alopecia areata", "list": [
                 "Round, well-defined bald patches",
                 "Can regrow spontaneously", "Sometimes needs systemic therapy",
                 "Nail pitting is a clue"]},
         ]},

        COURSE,

        {"kind": "table", "eyebrow": "Coming from", "h2": "Getting here for follow-up",
         "head": ["Locality", "Distance", "Practical for 2–3 visits a week"],
         "rows": _areas_rows(),
         "note": "Hair follow-up is every eight to twelve weeks rather than weekly, so a "
                 "longer journey is workable. The distances matter most if your plan turns "
                 "out to include phototherapy or a graft with staged reviews."},

        {"kind": "callout", "warn": True,
         "title": "Hair loss with scaling, redness or pain needs looking at sooner",
         "body": "A scalp that is itchy, tender, scaly or reddened alongside the shedding "
                 "may be a scarring alopecia. Those destroy the follicle, and what is lost "
                 "does not come back. It is the one presentation worth bringing forward "
                 "rather than watching for another few months."},

        VISIT,
    ],
    "faq_h2": "Hair loss treatment in Secunderabad",
    "faqs": [
        ("What happens at the first appointment?",
         "A history, a scalp and hair-pull examination, dermatoscopy where useful, and usually "
         "a blood panel: thyroid, ferritin, vitamin D and B12. A plan and its cost follow the "
         "diagnosis, not the other way round."),
        ("Do you sell hair treatment packages?",
         "No. Packages are sold before anyone knows what is wrong, which is why they so "
         "often treat the wrong thing. You are quoted after the examination."),
        ("How long before I see a change?",
         "Hair is slow. The first honest review is at eight to twelve weeks, and meaningful "
         "change usually takes longer. Anything promising a visible difference in a month "
         "is promising something it cannot deliver."),
        ("Is hair grafting done here?",
         "Yes, by the dermatosurgeon rather than a technician, and only where medical therapy "
         "has been given a fair trial first and the loss has stabilised."),
        ("Where is the clinic?",
         "Plot No D13B, Wellington Rd, Vikrampuri Colony, Karkhana, Secunderabad 500009, "
         "formerly BNR Skin & Vitiligo Hospital. Monday to Saturday, 11:30 am to 5:00 pm."),
    ],
    "related": [
        ("hair-loss-treatment-hyderabad", "Hair loss treatment in Hyderabad",
         "The same clinic, written for patients travelling from the Hyderabad side."),
        ("alopecia-areata-treatment-india", "Alopecia areata, totalis and universalis",
         "The autoimmune pattern, and what treatment can and cannot do."),
        ("hair-grafting-hyderabad", "Hair grafting surgery",
         "When a graft is appropriate, and when medical therapy still has room."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "areas-we-serve", "template": "T3",
    "crumbs": [("Areas we serve", None)],
    "title": "Areas We Serve: Secunderabad & Hyderabad | Dr. Varada's",
    "meta": "Where patients travel from to our clinic in Karkhana, Secunderabad. Trimulgherry, "
            "Marredpally, Bowenpally, Alwal, Tarnaka, Begumpet and Hyderabad.",
    "eyebrow": "Visiting",
    "h1": "Where patients travel from.",
    "lede": "One clinic, in Karkhana, Secunderabad. This page is the honest version of “do we "
            "serve your area”, which is really a question about how far you would have to come "
            "and how often.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Get directions", MAPS)],
    "glance": [
        ("The clinic", "Karkhana, Secunderabad"),
        ("Hours", HOURS),
        ("Closed", "Sunday"),
        ("Nearest localities", "Vikrampuri, Trimulgherry, Marredpally"),
        ("Across the city", "Seen routinely: see the note on courses"),
        ("Outside Hyderabad", "Video consultation, then a staged visit"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The honest answer",
         "h2": "Everyone is welcome. Not every plan travels equally well.",
         "body": [
             "A consultation, a second opinion, a diagnosis, a review every eight weeks. None "
             "of those care where you live. Patients come to this clinic from across Hyderabad "
             "and Secunderabad and from outside Telangana entirely, and the clinical work is "
             "identical whoever walks in.",
             "What does depend on distance is a course. Narrowband UVB and excimer are "
             "two to three sessions a week for months. So is any plan where the review "
             "schedule is weekly rather than seasonal. Those are decided by the journey, "
             "and pretending otherwise sets a patient up to stop in month two and conclude "
             "the treatment failed.",
             "So the tables below are distances, not marketing. If you are far out and the "
             "plan needs frequent sessions, you will be told so, and told what your "
             "alternatives are.",
         ]},

        {"kind": "table", "eyebrow": "Secunderabad side",
         "h2": "Within a short run of the clinic",
         "head": ["Locality", "Distance", "Practical for 2–3 visits a week"],
         "rows": _areas_rows(),
         "note": "Approximate road distances to Karkhana. Anything in this table makes a "
                 "twice- or thrice-weekly course realistic for most people."},

        {"kind": "table", "eyebrow": "Hyderabad side",
         "h2": "Across the city",
         "head": ["Area", "Roughly", "Practical for 2–3 visits a week"],
         "rows": [
             ["Secunderabad Cantonment, Sainikpuri", "8–10 km", "Yes"],
             ["Tarnaka, Habsiguda, Uppal", "7–12 km", "Usually"],
             ["Begumpet, Somajiguda, Punjagutta", "7–12 km", "Usually"],
             ["Ameerpet, S.R. Nagar, Erragadda", "10–14 km", "Consider carefully"],
             ["Banjara Hills, Jubilee Hills", "12–16 km", "Consider carefully"],
             ["Kukatpally, Miyapur, Nizampet", "15–22 km", "A consultation, not a course"],
             ["Gachibowli, Madhapur, Kondapur", "16–24 km", "A consultation, not a course"],
             ["LB Nagar, Dilsukhnagar, Vanasthalipuram", "16–24 km",
              "A consultation, not a course"],
         ],
         "note": "“Consider carefully” and “a consultation, not a course” are not "
                 "refusals. They mean the assessment, the diagnosis and the plan are worth "
                 "the trip, and that if the plan needs three sessions a week you should "
                 "hear that before you commit rather than after."},

        {"kind": "split", "eyebrow": "From outside Hyderabad",
         "h2": "Patients travel here for the surgery, not for the sessions.",
         "body": ["Melanocyte transplant and punch grafting for stable vitiligo are offered at "
                  "comparatively few centres in India, and that is what brings patients from "
                  "outside Telangana. Surgery is a staged visit (assessment, procedure, "
                  "review), rather than a standing weekly commitment, which is what makes "
                  "travelling for it sensible where travelling for phototherapy is not.",
                  "The sequence that wastes least is: send photographs on WhatsApp, take a "
                  "video consultation, and only then book travel. A significant proportion "
                  "of people who ask about grafting are told to wait, because the disease "
                  "has not been stable long enough. Hearing that from home is better than "
                  "hearing it after a flight."],
         "cta": ("How to plan a visit from out of state", "travelling-for-treatment"),
         "items": [
             {"title": "Photographs first",
              "body": "Daylight, no filter, and a one-line history. Enough to say whether "
                      "the trip is warranted."},
             {"title": "Video consultation second",
              "body": "Arranged on WhatsApp. Diagnosis, plan and a realistic timeline, "
                      "before anything is booked."},
         ]},

        {"kind": "callout", "title": "Not in Hyderabad at all?",
         "body": "Video consultation covers a great deal: diagnosis from photographs and "
                 "history, a written plan, a second opinion on a plan you already have, and "
                 "arranging phototherapy near you where that is the sensible answer. What it "
                 "cannot do is a Wood's lamp examination or any procedure."},

        VISIT,
    ],
    "faq_h2": "Getting to the clinic",
    "faqs": [
        ("Do you have a second clinic in Hyderabad?",
         "No. There is one consulting location, in Karkhana, Secunderabad. Earlier listings "
         "showing a Jubilee Hills or West Marredpally clinic are out of date."),
        ("I live 20 km away. Is it worth coming?",
         "For a diagnosis, a second opinion or a plan: yes, and people do. For a course of "
         "phototherapy at three sessions a week, be honest with yourself about the journey "
         "first; you will get the same honesty back at the consultation."),
        ("Which localities are closest?",
         "Vikrampuri Colony, Trimulgherry, West and East Marredpally, Bowenpally, Bolarum "
         "and Alwal are all within about six kilometres of Karkhana."),
        ("Is the clinic near a Metro station?",
         "It is on the Secunderabad side, off Wellington Road. Directions are easiest from "
         "the Google listing, which is still under the name BNR Skin & Vitiligo Hospital."),
        ("Do you see patients from outside Telangana?",
         "Yes. Particularly for vitiligo surgery. Send photographs on WhatsApp and take a video "
         "consultation before booking travel, so you know whether the trip is warranted."),
    ],
    "related": [
        ("locations-secunderabad", "The clinic in Secunderabad",
         "The address, what runs there, and how to find it."),
        ("travelling-for-treatment", "Coming from another state",
         "How a staged visit works, and what to send before you book anything."),
        ("online-consultation", "Consult online from anywhere in India",
         "What a video consultation can settle, and what it cannot."),
    ],
},

]
