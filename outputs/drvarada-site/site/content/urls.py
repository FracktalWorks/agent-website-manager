"""slug → production URL.

The build writes flat files (`vitiligo-graft-surgery.html`) so the Open Design preview
and any static host resolve links without a server. This map is the bridge to the real
IA: canonical tags, breadcrumbs and every schema `@id` use these paths, and
`build.py --links=production` rewrites internal hrefs to them for the WordPress deploy.

Paths come straight from MASTER_PLAN §4 and the keyword map. One page owns one query
cluster — if you are tempted to add a second URL for a term already listed here, merge
instead.
"""

URLS = {
    # ── T3 · brand and utility ───────────────────────────────────────────────
    "index": "/",
    "about-dr-khagendra-varada": "/about/dr-khagendra-varada/",
    # One consulting location, in Karkhana, Secunderabad. The path names the
    # city rather than the colony because that is the query people type —
    # "dermatologist in Secunderabad", not "dermatologist in Vikrampuri Colony".
    "locations-secunderabad": "/locations/secunderabad/",
    "areas-we-serve": "/areas-we-serve/",
    "contact": "/contact/",
    "results": "/results/",
    "patient-stories": "/patient-stories/",
    "blog": "/blog/",

    # ── pan-India, condition-independent ─────────────────────────────────────
    # The tier that reaches patients outside Telangana without minting a page
    # per city. See content/national.py for why a city grid is the wrong answer.
    "online-consultation": "/online-consultation/",
    "alopecia-areata-treatment-india": "/alopecia-areata-treatment-india/",
    "travelling-for-treatment": "/travelling-for-treatment/",

    # ── T2 · pan-India vitiligo hub and cluster ──────────────────────────────
    "vitiligo": "/vitiligo/",
    "vitiligo-types-and-stages": "/vitiligo/types-and-stages/",
    "vitiligo-excimer-laser": "/vitiligo/excimer-laser/",
    "vitiligo-phototherapy": "/vitiligo/phototherapy/",
    "vitiligo-graft-surgery": "/vitiligo/graft-surgery/",
    "vitiligo-children": "/vitiligo/children/",
    "vitiligo-diet-and-myths": "/vitiligo/diet-and-myths/",
    "vitiligo-cost": "/vitiligo/cost/",
    "vitiligo-online-consultation": "/vitiligo/online-consultation/",

    # ── T2 · pan-India psoriasis hub and cluster ─────────────────────────────
    "psoriasis": "/psoriasis/",
    "psoriasis-types": "/psoriasis/types/",
    "psoriasis-scalp": "/psoriasis/scalp/",
    "psoriasis-triggers-and-diet": "/psoriasis/triggers-and-diet/",
    "psoriasis-phototherapy": "/psoriasis/phototherapy/",
    "psoriasis-biologics": "/psoriasis/biologics/",
    "psoriasis-cost": "/psoriasis/cost/",
    "psoriasis-online-consultation": "/psoriasis/online-consultation/",

    # ── T1 · Hyderabad service pillars ───────────────────────────────────────
    "vitiligo-treatment-hyderabad": "/vitiligo-treatment-hyderabad/",
    "psoriasis-treatment-hyderabad": "/psoriasis-treatment-hyderabad/",
    "hair-loss-treatment-hyderabad": "/hair-loss-treatment-hyderabad/",
    "alopecia-treatment-hyderabad": "/alopecia-treatment-hyderabad/",
    "hair-grafting-hyderabad": "/hair-grafting-hyderabad/",
    "acne-treatment-hyderabad": "/acne-treatment-hyderabad/",
    "skin-allergy-rashes-treatment": "/skin-allergy-rashes-treatment/",
    "eczema-atopic-dermatitis-treatment": "/eczema-atopic-dermatitis-treatment/",
    "anti-aging-botox-hyderabad": "/anti-aging-botox-hyderabad/",
    "skin-boosters-hyderabad": "/skin-boosters-hyderabad/",
    "rf-skin-tightening-hyderabad": "/rf-skin-tightening-hyderabad/",
    "chemical-peels-hyderabad": "/chemical-peels-hyderabad/",
    "laser-hair-reduction-hyderabad": "/laser-hair-reduction-hyderabad/",
    "dermatosurgery-hyderabad": "/dermatosurgery-hyderabad/",
    "dandruff-treatment": "/dandruff-treatment/",

    # ── the procedure catalogue ──────────────────────────────────────────────
    # Added from the clinic's printed services card (see content/treatments.py).
    # `/treatments/` is the index a patient holding that card expects to find;
    # the rest are the ten procedures on it that had demand and no page.
    "treatments": "/treatments/",
    "fungal-infection-treatment-hyderabad": "/fungal-infection-treatment-hyderabad/",
    "keloid-treatment-hyderabad": "/keloid-treatment-hyderabad/",
    "ear-lobe-repair-hyderabad": "/ear-lobe-repair-hyderabad/",
    "nail-treatment-hyderabad": "/nail-treatment-hyderabad/",
    "prp-hair-treatment-hyderabad": "/prp-hair-treatment-hyderabad/",
    "dermal-fillers-hyderabad": "/dermal-fillers-hyderabad/",
    "thread-lift-hyderabad": "/thread-lift-hyderabad/",
    "mesotherapy-hyderabad": "/mesotherapy-hyderabad/",
    "acne-scar-treatment-hyderabad": "/acne-scar-treatment-hyderabad/",

    # ── Secunderabad · the twin city the clinic is physically in ─────────────
    # Distinct intent, not a city-swapped clone: these pages are about distance
    # and adherence, which is what decides a months-long course of light.
    "vitiligo-treatment-secunderabad": "/vitiligo-treatment-secunderabad/",
    "psoriasis-treatment-secunderabad": "/psoriasis-treatment-secunderabad/",
    "hair-loss-treatment-secunderabad": "/hair-loss-treatment-secunderabad/",
    "premature-greying-treatment": "/premature-greying-treatment/",

    # ── language layers: Telugu (phase 2), Hindi (phase 3) ───────────────────
    "te-vitiligo": "/te/vitiligo/",
    "te-psoriasis": "/te/psoriasis/",
    "hi-vitiligo": "/hi/vitiligo/",
    "hi-psoriasis": "/hi/psoriasis/",
}
