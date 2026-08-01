"""The reference library — every external source the site is allowed to cite.

Why this exists
---------------
The site had 96,000 words of clinical copy and cited nothing. For ordinary
content that is a stylistic choice; for YMYL medical content it is the single
largest authority gap available, and it costs on two fronts at once:

  * Google's quality guidance for health content treats verifiable sourcing as
    a first-order signal, and a page whose claims trace to NIH, the AAD, NICE
    or IADVL is a different object from one that asserts them unbacked.
  * An answer engine deciding whether to quote a page has almost nothing else
    to go on. Citations are what make a page quotable rather than merely
    readable, and quotability is how a clinic becomes the source an LLM names.

Rules this file enforces
------------------------
1. **Every URL here has been fetched and returned 200.** Not inferred from a
   slug pattern, not remembered — fetched. Guessing cost me a StatPearls ID
   that turned out to be *Corneal Trauma*, and an archived keloid chapter,
   both of which read entirely plausible as strings.
2. **Publisher over convenience.** A guideline body, a national health service
   or a peer-reviewed review — never a competing clinic, never a content farm,
   never anything selling the treatment on the page that cites it.
3. **Indian sources where Indian practice differs.** IADVL's vitiligo surgery
   consensus and the T. indotineae literature are not decoration: stability
   criteria and terbinafine resistance are exactly the places where a Western
   guideline would mislead a patient reading this in Hyderabad.

`build.py` re-checks that every id referenced by a page exists here, so a typo
in a page's `sources` list is a build failure rather than a silently missing
citation.
"""

from __future__ import annotations

