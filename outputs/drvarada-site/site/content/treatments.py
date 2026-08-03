"""The procedure catalogue — pages added from the clinic's printed services card.

WHY THIS IS ONE MODULE RATHER THAN SPREAD ACROSS THE OTHERS
  These pages arrived together, from one source: the card the clinic hands to
  patients, listing everything it does under five headings. Auditing the site
  against that card found ten procedures with real search demand and no page.
  Keeping them in one module keeps the audit reviewable — you can hold the card
  next to this file and see what was closed. They are organised here under the
  card's own five headings for the same reason.

  Where a procedure already had a home it stayed there and was extended instead:
  FUE/FUT and eyelash grafting on `hair-grafting-hyderabad`, follicular-unit
  transplant for vitiligo on `vitiligo-graft-surgery`, diode and IPL on
  `laser-hair-reduction-hyderabad`, body RF on `rf-skin-tightening-hyderabad`,
  molluscum on `dermatosurgery-hyderabad`. Adding a thin page beside an existing
  one splits a query cluster in two and both rank worse.

THE COMPLIANCE BURDEN IS HIGHEST HERE
  Fillers, threads, PRP and mesotherapy are the treatments most often sold on
  promises — years off your face, permanent results, a fixed number of sessions
  decided before anyone has looked at you. None of that appears on these pages.
  Where the evidence is weak (PRP, mesotherapy, threads) the page says so, in
  the body text, above the booking link. That is the point of publishing them.
"""

from chrome import PHONE, WHATSAPP
from content.hyderabad_medical import CRED, VISIT

