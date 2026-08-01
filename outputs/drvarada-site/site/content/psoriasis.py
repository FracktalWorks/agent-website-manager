"""T2 — the pan-India psoriasis hub and its cluster.

Same rules as the vitiligo section: no city qualifier, education-first, funnelling to
online consultation, and no cure claims. Psoriasis is described as controllable and
remitting — which is both compliant and clinically correct.

One extra duty on these pages: psoriatic arthritis red flags. Joint damage is
irreversible and joint symptoms are routinely dismissed as unrelated, so every
relevant page carries the warning rather than hiding it on one.
"""

from chrome import PHONE, WHATSAPP

CROSS = ("psoriasis-treatment-hyderabad", "Psoriasis treatment in Hyderabad",
         "If you can reach the clinic: phototherapy, systemics and regular review.")
ONLINE = ("psoriasis-online-consultation", "Consult online from anywhere in India",
          "Second opinions, flare plans and systemic-therapy counselling by video.")

ARTHRITIS = {
    "kind": "callout", "warn": True,
    "title": "Joint pain with psoriasis is not a coincidence",
    "body": "Up to a third of people with psoriasis develop psoriatic arthritis, and the "
            "joint damage it causes does not reverse. Morning stiffness lasting over "
            "30 minutes, a swollen finger or toe, heel pain, or low back pain that improves "
            "with movement all need reporting. Early treatment protects the joint.",
}

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis", "template": "T2", "condition": "Psoriasis",
    "crumbs": [("Psoriasis", None)],
    "title": "Psoriasis Treatment in India: Types & Control | Dr. Varada",
    "meta": "Psoriasis treatment by a dermatologist of 45 years: the types, what triggers "
            "flares, which treatments control it, and when biologics are appropriate.",
    "eyebrow": "The psoriasis section",
    "h1": "Psoriasis, and how it is actually controlled.",
    "lede": "Psoriasis is not a skin infection, not contagious, and not curable. It is an "
            "immune condition that flares and settles, and the aim of good treatment is a "
            "longer gap between flares, not a photograph of clear skin taken once.",
    "acts": [("Consult online", WHATSAPP), ("Call the clinic", PHONE)],
    "sources": ["niams-psoriasis", "aad-psoriasis", "dermnet-psoriasis", "nice-psoriasis", "who-psoriasis", "npf"],
    "glance": [
        ("What it is", "An immune-driven inflammatory skin disease"),
        ("Curable", "No, but often well controlled"),
        ("Course", "Flares and remissions over years"),
        ("Main treatments", "Topicals, phototherapy, systemics, biologics"),
        ("Watch for", "Joint pain: psoriatic arthritis"),
        ("Associated with", "Metabolic and cardiovascular risk"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What it is",
         "h2": "Skin cells made too fast, because the immune system said so.",
         "body": [
             "In normal skin, a cell takes around four weeks to travel from the base of the "
             "epidermis to the surface and shed. In psoriasis that journey takes a few days. "
             "The cells pile up before they mature, and the result is the thickened, "
             "silvery-scaled plaque that gives the disease its appearance.",
             "The acceleration is driven by the immune system: specific inflammatory signals, "
             "which is precisely why the newer treatments that block those signals work so "
             "well. It is not an infection, it is not caused by poor hygiene, and it cannot be "
             "caught from anyone.",
             "It is also more than a skin disease. Psoriasis carries a meaningful "
             "association with joint disease, with metabolic syndrome, and with "
             "cardiovascular risk. A consultation that only looks at the plaques is an "
             "incomplete consultation.",
         ]},

        ARTHRITIS,

        {"kind": "cards", "eyebrow": "The shapes it takes", "h2": "Types you may be told you have",
         "accent": "chronic",
         "items": [
             {"eyebrow": "Most common", "title": "Plaque psoriasis",
              "body": "Well-defined raised plaques with silvery scale, classically on "
                      "elbows, knees, the lower back and the scalp.",
              "list": ["Around 80–90% of cases", "Symmetrical",
                       "Responds to topicals and light"]},
             {"eyebrow": "Often first", "title": "Guttate psoriasis",
              "body": "Sudden crops of small drop-like spots across the trunk, frequently "
                      "two to three weeks after a throat infection.",
              "list": ["Common in children and young adults",
                       "May resolve entirely", "Responds well to phototherapy"]},
             {"eyebrow": "Easily missed", "title": "Inverse and nail psoriasis",
              "body": "Smooth red areas in body folds without obvious scale; pitting, "
                      "thickening or lifting of the nails.",
              "list": ["Frequently misdiagnosed as fungal",
                       "Nail disease predicts joint disease",
                       "Needs a different treatment approach"]},
         ]},

        {"kind": "table", "eyebrow": "Treatment", "h2": "The ladder, and where you enter it",
         "intro": "Treatment is chosen by how much skin is involved and how much the disease is "
                  "affecting your life. Not by how it looks in a photograph.",
         "head": ["Treatment", "What it does", "Typically for"],
         "rows": [
             ["Emollients", "Reduces scale, cracking and itch", "Everyone, always, alongside"],
             ["Topical steroids", "Suppresses local inflammation", "Limited plaque disease"],
             ["Vitamin D analogues", "Slows the cell turnover", "Maintenance; steroid-sparing"],
             ["Coal tar / salicylic acid", "Descaling; long-established", "Scalp and thick plaques"],
             ["NB-UVB phototherapy", "Damps the immune response in skin",
              "Widespread disease; guttate"],
             ["Methotrexate", "Systemic immune suppression", "Extensive or resistant disease"],
             ["Other systemics", "Ciclosporin, acitretin, apremilast",
              "Where methotrexate is unsuitable"],
             ["Biologics", "Blocks a specific inflammatory signal",
              "Severe disease; failed systemics"],
         ],
         "note": "Nothing on this list cures psoriasis. Each moves the disease toward "
                 "remission and holds it there, and most patients change rungs over their "
                 "lifetime."},

        {"kind": "split", "eyebrow": "The honest framing",
         "h2": "Clearance is easy. Staying clear is the work.",
         "body": ["Almost any potent treatment will clear a plaque. Steroids clear plaques. The "
                  "question that separates good psoriasis care from bad is what happens in "
                  "month four, whether the disease is quietly rebounding because a strong "
                  "topical was used for too long without a maintenance plan.",
                  "So treatment here is written as a sequence: what clears the flare, what "
                  "holds it, when to step down, and what to do at the first sign of the "
                  "next one. Patients who have that written down flare less."],
         "cta": ("What triggers a flare", "psoriasis-triggers-and-diet"),
         "items": [
             {"title": "Step down, don't stop",
              "body": "Abruptly stopping a potent steroid is one of the commonest causes of "
                      "a rebound flare, sometimes worse than the original."},
             {"title": "A written flare plan",
              "body": "What to start, at what point, and when to call. It turns a three-week "
                      "flare into a three-day one."},
         ]},

        {"kind": "checklist", "eyebrow": "Beyond the skin",
         "h2": "What a proper psoriasis review checks.",
         "items": [
             "<b>Joints</b>: stiffness, swelling, heel and back pain",
             "<b>Nails</b>: pitting and lifting predict joint disease",
             "<b>Blood pressure, sugar and lipids</b>: the metabolic association",
             "<b>Weight</b>: it changes how well treatment works",
             "<b>Alcohol and smoking</b>: both worsen disease and limit drug choice",
             "<b>Mood</b>: psoriasis carries a real burden and it is asked about",
         ]},

        {"kind": "cards", "eyebrow": "Read next", "h2": "The rest of this section",
         "items": [
             {"title": "Understanding it",
              "list": ["Types of psoriasis in detail",
                       "Scalp psoriasis, and telling it from dandruff",
                       "Triggers and diet"]},
             {"title": "The treatments",
              "list": ["Phototherapy for psoriasis",
                       "Methotrexate, systemics and biologics"]},
             {"title": "Practical",
              "list": ["What treatment costs",
                       "Online consultation across India",
                       "Psoriasis treatment in Hyderabad"]},
         ]},
    ],
    "faq_h2": "Psoriasis questions",
    "faqs": [
        ("Can psoriasis be cured?",
         ["No. Psoriasis is a long-term immune condition, and no treatment available cures "
          "it. Any clinic offering a permanent cure is making a claim it cannot support.",
          "What treatment does achieve, often very well, is remission: skin that is clear or "
          "nearly clear, held there with maintenance, sometimes for years at a time."]),
        ("Is psoriasis contagious?",
         "No. It cannot be caught by touch, by sharing a towel or a swimming pool, or by any "
         "other contact. It is an immune condition, not an infection."),
        ("What triggers a psoriasis flare?",
         "The commonest are throat infections, stress, stopping a treatment abruptly, skin "
         "injury, certain medications including some blood pressure and antimalarial drugs, "
         "smoking and heavy alcohol use. Cold dry weather worsens many people's disease."),
        ("Does diet affect psoriasis?",
         "There is no psoriasis diet that clears the disease. What does have evidence is "
         "that losing excess weight improves both the psoriasis and how well treatment "
         "works, and that heavy alcohol use makes disease worse and limits drug choices."),
        ("Will I need lifelong treatment?",
         "Not necessarily continuous treatment, but lifelong awareness. Many patients cycle "
         "between active treatment during flares and maintenance or nothing in between. The "
         "aim is longer gaps, not a permanent prescription."),
        ("Is psoriasis linked to other health problems?",
         "Yes. Psoriatic arthritis affects up to a third of patients. There are also "
         "recognised associations with metabolic syndrome, fatty liver and cardiovascular "
         "risk, which is why blood pressure, sugar and lipids are checked."),
        ("Is scalp psoriasis the same as dandruff?",
         "No, although they are constantly confused. Scalp psoriasis has thicker, adherent "
         "silvery scale, often extends past the hairline, and does not respond to ordinary "
         "anti-dandruff shampoo alone."),
    ],
    "related": [CROSS, ONLINE,
                ("psoriasis-cost", "What psoriasis treatment costs",
                 "Topicals, light, systemics and biologics: how each is priced.")],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-types", "template": "T2", "condition": "Psoriasis",
    "crumbs": [("Psoriasis", "psoriasis"), ("Types", None)],
    "title": "Types of Psoriasis: Plaque, Scalp, Guttate | Dr. Varada",
    "meta": "The types of psoriasis and how they differ: plaque, guttate, inverse, nail, "
            "palmoplantar, erythrodermic and pustular.",
    "eyebrow": "Psoriasis",
    "h1": "Types of psoriasis",
    "lede": "The type is not a label. It changes the treatment. Guttate disease often clears "
            "completely with light; inverse disease is ruined by the same treatment that helps "
            "plaques; pustular disease can be a medical emergency.",
    "acts": [("Consult online", WHATSAPP), ("Back to the psoriasis hub", "psoriasis")],
    "sources": ["dermnet-psoriasis", "niams-psoriasis", "aad-psoriasis", "dermnet-psa"],
    "glance": [
        ("Plaque", "80–90% of all psoriasis"),
        ("Guttate", "Post-infection; may fully resolve"),
        ("Inverse", "In folds; misdiagnosed as fungal"),
        ("Nail", "Predicts psoriatic arthritis"),
        ("Palmoplantar", "Disabling out of proportion to area"),
        ("Erythrodermic / pustular", "Urgent: needs same-day care"),
    ],
    "sections": [
        {"kind": "cards", "eyebrow": "The common ones", "h2": "What you are most likely to have",
         "accent": "chronic",
         "items": [
             {"eyebrow": "Plaque", "title": "Psoriasis vulgaris",
              "body": "Raised, sharply bordered plaques with silvery scale. Elbows, knees, "
                      "lower back and scalp are classic sites, usually symmetrically.",
              "list": ["Scale lifts to leave pinpoint bleeding",
                       "Often itchy, sometimes painful when cracked",
                       "Responds to topicals, light and systemics"]},
             {"eyebrow": "Guttate", "title": "Drop-like psoriasis",
              "body": "A sudden shower of small spots across the trunk and limbs, typically "
                      "one to three weeks after a streptococcal throat infection.",
              "list": ["Most common in children and young adults",
                       "Often the first-ever episode",
                       "Frequently clears entirely with phototherapy"]},
             {"eyebrow": "Inverse", "title": "Flexural psoriasis",
              "body": "Smooth, shiny red areas in the armpits, groin, under the breasts and "
                      "between the buttocks. Little or no scale, because the fold keeps it "
                      "moist.",
              "list": ["Regularly misdiagnosed as a fungal infection",
                       "Potent steroids are harmful here",
                       "Needs low-potency or steroid-sparing agents"]},
         ]},

        {"kind": "table", "eyebrow": "Less common but important",
         "h2": "The types that change management most",
         "head": ["Type", "What it looks like", "Why it matters"],
         "rows": [
             ["Nail psoriasis", "Pitting, oil-drop discolouration, lifting, crumbling",
              "Strongly associated with psoriatic arthritis; treat and screen"],
             ["Scalp psoriasis", "Thick adherent scale, often past the hairline",
              "Very common; needs descaling before anything else will penetrate"],
             ["Palmoplantar", "Thickened, fissured palms and soles",
              "Small area, large disability: affects work and walking"],
             ["Pustular (localised)", "Sterile pustules on palms or soles",
              "Not infection; often linked to smoking"],
             ["Generalised pustular", "Widespread pustules with fever and malaise",
              "A medical emergency: same-day assessment"],
             ["Erythrodermic", "Redness and scaling over most of the body",
              "Emergency: risk of fluid, temperature and infection problems"],
         ],
         "note": "The last two rows are the reason this page names them. Both are "
                 "uncommon, both can follow abrupt withdrawal of oral steroids, and both "
                 "need urgent care rather than a routine appointment."},

        {"kind": "split", "eyebrow": "Getting it right",
         "h2": "Why the wrong label leads to the wrong cream.",
         "body": ["Inverse psoriasis treated as a fungal infection gets antifungals for "
                  "months and does not improve. Nail psoriasis treated as onychomycosis gets "
                  "oral antifungals with liver monitoring for a disease it does not have. "
                  "Scalp psoriasis treated as dandruff gets a shampoo that cannot penetrate "
                  "the scale.",
                  "All three are ordinary, frequent errors, and all three are settled by "
                  "examination, looking for psoriasis elsewhere on the body, checking the "
                  "nails, and looking at the scale rather than the redness."],
         "cta": ("Telling scalp psoriasis from dandruff", "psoriasis-scalp"),
         "items": [
             {"title": "Check the nails, always",
              "body": "Nail changes in someone with an unclear rash frequently settle the "
                      "diagnosis, and flag arthritis risk at the same time."},
             {"title": "Check the whole skin",
              "body": "A single confusing patch in a fold is much easier to name when there "
                      "are typical plaques on the elbows."},
         ]},

        ARTHRITIS,
    ],
    "faq_h2": "About the types",
    "faqs": [
        ("Can I have more than one type at once?",
         "Yes, and it is common. Plaque psoriasis with scalp and nail involvement is probably "
         "the most frequent combination seen in clinic."),
        ("Does guttate psoriasis become plaque psoriasis?",
         "Sometimes. Many first episodes clear completely and never return. A proportion of "
         "people go on to develop chronic plaque disease later, but a single guttate episode "
         "is not a guarantee of that."),
        ("Why does my psoriasis have no scale?",
         "Most likely because it is in a body fold. Inverse psoriasis stays moist, so it looks "
         "smooth and red rather than silvery, and is often mistaken for a fungal infection as a "
         "result."),
        ("Is nail psoriasis treatable?",
         "Yes, though it is slow because nails grow slowly. Expect to judge results over six to "
         "twelve months. It matters beyond appearance, because nail disease is associated with "
         "psoriatic arthritis."),
        ("What makes psoriasis an emergency?",
         "Redness and scaling covering most of the body, or widespread pustules with fever "
         "and feeling unwell. Both need same-day medical assessment rather than a routine "
         "clinic appointment."),
    ],
    "related": [
        ("psoriasis-scalp", "Scalp psoriasis", "The commonest site, and the commonest confusion."),
        ("psoriasis-triggers-and-diet", "Triggers and diet", "Including the throat infection link."),
        ("psoriasis-biologics", "Systemics and biologics", "When topical treatment is not enough."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-scalp", "template": "T2", "condition": "Scalp psoriasis",
    "crumbs": [("Psoriasis", "psoriasis"), ("Scalp", None)],
    "title": "Scalp Psoriasis or Dandruff? | Dr. Varada",
    "meta": "Scalp psoriasis: how to tell it from dandruff and seborrhoeic dermatitis, why "
            "ordinary shampoo fails, the descale-then-treat sequence, and hair loss.",
    "eyebrow": "Psoriasis",
    "h1": "Scalp psoriasis",
    "lede": "The scalp is the commonest site of psoriasis and the one most often treated "
            "wrongly, because thick adherent scale blocks every medicine applied on top of it. "
            "The order of treatment matters more than the choice of it.",
    "acts": [("Consult online", WHATSAPP), ("Back to the psoriasis hub", "psoriasis")],
    "sources": ["dermnet-scalp-psoriasis", "aad-psoriasis", "nice-psoriasis", "dermnet-seb-derm"],
    "glance": [
        ("How common", "Affects around half of psoriasis patients"),
        ("Key sign", "Scale extending past the hairline"),
        ("Confused with", "Dandruff, seborrhoeic dermatitis"),
        ("First step", "Descale: nothing works through scale"),
        ("Hair loss", "Usually temporary, from scratching and picking"),
        ("Review", "6–8 weeks"),
    ],
    "sections": [
        {"kind": "table", "eyebrow": "Telling them apart",
         "h2": "Scalp psoriasis or dandruff?",
         "intro": "These are treated differently, and the distinction is usually visible "
                  "without any test at all.",
         "head": ["", "Scalp psoriasis", "Dandruff / seborrhoeic dermatitis"],
         "rows": [
             ["Scale", "Thick, silvery, adherent", "Fine, white or greasy, loose"],
             ["Border", "Sharply defined patches", "Diffuse, ill-defined"],
             ["Hairline", "Extends onto forehead, behind ears, nape", "Usually stops at hairline"],
             ["Feel", "Raised, lumpy to the fingertips", "Flat"],
             ["Elsewhere", "Often plaques on elbows, knees; nail pitting", "Face, eyebrows, chest"],
             ["Response to anti-dandruff shampoo", "Partial at best", "Usually good"],
         ],
         "note": "The two can coexist. 'Sebopsoriasis' is a genuine overlap. Where it is "
                 "unclear, the elbows, knees and nails usually settle it."},

        {"kind": "steps", "eyebrow": "The sequence", "h2": "Descale first, then treat",
         "items": [
             {"title": "Soften the scale",
              "body": "A salicylic acid or oil-based preparation applied to the scalp and left "
                      "on, often overnight, to lift adherent scale. This step is skipped "
                      "constantly and is why treatments 'don't work'."},
             {"title": "Wash it out properly",
              "body": "A tar or ketoconazole shampoo, worked into the scalp rather than the "
                      "hair, and left for several minutes before rinsing."},
             {"title": "Now apply the active treatment",
              "body": "A steroid or vitamin D scalp application, which can finally reach skin "
                      "instead of sitting on scale."},
             {"title": "Step down to maintenance",
              "body": "Reduce frequency once controlled rather than stopping. Abrupt "
                      "stopping is the commonest cause of a rebound."},
         ]},

        {"kind": "split", "eyebrow": "Hair",
         "h2": "Does scalp psoriasis cause hair loss?",
         "body": ["Usually yes, temporarily, and usually not because of the psoriasis itself. "
                  "Hair is lost from scratching, from picking scale off (which pulls hairs with "
                  "it), and from the inflammation of a severe flare. It regrows once the scalp "
                  "settles.",
                  "Permanent loss is uncommon and results from prolonged severe inflammation or "
                  "repeated trauma to the same area. The practical message is not to pick the "
                  "scale. Soften it and let it come away."],
         "cta": ("If hair loss persists", "hair-loss-treatment-hyderabad"),
         "items": [
             {"title": "Don't pick, soften",
              "body": "Scale removed by force takes hair with it. Oil, soften, and let it "
                      "lift."},
             {"title": "Regrowth follows control",
              "body": "Hair generally returns within months once the scalp is quiet. If it "
                      "does not, it is assessed separately."},
         ]},

        {"kind": "checklist", "eyebrow": "Practical",
         "h2": "What makes scalp treatment actually work.",
         "items": [
             "<b>Treat the scalp, not the hair</b>: part it and apply to skin",
             "<b>Give it contact time</b>: minutes, not a rinse",
             "<b>Overnight oil</b> before wash days during a flare",
             "<b>Don't stop abruptly</b>: step down the frequency",
             "<b>Behind the ears and nape</b> are missed constantly",
             "<b>Colouring hair</b> is fine when the scalp is calm, not during a flare",
         ]},

        ARTHRITIS,
    ],
    "faq_h2": "Scalp psoriasis",
    "faqs": [
        ("How do I know if it's psoriasis or dandruff?",
         "Psoriasis scale is thicker, silvery and stuck down, forms sharply bordered "
         "patches, and typically extends past the hairline onto the forehead, behind the "
         "ears or down the nape. Dandruff is finer, looser and stops at the hairline."),
        ("Why doesn't anti-dandruff shampoo work on it?",
         "Partly because the active ingredient cannot penetrate thick adherent scale, and "
         "partly because psoriasis is a different disease. Descaling first is what makes "
         "subsequent treatment effective."),
        ("Will my hair grow back?",
         "In almost all cases, yes. Hair loss in scalp psoriasis is usually from scratching "
         "and picking rather than the disease destroying follicles, and it regrows once the "
         "scalp is controlled."),
        ("Can I colour or chemically treat my hair?",
         "When the scalp is calm, generally yes. During an active flare, colouring and chemical "
         "straightening will sting on cracked skin and can aggravate it. Wait until it settles."),
        ("Is scalp psoriasis a sign of worse disease elsewhere?",
         "Not necessarily, but it is worth a full skin and nail examination. Nail pitting in "
         "particular matters, because nail involvement is associated with psoriatic "
         "arthritis."),
    ],
    "related": [
        ("dandruff-treatment", "Dandruff treatment", "If it turns out to be seborrhoeic dermatitis."),
        ("psoriasis-types", "Types of psoriasis", "Where scalp disease fits."),
        CROSS,
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-triggers-and-diet", "template": "T2", "condition": "Psoriasis",
    "crumbs": [("Psoriasis", "psoriasis"), ("Triggers and diet", None)],
    "title": "Psoriasis Triggers & Diet: Managing Flares | Dr. Varada",
    "meta": "What triggers psoriasis flares (infection, stress, medication, smoking, alcohol, "
            "weather, skin injury), and what the evidence says about diet and weight.",
    "eyebrow": "Psoriasis",
    "h1": "Triggers, diet and keeping flares apart",
    "lede": "Most people can name their own trigger within a month of being asked to keep a "
            "record. The value is not academic. A known trigger turns a flare from something "
            "that happens to you into something you can get ahead of.",
    "acts": [("Consult online", WHATSAPP), ("Back to the psoriasis hub", "psoriasis")],
    "sources": ["niams-psoriasis", "nhs-psoriasis", "npf", "who-psoriasis"],
    "glance": [
        ("Strongest triggers", "Throat infection, stopping treatment, injury"),
        ("Diet that cures it", "None"),
        ("Diet change with evidence", "Weight loss, if overweight"),
        ("Alcohol", "Worsens disease; limits drug options"),
        ("Smoking", "Worsens disease, especially palmoplantar"),
        ("Weather", "Cold, dry seasons are worse for most"),
    ],
    "sections": [
        {"kind": "table", "eyebrow": "Triggers", "h2": "What actually sets off a flare",
         "head": ["Trigger", "How it shows", "What to do"],
         "rows": [
             ["Streptococcal throat infection", "Guttate crop 1–3 weeks later",
              "Treat the throat; tell the dermatologist"],
             ["Stopping treatment abruptly", "Rebound, sometimes worse than before",
              "Step down, never stop dead"],
             ["Skin injury", "New plaque exactly at the site (Koebner)",
              "Protect skin; treat cuts promptly"],
             ["Certain medications", "Flare weeks after starting",
              "Beta blockers, lithium, antimalarials: never stop without advice"],
             ["Smoking", "Worse disease; strong link to palmoplantar pustulosis",
              "Stopping improves both disease and drug options"],
             ["Alcohol", "Worse disease; restricts methotrexate use",
              "Reduce: it changes what can be prescribed"],
             ["Stress", "Flare during or after a difficult period",
              "Recognised trigger; worth naming"],
             ["Cold, dry weather", "Seasonal worsening", "Increase emollients pre-emptively"],
         ],
         "note": "Never stop a prescribed medicine because it appears on this list. The "
                 "psoriasis is managed around it, or the prescriber is consulted."},

        {"kind": "prose", "eyebrow": "Diet", "h2": "What the evidence actually supports.",
         "body": [
             "There is no psoriasis diet. No food causes it, no elimination clears it, and "
             "the confident dietary advice circulating online is not supported by evidence "
             "of a quality that would change a prescription.",
             "Two things do have real support. The first is weight: in people who are "
             "overweight, losing weight improves psoriasis severity and improves how well "
             "treatments, including systemic drugs, work. This is one of the few lifestyle "
             "changes with a genuinely measurable effect on the disease.",
             "The second is alcohol. Heavy use worsens psoriasis and, more practically, "
             "restricts what can safely be prescribed. Methotrexate and alcohol together are a "
             "liver problem waiting to happen. Reducing intake widens your treatment options as "
             "well as improving your skin.",
         ]},

        {"kind": "split", "eyebrow": "The flare plan",
         "h2": "Deciding what to do before you need to decide.",
         "body": ["The difference between a three-day flare and a three-week one is usually "
                  "how quickly treatment restarts. And the thing that decides that is "
                  "whether the patient already knows what to start, at what point, without "
                  "waiting for an appointment.",
                  "So every psoriasis patient here leaves with that written down: the early "
                  "sign to watch for, what to apply, how long to give it, and the point at "
                  "which to call rather than continue."],
         "cta": ("Get a written flare plan", WHATSAPP),
         "items": [
             {"title": "Keep a simple record",
              "body": "Date, what flared, what happened in the fortnight before. Most people "
                      "identify their own pattern within a month or two."},
             {"title": "Emollient before the season",
              "body": "For people who worsen every winter, increasing emollients before the "
                      "cold starts works better than reacting to it."},
         ]},

        {"kind": "checklist", "eyebrow": "Worth doing", "h2": "The evidence-based short list.",
         "items": [
             "<b>Lose excess weight</b>: the change with the clearest effect",
             "<b>Reduce alcohol</b>: improves disease and widens drug options",
             "<b>Stop smoking</b>: particularly for palms and soles",
             "<b>Emollient daily</b>, not only during flares",
             "<b>Treat throat infections</b> promptly",
             "<b>Never stop treatment abruptly</b>: step it down",
         ]},

        ARTHRITIS,
    ],
    "faq_h2": "Triggers and diet",
    "faqs": [
        ("What food should I avoid with psoriasis?",
         "There is no food that must be avoided. No elimination diet has been shown to clear "
         "psoriasis. If you are overweight, losing weight has better evidence behind it than "
         "any specific food restriction."),
        ("Does a gluten-free diet help psoriasis?",
         "Only in the minority of patients who also have coeliac disease or demonstrated "
         "gluten sensitivity. For everyone else there is no benefit, and it is an "
         "unnecessary restriction."),
        ("Can stress cause psoriasis?",
         "Stress does not cause the disease, but it is a well-recognised trigger for flares "
         "in people who already have it. Many patients can date a flare to a specific "
         "difficult period."),
        ("Which medicines can make psoriasis worse?",
         "Beta blockers, lithium, antimalarials and abrupt withdrawal of oral steroids are the "
         "recognised ones. Never stop a prescribed medicine on your own. Tell the "
         "dermatologist, who will work with the prescriber."),
        ("Does sunlight help?",
         "Moderate natural sunlight improves psoriasis in most people, which is the same "
         "principle phototherapy uses in a controlled dose. Burning makes it worse, because "
         "injured skin can trigger new plaques."),
        ("Do supplements like fish oil or vitamin D help?",
         "Evidence is weak and inconsistent. Correcting a documented vitamin D deficiency is "
         "reasonable for general health; taking supplements as a psoriasis treatment is not "
         "supported."),
    ],
    "related": [
        ("psoriasis-phototherapy", "Phototherapy", "Sunlight, dosed properly."),
        ("psoriasis-biologics", "Systemics and biologics", "When lifestyle alone isn't enough."),
        CROSS,
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-phototherapy", "template": "T2", "condition": "Psoriasis",
    "crumbs": [("Psoriasis", "psoriasis"), ("Phototherapy", None)],
    "title": "Phototherapy for Psoriasis: NB-UVB Explained | Dr. Varada",
    "meta": "Narrowband UVB phototherapy for psoriasis: how it works, how many sessions it "
            "takes, what remission looks like, and how it compares with systemic drugs.",
    "eyebrow": "Psoriasis · Treatment",
    "h1": "Phototherapy for psoriasis",
    "lede": "The treatment that sits between creams and tablets: effective for widespread "
            "disease, without suppressing the whole immune system. Its cost is not money so "
            "much as time. Two or three visits a week for a couple of months.",
    "acts": [("Consult online", WHATSAPP), ("Back to the psoriasis hub", "psoriasis")],
    "sources": ["dermnet-phototherapy", "nice-psoriasis", "aad-psoriasis", "dermnet-psoriasis"],
    "glance": [
        ("What it is", "311 nm narrowband ultraviolet B"),
        ("Frequency", "2–3 sessions a week"),
        ("Typical course", "20–36 sessions"),
        ("Clearance", "Substantial in most patients"),
        ("Remission", "Often months after a completed course"),
        ("Best for", "Widespread plaque and guttate disease"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How it works",
         "h2": "Immune suppression, confined to the skin.",
         "body": [
             "Narrowband UVB damps down the inflammatory activity driving psoriasis, but it "
             "does so only in the skin the light reaches. That is its central advantage over "
             "tablets: no whole-body immune suppression, no liver monitoring, no drug "
             "interactions.",
             "It suits widespread disease particularly well, because treating forty plaques "
             "with creams is impractical and treating them with a systemic drug is more than "
             "many patients need. Guttate psoriasis, dozens of small spots after a throat "
             "infection, is close to an ideal indication and often clears completely.",
             "The limitation is logistics. A course means two or three clinic visits a week "
             "for two to three months, and courses abandoned halfway are the commonest "
             "reason phototherapy is judged not to have worked.",
         ]},

        {"kind": "steps", "eyebrow": "A course", "h2": "What to expect",
         "items": [
             {"title": "Dose set to your skin",
              "body": "The starting dose depends on your skin type, and is increased "
                      "session by session to the point of faint pinkness that fades."},
             {"title": "Two to three times a week",
              "body": "Each session lasts seconds to a few minutes. Goggles at every "
                      "session; men are shielded genitally without exception."},
             {"title": "Improvement by week three or four",
              "body": "Plaques flatten before they fade. Residual brown marks after "
                      "clearance are post-inflammatory and settle over months."},
             {"title": "Complete the course, then stop",
              "body": "A finished course frequently gives months of remission. A course "
                      "stopped at week four usually gives a rapid relapse."},
         ]},

        {"kind": "table", "eyebrow": "Comparisons", "h2": "Phototherapy or a systemic drug?",
         "head": ["", "Phototherapy", "Methotrexate / systemics"],
         "rows": [
             ["Immune effect", "Skin only", "Whole body"],
             ["Blood monitoring", "None routinely", "Regular, ongoing"],
             ["Time cost", "2–3 clinic visits weekly", "Tablets at home"],
             ["Works on joints", "No", "Yes: methotrexate treats arthritis too"],
             ["Pregnancy", "Generally acceptable", "Methotrexate absolutely contraindicated"],
             ["Remission after stopping", "Often months", "Usually returns on stopping"],
             ["Best for", "Widespread skin-only disease", "Joint disease, resistant disease"],
         ],
         "note": "If you have psoriatic arthritis, phototherapy will help your skin and do "
                 "nothing for your joints. That single fact decides the choice for many "
                 "patients."},

        {"kind": "split", "eyebrow": "Practicalities",
         "h2": "The reason courses fail is almost never the light.",
         "body": ["Phototherapy has good evidence and a good safety record. What it does not "
                  "have is convenience, and adherence is the strongest predictor of whether a "
                  "course works.",
                  "So the practical conversation happens before the first session: whether "
                  "you can realistically attend twice a week for two months, whether the "
                  "clinic timings fit your work, and whether a systemic drug would actually "
                  "suit your life better. Choosing the treatment you will finish beats "
                  "choosing the one that scores best on paper."],
         "cta": ("Discuss which suits you", WHATSAPP),
         "items": [
             {"title": "Timings decide adherence",
              "body": "Sessions are short. It is the travel that people cannot sustain. Worth "
                      "being honest about before starting."},
             {"title": "Cumulative dose is tracked",
              "body": "Lifetime session counts are recorded, as with any ultraviolet "
                      "treatment."},
         ]},

        {"kind": "callout", "warn": True, "title": "Ultraviolet is not sunbathing",
         "body": "Tanning beds emit mostly UVA at uncontrolled doses and will not deliver "
                 "the 311 nm narrowband wavelength. They raise skin cancer risk without "
                 "delivering the therapeutic effect. Sunburn also injures skin, which can "
                 "trigger new plaques."},
    ],
    "faq_h2": "Phototherapy questions",
    "faqs": [
        ("How many phototherapy sessions will I need for psoriasis?",
         "Most courses run 20 to 36 sessions at two to three a week, so roughly two to three "
         "months. Improvement usually begins by week three or four."),
        ("How long does remission last afterwards?",
         "Often several months after a completed course, and sometimes longer. It varies "
         "considerably. Stopping halfway generally means a rapid relapse."),
        ("Is phototherapy safer than methotrexate?",
         "It avoids whole-body immune suppression and routine blood monitoring, which many "
         "patients prefer. But it does nothing for joint disease, and it demands far more of "
         "your time. Neither is simply safer. They suit different situations."),
        ("Can I have phototherapy during pregnancy?",
         "Narrowband UVB is generally considered acceptable in pregnancy and is often the "
         "preferred option, because most systemic psoriasis drugs are not. This is decided "
         "case by case."),
        ("Does it hurt?",
         "No. Sessions are short and feel like warmth. Mild pinkness that fades within a day "
         "is the intended endpoint; burning means the dose needs reducing."),
        ("Will the brown marks left behind fade?",
         "Yes. Those are post-inflammatory pigmentation, not remaining psoriasis, and they "
         "settle over weeks to months once the plaque has cleared."),
    ],
    "related": [
        ("psoriasis-biologics", "Systemics and biologics", "The next rung of the ladder."),
        ("psoriasis-cost", "What it costs", "How a course is priced."),
        CROSS,
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-biologics", "template": "T2", "condition": "Psoriasis",
    "crumbs": [("Psoriasis", "psoriasis"), ("Systemics and biologics", None)],
    "title": "Systemic & Biologic Treatment for Psoriasis | Dr. Varada",
    "meta": "Methotrexate, ciclosporin, acitretin, apremilast and biologics for psoriasis, when "
            "systemic treatment is appropriate, and what monitoring it requires.",
    "eyebrow": "Psoriasis · Treatment",
    "h1": "Systemic treatment and biologics",
    "lede": "When psoriasis is extensive, disabling, or attacking the joints, treating it from "
            "the outside stops being enough. These are the drugs that work from the inside: "
            "powerful, well-evidenced, and requiring proper monitoring.",
    "acts": [("Discuss your options", WHATSAPP), ("Back to the psoriasis hub", "psoriasis")],
    "sources": ["dermnet-biologics", "dermnet-methotrexate", "nice-psoriasis", "aad-psoriasis"],
    "glance": [
        ("Considered when", "Extensive, disabling, or joint disease"),
        ("First-line systemic", "Usually methotrexate"),
        ("Monitoring", "Blood tests before and during"),
        ("Biologics", "Target one inflammatory signal"),
        ("Screening", "TB and hepatitis before biologics"),
        ("Pregnancy", "Several are absolutely contraindicated"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The threshold",
         "h2": "When creams and light stop being the right answer.",
         "body": [
             "Systemic treatment is considered when disease is extensive, when it has failed "
             "adequate topical and phototherapy trials, when it is disabling out of proportion "
             "to its area, palms and soles are the classic example, or when there is psoriatic "
             "arthritis, because joints do not respond to anything applied to skin.",
             "That last point deserves emphasis. Joint damage in psoriatic arthritis is "
             "irreversible, and the window in which treatment prevents it is early. A "
             "patient with joint symptoms is not someone to try another cream on.",
             "The trade is real and it is discussed openly: these drugs suppress immune "
             "function and require monitoring. For the right patient the balance is "
             "strongly favourable. For someone with mild, limited disease it is not, and "
             "the honest answer is to stay on the lower rungs.",
         ]},

        {"kind": "table", "eyebrow": "The conventional systemics",
         "h2": "What each is, and what it demands",
         "head": ["Drug", "Suits", "Requires"],
         "rows": [
             ["Methotrexate", "Extensive disease; also treats psoriatic arthritis",
              "Regular blood counts and liver monitoring; no alcohol excess; not in pregnancy"],
             ["Ciclosporin", "Rapid control of a severe flare; short-term use",
              "Blood pressure and kidney monitoring; time-limited courses"],
             ["Acitretin", "Palmoplantar and pustular disease",
              "Lipid and liver monitoring; strict pregnancy avoidance for years after"],
             ["Apremilast", "Moderate disease where monitoring is difficult",
              "No routine blood monitoring; nausea and weight loss common early"],
         ],
         "note": "Choice depends on your other conditions as much as on the psoriasis: liver, "
                 "kidneys, blood pressure, alcohol use and pregnancy plans all narrow the list "
                 "before anything else is considered."},

        {"kind": "cards", "eyebrow": "Biologics", "h2": "Targeted, and how they differ",
         "accent": "chronic",
         "items": [
             {"eyebrow": "What they are", "title": "One signal, blocked",
              "body": "Biologics are injected antibodies that block a single specific "
                      "inflammatory messenger driving psoriasis, rather than suppressing "
                      "immune function broadly.",
              "list": ["Given by injection", "Highly effective in severe disease",
                       "Several classes with different targets"]},
             {"eyebrow": "Before starting", "title": "Screening is mandatory",
              "body": "Latent tuberculosis and hepatitis B and C are screened for before "
                      "any biologic is started. In India, TB screening is not a formality.",
              "list": ["TB screening", "Hepatitis B and C", "Vaccination review"]},
             {"eyebrow": "In practice", "title": "Access and cost",
              "body": "The main barrier in India is cost, and biosimilars have changed but "
                      "not removed it. This is discussed frankly before starting.",
              "list": ["Long-term commitment", "Ongoing monitoring",
                       "Infection risk needs awareness"]},
         ]},

        {"kind": "split", "eyebrow": "Monitoring",
         "h2": "The tests are not bureaucracy.",
         "body": ["Every systemic drug here has a monitoring schedule, and the schedule "
                  "exists because the problems it catches are silent until they are not. "
                  "Methotrexate can affect blood counts and the liver without any symptom "
                  "at all until damage is done.",
                  "So treatment is not started unless the monitoring is realistic for you, "
                  "which for patients outside Hyderabad means agreeing where blood tests will "
                  "be done locally and how results will reach the clinic."],
         "cta": ("Arrange a systemic-therapy review", WHATSAPP),
         "items": [
             {"title": "Baseline before starting",
              "body": "Bloods, and screening where a biologic is planned. Nothing starts "
                      "before the baseline is in hand."},
             {"title": "Local tests, remote review",
              "body": "Out-of-state patients have bloods done locally and reviewed by video. "
                      "It works, provided it is agreed in advance."},
         ]},

        {"kind": "callout", "warn": True, "title": "Oral steroids are not a psoriasis treatment",
         "body": "Systemic steroids clear psoriasis impressively and are still prescribed for "
                 "it. Withdrawal frequently causes a severe rebound, and generalised pustular "
                 "psoriasis, a medical emergency, can follow. If you have been given oral "
                 "steroids for psoriasis, raise it at your next appointment rather than "
                 "stopping them yourself."},

        ARTHRITIS,
    ],
    "faq_h2": "Systemic treatment",
    "faqs": [
        ("When is methotrexate needed for psoriasis?",
         "When disease is extensive, has failed adequate topical and phototherapy treatment, or "
         "when psoriatic arthritis is present. Methotrexate treats both skin and joints, which "
         "phototherapy does not."),
        ("Is methotrexate dangerous?",
         "It requires respect rather than fear. Regular blood monitoring catches the "
         "problems that matter, alcohol must be limited, and it is absolutely avoided in "
         "pregnancy. Within those boundaries it has decades of safe use in psoriasis."),
        ("Are biologics available in India?",
         "Yes, including biosimilars which have reduced cost substantially. Cost remains the "
         "main barrier for most patients, and it is discussed openly before starting rather "
         "than after."),
        ("Why do I need a TB test before a biologic?",
         "Biologics can reactivate latent tuberculosis. Given TB prevalence in India, "
         "screening before starting is essential and is not optional."),
        ("Can I stop systemic treatment once my skin is clear?",
         "Sometimes, with a planned reduction. Psoriasis usually returns after stopping, so "
         "the decision balances how long remission has held against the burden of "
         "continuing. It is never stopped abruptly."),
        ("Can I take these if I want to become pregnant?",
         "Several are absolutely contraindicated: methotrexate and acitretin in particular, "
         "with acitretin requiring pregnancy avoidance for years after stopping. Tell the "
         "clinic about pregnancy plans before starting anything, not after."),
    ],
    "related": [
        ("psoriasis-phototherapy", "Phototherapy", "The rung below, and often tried first."),
        ("psoriasis-cost", "What it costs", "Including biologics and monitoring."),
        ONLINE,
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-cost", "template": "T2", "condition": "Psoriasis",
    "crumbs": [("Psoriasis", "psoriasis"), ("Cost", None)],
    "title": "Psoriasis Treatment Cost in India | Dr. Varada",
    "meta": "What psoriasis treatment costs in India: how topicals, phototherapy, methotrexate "
            "and biologics are priced, and how to compare one clinic's quote.",
    "eyebrow": "Psoriasis",
    "h1": "What psoriasis treatment costs",
    "lede": "Psoriasis is a lifetime condition treated in episodes, so the useful question is "
            "not the price of one prescription. It is the annual cost of keeping the disease "
            "quiet, including the monitoring nobody quotes for.",
    "acts": [("Ask for your costing", WHATSAPP), ("Back to the psoriasis hub", "psoriasis")],
    "sources": ["nice-psoriasis", "dermnet-biologics", "dermnet-methotrexate"],
    "glance": [
        ("Topicals", "Monthly, at the pharmacy"),
        ("Phototherapy", "Per session, 20–36 per course"),
        ("Methotrexate", "Low drug cost; monitoring adds"),
        ("Biologics", "The largest cost by a wide margin"),
        ("Monitoring", "Recurring: quote it separately"),
        ("Quoted", "After examination, in writing"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How pricing works",
         "h2": "The cost that gets forgotten is the monitoring.",
         "body": [
             "Psoriasis costs split into three streams that behave differently. Medication is a "
             "recurring pharmacy cost. Procedures, phototherapy, are per session across a "
             "defined course. And monitoring is a recurring laboratory cost that almost nobody "
             "includes when they compare quotes.",
             "That last one matters most for systemic drugs. Methotrexate itself is "
             "inexpensive; the blood tests that make it safe are not free, and they recur "
             "for as long as you take it. A quote that names only the tablet price is "
             "incomplete rather than dishonest, but the effect on your planning is the same.",
             "Biologics sit in their own category. They are dramatically more expensive than "
             "everything else here, biosimilars have narrowed the gap without closing it, "
             "and the conversation about affordability happens before the prescription is "
             "written rather than after.",
         ]},

        {"kind": "table", "eyebrow": "The structure", "h2": "What you are charged for",
         "intro": "Figures are confirmed at consultation. The structure below is what lets "
                  "you compare one clinic's quote against another's meaningfully.",
         "head": ["Item", "Charged", "What drives the total"],
         "rows": [
             ["Consultation", "Per visit", "First visit and periodic reviews"],
             ["Topical treatment", "Monthly at the pharmacy",
              "Body surface treated; which agents"],
             ["Medicated shampoos", "Monthly", "Scalp involvement"],
             ["NB-UVB phototherapy", "Per session", "20–36 sessions per course"],
             ["Methotrexate", "Monthly: low", "Drug cost is small"],
             ["Blood monitoring", "Per test round, recurring",
              "The cost most often left out of a quote"],
             ["Biologics", "Per dose, ongoing", "Which agent; biosimilar availability"],
             ["Pre-biologic screening", "One-off", "TB and hepatitis screening"],
         ],
         "note": "Rupee figures are quoted after examination and deliberately not published "
                 "here. The right treatment depends on how much skin is involved and whether "
                 "your joints are affected, and so therefore does the cost."},

        {"kind": "checklist", "eyebrow": "Before you commit",
         "h2": "Questions worth asking about any psoriasis quote.",
         "items": [
             "<b>Is monitoring included</b> in this figure?",
             "<b>How many phototherapy sessions</b> is the course expected to run?",
             "<b>What is the annual cost</b>, not the monthly one?",
             "<b>What happens at review</b> if this hasn't worked?",
             "<b>Is a biosimilar available</b> for the biologic proposed?",
             "<b>What does the flare plan cost</b> when I use it?",
         ]},

        {"kind": "split", "eyebrow": "Value, not price",
         "h2": "The cheapest treatment is the one that stops the flares.",
         "body": ["A patient flaring four times a year pays for four courses of rescue "
                  "treatment, four rounds of appointments and four periods of not working "
                  "properly. A maintenance plan that reduces that to one flare a year is "
                  "cheaper even if the monthly cost looks higher.",
                  "That is the calculation worth doing, and it is rarely the one presented. "
                  "It is also why the plan here is written as a year, not as a prescription."],
         "cta": ("Get a costed plan", WHATSAPP),
         "items": [
             {"title": "Count the flares",
              "body": "How many per year, and what each one costs you in treatment and in "
                      "days. That number is the real baseline."},
             {"title": "Maintenance is cheaper than rescue",
              "body": "Almost always, and it is also less disruptive, which is the part no "
                      "invoice shows."},
         ]},

        {"kind": "callout", "title": "Insurance in India",
         "body": "Most policies treat psoriasis as a chronic outpatient condition and do not "
                 "cover routine treatment. Cover is more likely where admission is required "
                 "or where psoriatic arthritis is being treated. Check your specific policy "
                 "wording rather than assuming either way."},
    ],
    "faq_h2": "Cost questions",
    "faqs": [
        ("Why aren't rupee figures listed here?",
         "Because the right treatment, and therefore the cost, depends on how much skin is "
         "involved, whether your joints are affected, and what has already been tried. Costs "
         "are quoted in writing after examination, including after a video consultation."),
        ("What is the most expensive psoriasis treatment?",
         "Biologics, by a wide margin. Biosimilars have reduced the gap. Everything else "
         "(topicals, phototherapy, conventional systemics), sits in a much lower range."),
        ("Is phototherapy or methotrexate cheaper?",
         "Methotrexate is usually cheaper in drug cost, but requires recurring blood "
         "monitoring. Phototherapy has no monitoring cost but requires 20–36 clinic visits, "
         "which carries its own travel and time cost. Compare the total, not the headline."),
        ("Does insurance cover psoriasis treatment in India?",
         "Usually not for routine outpatient care. Cover is more likely where admission is "
         "needed or where psoriatic arthritis is being treated. Read your policy wording."),
        ("Can I reduce costs without compromising treatment?",
         "Often yes, by using generics and biosimilars where clinically equivalent, by "
         "completing a phototherapy course properly so it delivers a real remission, and by "
         "having monitoring bloods done locally rather than at a hospital laboratory."),
    ],
    "related": [
        ("psoriasis-biologics", "Systemics and biologics", "Where the large numbers are."),
        ("psoriasis-phototherapy", "Phototherapy", "Per-session pricing explained."),
        ONLINE,
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "psoriasis-online-consultation", "template": "T2", "condition": "Psoriasis",
    "crumbs": [("Psoriasis", "psoriasis"), ("Online consultation", None)],
    "title": "Online Psoriasis Consultation Across India | Dr. Varada",
    "meta": "Consult a dermatologist of 45 years about psoriasis by video, anywhere in India. "
            "Second opinions, flare plans, systemic reviews and arthritis screening.",
    "eyebrow": "Psoriasis",
    "h1": "Consult about psoriasis from anywhere in India",
    "lede": "Psoriasis is managed by decisions far more than by procedures, which treatment, at "
            "what point, for how long, and when to escalate. Almost all of that can be done "
            "properly over video.",
    "acts": [("Book a video consultation", WHATSAPP), ("Call the clinic", PHONE)],
    "sources": ["niams-psoriasis", "nice-psoriasis", "dermnet-psa"],
    "glance": [
        ("Booking", "WhatsApp: video link sent back"),
        ("Good for", "Second opinions, flare plans, systemic reviews"),
        ("Not for", "Phototherapy, procedures, joint examination"),
        ("You'll need", "Photographs, prescriptions, recent bloods"),
        ("Languages", "English, Hindi, Telugu"),
        ("Outcome", "A written plan you can run locally"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Why this works",
         "h2": "Psoriasis is a management problem, not a procedural one.",
         "body": [
             "Unlike conditions that need a scalpel or a light box, most of what determines "
             "a psoriasis outcome is judgement: whether the current treatment is adequate, "
             "whether a potent steroid has been running unsupervised for too long, whether "
             "the joint symptoms being dismissed are actually psoriatic arthritis, and "
             "whether it is time to escalate.",
             "All of those can be assessed from a good history, clear photographs and recent "
             "blood results. And they are exactly the questions patients outside major "
             "cities most often cannot get answered.",
             "The commonest single finding in these consultations is not a missed diagnosis. It "
             "is a patient using a potent topical steroid month after month with no maintenance "
             "plan and no review. Controlled just enough not to complain, and heading for a "
             "rebound.",
         ]},

        {"kind": "cards", "eyebrow": "Scope", "h2": "What a video consultation can settle",
         "accent": "chronic",
         "items": [
             {"eyebrow": "Works well", "title": "What can be done remotely",
              "list": ["Review a treatment that isn't holding",
                       "Write a flare plan",
                       "Screen for psoriatic arthritis by history",
                       "Second opinion on proposed systemic therapy",
                       "Interpret monitoring bloods",
                       "Advise on phototherapy available near you"]},
             {"eyebrow": "Needs a visit", "title": "What can't",
              "list": ["Phototherapy itself",
                       "Joint examination",
                       "Biopsy of an uncertain rash",
                       "Starting some systemics for the first time"]},
             {"eyebrow": "Typical outcome", "title": "What you leave with",
              "body": "A written plan: what to use now, what to step down to, what to start "
                      "at the first sign of a flare, and the point at which to escalate or "
                      "be seen in person."},
         ]},

        {"kind": "steps", "eyebrow": "Preparing", "h2": "How to make it count",
         "items": [
             {"title": "Photograph in daylight",
              "body": "Wide shots of each affected region and close shots of representative "
                      "plaques. Include the scalp, nails and any fold involvement."},
             {"title": "List every treatment tried",
              "body": "Names, strengths, how long each was used and whether it worked. "
                      "'Some cream from the chemist' cannot be assessed."},
             {"title": "Bring recent bloods",
              "body": "Especially if you are on or considering methotrexate. Liver function and "
                      "blood counts."},
             {"title": "Note your joints",
              "body": "Morning stiffness and how long it lasts, any swollen finger or toe, "
                      "heel pain, back pain that eases with movement."},
         ]},

        ARTHRITIS,

        {"kind": "split", "eyebrow": "Continuing care",
         "h2": "A remote plan only works if the monitoring does.",
         "body": ["Systemic treatment started or continued remotely requires blood tests, "
                  "and those have to be practical where you live. So part of the "
                  "consultation is agreeing the arrangement: which laboratory, how often, "
                  "and how the results reach the clinic before the next review.",
                  "Where that cannot be arranged reliably, the honest answer is that systemic "
                  "therapy should be supervised by someone you can reach, and that is said "
                  "rather than avoided."],
         "cta": ("Book a review", WHATSAPP),
         "items": [
             {"title": "Local bloods, remote review",
              "body": "Standard practice for out-of-state patients, and it works when it is "
                      "agreed in advance."},
             {"title": "Escalation has a threshold",
              "body": "The plan states what change means 'be seen in person', so nobody is "
                      "left guessing during a flare."},
         ]},
    ],
    "faq_h2": "Online consultation",
    "faqs": [
        ("Can psoriasis really be treated over video?",
         "Managed, yes: psoriasis care is mostly decisions rather than procedures. What cannot "
         "be done remotely is phototherapy, joint examination, and biopsy of an unclear rash."),
        ("What photographs should I send?",
         "Daylight, no flash or filter. Wide shots of each affected area plus close shots of "
         "representative plaques, and specifically include scalp, nails and any skin folds. "
         "Those three change the diagnosis most often."),
        ("Can I be started on methotrexate after a video consultation?",
         "Sometimes, provided baseline bloods are available and ongoing monitoring can be "
         "arranged reliably where you live. If that cannot be arranged, you will be told so "
         "rather than started on it anyway."),
        ("Can you tell if I have psoriatic arthritis over video?",
         "The history is highly informative, morning stiffness over 30 minutes, a swollen "
         "finger or toe, heel pain, inflammatory back pain. If those are present you will be "
         "advised to be examined, usually by a rheumatologist, without delay."),
        ("Do I need to come to Hyderabad at all?",
         "Many psoriasis patients do not. Travel is worth it mainly for phototherapy courses "
         "that are not available locally, or for a rash that needs biopsy."),
        ("Which languages can I consult in?",
         "English, Hindi and Telugu."),
    ],
    "related": [CROSS,
                ("psoriasis-biologics", "Systemics and biologics",
                 "The escalation conversation, and what monitoring it needs."),
                ("psoriasis-triggers-and-diet", "Triggers and diet",
                 "What to record before the appointment.")],
},

]
