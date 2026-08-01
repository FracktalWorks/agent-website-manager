"""T1 — Hyderabad service pillars: inflammatory skin disease and aesthetic dermatology.

The aesthetic pages carry an extra burden. Aesthetic marketing is where medical
advertising rules are broken most often — guaranteed results, "years younger",
before-and-afters without consent, superlatives. None of that appears here. What
these pages sell instead is judgement: what a treatment does, what it does not do,
and when the answer is not to have it.
"""

from chrome import PHONE, WHATSAPP
from content.hyderabad_medical import CRED, VISIT

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "skin-allergy-rashes-treatment", "template": "T1", "condition": "Skin allergy",
    "crumbs": [("Skin allergy and rashes", None)],
    "title": "Skin Allergy & Rash Treatment in Hyderabad | Dr. Varada",
    "meta": "Skin allergy, hives and rash treatment in Hyderabad, including itchy rashes in "
            "children, contact allergy and chronic urticaria.",
    "eyebrow": "Hyderabad",
    "h1": "Skin allergy and rash treatment in Hyderabad",
    "lede": "A rash is a sign, not a diagnosis. Two rashes that look identical can be an "
            "allergy, an infection or a chronic inflammatory disease, and the antihistamine "
            "that helps one does nothing for the others.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["dermnet-urticaria", "dermnet-contact-dermatitis", "dermnet-eczema"],
    "glance": [
        ("Covers", "Hives, contact allergy, drug rash, itchy rashes"),
        ("In children", "Common and usually straightforward"),
        ("Chronic urticaria", "Over 6 weeks: needs proper assessment"),
        ("Patch testing", "For suspected contact allergy"),
        ("Red flags", "Fever, blistering, lip or tongue swelling"),
        ("First step", "Identify what it actually is"),
    ],
    "sections": [
        {"kind": "callout", "warn": True, "title": "When not to wait for an appointment",
         "body": "Swelling of the lips, tongue or throat, difficulty breathing, a rash with "
                 "high fever, blistering or skin peeling in sheets, or a rash that does not "
                 "fade when pressed. All need emergency care the same day, not a clinic "
                 "booking."},

        {"kind": "prose", "eyebrow": "The problem",
         "h2": "Most rashes are treated before they are named.",
         "body": [
             "The usual sequence for a rash in India is a topical steroid-antifungal-antibiotic "
             "combination cream bought over the counter, applied for weeks. Those combinations "
             "suppress appearance without treating cause, and they change how the rash looks, "
             "so by the time it is examined properly, the diagnosis has been obscured as well "
             "as delayed.",
             "The alternative takes one appointment. Where it started, how it spreads, what "
             "makes it worse, whether it itches or burns, whether individual spots last hours "
             "or days. That history plus an examination names most rashes without any test at "
             "all.",
             "Where a test is needed it is a specific one: patch testing for suspected "
             "contact allergy, a scraping for suspected fungus, occasionally a biopsy. Not "
             "a broad allergy panel, which in chronic hives generates false positives and "
             "unnecessary food restriction far more often than it finds a cause.",
         ]},

        {"kind": "table", "eyebrow": "Common patterns", "h2": "What the pattern usually means",
         "head": ["What you see", "Often", "What it needs"],
         "rows": [
             ["Raised weals that move and fade within a day", "Urticaria (hives)",
              "Antihistamine, properly dosed; find the trigger if acute"],
             ["Rash exactly where something touched skin", "Contact dermatitis",
              "Identify the contact; patch testing if unclear"],
             ["Widespread rash days after a new medicine", "Drug reaction",
              "Review the medicine urgently: do not simply treat the skin"],
             ["Itchy rash in a child, flexures and cheeks", "Atopic dermatitis",
              "Emollients and anti-inflammatory treatment"],
             ["Ring-shaped, scaly, spreading edge", "Fungal infection",
              "Antifungal: steroid creams make it worse and spread it"],
             ["Intense night-time itch, whole family affected", "Scabies",
              "Treat everyone in the household simultaneously"],
         ],
         "note": "The fungal row matters most in India, where steroid-containing "
                 "combination creams are freely sold. They convert an ordinary treatable "
                 "fungal infection into an extensive, hard-to-treat one."},

        {"kind": "split", "eyebrow": "Chronic hives",
         "h2": "Hives for more than six weeks are a different problem.",
         "body": ["Acute hives usually have a trigger and settle. Chronic urticaria. Weals "
                  "coming and going for more than six weeks. Usually does not have an external "
                  "trigger at all, which is why the extensive food-allergy testing patients "
                  "often demand is unhelpful and frequently harmful.",
                  "It is managed rather than chased: antihistamines at properly optimised "
                  "doses, a limited set of blood tests, and escalation where that is not "
                  "enough. Most cases eventually resolve, though it can take a long time, "
                  "and knowing that changes how the wait feels."],
         "cta": ("If it's eczema rather than hives", "eczema-atopic-dermatitis-treatment"),
         "items": [
             {"title": "Individual weals last under 24 hours",
              "body": "If a single spot persists for days or leaves a bruise, it may not be "
                      "ordinary urticaria and is investigated differently."},
             {"title": "Food allergy testing rarely helps",
              "body": "In chronic urticaria it produces false positives and needless "
                      "restriction far more often than it finds a cause."},
         ]},

        VISIT,
    ],
    "faq_h2": "Skin allergy questions",
    "faqs": [
        ("How do I know if my rash is an allergy?",
         "Allergic rashes typically itch, appear soon after exposure, and settle when the "
         "exposure stops. A rash appearing exactly where something touched the skin, or "
         "within days of a new medicine, points that way. Many itchy rashes are not "
         "allergic at all."),
        ("Should I get allergy testing done?",
         "Only where it will change the treatment. Patch testing is genuinely useful for "
         "suspected contact allergy. Broad food-allergy panels in chronic hives are not. They "
         "generate false positives and unnecessary dietary restriction."),
        ("My child has an itchy rash. Is it serious?",
         "Most childhood rashes are not, and most are straightforward once named. Seek care "
         "the same day if there is fever, the rash does not fade when pressed, there is "
         "blistering, or the child is unwell rather than simply itchy."),
        ("Why does my rash keep coming back?",
         "Either the trigger is still present, or it is a chronic condition rather than an "
         "allergy. Both are common. Recurrent rashes are worth a proper diagnosis rather "
         "than another round of the same cream."),
        ("Are over-the-counter combination creams safe?",
         "The steroid-antifungal-antibiotic combinations sold widely in India cause real "
         "harm. They make fungal infections extensive and harder to treat, thin the skin, "
         "and disguise the diagnosis. They should not be used without a prescription."),
        ("What is chronic urticaria?",
         "Hives that come and go for more than six weeks. Usually there is no external "
         "trigger to find. It is managed with optimised antihistamine dosing and escalation "
         "where needed, and most cases eventually resolve."),
    ],
    "related": [
        ("eczema-atopic-dermatitis-treatment", "Eczema and atopic dermatitis",
         "The commonest chronic itchy rash, especially in children."),
        ("fungal-infection-treatment-hyderabad", "Fungal infections", "If it is ring-shaped and spreading."),
        ("psoriasis-treatment-hyderabad", "Psoriasis", "If the rash is scaly and persistent."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "eczema-atopic-dermatitis-treatment", "template": "T1",
    "condition": "Atopic dermatitis",
    "crumbs": [("Eczema and atopic dermatitis", None)],
    "title": "Eczema & Atopic Dermatitis in Hyderabad | Dr. Varada",
    "meta": "Eczema and atopic dermatitis treatment in Hyderabad for children and adults: the "
            "emollient-first approach, using steroids correctly, and the itch cycle.",
    "eyebrow": "Hyderabad",
    "h1": "Eczema and atopic dermatitis treatment",
    "lede": "Eczema is a barrier problem before it is an inflammation problem. Treatment "
            "that only suppresses the flare and never repairs the barrier produces exactly "
            "the pattern most families describe: better for a week, back within a month.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["niams-eczema", "dermnet-eczema", "nhs-eczema"],
    "glance": [
        ("Curable", "No, but usually well controlled"),
        ("In children", "Most improve substantially with age"),
        ("Foundation", "Emollients, used generously and daily"),
        ("Flares", "Anti-inflammatory treatment, then step down"),
        ("Steroid phobia", "A bigger problem than steroid overuse"),
        ("Watch for", "Infection: weeping, crusting, sudden worsening"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The mechanism",
         "h2": "A leaky barrier, then inflammation.",
         "body": [
             "Skin in atopic dermatitis does not hold water well and does not keep "
             "irritants out well. Water escapes, the skin dries and cracks, irritants and "
             "allergens get in, and the immune system reacts. The itch that follows leads to "
             "scratching, scratching damages the barrier further, and the cycle continues.",
             "That is why moisturiser is not supportive care in eczema: it is the treatment. "
             "Applied generously and daily, including on skin that currently looks fine, it "
             "reduces the number of flares and the amount of steroid needed over a year.",
             "Most families use far too little. A child with widespread eczema needs "
             "emollient measured in hundreds of grams a month, not a small tube that lasts "
             "the season.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "How eczema is managed",
         "items": [
             {"title": "Emollient, generously, daily",
              "body": "Applied several times a day, and always after bathing on damp skin. On "
                      "good days as well as bad. That is what prevents the next flare."},
             {"title": "Treat a flare properly",
              "body": "An anti-inflammatory of the right potency for the site, used for "
                      "long enough to actually clear it. Under-treating prolongs everything."},
             {"title": "Step down, don't stop dead",
              "body": "Reduce frequency as it settles. For frequently flaring sites, "
                      "twice-weekly maintenance to the usual spots prevents the next flare."},
             {"title": "Break the itch cycle",
              "body": "Nails short, cotton clothing, cool rooms at night, and treating the "
                      "itch specifically. Scratching is a driver, not just a symptom."},
         ]},

        {"kind": "split", "eyebrow": "Steroid fear",
         "h2": "The bigger problem is under-treatment.",
         "body": ["Almost every family arrives worried about steroid creams, and the worry is "
                  "understandable. Potent steroids used carelessly on thin skin do cause harm. "
                  "But in practice far more eczema is damaged by treating it too little and too "
                  "briefly than by treating it too much.",
                  "Used at the right potency for the site, for a defined period, and "
                  "stepped down properly, topical steroids are safe and are the reason "
                  "eczema became manageable. Where the face or eyelids are involved, "
                  "steroid-free anti-inflammatory options are used instead."],
         "cta": ("If it might be an allergy instead", "skin-allergy-rashes-treatment"),
         "items": [
             {"title": "Potency matches the site",
              "body": "What is right for the shins is wrong for the eyelids. Site, not "
                      "severity alone, chooses the strength."},
             {"title": "A finger-tip unit",
              "body": "There is a proper measure for how much to apply. Being shown it is "
                      "worth more than any leaflet."},
         ]},

        {"kind": "callout", "warn": True, "title": "When eczema is infected",
         "body": "Weeping, golden crusting, sudden worsening or painful clustered blisters "
                 "suggest bacterial or viral infection on top of the eczema. That needs "
                 "assessing promptly. Eczema herpeticum in particular is a genuine emergency in "
                 "a child."},

        VISIT,
    ],
    "faq_h2": "Eczema questions",
    "faqs": [
        ("Will my child grow out of eczema?",
         "Many children improve substantially through childhood, and a majority are much "
         "better by adolescence. It does not disappear in everyone, and skin often remains "
         "dry and sensitive even when the eczema itself has settled."),
        ("Are steroid creams safe for eczema?",
         "Yes, when the potency matches the site, the course is long enough to clear the "
         "flare, and treatment is stepped down rather than stopped abruptly. Under-treating "
         "eczema causes more harm in practice than appropriate steroid use."),
        ("How much moisturiser should we be using?",
         "Far more than most families expect, for a child with widespread eczema, hundreds of "
         "grams a month. It is applied several times daily and continued on clear skin, because "
         "that is what prevents the next flare."),
        ("Does food cause eczema?",
         "Food allergy is a genuine trigger in a minority of children with severe eczema, "
         "and worth investigating in that group. In most people diet is not the driver, and "
         "unnecessary restriction risks nutrition without helping the skin."),
        ("Why does eczema get worse at night?",
         "Skin temperature rises and there are fewer distractions, so the itch dominates. "
         "Cool bedding, cotton nightwear, emollient before bed and treating the itch "
         "specifically all help."),
        ("Is eczema contagious?",
         "No. It cannot be passed to anyone. Infected eczema can spread bacteria or virus, "
         "which is a separate issue and a reason to have sudden worsening looked at."),
    ],
    "related": [
        ("skin-allergy-rashes-treatment", "Skin allergy and rashes",
         "For rashes that are not eczema."),
        ("dandruff-treatment", "Seborrhoeic dermatitis",
         "The other common chronic inflammatory rash."),
        ("psoriasis-treatment-hyderabad", "Psoriasis",
         "Sometimes confused with eczema, treated differently."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "anti-aging-botox-hyderabad", "template": "T1",
    "crumbs": [("Botox and anti-ageing", None)],
    "title": "Botox & Anti-Ageing Treatment in Hyderabad | Dr. Varada",
    "meta": "Botulinum toxin and anti-ageing treatment in Hyderabad: what it treats, what it "
            "cannot, how long it lasts, and why conservative dosing is the point.",
    "eyebrow": "Hyderabad",
    "h1": "Botox and anti-ageing treatment in Hyderabad",
    "lede": "Botulinum toxin relaxes the specific muscles that fold skin into lines. It does "
            "that well and it does nothing else, which is why the useful conversation is about "
            "whether your concern is actually a muscle problem.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "sources": ["dermnet-botulinum"],
    "glance": [
        ("Treats", "Lines caused by muscle movement"),
        ("Does not treat", "Volume loss, laxity, pigmentation, texture"),
        ("Onset", "3–7 days, full effect around 2 weeks"),
        ("Lasts", "Typically 3–4 months"),
        ("Where", "Secunderabad clinic"),
        ("Approach", "Conservative: movement retained"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What it actually does",
         "h2": "One mechanism, and its honest limits.",
         "body": [
             "Botulinum toxin temporarily reduces the contraction of specific small facial "
             "muscles. Where a line is created by repeated folding (frown lines, forehead "
             "lines, crow's feet), relaxing that muscle allows the line to soften and prevents "
             "it deepening further.",
             "Where a line is not caused by movement, it does nothing. Lines from volume "
             "loss, skin laxity, sun damage or texture are different problems with different "
             "answers, and treating them with toxin produces disappointment at some expense.",
             "It also has genuine medical uses that patients often do not realise are "
             "available. Excessive underarm or palm sweating responds to it well.",
             "The approach here is deliberately conservative: enough to soften the line, not "
             "enough to remove expression. A face that cannot move does not read as younger. "
             "It reads as treated.",
         ]},

        {"kind": "table", "eyebrow": "Matching concern to treatment",
         "h2": "Is toxin actually the right answer?",
         "head": ["What you dislike", "The cause", "What addresses it"],
         "rows": [
             ["Lines that appear when you frown", "Muscle movement", "Botulinum toxin"],
             ["Lines visible at rest, skin looks thin", "Collagen and volume loss",
              "Skin boosters, resurfacing, volume approaches"],
             ["Sagging along the jaw", "Laxity", "RF tightening; toxin will not help"],
             ["Dull, uneven, pigmented skin", "Sun damage and pigmentation",
              "Peels, topicals, sun protection"],
             ["Open pores and rough texture", "Texture", "Resurfacing and peels"],
             ["Excessive sweating", "Overactive sweat glands",
              "Botulinum toxin: a genuine medical indication"],
         ],
         "note": "Half the value of the consultation is this table. Being told your concern "
                 "is not a toxin problem saves you the cost of finding out."},

        {"kind": "split", "eyebrow": "Doing it well",
         "h2": "Conservative, reviewed, and adjusted.",
         "body": ["The first treatment is deliberately under-dosed and reviewed at two "
                  "weeks. Adding a little more is straightforward; waiting three months for "
                  "an over-treated forehead to recover is not.",
                  "It is also a medical procedure with real anatomy behind it. Injected in the "
                  "wrong plane or the wrong place it produces a drooping eyelid or a heavy "
                  "brow. Temporary, but months of temporary. Who is holding the syringe matters "
                  "more than which brand is in it."],
         "cta": ("For laxity rather than lines", "rf-skin-tightening-hyderabad"),
         "items": [
             {"title": "Reviewed at two weeks",
              "body": "Full effect takes about that long. Adjustment is part of the plan, "
                      "not a sign something went wrong."},
             {"title": "Expression is retained deliberately",
              "body": "The aim is looking rested, not looking treated. That is a dosing "
                      "decision made at the outset."},
         ]},

        {"kind": "callout", "warn": True, "title": "Who should not have it",
         "body": "Pregnancy and breastfeeding, certain neuromuscular conditions, active "
                 "infection at the injection site, and unrealistic expectations. The last being "
                 "the most common reason to decline. Anyone who cannot be talked out of "
                 "expecting a different face is better served by not having the injection."},

        VISIT,
    ],
    "faq_h2": "Botox questions",
    "faqs": [
        ("How long does botulinum toxin last?",
         "Typically three to four months. It varies with the area treated, the dose, and how "
         "strong the muscle is. Effect begins in three to seven days and is complete at "
         "about two weeks."),
        ("Will my face look frozen?",
         "Not with conservative dosing. The aim is softening the line while retaining "
         "expression. A frozen appearance is a dosing choice, and it is not the one made "
         "here."),
        ("Does it hurt?",
         "The injections are very fine and take a few minutes. Most people describe brief "
         "stinging. Small bruises are possible and settle within days."),
        ("What happens if I stop having it?",
         "Muscle movement gradually returns and lines return to their previous state over a few "
         "months. Nothing gets worse than it was. That is a persistent myth."),
        ("Is it safe long-term?",
         "It has decades of use in both medical and cosmetic indications with a well-"
         "characterised safety profile at the doses used cosmetically. Treated muscles may "
         "weaken slightly with repeated use, which usually means longer gaps between "
         "treatments."),
        ("Can it help excessive sweating?",
         "Yes, and this is a genuine medical indication that works well. Particularly for "
         "underarm sweating. Effect typically lasts several months."),
    ],
    "related": [
        ("dermal-fillers-hyderabad", "Dermal fillers", "For lost volume, which toxin cannot treat."),
        ("thread-lift-hyderabad", "Thread lift", "For mild laxity, with the limits stated."),
        ("rf-skin-tightening-hyderabad", "RF skin tightening", "For laxity."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "skin-boosters-hyderabad", "template": "T1",
    "crumbs": [("Skin boosters", None)],
    "title": "Skin Boosters in Hyderabad: Skin Quality | Dr. Varada",
    "meta": "Skin boosters in Hyderabad: what they are, how they differ from fillers, what "
            "change to expect and over how long, and who they suit.",
    "eyebrow": "Hyderabad",
    "h1": "Skin boosters in Hyderabad",
    "lede": "Skin boosters treat skin quality (hydration, fine texture, that dull tight look), "
            "rather than shape. They do not add volume and they do not lift. Knowing that "
            "before you book is most of the value.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "sources": ["dermnet-mesotherapy", "dermnet-fillers"],
    "glance": [
        ("Treats", "Hydration, fine crepiness, dullness"),
        ("Does not treat", "Volume loss, sagging, deep lines"),
        ("Protocol", "Usually a short course, then maintenance"),
        ("Visible change", "Gradual: weeks, not days"),
        ("Common areas", "Face, neck, décolletage, hands"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What they are",
         "h2": "Not a filler, and not marketed as one here.",
         "body": [
             "Skin boosters are injectable preparations placed superficially and spread "
             "across an area rather than shaped in one spot. They hydrate the skin and "
             "stimulate its own repair, improving the way skin reflects light and feels, "
             "without changing the contours of the face.",
             "Fillers do the opposite job: they add volume to a specific place to restore or "
             "alter shape. The two are frequently conflated in marketing, and a patient who "
             "wanted cheek volume and received boosters will be disappointed, as will a patient "
             "who wanted brighter skin and received filler.",
             "The realistic result is that skin looks better rested and better hydrated. It "
             "is a subtle, cumulative change over weeks, not a transformation photographed "
             "the next day.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "How a course runs",
         "items": [
             {"title": "Assess what the skin actually needs",
              "body": "Dullness from sun damage needs pigment treatment. Laxity needs "
                      "tightening. Boosters are for quality, and that distinction is made "
                      "first."},
             {"title": "An initial short course",
              "body": "Typically a small number of sessions spaced a few weeks apart, "
                      "building the effect gradually."},
             {"title": "Assess at the end, not during",
              "body": "The change is cumulative. Judging it after one session understates "
                      "it considerably."},
             {"title": "Maintain periodically",
              "body": "The effect is not permanent. Maintenance intervals are agreed once "
                      "the initial course shows what your skin does."},
         ]},

        {"kind": "split", "eyebrow": "Honest expectations",
         "h2": "What it will not do.",
         "body": ["It will not lift a jawline, fill a hollow, or remove a deep static line. "
                  "If those are your concerns, boosters are the wrong purchase and you will "
                  "be told so rather than sold a course that cannot deliver.",
                  "It also will not substitute for sun protection. Skin quality treatments "
                  "applied to skin that continues to accumulate ultraviolet damage are "
                  "spending money to stand still."],
         "cta": ("For laxity, this instead", "rf-skin-tightening-hyderabad"),
         "items": [
             {"title": "Subtle by design",
              "body": "The intended result is skin that looks well, not a visible "
                      "intervention. Anyone promising dramatic change is describing a "
                      "different treatment."},
             {"title": "Sunscreen is non-negotiable",
              "body": "It is the single highest-value part of any skin quality plan, and "
                      "the cheapest."},
         ]},

        {"kind": "callout", "title": "Small bumps afterwards are normal",
         "body": "Injection points can leave small raised areas and occasional bruising for "
                 "a day or two. Plan the appointment with that in mind rather than the day "
                 "before an event."},

        VISIT,
    ],
    "faq_h2": "Skin booster questions",
    "faqs": [
        ("What is the difference between skin boosters and fillers?",
         "Boosters are placed superficially across an area to improve skin hydration and "
         "quality. Fillers are placed to add volume and change shape in a specific location. "
         "Different products, different purposes."),
        ("How soon will I see a result?",
         "Gradually, over weeks, and cumulatively across the course. It is not a next-day "
         "change, and judging it after a single session understates what the full course "
         "does."),
        ("How long do skin boosters last?",
         "The effect is temporary and maintenance is needed periodically. How often depends on "
         "your skin, sun exposure and general skin care. It is agreed after the first course "
         "shows how you respond."),
        ("Do they help acne scars or open pores?",
         "Skin quality generally improves, which can make texture look better. They are not "
         "a treatment for true scarring, which needs procedural work."),
        ("Is there downtime?",
         "Minimal. Small bumps at injection points and occasional bruising for a day or two. "
         "Most people return to normal activity immediately."),
        ("Am I too young or too old for this?",
         "Neither age is the criterion. What the skin needs is. Someone with genuine volume "
         "loss or laxity will be better served by a different treatment regardless of age."),
    ],
    "related": [
        ("mesotherapy-hyderabad", "Mesotherapy", "The broader technique, and how it differs."),
        ("dermal-fillers-hyderabad", "Dermal fillers", "For volume, which boosters do not add."),
        ("chemical-peels-hyderabad", "Chemical peels", "For pigmentation and texture."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "rf-skin-tightening-hyderabad", "template": "T1",
    "crumbs": [("RF skin tightening", None)],
    "title": "RF Skin Tightening in Hyderabad | Dr. Varada",
    "meta": "Radiofrequency skin tightening in Hyderabad: how it works, what tightening is "
            "realistic, how many sessions, and when surgery is the honest answer.",
    "eyebrow": "Hyderabad",
    "h1": "RF skin tightening in Hyderabad",
    "lede": "Radiofrequency heats the deeper layers of skin enough to make collagen contract "
            "and remodel. It produces a genuine but modest tightening, and it is not a "
            "non-surgical facelift, whatever it is marketed as.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "sources": ["dermnet-needling", "dermnet-phototype"],
    "glance": [
        ("Treats", "Mild to moderate laxity"),
        ("Realistic result", "Modest tightening, gradual"),
        ("Sessions", "Usually a course, spaced weeks apart"),
        ("Full effect", "3–6 months as collagen remodels"),
        ("Downtime", "Little to none"),
        ("Not a substitute for", "Surgical lifting"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How it works",
         "h2": "Controlled heating, then months of remodelling.",
         "body": [
             "Radiofrequency energy passes through the skin surface and heats the layer "
             "beneath it. At the right temperature, existing collagen contracts immediately "
             "and the tissue responds by producing new collagen over the following months. "
             "The immediate change is small; the useful change is the remodelling.",
             "That is why results are judged at three to six months, not at the end of the "
             "session. It is also why a course is used rather than a single treatment. The "
             "stimulus is cumulative.",
             "The honest limit is degree. Radiofrequency improves mild to moderate laxity. "
             "It does not reposition tissue that has descended substantially, and no amount "
             "of it will do what surgery does. Where surgery is the appropriate answer, "
             "saying so is more useful than selling a course that cannot reach it.",
         ]},

        {"kind": "table", "eyebrow": "Suitability", "h2": "Who this genuinely suits",
         "head": ["Situation", "Suitable?", "Why"],
         "rows": [
             ["Early laxity, skin still elastic", "Good candidate",
              "This is what the treatment was designed for"],
             ["Mild jawline softening", "Reasonable", "Modest improvement is realistic"],
             ["Crepey texture on neck", "Reasonable", "Often combined with skin quality work"],
             ["Significant sagging or excess skin", "Not suitable",
              "Needs surgical assessment: RF will disappoint"],
             ["Lines from muscle movement", "Wrong treatment", "Botulinum toxin addresses these"],
             ["Volume loss in cheeks", "Wrong treatment", "Tightening does not replace volume"],
             ["Mild laxity on arms or abdomen", "Modest, same as the face",
              "A longer course; the same collagen response, over a larger area"],
             ["Fat reduction or weight loss", "Not what this is",
              "Body RF is sold for this constantly; it does not deliver it"],
         ],
         "note": "Two of these rows say 'wrong treatment' rather than 'no'. Most "
                 "disappointment with tightening treatments comes from using them on a "
                 "problem they were never meant to solve."},

        {"kind": "split", "eyebrow": "Marketing versus mechanism",
         "h2": "Why 'non-surgical facelift' is a phrase worth distrusting.",
         "body": ["Every energy-based tightening device is marketed with that phrase, and no "
                  "device delivers it. A facelift repositions and removes tissue. "
                  "Radiofrequency tightens what is there, modestly, over months.",
                  "Used on the right candidate with realistic expectations, it is a good "
                  "treatment with essentially no downtime. Used as a substitute for surgery "
                  "in someone who needs surgery, it is an expensive delay."],
         "cta": ("For skin quality rather than laxity", "skin-boosters-hyderabad"),
         "items": [
             {"title": "Judged at 3–6 months",
              "body": "The collagen response takes that long. Assessing it at the end of "
                      "the course understates the result."},
             {"title": "Maintenance, not permanence",
              "body": "The tissue continues to age. Periodic sessions maintain the gain; "
                      "nothing stops the underlying process."},
         ]},

        VISIT,
    ],
    "faq_h2": "RF tightening questions",
    "faqs": [
        ("How many RF sessions will I need?",
         "Usually a course spaced a few weeks apart, with the number depending on the area "
         "and the degree of laxity. The full result is judged three to six months after the "
         "course as collagen remodels."),
        ("Is it painful?",
         "Most people describe it as warm, sometimes intensely so in short bursts. It is "
         "tolerable without anaesthesia and there is essentially no downtime afterwards."),
        ("How long do results last?",
         "Typically a year or more, though skin continues to age. Periodic maintenance "
         "sessions preserve the gain. Nothing halts the underlying process."),
        ("Is this the same as a facelift?",
         "No, and the marketing phrase 'non-surgical facelift' is misleading. Surgery "
         "repositions and removes tissue. Radiofrequency modestly tightens what is present. "
         "Different scale of result entirely."),
        ("Can it be combined with other treatments?",
         "Frequently, yes: laxity, movement lines, pigmentation and skin quality are separate "
         "problems, and a plan addressing several usually looks better than any one treatment "
         "pushed too hard."),
        ("Is it safe on Indian skin?",
         "Radiofrequency does not target pigment, so it does not carry the pigmentary risk "
         "that some light-based devices do in darker skin types. That makes it a "
         "comparatively safe choice."),
        ("Can radiofrequency be used on the body?",
         "For mild laxity on the arms or abdomen, yes: the same modest tightening, over a "
         "larger area and so across a longer course. What it does not do is reduce fat or "
         "change your weight, which is what body radiofrequency is most often sold for."),
    ],
    "related": [
        ("skin-boosters-hyderabad", "Skin boosters", "For hydration and quality."),
        ("thread-lift-hyderabad", "Thread lift", "The other non-surgical option, with its limits."),
        ("chemical-peels-hyderabad", "Chemical peels", "For pigmentation and surface texture."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "chemical-peels-hyderabad", "template": "T1",
    "crumbs": [("Chemical peels", None)],
    "title": "Chemical Peels in Hyderabad: Cost & Sessions | Dr. Varada",
    "meta": "Chemical peels in Hyderabad for pigmentation, acne marks and melasma, which peel "
            "suits Indian skin, how many sessions, and the risk of getting it wrong.",
    "eyebrow": "Hyderabad",
    "h1": "Chemical peels in Hyderabad",
    "lede": "A peel is a controlled chemical injury that makes skin renew itself. On Indian "
            "skin the depth and the aftercare matter more than the ingredient, because the same "
            "treatment that clears pigmentation can cause it.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "sources": ["dermnet-peels", "dermnet-melasma", "dermnet-phototype"],
    "glance": [
        ("Treats", "Pigmentation, acne marks, melasma, texture"),
        ("Sessions", "A course, spaced 2–4 weeks apart"),
        ("Depth", "Superficial to medium in Indian skin"),
        ("Essential", "Daily sunscreen throughout"),
        ("Main risk", "Post-inflammatory pigmentation"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The Indian skin problem",
         "h2": "The risk is not the peel. It is what follows it.",
         "body": [
             "Skin that produces pigment readily responds to injury by producing more "
             "pigment. A peel is a deliberate, controlled injury. Done at the right depth "
             "with the right aftercare it clears pigmentation; done too deep or without sun "
             "protection afterwards it produces exactly the pigmentation it was meant to "
             "treat.",
             "This is why peeling protocols for darker skin are conservative: superficial to "
             "medium depth, built up gradually across a course, with priming beforehand and "
             "rigorous sun protection throughout. It is slower than the aggressive "
             "single-session approach, and it is the reason it works.",
             "Melasma deserves a specific warning. It is the commonest reason people ask "
             "about peels, it is genuinely improvable, and it is also prone to rebounding "
             "worse if treated aggressively. It is managed as a long-term condition rather "
             "than removed.",
         ]},

        {"kind": "table", "eyebrow": "Matching peel to problem",
         "h2": "What a peel is being used for",
         "head": ["Concern", "Realistic outcome", "Notes"],
         "rows": [
             ["Post-acne brown marks", "Good: often substantial improvement",
              "Often the most satisfying indication"],
             ["Melasma", "Improvement, needs maintenance",
              "Prone to rebound; treated conservatively"],
             ["Dull, uneven tone", "Good", "Usually a short course"],
             ["Rough texture, open pores", "Modest", "Combined approaches work better"],
             ["Fine lines", "Modest", "Not a substitute for other modalities"],
             ["Active acne", "Adjunct only", "Control the acne medically first"],
             ["True indented scars", "Not the right treatment", "Needs procedural scar work"],
         ],
         "note": "The last two rows are where peels are most often mis-sold. Peels support "
                 "acne treatment; they do not replace it, and they do not fill a scar."},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "How a course is run",
         "items": [
             {"title": "Prime the skin first",
              "body": "Topical preparation for some weeks before the first peel reduces "
                      "pigmentary complications considerably. It is not an upsell. It is risk "
                      "reduction."},
             {"title": "Start superficial",
              "body": "Depth is built across sessions based on how your skin responded to "
                      "the last one, rather than fixed in advance."},
             {"title": "Space sessions properly",
              "body": "Two to four weeks apart. Skin needs to complete its recovery before "
                      "the next injury is applied."},
             {"title": "Sun protection, without exception",
              "body": "Daily broad-spectrum sunscreen throughout the course and after it. "
                      "This is the step that decides the outcome."},
         ]},

        {"kind": "split", "eyebrow": "Aftercare",
         "h2": "Most peel complications are aftercare failures.",
         "body": ["Peeling and flaking for a few days is expected, picking at it is not. Skin "
                  "lifted before it is ready leaves marks that last far longer than the peel "
                  "would have.",
                  "The other frequent failure is sun. A week of good aftercare followed by a "
                  "sunny afternoon undoes the session and can leave the treated area darker "
                  "than when it started."],
         "cta": ("If the acne is still active", "acne-treatment-hyderabad"),
         "items": [
             {"title": "Do not pick",
              "body": "Let flaking lift on its own. Forcing it is the commonest cause of "
                      "post-peel marks."},
             {"title": "Sunscreen daily, reapplied",
              "body": "Not just on the day. Throughout the course and for weeks after it."},
         ]},

        VISIT,
    ],
    "faq_h2": "Chemical peel questions",
    "faqs": [
        ("How many chemical peel sessions will I need?",
         "Usually a course spaced two to four weeks apart. The number depends on the concern. "
         "Post-acne pigmentation often responds within a few sessions, melasma needs ongoing "
         "management."),
        ("Are chemical peels safe for Indian skin?",
         "Yes, when the depth is conservative, the skin is primed beforehand and sun "
         "protection is rigorous. The risk in darker skin is post-inflammatory "
         "pigmentation, which is exactly what a cautious protocol is designed to avoid."),
        ("How much do chemical peels cost?",
         "Priced per session and quoted after assessment, because the peel chosen and the "
         "number of sessions depend on your skin and your concern. A single session price "
         "without a course plan is not a useful comparison."),
        ("Will my skin peel visibly?",
         "Superficial peels usually cause mild flaking for a few days rather than dramatic "
         "shedding. Deeper peels peel more. Do not pick at it. That is the commonest cause of "
         "marks afterwards."),
        ("Can peels remove acne scars?",
         "They improve the brown marks left by acne, which many people take for scars. True "
         "indented scars need procedural treatment; peels will not fill them."),
        ("Can I have a peel while on acne treatment?",
         "It depends on the treatment. Some, particularly oral retinoids, require a gap before "
         "peeling. Tell the clinic everything you are using."),
    ],
    "related": [
        ("acne-treatment-hyderabad", "Acne treatment", "Control the acne before treating marks."),
        ("acne-scar-treatment-hyderabad", "Acne scar treatment", "For indented scars, which peels do not fill."),
        ("skin-boosters-hyderabad", "Skin boosters", "For hydration and quality."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "laser-hair-reduction-hyderabad", "template": "T1",
    "crumbs": [("Laser hair reduction", None)],
    "title": "Laser Hair Reduction in Hyderabad | Dr. Varada",
    "meta": "Laser hair reduction in Hyderabad: why it is reduction not removal, how many "
            "sessions, safety on Indian skin, and when facial hair needs investigating.",
    "eyebrow": "Hyderabad",
    "h1": "Laser hair reduction in Hyderabad",
    "sources": ["dermnet-phototype", "aad-hair-loss"],
    "lede": "It is called reduction rather than removal deliberately. A proper course removes "
            "most hair in the treated area for a long time, and a proportion returns. Anyone "
            "promising permanent removal is describing something the technology does not do.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "glance": [
        ("Sessions", "Typically 6–8, spaced by body area"),
        ("Works on", "Dark hair: targets pigment in the follicle"),
        ("Does not work on", "White, grey and very fine fair hair"),
        ("Indian skin", "Suitable with appropriate device settings"),
        ("Maintenance", "Occasional top-up sessions"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "How it works",
         "h2": "It targets pigment, which explains everything.",
         "body": [
             "Laser energy is absorbed by the pigment in the hair shaft and converted to "
             "heat, which damages the follicle. Two consequences follow directly from that "
             "mechanism, and they explain almost every question patients ask.",
             "First, it works on dark hair and does not work on white, grey or very fine fair "
             "hair: there is no pigment to absorb the energy. Second, because the skin also "
             "contains pigment, darker skin requires wavelengths and settings that target the "
             "hair without heating the surrounding skin. Getting that wrong causes burns and "
             "pigmentation, which is why device choice and operator judgement matter more than "
             "the brand name.",
             "Hair also grows in cycles, and only follicles in their active growth phase "
             "respond. That is why a course is needed. Each session catches a different "
             "proportion of the follicles.",
         ]},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "What a course involves",
         "items": [
             {"title": "Assess skin and hair type",
              "body": "Both decide the settings. In women with new or coarse facial hair, "
                      "an underlying hormonal cause is considered before starting."},
             {"title": "A patch test",
              "body": "Standard before a first course, particularly on darker skin. It "
                      "establishes tolerance before treating a whole area."},
             {"title": "Sessions spaced by area",
              "body": "Face is treated more frequently than legs, because hair cycles "
                      "differ by body site. Typically six to eight sessions."},
             {"title": "Maintenance afterwards",
              "body": "Occasional top-ups. A proportion of hair returns over time, and "
                      "hormonal changes can prompt new growth."},
         ]},

        {"kind": "table", "eyebrow": "The machines",
         "h2": "Diode, IPL, and what the difference means for you",
         "head": ["Technology", "How it behaves", "Where it fits"],
         "rows": [
             ["Diode laser", "A single wavelength, absorbed efficiently by hair pigment",
              "The workhorse for coarse hair; well tolerated on Indian skin"],
             ["IPL", "Broad-spectrum light rather than a laser, filtered to a range",
              "Less selective; better on fair skin with dark hair"],
             ["Longer wavelengths", "Penetrate deeper and interact less with skin pigment",
              "Preferred where skin is darker or has been recently sun-exposed"],
             ["Home devices", "Low fluence by regulation",
              "Slower, weaker, and no substitute for a course, but not dangerous"],
         ],
         "note": "IPL is routinely advertised as laser and it is not one. On skin that "
                 "carries pigment the distinction is practical rather than pedantic: a "
                 "broad-spectrum source is less selective, so the settings that clear hair "
                 "sit closer to the settings that burn."},

        {"kind": "split", "eyebrow": "Facial hair in women",
         "h2": "Sometimes the hair is a symptom.",
         "body": ["New or rapidly increasing coarse hair on the face, chest or abdomen in a "
                  "woman (particularly with irregular periods, acne or weight change), can "
                  "indicate an underlying hormonal condition, most commonly polycystic ovary "
                  "syndrome.",
                  "Treating the hair with laser without investigating that means treating a "
                  "symptom while the cause continues to produce new hair. It is a "
                  "conversation worth having before a course starts rather than after it "
                  "disappoints."],
         "cta": ("Book a consultation first", WHATSAPP),
         "items": [
             {"title": "Worth investigating first",
              "body": "A short assessment can save an unsatisfying course, and can find "
                      "something worth treating in its own right."},
             {"title": "Laser still helps",
              "body": "It is not either-or. Treating the cause and reducing the existing "
                      "hair work together."},
         ]},

        {"kind": "callout", "warn": True, "title": "Before each session",
         "body": "Shave the area rather than waxing, threading or plucking. The laser needs the "
                 "follicle intact and pigmented. Avoid sun exposure and tanning before and "
                 "after; tanned skin raises the risk of burns and pigmentation."},

        VISIT,
    ],
    "faq_h2": "Laser hair reduction questions",
    "faqs": [
        ("How many sessions will I need?",
         "Typically six to eight for a good result, spaced according to the body area. Some "
         "people need more, and occasional maintenance sessions afterwards are usual."),
        ("Is it permanent?",
         "It is permanent reduction, not permanent removal. A proper course removes most "
         "hair in the treated area for a long period, and a proportion returns over time. "
         "Anyone promising permanent removal is overstating what the technology does."),
        ("Does it work on white or grey hair?",
         "No. The laser targets pigment in the hair. White, grey and very fine fair hair "
         "have too little to absorb the energy, so they do not respond."),
        ("Is laser hair reduction safe for Indian skin?",
         "Yes, with appropriate wavelength and settings, and a patch test first. Darker skin "
         "contains more pigment, so incorrect settings risk burns and pigmentation, which is "
         "why the assessment matters more than the device brand."),
        ("Should I shave or wax before a session?",
         "Shave. Waxing, threading and plucking remove the follicle target the laser needs. "
         "Shaving leaves it intact."),
        ("Does it hurt?",
         "Most people describe a snapping sensation with each pulse. Modern devices with "
         "cooling make it well tolerated. Sensitive areas are more uncomfortable than legs "
         "or arms."),
    ],
    "related": [
        ("chemical-peels-hyderabad", "Chemical peels", "The other common course-based treatment."),
        ("acne-treatment-hyderabad", "Acne treatment", "If hormonal features are part of the picture."),
        ("dermatosurgery-hyderabad", "Dermatosurgery", "For moles, warts and skin tags."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "dermatosurgery-hyderabad", "template": "T1",
    "crumbs": [("Dermatosurgery", None)],
    "title": "Mole, Wart & Skin Tag Removal in Hyderabad | Dr. Varada",
    "meta": "Mole, wart, skin tag and cyst removal in Hyderabad by a dermatosurgeon of 45 "
            "years. Examined before removal, with histology where indicated. Book on WhatsApp.",
    "eyebrow": "Hyderabad",
    "h1": "Mole, wart and skin tag removal in Hyderabad",
    "lede": "Small procedures, done properly: examined before removal, removed by the method "
            "that suits the lesion, and sent for histology whenever there is any doubt about "
            "what it was.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["dermnet-keloid", "dermnet-nail-disorders", "iadvl-vitiligo-surgery-std"],
    "glance": [
        ("Treats", "Moles, warts, skin tags, cysts, corns, keloids"),
        ("Examined first", "Dermatoscopy before any mole is removed"),
        ("Histology", "Whenever there is diagnostic doubt"),
        ("Anaesthesia", "Local, day procedure"),
        ("Where", "Secunderabad clinic"),
        ("Scarring", "Discussed before, not after"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The principle",
         "h2": "Look at it before you remove it.",
         "body": [
             "A mole removed at a salon or by cautery without examination destroys the one "
             "thing that could have told you what it was. The overwhelming majority of moles "
             "are entirely benign, but the way you know that is by examining them with a "
             "dermatoscope beforehand and, where there is any doubt, sending the tissue for "
             "histology afterwards.",
             "That is the difference between a dermatosurgical removal and a cosmetic one, "
             "and it costs very little. Every mole removed here is examined first; anything "
             "with atypical features is excised properly rather than destroyed, so it can be "
             "examined under a microscope.",
             "The same principle applies more mundanely to warts and skin tags: what looks "
             "like a wart is occasionally not, and a lesion that keeps recurring after "
             "treatment is a reason to reconsider the diagnosis rather than to repeat the "
             "treatment.",
         ]},

        {"kind": "table", "eyebrow": "What is treated", "h2": "Common procedures",
         "head": ["Lesion", "Usual approach", "Notes"],
         "rows": [
             ["Moles", "Excision or shave, after dermatoscopy",
              "Atypical features mean excision with histology"],
             ["Skin tags", "Snip or cautery", "Quick; often several in one sitting"],
             ["Warts", "Cautery, cryotherapy or chemical", "Recurrence is common; may need repeat"],
             ["Sebaceous cysts", "Excision including the wall",
              "Leaving the wall behind is why they recur"],
             ["Corns and callus", "Paring and offloading advice",
              "Recurs unless the pressure cause is addressed"],
             ["Molluscum contagiosum", "Extraction or cautery of each lesion",
              "Common in children; spreads by contact and scratching"],
             ["Keloids", "Injection-based treatment first",
              "Excising a keloid casually usually makes it worse"],
             ["Dermatosis papulosa nigra", "Fine cautery",
              "Common in Indian skin; cosmetic, and treatable"],
         ],
         "note": "The keloid row is worth reading twice. In skin prone to keloid formation, "
                 "cutting one out without adjunctive treatment frequently produces a larger "
                 "one."},

        {"kind": "split", "eyebrow": "Before you agree",
         "h2": "Every removal leaves something.",
         "body": ["A removed lesion is replaced by a scar. Usually a small flat pale one, "
                  "sometimes not, and the risk depends on the site, the size and your own "
                  "healing. Chest, shoulders and the upper back scar less predictably than the "
                  "face.",
                  "So the conversation happens before the procedure: what mark to expect, "
                  "what the alternatives are including doing nothing, and what would make it "
                  "worth removing regardless. For a lesion being removed for cosmetic "
                  "reasons that conversation decides whether to proceed at all."],
         "cta": ("Where procedures are done", "locations-secunderabad"),
         "items": [
             {"title": "Site changes the answer",
              "body": "The same lesion is a different decision on the face than on the "
                      "shoulder."},
             {"title": "Doing nothing is an option",
              "body": "For a benign, asymptomatic lesion it is frequently the right one, "
                      "and it is offered."},
         ]},

        {"kind": "callout", "warn": True, "title": "A mole that has changed needs examining",
         "body": "A mole that is growing, changing colour, developing an irregular border, "
                 "itching, bleeding or looking different from your others should be examined "
                 "promptly. Not removed at a salon, and not watched for another year."},

        VISIT,
    ],
    "faq_h2": "Dermatosurgery questions",
    "faqs": [
        ("Will removing a mole leave a scar?",
         "Yes: every removal leaves some mark, usually small, flat and pale. The site matters: "
         "chest, shoulders and upper back scar less predictably than the face. This is "
         "discussed before the procedure, not after."),
        ("Is mole removal painful?",
         "The area is numbed with local anaesthetic, so the procedure itself is not painful. "
         "There is a sting as the anaesthetic goes in, and mild soreness afterwards for a "
         "day or two."),
        ("Do you send moles for testing?",
         "Whenever there is any diagnostic doubt, and always where the lesion is excised for "
         "clinical rather than purely cosmetic reasons. This is why removal at a salon is "
         "unwise. It destroys the tissue that would have provided the answer."),
        ("Why do my warts keep coming back?",
         "Warts are viral and recurrence is common. The virus can persist in surrounding skin. "
         "Repeated treatment is often needed. A lesion that recurs persistently is also a "
         "reason to confirm the diagnosis."),
        ("Can skin tags be removed in one visit?",
         "Usually yes. Several can typically be treated in a single sitting under local "
         "anaesthetic, and healing is quick."),
        ("My cyst came back after removal. Why?",
         "Almost always because the cyst wall was not completely removed. A cyst has a "
         "lining, and if any of it remains the cyst re-forms. Complete excision is the "
         "difference."),
    ],
    "related": [
        ("keloid-treatment-hyderabad", "Keloid treatment", "For raised and thickened scars."),
        ("nail-treatment-hyderabad", "Nail treatment", "Ingrown nails and nail surgery."),
        ("ear-lobe-repair-hyderabad", "Ear lobe repair", "Split, stretched and torn lobes."),
    ],
},

]
