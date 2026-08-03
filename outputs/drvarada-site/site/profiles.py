"""Emit the off-site profile sheet — Google Business Profile, Bing Places and
the directory citations — from the site's own constants.

WHY THIS IS A SCRIPT AND NOT A DOCUMENT.

Local ranking depends on the business's name, address and phone being the SAME
STRING everywhere it appears. Not "the same address" — the same characters.
Google reconciles a site and a listing by matching them, and "Plot No D13B" on
one and "Plot no. D-13B" on the other is two businesses as far as the match is
concerned. That is the single most common reason a practice ranks below its own
listing.

So the profile content is not written out by hand anywhere. It is DERIVED from
`chrome.py`, which is already the one place the facts live. Change the address
there and this sheet changes with it; there is no second copy to go stale, and
no chance of a typo entering through a profile field.

    python profiles.py            # write the sheet to outputs/
    python profiles.py --print    # dump it to the terminal instead

The sheet is a fill-in aid for a human. Neither Google nor Bing exposes an API
for this: the Business Profile Performance API is read-only for these fields,
and Bing Places has no public write API at all. Somebody has to paste it in.
This makes sure what they paste is right.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import chrome as C

OUT = Path(__file__).resolve().parents[1] / "outputs" / "profile-sheet.md"

# Google Business Profile's own field limits, as enforced by the form. Stated
# here so the sheet can flag an overrun BEFORE it is pasted and truncated —
# a description cut mid-sentence by the form is a thing nobody notices until a
# patient reads it.
GBP_DESCRIPTION_MAX = 750
GBP_SERVICE_NAME_MAX = 120

# Categories, in Google's own vocabulary. The PRIMARY category carries most of
# the local ranking weight and is the one query class the listing competes in;
# secondaries broaden it without diluting the primary. "Dermatologist" over
# "Skin care clinic" because the practice is a doctor-led medical practice and
# the searches that matter are for a specialist, not a salon.
GBP_PRIMARY_CATEGORY = "Dermatologist"
GBP_SECONDARY_CATEGORIES = [
    "Skin care clinic",
    "Hair transplant clinic",
    "Laser hair removal service",
    "Doctor",
]

# The services list. Named the way a PATIENT types them, not the way a
# clinician writes them: Google matches service names against queries, so
# "Vitiligo treatment" earns its place and "Melanocyte transplantation" only
# earns one because it is genuinely what this practice is known for.
GBP_SERVICES = [
    ("Vitiligo", [
        "Vitiligo treatment",
        "Vitiligo surgery",
        "Melanocyte transplantation",
        "Narrowband UVB phototherapy",
        "Excimer laser treatment",
    ]),
    ("Psoriasis", [
        "Psoriasis treatment",
        "Scalp psoriasis treatment",
        "Phototherapy for psoriasis",
        "Biologic treatment for psoriasis",
    ]),
    ("Hair", [
        "Hair loss treatment",
        "Alopecia areata treatment",
        "PRP hair treatment",
        "Hair grafting surgery",
    ]),
    ("Skin", [
        "Acne treatment",
        "Acne scar treatment",
        "Eczema treatment",
        "Fungal infection treatment",
        "Skin allergy treatment",
        "Keloid treatment",
        "Nail treatment",
    ]),
    ("Consultation", [
        "Online dermatology consultation",
        "In-person dermatology consultation",
    ]),
]

# Attributes worth setting, and the reason each one is worth the click. Google
# surfaces several of these as filter chips in the local pack, which means an
# unset attribute is not neutral — it excludes the listing from a filtered
# search rather than merely failing to advertise.
GBP_ATTRIBUTES = [
    ("Identifies as veteran-owned",
     "25 years in the Army Medical Corps — true, and a filterable attribute "
     "Google shows as a badge."),
    ("Appointment required", "matches the WhatsApp-only booking path."),
    ("Wheelchair accessible entrance",
     "set it only if the entrance genuinely is; a wrong answer here is the "
     "kind patients report."),
    ("Online care", "true — online consultations are offered and priced."),
    ("Restroom", "commonly filtered on for a clinic visit."),
    ("Gender-neutral restroom", "set only if accurate."),
    ("LGBTQ+ friendly", "set only if the practice wants to state it."),
]

# The directory citations that matter in Indian local search, in the order
# worth doing them. Each is a place the NAP must match character for character.
CITATIONS = [
    ("Practo", "https://www.practo.com",
     "already live — verify the address string matches the one below "
     "exactly, then leave it alone."),
    ("Bing Places", "https://www.bingplaces.com",
     "import from Google Business Profile; Bing is the index behind "
     "ChatGPT search."),
    ("Apple Business Connect", "https://businessconnect.apple.com",
     "owns the map on every iPhone; nothing else covers that surface."),
    ("JustDial", "https://www.justdial.com",
     "high-volume in Indian local search."),
    ("Sulekha", "https://www.sulekha.com",
     "secondary but widely scraped, so it propagates the NAP onward."),
    ("Lybrate", "https://www.lybrate.com",
     "doctor-specific; carries the physician entity, not the clinic."),
    ("IndiaMART / TradeIndia", "",
     "skip — B2B, wrong audience for a clinic."),
]


def _description() -> str:
    """The 750-character Business Profile description.

    Written to the facts in chrome.py rather than to a marketing brief: it
    opens with what the practice is and where, states the two conditions it is
    genuinely known for, and names the former identity — because a reader who
    knew this clinic as BNR needs to recognise it, and because Google reads the
    description as corroboration that the two names are one business.
    """
    return (
        f"{C.BRAND_PLAIN} is a dermatology practice in {C.LOCALITY}, "
        f"{C.CITY}, led by {C.PHYSICIAN['name']}, a consultant dermatologist "
        f"and dermatosurgeon with 45 years in practice — including 25 years "
        f"as a specialist in the Indian Army Medical Corps.\n\n"
        f"The clinic has a long-standing focus on vitiligo and psoriasis, "
        f"offering narrowband UVB phototherapy, excimer laser, and vitiligo "
        f"graft surgery including melanocyte transplantation. It also treats "
        f"hair loss, alopecia areata, acne and acne scarring, eczema, fungal "
        f"infections, keloids and nail disease.\n\n"
        f"Formerly {C.FORMER_PLAIN}. Consultations are by appointment, "
        f"{C.HOURS}. Online video consultations are available for patients "
        f"outside {C.CITY}."
    )


def _rows() -> list[tuple[str, str]]:
    """The Business Profile fields, paired with the exact value to paste."""
    return [
        ("Business name", C.GOOGLE_LISTING_PLAIN),
        ("Primary category", GBP_PRIMARY_CATEGORY),
        ("Additional categories", ", ".join(GBP_SECONDARY_CATEGORIES)),
        ("Address", C.ADDRESS),
        ("Pin (lat, long)", f"{C.GEO_LAT}, {C.GEO_LNG}"),
        ("Phone (primary)", C.PHONE_SHOW),
        ("Phone (additional)", f"{C.PHONE_ALT_SHOW}, {C.PHONE_LANDLINE_SHOW}"),
        ("Website", C.SITE + "/"),
        ("Appointment link", C.WHATSAPP),
        ("Hours", C.HOURS),
        ("Service area", C.SERVES),
    ]


def cell(v: str) -> str:
    """Escape a value for a markdown table cell.

    The business name is `Dr. Varada's ... | BNR Skin & Vitiligo Hospital` —
    a pipe inside the ONE field that must be copied character-perfect.
    Unescaped, the table silently splits it into two columns and the reader
    pastes half a name into Google. Escaping is not cosmetic here.
    """
    return v.replace("|", "\\|")


def build_sheet() -> str:
    d = _description()
    over = len(d) - GBP_DESCRIPTION_MAX
    L: list[str] = []
    add = L.append

    add("# Off-site profile sheet")
    add("")
    add("Generated by `python profiles.py` from `chrome.py`. **Do not edit "
        "this file** — change the constant and regenerate, or the site and "
        "the listings will drift apart.")
    add("")
    add("Every value below is the exact string to paste. Character-identical "
        "NAP across the site and every profile is the requirement; \"same "
        "address, different punctuation\" reads as two businesses.")
    add("")

    add("## 1. Google Business Profile — fields")
    add("")
    add(f"Listing: <{C.GOOGLE_LISTING_URL}>  ")
    add(f"Place ID: `{C.GOOGLE_PLACE_ID}`  ")
    add(f"CID: `{C.GOOGLE_CID}`")
    add("")
    add("| Field | Value to paste |")
    add("|---|---|")
    for k, v in _rows():
        add(f"| {k} | {cell(v)} |")
    add("")
    add("> The business name contains a literal `|`. It is escaped in the "
        "table above for rendering; the string to paste is:")
    add("")
    add(f"    {C.GOOGLE_LISTING_PLAIN}")
    add("")

    add("### Description")
    add("")
    add(f"{len(d)} / {GBP_DESCRIPTION_MAX} characters"
        + (f" — **{over} OVER, trim before pasting**" if over > 0
           else " — fits."))
    add("")
    add("```")
    add(d)
    add("```")
    add("")

    add("### Services")
    add("")
    add("Add under Edit profile → Services. Google matches these against "
        "queries, so each one is a query this listing can answer.")
    add("")
    for group, items in GBP_SERVICES:
        add(f"**{group}**")
        for s in items:
            flag = "  ⚠ too long" if len(s) > GBP_SERVICE_NAME_MAX else ""
            add(f"- {s}{flag}")
        add("")

    add("### Attributes")
    add("")
    add("An unset attribute is not neutral — Google shows several as filter "
        "chips, so leaving one blank excludes the listing from a filtered "
        "search.")
    add("")
    for name, why in GBP_ATTRIBUTES:
        add(f"- **{name}** — {why}")
    add("")

    add("### Photos")
    add("")
    add("The largest single gap. The profile and the site's schema both have "
        "one photograph between them — the doctor's portrait. Photo count "
        "and recency are a documented local ranking input, and listings with "
        "none lose the click even when they rank.")
    add("")
    add("Needed, in priority order:")
    add("")
    add("1. **Exterior** — the signage, shot from the road, so an arriving "
        "patient recognises the building. Google matches this against Street "
        "View.")
    add("2. **Interior** — reception and a consulting room.")
    add("3. **At work** — the phototherapy chamber and the excimer laser; "
        "they distinguish this practice from a general clinic.")
    add("4. **Team** — the doctor, captioned by name.")
    add("5. **Logo** (circle-safe) and a **16:9 cover**.")
    add("")
    add("Anything showing a patient needs consent on file before upload — "
        "the same gate the site's build applies to result imagery.")
    add("")

    add("## 2. Reviews — the biggest lever not yet pulled")
    add("")
    add(f"Current: Google {C.GOOGLE_RATING} across {C.GOOGLE_COUNT}; Practo "
        f"5.0 across 65. Review count, velocity and recency are the strongest "
        f"local-pack factors after proximity, and {C.GOOGLE_COUNT} is thin "
        f"for a practice this established.")
    add("")
    add("Deep link straight to the review box on the **correct** listing — "
        "\"search for us on Google\" loses most people who meant to write:")
    add("")
    add(f"    {C.GOOGLE_REVIEW_LINK}")
    add("")
    add("Send it in the WhatsApp thread a day after the visit, where the "
        "conversation already exists. Never incentivise a review, never bulk-"
        "send, and answer every one that arrives — response rate is itself "
        "a signal, and an unanswered bad review costs more than it should.")
    add("")

    add("## 3. The duplicate listing")
    add("")
    add("A second listing for this practice is still live and splitting the "
        "local signal:")
    add("")
    add("- **BNR Skin and Vitiligo Centre**, D/13A — unclaimed, no reviews, "
        "marked Temporarily closed")
    add("- Place ID `ChIJf5a-MQCbyzsRBpZuVNzoR9U`")
    add("")
    add("Report it: open in Maps → Suggest an edit → Close or remove → "
        "**Duplicate of** → point at the live listing above. Do not close "
        "the live one by mistake; the names differ by one word (\"Centre\" "
        "is the dead one).")
    add("")

    add("## 4. Bing Places")
    add("")
    add("Do it by **import from Google Business Profile**, not by adding the "
        "business manually — the import carries the fields and the "
        "verification in one step, and a manual entry becomes a third NAP "
        "to keep in sync.")
    add("")
    add("Bing matters far beyond its search share: **ChatGPT's web search "
        "runs on Bing's index**, so this is the most direct answer-engine "
        "lever available.")
    add("")
    add("Separately, in **Bing Webmaster Tools**, import the site from Search "
        "Console — that carries site verification and the sitemap across "
        "together.")
    add("")

    add("## 5. Directory citations")
    add("")
    add("Each is a place the NAP has to match the table above exactly.")
    add("")
    add("| Directory | URL | Note |")
    add("|---|---|---|")
    for name, url, note in CITATIONS:
        add(f"| {cell(name)} | {url or '—'} | {cell(note)} |")
    add("")

    add("---")
    add("")
    add("Regenerate with `python profiles.py` whenever a fact in `chrome.py` "
        "changes. A profile edit is always an edit to both.")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--print", action="store_true", dest="to_stdout",
                    help="write to stdout instead of the outputs file")
    args = ap.parse_args()
    sheet = build_sheet()
    if args.to_stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(sheet)
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(sheet, encoding="utf-8")
    d = _description()
    print(f"  profile sheet -> {OUT}")
    print(f"    description  {len(d)}/{GBP_DESCRIPTION_MAX} chars"
          + ("  OVER" if len(d) > GBP_DESCRIPTION_MAX else "  ok"))
    print(f"    services     {sum(len(i) for _, i in GBP_SERVICES)}")
    print(f"    citations    {len(CITATIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