# id -> (title, publisher, url)
SOURCES: dict[str, tuple[str, str, str]] = {
    # ── vitiligo ─────────────────────────────────────────────────────────────
    "niams-vitiligo": (
        "Vitiligo: overview, causes and treatment",
        "US National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIH)",
        "https://www.niams.nih.gov/health-topics/vitiligo"),
    "aad-vitiligo": (
        "Vitiligo: overview and diagnosis",
        "American Academy of Dermatology",
        "https://www.aad.org/public/diseases/a-z/vitiligo-overview"),
    "aad-vitiligo-tx": (
        "Vitiligo: diagnosis and treatment",
        "American Academy of Dermatology",
        "https://www.aad.org/public/diseases/a-z/vitiligo-treatment"),
    "dermnet-vitiligo": (
        "Vitiligo",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/vitiligo"),
    "nhs-vitiligo": (
        "Vitiligo",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/vitiligo/"),
    "iadvl-vitiligo-surgery": (
        "Consensus-based guidelines for surgical management of vitiligo, "
        "Vitiligo Task Force, IADVL Academy 2024–2025",
        "Indian Journal of Dermatology, Venereology and Leprology",
        "https://ijdvl.com/consensus-based-guidelines-for-surgical-management-of-"
        "vitiligo-by-vitiligo-task-force-iadvl-academy-2024-2025/"),
    "iadvl-vitiligo-surgery-std": (
        "Standard guidelines of care for vitiligo surgery, "
        "IADVL Dermatosurgery Task Force",
        "Indian Journal of Dermatology, Venereology and Leprology",
        "https://ijdvl.com/standard-guidelines-of-care-for-vitiligo-surgery/"),
    "gvf": (
        "Vitiligo: patient resources and research updates",
        "Global Vitiligo Foundation",
        "https://globalvitiligofoundation.org/"),

    # ── psoriasis ────────────────────────────────────────────────────────────
    "niams-psoriasis": (
        "Psoriasis: overview, symptoms and treatment",
        "US National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIH)",
        "https://www.niams.nih.gov/health-topics/psoriasis"),
    "aad-psoriasis": (
        "Psoriasis resource centre",
        "American Academy of Dermatology",
        "https://www.aad.org/public/diseases/psoriasis"),
    "dermnet-psoriasis": (
        "Psoriasis",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/psoriasis"),
    "nhs-psoriasis": (
        "Psoriasis",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/psoriasis/"),
    "nice-psoriasis": (
        "Psoriasis: assessment and management (CG153)",
        "National Institute for Health and Care Excellence (UK)",
        "https://www.nice.org.uk/guidance/cg153"),
    "who-psoriasis": (
        "Global report on psoriasis",
        "World Health Organization",
        "https://www.who.int/publications/i/item/9789241565189"),
    "npf": (
        "About psoriasis",
        "National Psoriasis Foundation",
        "https://www.psoriasis.org/about-psoriasis/"),
    "dermnet-scalp-psoriasis": (
        "Scalp psoriasis",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/scalp-psoriasis"),
    "dermnet-psa": (
        "Psoriatic arthritis",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/psoriatic-arthritis"),
    "dermnet-nail-psoriasis": (
        "Nail psoriasis",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/nail-psoriasis"),
    "dermnet-phototherapy": (
        "Phototherapy",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/phototherapy"),
    "dermnet-methotrexate": (
        "Methotrexate",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/methotrexate"),
    "dermnet-biologics": (
        "Biologics",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/biologics"),

    # ── hair ─────────────────────────────────────────────────────────────────
    "niams-alopecia-areata": (
        "Alopecia areata",
        "US National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIH)",
        "https://www.niams.nih.gov/health-topics/alopecia-areata"),
    "dermnet-alopecia-areata": (
        "Alopecia areata",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/alopecia-areata"),
    "aad-hair-loss": (
        "Hair loss: causes, diagnosis and treatment",
        "American Academy of Dermatology",
        "https://www.aad.org/public/diseases/hair-loss"),
    "nhs-hair-loss": (
        "Hair loss",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/symptoms/hair-loss/"),
    "dermnet-mphl": (
        "Male pattern hair loss",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/male-pattern-hair-loss"),
    "dermnet-fphl": (
        "Female pattern hair loss",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/female-pattern-hair-loss"),
    "dermnet-telogen-effluvium": (
        "Telogen effluvium",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/telogen-effluvium"),
    "statpearls-aga": (
        "Androgenetic alopecia",
        "StatPearls, US National Library of Medicine",
        "https://www.ncbi.nlm.nih.gov/books/NBK430924/"),
    "pmc-prp-aga": (
        "Platelet-rich plasma therapy for androgenetic alopecia",
        "PubMed Central, US National Library of Medicine",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC6749759/"),
    "dermnet-seb-derm": (
        "Seborrhoeic dermatitis",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/seborrhoeic-dermatitis"),
    "nhs-dandruff": (
        "Dandruff",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/dandruff/"),

    # ── skin ─────────────────────────────────────────────────────────────────
    "niams-eczema": (
        "Atopic dermatitis",
        "US National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIH)",
        "https://www.niams.nih.gov/health-topics/atopic-dermatitis"),
    "dermnet-eczema": (
        "Atopic dermatitis",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/atopic-dermatitis"),
    "nhs-eczema": (
        "Atopic eczema",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/atopic-eczema/"),
    "niams-acne": (
        "Acne",
        "US National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIH)",
        "https://www.niams.nih.gov/health-topics/acne"),
    "dermnet-acne": (
        "Acne vulgaris",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/acne-vulgaris"),
    "dermnet-acne-scarring": (
        "Acne scarring",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/acne-scarring"),
    "nhs-acne": (
        "Acne",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/acne/"),
    "dermnet-tinea": (
        "Tinea corporis (ringworm)",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/tinea-corporis"),
    "nhs-ringworm": (
        "Ringworm",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/ringworm/"),
    "pmc-terbinafine-resistance": (
        "Terbinafine resistance in Trichophyton rubrum and Trichophyton "
        "indotineae: a literature review",
        "PubMed Central, US National Library of Medicine",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC12108360/"),
    "pmc-indotineae-outcomes": (
        "Therapeutic outcomes in patients with Trichophyton indotineae: a "
        "systematic review and meta-analysis of individual patient data",
        "PubMed Central, US National Library of Medicine",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC11971648/"),
    "dermnet-fungal-nails": (
        "Fungal nail infections",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/fungal-nail-infections"),
    "nhs-fungal-nail": (
        "Fungal nail infection",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/fungal-nail-infection/"),
    "dermnet-nail-disorders": (
        "Nail disorders",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/nail-disorders"),
    "dermnet-ingrown-toenail": (
        "Ingrown toenail",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/ingrown-toenail"),
    "dermnet-keloid": (
        "Keloid and hypertrophic scar",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/keloid-and-hypertrophic-scar"),
    "nhs-keloid": (
        "Keloid scars",
        "NHS (United Kingdom)",
        "https://www.nhs.uk/conditions/keloid-scars/"),
    "dermnet-urticaria": (
        "Urticaria: an overview",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/urticaria-an-overview"),
    "dermnet-contact-dermatitis": (
        "Contact dermatitis",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/contact-dermatitis"),
    "dermnet-melasma": (
        "Melasma",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/melasma"),

    # ── procedures ───────────────────────────────────────────────────────────
    "dermnet-peels": (
        "Chemical peels",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/chemical-peels"),
    "dermnet-fillers": (
        "Fillers",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/fillers"),
    "dermnet-botulinum": (
        "Botulinum toxin",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/botulinum-toxin"),
    "dermnet-needling": (
        "Skin needling",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/skin-needling"),
    "dermnet-mesotherapy": (
        "Mesotherapy",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/mesotherapy"),
    # Fitzpatrick type is the reason half the aesthetic copy on this site reads
    # differently from an American clinic's: the risk arithmetic for peels,
    # lasers and energy devices changes with skin phototype.
    "dermnet-phototype": (
        "Skin phototype",
        "DermNet (New Zealand Dermatological Society)",
        "https://dermnetnz.org/topics/skin-phototype"),

    # ── regulatory ───────────────────────────────────────────────────────────
    "nmc": (
        "National Medical Commission, India",
        "National Medical Commission",
        "https://www.nmc.org.in/"),
}


def unknown(ids) -> list[str]:
    """Ids referenced by a page that this library does not define."""
    return [i for i in ids if i not in SOURCES]
