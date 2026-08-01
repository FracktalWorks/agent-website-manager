"""Pan-India pages — the tier that reaches patients outside Telangana.

WHY THESE THREE
  The site already ranks nationally for its two flagship conditions: `/vitiligo/`
  and `/psoriasis/` are national hubs with sixteen cluster pages, two cost pages
  and four language pages behind them. Everything else was Hyderabad-scoped, so
  someone in Pune searching for alopecia universalis found nothing here at all.

  The temptation at this point is a city grid — "vitiligo treatment in Mumbai",
  "…in Delhi", forty pages of it. That is a doorway set. The clinic is not in
  Mumbai, the page would have nothing true to say about Mumbai, and for a
  medical practice it is an advertising-code problem as well as an SEO one.

  What genuinely serves a national reader is the opposite: pages about the
  things that do not depend on where they live.

    1. `online-consultation`   — the one hub for "can I be treated from here",
                                 across every condition rather than per-condition.
    2. `alopecia-areata-treatment-india` — a national hub for the condition after
                                 vitiligo that patients actually travel for.
    3. `travelling-for-treatment` — the conversion page for people who have
                                 decided to come, and need to know how.
"""

from chrome import PHONE, PHONE_SHOW, WHATSAPP

CRED = ["45 years in dermatology", "Dermatologist &amp; dermatosurgeon",
        "Consults across India by video", "Booking on WhatsApp"]

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "online-consultation", "template": "T2",
    "crumbs": [("Online consultation", None)],
    "title": "Online Dermatology Consultation Across India | Dr. Varada",
    "meta": "Video dermatology consultation anywhere in India with Dr. (Lt Col) Khagendra "
            "Varada, 45 years in practice. Diagnosis, a written plan, second opinions.",
    "eyebrow": "Anywhere in India",
    "h1": "Consult from wherever you are.",
    "lede": "A great deal of dermatology is history, pattern and photographs, which travel "
            "perfectly well over video. This page is about which parts do, which parts do not, "
            "and how to tell before you spend money finding out.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "glance": [
        ("Booking", "WhatsApp. " + PHONE_SHOW),
        ("Language", "English, Telugu, Hindi"),
        ("Good for", "Diagnosis, second opinions, plan reviews"),
        ("Not for", "Wood's lamp, dermatoscopy, any procedure"),
        ("You'll need", "Daylight photographs, prescriptions, recent bloods"),
        ("Follow-up", "On the same WhatsApp thread"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What it is",
         "h2": "Most of a dermatology consultation is not the touching.",
         "body": [
             "A skin diagnosis is built from where the rash is, what shape it takes, how it "
             "started, what it does over a week, what has already been tried and what "
             "happened when it was. Almost all of that is spoken, and the rest is visible "
             "in a photograph taken in daylight.",
             "So a video consultation is not a lesser version of the real thing for a large "
             "share of what walks into a skin clinic. It is the same consultation with two "
             "instruments missing, the Wood's lamp and the dermatoscope, and a clear answer "
             "about whether either of them would have changed the plan.",
             "Where they would, you are told to come in, or to see someone near you. Being "
             "told a video consultation is not enough for your problem is a legitimate "
             "outcome, and it is cheaper than discovering it three months later.",
         ]},

        {"kind": "table", "eyebrow": "Honestly",
         "h2": "What video settles and what it does not",
         "head": ["What you want", "Over video", "Why"],
         "rows": [
             ["A diagnosis for a rash you have had for weeks", "Usually yes",
              "History and daylight photographs carry most of it"],
             ["A second opinion on a plan you already have", "Yes",
              "The paperwork matters more than the skin here"],
             ["A vitiligo activity assessment", "Partly",
              "Spread and distribution show; a Wood's lamp does not travel"],
             ["A psoriasis flare and maintenance plan", "Yes",
              "Written plan, step-down schedule, joint questions"],
             ["Hair loss, which of the four patterns", "Usually yes",
              "Photographs, a pull test you can do, and bloods you can get locally"],
             ["Whether a mole needs removing", "No",
              "This needs dermatoscopy, in person"],
             ["Phototherapy, excimer, grafting, any procedure", "No",
              "Physical treatment; a video consult decides whether to plan one"],
         ],
         "note": "Anything in the “no” rows is still worth a video consultation first. Not to "
                 "do the procedure, but to find out whether it is the right one before you "
                 "arrange travel for it."},

        {"kind": "steps", "eyebrow": "How it runs", "h2": "Four steps, from wherever you are",
         "items": [
             {"title": "Message on WhatsApp",
              "body": "Say what you are seeing and roughly how long it has been there. "
                      "One number, answered by the clinic team."},
             {"title": "Send photographs",
              "body": "Daylight, no filter, one wide and one close for each affected area. "
                      "Add previous prescriptions and any reports."},
             {"title": "Take the consultation",
              "body": "A time is agreed and the video link comes back on the same thread. "
                      "In English, Telugu or Hindi."},
             {"title": "Get it in writing",
              "body": "Diagnosis, plan, what to expect and when to review. Sent back to you, so "
                      "the plan is not something you have to remember."},
         ]},

        {"kind": "split", "eyebrow": "Treatment where you live",
         "h2": "A plan that assumes you are in Hyderabad is no plan at all.",
         "body": ["Narrowband UVB is available in most Indian cities. Where light therapy is "
                  "the right answer and you are three states away, the useful thing is not an "
                  "appointment here: it is a written protocol you can hand to a unit near you, "
                  "with the dosing, the schedule and the review interval spelled out.",
                  "The same applies to bloods, to topicals and to systemic monitoring. "
                  "What a national consultation is for is deciding what should happen and "
                  "writing it down clearly enough that it can happen anywhere. Coming here "
                  "is reserved for the things that genuinely have to be done here."],
         "cta": ("What actually requires a visit", "travelling-for-treatment"),
         "items": [
             {"title": "Protocols travel",
              "body": "Dosing, schedule and review intervals written for another unit to "
                      "follow."},
             {"title": "Procedures do not",
              "body": "Grafting, excimer and dermatosurgery are the reasons to travel, and only "
                      "after a video assessment says so."},
         ]},

        {"kind": "callout", "warn": True, "title": "This is not an emergency service",
         "body": "For a rapidly spreading rash with fever, blistering across large areas, "
                 "or swelling of the lips or tongue, go to a hospital emergency department "
                 "now. Do not wait for a video appointment."},
    ],
    "faq_h2": "Consulting online",
    "faqs": [
        ("How do I book an online consultation?",
         "Message the clinic on WhatsApp at " + PHONE_SHOW + ". Say what you are seeing, "
         "attach photographs if you have them, and the team confirm a time and send the "
         "video link back on the same thread."),
        ("Which conditions can be handled over video?",
         "Vitiligo, psoriasis, eczema, acne, skin allergies and hair loss are all commonly "
         "managed this way, for diagnosis, for a plan, and for second opinions. Anything "
         "needing dermatoscopy or a procedure needs a visit."),
        ("Can I get a prescription after a video consultation?",
         "Yes, where an examination is not required to reach the diagnosis. Nothing is "
         "prescribed without a consultation, and a repeat prescription for an existing plan "
         "is still a review rather than a rubber stamp."),
        ("Which languages can I consult in?",
         "English, Telugu or Hindi. Say which you prefer when you message."),
        ("I live outside India. Can I still consult?",
         "Photographs and a written opinion, yes. Anything that needs a procedure or "
         "ongoing supervised therapy is better arranged with a dermatologist you can "
         "physically reach."),
        ("What if the video consultation says I need to come in?",
         "Then you have saved yourself the risk of coming in for the wrong thing. You will "
         "be told what the visit is for, what it involves and roughly what it costs before "
         "you arrange anything."),
    ],
    "related": [
        ("vitiligo-online-consultation", "Online vitiligo consultation",
         "How a video consultation for vitiligo works, and what it can settle."),
        ("psoriasis-online-consultation", "Online psoriasis consultation",
         "Flare plans, systemic reviews and second opinions, over video."),
        ("travelling-for-treatment", "Coming to Hyderabad for treatment",
         "The staged visit, what to send first, and how long to allow."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "alopecia-areata-treatment-india", "template": "T2",
    "condition": "Alopecia areata",
    "crumbs": [("Alopecia areata", None)],
    "title": "Alopecia Areata, Totalis & Universalis | Dr. Varada",
    "meta": "Alopecia areata, totalis and universalis: why it happens, what regrowth "
            "realistically looks like, and which treatments are worth trying at each stage.",
    "eyebrow": "Across India",
    "h1": "Alopecia areata, totalis and universalis",
    "lede": "An autoimmune condition, not a hair-care failure. The follicle is switched off "
            "rather than destroyed, which is why regrowth remains possible years in, and why "
            "nobody can promise you when.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Consult online", "online-consultation")],
    "creds": CRED,
    "sources": ["niams-alopecia-areata", "dermnet-alopecia-areata", "aad-hair-loss"],
    "glance": [
        ("What it is", "Autoimmune, non-scarring hair loss"),
        ("Follicle", "Switched off, not destroyed"),
        ("Patchy", "Alopecia areata"),
        ("Whole scalp", "Alopecia totalis"),
        ("Whole body", "Alopecia universalis"),
        ("Curable", "No, but regrowth is common and can be substantial"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What is happening",
         "h2": "The follicle is asleep, not gone.",
         "body": [
             "In alopecia areata the immune system attacks the hair follicle and stops it "
             "producing a shaft. It does not scar it. That distinction is the single most "
             "important fact about this condition, because it means the machinery is still "
             "there, and regrowth remains biologically possible even after years without hair.",
             "It also explains the shape of the disease. Round, sharply defined patches "
             "with normal skin inside. Sometimes short broken hairs at the edge. Often "
             "pitting or ridging of the nails, which is the clue that most reliably "
             "separates it from the other causes of a bald patch.",
             "Where it spreads to the whole scalp it is called alopecia totalis; where it takes "
             "body hair, eyebrows and lashes too, alopecia universalis. Those are the same "
             "disease at greater extent, not different diseases, but they behave less "
             "predictably and they are harder to treat.",
         ]},

        {"kind": "table", "eyebrow": "By extent",
         "h2": "What is usually tried, and when",
         "head": ["Presentation", "Commonly used", "What to expect"],
         "rows": [
             ["A few small patches", "Topical or intralesional steroid",
              "Many regrow, some without treatment at all"],
             ["Multiple or enlarging patches", "Intralesional steroid, topical immunotherapy",
              "Slower; may need several cycles"],
             ["Rapidly spreading disease", "Systemic therapy under supervision",
              "Aimed at halting progression first"],
             ["Alopecia totalis", "Systemic therapy, immunotherapy",
              "Less predictable; response varies widely"],
             ["Alopecia universalis", "Systemic therapy, immunotherapy",
              "The hardest group; honest expectation-setting matters most here"],
             ["Eyebrows and lashes", "Site-specific treatment",
              "Often treated alongside, not after"],
         ],
         "note": "Which of these applies to you is a clinical decision after examination, and "
                 "several carry monitoring requirements. Nothing on this page is a "
                 "prescription. It is what the options are, so you can ask about yours."},

        {"kind": "split", "eyebrow": "The honest part",
         "h2": "Nobody can tell you when it will regrow.",
         "body": ["Alopecia areata relapses and remits on its own. A patch can regrow "
                  "during treatment that did nothing, and a treatment that worked once can "
                  "do nothing the next time. That unpredictability is the disease, not a "
                  "failure of the doctor, and it is why any clinic quoting you a timeline "
                  "for regrowth is quoting a number it does not have.",
                  "What can honestly be offered is this: an accurate diagnosis, the "
                  "treatment appropriate to your extent and rate of spread, screening for "
                  "the thyroid and other autoimmune conditions that travel with it, and a "
                  "review schedule that changes the plan when it is not working rather "
                  "than continuing it out of momentum."],
         "cta": ("How a video consultation works", "online-consultation"),
         "items": [
             {"title": "Extent and speed guide treatment",
              "body": "A few stable patches and rapidly spreading disease are not the "
                      "same problem and are not treated the same way."},
             {"title": "Screened alongside",
              "body": "Thyroid disease, vitiligo and other autoimmune conditions occur "
                      "together often enough to be looked for."},
         ]},

        {"kind": "checklist", "eyebrow": "Bring or send",
         "h2": "What makes a first alopecia consultation useful.",
         "items": [
             "<b>Photographs</b> of every patch, in daylight, with a size reference",
             "<b>When it started</b> and whether it has spread since",
             "<b>Your nails</b>: photograph them; pitting is diagnostic information",
             "<b>Previous treatment</b>, with dates and what happened",
             "<b>Thyroid results</b> if you have had them",
             "<b>Family history</b> of autoimmune conditions",
         ]},

        {"kind": "callout", "title": "Patients travel for this, and often do not need to",
         "body": "Alopecia areata is one of the conditions best suited to a first "
                 "consultation over video: the diagnosis is largely visual, the bloods can "
                 "be done locally, and much of the treatment can be supervised remotely. "
                 "Send photographs on WhatsApp before you plan a journey."},
    ],
    "faq_h2": "Alopecia areata",
    "faqs": [
        ("Can alopecia areata be cured?",
         "No. It is an autoimmune condition that relapses and remits, and no treatment "
         "removes that tendency. What treatment does is encourage regrowth and, in rapidly "
         "spreading disease, try to halt the spread. Many people regrow substantially; some "
         "do not, and that is said plainly rather than left to be discovered."),
        ("Will my hair grow back?",
         "It may: the follicle is not destroyed, so regrowth stays possible even after years. "
         "Nobody can tell you when, or how completely, and a clinic that offers you a timeline "
         "is offering a number it does not have."),
        ("What is the difference between areata, totalis and universalis?",
         "Extent. Areata is patchy loss; totalis is the whole scalp; universalis is scalp "
         "and body hair including eyebrows and lashes. Same disease, greater extent, less "
         "predictable behaviour."),
        ("Is it caused by stress?",
         "Stress is reported as a trigger by many patients and may contribute, but alopecia "
         "areata is an autoimmune condition with a genetic component. It is not caused by "
         "poor hair care, oil, shampoo or diet."),
        ("Is it contagious?",
         "No. It cannot be passed to anyone by contact of any kind."),
        ("Can I be treated for this from outside Hyderabad?",
         "Often, yes. The diagnosis is largely visual, bloods can be done locally, and much "
         "of the treatment can be supervised over video with reviews on WhatsApp. Send "
         "photographs first and you will be told whether a visit adds anything."),
    ],
    "related": [
        ("alopecia-treatment-hyderabad", "Alopecia treatment in Hyderabad",
         "The same condition, written for patients who can come to the clinic."),
        ("hair-loss-treatment-hyderabad", "Hair loss: the four patterns",
         "Telling alopecia areata apart from the other causes of shedding."),
        ("online-consultation", "Consult online from anywhere in India",
         "What a video consultation settles, and what it cannot."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "travelling-for-treatment", "template": "T2",
    "crumbs": [("Travelling for treatment", None)],
    "title": "Travelling to Hyderabad for Skin Treatment | Dr. Varada",
    "meta": "Coming to Hyderabad from another state for vitiligo surgery: what to send before "
            "booking, how a staged visit works, and why a video consult comes first.",
    "eyebrow": "From outside Telangana",
    "h1": "Before you book the ticket.",
    "lede": "Patients travel here mainly for vitiligo surgery, which comparatively few centres "
            "in India perform. This page exists so the journey is made by people for whom it is "
            "worth making, and skipped by the people for whom it is not.",
    "acts": [("Send photographs on WhatsApp", WHATSAPP),
             ("Consult online first", "online-consultation")],
    "creds": CRED,
    "glance": [
        ("The clinic", "Karkhana, Secunderabad, Telangana"),
        ("Travel for", "Grafting, excimer, dermatosurgery"),
        ("Don't travel for", "What a video consultation can settle"),
        ("First step", "Photographs on WhatsApp. " + PHONE_SHOW),
        ("Typical answer", "Sometimes “wait”: that is a clinical answer"),
        ("Allow for", "A staged visit, not a single day"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Start here",
         "h2": "The commonest wasted journey is the avoidable one.",
         "body": [
             "Surgical repigmentation only works on vitiligo that has been stable for roughly "
             "twelve months: no new patches, no existing ones enlarging. A significant "
             "proportion of the people who ask about grafting are told to wait, because their "
             "disease is still active and operating on it would fail.",
             "That answer costs nothing to receive from home and a great deal to receive after "
             "a flight. So the sequence is: photographs on WhatsApp, then a video consultation, "
             "then travel, in that order, and only if the first two say the trip is warranted.",
             "The same logic applies to every procedure. A video consultation cannot do "
             "dermatoscopy or hold a Wood's lamp, but it can nearly always tell you whether "
             "the thing you are travelling for is the thing you need.",
         ]},

        {"kind": "steps", "eyebrow": "The sequence", "h2": "How a visit from out of state works",
         "items": [
             {"title": "Send photographs",
              "body": "Daylight, no filter, one wide and one close of each area, plus any "
                      "previous prescriptions and reports. On WhatsApp."},
             {"title": "Take a video consultation",
              "body": "Diagnosis, whether the procedure suits your case, a realistic timeline, "
                      "and an approximate cost, before anything is booked."},
             {"title": "Come for the assessment and the procedure",
              "body": "Usually the same visit where the video consultation has already "
                      "settled the diagnosis. Allow more than a single day."},
             {"title": "Review, some of it from home",
              "body": "The early review is in person; later ones are frequently done over "
                      "video with photographs, so a second journey is often unnecessary."},
         ]},

        {"kind": "checklist", "eyebrow": "Send before you book",
         "h2": "What makes the answer reliable.",
         "items": [
             "<b>Photographs in daylight</b>: no filter, no flash, a coin for scale",
             "<b>When each patch appeared</b> and whether any are still growing",
             "<b>Every treatment tried</b>, with dates and what happened",
             "<b>Reports</b>: biopsy, thyroid, blood work",
             "<b>Which city you are travelling from</b>, so the visit can be staged sensibly",
             "<b>Your dates</b>, so you are not told to wait after you have booked",
         ]},

        {"kind": "split", "eyebrow": "What is worth the journey",
         "h2": "Procedures travel. Prescriptions do not.",
         "body": ["Melanocyte transplant, punch and blister grafting, excimer, "
                  "phototherapy and the dermatosurgery list are physical treatments done in "
                  "one place. Vitiligo surgery in particular is offered at comparatively "
                  "few centres in India, and that is the honest reason patients come from "
                  "outside the state.",
                  "Almost everything else: a diagnosis, a written plan, a second opinion, a "
                  "systemic therapy review, arranging phototherapy at a unit near your home. Is "
                  "better done over video, because it produces the same result without a "
                  "journey. You will be steered towards whichever of those two your case "
                  "actually calls for."],
         "cta": ("How graft surgery works", "vitiligo-graft-surgery"),
         "items": [
             {"title": "Worth travelling for",
              "body": "Grafting and melanocyte transplant, excimer where no local unit "
                      "exists, dermatosurgery."},
             {"title": "Not worth travelling for",
              "body": "A diagnosis, a plan, a second opinion, a prescription review. All "
                      "of those work over video."},
         ]},

        {"kind": "callout", "title": "“Wait” is the most useful answer we give",
         "body": "Surgery on unstable vitiligo fails, and the graft is wasted along with the "
                 "trip. Being told to come back in six months is a clinical judgement, not a "
                 "scheduling one, and it is the reason to ask before you travel rather than "
                 "after."},
    ],
    "faq_h2": "Travelling for treatment",
    "faqs": [
        ("How long should I allow for a visit?",
         "More than a single day. Assessment and procedure can often be arranged close "
         "together where a video consultation has already settled the diagnosis, but an "
         "early review follows the procedure and it is better not to fly the same evening."),
        ("Will I definitely be offered surgery if I travel?",
         "No, and that is the point of sending photographs first. Grafting needs disease "
         "that has been stable for about twelve months; a significant proportion of people "
         "who ask are told to wait. Hearing that from home costs nothing."),
        ("Can the follow-up be done from my own city?",
         "Much of it, yes. The early review is in person; later reviews are frequently done "
         "over video with photographs on the same WhatsApp thread."),
        ("Where exactly would I be coming to?",
         "Plot No D13B, Wellington Rd, Vikrampuri Colony, Karkhana, Secunderabad, Telangana "
         "500009. The practice formerly known as BNR Skin & Vitiligo Hospital."),
        ("Do you help with accommodation?",
         "Not directly, but the clinic team will tell you how many days to plan for and "
         "roughly when in the visit each stage falls, which is what you need in order to "
         "book sensibly."),
        ("What does it cost?",
         "Costs are quoted in writing after the assessment, because the number of grafts or "
         "sessions is not knowable before it. A video consultation gives you an approximate "
         "range so you can plan before you travel."),
    ],
    "related": [
        ("vitiligo-graft-surgery", "Vitiligo graft surgery",
         "Who qualifies, the three techniques, and what recovery involves."),
        ("online-consultation", "Consult online from anywhere in India",
         "The step that should come before any travel is booked."),
        ("areas-we-serve", "Areas we serve",
         "Where patients travel from, and what each distance means in practice."),
    ],
},

]