PAGES = [

# ══════════════════════════════════════════════════════════════════════════════
# The index — everything on the clinic's card, in one place
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "treatments", "template": "T3",
    "crumbs": [("Treatments", None)],
    "title": "All Treatments & Procedures | Dr. Varada's",
    "meta": "Every treatment at Dr. Varada's Skin & Hair Center, Secunderabad: dermatology, "
            "dermatosurgery, trichology, aesthetics and lasers, and what each does.",
    "eyebrow": "The full list",
    "h1": "Everything the clinic does",
    "lede": "Five kinds of work under one roof, done by one dermatologist rather than "
            "handed to a technician. Each entry links to a page that explains what the "
            "treatment achieves, what it will not achieve, and when the answer is to skip "
            "it.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Find the clinic", "locations-secunderabad")],
    "creds": CRED,
    "sections": [
        {"kind": "prose", "eyebrow": "How to use this page",
         "h2": "A list of procedures is not a menu.",
         "body": [
             "Most people arrive with a problem rather than a procedure in mind, and that is "
             "the right way round. The treatment is chosen after the diagnosis, and the same "
             "complaint: hair falling, a patch that will not clear, a scar. Has different "
             "answers depending on what is causing it.",
             "So read this as a map of what is available rather than a price list to pick "
             "from. If you already know the name of what you want, the links go straight "
             "there. If you do not, start with the condition and the procedure will follow "
             "from it.",
             "Everything listed is performed at the Secunderabad clinic by Dr. Varada. "
             "Nothing here is delegated to a therapist, and nothing is sold in packages "
             "bought before an examination.",
         ]},

        {"kind": "pillars", "eyebrow": "Medical work", "h2": "Conditions, hair, and surgery.",
         "intro": "The three practices that make up most of the clinic's list. Diagnosis "
                  "first in every one of them.",
         "items": [
             {"accent": "mint", "title": "Clinical dermatology",
              "body": "Skin disease investigated and managed properly, including the infections "
                      "and inflammatory conditions that get mistreated for months before they "
                      "arrive here.",
              "list": [
                  ("Psoriasis", "psoriasis-treatment-hyderabad", "Specialty"),
                  ("Eczema &amp; atopic dermatitis", "eczema-atopic-dermatitis-treatment"),
                  ("Allergy &amp; urticaria", "skin-allergy-rashes-treatment"),
                  ("Fungal infections", "fungal-infection-treatment-hyderabad"),
                  ("Acne", "acne-treatment-hyderabad"),
                  ("Keloids &amp; raised scars", "keloid-treatment-hyderabad"),
              ],
              "go": ("Start with the rash you have", "skin-allergy-rashes-treatment")},
             {"accent": "lilac", "title": "Trichology",
              "body": "Hair and scalp. Every course starts with finding the cause, because "
                      "the treatments for the common causes are not interchangeable.",
              "list": [
                  ("Hair fall &amp; pattern loss", "hair-loss-treatment-hyderabad"),
                  ("Alopecia areata", "alopecia-treatment-hyderabad", "Specialty"),
                  ("PRP &amp; microneedling", "prp-hair-treatment-hyderabad"),
                  ("Hair grafting (FUE/FUT)", "hair-grafting-hyderabad"),
                  ("Dandruff &amp; scalp care", "dandruff-treatment"),
                  ("Premature greying", "premature-greying-treatment"),
              ],
              "go": ("Find the cause first", "hair-loss-treatment-hyderabad")},
             {"accent": "mint", "title": "Surgical dermatology",
              "body": "Day procedures under local anaesthetic, by a dermatosurgeon. "
                      "Examined before removal, and sent for histology where there is any "
                      "doubt.",
              "list": [
                  ("Vitiligo grafting", "vitiligo-graft-surgery", "Specialty"),
                  ("Moles, warts &amp; skin tags", "dermatosurgery-hyderabad"),
                  ("Nail surgery &amp; nail disease", "nail-treatment-hyderabad"),
                  ("Ear lobe repair", "ear-lobe-repair-hyderabad"),
                  ("Hair grafting surgery", "hair-grafting-hyderabad"),
              ],
              "go": ("How surgical repigmentation works", "vitiligo-graft-surgery")},
         ]},

        {"kind": "split", "eyebrow": "The part most lists leave out",
         "h2": "Several of these are treatments you may not need.",
         "body": ["A clinic that lists forty procedures has an obvious incentive to find a use "
                  "for all of them. The counterweight is being told, in the consultation, when "
                  "a treatment is not indicated for what you have, and that happens here often "
                  "enough to be worth stating in advance.",
                  "It applies most to the aesthetic list. Toxin does nothing for volume "
                  "loss. Fillers do nothing for texture. Threads are not a facelift and do "
                  "not last like one. Where the evidence for a treatment is thin, the page "
                  "for it says so rather than describing it as advanced."],
         "cta": ("What a first appointment involves", "contact"),
         "items": [
             {"title": "Doing nothing is on the list",
              "body": "For a benign, asymptomatic lesion or a concern that does not bother "
                      "you day to day, it is frequently the right recommendation."},
             {"title": "One problem, several answers",
              "body": "Which one suits you depends on your skin, your budget and how much "
                      "downtime you can take. That conversation is the appointment."},
         ]},

        {"kind": "pillars", "eyebrow": "Aesthetic and device work",
         "h2": "Performed by the dermatologist.",
         "intro": "Conservative dosing, honest timelines, and no course bought before an "
                  "examination.",
         "items": [
             {"accent": "apricot", "title": "Aesthetic dermatology",
              "body": "Injectables and skin-quality work. What each one treats is narrower "
                      "than the marketing suggests, which is why they are listed "
                      "separately.",
              "list": [
                  ("Botulinum toxin", "anti-aging-botox-hyderabad"),
                  ("Dermal fillers", "dermal-fillers-hyderabad"),
                  ("Thread lift", "thread-lift-hyderabad"),
                  ("Mesotherapy", "mesotherapy-hyderabad"),
                  ("Skin boosters", "skin-boosters-hyderabad"),
                  ("Chemical peels", "chemical-peels-hyderabad"),
              ],
              "go": ("What toxin can and cannot do", "anti-aging-botox-hyderabad")},
             {"accent": "apricot", "title": "Lasers &amp; devices",
              "body": "Energy-based treatment, chosen for Indian skin. Settings matter "
                      "more than the brand name on the machine.",
              "list": [
                  ("Laser hair reduction", "laser-hair-reduction-hyderabad"),
                  ("Acne scar treatment", "acne-scar-treatment-hyderabad"),
                  ("RF skin tightening", "rf-skin-tightening-hyderabad"),
                  ("Excimer laser", "vitiligo-excimer-laser", "Specialty"),
                  ("Phototherapy (NB-UVB)", "vitiligo-phototherapy"),
              ],
              "go": ("Why reduction, not removal", "laser-hair-reduction-hyderabad")},
             {"accent": "mint", "title": "The specialisms",
              "body": "The practice began as a vitiligo hospital. Both of these have their "
                      "own reference sections rather than a single service page.",
              "list": [
                  ("Vitiligo: the full section", "vitiligo", "Specialty"),
                  ("Psoriasis: the full section", "psoriasis", "Specialty"),
                  ("Vitiligo graft surgery", "vitiligo-graft-surgery"),
                  ("Systemics &amp; biologics", "psoriasis-biologics"),
                  ("What treatment costs", "vitiligo-cost"),
              ],
              "go": ("Read the vitiligo section", "vitiligo")},
         ]},

        {"kind": "callout", "title": "Not sure which of these you need?",
         "body": "Send a photograph on WhatsApp with a sentence about how long it has been "
                 "there. The clinic will tell you whether it needs an appointment, which one, "
                 "and what to bring, before you travel."},

        VISIT,
    ],
    "faq_h2": "Questions about the treatment list",
    "faqs": [
        ("Are all these treatments done at the Secunderabad clinic?",
         "Yes. There is one consulting location, in Karkhana, Secunderabad, and the "
         "consulting rooms, phototherapy and the surgical list are all at that address."),
        ("Who performs the procedures?",
         "Dr. Varada. Injectables, lasers and surgery are performed by the dermatologist rather "
         "than delegated to a therapist, which is the main reason the aesthetic list here is "
         "shorter and more conservative than at a chain clinic."),
        ("Do I have to book a package?",
         "No. Courses are planned after an examination, and the number of sessions depends "
         "on what is found. A package sold before anyone has looked at your skin is a "
         "pricing decision, not a treatment plan."),
        ("How do I know which treatment I need?",
         "Usually you do not, and you are not expected to. Describe the problem instead. The "
         "treatment follows from the diagnosis, and for the same complaint the right answer "
         "differs between people."),
        ("Can I consult about these online?",
         "For most conditions, yes. Procedures need you in the room, but the assessment "
         "that decides whether a procedure is appropriate can often be done by video."),
        ("Is there anything the clinic does not do?",
         "Body contouring surgery, hair systems and anything sold on the promise of a "
         "fixed outcome. Where a treatment is outside the practice's scope you will be "
         "told and, where possible, pointed somewhere appropriate."),
    ],
    "related": [
        ("contact", "Contact and directions", "How to reach the clinic."),
        ("locations-secunderabad", "The clinic in Secunderabad", "Where everything is done."),
        ("online-consultation", "Consult online", "If you are outside Hyderabad."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# CLINICAL DERMATOLOGY — anti-fungal protocols
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "fungal-infection-treatment-hyderabad", "template": "T1",
    "condition": "Dermatophytosis",
    "crumbs": [("Fungal infections", None)],
    "title": "Fungal Infection Treatment in Hyderabad | Dr. Varada",
    "meta": "Ringworm and fungal skin infection treatment in Hyderabad. Why over-the-counter "
            "combination creams make it worse, and how resistant tinea is managed.",
    "eyebrow": "Hyderabad",
    "h1": "Fungal skin infection treatment in Hyderabad",
    "sources": ["dermnet-tinea", "nhs-ringworm", "pmc-terbinafine-resistance", "pmc-indotineae-outcomes"],
    "lede": "Ringworm in India is not the illness it was ten years ago. It spreads further, "
            "recurs harder and takes far longer to clear. Largely because of what is being sold "
            "for it over the counter, and partly because the organism itself has changed.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "glance": [
        ("Treats", "Tinea of body, groin, feet, scalp and nails"),
        ("Typical course", "Weeks of oral treatment, not days"),
        ("Main obstacle", "Steroid-combination creams bought first"),
        ("Also treated", "Household contacts, or it returns"),
        ("Confirmed by", "Scraping and microscopy where unclear"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "callout", "warn": True,
         "title": "If you are using a combination cream, stop and bring the tube",
         "body": "The creams sold across Indian counters for “ring infection” usually contain a "
                 "potent steroid alongside the antifungal. The steroid settles the itch within "
                 "a day, which is why they sell, while suppressing the local immune response "
                 "the body needs to clear the fungus. The rash spreads, loses its ring shape, "
                 "and becomes far harder to treat. Bring the packet to the appointment."},

        {"kind": "prose", "eyebrow": "Why this changed",
         "h2": "A common infection that stopped behaving like one.",
         "body": [
             "For decades tinea was a straightforward problem: an antifungal cream for two "
             "or three weeks and it was over. Across South Asia that stopped being true. "
             "Infections now cover large areas, involve several family members at once, "
             "recur within weeks of stopping treatment, and fail the drugs that used to "
             "work reliably.",
             "Two things drove it. The first is the steroid-antifungal combination cream, "
             "available without prescription and applied for months: it changes the appearance "
             "of the rash so it no longer looks like ringworm, and it suppresses the skin's "
             "ability to fight the organism. The second is a dermatophyte that has become "
             "widespread in India and is frequently resistant to terbinafine, the drug most "
             "often prescribed first.",
             "The practical consequence for you is duration. A course that would once have "
             "run two weeks now commonly runs six to twelve, sometimes longer for nails and "
             "scalp. Stopping when the itch settles is the single commonest reason people "
             "end up back with the same rash a month later.",
         ]},

        {"kind": "diagram", "eyebrow": "The mechanism",
         "h2": "An infection of the dead surface layer.",
         "intro": "The fungus lives in the outermost dead layer of skin and spreads outward from where it started, which is why the edge is active and scaly while the middle looks calmer.",
         "caption": "A steroid cream removes the redness without touching the fungus. The rash looks better within days and is meanwhile spreading further and deeper — which is why the tube matters more than the rash.",
         "rail": True,
    # "Active scaly border" was at y=19, six percent above the middle block's
    # top face, so it named the background and its leader ran down THROUGH the
    # annular lesion it was pointing at. Read off `diagram_grid.py`: the raised
    # rim's left limb is at (34, 33). Label 1 was on the block's top edge
    # rather than in the dead layer that carries the threads.
 "labels": [
     {"text": "Threads in the dead top layer", "x": 14, "y": 38, "row": 1, "find": "artwork"},
     {"text": "Active scaly border", "x": 34, "y": 33, "find": "edge:pale|skin"},
     {"text": "Calmer above, spreading below", "x": 70, "y": 45, "find": "artwork"},
 ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/C3-fungal-infection.webp", "w": 1820, "h": 1024,
             "alt": "Three panels. The first magnifies the outermost dead layer of skin with fine branching fungal threads growing sideways through it. The second shows the same infection from above as a ring with a raised scaly active border and a clearer centre. The third shows that ring after a steroid cream: the surface looks calm, but the threads beneath have spread much further and deeper than the visible edge."}},

        {"kind": "table", "eyebrow": "What is being treated", "h2": "Where it appears",
         "head": ["Site", "Usual name", "What treatment involves"],
         "rows": [
             ["Body, trunk, limbs", "Tinea corporis",
              "Oral plus topical; weeks, reviewed rather than fixed"],
             ["Groin and inner thigh", "Tinea cruris",
              "Same course; clothing and moisture matter as much"],
             ["Feet and between toes", "Tinea pedis",
              "Often the reservoir that reinfects everything else"],
             ["Scalp, usually in children", "Tinea capitis",
              "Always oral: creams cannot reach the follicle"],
             ["Nails", "Onychomycosis",
              "Months, confirmed before starting: see nail treatment"],
             ["Face", "Tinea faciei",
              "Most often the one misdiagnosed and steroid-treated"],
         ],
         "note": "A rash that has been treated with a steroid cream frequently loses its "
                 "ring shape and scaly edge entirely. Where the picture is unclear a "
                 "scraping is examined rather than guessed at."},

        {"kind": "steps", "eyebrow": "The protocol", "h2": "How a course is actually run",
         "items": [
             {"title": "Stop the steroid, confirm the diagnosis",
              "body": "The combination cream comes off first. Where the appearance has been "
                      "altered by it, or where previous treatment has failed, a skin "
                      "scraping settles what is actually there."},
             {"title": "Treat orally, and for long enough",
              "body": "Extensive or recurrent disease needs systemic treatment, not cream "
                      "alone. Dose and duration are set by site and severity, and reviewed. Not "
                      "fixed in advance from a chart."},
             {"title": "Treat the household and the clothes",
              "body": "Tinea moves between family members and lives in towels, bedding and "
                      "waistbands. Treating one person in a house where three are itching "
                      "is why it comes back."},
             {"title": "Review before stopping",
              "body": "Clear skin is not the same as cleared infection. The end of a course "
                      "is decided at a review, and stopping at the point the itch settles "
                      "is the commonest cause of relapse."},
         ]},

        {"kind": "split", "eyebrow": "Resistant infection",
         "h2": "When the first drug does not work.",
         "body": ["Terbinafine failure is now common in India rather than exceptional. Where an "
                  "adequate course has genuinely been taken and the rash has not responded, the "
                  "answer is to change the drug and extend the duration, and, where it matters, "
                  "to confirm what organism is present rather than cycling through "
                  "prescriptions.",
                  "That decision needs a proper history: what was taken, at what dose, for "
                  "how long, and whether it was actually taken every day. A large share of "
                  "apparent resistance is an incomplete course, and the two are managed "
                  "very differently. Bring your old prescriptions."],
         "cta": ("If the nails are involved too", "nail-treatment-hyderabad"),
         "items": [
             {"title": "Longer, not stronger",
              "body": "Extending a course is usually more effective than escalating the "
                      "dose, and it is monitored where treatment runs for months."},
             {"title": "Liver checks where indicated",
              "body": "Prolonged oral antifungal treatment is monitored with blood tests "
                      "when duration or other medication makes that sensible."},
         ]},

        VISIT,
    ],
    "faq_h2": "Fungal infection questions",
    "faqs": [
        ("Why does my ringworm keep coming back?",
         "Three usual reasons: the course was stopped when the itch settled rather than "
         "when the infection cleared, an untreated family member or a pair of shoes keeps "
         "reinfecting you, or the organism does not respond to the drug that was used. All "
         "three are addressable, and which one applies is worked out from the history."),
        ("Can I just use a cream from the pharmacy?",
         "For a small, new, single patch sometimes yes. The problem is what is usually sold. "
         "Most over-the-counter “ring” creams in India contain a potent steroid, which settles "
         "the itch quickly and makes the infection worse and harder to diagnose."),
        ("How long does treatment take?",
         "Longer than most people expect. Body and groin infections commonly need several "
         "weeks of oral treatment, scalp longer, nails months. The duration is reviewed "
         "rather than fixed at the first visit."),
        ("Is it contagious to my family?",
         "Yes: it spreads by direct contact and through shared towels, bedding and clothing. If "
         "others at home are itching they need treating at the same time, or the infection "
         "simply circulates."),
        ("Do I need a test?",
         "Not always. Where the rash looks typical and has not been treated before, "
         "treatment can begin on the clinical picture. Where a steroid cream has changed "
         "its appearance, or previous treatment has failed, a scraping is examined first."),
        ("Are the tablets safe to take for weeks?",
         "Oral antifungals are well established and generally tolerated. Where a course "
         "runs long, or you take other medication, blood tests are used to monitor it. Tell "
         "the clinic everything you are taking, including anything bought over the counter."),
    ],
    "related": [
        ("skin-allergy-rashes-treatment", "Rashes and allergy", "If it may not be fungal."),
        ("nail-treatment-hyderabad", "Nail treatment", "When nails are involved."),
        ("dandruff-treatment", "Dandruff and scalp", "For a flaking, itchy scalp."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# CLINICAL / SURGICAL — keloid protocols
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "keloid-treatment-hyderabad", "template": "T1",
    "condition": "Keloid",
    "crumbs": [("Keloid treatment", None)],
    "title": "Keloid & Raised Scar Treatment | Dr. Varada",
    "meta": "Keloid and hypertrophic scar treatment in Hyderabad: injection protocols, why "
            "cutting a keloid out usually makes it larger, and how recurrence is managed.",
    "eyebrow": "Hyderabad",
    "h1": "Keloid and raised scar treatment in Hyderabad",
    "sources": ["dermnet-keloid", "nhs-keloid", "dermnet-phototype"],
    "lede": "A keloid is scar tissue that did not know when to stop. It can be flattened, "
            "softened and made much less symptomatic, but it is managed as a tendency rather "
            "than removed, and anyone offering to simply cut it out is describing how keloids "
            "get bigger.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "glance": [
        ("Treats", "Keloids and hypertrophic scars"),
        ("First line", "Intralesional injection, spaced weeks apart"),
        ("Realistic outcome", "Flatter, softer, less itchy: not erased"),
        ("Recurrence", "Common; planned for rather than denied"),
        ("Surgery alone", "Usually the wrong answer"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What it is",
         "h2": "Not a bad scar. A different one.",
         "body": [
             "An ordinary scar stays within the boundary of the original wound. A keloid grows "
             "past it, into skin that was never injured, and keeps going: often months after "
             "the wound itself healed. That distinction matters, because it is what makes "
             "surgery on its own counterproductive: cutting a keloid out creates a fresh, "
             "larger wound in skin that has already demonstrated how it heals.",
             "A hypertrophic scar is the milder relative. It is raised and red but stays "
             "within the original wound, and it frequently settles considerably on its own "
             "over a year or two. Telling the two apart changes the plan, which is why the "
             "scar is examined rather than treated from a description.",
             "Ear lobes after piercing, the chest, shoulders and upper back are where they form "
             "most readily, and a personal or family history of them is the strongest predictor "
             "that the next wound will do the same. If you know you are prone to keloids, that "
             "is worth saying before any elective procedure, including a cosmetic one.",
         ]},

        {"kind": "diagram", "eyebrow": "The difference",
         "h2": "A keloid outgrows its own wound.",
         "intro": "An ordinary scar fills the injury and stops. A keloid keeps producing collagen after the wound has closed and spreads onto skin that was never injured — which is what makes it a different problem rather than a bad version of the same one.",
         "caption": "Treatment aims to flatten and quieten, not to erase. A keloid that stops growing, stops itching and settles is the realistic result.",
         "rail": True,
"labels": [
    {"text": "Collagen stays inside the wound", "x": 23, "y": 40, "find": "artwork"},
    {"text": "Collagen grows past it", "x": 62, "y": 26, "find": "artwork"},
],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/C5-keloid.webp", "w": 1820, "h": 1024,
             "alt": "Two blocks of skin, each showing the same small original wound marked by a faint dotted outline. In the left block new collagen has filled the wound in orderly bundles and stayed inside that outline, leaving a flat surface. In the right block thick swirling collagen has grown well beyond the outline in every direction and pushed the surface into a raised mound."}},

        {"kind": "table", "eyebrow": "The options", "h2": "What is used, and what it does",
         "head": ["Approach", "What it achieves", "Notes"],
         "rows": [
             ["Intralesional steroid", "Flattens and softens; settles itch and pain",
              "First line for most; repeated every few weeks"],
             ["Steroid with 5-fluorouracil", "Often flatter, faster, than steroid alone",
              "Used where response is slow or the scar is dense"],
             ["Cryotherapy", "Useful for smaller, early lesions",
              "Repeated cycles; can lighten surrounding skin"],
             ["Silicone gel or sheeting", "Modest, mainly preventive",
              "Needs months of daily use to be worth anything"],
             ["Pressure therapy", "Standard after ear lobe keloid excision",
              "Clips or pressure earrings, worn for months"],
             ["Excision, with adjuvant treatment", "Considered for selected lesions",
              "Never alone: recurrence after plain excision is high"],
         ],
         "note": "The last row carries the whole page. Excision of a keloid without an "
                 "adjuvant plan afterwards has a high recurrence rate, and what returns is "
                 "frequently larger than what was removed."},

        {"kind": "steps", "eyebrow": "How a course runs",
         "h2": "Injections, spaced, and reviewed.",
         "items": [
             {"title": "Examine and classify",
              "body": "Keloid or hypertrophic, how long it has been there, whether it is still "
                      "growing, and what it does to you. Itch and pain are often the reason to "
                      "treat, not appearance."},
             {"title": "Start injections",
              "body": "Delivered into the scar itself, which is uncomfortable for a few "
                      "seconds and quick. Sessions are spaced by several weeks so the "
                      "response can be judged before the next."},
             {"title": "Judge at the third or fourth",
              "body": "Softening and reduced itch usually come first, flattening after. If "
                      "there has been no movement by then, the protocol changes rather than "
                      "repeating indefinitely."},
             {"title": "Plan for recurrence",
              "body": "Keloids recur, and a scar that has flattened may need occasional "
                      "top-up treatment. Being told that at the start is the difference "
                      "between a managed condition and a disappointment."},
         ]},

        {"kind": "split", "eyebrow": "Honest limits",
         "h2": "Flatter and quieter, not gone.",
         "body": ["The realistic result is a scar that is much less raised, much less itchy and "
                  "considerably less noticeable, usually leaving a flat mark that differs in "
                  "colour from the skin around it. Skin that has been stretched by a keloid for "
                  "years does not return to how it was.",
                  "Injections have their own trade-offs, and they are explained before the "
                  "first one rather than discovered afterwards: the treated area can thin, "
                  "and in darker skin it can lighten, sometimes visibly. Conservative dosing "
                  "spread across more sessions is the usual way to limit that."],
         "cta": ("If the keloid is on an ear lobe", "ear-lobe-repair-hyderabad"),
         "items": [
             {"title": "Colour change is likely",
              "body": "A treated keloid usually leaves a flat mark. Whether that is an "
                      "improvement on what you have is your call to make."},
             {"title": "Prevention counts double",
              "body": "If you form keloids, say so before any elective procedure. It "
                      "changes the technique used and the aftercare given."},
         ]},

        VISIT,
    ],
    "faq_h2": "Keloid questions",
    "faqs": [
        ("Can a keloid be removed completely?",
         "It can be flattened and softened substantially, and in selected cases excised, but "
         "excision alone has a high recurrence rate and what returns is often larger. Treatment "
         "aims at a flat, quiet scar rather than skin with no mark at all."),
        ("How many injection sessions will I need?",
         "Sessions are spaced several weeks apart and the response is judged over the first "
         "three or four. Some scars settle in a handful, dense long-standing ones take "
         "longer. The number is reviewed, not fixed at the first visit."),
        ("Do the injections hurt?",
         "There is a strong stinging sensation for a few seconds as the injection goes into "
         "the scar, which is firmer than normal skin. It is brief, and the session itself "
         "takes only minutes."),
        ("Why did my keloid come back after surgery elsewhere?",
         "Almost certainly because it was excised without adjuvant treatment afterwards. "
         "Cutting a keloid out creates a fresh wound in skin already proven to over-heal, "
         "so surgery is planned as part of a protocol rather than as the treatment."),
        ("Will treatment lighten my skin?",
         "Steroid injections can thin the treated area and lighten it, which is more "
         "visible in darker skin. Dosing is kept conservative and spread across sessions to "
         "limit it, and the risk is discussed before starting."),
        ("My keloid is from an ear piercing. Can it be treated?",
         "Yes, and ear lobe keloids are among the more satisfying to treat. Depending on "
         "size the plan may be injections alone, or excision with injections and pressure "
         "therapy afterwards to hold the result."),
    ],
    "related": [
        ("ear-lobe-repair-hyderabad", "Ear lobe repair", "For keloids and splits from piercing."),
        ("dermatosurgery-hyderabad", "Dermatosurgery", "Moles, warts, cysts and skin tags."),
        ("acne-scar-treatment-hyderabad", "Acne scar treatment", "For indented rather than raised scars."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# SURGICAL DERMATOLOGY — ear lobe repair
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "ear-lobe-repair-hyderabad", "template": "T1",
    "crumbs": [("Ear lobe repair", None)],
    "title": "Ear Lobe Repair Surgery in Hyderabad | Dr. Varada",
    "meta": "Ear lobe repair in Hyderabad for split, stretched or torn lobes and piercing "
            "keloids. A day procedure under local anaesthetic, and when to re-pierce.",
    "eyebrow": "Hyderabad",
    "h1": "Ear lobe repair surgery in Hyderabad",
    "sources": ["dermnet-keloid", "nhs-keloid"],
    "lede": "A lobe split by decades of heavy earrings, or torn in a single moment, is repaired "
            "in a short day procedure under local anaesthetic. The technical part is not "
            "closing it. It is closing it so the notch does not come back at the edge.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "glance": [
        ("Treats", "Split, torn, stretched and elongated lobes"),
        ("Also", "Keloids from piercing"),
        ("Anaesthesia", "Local; you are awake and go home"),
        ("Takes", "Around 30–45 minutes for both sides"),
        ("Stitches out", "About a week later"),
        ("Re-piercing", "Usually after some months, in a new spot"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "Why lobes split",
         "h2": "Usually years, occasionally a second.",
         "body": [
             "Most repairs are for a slow problem. Heavy earrings worn daily stretch the "
             "piercing downwards over years until the channel elongates into a slit and "
             "finally reaches the edge of the lobe. By then the earring no longer sits "
             "properly and the lobe has thinned around it.",
             "The rest are sudden: an earring caught on clothing, a child's hand, a dupatta. A "
             "fresh tear can be repaired promptly, and there is no advantage in waiting for it "
             "to heal on its own first. A healed slit has to be freshened before it can be "
             "closed anyway.",
             "Both are the same operation. The edges of the tract are pared back to raw "
             "tissue and closed in layers, with the closure arranged so the lower border of "
             "the lobe stays smooth. A repair that simply stitches the slit tends to leave a "
             "small notch exactly where it is most visible.",
         ]},

        {"kind": "diagram", "eyebrow": "What the repair involves",
         "h2": "Four steps, under local anaesthetic.",
         "intro": "A torn lobe does not close on its own, because the edges of the old tract have healed over with skin. That lining has to be removed before the two sides can knit — which is why the repair is a small operation and not a stitch.",
         "caption": "The lobe is repierced only after it has fully healed, usually at six to eight weeks, and deliberately away from the repair line. Piercing back through the scar is the commonest reason a repaired lobe tears a second time.",
         "label_col": 0,
         "labels": [
             {"text": "Torn through", "x": 15, "y": 83, "lead": 2},
             {"text": "Tract excised", "x": 35, "y": 83, "lead": 2},
             {"text": "Sutured", "x": 55, "y": 83, "lead": 2},
             {"text": "Healed", "x": 76, "y": 83, "lead": 2},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D17-ear-lobe-repair.webp", "w": 1820, "h": 1024,
             "alt": "Four stages of one ear in a row on brown skin. In the first, a piercing hole has torn all the way through the lower edge of the lobe, splitting it into two prongs lined with a thin pale border of healed skin. In the second that lining has been trimmed away as a narrow sliver, which lies beside the ear, leaving two fresh edges. In the third the edges are held together by a single row of fine stitches. In the fourth the lobe has healed to one smooth continuous edge with only a faint line where the repair was, and a small new piercing point marked higher up and away from it."}},

        {"kind": "steps", "eyebrow": "What happens", "h2": "A short list, done properly.",
         "items": [
             {"title": "Assessment and planning",
              "body": "How much lobe there is to work with, whether one side or both, and "
                      "whether you form keloids. That last answer changes the aftercare before "
                      "anything is cut."},
             {"title": "Local anaesthetic",
              "body": "The lobe is numbed. There is a sting as it goes in and nothing much "
                      "after that; you are awake and can hear the conversation throughout."},
             {"title": "Repair in layers",
              "body": "The old tract is excised and the lobe closed in layers, shaped so "
                      "the free border remains an even curve rather than a step."},
             {"title": "A week to stitches out",
              "body": "Keep it dry, no earrings on that side, and back in about a week. "
                      "Most people work the next day."},
         ]},

        {"kind": "table", "eyebrow": "Common questions before booking",
         "h2": "What people usually want to know",
         "head": ["Question", "Short answer", "Detail"],
         "rows": [
             ["Can both ears be done together?", "Yes",
              "Usual, and it is one appointment rather than two"],
             ["Will there be a scar?", "A fine line",
              "It sits along the repair and settles over months"],
             ["Can I be re-pierced?", "Usually, after some months",
              "Through a fresh site, not through the scar"],
             ["What if I keloid?", "The plan changes",
              "Adjuvant injections and pressure therapy afterwards"],
             ["Is it done under anaesthesia?", "Local only",
              "A day procedure; no admission, no fasting"],
             ["How soon can I wear earrings?", "After re-piercing heals",
              "Light ones first; heavy drops are what caused this"],
         ],
         "note": "Re-piercing through the repair itself is the usual reason a lobe splits a "
                 "second time. A new site, and lighter earrings, is the whole prevention."},

        {"kind": "split", "eyebrow": "Keloids on the lobe",
         "h2": "The other reason people come about ears.",
         "body": ["A firm, growing lump at a piercing site is usually a keloid, and the ear "
                  "lobe is where they form most readily. They are treatable, and the one thing "
                  "not to do is have it cut off without a plan for what happens next, because a "
                  "keloid excised on its own frequently returns larger.",
                  "Depending on size, the answer is injections alone, or excision followed "
                  "by injections and pressure therapy worn for some months. Either way it "
                  "is a course rather than an appointment, and that is said at the start."],
         "cta": ("How keloids are treated", "keloid-treatment-hyderabad"),
         "items": [
             {"title": "Do not let it be snipped",
              "body": "Removal without adjuvant treatment is the commonest reason an ear "
                      "keloid comes back bigger than before."},
             {"title": "Pressure earrings work",
              "body": "Unglamorous, and worn for months, but they are a large part of why a "
                      "repaired lobe stays flat."},
         ]},

        VISIT,
    ],
    "faq_h2": "Ear lobe repair questions",
    "faqs": [
        ("How long does ear lobe repair take?",
         "The procedure itself takes around thirty to forty-five minutes for both sides. It is "
         "a day procedure under local anaesthetic: you arrive, it is done, and you go home the "
         "same morning."),
        ("Will I be able to wear earrings again?",
         "Yes, after re-piercing, which is usually done some months later once the repair "
         "has fully settled. The new piercing goes through a fresh site rather than through "
         "the scar, and lighter earrings are strongly advised."),
        ("Does it leave a visible scar?",
         "There is a fine line along the repair. It is pink initially and fades over "
         "months. The lower border of the lobe is deliberately shaped during closure so "
         "there is no notch, which is the mark people actually notice."),
        ("Can a very stretched lobe be repaired?",
         "Usually yes, though a lobe stretched over years has less tissue to work with and "
         "the result depends on what remains. This is assessed before booking rather than "
         "on the day."),
        ("Is the procedure done under general anaesthesia?",
         "No. Local anaesthetic is sufficient. You are awake, there is no admission and no "
         "fasting, and most people are back at work the following day."),
        ("I get keloids. Can I still have this done?",
         "Yes, with a different aftercare plan. Usually injections and pressure therapy "
         "following the repair. Tell the clinic before booking, because it changes both the "
         "technique and what you will need to do afterwards."),
    ],
    "related": [
        ("keloid-treatment-hyderabad", "Keloid treatment", "For lumps at a piercing site."),
        ("dermatosurgery-hyderabad", "Dermatosurgery", "The rest of the minor surgery list."),
        ("locations-secunderabad", "The clinic", "Where the surgical list runs."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# SURGICAL DERMATOLOGY — nail surgery and nail disease
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "nail-treatment-hyderabad", "template": "T1",
    "crumbs": [("Nail treatment", None)],
    "title": "Nail Treatment & Nail Surgery in Hyderabad | Dr. Varada",
    "meta": "Nail disease and nail surgery in Hyderabad: ingrown toenails, fungal nails, nail "
            "psoriasis and changes that need investigating, by a dermatologist.",
    "eyebrow": "Hyderabad",
    "h1": "Nail treatment and nail surgery in Hyderabad",
    "sources": ["dermnet-nail-disorders", "dermnet-fungal-nails", "nhs-fungal-nail", "dermnet-nail-psoriasis", "dermnet-ingrown-toenail"],
    "lede": "Nails are skin, and they get the same diseases skin does: fungus, psoriasis, "
            "lichen planus, alopecia areata. Which is why a nail that has changed is worth a "
            "dermatologist looking at, rather than months of an antifungal that may be treating "
            "the wrong thing.",
    "acts": [("Book on WhatsApp", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "glance": [
        ("Treats", "Ingrown nails, fungal nails, nail psoriasis"),
        ("Surgery", "Ingrown nail procedures, nail biopsy"),
        ("Confirmed first", "Fungal nails tested before long treatment"),
        ("Duration", "Nails grow slowly: months, not weeks"),
        ("Anaesthesia", "Local ring block for procedures"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The common mistake",
         "h2": "Half of thickened nails are not fungal.",
         "body": [
             "A thickened, discoloured, crumbling nail is assumed to be fungus by almost "
             "everybody, including a fair number of prescriptions. A substantial proportion are "
             "something else: psoriasis of the nail, damage from repeated trauma, lichen "
             "planus, or the pitting that goes with alopecia areata.",
             "This matters because the treatments are not interchangeable and the courses "
             "are long. Months of oral antifungal for a nail that has psoriasis achieves "
             "nothing except the monitoring that goes with the drug. So where a long course "
             "is being considered, the diagnosis is confirmed before it starts rather than "
             "assumed from the appearance.",
             "The other thing nails do is report on the rest of you. Sudden changes across "
             "several nails, a dark streak in one, or nail changes appearing alongside a "
             "rash are all reasons for an examination rather than a pedicure.",
         ]},

        {"kind": "diagram", "eyebrow": "The nail unit",
         "h2": "The nail you see was made months ago.",
         "intro": "A nail is produced by a growth zone tucked under the skin at its base and then slides forward over its bed. Damage there shows up at the fingertip months later, which is why nail treatment is slow and why the diagnosis matters before anything is prescribed.",
         "caption": "Half of thickened nails are not fungal. Psoriasis, injury and a few other causes look similar at a glance, and antifungals do nothing for them.",
         "rail": True,
"labels": [
    {"text": "Where the nail is made", "x": 16, "y": 33, "find": "artwork"},
    {"text": "Fungal thickening", "x": 54, "y": 60, "row": 2, "find": "artwork"},
    {"text": "Pitting, and lifting", "x": 65, "y": 70, "row": 1, "find": "artwork"},
    {"text": "A single dark band", "x": 77, "y": 80, "find": "artwork"},
],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/C6-nail-unit.webp", "w": 1820, "h": 1024,
             "alt": "On the left, a fingertip in long section showing the growth zone under the skin at the base of the nail, the pale crescent, the nail plate lying over its bed, and the free edge. On the right, three nails seen from above: one thickened and crumbling from the free edge, one covered in small round pits with a patch lifting from its bed, and one crossed by a single dark band running lengthwise."}},

        {"kind": "table", "eyebrow": "What is treated", "h2": "Nail problems and their answers",
         "head": ["Problem", "Usual approach", "Notes"],
         "rows": [
             ["Ingrown toenail", "Procedure under local anaesthetic",
              "Recurrent ones need the nail edge dealt with, not just trimmed"],
             ["Fungal nail infection", "Oral treatment, confirmed first",
              "Months; topical alone rarely reaches the nail bed"],
             ["Nail psoriasis", "Treated as psoriasis, not as fungus",
              "Often the clue that a rash elsewhere is psoriatic"],
             ["Pitting and ridging", "Depends on cause",
              "Seen in psoriasis, eczema and alopecia areata"],
             ["Chronic paronychia", "Address the moisture and the inflammation",
              "Common in people whose hands are wet all day"],
             ["A dark streak in one nail", "Examined promptly",
              "Usually benign, but it is not something to watch for a year"],
         ],
         "note": "Recurrent ingrown toenails are the one where repeated trimming is the "
                 "problem rather than the treatment. A definitive procedure on the nail "
                 "edge is what stops the cycle."},

        {"kind": "split", "eyebrow": "Nail surgery",
         "h2": "Short procedures, done with a ring block.",
         "body": ["Nail procedures are done under local anaesthetic given as a ring block at "
                  "the base of the digit. The injection is the uncomfortable part and it is "
                  "brief; the procedure itself is felt as pressure rather than pain, and you "
                  "walk out afterwards.",
                  "For a recurrent ingrown toenail the aim is to stop it recurring, which means "
                  "treating the offending edge of the nail rather than cutting the spike out "
                  "again. For a nail that is changing in a way nobody can explain, a biopsy is "
                  "sometimes the only way to get an answer. Small, and worth it."],
         "cta": ("If the skin is fungal too", "fungal-infection-treatment-hyderabad"),
         "items": [
             {"title": "Healing is slow by nature",
              "body": "A fingernail takes around six months to grow out fully and a toenail "
                      "considerably longer. Improvement is judged against that."},
             {"title": "Footwear is part of the treatment",
              "body": "For ingrown nails and recurrent fungal infection, what you put your "
                      "feet into all day matters as much as what is prescribed."},
         ]},

        {"kind": "callout", "warn": True, "title": "A new dark streak in a single nail",
         "body": "A brown or black band appearing in one nail: particularly if it is widening, "
                 "irregular, or the pigment extends onto the surrounding skin. Should be "
                 "examined promptly rather than watched. The overwhelming majority are entirely "
                 "benign, and the way you establish that is by looking at it properly."},

        VISIT,
    ],
    "faq_h2": "Nail treatment questions",
    "faqs": [
        ("How long does fungal nail treatment take?",
         "Months, because the nail has to grow out. Toenails take longer than fingernails, "
         "and the treated nail does not look better until new growth reaches the tip. This "
         "is precisely why the diagnosis is confirmed before a long course is started."),
        ("Is my thick yellow nail definitely fungal?",
         "Not necessarily. Psoriasis, repeated trauma and lichen planus all produce similar "
         "changes, and the treatments are completely different. Where a long course of "
         "medication is being considered, it is worth confirming what you have first."),
        ("Will removing an ingrown toenail stop it coming back?",
         "Simply cutting out the spike usually does not. It grows back the same way. A "
         "procedure that addresses the edge of the nail is what breaks the cycle for recurrent "
         "cases, and that is decided after examining it."),
        ("Does nail surgery hurt?",
         "The local anaesthetic is given as a ring block at the base of the toe or finger, "
         "and that injection stings for a few seconds. After that the procedure is felt as "
         "pressure. There is soreness for a day or two afterwards."),
        ("Can I have a pedicure while being treated?",
         "Tell the clinic what you are having done. Aggressive cuticle work and shared "
         "instruments are a route to both infection and recurrent paronychia, and are worth "
         "avoiding while a nail is being treated."),
        ("Do nail changes mean something is wrong internally?",
         "Sometimes, and that is one reason a dermatologist looks at them. Nail changes "
         "accompany several skin conditions and occasionally point elsewhere, which is why "
         "sudden changes across several nails are worth examining rather than covering."),
    ],
    "related": [
        ("fungal-infection-treatment-hyderabad", "Fungal infections", "When the skin is involved too."),
        ("psoriasis-treatment-hyderabad", "Psoriasis", "Nail changes are common in psoriasis."),
        ("dermatosurgery-hyderabad", "Dermatosurgery", "The rest of the minor surgery list."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# TRICHOLOGY — PRP and microneedling induction
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "prp-hair-treatment-hyderabad", "template": "T1",
    "condition": "Androgenetic alopecia",
    "crumbs": [("PRP for hair", None)],
    "title": "PRP Hair Treatment in Hyderabad | Dr. Varada",
    "meta": "PRP and microneedling for hair loss in Hyderabad: what the evidence supports, why "
            "it is an adjunct rather than a treatment, and who it will not help.",
    "eyebrow": "Hyderabad",
    "h1": "PRP hair treatment in Hyderabad",
    "lede": "PRP concentrates the platelets from your own blood and returns them to the scalp. "
            "The evidence behind it is genuine but modest, and it works as an addition to a "
            "diagnosis and a medical plan. Not as a substitute for either.",
    "acts": [("Book an assessment", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "sources": ["pmc-prp-aga", "statpearls-aga", "dermnet-mphl", "dermnet-needling"],
    "glance": [
        ("Best suited to", "Pattern hair loss, early to moderate"),
        ("Role", "Adjunct to medical treatment, not a replacement"),
        ("Typical course", "Monthly sessions, then spaced maintenance"),
        ("Judged at", "Around 6 months, on photographs"),
        ("Not useful for", "Scarred, long-bald scalp"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What the evidence says",
         "h2": "Real, modest, and frequently oversold.",
         "body": [
             "A small amount of your blood is drawn, spun to separate the platelet-rich "
             "fraction, and injected into the affected areas of scalp. The rationale is that "
             "the growth factors platelets carry act on follicles that are miniaturising but "
             "still alive.",
             "Pooled analyses of randomised trials do show increases in hair density "
             "compared with placebo. They also show something worth knowing before you pay "
             "for a course: the studies vary widely in how the PRP was prepared, how often "
             "it was given and how the results were measured, and the overall quality of "
             "evidence is rated as limited. Anyone quoting you a precise percentage "
             "improvement is quoting one study, not the field.",
             "The honest position is that PRP is a reasonable addition for the right person "
             "and a poor first move for anybody. It does not tell you why your hair is "
             "falling, and if the reason is thyroid, iron deficiency or a scarring alopecia, "
             "injecting the scalp is treating the wrong thing at some expense.",
         ]},

        {"kind": "diagram", "eyebrow": "The cycle",
         "h2": "Every hair is somewhere in a cycle.",
         "intro": "A follicle grows for years, winds down over weeks, rests for months, then lets the old hair go and starts again. Only the growing ones respond to treatment, which is why nothing is judged before three months.",
         "caption": "At any moment most of your hair is growing and a smaller share is resting. Shedding is that balance shifting, not follicles disappearing.",
         "label_col": 0,
         "labels": [
             {"text": "Growing", "x": 14, "y": 85, "lead": 2},
             {"text": "Winding down", "x": 33, "y": 85, "lead": 2},
             {"text": "Resting", "x": 52, "y": 85, "lead": 2},
             {"text": "Shed, and starting again", "x": 71, "y": 85, "lead": 2},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/A4-hair-growth-cycle.webp", "w": 1820, "h": 1024,
             "alt": "Four blocks of skin in a row showing one follicle at four points in its cycle. In the first the bulb sits deep in the fat with a thick dark hair. In the second it has climbed to the edge of the fat. In the third it rests high in the dermis as a blunt club, above the papilla it left behind. In the fourth the old hair lifts away while a new dark bulb grows down again."}},

        {"kind": "steps", "eyebrow": "How a course runs",
         "h2": "Diagnosis first, then sessions.",
         "items": [
             {"title": "Establish the cause",
              "body": "Examination, and blood tests where indicated. Pattern loss, telogen "
                      "effluvium, deficiency and alopecia areata look similar to the person "
                      "losing the hair and are treated quite differently."},
             {"title": "Start the medical treatment",
              "body": "Where pattern loss is confirmed, proven medical therapy is the "
                      "backbone. PRP is added to it. A course of PRP with nothing else "
                      "running alongside is not how it is used here."},
             {"title": "An initial run of sessions",
              "body": "Usually monthly to begin with. Each session takes under an hour, "
                      "including the draw and the spin, and you go back to your day "
                      "afterwards."},
             {"title": "Judge on photographs at six months",
              "body": "Hair changes too slowly to assess in a mirror. Standardised "
                      "photographs from the first visit are what the decision to continue "
                      "or stop is made on."},
         ]},

        {"kind": "table", "eyebrow": "Who it suits", "h2": "Where PRP fits, and where it does not",
         "head": ["Situation", "Is PRP useful?", "Notes"],
         "rows": [
             ["Early to moderate pattern loss", "Reasonable adjunct",
              "Alongside medical treatment, not instead of it"],
             ["Diffuse shedding after illness or delivery", "Usually unnecessary",
              "Telogen effluvium recovers when the trigger resolves"],
             ["Deficiency-related hair fall", "Treat the deficiency",
              "Iron, thyroid and vitamin D come first"],
             ["Alopecia areata", "Sometimes considered",
              "Established treatments are tried first"],
             ["Long-standing bald, shiny scalp", "No",
              "Follicles that are gone cannot be stimulated"],
             ["Scarring alopecia", "No",
              "The disease must be controlled; needs a different plan"],
         ],
         "note": "The last two rows are the honest limit of the treatment. PRP acts on "
                 "follicles that still exist, where the scalp has been bald and smooth for "
                 "years, grafting is the conversation, not injections."},

        {"kind": "diagram", "eyebrow": "The preparation",
         "h2": "What is actually being injected.",
         "intro": "Your own blood is spun so the platelets separate from the rest of it. The thin fraction that carries them is what goes back into the scalp, at the depth the follicle bulbs sit.",
         "caption": "Nothing is added and nothing is manufactured — which is also why the effect is real but modest, and why it is a course rather than a single visit.",
         "label_col": 0,
         "labels": [
             {"text": "Blood drawn", "x": 10, "y": 85, "lead": 2},
             {"text": "Spun", "x": 29, "y": 85, "lead": 2},
             {"text": "Separated", "x": 48, "y": 85, "lead": 2},
             {"text": "Injected at bulb depth", "x": 72, "y": 85, "lead": 2},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D14-prp.webp", "w": 1820, "h": 1024,
             "alt": "Four stages in a row. A tube of blood is drawn, spun in a small centrifuge, and comes to rest separated into three layers with a thin platelet-rich band across the middle. A fine syringe then delivers that middle fraction into scalp skin, its needle stopping at the depth of the hair bulbs."}},

        {"kind": "split", "eyebrow": "Microneedling and derma roller",
         "h2": "The induction step, and what it is for.",
         "body": ["Controlled microneedling of the scalp is often combined with PRP or with "
                  "topical treatment. The needling itself provokes a wound-healing response, "
                  "and it improves how much of an applied topical actually reaches the "
                  "follicle, which is a large part of why it is used.",
                  "Done in clinic at a set depth on assessed scalp, it is a sensible adjunct. "
                  "Done at home with a roller bought online, over active infection or "
                  "inflamed skin, it is a way to spread a problem and occasionally to scar. "
                  "If you are already using one, bring it and say how."],
         "cta": ("If grafting is the real question", "hair-grafting-hyderabad"),
         "items": [
             {"title": "Depth is not a detail",
              "body": "The needle length that helps a topical penetrate and the length that "
                      "damages scalp are not far apart."},
             {"title": "Not over active disease",
              "body": "Needling inflamed, infected or actively shedding scalp is how a "
                      "manageable problem is made worse."},
         ]},

        VISIT,
    ],
    "faq_h2": "PRP questions",
    "faqs": [
        ("Does PRP actually work for hair loss?",
         "Pooled trial data show a genuine increase in hair density compared with placebo, "
         "but the studies differ so much in preparation and protocol that the overall "
         "quality of evidence is judged limited. It is a reasonable adjunct to proven "
         "medical treatment, and a poor substitute for it."),
        ("How many PRP sessions will I need?",
         "An initial run of monthly sessions, then spaced maintenance if it is helping. The "
         "decision to continue is made at around six months on standardised photographs, not on "
         "how it feels. Hair changes too slowly to judge in a mirror."),
        ("Is PRP safe?",
         "It uses your own blood, so the material itself carries no rejection risk. Expect "
         "scalp tenderness, some soreness and occasionally mild swelling for a day. It is "
         "done as a clinic procedure with sterile technique."),
        ("Can PRP regrow hair on a completely bald area?",
         "No. It acts on follicles that are miniaturising but still present. Scalp that has "
         "been bald and shiny for years has no follicles left to stimulate, and grafting is "
         "the relevant conversation instead."),
        ("Do I have to keep taking medication as well?",
         "For pattern hair loss, yes. That is the backbone of treatment and PRP is added to it. "
         "Stopping medical therapy and relying on injections alone generally means losing the "
         "ground gained."),
        ("Is a derma roller at home a good idea?",
         "Not without advice. Needle depth matters, and rolling over inflamed, infected or "
         "actively shedding scalp can make things worse and occasionally scar. If you "
         "already use one, bring it to the appointment."),
    ],
    "related": [
        ("hair-loss-treatment-hyderabad", "Hair loss treatment", "Start here: the cause decides "
                                                                 "the plan."),
        ("hair-grafting-hyderabad", "Hair grafting surgery", "When there is nothing left to stimulate."),
        ("alopecia-treatment-hyderabad", "Alopecia areata", "A different disease, treated differently."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# AESTHETIC DERMATOLOGY — dermal fillers
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "dermal-fillers-hyderabad", "template": "T1",
    "crumbs": [("Dermal fillers", None)],
    "title": "Dermal Fillers in Hyderabad | Dr. Varada",
    "meta": "Dermal fillers in Hyderabad including lip and tear trough: what filler restores, "
            "what it cannot fix, how long it lasts, and the vascular risk to know.",
    "eyebrow": "Hyderabad",
    "h1": "Dermal fillers in Hyderabad",
    "sources": ["dermnet-fillers", "dermnet-phototype"],
    "lede": "Filler replaces volume. Where a line or a hollow exists because tissue has been "
            "lost, it is the right tool and the result is immediate, and where the problem is "
            "texture, pigment or muscle movement, it is the wrong one and no amount will help.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "glance": [
        ("Treats", "Volume loss, hollows, lip shape and definition"),
        ("Does not treat", "Texture, pigmentation, movement lines"),
        ("Material", "Hyaluronic acid: dissolvable if needed"),
        ("Lasts", "Broadly 6–18 months, varying by site"),
        ("Injected by", "The dermatologist, not a therapist"),
        ("Reversal available", "Hyaluronidase kept on site"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "What it does",
         "h2": "It replaces volume. That is the whole mechanism.",
         "body": [
             "Faces age partly by losing fat and bone volume in specific places, and skin "
             "that once had support beneath it falls into folds. Hyaluronic acid filler puts "
             "volume back where it went, and the change is visible on the day rather than "
             "over months.",
             "Because the mechanism is that specific, so are the indications. A tear trough "
             "hollow, a flattened cheek, thin or asymmetric lips, a fold with genuine volume "
             "loss behind it: all reasonable. Dull skin, open pores, pigmentation, fine crêpey "
             "texture and lines that only appear when you move. None of them. Those are "
             "different problems, and filler injected for them produces a face that looks "
             "treated rather than rested.",
             "The material used here is hyaluronic acid, and one of its important properties "
             "is that it can be dissolved. If a result is not what you wanted, or something "
             "goes wrong, an enzyme can remove it. Permanent fillers offer no such exit and "
             "are not used.",
         ]},

        {"kind": "diagram", "eyebrow": "The anatomy",
         "h2": "Depth is the whole decision.",
         "intro": "Filler does one thing: it replaces volume. Where it is placed decides what it does — a fine line under the skin, a soft cushion in the fat, or a firm support on the bone. Arteries run up through those same layers.",
         "caption": "This is why who injects you matters more than which brand is used. The serious complications are vascular, and they are anatomy problems.",
         "rail": True,
"labels": [
    {"text": "Just under the skin", "x": 32, "y": 27, "find": "artwork"},
    {"text": "In the fat", "x": 23, "y": 55, "row": 1, "find": "artwork"},
    {"text": "On the bone", "x": 20, "y": 72, "row": 2, "find": "artwork"},
    {"text": "Arteries share those layers", "x": 72, "y": 45, "find": "artwork"},
],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D10-filler-anatomy.webp", "w": 1820, "h": 1024,
             "alt": "Two blocks of facial tissue at the same scale. The left block shows skin, fat, muscle and bone in section with three separate deposits of clear gel placed at three different depths, each lifting the surface above it by a different amount. The right block shows the same layers with the arteries drawn instead, branching upward through them."}},

        {"kind": "table", "eyebrow": "By area", "h2": "What each area realistically gives",
         "head": ["Area", "What it addresses", "Notes"],
         "rows": [
             ["Tear trough / under eye", "A true hollow casting a shadow",
              "High-risk area; not for pigmentation or eye bags"],
             ["Cheeks / midface", "Lost projection and support",
              "Often improves the folds below without treating them"],
             ["Lips", "Shape, definition, mild volume",
              "Conservative here; the aim is proportion, not size"],
             ["Nasolabial folds", "Depth from volume loss",
              "Better addressed by supporting the cheek above"],
             ["Chin and jawline", "Definition and projection",
              "Small volumes change the profile considerably"],
             ["Fine lines and texture", "Not a filler problem",
              "Peels, boosters or resurfacing instead"],
         ],
         "note": "The under-eye row is the one to read carefully. Dark circles from "
                 "pigmentation or from thin skin do not improve with filler, and filling a "
                 "shadow that is not caused by a hollow makes the area look puffy."},

        {"kind": "split", "eyebrow": "The risk that matters",
         "h2": "Rare, serious, and the reason who injects you matters.",
         "body": ["Filler placed into or compressing a blood vessel can obstruct the supply to "
                  "an area of skin, and in the worst reported cases to the eye. It is uncommon, "
                  "but the face has high-risk zones, and the under-eye, nose and glabella are "
                  "among them.",
                  "What reduces the risk is anatomical knowledge, conservative technique and "
                  "recognising the signs immediately. What manages it is having the reversal "
                  "enzyme on site and using it without delay, because the window in which "
                  "reversal helps is measured in hours. Any clinic offering filler should be "
                  "able to tell you both of these without hesitating."],
         "cta": ("If the concern is movement lines", "anti-aging-botox-hyderabad"),
         "items": [
             {"title": "Ask who is holding the needle",
              "body": "Filler is a medical procedure. In this clinic it is performed by the "
                      "dermatologist, not delegated."},
             {"title": "Reversal on site, not ordered in",
              "body": "Hyaluronidase is kept available. An enzyme that has to be sourced "
                      "the next morning is of no use."},
         ]},

        {"kind": "callout", "warn": True, "title": "Severe pain or blanching after filler",
         "body": "Pain out of proportion, skin that goes white or dusky, or any change in "
                 "vision after an injection is an emergency and not something to sleep on. "
                 "Contact the clinic immediately. The treatment for vascular obstruction works "
                 "best within hours."},

        VISIT,
    ],
    "faq_h2": "Dermal filler questions",
    "faqs": [
        ("How long do dermal fillers last?",
         "Broadly six to eighteen months depending on the area, the product and your own "
         "metabolism. Lips tend to be at the shorter end because the area moves constantly; "
         "structural areas like the chin last longer."),
        ("Are fillers reversible?",
         "Hyaluronic acid fillers are. An enzyme called hyaluronidase dissolves them, which is "
         "used both to correct a result and to manage complications. Permanent fillers cannot "
         "be reversed and are not used here."),
        ("Will filler get rid of my dark circles?",
         "Only if the shadow is caused by a genuine hollow. Dark circles from pigmentation, "
         "from thin skin showing the vessels beneath, or from eye bags will not improve, and "
         "filling them can make the area look puffy. This is assessed before booking."),
        ("Does it hurt?",
         "The area is numbed with topical anaesthetic and most fillers contain local "
         "anaesthetic themselves. You will feel pressure, and lips are the most sensitive "
         "area. Bruising and swelling for a few days is normal."),
        ("Will I look done?",
         "Not if the volume is conservative and placed where it was actually lost. The "
         "overfilled look comes from treating folds directly and from repeated top-ups before "
         "the previous treatment has settled. Both avoidable."),
        ("Can I have filler and toxin at the same time?",
         "Often yes, and they address different problems. Toxin for lines made by movement, "
         "filler for lost volume. Whether to do both at one appointment is decided on the day."),
    ],
    "related": [
        ("anti-aging-botox-hyderabad", "Botulinum toxin", "For lines caused by movement."),
        ("thread-lift-hyderabad", "Thread lift", "For mild laxity, with honest limits."),
        ("skin-boosters-hyderabad", "Skin boosters", "For quality and hydration, not volume."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# AESTHETIC DERMATOLOGY — thread lift
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "thread-lift-hyderabad", "template": "T1",
    "crumbs": [("Thread lift", None)],
    "title": "Thread Lift in Hyderabad | Dr. Varada",
    "meta": "Thread lift in Hyderabad: what PDO threads realistically achieve, how long it "
            "lasts, why the evidence is thinner than the marketing, and the honest limit.",
    "eyebrow": "Hyderabad",
    "h1": "Thread lift in Hyderabad",
    "lede": "Absorbable threads placed under the skin lift tissue slightly and provoke collagen "
            "around them as they dissolve. The effect is real and it is modest, and it is not a "
            "facelift, whatever the before-and-afters imply.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "sources": ["dermnet-fillers", "dermnet-needling"],
    "glance": [
        ("Treats", "Mild laxity, early jowling, brow position"),
        ("Realistic effect", "Subtle repositioning, not a lift"),
        ("Threads absorb in", "Roughly 4–6 months"),
        ("Effect reported for", "About 12–18 months, variably"),
        ("Downtime", "Days of swelling and tenderness"),
        ("Not for", "Significant sagging or excess skin"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The honest framing",
         "h2": "A modest reposition, and some collagen.",
         "body": [
             "The threads used are made of polydioxanone, the same absorbable material used "
             "in surgical sutures. Some are smooth and placed to stimulate; others carry "
             "barbs or cones that grip tissue and allow it to be repositioned slightly when "
             "the thread is anchored.",
             "Both effects are genuine. Both are also smaller than the marketing around them "
             "suggests. The threads themselves absorb within four to six months, and what "
             "persists afterwards is the collagen response, which is why reported duration sits "
             "in the range of twelve to eighteen months rather than the years a surgical lift "
             "gives.",
             "The literature is thinner than you would expect for how widely threads are "
             "sold. Most published work is small, short-term or uncontrolled, and one "
             "randomised comparison found that using more threads did not produce a better "
             "sustained result. That is not a reason to avoid the treatment. It is a reason "
             "to be sceptical of anyone describing a precise outcome in advance.",
         ]},

        {"kind": "table", "eyebrow": "Suitability", "h2": "Who gets something from this",
         "head": ["Situation", "Threads?", "Better answer"],
         "rows": [
             ["Early jowling, good skin quality", "Reasonable",
              "The group that is most often satisfied"],
             ["Mild brow descent", "Reasonable",
              "Small changes read well around the eyes"],
             ["Marked sagging, loose excess skin", "No",
              "A surgical lift; threads will disappoint"],
             ["Volume loss mistaken for sagging", "No",
              "Filler restores the support that was lost"],
             ["Poor skin quality and texture", "Not on its own",
              "Treat the skin first: boosters, peels, resurfacing"],
             ["Wanting a result that lasts years", "No",
              "That is a surgical conversation, honestly had"],
         ],
         "note": "Half the people who ask about threads have volume loss rather than "
                 "laxity. Pulling skin that has lost its support beneath it is the "
                 "commonest reason a thread lift disappoints."},

        {"kind": "split", "eyebrow": "What the days after look like",
         "h2": "Not a lunchtime procedure, despite the phrase.",
         "body": ["Expect swelling, tenderness and often some bruising for several days, and "
                  "a pulling sensation when you move your face that settles over a week or "
                  "two. Sleeping on your back and avoiding wide mouth movements is advised "
                  "for the first fortnight.",
                  "Occasional problems include visible or palpable thread ends, puckering of "
                  "the skin at an insertion point, and asymmetry. Most settle or are "
                  "correctable, and they are described before you book rather than after "
                  "they happen."],
         "cta": ("If the problem is lost volume", "dermal-fillers-hyderabad"),
         "items": [
             {"title": "Two weeks of behaving",
              "body": "No dental work, facials or vigorous massage while the threads settle "
                      "into position."},
             {"title": "Reasonable expectations, stated first",
              "body": "If what you want is a decade off, this is not the treatment and you "
                      "will be told so at the consultation."},
         ]},

        {"kind": "callout", "title": "The consultation may end with a recommendation not to",
         "body": "Threads suit a specific situation: mild laxity with reasonable skin quality, "
                 "in someone who wants a subtle change and understands the duration. Outside "
                 "that, the honest options are filler, skin treatment, or a surgical referral, "
                 "and saying so is the point of examining you first."},

        VISIT,
    ],
    "faq_h2": "Thread lift questions",
    "faqs": [
        ("How long does a thread lift last?",
         "The threads themselves absorb over roughly four to six months. The collagen response "
         "they provoke outlasts them, and reported effect sits broadly in the twelve to "
         "eighteen month range, with considerable variation between people."),
        ("Is a thread lift the same as a facelift?",
         "No, and the difference is large. A surgical facelift repositions deeper tissue and "
         "removes excess skin, with results lasting years. Threads produce a subtle "
         "repositioning in someone with mild laxity. Where sagging is significant, threads "
         "will disappoint."),
        ("Is there downtime?",
         "Yes: several days of swelling, tenderness and often bruising, with a pulling "
         "sensation that settles over a week or two. Calling it a lunchtime procedure "
         "understates it."),
        ("What can go wrong?",
         "Thread ends that become visible or palpable, puckering at an insertion point, "
         "asymmetry, and occasionally infection. Most are manageable or settle, and they are "
         "explained before you book."),
        ("Can threads be removed if I do not like the result?",
         "They are absorbable, so they dissolve on their own within months. A thread causing "
         "a specific problem, such as puckering or an exposed end, can usually be dealt with "
         "before then."),
        ("Are threads better than filler?",
         "They do different things. Threads reposition slightly; filler replaces lost "
         "volume. Most faces that look tired have lost volume rather than developed laxity, "
         "which is why the examination decides this and not the enquiry."),
    ],
    "related": [
        ("dermal-fillers-hyderabad", "Dermal fillers", "For volume loss, which is more often the issue."),
        ("rf-skin-tightening-hyderabad", "RF skin tightening", "The other non-surgical tightening option."),
        ("anti-aging-botox-hyderabad", "Botulinum toxin", "For lines caused by movement."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# AESTHETIC DERMATOLOGY — mesotherapy
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "mesotherapy-hyderabad", "template": "T1",
    "crumbs": [("Mesotherapy", None)],
    "title": "Mesotherapy in Hyderabad | Dr. Varada",
    "meta": "Mesotherapy in Hyderabad for skin and hair: what is actually injected, how it "
            "differs from a skin booster, and which claims are worth distrusting.",
    "eyebrow": "Hyderabad",
    "h1": "Mesotherapy in Hyderabad",
    "sources": ["dermnet-mesotherapy", "dermnet-fillers"],
    "lede": "Mesotherapy means delivering small amounts of a substance into the superficial "
            "skin or scalp through many tiny injections. It is a delivery method rather than a "
            "treatment, so the only useful question is what is being delivered, and what "
            "evidence supports it.",
    "acts": [("Book a consultation", WHATSAPP), ("See the clinic", "locations-secunderabad")],
    "creds": CRED,
    "glance": [
        ("Used for", "Skin hydration and quality; scalp support"),
        ("Commonly delivers", "Hyaluronic acid, vitamins, amino acids"),
        ("Course", "Sessions spaced weeks apart, then maintenance"),
        ("Evidence", "Varies sharply by what is injected"),
        ("Not used for", "Fat dissolving or weight loss"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "The distinction worth making",
         "h2": "A technique, sold as though it were a product.",
         "body": [
             "Mesotherapy describes how something is administered, many superficial injections "
             "across an area, not what is administered. Two clinics offering “mesotherapy” may "
             "be injecting completely different things, with completely different evidence "
             "behind them and completely different results.",
             "That is why the useful conversation is about contents. Hyaluronic acid "
             "mesotherapy for skin hydration and quality has a reasonable rationale and "
             "overlaps with what is sold as a skin booster. Cocktails of vitamins, amino "
             "acids and plant extracts vary from plausible to entirely unstudied, and the "
             "further a formulation gets from something with published data, the less anyone "
             "can tell you about what to expect.",
             "So this page will not promise you a result. It will tell you what is used here, "
             "why, and where the evidence stops, which is more than most pages on the subject "
             "do.",
         ]},

        {"kind": "diagram", "eyebrow": "What the needles do",
         "h2": "Depth is the whole technique.",
         "intro": "Fine needles make controlled channels to a set depth in the upper dermis. The channels themselves close within hours; what matters is the repair response they provoke in the tissue at their tips.",
         "caption": "Depth is set for the area being treated and is not a dial to turn up. Going deeper does not accelerate anything — it risks the structures below and, on brown skin, risks pigmentation that outlasts the benefit.",
         "labels": [
             {"text": "Needles of one length", "x": 28, "y": 8, "lead": 26, "find": "artwork"},
             {"text": "Channels through the epidermis", "x": 31, "y": 40, "lead": 23, "find": "artwork"},
             {"text": "Every tip stops at one depth", "x": 30, "y": 54, "lead": 24, "find": "artwork"},
             {"text": "The fat is never reached", "x": 25, "y": 82, "lead": 29, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/D13-microneedling-depth.webp", "w": 1820, "h": 1024,
             "alt": "A block of brown skin in section with a flat head carrying a row of fine short needles above it. Several needles have entered the skin, each passing through the epidermis and stopping at the same depth in the upper dermis with their tips level along an even line, leaving narrow straight channels behind them. The fat layer below is clearly untouched. Small round repair cells and fine new collagen fibres gather around and below the tips."}},

        {"kind": "steps", "eyebrow": "What a session involves",
         "h2": "Short, repeated, and unremarkable.",
         "items": [
             {"title": "Assessment first",
              "body": "For skin, what the actual complaint is: dehydration and quality respond, "
                      "pigmentation and texture usually need something else. For scalp, the "
                      "cause of the hair loss, before anything is injected."},
             {"title": "Topical anaesthetic, then the session",
              "body": "Numbing cream beforehand. The injections themselves are superficial "
                      "and quick; a face or a scalp takes a matter of minutes."},
             {"title": "A course, spaced",
              "body": "Sessions weeks apart rather than a single treatment, with the number "
                      "decided by response rather than sold up front."},
             {"title": "Reassess before continuing",
              "body": "If nothing has changed after an initial course, the answer is to stop "
                      "and reconsider. Not to book more of the same."},
         ]},

        {"kind": "table", "eyebrow": "By indication", "h2": "What it is reasonable to expect",
         "head": ["Use", "Realistic expectation", "Notes"],
         "rows": [
             ["Skin hydration and quality", "Modest improvement in glow and suppleness",
              "Overlaps with skin boosters; the same conversation"],
             ["Scalp support alongside hair treatment", "Adjunct at best",
              "The diagnosis and medical treatment do the work"],
             ["Fine crêpey texture", "Modest",
              "Combined approaches do better than either alone"],
             ["Pigmentation and melasma", "Not the right tool",
              "Peels and a proper topical plan instead"],
             ["Deep lines and volume loss", "No",
              "Filler replaces volume; this does not"],
             ["Fat dissolving, body contouring", "Not offered",
              "Claims in this area outrun the evidence badly"],
         ],
         "note": "The last row is deliberate. Injection lipolysis is widely marketed in "
                 "India and the evidence for the formulations commonly used does not "
                 "support the claims made for them."},

        {"kind": "split", "eyebrow": "Before you book anywhere",
         "h2": "Three questions worth asking.",
         "body": ["What exactly is being injected, and is it a licensed product for this use? "
                  "Who is injecting it? And what happens if there is no change. Is there a "
                  "point at which the course stops, or does it simply continue?",
                  "These are unglamorous questions and they filter out most of what goes "
                  "wrong with mesotherapy. Injecting unlicensed cocktails into skin causes "
                  "the granulomas and prolonged inflammation that occasionally appear in the "
                  "literature, and those are far harder to treat than the concern that "
                  "prompted the treatment."],
         "cta": ("The better-defined alternative", "skin-boosters-hyderabad"),
         "items": [
             {"title": "Contents over branding",
              "body": "A named, licensed product with published data beats a proprietary "
                      "cocktail with a memorable name."},
             {"title": "A defined end point",
              "body": "Every course here has a review at which it either continues for a "
                      "reason or stops."},
         ]},

        VISIT,
    ],
    "faq_h2": "Mesotherapy questions",
    "faqs": [
        ("Is mesotherapy the same as skin boosters?",
         "They overlap. Skin boosters are usually a specific licensed hyaluronic acid product "
         "injected for hydration and quality. Mesotherapy is the broader technique and may "
         "deliver anything from that same hyaluronic acid to an unstudied cocktail, which is "
         "why the contents matter more than the label."),
        ("How many sessions will I need?",
         "A course spaced across weeks rather than one treatment, with the number set by "
         "response. There is a review point at which the course either continues for a "
         "stated reason or stops."),
        ("Does mesotherapy work for hair loss?",
         "As an adjunct at most. What determines the outcome in hair loss is identifying the "
         "cause and treating it properly. Scalp injections added to that are reasonable; "
         "scalp injections instead of it are not."),
        ("Can mesotherapy dissolve fat?",
         "Injection lipolysis is widely marketed and the evidence for the formulations "
         "commonly used does not support the claims made. It is not offered here."),
        ("Does it hurt?",
         "Numbing cream is applied first and the injections are superficial. Most people "
         "describe it as tolerable rather than comfortable. Expect small bumps and some "
         "redness for a few hours afterwards."),
        ("Is it safe?",
         "The technique is, when what is injected is a licensed product delivered by a "
         "clinician. The reported problems (persistent lumps, granulomas, prolonged "
         "inflammation), come overwhelmingly from unlicensed cocktails, which is why the first "
         "question to ask any clinic is what is in the syringe."),
    ],
    "related": [
        ("skin-boosters-hyderabad", "Skin boosters", "The better-defined version of the same idea."),
        ("chemical-peels-hyderabad", "Chemical peels", "For pigmentation and texture."),
        ("prp-hair-treatment-hyderabad", "PRP for hair", "The scalp conversation, properly framed."),
    ],
},

# ══════════════════════════════════════════════════════════════════════════════
# LASER SERVICES — acne scars
# ══════════════════════════════════════════════════════════════════════════════
{
    "slug": "acne-scar-treatment-hyderabad", "template": "T1",
    "condition": "Acne scarring",
    "crumbs": [("Acne scar treatment", None)],
    "title": "Acne Scar Treatment in Hyderabad | Dr. Varada",
    "meta": "Acne scar treatment in Hyderabad: subcision, TCA CROSS, microneedling RF and "
            "fractional laser, matched to your scar type and to Indian skin.",
    "eyebrow": "Hyderabad",
    "h1": "Acne scar treatment in Hyderabad",
    "sources": ["dermnet-acne-scarring", "dermnet-needling", "dermnet-peels", "dermnet-phototype"],
    "lede": "There is no single treatment for acne scars, because there is no single kind of "
            "acne scar. Tethered rolling scars, sharp ice-pick pits and brown marks each need a "
            "different procedure, and the brown marks, which most people call scars, are not "
            "scars at all.",
    "acts": [("Book an assessment", WHATSAPP), ("Call the clinic", PHONE)],
    "creds": CRED,
    "glance": [
        ("Treats", "Rolling, boxcar and ice-pick scarring"),
        ("First, always", "Active acne controlled medically"),
        ("Usual approach", "Combination, staged across months"),
        ("Indian skin", "Device and depth chosen for pigment risk"),
        ("Realistic result", "Substantial improvement, not flat skin"),
        ("Where", "Secunderabad clinic"),
    ],
    "sections": [
        {"kind": "prose", "eyebrow": "First, the distinction",
         "h2": "Most people asking about scars have marks.",
         "body": [
             "Flat brown or red patches left where a spot used to be are post-inflammatory "
             "pigmentation and erythema. They are not scars, they fade (slowly, over months to "
             "a couple of years), and they respond to topical treatment, peels and, above all, "
             "sun protection. Nobody needs a laser for them.",
             "A true scar is a change in the contour of the skin. Run a finger over it and "
             "there is a dip. Those do not fade, and they are what procedural treatment is "
             "for. The distinction is made by examining the skin in raking light, which is "
             "also how you find the shallow scarring people have not noticed.",
             "The other rule is absolute and gets ignored constantly: active acne is "
             "controlled before scars are treated. Resurfacing skin that is still breaking "
             "out produces fresh scars alongside the ones being treated, and any course "
             "started under those conditions is being sold rather than planned.",
         ]},

        {"kind": "diagram", "eyebrow": "The distinction",
         "h2": "A mark is not a scar.",
         "intro": "Most people who ask about acne scars have marks: flat brown patches left where a spot healed. A scar is a change in the skin's shape. The two need completely different treatment, and only one of them fades on its own.",
         "caption": "Marks fade with time, sun protection and pigment-directed treatment. Scars do not — they need the collagen rebuilt. Telling them apart is most of the first consultation.",
         "rail": True,
"labels": [
    {"text": "Extra pigment, surface still level", "x": 23, "y": 40, "find": "artwork"},
    {"text": "Collagen lost, surface dented", "x": 64, "y": 30, "find": "artwork"},
],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/B11-mark-vs-scar.webp", "w": 1820, "h": 1024,
             "alt": "Two blocks of skin side by side. In the left block the surface is completely smooth and level, and the only abnormality is a dense band of dark brown pigment sitting in the lower epidermis. In the right block the pigment is normal but the surface dips into a saucer-shaped depression because the collagen beneath it has been lost."}},

        {"kind": "table", "eyebrow": "Matching procedure to scar",
         "h2": "Different scars, different tools",
         "head": ["Scar type", "What it responds to", "Notes"],
         "rows": [
             ["Rolling: broad, tethered dips", "Subcision, releasing the tether",
              "Little else works until the tether is cut"],
             ["Boxcar: sharp-edged, wide", "Microneedling RF or fractional resurfacing",
              "Depth of the edge decides which"],
             ["Ice-pick: narrow, deep pits", "TCA CROSS, applied point by point",
              "Resurfacing passes over these without touching them"],
             ["Shallow, diffuse irregularity", "Microneedling, peels",
              "Often the most improvable group"],
             ["Brown marks with no dip", "Topicals, peels, sunscreen",
              "Not a scar; do not laser it"],
             ["Raised or keloid scarring", "Injection-based treatment",
              "The opposite problem: see keloid treatment"],
         ],
         "note": "Most faces carry more than one type, which is why single-modality courses "
                 "underperform. A plan usually combines two or three procedures in a "
                 "deliberate order."},

        {"kind": "diagram", "eyebrow": "The shapes",
         "h2": "Three scars, three different problems.",
         "intro": "Scars are classified by shape because shape decides the tool. A narrow deep tract, a sharp-walled crater and a broad tethered dip do not respond to the same treatment, and most faces carry more than one kind.",
         "caption": "This is why a single device rarely clears a face, and why a plan usually combines methods in a deliberate order.",
         "labels": [
             {"text": "Narrow and deep", "x": 16, "y": 42, "lead": 49, "find": "artwork"},
             {"text": "Sharp-walled crater", "x": 36, "y": 27, "lead": 29, "find": "artwork"},
             {"text": "Tethered from below", "x": 51, "y": 55, "lead": 14, "find": "artwork"},
         ],
         "body": "[ diagram ]",
         "image": {
             "src": "img/diagrams/B12-acne-scar-types.webp", "w": 1820, "h": 1024,
             "alt": "One block of skin containing three different scars. The first is a very narrow tract plunging steeply and deeply into the dermis. The second is a wider crater with a flat floor and sharp vertical walls. The third is a broad shallow undulation with fibrous strands beneath tethering the surface down to deeper tissue."}},

        {"kind": "steps", "eyebrow": "How a plan is built",
         "h2": "Order matters more than intensity.",
         "items": [
             {"title": "Control the acne first",
              "body": "Non-negotiable. Treating scars while lesions are still appearing "
                      "creates new ones. Where oral retinoid treatment is involved, timing "
                      "of procedures is planned around it."},
             {"title": "Release what is tethered",
              "body": "Rolling scars are held down from beneath. Subcision frees them, and it "
                      "is done before resurfacing rather than after, resurfacing a tethered "
                      "scar smooths a dip that is still being pulled."},
             {"title": "Treat the pits individually",
              "body": "Ice-pick scars are addressed point by point with focal TCA rather "
                      "than by a resurfacing pass, which cannot reach the base of a narrow "
                      "deep scar."},
             {"title": "Resurface, then wait",
              "body": "Remodelling continues for months after a session. Sessions are "
                      "spaced accordingly and the result is judged late, not at two weeks."},
         ]},

        {"kind": "split", "eyebrow": "Indian skin",
         "h2": "The device is chosen for your pigment, not for its brochure.",
         "body": ["Skin that pigments readily responds to thermal injury by darkening, and "
                  "ablative fractional resurfacing carries a meaningfully higher risk of "
                  "post-inflammatory pigmentation in darker skin than the alternatives. That is "
                  "not a reason to rule it out. It is a reason for the choice to be deliberate.",
                  "Subcision, microneedling and focal TCA involve little or no thermal "
                  "damage, which is much of why they carry a lower pigmentation risk and why "
                  "combination approaches built around them suit Indian skin well. Where "
                  "resurfacing is used, settings are conservative, the course is longer, and "
                  "sun protection is treated as part of the treatment rather than advice."],
         "cta": ("If the acne is still active", "acne-treatment-hyderabad"),
         "items": [
             {"title": "Longer course, lower risk",
              "body": "More sessions at conservative settings usually beats fewer aggressive "
                      "ones on skin that pigments."},
             {"title": "Sunscreen decides the outcome",
              "body": "Daily, throughout the course and for weeks after each session. It is "
                      "the step that separates a good result from a brown one."},
         ]},

        VISIT,
    ],
    "faq_h2": "Acne scar questions",
    "faqs": [
        ("Can acne scars be removed completely?",
         "Substantial improvement is realistic; flat, unmarked skin generally is not. A "
         "well-planned combination course typically produces a face where the scarring is no "
         "longer the first thing you see, which is a different promise from erasure, and the "
         "honest one."),
        ("How many sessions will I need?",
         "It depends on the scar types present and how deep they are. Combination plans "
         "usually run across several months with sessions spaced by weeks, because "
         "remodelling continues long after each one. The number is reviewed against "
         "photographs rather than fixed in advance."),
        ("Are lasers safe for Indian skin?",
         "Used appropriately, yes, but the choice matters. Ablative fractional resurfacing "
         "carries a higher risk of post-inflammatory pigmentation in darker skin than "
         "microneedling RF, subcision or focal TCA. The device and the settings are chosen for "
         "your skin, and conservative courses are preferred."),
        ("My marks are brown, not indented. What do I need?",
         "Probably not a procedure. Flat brown marks are post-inflammatory pigmentation, "
         "which fades over months and responds to topical treatment, peels and rigorous sun "
         "protection. Save the procedural treatment for scars with a contour change."),
        ("Do I have to finish acne treatment first?",
         "Yes. Treating scars while acne is still active produces new scars alongside the old "
         "ones. If you are on or recently finished oral retinoid treatment, tell the clinic. It "
         "changes when procedures can be done."),
        ("What does acne scar treatment cost?",
         "It is quoted after assessment, because the plan depends on which scar types you "
         "have and how many sessions each needs. A per-session price without a plan behind "
         "it is not a comparison worth making."),
    ],
    "related": [
        ("acne-treatment-hyderabad", "Acne treatment", "Control the acne before treating scars."),
        ("chemical-peels-hyderabad", "Chemical peels", "For the brown marks rather than the dips."),
        ("keloid-treatment-hyderabad", "Keloid treatment", "For raised rather than indented scars."),
    ],
},

]
