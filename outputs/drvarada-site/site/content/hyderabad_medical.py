"""T1 — Hyderabad service pillars: chronic conditions, acne and trichology.

Local intent. These pages answer "can this clinic treat my problem, and should I book"
— they do not re-teach the disease. Where a national hub exists (vitiligo, psoriasis),
the education lives there and this page links to it. That separation is the whole point
of KEYWORD_MAP rule 2: two pages, two intents, no cannibalisation.

Page anatomy is fixed by MASTER_PLAN §5: query-matched H1 → credibility → what we
actually do → protocol with named technology → honest limits → FAQ → related.
"""

from chrome import PHONE, WHATSAPP

CRED = ["45 years in dermatology", "Dermatologist & dermatosurgeon",
        "Karkhana, Secunderabad", "Booking on WhatsApp"]

VISIT = {
    "kind": "cards", "eyebrow": "Where to book", "h2": "One clinic, in Secunderabad",
    "intro": "Consulting rooms, phototherapy and the surgical list at one address in "
             "Secunderabad. The practice was formerly known as BNR Skin & Vitiligo "
             "Hospital.",
    "items": [
        {"title": "Where", "icon": "pin",
         "body": "Plot No D13B, Wellington Rd, Vikrampuri Colony, "
                 "Karkhana, Secunderabad, Telangana 500009.",
         "list": ["Serves Trimulgherry, West Marredpally, Bowenpally, Alwal",
                  "Formerly BNR Skin & Vitiligo Hospital"]},
        {"title": "How to book", "icon": "chat",
         "body": "On WhatsApp: one number, answered by the clinic team, who confirm a "
                 "time and say what to bring.",
         "list": ["Photographs welcome before you travel",
                  "Video consultation arranged the same way"]},
    ],
}

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-treatment-hyderabad", "template": "T1", "condition": "Vitiligo",
    "crumbs": [("Vitiligo treatment in Hyderabad", None)],
    "title": "Vitiligo Treatment in Hyderabad | Dr. Varada",
    "meta": "Vitiligo and leucoderma treatment in Hyderabad. Narrowband UVB, excimer laser and "
            "melanocyte graft surgery with a dermatosurgeon of 45 years.",
    "eyebrow": "Hyderabad",
    "h1": "Vitiligo treatment in Hyderabad",
    "lede": "A practice that began as a vitiligo hospital, still run by the same "
            "dermatosurgeon, with the full range under one roof: topical therapy, narrowband "
            "UVB, excimer laser and surgical repigmentation for stable disease.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["niams-vitiligo", "aad-vitiligo-tx", "dermnet-vitiligo", "nhs-vitiligo", "iadvl-vitiligo-surgery"],
    "glance": [
        ("Also called", "Leucoderma, white patches, safed daag"),
        ("Available here", "Topicals, NB-UVB, excimer, graft surgery"),
        ("Surgery", "Melanocyte transplant, punch, blister grafting"),
        ("Where", "At the Secunderabad clinic"),
        ("First visit", "Diagnosis, activity assessment, plan"),
        ("Review", "Every 6–8 weeks"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Why here",
         "h2": "The clinic that still does the surgery.",
         "body": [
             "Most vitiligo in Hyderabad is treated medically, which is correct for most "
             "patients. But medical treatment reaches a limit: patches on the lips, the "
             "fingertips, and any patch whose hairs have turned white have lost the pigment "
             "reservoir that creams and light work by recruiting.",
             "For those patches the option is surgical: melanocyte transplant or punch "
             "grafting, moving your own pigment cells into skin that has none. "
             "Comparatively few centres in the city offer it, and it is the reason patients "
             "travel here from outside Telangana.",
             "It is also the reason a first appointment here is an assessment rather than a "
             "sale. Surgery only works on disease that has been stable for about twelve months, "
             "and a significant proportion of people who ask about it are told to wait, which "
             "is a clinical answer, not a scheduling one.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "What treatment looks like here",
         "items": [
             {"title": "Assess activity",
              "body": "Wood's lamp examination, patch margins, history of new patches, and "
                      "baseline photographs. Active or stable decides everything after."},
             {"title": "Stop the spread",
              "body": "Active disease is quietened first: topicals, occasionally a short oral "
                      "course. Repigmenting while new patches appear is wasted effort."},
             {"title": "Repigment medically",
              "body": "Narrowband UVB for widespread disease, excimer for a few patches, "
                      "usually combined with a topical. Reviewed at six to eight weeks."},
             {"title": "Operate if stable",
              "body": "Patches that will not respond to light, on disease quiet for twelve "
                      "months, are assessed for grafting on the surgical list."},
         ]},

        {"kind": "split", "eyebrow": "Realistic expectations",
         "h2": "What can be promised, and what cannot.",
         "body": ["Vitiligo cannot be cured, here or anywhere. What treatment does reliably do "
                  "is stop the spread in active disease, and repigment a meaningful proportion "
                  "of affected skin in many patients: best on the face and trunk, least on "
                  "hands, feet and lips.",
                  "You will be told at the first visit which category your patches fall "
                  "into, and roughly how long a fair trial takes. Being told that a patch "
                  "is unlikely to respond to light is more useful than six months of "
                  "finding out."],
         "cta": ("Read the full vitiligo section", "vitiligo"),
         "items": [
             {"title": "Face and trunk respond best",
              "body": "Dense follicles, good reservoir. This is where phototherapy earns "
                      "its reputation."},
             {"title": "Hands, feet and lips need surgery",
              "body": "Not as a fallback, as the appropriate first choice for those sites."},
         ]},

        VISIT,

        {"kind": "callout", "title": "Coming from outside Hyderabad?",
         "body": "Send photographs by WhatsApp before booking travel, or take a video "
                 "consultation first. The point is to know whether the trip is warranted, and "
                 "if surgery is the reason for it, whether your disease is stable enough."},
    ],
    "faq_h2": "Vitiligo treatment in Hyderabad",
    "faqs": [
        ("Which vitiligo treatments are available at this clinic?",
         "Topical therapy including calcineurin and JAK inhibitors, narrowband UVB "
         "phototherapy, excimer laser, and surgical repigmentation: melanocyte transplant, "
         "punch grafting and blister grafting. Every one of them is done at the clinic in "
         "Secunderabad, so nothing is referred out mid-treatment."),
        ("Can vitiligo be cured in Hyderabad or anywhere else?",
         "No. Vitiligo is not curable. Treatment stops the spread and repigments affected "
         "skin, often substantially. Any clinic in any city promising a cure is making a "
         "claim it cannot support."),
        ("How much does vitiligo treatment cost here?",
         "Costs are quoted in writing after examination, because the number of sessions "
         "your patches need depends on their site, size and duration. The pricing structure "
         "is explained on the cost page."),
        ("Do you do vitiligo surgery?",
         "Yes: melanocyte transplant and punch grafting, for disease that has been stable for "
         "about twelve months. Assessment for stability comes first, and being told to wait is "
         "a common outcome."),
        ("Where is the clinic, and how do I book?",
         "Karkhana, Secunderabad: the practice you may know as BNR Skin & Vitiligo Hospital. "
         "Everything runs at that one address: consultation, phototherapy, excimer and surgery. "
         "Appointments are arranged on WhatsApp."),
        ("Do you treat children with vitiligo?",
         "Yes. Children generally respond better than adults, and early treatment is the "
         "single biggest variable a family controls."),
    ],
    "related": [
        ("vitiligo", "The full vitiligo section",
         "What the disease is, every treatment explained, and what each costs."),
        ("vitiligo-graft-surgery", "Graft surgery",
         "Who qualifies, the three techniques, and what recovery involves."),
        ("vitiligo-treatment-secunderabad", "Vitiligo treatment in Secunderabad",
         "The same clinic, and what the journey means for a course of light."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-treatment-hyderabad", "template": "T1", "condition": "Psoriasis",
    "crumbs": [("Psoriasis treatment in Hyderabad", None)],
    "title": "Psoriasis Treatment in Hyderabad | Dr. Varada",
    "meta": "Psoriasis treatment in Hyderabad: topical therapy, narrowband UVB phototherapy, "
            "methotrexate and biologics, with joint screening.",
    "eyebrow": "Hyderabad",
    "h1": "Psoriasis treatment in Hyderabad",
    "lede": "Psoriasis is a long-term condition, so it is treated as one: a plan for the flare, "
            "a plan for maintenance, a written plan for the next flare, and a review of your "
            "joints, which is the part most often skipped.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["niams-psoriasis", "aad-psoriasis", "dermnet-psoriasis", "nice-psoriasis", "who-psoriasis"],
    "glance": [
        ("Available here", "Topicals, NB-UVB, systemics, biologics"),
        ("Phototherapy", "At the clinic"),
        ("Screened for", "Psoriatic arthritis, metabolic risk"),
        ("Reviews", "At the Secunderabad clinic"),
        ("Flare plan", "Written, at the first visit"),
        ("Curable", "No, but often well controlled"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The approach",
         "h2": "Clearing a flare is easy. Keeping it away is the job.",
         "body": [
             "Almost any potent steroid will flatten a plaque. What separates good psoriasis "
             "care from the other kind is what happens in month four, whether there was a "
             "step-down plan, or whether the treatment was simply stopped and the disease "
             "rebounded, sometimes worse than before.",
             "So the first consultation produces three things: what clears the current "
             "flare, what holds it afterwards, and a written plan for what to start at the "
             "first sign of the next one. Patients who leave with that flare less.",
             "It also produces a joint assessment. Up to a third of people with psoriasis "
             "develop psoriatic arthritis, the damage it causes is permanent, and the "
             "symptoms are routinely dismissed as unrelated aches. It is asked about at "
             "every visit here.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "How a course runs",
         "items": [
             {"title": "Diagnose properly",
              "body": "Including the nails, the scalp and the folds. The three sites where "
                      "psoriasis is most often called something else."},
             {"title": "Clear the flare",
              "body": "Topical therapy matched to site and severity. Phototherapy where "
                      "disease is widespread or guttate."},
             {"title": "Step down to maintenance",
              "body": "Frequency reduced rather than stopped, because abrupt withdrawal is "
                      "the commonest cause of a rebound."},
             {"title": "Escalate if needed",
              "body": "Methotrexate or other systemics for extensive or disabling disease; "
                      "biologics where those fail, after TB and hepatitis screening."},
         ]},

        {"kind": "split", "eyebrow": "The part usually missed",
         "h2": "Your joints are part of this consultation.",
         "body": ["Morning stiffness lasting more than half an hour. A finger or toe swollen "
                  "along its whole length. Heel pain. Low back pain that eases as you move "
                  "rather than worsening. Any of those alongside psoriasis needs "
                  "investigating rather than tolerating.",
                  "Joint damage in psoriatic arthritis does not reverse, and the window in "
                  "which treatment prevents it is early. Where the picture suggests it, you are "
                  "referred to a rheumatologist promptly, and methotrexate, which treats both "
                  "skin and joints, becomes the obvious systemic choice."],
         "cta": ("Systemics and biologics explained", "psoriasis-biologics"),
         "items": [
             {"title": "Nail changes are a warning",
              "body": "Pitting and lifting are associated with joint disease. They are "
                      "looked for deliberately."},
             {"title": "Asked at every visit",
              "body": "Not once at diagnosis. Arthritis can appear years after the skin "
                      "disease."},
         ]},

        VISIT,

        {"kind": "callout", "title": "Second opinions are welcome",
         "body": "Bring the previous diagnosis, every prescription and any blood results. The "
                 "commonest finding in a psoriasis second opinion is not a wrong diagnosis. It "
                 "is a potent steroid that has been running for months without a maintenance "
                 "plan or a review."},
    ],
    "faq_h2": "Psoriasis treatment in Hyderabad",
    "faqs": [
        ("Which psoriasis treatments are available at this clinic?",
         "Topical therapy, medicated scalp treatment, narrowband UVB phototherapy at the "
         "Secunderabad clinic, conventional systemics including methotrexate, and "
         "biologics after appropriate screening."),
        ("Can psoriasis be cured?",
         "No. It is a long-term immune condition. Treatment aims at remission: skin that is "
         "clear or nearly clear, held there with maintenance, sometimes for years."),
        ("Do you offer phototherapy in Hyderabad?",
         "Yes, narrowband UVB at the clinic. A course typically runs 20 to 36 "
         "sessions at two to three a week, so it is worth checking the timings suit you "
         "before starting."),
        ("I have joint pain along with psoriasis. Is that related?",
         "It may well be. Up to a third of people with psoriasis develop psoriatic arthritis, "
         "and it is important to catch early because joint damage does not reverse. Raise it at "
         "your appointment. It will be asked about anyway."),
        ("Where is the clinic, and how do I book?",
         "Karkhana, Secunderabad. Phototherapy, consultations and reviews all run at "
         "the same address, so a course of light treatment does not mean travelling "
         "between sites. Appointments are arranged on WhatsApp."),
        ("Is scalp psoriasis treated here?",
         "Yes, and it is the commonest site. It needs a descale-then-treat sequence. Ordinary "
         "anti-dandruff shampoo cannot penetrate the adherent scale."),
    ],
    "related": [
        ("psoriasis", "The full psoriasis section",
         "Types, triggers, every treatment, and what each costs."),
        ("psoriasis-scalp", "Scalp psoriasis",
         "The commonest site, and how to tell it from dandruff."),
        ("psoriasis-treatment-secunderabad", "Psoriasis treatment in Secunderabad",
         "The same clinic, written for patients on the Secunderabad side."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "hair-loss-treatment-hyderabad", "template": "T1", "condition": "Hair loss",
    "crumbs": [("Hair loss treatment in Hyderabad", None)],
    "title": "Hair Loss Treatment in Hyderabad | Dr. Varada",
    "meta": "Hair loss and hair fall treatment in Hyderabad for men and women. Diagnosed with "
            "trichoscopy and blood work before anything is prescribed.",
    "eyebrow": "Hyderabad",
    "h1": "Hair loss treatment in Hyderabad",
    "lede": "Hair loss has around six common causes and they need different treatments. "
            "The reason most hair treatment fails is that it was started before anyone "
            "established which one you actually have.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["aad-hair-loss", "statpearls-aga", "dermnet-mphl", "dermnet-fphl", "dermnet-telogen-effluvium"],
    "glance": [
        ("Assessed with", "History, pull test, trichoscopy, bloods"),
        ("Common causes", "Pattern loss, telogen effluvium, deficiency, thyroid"),
        ("Men", "Pattern hair loss: treatable, needs consistency"),
        ("Women", "Deficiency and thyroid more often involved"),
        ("First result", "Judged at 3–6 months, not weeks"),
        ("Surgery", "Grafting, if medical treatment is not enough"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The problem with hair treatment",
         "h2": "Shedding and thinning are not the same complaint.",
         "body": [
             "Someone losing handfuls in the shower and someone whose parting has widened over "
             "five years have different diseases, and giving them the same serum helps neither. "
             "Sudden diffuse shedding is usually telogen effluvium: a reaction to an illness, a "
             "fever, childbirth, a crash diet or severe stress, typically three months earlier. "
             "It is self-limiting and it needs the cause found, not a growth stimulant.",
             "Gradual thinning at the crown or the parting is pattern hair loss, which is "
             "progressive, genetic and treatable, but only with consistent long-term treatment, "
             "and only while treatment continues.",
             "Patchy round bald areas are alopecia areata, an autoimmune condition needing "
             "different treatment again. Telling these apart takes an examination and a "
             "trichoscope, and takes about ten minutes.",
         ]},

        {"kind": "table", "eyebrow": "Causes", "h2": "What is actually causing it",
         "head": ["Pattern", "Likely cause", "What it needs"],
         "rows": [
             ["Sudden diffuse shedding", "Telogen effluvium",
              "Find the trigger 3 months back; usually self-limiting"],
             ["Gradual crown or parting thinning", "Pattern hair loss",
              "Long-term medical treatment; grafting if advanced"],
             ["Round smooth bald patches", "Alopecia areata",
              "Immune-directed treatment, not growth stimulants"],
             ["Thinning with fatigue, cold, weight change", "Thyroid disease",
              "Thyroid function test; treat the thyroid"],
             ["Thinning with heavy periods or poor diet", "Iron or ferritin deficiency",
              "Confirm on bloods; correct properly, not casually"],
             ["Scaling, itch, redness with loss", "Scalp disease",
              "Treat the scalp first: hair follows"],
             ["Loss along the hairline, with tightness", "Traction or scarring alopecia",
              "Urgent: scarring loss is permanent"],
         ],
         "note": "The last row is the one that cannot wait. Scarring alopecias destroy "
                 "follicles permanently, and the difference between early and late "
                 "treatment is the difference between keeping hair and not."},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "What the first appointment does",
         "items": [
             {"title": "History that goes back a year",
              "body": "Illness, fever, surgery, childbirth, dieting, new medication, stress. "
                      "The cause of today's shedding was usually three months ago."},
             {"title": "Examination and trichoscopy",
              "body": "A pull test, and magnified examination of the scalp: miniaturised hairs, "
                      "follicular openings, whether scarring is present."},
             {"title": "Targeted blood tests",
              "body": "Ferritin, thyroid function, vitamin D and B12 where indicated. "
                      "Tested, not assumed."},
             {"title": "A treatment matched to the cause",
              "body": "And a review date, because hair is judged at three to six months. "
                      "Anything judged at three weeks is being judged wrong."},
         ]},

        {"kind": "split", "eyebrow": "Expectations",
         "h2": "Hair moves slowly. Treatment has to be judged slowly.",
         "body": ["Hair grows about a centimetre a month, and a follicle pushed back into "
                  "its growing phase takes months to produce visible hair. Nothing genuine "
                  "works in three weeks, and anything advertised as working in three weeks "
                  "is selling you the shedding phase of a normal cycle.",
                  "There is also an unpleasant truth about pattern hair loss: treatment "
                  "holds the ground while you continue it. Stopping generally means losing "
                  "what was gained over the following year. That is said before you start, "
                  "not after."],
         "cta": ("If surgery is the answer", "hair-grafting-hyderabad"),
         "items": [
             {"title": "Photographs at baseline",
              "body": "Standardised, fixed distance. Memory cannot judge hair density over "
                      "six months; a photograph can."},
             {"title": "Consistency beats intensity",
              "body": "A treatment used daily for a year outperforms three treatments used "
                      "enthusiastically for a month each."},
         ]},

        VISIT,
    ],
    "faq_h2": "Hair loss questions",
    "faqs": [
        ("Why is my hair falling out suddenly?",
         "Sudden diffuse shedding is usually telogen effluvium: a delayed reaction to an "
         "illness, fever, surgery, childbirth, crash dieting or severe stress, typically around "
         "three months earlier. It is self-limiting, but the trigger is worth identifying and "
         "any deficiency worth correcting."),
        ("How long before hair loss treatment shows results?",
         "Three to six months for a fair judgement. Hair grows roughly a centimetre a month "
         "and a follicle re-entering its growth phase takes time to produce visible hair."),
        ("Is hair loss treatment different for men and women?",
         "The assessment is the same but the answers differ. Iron deficiency, thyroid disease "
         "and hormonal causes are found more often in women, and some treatments used in men "
         "are not appropriate for women. Particularly if pregnancy is possible."),
        ("Do I need blood tests?",
         "Usually a small targeted set: ferritin, thyroid function, and vitamin D or B12 where "
         "the history suggests it. Not a broad panel for its own sake."),
        ("Will I need treatment forever?",
         "For pattern hair loss, treatment holds ground while it continues, and stopping "
         "generally means losing the gain over the following year. Telogen effluvium and "
         "deficiency-related loss usually need treatment only until the cause is corrected."),
        ("Can hair loss be reversed?",
         "It depends entirely on the cause. Telogen effluvium and deficiency-related loss "
         "recover well. Pattern loss can be slowed and partially reversed. Scarring "
         "alopecias destroy the follicle permanently, which is why early diagnosis matters."),
    ],
    "related": [
        ("alopecia-treatment-hyderabad", "Alopecia areata",
         "Round patches: an autoimmune condition needing different treatment."),
        ("prp-hair-treatment-hyderabad", "PRP and microneedling",
         "The adjunct people ask for first: what it does and does not do."),
        ("hair-loss-treatment-secunderabad", "Hair loss treatment in Secunderabad",
         "The same workup, for patients on the Secunderabad side."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "alopecia-treatment-hyderabad", "template": "T1", "condition": "Alopecia areata",
    "crumbs": [("Alopecia treatment in Hyderabad", None)],
    "title": "Alopecia Areata Treatment in Hyderabad | Dr. Varada",
    "meta": "Alopecia areata treatment in Hyderabad: patchy hair loss, totalis and universalis. "
            "Intralesional steroids, immunotherapy and newer options assessed.",
    "eyebrow": "Hyderabad",
    "h1": "Alopecia areata treatment in Hyderabad",
    "lede": "Smooth round bald patches that appeared over weeks are not ordinary hair loss. "
            "Alopecia areata is autoimmune, the follicles are alive but switched off, which is "
            "why it needs immune-directed treatment and not a growth serum.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["niams-alopecia-areata", "dermnet-alopecia-areata", "aad-hair-loss"],
    "glance": [
        ("What it is", "Autoimmune: follicles alive but suppressed"),
        ("Pattern", "Smooth round patches, scalp or beard"),
        ("Totalis", "Complete scalp loss"),
        ("Universalis", "All body hair"),
        ("Regrowth", "Common: often spontaneous in limited disease"),
        ("Associated", "Thyroid disease, vitiligo"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What it is",
         "h2": "The follicles are still there.",
         "body": [
             "In alopecia areata the immune system attacks the hair follicle and forces it "
             "into dormancy. Crucially it does not destroy it. That is why regrowth is "
             "possible even after years, and why the treatment is aimed at calling off the "
             "immune attack rather than at stimulating growth.",
             "Limited patchy disease has a good outlook: a substantial proportion regrows "
             "within a year even without treatment, though treatment shortens that and reduces "
             "the psychological weight of waiting. Extensive disease, alopecia totalis and "
             "universalis, is harder and less predictable.",
             "It is also worth screening for the conditions that travel with it. Autoimmune "
             "thyroid disease is the commonest association, and vitiligo occurs more often "
             "in people with alopecia areata than in the general population.",
         ]},

        {"kind": "table", "eyebrow": "Treatment", "h2": "What is used, and for what",
         "head": ["Treatment", "Suits", "Notes"],
         "rows": [
             ["Intralesional steroid injections", "A few discrete patches",
              "First-line for limited adult disease; repeated at intervals"],
             ["Potent topical steroids", "Children, or where injections are declined",
              "Time-limited; skin thinning is the risk"],
             ["Topical immunotherapy", "Extensive or resistant disease",
              "Deliberately provokes a mild reaction; specialist supervision"],
             ["Topical minoxidil", "Adjunct, not a primary treatment",
              "Supports regrowth once the attack is controlled"],
             ["Newer immune-directed agents", "Severe or extensive disease",
              "Assessed case by case; monitoring required"],
             ["No active treatment", "Small patches, patient preference",
              "A legitimate choice: many regrow spontaneously"],
         ],
         "note": "'Watch and wait' belongs on this list. For a single small patch in an "
                 "adult it is a reasonable plan, provided it is a decision rather than an "
                 "absence of one."},

        {"kind": "split", "eyebrow": "The part that isn't dermatology",
         "h2": "Sudden visible hair loss is not a small thing.",
         "body": ["Alopecia areata arrives quickly, is highly visible, and has no symptoms, "
                  "which makes it easy for other people to treat as trivial. It is not. The "
                  "distress it causes is frequently out of proportion to the area involved, and "
                  "that is a normal response rather than an overreaction.",
                  "Practical measures are part of the plan: what to say to people, whether "
                  "camouflage or a hairpiece is wanted, and, for children, a note to the "
                  "school. None of these are consolation prizes; they are the part of treatment "
                  "that works immediately."],
         "cta": ("If it is not alopecia areata", "hair-loss-treatment-hyderabad"),
         "items": [
             {"title": "Regrowth is common",
              "body": "Limited disease frequently regrows within a year. New hair often "
                      "comes back white first and recolours later."},
             {"title": "Relapse is also common",
              "body": "It can recur years later. Knowing that in advance makes it far less "
                      "alarming when it happens."},
         ]},

        VISIT,

        {"kind": "callout", "warn": True, "title": "Beware anything promising a permanent cure",
         "body": "Alopecia areata relapses and remits by nature. A treatment that coincides "
                 "with a spontaneous regrowth will appear to have cured it, which is why "
                 "this condition attracts more unfounded claims than almost any other in "
                 "dermatology."},
    ],
    "faq_h2": "Alopecia areata questions",
    "faqs": [
        ("Will my hair grow back?",
         "In limited patchy alopecia areata, frequently yes: a substantial proportion regrows "
         "within a year, and treatment shortens that. Extensive disease, totalis and "
         "universalis, is less predictable."),
        ("Is alopecia areata permanent?",
         "The follicles are not destroyed, so regrowth remains possible even after long "
         "periods. That distinguishes it from scarring alopecias, where the follicle is lost "
         "for good."),
        ("What causes alopecia areata?",
         "It is autoimmune, with a genetic component. Stress is often blamed and may act as "
         "a trigger in someone predisposed, but it is not the cause."),
        ("Does it mean I have another autoimmune disease?",
         "Not necessarily, but the associations are real enough to check for. Thyroid disease "
         "most commonly, and vitiligo occurs more often than in the general population."),
        ("Are steroid injections painful?",
         "There is a brief sting with each injection. Sessions are short and repeated at "
         "intervals of several weeks. Most adults tolerate them without difficulty."),
        ("Can children be treated?",
         "Yes, though injections are usually avoided in young children in favour of topical "
         "treatment. The approach is gentler and the outlook in children is generally good."),
    ],
    "related": [
        ("hair-loss-treatment-hyderabad", "Hair loss treatment",
         "If the pattern is thinning rather than round patches."),
        ("alopecia-areata-treatment-india", "Alopecia across India",
         "Totalis and universalis explained, and what treatment can realistically do."),
        ("hair-grafting-hyderabad", "Hair grafting",
         "Not appropriate in active alopecia areata, and here is why."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "hair-grafting-hyderabad", "template": "T1", "condition": "Hair loss",
    "crumbs": [("Hair grafting in Hyderabad", None)],
    "title": "Hair Grafting Surgery in Hyderabad | Dr. Varada",
    "meta": "Hair grafting and transplant surgery in Hyderabad by a dermatosurgeon of 45 years, "
            "who is a candidate, why medical treatment comes first, and results.",
    "eyebrow": "Hyderabad",
    "h1": "Hair grafting surgery in Hyderabad",
    "lede": "Grafting moves hair you already have to where you no longer have it. It does not "
            "create new hair, and it does not stop the loss continuing around it, which is why "
            "medical treatment comes first and surgery second.",
    "acts": [("Book an assessment", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["statpearls-aga", "dermnet-mphl", "dermnet-fphl", "aad-hair-loss"],
    "glance": [
        ("What it is", "Redistribution of your own follicles"),
        ("Assessed first", "Cause of loss, donor density, stability"),
        ("Not suitable for", "Active alopecia areata, unstable loss"),
        ("Anaesthesia", "Local, day procedure"),
        ("Visible result", "Judged at 9–12 months"),
        ("Continues after", "Medical treatment does not stop"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The honest framing",
         "h2": "A fixed supply, redistributed.",
         "body": [
             "Every hair placed in a graft comes from the back and sides of your own head. "
             "There is a finite number available, it does not regenerate, and spending it "
             "badly cannot be undone. That single fact is why assessment matters more than "
             "technique.",
             "Pattern hair loss also continues after surgery. Grafted hairs are taken from an "
             "area genetically resistant to thinning and generally persist, but the native hair "
             "around them keeps receding, which is how someone ends up with an island of "
             "transplanted hair and a new bald zone behind it. Continuing medical treatment is "
             "not optional; it is what protects the result.",
             "For those reasons a great many people who ask about grafting are advised to "
             "treat medically first and reassess in a year. Some never need surgery at all.",
         ]},

        {"kind": "steps", "eyebrow": "The pathway", "h2": "How a case is assessed",
         "items": [
             {"title": "Establish the cause",
              "body": "Grafting is for pattern hair loss and for scarring or traction loss "
                      "that has stabilised. It is wrong for telogen effluvium and dangerous "
                      "in active alopecia areata."},
             {"title": "Measure the donor area",
              "body": "Density at the back and sides sets the ceiling on what is possible. "
                      "This is measured, not eyeballed."},
             {"title": "Treat medically, then review",
              "body": "Often for six to twelve months. Stabilising the loss first protects "
                      "both the result and the donor supply."},
             {"title": "Plan conservatively",
              "body": "A hairline designed for a forty-year-old should still look right at "
                      "sixty. Overly low, overly dense hairlines age badly."},
         ]},

        {"kind": "table", "eyebrow": "Techniques",
         "h2": "FUE, FUT, and the smaller grafts",
         "head": ["Technique", "What it involves", "Where it suits"],
         "rows": [
             ["FUE: follicular unit extraction",
              "Follicles taken individually from the donor area",
              "No linear scar; suits short hair and smaller sessions"],
             ["FUT: follicular unit transplantation",
              "A donor strip removed, then dissected into units",
              "Yields more grafts per session; leaves a line scar"],
             ["Eyebrow grafting", "Single hairs placed at very shallow angles",
              "Loss from over-plucking, scarring or thyroid disease"],
             ["Eyelash grafting", "A small number of hairs, meticulously angled",
              "Selected cases; the transplanted lashes need trimming"],
             ["Beard and moustache", "Same principle, different angles",
              "Scarring and patchy growth"],
             ["Scar and traction loss", "Grafting into stabilised scar tissue",
              "Only once the underlying cause has stopped"],
         ],
         "note": "Neither FUE nor FUT is the better operation in the abstract: they trade donor "
                 "scar against graft yield, and which trade suits you depends on your donor "
                 "density, how much you need and how short you wear your hair. Any clinic that "
                 "offers only one will recommend only one."},

        {"kind": "split", "eyebrow": "Expectations",
         "h2": "What a good result looks like, and when.",
         "body": ["Transplanted hairs shed within the first few weeks. This is normal and "
                  "expected, and it is the point at which patients who were not warned "
                  "panic. Regrowth begins around month three or four, and the result is "
                  "judged at nine to twelve months.",
                  "A good result is one nobody identifies as surgery. That means a "
                  "conservative hairline, natural irregularity at the front, and density "
                  "placed where it reads best rather than spread thin across everything."],
         "cta": ("Start with the medical assessment", "hair-loss-treatment-hyderabad"),
         "items": [
             {"title": "Shedding at week three",
              "body": "Expected. The follicle is retained; the shaft is shed before "
                      "regrowth."},
             {"title": "Judged at nine months",
              "body": "Not at three. Assessing the result early produces unnecessary "
                      "disappointment."},
         ]},

        VISIT,

        {"kind": "callout", "warn": True, "title": "Graft counts are not a measure of quality",
         "body": "A larger number of grafts is not automatically a better outcome, and "
                 "harvesting aggressively to reach a headline figure permanently thins the "
                 "donor area. What matters is the cause of your loss, your donor density, "
                 "and where the hair is placed."},
    ],
    "faq_h2": "Hair grafting questions",
    "faqs": [
        ("Am I a candidate for hair grafting?",
         "It depends on the cause of your loss, whether it has stabilised, and how much "
         "donor hair you have. Pattern hair loss with good donor density is the classic "
         "indication. Active alopecia areata and unstable loss are not."),
        ("Will I need to keep taking medication after surgery?",
         "Generally yes. Grafted hair persists, but the native hair around it continues to "
         "thin if pattern loss is untreated. Medical treatment is what protects the surgical "
         "result over time."),
        ("When will I see the result?",
         "Transplanted hairs shed within a few weeks. Expected and normal. Regrowth starts "
         "around month three or four, and the result is judged at nine to twelve months."),
        ("Does it hurt?",
         "The procedure is done under local anaesthetic. There is discomfort afterwards for "
         "a few days, managed with simple analgesia."),
        ("Can hair grafting treat alopecia areata?",
         "No. Not while it is active. The immune attack that caused the loss would affect "
         "transplanted follicles as well, and the trauma of surgery can provoke further loss."),
        ("Why might I be told to wait?",
         "Because the loss has not stabilised, because medical treatment has not been given "
         "a fair trial, or because your donor supply would be better spent later. Donor hair "
         "is finite and spending it early cannot be undone."),
    ],
    "related": [
        ("hair-loss-treatment-hyderabad", "Hair loss treatment",
         "The medical assessment that comes first."),
        ("alopecia-treatment-hyderabad", "Alopecia areata",
         "Why grafting is not the answer for this one."),
        ("prp-hair-treatment-hyderabad", "PRP and microneedling",
         "The non-surgical adjunct, framed honestly."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "acne-treatment-hyderabad", "template": "T1", "condition": "Acne",
    "crumbs": [("Acne treatment in Hyderabad", None)],
    "title": "Acne & Acne Scar Treatment in Hyderabad | Dr. Varada",
    "meta": "Acne and acne scar treatment in Hyderabad. Medical therapy first, then peels and "
            "scar work. Treating active acne before scarring is the whole strategy.",
    "eyebrow": "Hyderabad",
    "h1": "Acne treatment in Hyderabad",
    "lede": "Acne is treated in a specific order for a specific reason: every month of "
            "active inflammation is a month of new scarring, and scarring is far harder to "
            "treat than the acne that caused it.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["niams-acne", "dermnet-acne", "nhs-acne", "dermnet-phototype"],
    "glance": [
        ("First", "Control the active acne"),
        ("Then", "Marks, then scars, in that order"),
        ("Available", "Medical therapy, peels, scar procedures"),
        ("Judged at", "8–12 weeks"),
        ("Marks vs scars", "Different problems, different treatments"),
        ("Where", "At the Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The order matters",
         "h2": "Treat the acne first. Always.",
         "body": [
             "Patients frequently arrive asking about scar treatment while acne is still "
             "active. Doing scar work on inflamed skin is both less effective and "
             "counterproductive: new lesions keep arriving, and some procedures aggravate them. "
             "So the sequence is fixed: control the acne, wait for it to settle, then address "
             "what it left behind.",
             "The second thing worth separating is marks from scars. Flat brown or red patches "
             "left after a spot are post-inflammatory pigmentation: they fade on their own over "
             "months and respond well to topicals and peels. Indentations and raised areas are "
             "true scars, they do not fade, and they need procedural treatment.",
             "Being told which of the two you have saves a great deal of money. A large "
             "proportion of people who believe they have acne scars have pigmentation that "
             "will resolve with sun protection and time.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "How acne is treated here",
         "items": [
             {"title": "Grade it, and look for a cause",
              "body": "Comedonal, inflammatory or nodular. In women with irregular cycles or "
                      "sudden adult acne, hormonal causes are considered."},
             {"title": "Medical treatment first",
              "body": "Topical retinoids, benzoyl peroxide, antibiotics where indicated, or "
                      "oral therapy in severe or scarring disease."},
             {"title": "Review at 8 to 12 weeks",
              "body": "Acne treatment takes that long to judge. Skin often looks worse in "
                      "week three, which is expected and not a reason to stop."},
             {"title": "Then treat what's left",
              "body": "Peels for pigmentation and texture; procedural treatment for true "
                      "scarring once the acne is quiet."},
         ]},

        {"kind": "table", "eyebrow": "After the acne", "h2": "Marks or scars?",
         "head": ["What you see", "What it is", "What it needs"],
         "rows": [
             ["Flat brown patches", "Post-inflammatory hyperpigmentation",
              "Sun protection, topicals, peels: fades with time"],
             ["Flat red or purple marks", "Post-inflammatory erythema",
              "Usually settles on its own over months"],
             ["Small deep pits", "Ice-pick scarring", "Procedural; often needs combination"],
             ["Broad shallow depressions", "Rolling or boxcar scarring",
              "Resurfacing and subcision approaches"],
             ["Raised firm lumps", "Hypertrophic or keloid scarring",
              "Injection-based treatment; do not excise casually"],
         ],
         "note": "The top two rows fade without procedures. Being told that, rather than "
                 "being sold a course of laser for pigmentation, is the difference this "
                 "page is trying to make."},

        {"kind": "split", "eyebrow": "Sun and pigmentation",
         "h2": "Why acne marks last longer in India.",
         "body": ["Skin that produces more pigment reacts to inflammation by producing more "
                  "pigment. That is why acne in Indian skin so often leaves brown marks "
                  "that outlast the spot by months, and why sun exposure makes those marks "
                  "darker and slower to fade.",
                  "Daily broad-spectrum sunscreen is therefore not a cosmetic recommendation in "
                  "acne treatment. It is part of the treatment, and it is the step most often "
                  "skipped."],
         "cta": ("Chemical peels explained", "chemical-peels-hyderabad"),
         "items": [
             {"title": "Sunscreen is treatment",
              "body": "It prevents the marks from darkening while the acne is being brought "
                      "under control."},
             {"title": "Picking prolongs everything",
              "body": "A squeezed lesion leaves a deeper mark for longer, and is the "
                      "commonest cause of scarring in otherwise mild acne."},
         ]},

        VISIT,
    ],
    "faq_h2": "Acne questions",
    "faqs": [
        ("How long does acne treatment take to work?",
         "Eight to twelve weeks for a fair judgement. Skin often looks slightly worse in the "
         "first few weeks of a retinoid, which is expected and not a reason to stop."),
        ("Are my marks scars?",
         "Flat brown or red marks are post-inflammatory pigmentation and fade over months. "
         "Only indentations and raised areas are true scars. A great many people who believe "
         "they have scarring actually have pigmentation."),
        ("Can I have laser or peels while my acne is active?",
         "Generally no. Scar and resurfacing work is done once the acne is controlled. "
         "Otherwise new lesions keep arriving and some procedures aggravate them."),
        ("Does diet cause acne?",
         "Evidence is modest. High-glycaemic diets and, in some people, skimmed milk are "
         "associated with worse acne. Diet is not the main driver and dietary change alone "
         "is not a treatment."),
        ("Why does my acne keep coming back after antibiotics?",
         "Because antibiotics reduce inflammation but do not address the underlying follicular "
         "blockage. Maintenance treatment, usually a topical retinoid, is what prevents "
         "relapse, and it is the step most often dropped."),
        ("I'm an adult woman with new acne. Is that different?",
         "It can be. Adult-onset acne in women, especially along the jawline and with "
         "irregular cycles, warrants considering a hormonal cause. That changes the "
         "treatment."),
    ],
    "related": [
        ("chemical-peels-hyderabad", "Chemical peels",
         "For pigmentation and texture once the acne is settled."),
        ("acne-scar-treatment-hyderabad", "Acne scar treatment",
         "Subcision, TCA CROSS and resurfacing: once the acne is controlled."),
        ("skin-allergy-rashes-treatment", "Skin allergy and rashes",
         "If the breakout is not actually acne."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "dandruff-treatment", "template": "T1", "condition": "Seborrhoeic dermatitis",
    "crumbs": [("Dandruff treatment", None)],
    "title": "Dandruff & Seborrhoeic Dermatitis Treatment | Dr. Varada",
    "meta": "Dandruff and seborrhoeic dermatitis treatment in Hyderabad: why it keeps coming "
            "back, how it differs from scalp psoriasis, and the maintenance plan.",
    "eyebrow": "Hyderabad",
    "h1": "Dandruff and seborrhoeic dermatitis treatment",
    "lede": "Dandruff comes back because it is a chronic condition being treated as an acute "
            "one. Clearing it takes a fortnight. Keeping it clear takes a maintenance routine, "
            "and that is the part nobody is usually given.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["dermnet-seb-derm", "nhs-dandruff", "dermnet-scalp-psoriasis"],
    "glance": [
        ("What it is", "Inflammation with an overgrowth of Malassezia yeast"),
        ("Why it returns", "Chronic condition; needs maintenance"),
        ("Also affects", "Eyebrows, sides of nose, chest, ears"),
        ("Confused with", "Scalp psoriasis"),
        ("Hair loss", "Possible while inflamed; usually recovers"),
        ("Clearance", "1–2 weeks; maintenance ongoing"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Why it keeps returning",
         "h2": "You cleared it. You did not change the conditions.",
         "body": [
             "Seborrhoeic dermatitis is an inflammatory reaction to a yeast, Malassezia, "
             "which lives on everyone's skin and thrives where there is oil. Treating it "
             "reduces the yeast and the inflammation. Stopping treatment lets both return, "
             "because nothing about your scalp has permanently changed.",
             "That is why the intermittent pattern is so familiar: two weeks of medicated "
             "shampoo, clear scalp, back to normal shampoo, flakes return within a month. The "
             "fix is not a stronger product. It is continuing a reduced schedule, typically "
             "once or twice a week, indefinitely.",
             "It is also worth checking whether it is dandruff at all. Thick adherent "
             "silvery scale in sharply bordered patches, extending past the hairline, is "
             "scalp psoriasis and needs different treatment.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "Clear it, then hold it",
         "items": [
             {"title": "Confirm what it is",
              "body": "Seborrhoeic dermatitis, scalp psoriasis, or a fungal infection. They "
                      "look similar at a glance and are treated differently."},
             {"title": "Clear the flare",
              "body": "An antifungal shampoo (ketoconazole, zinc pyrithione or selenium), used "
                      "correctly, with a short anti-inflammatory course if the scalp is very "
                      "inflamed."},
             {"title": "Use it properly",
              "body": "Applied to the scalp, not the hair, and left for several minutes. "
                      "Most treatment failure is application failure."},
             {"title": "Drop to maintenance",
              "body": "Once or twice a week, ongoing. This is the step that decides whether "
                      "it returns."},
         ]},

        {"kind": "split", "eyebrow": "Beyond the scalp",
         "h2": "The places it goes that people don't connect.",
         "body": ["Redness and fine scaling at the sides of the nose, in the eyebrows, behind "
                  "the ears, in the beard and on the central chest are the same condition, and "
                  "are frequently treated as unrelated dry skin or as a fungal rash for months.",
                  "Recognising them as one condition simplifies treatment considerably, and "
                  "explains why the facial redness improves when the scalp is treated "
                  "properly."],
         "cta": ("If it's actually psoriasis", "psoriasis-scalp"),
         "items": [
             {"title": "Face and chest too",
              "body": "Same condition, gentler preparations. Potent steroids on the face are "
                      "not the answer."},
             {"title": "Worse in winter and stress",
              "body": "Both are recognised aggravators. Increasing maintenance frequency "
                      "before winter works better than reacting to it."},
         ]},

        VISIT,

        {"kind": "callout", "title": "Does dandruff cause hair loss?",
         "body": "Indirectly and usually temporarily. An inflamed, itchy scalp gets "
                 "scratched, and scratching sheds hair. Treating the scalp properly "
                 "generally allows it to recover. Persistent loss after the scalp is calm "
                 "needs assessing separately."},
    ],
    "faq_h2": "Dandruff questions",
    "faqs": [
        ("Why does my dandruff always come back?",
         "Because it is a chronic condition treated as an acute one. The yeast and the oily "
         "conditions it thrives in do not go away, so treatment has to continue at a reduced "
         "frequency, usually once or twice a week, rather than stopping when the flakes do."),
        ("Is it dandruff or scalp psoriasis?",
         "Psoriasis scale is thicker, silvery and stuck down, forms sharply bordered "
         "patches, and typically extends past the hairline. Dandruff is finer and more "
         "diffuse. Checking elbows, knees and nails usually settles it."),
        ("How should I use medicated shampoo?",
         "On the scalp rather than the hair, worked in with the fingertips, and left for "
         "several minutes before rinsing. Applying it like ordinary shampoo is the single "
         "commonest reason it appears not to work."),
        ("Does dandruff cause hair loss?",
         "Temporarily, mostly through scratching and inflammation. Hair generally recovers "
         "once the scalp is controlled. Loss that continues after the scalp is calm needs "
         "separate assessment."),
        ("Can I treat it with oil?",
         "Coconut and similar oils can worsen it, because Malassezia feeds on the lipids. Oil "
         "is useful only for softening thick adherent scale before washing it out. Not as a "
         "leave-in treatment."),
        ("Is it contagious?",
         "No. The yeast involved lives on everyone's skin. What differs is the inflammatory "
         "reaction to it, and that is not transmissible."),
    ],
    "related": [
        ("psoriasis-scalp", "Scalp psoriasis", "The condition it is most often confused with."),
        ("hair-loss-treatment-hyderabad", "Hair loss", "If shedding continues after the scalp settles."),
        ("eczema-atopic-dermatitis-treatment", "Eczema", "The other chronic inflammatory skin condition."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "premature-greying-treatment", "template": "T1", "condition": "Canities",
    "crumbs": [("Premature greying", None)],
    "title": "Premature Greying: Causes & Treatment | Dr. Varada",
    "meta": "Premature greying of hair: what actually causes it, which deficiencies are worth "
            "testing for, what treatment can and cannot do, and the claims to distrust.",
    "eyebrow": "Hyderabad",
    "h1": "Premature greying of hair",
    "lede": "Greying before thirty is worth investigating, because a small proportion of cases "
            "have a correctable cause. The rest are genetic, and it is more useful to be told "
            "that clearly than to be sold a treatment for it.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["aad-hair-loss", "nhs-hair-loss"],
    "glance": [
        ("Defined as", "Greying before 20 (Asian), 25 (African)"),
        ("Commonest cause", "Genetics, by a wide margin"),
        ("Worth testing", "B12, ferritin, thyroid, vitamin D"),
        ("Reversible", "Only where a deficiency is found and corrected"),
        ("Smoking", "An established, avoidable contributor"),
        ("Honest answer", "Most greying does not reverse"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What happens",
         "h2": "The pigment factory in each follicle winds down.",
         "body": [
             "Each hair follicle has its own population of pigment cells that colour the hair "
             "as it grows. Over time those cells exhaust, and hair grows without pigment. The "
             "age at which this happens is largely inherited, which is why the most informative "
             "question in the consultation is when your parents went grey.",
             "A minority of early greying has a contributing cause worth finding: vitamin "
             "B12 deficiency, iron deficiency, thyroid disease, and vitamin D deficiency all "
             "appear in the literature. Smoking is an established and avoidable "
             "contributor. Where one of these is found and corrected, some improvement is "
             "possible.",
             "Where none is found, which is the majority, the honest position is that greying "
             "does not reverse, and the useful conversation is about colouring safely and about "
             "the hair that remains. Saying so is not defeatism; it is the alternative to "
             "selling a course of treatment for a genetic trait.",
         ]},

        {"kind": "table", "eyebrow": "Assessment", "h2": "What is worth testing",
         "head": ["Test", "Why", "If abnormal"],
         "rows": [
             ["Vitamin B12", "Deficiency is associated with early greying",
              "Correct it properly; some improvement reported"],
             ["Ferritin", "Iron deficiency is common and often silent",
              "Correct and recheck: also helps hair shedding"],
             ["Thyroid function", "Both under- and overactive thyroid are associated",
              "Treat the thyroid"],
             ["Vitamin D", "Commonly deficient; association reported",
              "Correct if low"],
             ["Family history", "The strongest single predictor", "Not correctable"],
             ["Smoking history", "Established and avoidable contributor",
              "Stopping helps; it will not reverse what has greyed"],
         ],
         "note": "This is a short, targeted panel. Not a broad screen. Testing everything "
                 "generates incidental findings that lead nowhere."},

        {"kind": "split", "eyebrow": "Claims to distrust",
         "h2": "Why this condition attracts so much nonsense.",
         "body": ["Greying is visible, distressing, and has no reliable medical reversal, which "
                  "is precisely the combination that attracts unsupported claims. Oils that "
                  "'restore melanin', supplements promising reversal in weeks, and treatments "
                  "claiming to reverse genetic greying all have the same evidence base, which "
                  "is none.",
                  "The things that genuinely help are unglamorous: correct a deficiency if "
                  "you have one, stop smoking, and treat the scalp if it is inflamed. Beyond "
                  "that, colouring hair safely is a legitimate and effective answer, and it "
                  "is discussed rather than dismissed."],
         "cta": ("If hair is also thinning", "hair-loss-treatment-hyderabad"),
         "items": [
             {"title": "Plucking does not spread it",
              "body": "Removing a grey hair does not cause neighbouring hairs to grey. It "
                      "does risk damaging the follicle."},
             {"title": "Stress does not turn hair grey overnight",
              "body": "Existing hair cannot lose its pigment. What stress can do is trigger "
                      "shedding that makes existing grey more obvious."},
         ]},

        VISIT,
    ],
    "faq_h2": "Premature greying questions",
    "faqs": [
        ("Can grey hair turn black again?",
         "Only where a correctable cause is found and treated: a B12 or iron deficiency, or "
         "thyroid disease. Genetic greying does not reverse, and no treatment currently "
         "available changes that."),
        ("What deficiency causes premature greying?",
         "Vitamin B12 deficiency is the one with the clearest association. Iron deficiency, "
         "thyroid disease and vitamin D deficiency also appear in the literature. All are "
         "worth testing for once if greying began early."),
        ("Does plucking a grey hair cause more to grow?",
         "No. That is a myth. Plucking affects only that follicle, and repeated plucking can "
         "damage it."),
        ("Can stress turn hair grey?",
         "Not overnight: hair that has already grown cannot lose its colour. Severe stress can "
         "trigger shedding, which makes existing grey hairs more noticeable, and stress may "
         "contribute to the process over longer periods."),
        ("Do any oils or supplements reverse greying?",
         "None with credible evidence. Supplements help only where they correct a "
         "demonstrated deficiency. Claims of restoring pigment to genetically grey hair are "
         "not supported."),
        ("Is hair colouring safe to do regularly?",
         "For most people, yes, with sensible precautions: a patch test before first use, "
         "avoiding application to broken or inflamed scalp, and stopping if irritation "
         "develops. Allergy to hair dye is real and worth taking seriously."),
    ],
    "related": [
        ("hair-loss-treatment-hyderabad", "Hair loss treatment",
         "If thinning accompanies the greying."),
        ("dandruff-treatment", "Dandruff and scalp disease",
         "Scalp inflammation worth treating either way."),
        ("skin-allergy-rashes-treatment", "Skin allergy",
         "Including hair dye allergy, which is commoner than people expect."),
    ],
},

]
