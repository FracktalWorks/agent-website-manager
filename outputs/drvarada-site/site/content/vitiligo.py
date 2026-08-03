"""T2 — the pan-India vitiligo hub and its cluster.

These pages carry no city qualifier. They compete nationally, they educate, and they
funnel to online consultation; `/vitiligo-treatment-hyderabad/` is the local twin and
the two must never chase the same query (KEYWORD_MAP rule 2).

The single hardest rule on these pages: **vitiligo is not curable, and nothing here
may imply otherwise.** The vocabulary is repigmentation, stability, control and
spread. It is also the correct clinical vocabulary, so this costs nothing.
"""

from chrome import (FEE_CLINIC_SHOW, FEE_DIFF_SHOW, FEE_ONLINE_SHOW, FEE_TAX,
                    PHONE, WHATSAPP)
from content.fees import FEE_FAQS, NOTE_COST, fees_block

CROSS = ("vitiligo-treatment-hyderabad", "Vitiligo treatment in Hyderabad",
         "If you can reach the clinic: phototherapy, excimer and the grafting list.")
ONLINE = ("vitiligo-online-consultation", "Consult online from anywhere in India",
          "How a video consultation works, what it can settle, and what it can't.")

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", None)],
    "title": "Vitiligo Treatment in India: Light & Surgery | Dr. Varada",
    "meta": "Vitiligo treatment by a dermatologist of 45 years: what causes white patches, "
            "which treatments repigment skin, when surgery works, and what it costs.",
    "eyebrow": "The vitiligo section",
    "h1": "Vitiligo, explained properly.",
    "lede": "White patches are the visible part. What decides your treatment is invisible: "
            "whether the disease is still spreading, how long each patch has been there, "
            "and where on the body it sits. This section covers all of it.",
    "acts": [("Consult online", WHATSAPP), ("Call the clinic", PHONE)],
    "sources": ["niams-vitiligo", "aad-vitiligo-tx", "dermnet-vitiligo", "nhs-vitiligo", "iadvl-vitiligo-surgery", "gvf"],
    "glance": [
        ("Also called", "Leucoderma, white patches, safed daag"),
        ("Curable", "No, but repigmentation is common"),
        ("Main treatments", "Topicals, NB-UVB, excimer, surgery"),
        ("Timeline", "Months, reviewed every 6–8 weeks"),
        ("Surgery needs", "Disease stable for 12 months"),
        ("India prevalence", "Among the highest in the world"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What it is",
         "h2": "An immune system that stopped recognising your pigment cells.",
         "body": [
             "Vitiligo is an autoimmune condition. The melanocytes, the cells that make "
             "pigment, are destroyed or switched off in patches, and the skin left behind has "
             "no colour. It is not an infection, it is not caused by anything you ate, and it "
             "cannot be passed to anyone else by touch.",
             "It affects roughly one person in a hundred worldwide, and India carries one of "
             "the highest burdens of any country. Around a fifth of patients have a close "
             "relative with it, so a family history is common without being deterministic. Most "
             "children of a parent with vitiligo never develop it.",
             "The clinically important distinction is not how big the patches are. It is "
             "whether the disease is <b>active</b>, still producing new patches or expanding "
             "old ones, or <b>stable</b>. Almost every treatment decision on this page follows "
             "from that one answer.",
         ]},

        {"kind": "diagram", "eyebrow": "How pigment works",
         "h2": "What the immune system is destroying.",
         "intro": "Pigment is made by one cell type and given away. A melanocyte sits at the base of the epidermis and passes packets of pigment out along its arms into the surrounding skin cells, which carry them upward. Lose the melanocyte and the skin above it has no supply.",
         "caption": "One melanocyte supplies roughly thirty-six surrounding cells. That is why losing a small number of them clears the colour from a visible patch of skin, and why treatment aims to bring cells back rather than add dye.",
         "labels": [
             {"text": "Pigment cap over each nucleus", "x": 40, "y": 33, "lead": 21, "find": "artwork"},
             {"text": "Packets travelling along the arm", "x": 34, "y": 47, "lead": 27, "find": "artwork"},
             {"text": "Arms reaching between cells", "x": 46, "y": 57, "lead": 15, "find": "artwork"},
             {"text": "Melanocyte", "x": 31, "y": 74, "lead": 30, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/A2-melanocyte.webp", "w": 1820, "h": 1024,
             "alt": "A melanocyte at the base of the epidermis, drawn as a star-shaped cell with long arms reaching up between the surrounding skin cells. Dark brown pigment granules are made inside the melanocyte, travel along its arms, and are handed into neighbouring cells, where they gather into a cap sitting above each cell nucleus. Higher rows of cells flatten and pale toward the skin surface."}},

        {"kind": "cards", "eyebrow": "The two questions", "h2": "What the first visit settles",
         "accent": "chronic",
         "items": [
             {"eyebrow": "Question one", "title": "Is it still spreading?",
              "body": "Active disease has to be stopped before anything can be rebuilt. "
                      "New patches in the last six months, patches with blurred edges, or "
                      "depigmentation appearing where the skin was scratched or injured all "
                      "point to activity.",
              "list": ["Wood's lamp examination", "Dated photographs of the margins",
                       "History of new patches in 6 months"]},
             {"eyebrow": "Question two", "title": "Where is it, and for how long?",
              "body": "Face and neck respond best; hands, feet and lips respond least, "
                      "because they have the fewest pigment reservoirs to repopulate from. "
                      "Patches present for many years respond more slowly.",
              "list": ["Site: face, trunk, extremities", "Duration of each patch",
                       "Hair colour inside the patch"]},
         ]},

        {"kind": "callout", "title": "Why the hair inside a patch matters",
         "body": "Pigment cells survive in hair follicles even when they are gone from the "
                 "surrounding skin, and repigmentation usually starts as small dark dots around "
                 "each hair. If the hairs inside a patch have turned white too, that reservoir "
                 "is depleted, which is why those patches respond poorly to creams and light, "
                 "and why surgery exists."},

        {"kind": "diagram", "eyebrow": "Repigmentation",
         "h2": "Colour comes back two ways, and one of them needs hair.",
         "intro": "Pigment returns as small islands spreading outward from each hair follicle, and as a band creeping in from the edge of the patch. That is the whole reason lips and fingertips are difficult: almost no follicles, almost no reservoir to repopulate from.",
         "caption": "Pigment cells survive inside hair follicles after they have gone from the skin around them. Light and creams work by waking that reservoir, which is why a patch whose hairs have turned white responds so poorly to both.",
         "labels": [
             {"text": "Island spreading from one hair", "x": 22, "y": 19, "lead": 39, "find": "spot:skin@pale"},
             {"text": "A hair with no island yet", "x": 40, "y": 31, "lead": 21, "col": 71, "find": "artwork"},
             {"text": "Pigment advancing from the edge", "x": 18, "y": 40, "lead": 43, "find": "edge:pale|skin"},
             {"text": "The follicle beneath", "x": 19, "y": 69, "lead": 42, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/B2-repigmentation-routes.webp", "w": 1820, "h": 1024,
             "alt": "A pale vitiligo patch on brown skin, seen from above, with pigment returning in two ways. Small round islands of brown pigment have appeared inside the patch, each one centred on a hair and spreading outward from it, while a band of pigment creeps inward from the patch border. Two hairs in the patch have no island around them yet. A cut-away at the corner shows a hair follicle running down beneath the pale surface."}},

        {"kind": "table", "eyebrow": "Treatments",
         "h2": "What each treatment does, and who it suits",
         "intro": "There is no single vitiligo treatment. There is a sequence, and where "
                  "you enter it depends on activity, site and duration.",
         "head": ["Treatment", "What it does", "Best suited to"],
         "rows": [
             ["Topical steroids", "Suppresses the immune attack; halts spread",
              "Recent, active, limited patches"],
             ["Calcineurin inhibitors", "Immune-modulating without steroid thinning",
              "Face, eyelids, folds: thin skin"],
             ["Topical JAK inhibitors", "Blocks the specific immune signal in vitiligo",
              "Facial and limited non-segmental disease"],
             ["NB-UVB phototherapy", "Stimulates surviving melanocytes to repopulate",
              "Widespread disease; the workhorse treatment"],
             ["Excimer laser", "Targeted high-dose light on individual patches",
              "Few, small, localised patches"],
             ["Oral mini-pulse steroids", "Arrests rapidly progressing disease",
              "Actively spreading vitiligo"],
             ["Melanocyte transplant", "Moves your own pigment cells into the patch",
              "Stable disease only, 12 months quiet"],
             ["Punch / blister grafting", "Transplants pigmented skin fragments",
              "Small stable patches, lips, extremities"],
         ],
         "note": "Nothing on this list cures vitiligo. Each is a way of stopping the disease, "
                 "restoring colour, or both, and most patients need more than one."},

        {"kind": "steps", "eyebrow": "The sequence", "h2": "How treatment is actually ordered",
         "items": [
             {"title": "Stop the spread",
              "body": "Active disease is quietened first: usually topicals, sometimes a short "
                      "oral course. Repigmenting skin while new patches appear is running up a "
                      "down escalator."},
             {"title": "Repigment medically",
              "body": "Phototherapy, targeted light and topicals, given long enough to "
                      "judge. Six to eight weeks is a check, not a verdict; three to six "
                      "months is a verdict."},
             {"title": "Reassess what's left",
              "body": "Some patches recolour fully, some partially, some not at all. What "
                      "remains after a proper medical trial is what surgery is for."},
             {"title": "Operate only if stable",
              "body": "Grafting into active disease fails and can trigger new patches at "
                      "the donor site. Twelve quiet months is the threshold."},
         ]},

        {"kind": "split", "eyebrow": "The differentiator",
         "h2": "Surgical repigmentation, which most centres don't offer.",
         "body": ["Melanocyte transplant and punch grafting move your own pigment cells "
                  "into skin that has none left. For stable patches on hands, lips and "
                  "other stubborn sites, it is often the only thing that will work.",
                  "It requires an operating list, the skill to harvest and place cells, and the "
                  "judgement to refuse patients whose disease is not stable. This practice has "
                  "done it for decades, and it began life as a vitiligo hospital, which is why."],
         "cta": ("How graft surgery works", "vitiligo-graft-surgery"),
         "items": [
             {"title": "Stability is the gate",
              "body": "No new patches, no expansion, no koebnerisation for twelve months. "
                      "Being told to wait is a common answer."},
             {"title": "Patients travel for it",
              "body": "Send photographs before booking travel. A video consultation can "
                      "settle whether the trip is worth making."},
         ]},

        {"kind": "cards", "eyebrow": "Read next", "h2": "The rest of this section",
         "items": [
             {"title": "Understanding your vitiligo",
              "list": ["Types and stages: segmental, non-segmental, stable, unstable",
                       "Vitiligo in children",
                       "Diet, myths and what actually has evidence"]},
             {"title": "The treatments in detail",
              "list": ["Narrowband UVB phototherapy",
                       "Excimer laser",
                       "Graft surgery and melanocyte transplant"]},
             {"title": "Practical",
              "list": ["What treatment costs",
                       "Online consultation from anywhere in India",
                       "Vitiligo treatment in Hyderabad"]},
         ]},
    ],
    "faq_h2": "Vitiligo questions",
    "faqs": [
        ("Can vitiligo be cured?",
         ["No. No treatment available anywhere cures vitiligo, and any clinic promising a "
          "cure is making a claim it cannot support.",
          "What treatment does reliably achieve is stopping the spread, and repigmenting a "
          "significant proportion of affected skin in many patients. Particularly on the face "
          "and trunk, and particularly when treated early."]),
        ("Is vitiligo contagious?",
         "No. It is an autoimmune condition, not an infection. It cannot spread by touch, "
         "by sharing food, by using the same towel, or by any other contact."),
        ("Will it spread to the whole body?",
         "Usually not. Most vitiligo remains limited, and the pattern in the first year or "
         "two is broadly predictive. A minority does progress widely, which is precisely why "
         "active disease is treated promptly rather than watched."),
        ("How long does treatment take to show a result?",
         "Facial patches often show the first specks of colour within two to three months of "
         "consistent phototherapy. Hands and feet may take much longer or not respond at "
         "all. Six to eight weeks is the first review, not the deadline."),
        ("Does diet cause vitiligo, or fix it?",
         "No food causes vitiligo, and no diet has been shown to reverse it. The advice "
         "about avoiding citrus, milk and sour foods together is folklore with no evidence "
         "behind it. Eating well matters; a restrictive diet does not."),
        ("Is vitiligo linked to other diseases?",
         "It can be. Thyroid disease is the most common association, which is why thyroid "
         "function is usually checked at the first visit. Diabetes and pernicious anaemia "
         "are less frequent associations."),
        ("Can vitiligo come back after it repigments?",
         "Yes, it can. Repigmented skin can lose colour again, particularly if treatment "
         "stops abruptly or the disease reactivates, which is why maintenance and review "
         "continue after the visible result."),
    ],
    "related": [CROSS, ONLINE,
                ("vitiligo-cost", "What vitiligo treatment costs",
                 "How the money actually works: per session, per course, per graft.")],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-types-and-stages", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("Types and stages", None)],
    "title": "Types & Stages of Vitiligo: Stable or Active | Dr. Varada",
    "meta": "Segmental vs non-segmental vitiligo, stable vs unstable disease. What the "
            "difference means for treatment, and how a dermatologist tells which you have.",
    "eyebrow": "Vitiligo",
    "h1": "Types and stages of vitiligo",
    "lede": "Two classifications matter clinically. One describes the pattern. Segmental or "
            "non-segmental. The other describes the moment. Active or stable. Between them they "
            "decide almost everything about your treatment.",
    "acts": [("Consult online", WHATSAPP), ("Back to the vitiligo hub", "vitiligo")],
    "sources": ["niams-vitiligo", "dermnet-vitiligo", "aad-vitiligo", "iadvl-vitiligo-surgery"],
    "glance": [
        ("Non-segmental", "Symmetrical, both sides, most common"),
        ("Segmental", "One side, one nerve territory, young onset"),
        ("Active", "New or expanding patches within 6–12 months"),
        ("Stable", "No change for 12 months: the surgical gate"),
        ("Assessed by", "History, Wood's lamp, dated photographs"),
        ("Why it matters", "It picks the treatment"),
    ],
    "sections": [
        {"kind": "diagram", "eyebrow": "The two patterns",
         "h2": "One side, or both sides.",
         "intro": "This is the first thing a dermatologist decides, and it changes almost everything that follows. Segmental disease keeps to one side of the body and stops at the midline. Non-segmental appears in matched pairs — the same site on both sides.",
         "caption": "Segmental disease usually becomes stable within a year and is the pattern that responds best to surgical repigmentation. Non-segmental is the immune-driven form, and controlling the immune attack comes before anything else.",
         "rail": True,
"labels": [
    {"text": "One side only", "x": 22, "y": 32, "row": 1, "find": "artwork"},
    {"text": "Stops at the midline", "x": 25, "y": 52, "find": "edge:pale|skin"},
    {"text": "Matched on both sides", "x": 72, "y": 63, "find": "pale"},
    {"text": "Hands, face, knees", "x": 57, "y": 82, "row": 1, "find": "artwork"},
],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/B3-vitiligo-patterns.webp", "w": 1820, "h": 1024,
             "alt": "Two simplified featureless human figures side by side on brown skin. The left figure has pale depigmented patches gathered into a single band running down one side of the face, trunk and arm, stopping abruptly at the midline so the other half is unaffected. The right figure has smaller patches arranged symmetrically — a matching patch at each eye, each elbow, each hand and each knee."}},

        {"kind": "cards", "eyebrow": "By pattern", "h2": "Segmental or non-segmental",
         "accent": "chronic",
         "intro": "These behave so differently that they are almost two conditions sharing "
                  "one name.",
         "items": [
             {"eyebrow": "About 90% of cases", "title": "Non-segmental vitiligo",
              "body": "Symmetrical, if it appears on one knee it tends to appear on the other. "
                      "Comes and goes in waves over years, often starting on the hands, face, "
                      "or around the eyes and mouth.",
              "list": ["Both sides of the body", "Unpredictable course",
                       "Autoimmune associations more common",
                       "Responds to phototherapy"]},
             {"eyebrow": "About 10% of cases", "title": "Segmental vitiligo",
              "body": "Confined to one side, often following a nerve territory, and usually "
                      "starting in childhood or adolescence. It spreads quickly for six to "
                      "twenty-four months, then typically stops for good.",
              "list": ["One side only", "Early onset", "Burns out and stabilises",
                       "The best candidate for surgery"]},
         ]},

        {"kind": "callout", "title": "Segmental vitiligo is the surgical success story",
         "body": "Because it stabilises reliably and rarely returns, segmental disease is where "
                 "grafting gives its most durable results. It also responds poorly to "
                 "phototherapy, so recognising it early saves patients months of light "
                 "treatment that was never going to work."},

        {"kind": "diagram", "eyebrow": "Reading the edge",
         "h2": "The border tells you what it is doing.",
         "intro": "Whether the disease is currently spreading is read from the margin of the patch, not from how large it is. An advancing edge fades; a settled one is drawn.",
         "caption": "This is why the twelve-month wait before surgery is not caution for its own sake. Grafting into active disease means the same immune process destroys the transplanted cells.",
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
             "alt": "Two areas of brown skin seen from above. The left patch has a soft ill-defined border fading gradually into the surrounding skin, with tiny separate pale dots scattered outside it and one straight pale streak crossing the skin nearby. The right patch has a single crisp border, no scattered dots, and several small round islands of returning brown pigment inside it, each centred on a hair."}},

        {"kind": "prose", "eyebrow": "By activity", "h2": "Active or stable: the real question",
         "body": [
             "Every treatment decision hangs on this. Active disease must be quietened "
             "before anything is rebuilt; stable disease can be rebuilt, including "
             "surgically. Getting it wrong in either direction wastes months.",
             "There is no blood test for stability. It is a clinical judgement made from the "
             "history, the appearance of the patch margins, and, most reliably, photographs "
             "taken at intervals and compared properly.",
         ]},

        {"kind": "diagram", "eyebrow": "What the lamp shows",
         "h2": "More patches than you can see.",
         "intro": "A Wood's lamp is a handheld ultraviolet light. Under it, skin that has lost pigment fluoresces bright chalk-white with a sharp border, while normal skin stays dark — so patches that are invisible in ordinary light, and edges that look vague, both become obvious.",
         "caption": "This is how the true extent of the disease is judged, and how a vague-looking border is confirmed as genuinely advancing. It is also the examination most often skipped.",
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
             "alt": "The same patch of brown forearm skin shown twice. In ordinary daylight two pale patches are faint and low in contrast with soft edges. Under a handheld lamp casting a violet glow, the same two patches stand out as sharp-edged chalk-white areas — and three more patches are visible that could not be seen at all in daylight."}},

        {"kind": "table", "eyebrow": "Telling them apart",
         "h2": "What suggests active disease",
         "head": ["Sign", "What it means", "What it changes"],
         "rows": [
             ["New patches in 6 months", "The disease is producing fresh lesions",
              "Stop the spread before repigmenting"],
             ["Blurred, ill-defined edges", "The patch is expanding outward",
              "Surgery deferred"],
             ["Trichrome appearance", "A pale zone between normal and white skin",
              "Marker of ongoing activity"],
             ["Koebner phenomenon", "New patches where skin was cut or scratched",
              "A strong argument against grafting now"],
             ["Confetti-like macules", "Small scattered spots around a patch",
              "Suggests rapid progression"],
             ["White hairs in the patch", "Follicular pigment reserve is depleted",
              "Medical repigmentation less likely to work"],
         ],
         "note": "None of these is decisive alone. A Wood's lamp examination and dated "
                 "photographs together are how the judgement is actually made."},

        {"kind": "split", "eyebrow": "The stability clock",
         "h2": "Why twelve months, and not six.",
         "body": ["Grafting into disease that is still active does two things, both bad: "
                  "the transplanted cells are attacked like the original ones, and the "
                  "donor site can develop its own patch.",
                  "Twelve months without a new patch, without expansion at any margin, and "
                  "without koebnerisation is the accepted threshold. It is not an arbitrary "
                  "wait. It is the interval that separates a graft that takes from a graft that "
                  "fails."],
         "cta": ("What graft surgery involves", "vitiligo-graft-surgery"),
         "items": [
             {"title": "The clock restarts",
              "body": "One new patch in month ten resets the count. This is frustrating and "
                      "it is also the honest answer."},
             {"title": "Photographs settle it",
              "body": "Dated images at fixed distance and lighting are worth more than "
                      "anyone's recollection of what the patch looked like last year."},
         ]},

        {"kind": "checklist", "eyebrow": "Other patterns you may be told",
         "h2": "Terms that appear in reports.",
         "items": [
             "<b>Focal</b>: one or a few patches, not yet classifiable",
             "<b>Acrofacial</b>: face plus fingers and toes",
             "<b>Mucosal</b>: lips and genitals; notoriously stubborn",
             "<b>Universal</b>: over 80% of the body depigmented",
             "<b>Trichrome</b>: three shades in one patch; a sign of activity",
             "<b>Halo naevus</b>: a pale ring around a mole; often coexists",
         ]},
    ],
    "faq_h2": "Types and stages",
    "faqs": [
        ("How do I know if my vitiligo is stable?",
         "If no new patch has appeared and no existing patch has grown for twelve months, and "
         "cuts or scratches have not turned white, it is likely stable. It is confirmed "
         "clinically with a Wood's lamp and by comparing dated photographs. Not by how it feels "
         "to you."),
        ("Which type of vitiligo responds best to treatment?",
         "Non-segmental vitiligo on the face and trunk responds best to phototherapy. "
         "Segmental vitiligo responds poorly to light but does very well with surgery once "
         "it has burnt out."),
        ("Does segmental vitiligo spread to the rest of the body?",
         "Typically not. It spreads within its segment for six to twenty-four months and "
         "then usually stops permanently. That predictability is what makes it a good "
         "surgical candidate."),
        ("What is the Koebner phenomenon?",
         "New vitiligo appearing exactly where the skin was injured: a cut, a scratch, a burn, "
         "a tight strap. It is a marker of active disease and an argument against operating "
         "until things settle."),
        ("Can the type change over time?",
         "Segmental disease does not usually become non-segmental. But a person can have both, "
         "and focal disease that has not declared itself may evolve into either, which is why "
         "the first classification is sometimes provisional."),
    ],
    "related": [
        ("vitiligo-graft-surgery", "Graft surgery", "What stable disease makes possible."),
        ("vitiligo-phototherapy", "NB-UVB phototherapy", "The workhorse for non-segmental disease."),
        ("vitiligo-children", "Vitiligo in children", "Where segmental disease usually starts."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-phototherapy", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("Phototherapy", None)],
    "title": "Narrowband UVB Phototherapy for Vitiligo | Dr. Varada",
    "meta": "How narrowband UVB works for vitiligo, how many sessions it takes, what results to "
            "expect by body site, and whether home units are worth it.",
    "eyebrow": "Vitiligo · Treatment",
    "h1": "Narrowband UVB phototherapy",
    "sources": ["aad-vitiligo-tx", "dermnet-phototherapy", "dermnet-vitiligo", "niams-vitiligo"],
    "lede": "The most widely used vitiligo treatment in the world, and the one with the most "
            "evidence behind it. It works by waking up the pigment cells still living in your "
            "hair follicles, which is also the reason it works on some sites and not others.",
    "acts": [("Consult online", WHATSAPP), ("Back to the vitiligo hub", "vitiligo")],
    "glance": [
        ("What it is", "311 nm ultraviolet B, whole-body or targeted"),
        ("Frequency", "2–3 sessions a week"),
        ("First verdict", "3 months, not 3 weeks"),
        ("Full course", "Often 6–12 months"),
        ("Responds best", "Face, neck, trunk"),
        ("Responds least", "Hands, feet, lips"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How it works",
         "h2": "Light that recruits the cells you still have.",
         "body": [
             "Narrowband UVB is ultraviolet light at a very specific wavelength. Around 311 "
             "nanometres. At that wavelength it does two useful things at once: it damps down "
             "the local immune attack that is destroying pigment cells, and it stimulates the "
             "melanocytes that survive in hair follicles to multiply and migrate up into the "
             "skin surface.",
             "That second mechanism explains the pattern of results. Repigmentation "
             "typically appears first as small dark dots scattered inside the patch, each "
             "one centred on a hair. Those dots enlarge and merge. It is slow, and it looks "
             "odd halfway through, and it is exactly what success looks like.",
             "It also explains the failures. Skin with few hair follicles (fingertips, the "
             "backs of the hands, lips), has little to recruit from. And a patch whose hairs "
             "have themselves gone white has lost its reservoir. Those are the patches that "
             "need surgery rather than more light.",
         ]},

        {"kind": "diagram", "eyebrow": "The mechanism",
         "h2": "Light that reaches exactly far enough.",
         "intro": "Narrowband ultraviolet penetrates the epidermis and the top of the dermis and stops there. In that zone it does two useful things at once: it calms the immune cells attacking pigment, and it stimulates the pigment cells that survive.",
         "caption": "It is not sunbathing and it is not a tanning bed. The wavelength is narrow, the dose is measured, and the depth it reaches is why it is safe to repeat.",
         "labels": [
             {"text": "Ultraviolet enters here", "x": 47, "y": 23, "lead": 10, "find": "artwork"},
             {"text": "Pigment cells reactivated", "x": 29, "y": 40, "lead": 29, "find": "artwork"},
             {"text": "Immune cells suppressed, and no deeper", "x": 38, "y": 52, "lead": 20, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D1-phototherapy.webp", "w": 1820, "h": 1024,
             "alt": "A block of skin with a band of fine parallel light rays entering from above. The rays penetrate the epidermis and stop in the upper dermis, forming a clearly bounded lit zone that does not reach the fat. Inside that zone immune cells are breaking apart while the star-shaped pigment cells at the base of the epidermis are enlarged and active, releasing dark granules upward."}},

        {"kind": "steps", "eyebrow": "A course", "h2": "What the schedule looks like",
         "items": [
             {"title": "Start low, build up",
              "body": "The first dose is deliberately conservative and increased session by "
                      "session until the skin shows a faint pinkness that fades within a "
                      "day. That threshold is individual."},
             {"title": "Two or three times a week",
              "body": "Consistency matters more than intensity. Two sessions a week for "
                      "six months beats five sessions a week for three."},
             {"title": "First honest review at three months",
              "body": "Perifollicular dots by month three is a good sign. Nothing at all by "
                      "month four on responsive sites means the plan changes."},
             {"title": "Taper, don't stop",
              "body": "Frequency is reduced gradually once colour is established. Abrupt "
                      "stopping is a common reason repigmented skin fades again."},
         ]},

        {"kind": "table", "eyebrow": "By site", "h2": "What responds, and what doesn't",
         "intro": "This is the single most useful table for setting expectations, and the "
                  "one most patients are never shown.",
         "head": ["Body site", "Typical response", "Why"],
         "rows": [
             ["Face and neck", "Best: often substantial",
              "Dense hair follicles, good blood supply"],
             ["Trunk", "Good", "Adequate follicular reservoir"],
             ["Upper arms and thighs", "Moderate", "Fewer follicles, slower migration"],
             ["Backs of hands and feet", "Poor", "Sparse follicles, thick skin"],
             ["Fingertips and toes", "Very poor", "Almost no follicular reservoir"],
             ["Lips", "Very poor", "No hair follicles at all"],
             ["Patches with white hairs", "Poor at any site", "Reservoir already lost"],
         ],
         "note": "Sites in the bottom half of this table are where melanocyte transplant and "
                 "punch grafting are considered instead. Not as a fallback, but as the "
                 "appropriate first choice."},

        {"kind": "split", "eyebrow": "Home units",
         "h2": "Are home phototherapy devices worth it?",
         "body": ["For the right patient, genuinely yes. A handheld or panel unit removes "
                  "the travel burden that causes most courses to be abandoned, and "
                  "adherence is the strongest predictor of result.",
                  "For the wrong patient it is money spent on burning yourself. Home units "
                  "are appropriate once the dose has been established in clinic, when the "
                  "patches are countable and reachable, and when someone is prepared to "
                  "keep a log. They are not appropriate as a first step, unsupervised, or "
                  "for widespread disease."],
         "cta": ("Ask whether a home unit suits you", WHATSAPP),
         "items": [
             {"title": "Dose is set in clinic first",
              "body": "The starting dose depends on your skin type and your response. "
                      "Guessing it at home is how burns happen."},
             {"title": "A log, or it didn't happen",
              "body": "Date, duration, site, and any redness. Without it there is no way "
                      "to judge whether the plan is working."},
         ]},

        {"kind": "checklist", "eyebrow": "Safety", "h2": "What to expect, and what to report.",
         "items": [
             "<b>Mild pinkness</b> that fades in a day. Expected, and the target",
             "<b>Dryness and itch</b>: common, managed with moisturiser",
             "<b>Burning or blistering</b>: report it; the dose is too high",
             "<b>Tanning of normal skin</b>: expected; contrast increases before it decreases",
             "<b>Eye protection</b>: goggles at every session, no exceptions",
             "<b>Photosensitising drugs</b>: tell the clinic about every medicine you take",
         ]},

        {"kind": "callout", "warn": True, "title": "Contrast gets worse before it gets better",
         "body": "Phototherapy tans the normal skin around a patch as well as repigmenting "
                 "the patch itself. For the first weeks the patches can look more obvious, "
                 "not less. This is expected and it is not a sign the treatment is failing."},
    ],
    "faq_h2": "Phototherapy questions",
    "faqs": [
        ("How many phototherapy sessions will I need?",
         "Most courses run six to twelve months at two to three sessions a week, so "
         "typically 50 to 150 sessions. Facial patches often show first change by month "
         "three; extremities may need far longer or may not respond at all."),
        ("Is narrowband UVB safe long-term?",
         "It has the best long-term safety record of the ultraviolet treatments and is used "
         "in children and in pregnancy where needed. Cumulative exposure is still tracked, "
         "and total lifetime sessions are kept in the record."),
        ("Can I use a tanning bed instead?",
         "No. Tanning beds emit mostly UVA at uncontrolled doses. They do not deliver the "
         "311 nm narrowband wavelength, they raise skin cancer risk, and they will not "
         "repigment vitiligo."),
        ("Does phototherapy hurt?",
         "No. A session is short, seconds to a few minutes, and feels like standing in warm "
         "light. Mild pinkness afterwards is the intended endpoint; pain or blistering means "
         "the dose needs reducing."),
        ("Will the colour stay after I stop?",
         "Often yes, particularly if the course is tapered rather than stopped abruptly and "
         "the disease is stable. Some patients lose a proportion of the repigmentation and "
         "need maintenance sessions."),
        ("Can I combine it with creams?",
         "Yes, combining phototherapy with a topical calcineurin inhibitor or a topical JAK "
         "inhibitor generally works better than either alone, particularly on the face."),
    ],
    "related": [
        ("vitiligo-excimer-laser", "Excimer laser", "Targeted light for a few small patches."),
        ("vitiligo-graft-surgery", "Graft surgery", "For the sites light cannot reach."),
        ("vitiligo-cost", "What it costs", "Per session, per course, and what's included."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-excimer-laser", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("Excimer laser", None)],
    "title": "Excimer Laser for Vitiligo: Who It Suits | Dr. Varada",
    "meta": "Excimer laser for vitiligo: how 308 nm targeted light differs from full-body "
            "NB-UVB, who it suits, how many sessions, and how the two compare on cost.",
    "eyebrow": "Vitiligo · Treatment",
    "h1": "Excimer laser for vitiligo",
    "lede": "Same idea as phototherapy, delivered differently: a 308 nm beam aimed only at the "
            "patch. That precision buys higher doses and faster results on small areas, and "
            "makes it the wrong tool for widespread disease.",
    "acts": [("Consult online", WHATSAPP), ("Back to the vitiligo hub", "vitiligo")],
    "sources": ["aad-vitiligo-tx", "dermnet-phototherapy", "dermnet-vitiligo", "nhs-vitiligo"],
    "glance": [
        ("What it is", "308 nm targeted ultraviolet light"),
        ("Best for", "A few small patches, especially facial"),
        ("Frequency", "2 sessions a week"),
        ("Typical course", "24–48 sessions"),
        ("First signs", "Often by 8–12 sessions on the face"),
        ("Not for", "Widespread or unstable disease"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How it differs",
         "h2": "Precision, and what precision buys.",
         "body": [
             "Narrowband UVB treats the whole body, which means the dose is limited by what "
             "your normal skin can tolerate. Excimer treats only the patch, so the dose can "
             "be pushed considerably higher without burning the skin around it.",
             "Two practical consequences follow. Results generally come faster. Facial patches "
             "often show the first pigment within eight to twelve sessions rather than three "
             "months. And the normal skin is not tanned, so the contrast problem that makes "
             "early phototherapy look discouraging largely disappears.",
             "The trade is coverage. Treating a large surface patch by patch is slow and "
             "expensive, which is why excimer is chosen for a handful of stubborn areas and "
             "narrowband UVB for anything widespread. Many patients have both. Full-body light "
             "for the general disease, excimer for the two patches that won't shift.",
         ]},

        {"kind": "diagram", "eyebrow": "Two ways to deliver light",
         "h2": "A beam, or a room.",
         "intro": "Both use ultraviolet light to stimulate pigment cells. The difference is what else gets treated. A targeted handpiece doses one patch at a higher intensity; a cabinet doses everything at once.",
         "caption": "Targeted light suits a few small patches and spares the normal skin between them. Once the disease is widespread, treating each patch separately stops being practical and the cabinet is the sensible tool.",
         "rail": True,
"labels": [
    {"text": "Skin beside it is spared", "x": 13, "y": 48, "row": 1, "find": "artwork"},
    {"text": "One patch, one beam", "x": 24, "y": 25, "find": "artwork"},
    {"text": "The whole body at once", "x": 63, "y": 30, "row": 1, "find": "artwork"},
    {"text": "Normal skin too", "x": 75, "y": 68, "find": "artwork"},
],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D2-excimer-vs-cabinet.webp", "w": 1820, "h": 1024,
             "alt": "Two panels. On the left a handheld treatment head is held above a block of brown skin and sends a narrow cone of pale light down onto one small depigmented patch, leaving the skin around it unlit. On the right a tall three-sided cabinet lined with vertical light tubes holds a plain featureless mannequin in simple clothing; light fills the whole cabinet and reaches its arms, legs and head evenly, with several pale patches lit along with all the surface around them."}},

        {"kind": "table", "eyebrow": "Side by side", "h2": "Excimer or NB-UVB?",
         "head": ["", "Excimer laser", "Narrowband UVB"],
         "rows": [
             ["Area treated", "Individual patches only", "Whole body or large regions"],
             ["Dose per session", "Higher: normal skin spared", "Limited by normal skin"],
             ["First visible change", "Often 8–12 sessions", "Usually 2–3 months"],
             ["Normal skin tanning", "Minimal", "Expected"],
             ["Best for", "Few, small, localised patches", "Widespread disease"],
             ["Cost per session", "Higher", "Lower"],
             ["Cost per course", "Depends on area treated", "Predictable"],
         ],
         "note": "These are not competitors. On a patient with scattered disease plus two "
                 "stubborn facial patches, using both is the correct answer."},

        {"kind": "steps", "eyebrow": "A course", "h2": "What treatment involves",
         "items": [
             {"title": "A test dose",
              "body": "The first session establishes how your skin responds. Everything "
                      "after is titrated against that."},
             {"title": "Twice a week",
              "body": "Sessions are short: the beam is applied patch by patch, often only "
                      "seconds each. Most appointments take minutes."},
             {"title": "Reviewed at 12 sessions",
              "body": "Facial patches showing perifollicular dots by then are on track. No "
                      "change at all after 20 sessions is a reason to reconsider."},
             {"title": "Stop or hand over",
              "body": "Once the patch has recoloured, treatment stops. Patches that do not "
                      "respond are assessed for grafting instead."},
         ]},

        {"kind": "split", "eyebrow": "Honest limits",
         "h2": "Where excimer will not help.",
         "body": ["Excimer is light, and light works by recruiting pigment cells from hair "
                  "follicles. Where that reservoir is gone, more light, however precisely "
                  "aimed, does not create it.",
                  "Patches with white hairs, lips, and fingertips remain poor responders "
                  "with excimer just as they are with narrowband UVB. Being told that at "
                  "the start saves twenty sessions of finding out."],
         "cta": ("What works on those sites", "vitiligo-graft-surgery"),
         "items": [
             {"title": "White hairs in the patch",
              "body": "The follicular reservoir is depleted. Surgery is the option that "
                      "brings pigment cells from elsewhere."},
             {"title": "Active disease",
              "body": "Spreading vitiligo is quietened first. Repigmenting one patch while "
                      "three more appear is not progress."},
         ]},

        {"kind": "callout", "title": "Combining improves the odds",
         "body": "Excimer paired with a topical calcineurin inhibitor or topical JAK "
                 "inhibitor consistently outperforms excimer alone, particularly on facial "
                 "patches. The cream is applied between sessions, not immediately before."},
    ],
    "faq_h2": "Excimer laser questions",
    "faqs": [
        ("How many excimer sessions are needed?",
         "Typically 24 to 48, at two sessions a week. Facial patches often need fewer; "
         "patches on the limbs need more, and some need to be reassessed for surgery "
         "instead."),
        ("Is excimer better than phototherapy?",
         "Not better. Different. Excimer is faster and more precise for a few small patches. "
         "Narrowband UVB is the right choice for widespread disease. For many patients the "
         "correct plan uses both."),
        ("Does excimer laser hurt?",
         "Very little. Most patients describe warmth. Mild pinkness for a day afterwards is "
         "the intended response; blistering means the dose was too high and is adjusted."),
        ("Can excimer treat lips or fingertips?",
         "It can be aimed there, but response is poor because those sites have little or no "
         "follicular pigment reserve. Grafting is usually the more realistic option."),
        ("Is it safe for children?",
         "Yes, and its precision is an advantage in children because total-body ultraviolet "
         "exposure is avoided. Cooperation with goggles is the practical limiting factor."),
    ],
    "related": [
        ("vitiligo-phototherapy", "NB-UVB phototherapy", "The whole-body alternative."),
        ("vitiligo-cost", "What it costs", "How per-session pricing works."),
        CROSS,
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-graft-surgery", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("Graft surgery", None)],
    "title": "Vitiligo Graft Surgery & Melanocyte Transplant | Dr. Varada",
    "meta": "Melanocyte transplant, punch and blister grafting for stable vitiligo, who "
            "qualifies, how each technique works, recovery, and why stability decides it.",
    "eyebrow": "Vitiligo · Surgery",
    "h1": "Vitiligo graft surgery",
    "lede": "When a patch has no pigment cells left to wake up, the only remaining option is to "
            "bring them from somewhere else on your own body. That is what these operations do, "
            "and they only work on disease that has stopped moving.",
    "acts": [("Send photographs first", WHATSAPP), ("Call the clinic", PHONE)],
    "sources": ["iadvl-vitiligo-surgery", "iadvl-vitiligo-surgery-std", "aad-vitiligo-tx", "dermnet-vitiligo"],
    "glance": [
        ("Who qualifies", "Stable for 12 months, no koebnerisation"),
        ("Techniques", "Melanocyte, punch, blister, follicular unit"),
        ("Donor site", "Usually the thigh or buttock"),
        ("Anaesthesia", "Local"),
        ("Colour appears", "Weeks to a few months"),
        ("Not offered for", "Active or spreading disease"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The principle",
         "h2": "Moving your own pigment cells, not adding dye.",
         "body": [
             "These are transplant operations, not tattoos. Healthy pigmented skin is taken "
             "from an inconspicuous donor site, usually the thigh, and the melanocytes within "
             "it are transferred to the depigmented patch, where they establish themselves and "
             "start producing pigment again.",
             "Because the cells are your own, the colour they produce is your own. It "
             "matures over weeks to months, and a good result is one you stop noticing.",
             "The absolute requirement is stability. Transplanted melanocytes are the same "
             "cells the immune system was attacking; put them into active disease and they "
             "are destroyed, while the donor site may develop a patch of its own. That is "
             "why the assessment is more important than the operation.",
         ]},

        {"kind": "diagram", "eyebrow": "The operation",
         "h2": "What a melanocyte transplant actually involves.",
         "intro": "A thin shaving of your own pigmented skin is taken from the thigh, separated into a suspension of individual pigment cells, and applied to the patch after its surface has been prepared. A small donor area can cover a much larger one.",
         "caption": "The colour that grows in is your own, because the cells are your own. It matures over weeks to months. None of this is worth doing while the disease is still active — the same immune system would destroy the new cells too.",
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
             "alt": "Four stages of a melanocyte transplant shown left to right. First, a very thin sheet of pigmented skin is lifted from a donor site with a fine blade. Second, that sheet is separated in a dish of fluid into a suspension of individual brown pigment cells. Third, the pale depigmented patch has its surface abraded by a small rotating burr. Fourth, the same patch has healed to the same brown as the skin around it, with only a faint outline showing where it was."}},

        {"kind": "diagram", "eyebrow": "The four operations",
         "h2": "Four ways to move the same thing.",
         "intro": "All four take pigmented skin from a donor site and put its pigment cells onto the patch. They differ in how much area one donor site can cover, and in how fine the result is.",
         "caption": "Cell suspension covers the largest area from the smallest donor site, which is why it suits extensive patches. Punch grafting is simplest but can leave a cobblestoned surface. The choice follows the site and the size, not preference.",
         "label_col": 0,
         "labels": [
             {"text": "Mini-punch", "x": 14, "y": 80, "lead": 2},
             {"text": "Blister roof", "x": 34, "y": 80, "lead": 2},
             {"text": "Thin sheet", "x": 55, "y": 80, "lead": 2},
             {"text": "Cell suspension", "x": 76, "y": 80, "lead": 2},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D4-graft-techniques.webp", "w": 1820, "h": 1024,
             "alt": "Four techniques in columns, each with a block of brown donor skin above and the pale recipient patch receiving it below. First, small round plugs of skin are lifted out of the donor block and set into matching holes in the patch. Second, a dome-shaped blister is raised on the donor and its thin roof laid over the patch. Third, a thin wide sheet is shaved off the donor with a blade and laid over the patch. Fourth, donor skin in a shallow dish has become a suspension of separate pigment cells, spread as a film across the patch."}},

        {"kind": "cards", "eyebrow": "The techniques", "h2": "Four operations, different jobs",
         "accent": "chronic",
         "items": [
             {"eyebrow": "Cell suspension", "title": "Melanocyte transplant",
              "body": "A small piece of donor skin is processed into a suspension of "
                      "pigment cells, which is applied to the prepared patch. A small donor "
                      "area can cover a much larger recipient area.",
              "list": ["Best area-to-donor ratio", "Good colour blending",
                       "Suits larger stable patches"]},
             {"eyebrow": "Mini-punch", "title": "Punch grafting",
              "body": "Tiny cores of pigmented skin are placed into matching holes in the "
                      "patch, a few millimetres apart. Pigment spreads outward from each "
                      "one until the areas merge.",
              "list": ["Simple and durable", "Good for small patches",
                       "Can leave a cobblestone texture"]},
             {"eyebrow": "Epidermal", "title": "Blister grafting",
              "body": "Suction raises blisters on the donor site; the thin roofs are lifted "
                      "and laid onto the patch after its surface is removed.",
              "list": ["Very good colour match", "Minimal donor scarring",
                       "Limited by blister size"]},
             {"eyebrow": "Hair follicle", "title": "Follicular unit transplant",
              "body": "Follicular units are transplanted into the patch. The reservoir of "
                      "pigment cells sits in the hair follicle itself, so this addresses the "
                      "one problem the other three cannot. White hair growing within the patch.",
              "list": ["For leucotrichia: white hair in the patch",
                       "Suits eyebrow, beard and scalp sites",
                       "Repigments the hair as well as the skin"]},
         ]},

        {"kind": "steps", "eyebrow": "The pathway", "h2": "From first photograph to result",
         "items": [
             {"title": "Assessment",
              "body": "History, examination, Wood's lamp and dated photographs establish "
                      "whether the disease has genuinely been quiet for twelve months."},
             {"title": "A test graft, sometimes",
              "body": "For borderline cases a small trial graft is placed and watched. It "
                      "answers the stability question more reliably than any argument."},
             {"title": "The procedure",
              "body": "Done under local anaesthetic as a day case. The patch is prepared, "
                      "the graft placed, and both sites dressed."},
             {"title": "Healing and colour",
              "body": "Dressings stay undisturbed for several days. Pigment appears over "
                      "weeks and continues to spread and blend for months."},
         ]},

        {"kind": "split", "eyebrow": "Being refused",
         "h2": "Why 'not yet' is a real answer.",
         "body": ["A significant proportion of people who ask about vitiligo surgery are "
                  "told to wait, and that is a clinical decision rather than a scheduling "
                  "one. Operating on unstable disease produces a failed graft, a "
                  "disappointed patient, and sometimes a new patch where the donor skin "
                  "was taken.",
                  "If you are told to wait, the interval is used: the disease is treated "
                  "medically to bring it under control, and photographs are taken so the "
                  "twelve-month clock can be judged properly rather than remembered."],
         "cta": ("How stability is assessed", "vitiligo-types-and-stages"),
         "items": [
             {"title": "Segmental disease qualifies soonest",
              "body": "It burns out reliably, which is why it produces the most durable "
                      "surgical results."},
             {"title": "Lips and fingertips are the point",
              "body": "These sites barely respond to light. Surgery is not the fallback there. "
                      "It is the appropriate first choice."},
         ]},

        {"kind": "checklist", "eyebrow": "Before you travel",
         "h2": "If you are coming from outside Hyderabad.",
         "items": [
             "<b>Send photographs first</b>: daylight, close and wide, of every patch",
             "<b>Say when each patch appeared</b> and when it last changed",
             "<b>Send older photographs</b> if you have them; they date the stability",
             "<b>Expect two visits</b>: assessment, then the procedure",
             "<b>Allow for review</b>: grafts are checked after healing",
             "<b>Be prepared to be told to wait</b>: it is a common outcome",
         ]},

        {"kind": "callout", "warn": True, "title": "What surgery does not do",
         "body": "It repigments the patch it treats. It does not cure vitiligo, does not "
                 "stop new patches appearing elsewhere, and does not remove the need for "
                 "ongoing review. Anyone describing it as a permanent cure is overstating it."},
    ],
    "faq_h2": "Graft surgery questions",
    "faqs": [
        ("Am I a candidate for vitiligo surgery?",
         ["Only if your disease has been stable for about twelve months: no new patches, no "
          "expansion of existing ones, and no depigmentation appearing where skin has been cut "
          "or scratched.",
          "Segmental vitiligo that has burnt out is the classic good candidate. Patches on "
          "the lips, fingertips and other sites that light cannot reach are the usual "
          "reason for choosing surgery."]),
        ("Is the result permanent?",
         "The transplanted pigment cells generally persist, and results in stable segmental "
         "disease are durable over years. But vitiligo can reactivate, and a graft does not "
         "protect against new patches elsewhere."),
        ("Will the colour match?",
         "Usually well, because the pigment is your own. It matures over months. Punch "
         "grafting can leave a slightly uneven texture; melanocyte transplant and blister "
         "grafting generally blend better."),
        ("Does it leave a scar at the donor site?",
         "Blister grafting leaves very little. Punch grafting leaves small marks in a "
         "concealed area. The donor site is chosen so that anything visible is hidden by "
         "clothing."),
        ("Is it done under general anaesthetic?",
         "No. Local anaesthetic, as a day procedure. You go home the same day."),
        ("How soon will I see colour?",
         "Pigment usually starts appearing within a few weeks and continues to spread and "
         "even out for several months. Judging the result before three months is premature."),
        ("What if my vitiligo isn't stable yet?",
         "Then surgery is deferred and the disease is treated medically first. The waiting "
         "period is not wasted. It is used to stop the spread and to build the photographic "
         "record that establishes when the clock started."),
    ],
    "related": [CROSS,
                ("vitiligo-types-and-stages", "Stable or unstable?",
                 "How the twelve-month judgement is actually made."),
                ("travelling-for-treatment", "Travelling here for surgery",
                 "What to send before you book, and how a staged visit works.")],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-children", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("In children", None)],
    "title": "Vitiligo in Children: Treatment Guide | Dr. Varada",
    "meta": "Childhood vitiligo: how it differs from adult disease, which treatments are safe "
            "in children, what to tell the school, and why early treatment matters.",
    "eyebrow": "Vitiligo",
    "h1": "Vitiligo in children",
    "lede": "Around half of all vitiligo begins before the age of twenty. Children respond "
            "better to treatment than adults do, and carry more of the social weight of the "
            "condition, which makes treating it early doubly worth doing.",
    "acts": [("Consult online", WHATSAPP), ("Call the clinic", PHONE)],
    "sources": ["niams-vitiligo", "aad-vitiligo", "dermnet-vitiligo", "nhs-vitiligo"],
    "glance": [
        ("Onset", "About half of cases start under 20"),
        ("Common type", "Segmental more frequent than in adults"),
        ("Response", "Generally better than adults"),
        ("First-line", "Topicals; phototherapy when needed"),
        ("Checked for", "Thyroid function"),
        ("Surgery", "Deferred until disease is stable"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How it differs",
         "h2": "Not simply adult vitiligo in a smaller person.",
         "body": [
             "Childhood vitiligo has its own pattern. Segmental disease, confined to one side "
             "of the body, is proportionally more common than in adults. A family history is "
             "found more often. And a personal or family history of thyroid disease is common "
             "enough that thyroid function is checked as a matter of routine.",
             "The encouraging part is that children generally respond better. Skin heals "
             "faster, follicular reservoirs are richer, and disease caught in its first "
             "months responds better than disease that has been present for years. Early "
             "treatment is not a marketing line here; it is the single biggest variable a "
             "family controls.",
             "The hard part is not medical. A visible patch in a school-age child is a "
             "social problem before it is a dermatological one, and the consultation has to "
             "address both or it has only done half the job.",
         ]},

        {"kind": "diagram", "eyebrow": "What is affected",
         "h2": "The cell a child has lost.",
         "intro": "It helps to know what is actually missing. Colour is made by one cell type sitting at the base of the epidermis, which hands packets of pigment out to the skin cells around it. Vitiligo is the loss of those cells — nothing the child ate, did, or caught.",
         "caption": "Children repigment better than adults, and the face and neck respond best of all. That is worth saying early, because the first question a parent asks is almost always whether the colour will come back.",
         "labels": [
             {"text": "Pigment cap over each nucleus", "x": 40, "y": 33, "lead": 21, "find": "artwork"},
             {"text": "Packets travelling along the arm", "x": 34, "y": 47, "lead": 27, "find": "artwork"},
             {"text": "Arms reaching between cells", "x": 46, "y": 57, "lead": 15, "find": "artwork"},
             {"text": "Melanocyte", "x": 31, "y": 74, "lead": 30, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/A2-melanocyte.webp", "w": 1820, "h": 1024,
             "alt": "A melanocyte at the base of the epidermis, drawn as a star-shaped cell with long arms reaching up between the surrounding skin cells. Dark brown pigment granules are made inside it, travel along its arms and are handed into neighbouring cells, where they gather into a cap above each nucleus."}},

        {"kind": "table", "eyebrow": "Treatment", "h2": "What is used, and at what age",
         "head": ["Treatment", "Use in children", "Notes"],
         "rows": [
             ["Topical steroids", "Yes, short courses",
              "Potency and duration limited; skin thinning is the risk"],
             ["Calcineurin inhibitors", "Yes: often first choice on the face",
              "No skin thinning; suits eyelids and folds"],
             ["Topical JAK inhibitors", "In selected older children",
              "Prescribed and monitored case by case"],
             ["Narrowband UVB", "Yes, when patches are widespread",
              "Practical limit is whether the child can stand still with goggles"],
             ["Excimer laser", "Yes, for a few patches",
              "Avoids whole-body exposure; sessions are seconds long"],
             ["Oral steroids", "Rarely, and only for rapid spread",
              "Short, supervised courses"],
             ["Graft surgery", "Deferred until stable",
              "Segmental disease that has burnt out is the usual indication"],
         ],
         "note": "Every one of these is a prescription decision made after examination. "
                 "Potent topical steroids used unsupervised on a child's face cause harm "
                 "that outlasts the vitiligo."},

        {"kind": "split", "eyebrow": "Beyond the skin",
         "h2": "The part of the consultation that isn't dermatology.",
         "body": ["Children with visible vitiligo report being asked about it constantly, being "
                  "avoided, and, in India especially, encountering adults who believe it is "
                  "contagious or a punishment. None of that is treated by a cream.",
                  "What helps is giving the child a short, accurate sentence they can say "
                  "themselves, and giving the school the same information in writing. "
                  "Children who can explain their condition confidently are asked about it "
                  "far less."],
         "cta": ("Myths worth correcting", "vitiligo-diet-and-myths"),
         "items": [
             {"title": "A sentence that works",
              "body": "\"It's called vitiligo. My skin stopped making colour in some "
                      "places. You can't catch it.\" Rehearsed, it ends most conversations."},
             {"title": "Tell the school",
              "body": "A note explaining that it is not contagious and needs no restriction "
                      "prevents most of the problems before they start."},
         ]},

        {"kind": "checklist", "eyebrow": "Practical", "h2": "What parents ask about most.",
         "items": [
             "<b>Sun protection</b>: depigmented skin burns; sunscreen daily",
             "<b>Swimming and sport</b>: no restriction whatsoever",
             "<b>Camouflage</b>: cosmetic cover is reasonable if the child wants it",
             "<b>Diet</b>: no food causes it; no restriction helps",
             "<b>Thyroid</b>: checked at diagnosis and periodically",
             "<b>Photographs</b>: take dated ones; they settle the stability question",
         ]},

        {"kind": "callout", "warn": True, "title": "Steroid creams bought without a prescription",
         "body": "Potent topical steroids are freely sold in India and are frequently applied "
                 "to children's faces for months. The result is thinned skin, visible "
                 "vessels and stretch marks that do not reverse. Any steroid on a child's "
                 "face should be prescribed, potency-appropriate and time-limited."},
    ],
    "faq_h2": "Vitiligo in children",
    "faqs": [
        ("Will my child's vitiligo spread?",
         "It may, and the first year or two is broadly indicative. Segmental vitiligo tends "
         "to spread within its area for six to twenty-four months and then stop. "
         "Non-segmental disease is less predictable, which is why active disease is treated "
         "promptly."),
        ("Is vitiligo in children curable?",
         "No. Vitiligo is not curable at any age. But children repigment more readily than "
         "adults, and patches treated within the first year commonly respond well."),
        ("Is it caused by something I did during pregnancy or feeding?",
         "No. Vitiligo is autoimmune. Nothing a parent ate, did or failed to do causes it, "
         "and no dietary restriction prevents or reverses it."),
        ("Is phototherapy safe for a child?",
         "Narrowband UVB is used in children where it is needed. The practical question is "
         "usually cooperation, whether the child will stand still wearing goggles. Excimer is "
         "often preferred for a few patches because exposure is limited to the patch."),
        ("Should I tell the school?",
         "Yes. A short written note that vitiligo is not contagious and needs no restriction "
         "prevents most of the difficulties children report."),
        ("Can my child have graft surgery?",
         "Not while the disease is active. Once it has been stable for about twelve months, "
         "which segmental vitiligo reliably becomes, surgery can be considered, and children "
         "heal well."),
    ],
    "related": [
        ("vitiligo-types-and-stages", "Types and stages", "Where segmental disease fits."),
        ("vitiligo-diet-and-myths", "Diet and myths", "What to say to relatives."),
        ("vitiligo-phototherapy", "Phototherapy", "How a light course is run."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-diet-and-myths", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("Diet and myths", None)],
    "title": "Vitiligo Diet & Myths: What the Evidence Says | Dr. Varada",
    "meta": "Does diet change vitiligo? Is it contagious? A dermatologist of 45 years answers "
            "what patients and relatives actually ask, and names the myths to ignore.",
    "eyebrow": "Vitiligo",
    "h1": "Vitiligo: diet, myths and what actually has evidence",
    "lede": "Almost every patient arrives having been told to stop eating something. Almost "
            "none of that advice has evidence behind it, and some of it does real harm by "
            "delaying treatment during the months when treatment works best.",
    "acts": [("Consult online", WHATSAPP), ("Back to the vitiligo hub", "vitiligo")],
    "sources": ["niams-vitiligo", "aad-vitiligo", "nhs-vitiligo", "gvf"],
    "glance": [
        ("Causes vitiligo", "An autoimmune process: not food"),
        ("Diet that reverses it", "None demonstrated"),
        ("Contagious", "No, in any way"),
        ("Worth checking", "Thyroid function, vitamin D, B12"),
        ("Worth doing", "Daily sunscreen on depigmented skin"),
        ("Worth ignoring", "Milk-and-citrus advice"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The short answer",
         "h2": "No food causes vitiligo. No diet reverses it.",
         "body": [
             "Vitiligo is an autoimmune condition: the immune system destroys or disables "
             "the cells that make pigment. Diet does not initiate that process, and no "
             "dietary change has been shown in any reliable study to reverse it.",
             "The most persistent piece of advice in India: do not eat sour foods with milk, "
             "avoid citrus, avoid fish with dairy: has no basis in evidence. It is folklore, "
             "repeated confidently, and it is harmless only in the sense that the food "
             "restriction itself rarely hurts. The harm is elsewhere: months spent adjusting a "
             "diet are months not spent treating active disease, and those are exactly the "
             "months in which treatment works best.",
             "What does matter nutritionally is unremarkable: eat a normal balanced diet, "
             "correct a documented deficiency if one is found. Vitamin D and B12 are worth "
             "checking because deficiency is common in the general population, not because "
             "correcting them repigments skin.",
         ]},

        {"kind": "diagram", "eyebrow": "Where colour comes from",
         "h2": "Pigment is made, not eaten.",
         "intro": "Every diet claim runs aground on this picture. Colour is manufactured inside a cell in your skin and handed to its neighbours. No food supplies it, no food destroys it, and no combination of foods rebuilds a cell that the immune system has removed.",
         "caption": "What food can do is support general health, which matters. What it cannot do is repigment a patch. Anyone selling a diet that reverses vitiligo is selling you the thing this picture rules out.",
         "labels": [
             {"text": "Pigment cap over each nucleus", "x": 40, "y": 33, "lead": 21, "find": "artwork"},
             {"text": "Packets travelling along the arm", "x": 34, "y": 47, "lead": 27, "find": "artwork"},
             {"text": "Arms reaching between cells", "x": 46, "y": 57, "lead": 15, "find": "artwork"},
             {"text": "Melanocyte", "x": 31, "y": 74, "lead": 30, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/A2-melanocyte.webp", "w": 1820, "h": 1024,
             "alt": "A melanocyte at the base of the epidermis, drawn as a star-shaped cell with long arms reaching up between the surrounding skin cells. Dark brown pigment granules are made inside it, travel along its arms and are handed into neighbouring cells, where they gather into a cap above each nucleus."}},

        {"kind": "table", "eyebrow": "Myth by myth", "h2": "What patients are told, and what is true",
         "head": ["The claim", "The reality"],
         "rows": [
             ["Vitiligo is contagious",
              "It is not. It cannot spread by touch, sharing food, or any contact."],
             ["Milk with citrus causes white patches",
              "No evidence of any kind. This is folklore."],
             ["It is caused by 'bad blood' or past sin",
              "It is an autoimmune condition with a genetic component."],
             ["Only fair-skinned people get it",
              "It affects all skin types; it is simply more visible on darker skin."],
             ["It always spreads to the whole body",
              "Most vitiligo stays limited. Universal disease is uncommon."],
             ["Copper vessels or copper supplements cure it",
              "No demonstrated benefit; copper excess is harmful."],
             ["It means you will get cancer",
              "There is no increased skin cancer risk; if anything, slightly lower."],
             ["Nothing can be done",
              "Untrue, and the most damaging myth of all. Treatment often repigments skin."],
         ],
         "note": "The last row is why this page exists. Patients told nothing can be done "
                 "present years later with disease that would have responded early."},

        {"kind": "split", "eyebrow": "What does have evidence",
         "h2": "The short list of things actually worth doing.",
         "body": ["Stripped of folklore, the evidence-based advice for someone living with "
                  "vitiligo is brief, and almost all of it is about protecting skin and "
                  "catching associated conditions rather than about food.",
                  "It is a shorter list than most patients expect, and it is more effective "
                  "than the long one they were given."],
         "cta": ("Start with a proper assessment", WHATSAPP),
         "items": [
             {"title": "Sunscreen on depigmented skin",
              "body": "Skin without pigment has no protection and burns readily. Daily "
                      "broad-spectrum sunscreen, reapplied. This is the one non-negotiable."},
             {"title": "Check the thyroid",
              "body": "Autoimmune thyroid disease is the commonest association. Testing is "
                      "simple and finding it matters."},
         ]},

        {"kind": "checklist", "eyebrow": "Reasonable", "h2": "Advice worth following.",
         "items": [
             "<b>Broad-spectrum sunscreen daily</b> on all depigmented skin",
             "<b>Avoid deliberate tanning</b>: it widens the contrast",
             "<b>Protect from injury</b>: cuts can trigger new patches",
             "<b>Treat early</b>: the strongest predictor of response",
             "<b>Check thyroid</b>, vitamin D and B12 once",
             "<b>Cosmetic camouflage</b> if you want it: it is a legitimate choice",
         ]},

        {"kind": "callout", "warn": True, "title": "About 'natural cure' treatments",
         "body": "Herbal preparations, unregulated oral supplements and psoralen taken without "
                 "supervision cause real harm. Liver injury and severe burns are both "
                 "documented. Psoralen with light is a genuine medical treatment; psoralen "
                 "bought online and used in the sun is not the same thing."},
    ],
    "faq_h2": "Diet and myths",
    "faqs": [
        ("Should I avoid milk, curd or citrus?",
         "No. There is no evidence that any of these cause vitiligo or make it worse, "
         "including the widely repeated advice about not combining sour foods with milk."),
        ("Are there foods that help repigmentation?",
         "No food has been shown to repigment skin. A balanced diet supports general health; "
         "it is not a treatment for vitiligo."),
        ("Should I take vitamin supplements?",
         "Only to correct a deficiency that has actually been measured. Vitamin D and B12 "
         "are worth checking once. Taking supplements speculatively does nothing for the "
         "vitiligo."),
        ("Is vitiligo contagious?",
         "No. Not by touch, not by sharing food or utensils, not by any route. This is the "
         "single most damaging misconception the condition carries."),
        ("Can stress cause vitiligo?",
         "Stress does not cause it. Some patients report a flare after a period of severe "
         "stress or illness, and stress is a plausible trigger for activity in someone already "
         "predisposed, but it is not the cause."),
        ("Is there any truth to Ayurvedic or homeopathic cures?",
         "No treatment from any system has been shown to cure vitiligo. Some traditional "
         "preparations contain psoralens, which are genuinely active, and genuinely dangerous "
         "when used without supervised light dosing."),
    ],
    "related": [
        ("vitiligo", "The vitiligo hub", "What the condition is and how it is treated."),
        ("vitiligo-children", "Vitiligo in children", "What to tell family and school."),
        ("vitiligo-cost", "What treatment costs", "Before you are sold a package."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-cost", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("Cost", None)],
    "title": "Vitiligo Treatment Cost in India | Dr. Varada",
    "meta": "What vitiligo treatment costs in India: how phototherapy, excimer and graft "
            "surgery are priced, and the questions to ask before paying for a package.",
    "eyebrow": "Vitiligo",
    "h1": "What vitiligo treatment costs",
    "lede": "Vitiligo is treated over months, so the number that matters is not the price of a "
            "session. It is what a course adds up to, and what happens to the money if the "
            "patch does not respond.",
    "acts": [("Ask for your costing", WHATSAPP), ("Back to the vitiligo hub", "vitiligo")],
    "sources": ["aad-vitiligo-tx", "iadvl-vitiligo-surgery", "dermnet-vitiligo"],
    "glance": [
        ("Priced by", "Session, area, or graft: not by outcome"),
        ("Phototherapy", "Per session; courses run months"),
        ("Excimer", "Per session, by area treated"),
        ("Surgery", "Per procedure, by area and technique"),
        ("Consultation", f"{FEE_ONLINE_SHOW} online · {FEE_CLINIC_SHOW} in person, {FEE_TAX}"),
        ("Treatment", "Quoted after examination, in writing"),
        ("Packages", "Ask what happens if it doesn't work"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How pricing works",
         "h2": "Four different things are being charged for.",
         "body": [
             "Vitiligo costs confuse people because four unrelated pricing models sit under "
             "one condition. Consultations are per visit. Medication is per month at the "
             "pharmacy. Light treatment is per session across a course of many months. "
             "Surgery is per procedure, priced by the area covered and the technique used.",
             "A meaningful estimate therefore needs to name all four, and needs to state "
             "the expected course length rather than a single session price. A clinic that "
             "quotes only the per-session figure is quoting the smallest honest number "
             "available.",
             "Costs are given here after examination and in writing. Before an examination "
             "nobody can tell you how many sessions your particular patches will need, because "
             "that depends on site, duration and activity. The same three things that decide "
             "the treatment itself.",
         ]},

        fees_block(note=NOTE_COST,
                   h2="The one figure that can be published",
                   intro="A consultation fee is fixed before anybody examines anything, "
                         "so it is stated here. Everything below it depends on what is "
                         "found, which is why the rest of this page describes structure "
                         "rather than prices."),

        {"kind": "table", "eyebrow": "The structure", "h2": "What you are charged for",
         "intro": "Current figures are confirmed at consultation. What does not change is the "
                  "structure, which is what lets you compare one clinic with another.",
         "head": ["Item", "Charged", "What drives the total"],
         "rows": [
             ["Consultation", f"{FEE_ONLINE_SHOW} online · {FEE_CLINIC_SHOW} in person, {FEE_TAX}",
              "Fixed; reviews charged the same way"],
             ["Topical medication", "At the pharmacy, monthly",
              "Which agent; area being treated"],
             ["NB-UVB phototherapy", "Per session", "2–3 sessions/week over 6–12 months"],
             ["Excimer laser", "Per session, by area", "Number and size of patches"],
             ["Melanocyte transplant", "Per procedure", "Recipient area; theatre time"],
             ["Punch / blister grafting", "Per procedure or per session",
              "Number of grafts; number of sittings"],
             ["Review visits", "Per visit", "Every 6–8 weeks while active"],
         ],
         "note": "The consultation fee is fixed and is stated above. Every other rupee figure "
                 "is quoted by the clinic after examination and is deliberately not published "
                 "here: a number without your diagnosis attached to it is not information, it "
                 "is an advertisement."},

        {"kind": "checklist", "eyebrow": "Before you pay",
         "h2": "Six questions worth asking any clinic.",
         "items": [
             "<b>How many sessions</b> is this course expected to run?",
             "<b>What happens if</b> the patch does not respond by session 20?",
             "<b>Is medication included</b> or bought separately?",
             "<b>Are review visits</b> charged on top?",
             "<b>If I stop early</b>, is unused package money refunded?",
             "<b>Is surgery quoted</b> per procedure, or per sitting?",
         ]},

        {"kind": "split", "eyebrow": "Packages",
         "h2": "Why this practice quotes plans, not packages.",
         "body": ["A package sold before an examination is a commitment to a number of "
                  "sessions decided by pricing rather than by response. It creates pressure "
                  "to continue a treatment that has been shown not to be working, because "
                  "the money is already spent.",
                  "The alternative is to price the plan, review at defined intervals, and "
                  "change course when the review says to. It costs the clinic predictability "
                  "and it costs the patient nothing."],
         "cta": ("Get a plan and a costing", WHATSAPP),
         "items": [
             {"title": "Reviewed at 6–8 weeks",
              "body": "If nothing has moved on a site that should have responded, the plan "
                      "changes rather than continuing to bill."},
             {"title": "Surgery quoted separately",
              "body": "It is a distinct procedure with its own consent and its own costing, "
                      "not an add-on inside a light-therapy package."},
         ]},

        {"kind": "callout", "title": "Cost is not the only currency",
         "body": "Phototherapy demands two to three visits a week for months. For many patients "
                 "travel time and time off work outweigh the session fee, which is why a "
                 "supervised home unit, or excimer for a handful of patches, can be the cheaper "
                 "option overall even at a higher per-session price."},
    ],
    "faq_h2": "Cost questions",
    "faqs": [
        ("Why aren't treatment prices listed on this page?",
         f"The consultation fee is listed, because it is fixed: {FEE_ONLINE_SHOW} {FEE_TAX} "
         f"online, {FEE_CLINIC_SHOW} {FEE_TAX} in person. Treatment prices are not, because "
         f"a price without a diagnosis attached is meaningless — the number of sessions your "
         f"patches need depends on their site, size, duration and activity. Those are quoted "
         f"in writing after examination."),
        ("Is vitiligo treatment covered by insurance in India?",
         "Generally not. Most policies treat it as a chronic dermatological condition rather "
         "than an admissible one, and surgical repigmentation is often classed as cosmetic. "
         "Check your specific policy before assuming either way."),
        ("Is a package cheaper than paying per session?",
         "Sometimes on paper. The risk is that a package fixes the number of sessions before "
         "anyone knows whether your patches respond, and creates pressure to continue "
         "treatment that a review says should change."),
        ("What is the most expensive part of treatment?",
         "Usually the cumulative cost of a long phototherapy course, not any single procedure, "
         "because it runs for months. Surgery is a larger single number but a one-off."),
        ("Can I do part of the treatment at home to reduce cost?",
         "Sometimes. A home narrowband UVB unit can be appropriate once the dose has been "
         "established in clinic and the patches are countable and reachable. It is not "
         "suitable as a starting point or for widespread disease."),
    ],
    "related": [
        ("vitiligo-phototherapy", "Phototherapy", "What a course actually involves."),
        ("vitiligo-graft-surgery", "Graft surgery", "How the surgical option is priced."),
        ONLINE,
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "vitiligo-online-consultation", "template": "T2", "condition": "Vitiligo",
    "crumbs": [("Vitiligo", "vitiligo"), ("Online consultation", None)],
    "title": "Online Vitiligo Consultation Anywhere in India | Dr. Varada",
    "meta": "Consult a vitiligo specialist of 45 years by video, anywhere in India. What a "
            "video consult can settle, how to photograph patches, and when to travel.",
    "eyebrow": "Vitiligo",
    "h1": "Consult about vitiligo from anywhere in India",
    "lede": "Vitiligo is a condition people travel for, often without knowing in advance "
            "whether the journey is worth making. A video consultation answers that question "
            "first, and for many patients it is the whole answer.",
    "acts": [("Book a video consultation", WHATSAPP), ("Call the clinic", PHONE)],
    "sources": ["niams-vitiligo", "aad-vitiligo-tx", "dermnet-vitiligo"],
    "glance": [
        ("Fee", f"{FEE_ONLINE_SHOW} {FEE_TAX}, paid in advance"),
        ("Booking", "WhatsApp: video link sent back"),
        ("Good for", "Diagnosis review, plan, second opinion"),
        ("Not for", "Procedures, grafting assessment in isolation"),
        ("You'll need", "Daylight photographs, old prescriptions"),
        ("Languages", "English, Hindi, Telugu"),
        ("Outcome", "A written plan you can act on locally"),
    ],
    "sections": [
        fees_block(
            intro="Both fees are fixed and are the same for every condition. "
                  "Consult online first and, if an examination in person turns "
                  "out to be necessary, only the difference is charged."),

        {"kind": "prose", "eyebrow": "Why this exists",
         "h2": "Most of vitiligo care is decisions, not procedures.",
         "body": [
             "The things that determine a vitiligo outcome, whether the disease is active, "
             "whether the current treatment is the right one, whether a patch is a candidate "
             "for surgery, whether the diet advice you were given matters. Are all judgements. "
             "Almost none of them requires being in the room.",
             "India has among the highest vitiligo prevalence in the world and a very "
             "uneven distribution of dermatologists who treat it in depth. A patient in a "
             "district town is frequently told either that nothing can be done, or that a "
             "cure is available for a fee. Both answers are wrong and both are common.",
             "A video consultation is a way to get a considered opinion without a "
             "thousand-kilometre trip, and, when travel is genuinely warranted, to arrive "
             "knowing exactly what for.",
         ]},

        {"kind": "diagram", "eyebrow": "The limit of a photograph",
         "h2": "What a camera cannot do.",
         "intro": "Photographs settle a great deal — the pattern, the distribution, the change since last time. What they cannot do is fluoresce. A Wood's lamp reveals patches and borders that no camera in ordinary light will record.",
         "caption": "This is the honest boundary of an online consultation for vitiligo. Plans, drugs and expectations can be settled remotely; a full assessment of extent needs the lamp, and the lamp needs you in the room.",
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
             "alt": "The same patch of brown forearm skin shown twice. In ordinary daylight two pale patches are faint and low in contrast with soft edges. Under a handheld lamp casting a violet glow, the same two patches stand out as sharp-edged chalk-white areas — and three more patches are visible that could not be seen at all in daylight."}},

        {"kind": "cards", "eyebrow": "Scope", "h2": "What it can and can't settle",
         "accent": "chronic",
         "items": [
             {"eyebrow": "Works well", "title": "What a video consult can do",
              "list": ["Confirm or question a diagnosis",
                       "Judge whether disease is active or stable",
                       "Review a treatment that isn't working",
                       "Advise on phototherapy available near you",
                       "Give a second opinion on a proposed surgery",
                       "Answer diet and myth questions properly"]},
             {"eyebrow": "Needs a visit", "title": "What it can't",
              "list": ["Wood's lamp examination",
                       "Any procedure: light, laser or surgery",
                       "Final surgical assessment on its own",
                       "Dermatoscopy of an uncertain lesion",
                       "Anything requiring touch"]},
             {"eyebrow": "In between", "title": "The common outcome",
              "body": "A plan you can start locally, a clear statement of whether surgery "
                      "is even a possibility, and a defined point at which travelling "
                      "becomes worthwhile."},
         ]},

        {"kind": "steps", "eyebrow": "Preparing", "h2": "How to make the appointment count",
         "items": [
             {"title": "Photograph in daylight",
              "body": "Near a window, no flash, no filter. One wide shot showing the body "
                      "region and one close shot of each patch."},
             {"title": "Include a scale and a date",
              "body": "A coin or a ruler beside the patch. And older photographs if you have "
                      "any. They establish whether it is spreading."},
             {"title": "List what you've used",
              "body": "Every cream, tablet and course of light, with rough dates and how "
                      "long each was continued."},
             {"title": "Bring your reports",
              "body": "Thyroid function, vitamin D, B12, and any biopsy report. Have them "
                      "ready to share during the call."},
         ]},

        {"kind": "split", "eyebrow": "When to travel",
         "h2": "The reason people come to Hyderabad.",
         "body": ["Surgical repigmentation, melanocyte transplant and punch grafting, is the "
                  "treatment patients travel for, because comparatively few centres in India "
                  "perform it and because it is the only option for patches that light cannot "
                  "reach.",
                  "The consultation exists to establish whether you are a candidate before "
                  "you buy a ticket. A significant proportion of people who ask are told to "
                  "wait until their disease is stable, and hearing that on a video call "
                  "costs a great deal less than hearing it in a waiting room."],
         "cta": ("How graft surgery works", "vitiligo-graft-surgery"),
         "items": [
             {"title": "Stability decides it",
              "body": "Twelve months without new or expanding patches. Photographs are what "
                      "establish that, which is why old ones are valuable."},
             {"title": "Plan the trip once",
              "body": "Assessment and procedure can often be sequenced to reduce the number "
                      "of journeys. Ask about it on the call."},
         ]},

        {"kind": "callout", "warn": True, "title": "What cannot be prescribed remotely",
         "body": "Some vitiligo medications require examination and monitoring before they "
                 "are started, and will not be prescribed on a first video call. Being told "
                 "that is a sign the consultation is being run properly."},
    ],
    "faq_h2": "Online consultation",
    "faqs": [
        *FEE_FAQS,
        ("How do I book an online vitiligo consultation?",
         "Message the clinic on WhatsApp and ask for a video consultation. The team confirm a "
         "time and send the link back on the same thread. One conversation, so nothing is lost "
         "between booking and consulting."),
        ("Can vitiligo really be assessed over video?",
         "A great deal of it can: activity, distribution, whether the current treatment makes "
         "sense, and whether surgery is worth investigating. What cannot be done remotely is a "
         "Wood's lamp examination or any procedure."),
        ("What photographs should I send?",
         "Daylight, no flash, no filter. One wide shot per body region and one close shot "
         "per patch, with a coin or ruler for scale. Older photographs are especially "
         "valuable because they show whether the patches have grown."),
        ("Will I get a prescription?",
         "Where it is appropriate, yes, with a written plan. Some medications require in-person "
         "examination and monitoring before starting, and those will not be prescribed "
         "remotely."),
        ("Can I get phototherapy near my home town?",
         "Often yes. Part of the consultation is identifying what is available locally and "
         "specifying the protocol so a nearby centre can run it, with reviews done by video."),
        ("Which languages can I consult in?",
         "English, Hindi and Telugu."),
    ],
    "related": [CROSS,
                ("vitiligo-graft-surgery", "Graft surgery",
                 "The treatment most out-of-state patients are asking about."),
                ("online-consultation", "Consult online, any condition",
                 "What a video consultation settles, and what it cannot.")],
},

]
