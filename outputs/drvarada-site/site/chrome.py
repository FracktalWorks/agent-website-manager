"""Shared chrome and block renderers for drvarada.com.

Every page is data (see `content/`); this module is the only place that emits HTML.
That split is deliberate — copy changes should never require touching markup, and a
markup fix should land on all 41 pages at once.

Band rhythm is enforced here, not left to the author: the design system allows three
dark bands per page, and the utility bar and footer already spend two of them. So a
page gets **at most one** dark section, and `assign_surfaces` raises if content asks
for more.
"""

from __future__ import annotations

import html
import json
import re

# Aliased: `SOURCES` is already taken in this module by the review-badge map
# (Practo/Google), and two dicts of that name in one file is how a citation list
# silently becomes a colour lookup.
from sources import SOURCES as REFERENCES

# ── constants ────────────────────────────────────────────────────────────────
SITE = "https://drvarada.com"
BRAND = "Dr. Varada's Skin &amp; Hair Center"
BRAND_PLAIN = "Dr. Varada's Skin & Hair Center"

# The name the practice traded under until the rebrand. It is not a footnote: the
# Google Business Profile still carries it along with the reviews and the local
# ranking earned under it, and patients treated here for years know the clinic by
# no other name. So every page that establishes identity says both names, and
# schema.org carries it as `alternateName`. A cold rename would throw that away
# and start the entity from zero.
FORMER = "BNR Skin &amp; Vitiligo Hospital"
FORMER_PLAIN = "BNR Skin & Vitiligo Hospital"

# WhatsApp is the only booking path. Every CTA on every page terminates here.
#
# This replaced Practo on 2026-07-30 at the clinic's instruction. Practo is still
# in use — as the *back office* diary, and as the place verified reviews live —
# but no patient actually arrives through it, and a booking button pointing at a
# queue the practice does not watch is worse than no button at all.
#
# The number changed to 80088 55330 on 2026-08-01. That line is the one the
# clinic will put behind the WhatsApp Business API and its automations, so it
# has to be the number every booking link resolves to from the start: a number
# patients have already saved and messaged is expensive to move later, and the
# conversation history does not follow.
WHATSAPP = "https://wa.me/918008855330"

# Voice. The primary line is the same number as WhatsApp, answered for calls
# too. PHONE and WHATSAPP must always be the same line — a patient who taps
# "call" and a patient who taps "book" should reach the same place.
#
# The other two are call-only fallbacks, in the order they should be tried.
PHONE = "tel:+918008855330"
PHONE_ALT = "tel:+919989955330"
PHONE_LANDLINE = "tel:+914079645852"
PHONE_SHOW = "+91 80088 55330"
PHONE_ALT_SHOW = "+91 99899 55330"
PHONE_LANDLINE_SHOW = "040 7964 5852"

# Practo is evidence now, not a door. The profile holds reviews tied to real
# appointments that the clinic cannot edit, which is precisely what makes them
# worth citing — so it is linked from proof, never from a button that says book.
PRACTO_REVIEWS = ("https://www.practo.com/hyderabad/doctor/"
                  "dr-khagendra-varada-dermatologist-cosmetologist-1")

# Directions. A maps query rather than a share link, because a share link is
# opaque and expires; this one is legible and reconstructible.
MAPS = ("https://www.google.com/maps/search/?api=1&query="
        "BNR+Skin+%26+Vitiligo+Hospital+Karkhana+Secunderabad")

# The second review platform, deep-linked to the reviews panel.
#
# NOT a maps search, which is where this pointed first and which lands on a map
# rather than on the reviews. NOT the URL Google gives you from the Share button
# either: that one carries `sxsrf` and `si` session tokens that expire, so it
# would quietly rot. `kgmid` is the listing's Knowledge Graph id — stable, and
# verified to land on the review panel.
#
# The id matters: there are TWO Google listings for this practice. The other one
# ("BNR Skin and Vitiligo Centre", D/13A, place id ChIJf5a-MQCbyzsRBpZuVNzoR9U)
# is unclaimed, has no reviews and is marked Temporarily closed. Linking that by
# accident would send patients to a dead listing.
GOOGLE_REVIEWS = ("https://www.google.com/search?kgmid=/g/11b77bk0d6"
                  "&q=BNR+Skin+VITILIGO+HOSPITAL+Khagendra+Varada+Reviews")

# Both platforms' figures, read from the live listings on 2026-07-30. Practo:
# 5.0 across 65 stories, 97% of 66 patients recommend. Google: 4.6 across 31.
# Google's is the lower number and it is shown anyway — a clinic that publishes
# only its best score is telling you it has another one.
GOOGLE_RATING = "4.6"
GOOGLE_COUNT = "31"

# One clinic, one address, supplied by the clinic on 2026-07-30. Must stay
# character-identical to the Google Business Profile — a locally-differing
# address string is the classic reason a practice ranks below its own listing.
#
# LOCALITY is the geography the pages compete in and CITY the one people say
# they are travelling to. Secunderabad is its own name in local search: someone
# in Trimulgherry does not search "Hyderabad", and Google's own listing files
# this clinic as "Dermatologist in Secunderabad".
LOCALITY = "Karkhana"
CITY = "Secunderabad"
ADDRESS = ("Plot No D13B, Wellington Rd, Vikrampuri Colony, Karkhana, "
           "Secunderabad, Telangana 500009")

# The localities within a realistic repeat-visit radius. These go into
# schema.org `areaServed` and are the honest answer to a "near me" query —
# a list of colonies someone can actually reach for a twice-weekly course,
# not every suburb in the district.
AREAS_SERVED = (
    "Karkhana", "Vikrampuri Colony", "Trimulgherry", "West Marredpally",
    "East Marredpally", "Bowenpally", "Bolarum", "Alwal", "Tarnaka",
    "Begumpet", "Malkajgiri", "Kompally", "Sainikpuri", "A.S. Rao Nagar",
    "Secunderabad Cantonment", "Habsiguda", "Somajiguda", "Punjagutta",
)
STREET = "Plot No D13B, Wellington Rd, Vikrampuri Colony, Karkhana"
PINCODE = "500009"
SERVES = ("Karkhana, Vikrampuri Colony, Trimulgherry, West Marredpally, "
          "Bowenpally, Alwal and greater Secunderabad")

# Consulting hours, confirmed by the clinic 2026-07-30. Two spellings of one
# fact: the prose form for people and the schema.org form for machines. Deriving
# one from the other would be clever and fragile, so they sit next to each other
# where a mismatch is visible.
HOURS = "Mon–Sat, 11:30 am – 5:00 pm"
HOURS_SCHEMA = "Mo-Sa 11:30-17:00"

# Patient volume, supplied by the clinic. It is the number that puts the review
# count in proportion: 65 verified reviews sounds thin alone and reads as
# substantial the moment you know it is 65 out of ten thousand. So the site
# states both, near each other, rather than hiding the smaller one — reviews
# are always a small fraction of patients, and saying so is more credible than
# implying otherwise.
PATIENTS = "10,000+"
REVIEWS = "65"
RATING = "5.0"

REVIEWER = "Dr. (Lt Col) Khagendra Varada, MBBS, Dip. Practical Dermatology (Cardiff)"

# The review date, written once. It was previously spelled twice — "29 July
# 2026" for the byline and "2026-07-29" inside the schema — which is a drift
# waiting to happen, and the failure is silent: the visible byline and the
# machine-readable `lastReviewed` would simply disagree, on a medical site,
# where that date is precisely the thing a reader is being asked to trust.
REVIEWED_ISO = "2026-07-29"
REVIEWED = "29 July 2026"

# When the copy last actually changed, which is NOT the same thing as when it
# was last medically reviewed. The sitemap's `lastmod` needs the former: it is
# how Google decides a page is worth re-fetching, and after a site-wide rewrite
# the old date would tell it there is nothing new to see. Bump this whenever
# copy changes materially; do not set it from the build clock, because a
# sitemap where every date is always today is discounted entirely.
CONTENT_MODIFIED = "2026-08-01"


def e(s: str) -> str:
    """Escape text that came from content data. Content may contain deliberate
    entities (&amp;, &nbsp;) so we only escape a bare & that is not already one."""
    return re.sub(r"&(?!#?\w+;)", "&amp;", s)


# ── navigation ───────────────────────────────────────────────────────────────
NAV = [
    ("Vitiligo", "vitiligo", [
        ("Vitiligo treatment", "vitiligo", "The national hub"),
        ("Types &amp; stages", "vitiligo-types-and-stages", None),
        ("Excimer laser", "vitiligo-excimer-laser", None),
        ("NB-UVB phototherapy", "vitiligo-phototherapy", None),
        ("Graft surgery", "vitiligo-graft-surgery", None),
        ("Vitiligo in children", "vitiligo-children", None),
        ("Diet &amp; myths", "vitiligo-diet-and-myths", None),
        ("What it costs", "vitiligo-cost", None),
        ("__Near you", None, None),
        ("Vitiligo treatment in Hyderabad", "vitiligo-treatment-hyderabad", None),
        ("Vitiligo treatment in Secunderabad", "vitiligo-treatment-secunderabad", None),
        ("Consult online, anywhere in India", "vitiligo-online-consultation", None),
    ]),
    ("Psoriasis", "psoriasis", [
        ("Psoriasis treatment", "psoriasis", "The national hub"),
        ("Types of psoriasis", "psoriasis-types", None),
        ("Scalp psoriasis", "psoriasis-scalp", None),
        ("Triggers &amp; diet", "psoriasis-triggers-and-diet", None),
        ("Phototherapy", "psoriasis-phototherapy", None),
        ("Systemics &amp; biologics", "psoriasis-biologics", None),
        ("What it costs", "psoriasis-cost", None),
        ("__Near you", None, None),
        ("Psoriasis treatment in Hyderabad", "psoriasis-treatment-hyderabad", None),
        ("Psoriasis treatment in Secunderabad", "psoriasis-treatment-secunderabad", None),
        ("Consult online, anywhere in India", "psoriasis-online-consultation", None),
    ]),
    # Skin and Aesthetics were one menu until the procedure catalogue landed. A
    # single panel carrying all of it ran past twenty items — taller than a
    # laptop viewport, in an absolutely-positioned dropdown that cannot scroll.
    # Splitting by intent is also the better answer: a patient with a rash and a
    # patient asking about fillers are not browsing the same list.
    ("Skin", None, [
        ("All treatments", "treatments", "Everything the clinic does"),
        ("__Conditions", None, None),
        ("Acne &amp; breakouts", "acne-treatment-hyderabad", None),
        ("Acne scars", "acne-scar-treatment-hyderabad", None),
        ("Skin allergy &amp; rashes", "skin-allergy-rashes-treatment", None),
        ("Eczema &amp; atopic dermatitis", "eczema-atopic-dermatitis-treatment", None),
        ("Fungal infections", "fungal-infection-treatment-hyderabad", None),
        ("__Procedures", None, None),
        ("Moles, warts &amp; skin tags", "dermatosurgery-hyderabad", None),
        ("Keloids &amp; raised scars", "keloid-treatment-hyderabad", None),
        ("Nail treatment &amp; surgery", "nail-treatment-hyderabad", None),
        ("Ear lobe repair", "ear-lobe-repair-hyderabad", None),
    ]),
    ("Aesthetics", None, [
        ("All treatments", "treatments", "Everything the clinic does"),
        ("__Injectables", None, None),
        ("Botox &amp; anti-ageing", "anti-aging-botox-hyderabad", None),
        ("Dermal fillers", "dermal-fillers-hyderabad", None),
        ("Thread lift", "thread-lift-hyderabad", None),
        ("Mesotherapy", "mesotherapy-hyderabad", None),
        ("Skin boosters", "skin-boosters-hyderabad", None),
        ("__Skin &amp; devices", None, None),
        ("Chemical peels", "chemical-peels-hyderabad", None),
        ("RF skin tightening", "rf-skin-tightening-hyderabad", None),
        ("Laser hair reduction", "laser-hair-reduction-hyderabad", None),
        ("Acne scar treatment", "acne-scar-treatment-hyderabad", None),
    ]),
    ("Hair", None, [
        ("Hair loss", "hair-loss-treatment-hyderabad", None),
        ("Hair loss in Secunderabad", "hair-loss-treatment-secunderabad", None),
        ("Alopecia areata", "alopecia-treatment-hyderabad", None),
        ("Alopecia across India", "alopecia-areata-treatment-india", None),
        ("PRP &amp; microneedling", "prp-hair-treatment-hyderabad", None),
        ("Hair grafting surgery", "hair-grafting-hyderabad", None),
        # This pointed at premature-greying-treatment — a copy-paste from the
        # line below that left `dandruff-treatment` reachable only from the
        # footer and the home-page chips.
        ("Dandruff", "dandruff-treatment", None),
        ("Premature greying", "premature-greying-treatment", None),
    ]),
    ("Results", "results", None),
    ("Across India", "online-consultation", [
        ("Online consultation", "online-consultation", "Any condition, by video"),
        ("Travelling for treatment", "travelling-for-treatment",
         "Coming from another state"),
        ("__By condition", None, None),
        ("Vitiligo, online", "vitiligo-online-consultation", None),
        ("Psoriasis, online", "psoriasis-online-consultation", None),
        ("Alopecia areata", "alopecia-areata-treatment-india", None),
    ]),
    ("The doctor", "about-dr-khagendra-varada", None),
    ("Visit", "contact", [
        ("The clinic in Secunderabad", "locations-secunderabad", "Mon–Sat, 11:30 am–5 pm"),
        ("Areas we serve", "areas-we-serve", "Both cities, with distances"),
        ("Contact &amp; directions", "contact", None),
        ("Patient stories", "patient-stories", None),
    ]),
]

FOOTER = [
    ("Vitiligo", [
        ("Vitiligo treatment", "vitiligo-cost"),
        ("Graft surgery", "vitiligo-graft-surgery"),
        ("Phototherapy", "vitiligo-phototherapy"),
        ("In Hyderabad", "vitiligo-treatment-hyderabad"),
        ("In Secunderabad", "vitiligo-treatment-secunderabad"),
        ("Consult online", "vitiligo-online-consultation"),
    ]),
    ("Psoriasis", [
        ("Psoriasis treatment", "psoriasis"),
        ("Scalp psoriasis", "psoriasis-scalp"),
        ("Triggers &amp; diet", "psoriasis-triggers-and-diet"),
        ("In Hyderabad", "psoriasis-treatment-hyderabad"),
        ("In Secunderabad", "psoriasis-treatment-secunderabad"),
        ("Consult online", "psoriasis-online-consultation"),
    ]),
    # A footer cannot carry sixty pages, and the attempt is what produced the
    # six-in-a-five-column row this grid was rebuilt to fix. `/treatments/` is
    # the page that carries the long tail; this column links the heads of the
    # clusters and hands the rest to it.
    ("Skin &amp; hair", [
        ("All treatments", "treatments"),
        ("Acne &amp; acne scars", "acne-treatment-hyderabad"),
        ("Fungal infections", "fungal-infection-treatment-hyderabad"),
        ("Eczema", "eczema-atopic-dermatitis-treatment"),
        ("Hair loss", "hair-loss-treatment-hyderabad"),
        ("PRP for hair", "prp-hair-treatment-hyderabad"),
    ]),
    # "Vitiligo across India" and "Psoriasis across India" used to sit here and
    # pointed at `vitiligo` and `psoriasis` — the same two pages column one
    # already links. Two labels for one destination is not extra reach; it
    # splits the anchor text and pads the column. Three pages are genuinely
    # national, so this column is three long and honest about it.
    ("Across India", [
        ("Online consultation", "online-consultation"),
        ("Travelling for treatment", "travelling-for-treatment"),
        ("Alopecia areata", "alopecia-areata-treatment-india"),
    ]),
    ("Visit us", [
        ("The clinic", "locations-secunderabad"),
        ("Areas we serve", "areas-we-serve"),
        ("Contact &amp; directions", "contact"),
        ("The doctor", "about-dr-khagendra-varada"),
        ("Patient stories", "patient-stories"),
        # `blog` had no inbound link from anywhere on the site — not the nav, not
        # the footer, not one related block. A page nothing links to is a page
        # Google treats as unimportant and nobody ever reaches.
        ("Notes &amp; articles", "blog"),
    ]),
]

# The language alternates are not a navigation topic — they are the same site in
# another script. They sat at the bottom of the "Visit" column, so a reader
# scanning for the clinic had to read past them. They get their own line.
# All four language pages, not two. The psoriasis translations had ZERO inbound
# internal links — reachable only by typing the URL, which is how a page written
# for a real audience ends up never being found by it.
LANGUAGES = [
    ("తెలుగు · బొల్లి", "te-vitiligo"),
    ("తెలుగు · సోరియాసిస్", "te-psoriasis"),
    ("हिन्दी · सफ़ेद दाग", "hi-vitiligo"),
    ("हिन्दी · सोरायसिस", "hi-psoriasis"),
]

# slug → production URL. Filenames stay flat so the Open Design preview and any static
# host resolve them without a server; canonical tags and schema carry the real URL.
URLS: dict[str, str] = {}


def href(slug: str, links: str = "preview") -> str:
    if slug.startswith(("http", "tel:", "mailto:", "#")):
        return slug
    if links == "production":
        return URLS.get(slug, "/")
    return "index.html" if slug == "index" else f"{slug}.html"


# Content hashes for the asset URLs, filled in by build.py before any page is
# rendered. Empty in the live editor, where files are re-read on every request.
ASSET_HASH: dict[str, str] = {}


def asset(path: str, links: str) -> str:
    """A stylesheet/image URL that resolves from wherever the page is served.

    Preview pages are flat files, so a relative path is right. Production URLs
    are nested (`/vitiligo/leucoderma/`), where a relative `assets/…` would
    resolve against the page's directory and 404 — so production gets a
    root-absolute path.

    Production URLs also carry `?v=<content hash>`, and that is not cosmetic.
    The server sends `Cache-Control: public, max-age=604800` on everything under
    `/assets/`, so a visitor who loaded the site once holds our CSS for a week
    and will not even revalidate it. With a URL that never changes, shipping new
    CSS changes nothing for anyone who has already visited — a mobile rebuild
    can go fully live and still show the old layout on the one phone that
    matters. The hash makes a changed file a different URL, so it is fetched
    immediately, while unchanged files keep the long cache they should have.
    """
    if links == "preview":
        return f"assets/{path}"
    # Favicons are deliberately NOT versioned. Google fetches a site icon rarely
    # and caches it against the URL it saw, so a `?v=` that changes whenever any
    # stylesheet changes keeps resetting that cache and the icon never settles
    # in the search result. Everything else wants the opposite.
    if path.startswith("logos/favicon"):
        return f"/assets/{path}"
    v = ASSET_HASH.get(path)
    return f"/assets/{path}?v={v}" if v else f"/assets/{path}"


def at(address: str, links: str, kind: str = "od") -> str:
    """The live editor's data address for a value, emitted on preview only.

    The editor needs to name the exact value behind a piece of rendered markup.
    Open Design solves this with a child-index DOM path computed at serve time;
    because our pages come from data we can emit the *data* address instead —
    `sections.4.items.0.title` — which survives any markup change and can never
    be ambiguous. Production HTML stays clean: these attributes exist only in
    the preview build the editor serves.
    """
    return f' data-{kind}="{address}"' if address and links == "preview" else ""


def img(im: dict, links: str, cls: str = "", address: str = "",
        priority: bool = False) -> str:
    """An <img> from an image dict: {src, alt, w, h, focus}.

    `w`/`h` are the intrinsic pixel size, emitted so the browser reserves the
    right box before the file arrives (no layout shift). `focus` is an
    object-position — the honest way to "crop" a responsive image, since the
    rendered aspect ratio is set by CSS and only the focal point is a content
    decision.

    `priority` is for an image that is above the fold. Everything here used to be
    `loading="lazy"` unconditionally, which is right for the twentieth image on a
    page and actively harmful for the first: the portrait in the page head is the
    largest element in the initial viewport, so it IS the Largest Contentful
    Paint, and lazy-loading defers the request until after layout. The rule is
    the plain one — lazy below the fold, eager and high-priority above it.
    """
    dims = (f' width="{int(im["w"])}" height="{int(im["h"])}"'
            if im.get("w") and im.get("h") else "")
    style = f' style="object-position:{im["focus"]}"' if im.get("focus") else ""
    klass = f' class="{cls}"' if cls else ""
    loading = (' fetchpriority="high" decoding="async"' if priority
               else ' loading="lazy" decoding="async"')
    return (f'<img{klass} src="{asset(im["src"], links)}" alt="{e(im["alt"])}"'
            f'{dims}{style}{loading}'
            f'{at(address, links, "od-img")}>')



# ── icons ────────────────────────────────────────────────────────────────────
# Inline SVG, stroked in `currentColor`, on a 24-unit grid. Inline because the
# pages must stay a single file with no request per glyph, and `currentColor`
# because an icon that carries its own colour is a colour outside `:root` — the
# exact thing the build refuses in CSS, and it would survive a rebrand.
#
# Deliberately a small set. An icon is only worth adding where it names the
# thing faster than the label does; a decorative one beside every heading is
# noise that makes a page look busy rather than considered.
ICONS = {
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
    # a disc on two ribbons. The first attempt put a cross inside the disc and
    # read as a keyhole at 20px — detail inside a small circle rarely survives.
    "medal": ("<circle cx='12' cy='14.5' r='5'/>"
              "<path d='M9.2 10 6.5 3.5M14.8 10l2.7-6.5'/>"),
    "star": ("<path d='M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 "
             "1-5.8L3.5 9.7l5.9-.9z'/>"),
    "chat": ("<path d='M20 12a8 8 0 0 1-11.6 7.1L4 20l1-4.2A8 8 0 1 1 20 12z'/>"),
    "pin": ("<path d='M12 21s7-5.3 7-11a7 7 0 1 0-14 0c0 5.7 7 11 7 11z'/>"
            "<circle cx='12' cy='10' r='2.5'/>"),
    "phone": ("<path d='M6 3h3l2 5-2.2 1.3a12 12 0 0 0 5.9 5.9L16 13l5 2v3a2 2 0 0 1-2.2 2"
              "A17 17 0 0 1 4 5.2 2 2 0 0 1 6 3z'/>"),
    "shield": ("<path d='M12 3l7 3v5.5c0 4.4-3 8-7 9.5-4-1.5-7-5.1-7-9.5V6z'/>"
               "<path d='M9 12l2 2 4-4'/>"),
    "microscope": ("<path d='M9 4h4l1 8H8z'/><path d='M6 20h13'/>"
                   "<path d='M8.5 20a5.5 5.5 0 0 0 9.2-4.1A5.5 5.5 0 0 0 14 11'/>"),
    "light": ("<circle cx='12' cy='12' r='3.4'/>"
              "<path d='M12 3v2.4M12 18.6V21M3 12h2.4M18.6 12H21"
              "M5.6 5.6l1.7 1.7M16.7 16.7l1.7 1.7M18.4 5.6l-1.7 1.7M7.3 16.7l-1.7 1.7'/>"),
    "route": ("<circle cx='6' cy='18' r='2.5'/><circle cx='18' cy='6' r='2.5'/>"
              "<path d='M8.5 18H14a4 4 0 0 0 0-8H9a4 4 0 0 1 0-8h.5'/>"),
}


# Platform marks for the review sources. Deliberately a coloured monogram plus
# the name rather than a traced logo: an approximated trademark drawn from
# memory looks worse than an honest badge and misrepresents someone else's mark.
SOURCES = {
    "practo": ("Practo", "#0FA0A8"),
    "google": ("Google", "#4285F4"),
}


def source_badge(key: str) -> str:
    name, colour = SOURCES[key]
    return (f'<span class="src src-{key}">'
            f'<i style="background:{colour}">{name[0]}</i>{name}</span>')


def icon(name: str, cls: str = "ic") -> str:
    """One glyph, or nothing if the name is unknown — a missing icon must never
    be a build failure, because copy is edited far more often than this map."""
    body = ICONS.get(name)
    if not body:
        return ""
    return (f'<span class="{cls}" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            f"{body}</svg></span>")

# ── head, header, footer ─────────────────────────────────────────────────────
# Search-console ownership tokens.
#
# Empty until someone with access to the Google and Bing accounts pastes the
# codes in — and nothing is emitted while they are empty, because a meta tag
# with a placeholder value is worse than no tag: verification silently fails and
# the property looks configured. Both are HTML-file-free methods, so they cost
# one line each and survive the WordPress deploy (the head is carried in post
# meta, so these land on all 61 pages).
#
# This matters more than it looks. Until the property is verified there is no
# Search Console at all: no index coverage, no query data, no manual-action
# notice, and no way to submit the sitemap — the site is ranking blind.
GOOGLE_VERIFICATION = ""     # content= value from the "HTML tag" method
BING_VERIFICATION = ""       # content= value from Bing Webmaster Tools


def verification() -> str:
    tags = []
    if GOOGLE_VERIFICATION:
        tags.append(f'<meta name="google-site-verification" '
                    f'content="{e(GOOGLE_VERIFICATION)}">')
    if BING_VERIFICATION:
        tags.append(f'<meta name="msvalidate.01" content="{e(BING_VERIFICATION)}">')
    return ("\n" + "\n".join(tags)) if tags else ""


def head(page: dict, links: str) -> str:
    url = SITE + URLS.get(page["slug"], "/")
    # hreflang: a page lists its language siblings plus itself; en is x-default.
    hreflang = ""
    if page.get("langs"):
        rows = [f'<link rel="alternate" hreflang="{lang}" '
                f'href="{SITE}{URLS.get(slug, "/")}">'
                for lang, slug in page["langs"]]
        rows.append(f'<link rel="alternate" hreflang="x-default" '
                    f'href="{SITE}{URLS.get(page["langs"][0][1], "/")}">')
        hreflang = "\n" + "\n".join(rows)
    return f"""<title>{e(page['title'])}</title>
<meta name="description" content="{e(page['meta'])}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">{hreflang}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(page['title'])}">
<meta property="og:description" content="{e(page['meta'])}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_IN">
<meta property="og:image" content="{SITE}/assets/img/dr-varada-hero.webp">
<meta property="og:image:width" content="880">
<meta property="og:image:height" content="1100">
<meta property="og:image:alt" content="Dr. (Lt Col) Khagendra Varada, dermatologist and dermatosurgeon">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(page['title'])}">
<meta name="twitter:description" content="{e(page['meta'])}">
<meta name="twitter:image" content="{SITE}/assets/img/dr-varada-hero.webp">
<meta name="theme-color" content="{THEME_COLOR}">{verification()}
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="{asset("logos/favicon-192.png", links)}" type="image/png" sizes="192x192">
<link rel="icon" href="{asset("logos/favicon.svg", links)}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{asset("logos/favicon-192.png", links)}">
<link rel="stylesheet" href="{asset("design-system.css", links)}">
<link rel="stylesheet" href="{asset("site.css", links)}">{brand_link(links)}"""


# Set by build.py from assets/brand.json when a corpus design system is driving
# the site. The brand stylesheet must load LAST: it redefines the same :root
# tokens the kit and site.css declare, and with equal specificity the winner is
# whichever the browser reads last.
BRAND_SYSTEM: str | None = None
THEME_COLOR = "#F8F5F3"


def brand_link(links: str) -> str:
    return (f'\n<link rel="stylesheet" href="{asset("brand.css", links)}">'
            if BRAND_SYSTEM else "")


def utility(links: str) -> str:
    return f"""<!-- utility bar — dark 1 of 3 -->
<div class="utility">
  <div class="wrap">
    <span><b>Karkhana, Secunderabad</b><span class="u-hours"> {HOURS}</span><span class="u-former"> &nbsp;·&nbsp; formerly {FORMER}</span></span>
    <a href="{PRACTO_REVIEWS}" rel="noopener"><b>★ {RATING} on Practo</b><span class="u-pat"> · {PATIENTS} patients treated</span> →</a>
  </div>
</div>"""


def header(links: str) -> str:
    items = []
    for i, (label, slug, panel) in enumerate(NAV):
        nav_at = f"chrome:NAV.{i}.1"
        if not panel:
            items.append(f'<a href="{href(slug, links)}"'
                         f'{at(nav_at, links, "od-link")}>{label}</a>')
            continue
        rows = []
        for j, (plabel, pslug, note) in enumerate(panel):
            if plabel.startswith("__"):
                rows.append(f'<p class="grp">{plabel[2:]}</p>')
                continue
            sub = f"<small>{note}</small>" if note else ""
            rows.append(f'<a href="{href(pslug, links)}"'
                        f'{at(f"chrome:NAV.{i}.2.{j}.1", links, "od-link")}>'
                        f'{plabel}{sub}</a>')
        top = href(slug, links) if slug else "#"
        items.append(
            f'<div class="menu"><a href="{top}"'
            f'{at(nav_at, links, "od-link") if slug else ""}>{label}</a>'
            f'<div class="panel">{"".join(rows)}</div></div>'
        )
    nav = "\n      ".join(items)

    # The mobile menu. Below 1040px the desktop nav is hidden, and without this
    # the entire 45-page site was reachable only through the footer — on the
    # devices most of this clinic's patients actually use. It is a <details>
    # disclosure rather than a scripted drawer so the pages stay script-free:
    # keyboard operable, works with JS off, and needs no ARIA wiring of its own.
    groups = []
    for label, slug, panel in NAV:
        if not panel:
            groups.append(f'<a href="{href(slug, links)}">{label}</a>')
            continue
        rows = [f'<a href="{href(pslug, links)}">{plabel}</a>'
                for plabel, pslug, note in panel if not plabel.startswith("__")]
        if slug:
            rows.insert(0, f'<a href="{href(slug, links)}">'
                           f'<b>{label} overview</b></a>')
        groups.append(f'<details><summary>{label}</summary>'
                      f'<div>{"".join(rows)}</div></details>')

    return f"""<!-- header -->
<header class="head">
  <div class="wrap">
    <a class="logo" href="{href('index', links)}" aria-label="{BRAND} — home">
      <img src="{asset("logos/logo-header.svg", links)}" alt="{BRAND}" width="1144" height="342" fetchpriority="high" decoding="async">
    </a>
    <nav aria-label="Main">
      {nav}
      <a class="btn btn-primary" href="{WHATSAPP}" rel="noopener">Book on WhatsApp</a>
    </nav>
    <details class="mnav">
      <summary aria-label="Menu"><span></span><span></span><span></span></summary>
      <nav aria-label="Main, mobile">
        {"".join(groups)}
        <a class="btn btn-primary" href="{WHATSAPP}" rel="noopener">Book on WhatsApp</a>
      </nav>
    </details>
  </div>
</header>"""


def crumbs(page: dict, links: str) -> str:
    trail = page.get("crumbs")
    if not trail:
        return ""
    parts = [f'<a href="{href("index", links)}">Home</a>']
    for label, slug in trail:
        parts.append(f'<a href="{href(slug, links)}">{label}</a>' if slug else label)
    joined = "<span>›</span>".join(parts)
    return f'<div class="band" style="padding-block:0"><div class="wrap crumbs">{joined}</div></div>'


def footer(links: str) -> str:
    """Brand and clinic details across the top, then one row of link columns.

    The brand block used to be the first cell of the same grid as the link
    columns, which fixed the row at five cells: the brand plus four. Adding a
    fifth group pushed it onto a second row, alone, with four empty columns
    beside it — and the grid template said nothing about being full, so nothing
    complained. Taking the brand out of the grid decouples the two: the columns
    can now be counted from FOOTER rather than hard-coded.

    It also freed the space for the address, hours and phone numbers. A clinic
    footer that carries no NAP is a local-SEO miss, and this one carried none.
    """
    cols = []
    for i, (title, items) in enumerate(FOOTER):
        rows = "".join(
            f'<a href="{href(s, links)}"'
            f'{at(f"chrome:FOOTER.{i}.1.{j}.1", links, "od-link")}>{l}</a>'
            for j, (l, s) in enumerate(items))
        cols.append(f"<div><h4>{title}</h4>{rows}</div>")
    langs = "".join(
        f'<a href="{href(s, links)}"'
        f'{at(f"chrome:LANGUAGES.{i}.1", links, "od-link")}>{l}</a>'
        for i, (l, s) in enumerate(LANGUAGES))
    return f"""<!-- footer — dark 3 of 3 -->
<footer>
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-brand">
        <div class="logo"><img src="{asset("logos/logo-footer.svg", links)}" alt="{BRAND}" width="1227" height="460" loading="lazy" decoding="async"></div>
        <p>Dermatology, trichology and aesthetics in Karkhana, Secunderabad.
          Formerly {FORMER}.</p>
      </div>
      <address class="foot-nap">
        <h4>The clinic</h4>
        <a href="{MAPS}" rel="noopener">{ADDRESS}</a>
        <span>{HOURS}</span>
      </address>
      <div class="foot-reach">
        <h4>Talk to us</h4>
        <a class="btn btn-primary" href="{WHATSAPP}" rel="noopener">Book on WhatsApp</a>
        <span class="foot-tel">
          <a href="{PHONE}">{PHONE_SHOW}</a>
          <a href="{PHONE_ALT}">{PHONE_ALT_SHOW}</a>
          <a href="{PHONE_LANDLINE}">{PHONE_LANDLINE_SHOW}</a>
        </span>
      </div>
    </div>
    <div class="cols">{''.join(cols)}</div>
    <div class="foot-langs"><h4>Read in</h4>{langs}</div>
    <div class="legal">
      <span>© {BRAND} · Regenerate · Restore · Reveal</span>
      <span>Information here is general and is not a substitute for consultation.</span>
    </div>
  </div>
</footer>

<div class="dock">
  <a class="btn btn-primary" href="{WHATSAPP}" rel="noopener">Book on WhatsApp</a>
  <a class="btn btn-secondary" href="{PHONE}">Call</a>
</div>"""


def booking(page: dict) -> str:
    b = page.get("booking") or {}
    title = b.get("h2", "The first appointment is a diagnosis.")
    body = b.get("p", "Not a treatment plan sold on the spot. Message the clinic and bring "
                      "your history.")
    label = b.get("cta", "Book on WhatsApp")
    link = b.get("url", WHATSAPP)
    return f"""<!-- booking band — mint -->
<section class="booking" id="book">
  <div class="wrap">
    <h2>{e(title)}</h2>
    <p style="max-width:58ch">{e(body)}</p>
    <div class="acts">
      <a class="btn btn-dark" href="{link}" rel="noopener">{label}</a>
      <a class="btn btn-secondary btn-line" href="{PHONE}">Call {PHONE_SHOW}</a>
    </div>
  </div>
</section>"""


# ── page head block ──────────────────────────────────────────────────────────
PORTRAIT_RADIUS = "border-radius:200px 200px var(--r) var(--r)"


def slot(links: str, address: str, label: str, cls: str = "media",
         style: str = "", inner: str = "") -> str:
    """An empty image slot: the placeholder AND the editor's drop target.

    A slot and a filled image carry the same `data-od-img` address, so the
    editor treats "supply the portrait" and "replace the portrait" as one
    operation. Until an image exists the visitor sees the labelled placeholder
    the design uses today, so an unshot page still reads as designed rather
    than broken.
    """
    st = f' style="{style}"' if style else ""
    return (f'<div class="{cls}"{st}{at(address, links, "od-img")}>'
            f'<p>{e(label)}</p>{inner}</div>')


def page_head(page: dict, links: str) -> str:
    eyebrow = (f'<div class="eyebrow"{at("eyebrow", links)}>{e(page["eyebrow"])}</div>'
               if page.get("eyebrow") else "")
    creds = ""
    if page.get("creds"):
        creds = '<div class="creds">' + "".join(f"<span>{e(c)}</span>" for c in page["creds"]) + "</div>"
    acts = []
    for n, (label, link) in enumerate(page.get("acts", [("Book on WhatsApp", WHATSAPP)])):
        cls = "btn-primary" if not acts else "btn-secondary"
        acts.append(f'<a class="btn {cls}" href="{href(link, links)}" rel="noopener"'
                    f'{at(f"acts.{n}", links, "od-link")}>{e(label)}</a>')
    glance, portrait = page.get("glance"), page.get("portrait")
    if glance:
        rows = "".join(
            f'<dt{at(f"glance.{n}.0", links)}>{e(k)}</dt>'
            f'<dd{at(f"glance.{n}.1", links)}>{e(v)}</dd>'
            for n, (k, v) in enumerate(glance))
        aside = (f'<div class="glance"><h2>At a glance</h2>'
                 f'<dl>{rows}</dl></div>')
        cls = "phead"
    elif portrait:
        # A third element marks the chip as a rating, which earns it stars.
        # "5.0" with no stars beside it reads as a version number.
        chips = []
        # Positions are named, not computed, because each one is placed against
        # the portrait by hand — `zip` also means a fourth entry is silently
        # dropped rather than landing somewhere unplanned.
        for n, (item, p) in enumerate(zip(portrait, ("a", "b", "c"))):
            v, l = item[0], item[1]
            mark = item[2] if len(item) > 2 else ""
            stars = '<span class="stars">★★★★★</span>' if mark == "stars" else ""
            chips.append(
                f'<div class="float {p}"><div class="stat"{at(f"portrait.{n}.0", links)}>'
                f'{v}</div>{stars}'
                f'<small{at(f"portrait.{n}.1", links)}>{e(l)}</small></div>')
        floats = "".join(chips)
        photo = page.get("photo")
        if photo:
            # A cut-out has no background of its own, so the panel behind it is
            # the design's — kept as the placeholder's mint/lilac gradient
            # rather than the flat surface a full-bleed photograph sits on.
            # That gradient is built from tokens, which is why the figure is
            # exported transparent: `brandkit.py apply` restyles the panel and
            # the photograph never has to be re-cut.
            box = "media has-img has-cutout" if photo.get("cutout") else "media has-img"
            aside = (f'<div class="{box}" style="{PORTRAIT_RADIUS}">'
                     f'{img(photo, links, "fill", "photo", priority=True)}'
                     f'{floats}</div>')
        else:
            aside = slot(links, "photo", "[ Portrait of Dr. Varada — to be supplied ]",
                         style=PORTRAIT_RADIUS, inner=floats)
        cls = "phead"
    else:
        aside = ""
        cls = "phead solo"
    return f"""<section class="band {cls}">
  <div class="wrap">
    <div>
      {eyebrow}
      <h1{at("h1", links)}>{page['h1']}</h1>
      <p class="lede"{at("lede", links)}>{e(page['lede'])}</p>
      <div class="acts">{''.join(acts)}</div>
      {creds}
    </div>
    {aside}
  </div>
</section>"""


# ── section blocks ───────────────────────────────────────────────────────────
def _headblock(s: dict, links: str = 'production', a: str = '') -> str:
    bits = []
    if s.get("eyebrow"):
        bits.append(f'<div class="eyebrow"{at(f"{a}.eyebrow", links)}>'
                    f'{e(s["eyebrow"])}</div>')
    if s.get("h2"):
        bits.append(f'<h2{at(f"{a}.h2", links)}>{e(s["h2"])}</h2>')
    if s.get("intro"):
        bits.append(f'<p{at(f"{a}.intro", links)}>{e(s["intro"])}</p>')
    return f'<div class="head-block">{"".join(bits)}</div>' if bits else ""


def _para(items, links: str = "production", a: str = "") -> str:
    """Prose body: paragraphs, bullet lists, and the "1.a|b|c" ordered shorthand.

    Only the first two forms get addresses. The shorthand packs several list
    items into ONE string joined by pipes, and no address can name a segment of
    a string — so those fall through to the editor's value-based matching
    rather than carrying an address that would rewrite the whole list.
    """
    out = []
    for i, it in enumerate(items):
        if isinstance(it, list):
            lis = "".join(f"<li{at(f'{a}.{i}.{j}', links)}>{e(x)}</li>"
                          for j, x in enumerate(it))
            out.append(f"<ul>{lis}</ul>")
        elif it.startswith("1."):
            lis = "".join(f"<li>{e(x)}</li>" for x in it[2:].split("|"))
            out.append(f"<ol>{lis}</ol>")
        else:
            out.append(f"<p{at(f'{a}.{i}', links)}>{e(it)}</p>")
    return "".join(out)


def blk_prose(s, links, a=''):
    return (_headblock(s, links, a)
            + f'<div class="prose">{_para(s["body"], links, f"{a}.body")}</div>')


def blk_cards(s, links, a=''):
    accent = s.get("accent", "")
    cards = []
    for n, it in enumerate(s["items"]):
        w = f"{a}.items.{n}"
        eb = (f'<div class="eyebrow"{at(f"{w}.eyebrow", links)}>{e(it["eyebrow"])}</div>'
              if it.get("eyebrow") else "")
        body = f'<p{at(f"{w}.body", links)}>{e(it["body"])}</p>' if it.get("body") else ""
        lis = ""
        if it.get("list"):
            lis = "<ul>" + "".join(f'<li{at(f"{w}.list.{j}", links)}>{e(x)}</li>'
                                   for j, x in enumerate(it["list"])) + "</ul>"
        mark = icon(it["icon"]) if it.get("icon") else ""
        cards.append(f'<article class="card {accent}">{mark}{eb}'
                     f'<h3{at(f"{w}.title", links)}>{e(it["title"])}</h3>'
                     f'{body}{lis}</article>')
    return _headblock(s, links, a) + f'<div class="cols">{"".join(cards)}</div>'


def blk_steps(s, links, a=''):
    steps = "".join(
        f'<div class="step"><h3{at(f"{a}.items.{n}.title", links)}>{e(i["title"])}</h3>'
        f'<p{at(f"{a}.items.{n}.body", links)}>{e(i["body"])}</p></div>'
        for n, i in enumerate(s["items"])
    )
    return _headblock(s, links, a) + f'<div class="steps">{steps}</div>'


def blk_table(s, links, a=''):
    thead = "".join(f'<th{at(f"{a}.head.{j}", links)}>{e(h)}</th>'
                    for j, h in enumerate(s["head"]))
    rows = "".join(
        "<tr>" + "".join(f'<td{at(f"{a}.rows.{r}.{c}", links)}>{e(cell)}</td>'
                         for c, cell in enumerate(row)) + "</tr>"
        for r, row in enumerate(s["rows"]))
    note = (f'<p class="tnote"{at(f"{a}.note", links)}>{e(s["note"])}</p>'
            if s.get("note") else "")
    return (_headblock(s, links, a) + f'<div class="tablewrap"><table><thead><tr>{thead}</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>{note}")


def blk_checklist(s, links, a=''):
    lis = "".join(f'<li{at(f"{a}.items.{n}", links)}>{e(x)}</li>'
                  for n, x in enumerate(s["items"]))
    return _headblock(s, links, a) + f'<ul class="checks">{lis}</ul>'


def blk_callout(s, links, a=''):
    cls = " warn" if s.get("warn") else ""
    return (f'<div class="callout{cls}">'
            f'<h4{at(f"{a}.title", links)}>{e(s["title"])}</h4>'
            f'<p{at(f"{a}.body", links)}>{e(s["body"])}</p></div>')


def blk_quote(s, links, a=''):
    return (f'<div class="quote"><blockquote{at(f"{a}.text", links)}>'
            f'“{e(s["text"])}”</blockquote>'
            f'<cite{at(f"{a}.cite", links)}>'
            f'{e(s.get("cite", "Dr. (Lt Col) Khagendra Varada"))}</cite></div>')


def blk_stats(s, links, a=''):
    cards = []
    for n, item in enumerate(s["items"]):
        v, l = item[0], item[1]
        mark = icon(item[2]) if len(item) > 2 else ""
        cards.append(
            f'<div class="card">{mark}'
            f'<div class="stat"{at(f"{a}.items.{n}.0", links)}>{e(v)}</div>'
            f'<p{at(f"{a}.items.{n}.1", links)}>{e(l)}</p></div>')
    return _headblock(s, links, a) + f'<div class="stats">{"".join(cards)}</div>'


def blk_chips(s, links, a=''):
    chips = "".join(
        f'<a class="chip" href="{href(sl, links)}"'
        f'{at(f"{a}.items.{n}", links, "od-link")}>'
        f'<i style="background:var(--{c})"></i>{e(t)} →</a>'
        for n, (t, sl, c) in enumerate(s["items"])
    )
    return _headblock(s, links, a) + f'<div class="chips">{chips}</div>'


def blk_split(s, links, a=''):
    """The one dark band a page is allowed. Rendered by render_section, not here."""
    cards = "".join(
        f'<div class="qcard"><h3{at(f"{a}.items.{n}.title", links)}>{e(i["title"])}</h3>'
        f'<p{at(f"{a}.items.{n}.body", links)}>{e(i["body"])}</p></div>'
        for n, i in enumerate(s["items"])
    )
    cta = ""
    if s.get("cta"):
        label, link = s["cta"]
        cta = (f'<a class="btn btn-on-dark" style="margin-top:26px" '
               f'href="{href(link, links)}" rel="noopener"'
               f'{at(f"{a}.cta", links, "od-link")}>{e(label)}</a>')
    left = []
    if s.get("eyebrow"):
        left.append(f'<div class="eyebrow"{at(f"{a}.eyebrow", links)}>'
                    f'{e(s["eyebrow"])}</div>')
    left.append(f'<h2{at(f"{a}.h2", links)}>{e(s["h2"])}</h2>')
    for i, p in enumerate(s.get("body", [])):
        left.append(f'<p style="margin-top:16px"{at(f"{a}.body.{i}", links)}>'
                    f'{e(p)}</p>')
    return f'<div>{"".join(left)}{cta}</div><div class="aside">{cards}</div>'


def blk_media(s, links, a=''):
    """A wide image band. `body` describes the shot until the shot exists."""
    if s.get("image"):
        inner = (f'<div class="media wide has-img" style="margin-top:30px">'
                 f'{img(s["image"], links, "fill", f"{a}.image")}</div>')
    else:
        inner = slot(links, f"{a}.image", s["body"], cls="media wide",
                     style="margin-top:30px")
    return _headblock(s, links, a) + inner


PILLAR_ACCENTS = {"mint": ("mint-sf", "mint-dp"), "apricot": ("apr-sf", "apr-dp"),
                  "lilac": ("lil-sf", "lil-dp")}


def blk_pillars(s, links, a=''):
    """The home-v3 pillar card: numbered accent tag, lead, linked conditions with
    optional Specialty flags, and a category footer link pinned to the bottom."""
    cards = []
    for n, it in enumerate(s["items"], start=1):
        w = f"{a}.items.{n - 1}"          # the tag reads 1-based, the data is not
        sf, dp = PILLAR_ACCENTS[it["accent"]]
        rows = []
        for j, entry in enumerate(it["list"]):
            label, slug, flag = (entry if len(entry) == 3 else (*entry, None))
            badge = f'<span class="flag">{e(flag)}</span>' if flag else ""
            rows.append(f'<li><a href="{href(slug, links)}"'
                        f'{at(f"{w}.list.{j}", links, "od-link")}>{label}</a>'
                        f'{badge}</li>')
        go_label, go_slug = it["go"]
        cards.append(
            f'<article class="pcard">'
            f'<div class="ptag" style="background:var(--{sf});color:var(--{dp})">'
            f"{n:02d}</div>"
            f'<h3{at(f"{w}.title", links)}>{e(it["title"])}</h3>'
            f'<p{at(f"{w}.body", links)}>{e(it["body"])}</p>'
            f'<ul>{"".join(rows)}</ul>'
            f'<a class="go" href="{href(go_slug, links)}" '
            f'style="color:var(--{dp})"{at(f"{w}.go", links, "od-link")}>'
            f'{e(go_label)} →</a></article>'
        )
    return _headblock(s, links, a) + f'<div class="bento">{"".join(cards)}</div>'


def blk_quotes(s, links, a=''):
    """Rating strip plus a scrollable track of verified patient stories.

    The numbers used to be written into this function — "5.0", "65", "97%" — so
    a section with different data still rendered the same three figures, and the
    live editor could not touch them. They come from the section now, with the
    current values as defaults so existing pages are unchanged.

    Each card may carry a third element marking it as a five-star review. It is
    only rendered when the data says so: putting stars on every quote by default
    would be asserting a rating nobody gave.

    The track runs continuously and pauses on hover. That needs the cards twice
    over — the loop is seamless because the second set arrives exactly where the
    first one left. The duplicates are deliberately stripped of their `data-od`
    addresses and marked `aria-hidden`: an address that matches two elements is
    ambiguous to the live editor, and a screen reader should not read the same
    nine testimonials twice.
    """
    items = s["items"]

    def card(n, item, addressed):
        text, src = item[0], item[1]
        stars = ('<span class="stars">★★★★★</span>'
                 if len(item) > 2 and item[2] == "stars" else "")
        p_at = at(f"{a}.items.{n}.0", links) if addressed else ""
        s_at = at(f"{a}.items.{n}.1", links) if addressed else ""
        hide = "" if addressed else ' aria-hidden="true"'
        return (f'<div class="q"{hide}><p{p_at}>“{e(text)}”</p>'
                f'<footer>{stars}'
                f'<span{s_at}>{e(src)}</span></footer></div>')

    sets = "".join(
        f'<div class="set">'
        f'{"".join(card(n, it, addressed) for n, it in enumerate(items))}'
        f"</div>"
        for addressed in (True, False))
    # Constant speed regardless of how many stories a section holds. A fixed
    # duration would make a nine-card track run three times faster than a
    # three-card one.
    dur = max(len(items), 3) * 8

    def score(key, value, count, note, url):
        return (f'<a class="score" href="{url}" rel="noopener">'
                f'{source_badge(key)}'
                f'<span class="n">{e(value)}</span>'
                f'<span class="s">★★★★★</span>'
                f'<span class="c">{e(count)} reviews · {e(note)}</span></a>')

    return _headblock(s, links, a) + f"""<div class="scores">
      {score("practo", RATING, REVIEWS, "97% recommend", PRACTO_REVIEWS)}
      {score("google", GOOGLE_RATING, GOOGLE_COUNT, "read them all", GOOGLE_REVIEWS)}
    </div>
    <div class="quotes" role="region" tabindex="0"
         aria-label="Patient stories from Practo and Google">
      <div class="track" style="--quotes-dur:{dur}s">{sets}</div>
    </div>"""


def blk_ba(s, links, a=''):
    """Before/after strip — consented clinical photography, never stock.

    An item is either a `(title, caption)` tuple (nothing shot yet) or a dict
    that adds `before`/`after` image dicts and a `consent` record. The consent
    field is not decoration: `build.py` refuses a patient photograph that does
    not carry one, because publishing a treatment result without written
    consent is a medical-ethics breach, not a content bug.
    """
    figs = []
    for n, item in enumerate(s["items"]):
        if isinstance(item, dict):
            title, cap = item["title"], item["cap"]
            before, after = item.get("before"), item.get("after")
        else:
            title, cap = item
            before = after = None
        pair = ""
        for side, im in (("before", before), ("after", after)):
            addr = f"{a}.items.{n}.{side}"
            if im:
                pair += (f'<div class="ph has-img"><em>{side.title()}</em>'
                         f'{img(im, links, "fill", addr)}</div>')
            else:
                pair += (f'<div class="ph"{at(addr, links, "od-img")}>'
                         f'<em>{side.title()}</em>[ photo ]</div>')
        figs.append(
            f'<figure><div class="pair">{pair}</div>'
            f'<figcaption><b{at(f"{a}.items.{n}.title", links)}>{e(title)}</b>'
            f'<span{at(f"{a}.items.{n}.cap", links)}>{e(cap)}</span>'
            f'</figcaption></figure>')
    return _headblock(s, links, a) + f'<div class="ba">{"".join(figs)}</div>'


BLOCKS = {
    "prose": blk_prose, "cards": blk_cards, "steps": blk_steps, "table": blk_table,
    "checklist": blk_checklist, "callout": blk_callout, "quote": blk_quote,
    "stats": blk_stats, "chips": blk_chips, "media": blk_media,
    "quotes": blk_quotes, "ba": blk_ba, "pillars": blk_pillars,
}

TICKER_ITEMS = ("Vitiligo", "Psoriasis", "Eczema", "Acne", "Hair loss", "Alopecia",
                "Skin allergies", "Botox", "Skin boosters", "Chemical peels",
                "Laser hair reduction", "Dandruff")


def ticker() -> str:
    """Condition ticker under the hero (design-system component; from home-v3).
    Two identical spans + translateX(-50%) = a seamless loop; pauses on
    prefers-reduced-motion via the stylesheet."""
    row = "<i>/</i>".join(TICKER_ITEMS) + "<i>/</i>"
    return (f'<div class="ticker" aria-hidden="true"><div class="row">'
            f"<span>{row}</span><span>{row}</span></div></div>")


def assign_surfaces(sections: list[dict]) -> list[str]:
    """Alternate light surfaces so a long page has a pulse; allow exactly one dark.

    `callout` and `quote` are inline furniture, not bands — they are folded into the
    section above them by `render_body`, so they never consume a surface.
    """
    darks = [i for i, s in enumerate(sections) if s["kind"] == "split"]
    if len(darks) > 1:
        raise ValueError(
            f"{len(darks)} dark sections requested; the band rhythm allows one "
            "(the utility bar and footer already spend the other two)"
        )
    cycle = ["", "paper", "", "tinted", "paper", "", "tinted", "paper"]
    out, n = [], 0
    for s in sections:
        if s["kind"] == "split":
            out.append("on-dark")
        else:
            out.append(cycle[n % len(cycle)])
            n += 1
    return out


def render_body(page: dict, links: str) -> str:
    """Render the section list.

    Addresses use each section's index in `page["sections"]` — its *authored*
    position — not its position among rendered bands. The two differ because
    callouts and quotes fold into the band above them, and an address that
    counted bands would point at the wrong dict the moment a page gained a
    callout.
    """
    bands = [(i, s) for i, s in enumerate(page["sections"])
             if s["kind"] not in ("callout", "quote")]
    # fold inline furniture into the preceding band
    attach: dict[int, list[tuple[int, dict]]] = {}
    pos = -1
    for i, s in enumerate(page["sections"]):
        if s["kind"] in ("callout", "quote"):
            attach.setdefault(pos, []).append((i, s))
        else:
            pos += 1
    surfaces = assign_surfaces([s for _, s in bands])

    out = []
    for pos, (oi, s) in enumerate(bands):
        surf = surfaces[pos]
        anchor = f' id="{s["anchor"]}"' if s.get("anchor") else ""
        tag = (f' data-od-sec="{oi}" data-od-kind="{s["kind"]}"'
               if links == "preview" else "")
        if s["kind"] == "split":
            inner = blk_split(s, links, f"sections.{oi}")
            out.append(f'<section class="band on-dark spot"{anchor}{tag}>'
                       f'<div class="wrap">{inner}</div></section>')
            continue
        inner = BLOCKS[s["kind"]](s, links, f"sections.{oi}")
        # Furniture authored BEFORE any band has nothing above it to fold into.
        # `pos` starts at -1, and this loop only ever asks for keys >= 0, so a
        # callout written first was collected and then silently dropped — the
        # skin-allergy page shipped for weeks without its opening "go to
        # hospital today" red-flag box. It leads the first band instead.
        if pos == 0:
            inner = "".join(BLOCKS[x["kind"]](x, links, f"sections.{xi}")
                            for xi, x in attach.get(-1, [])) + inner
        extra = "".join(BLOCKS[x["kind"]](x, links, f"sections.{xi}")
                        for xi, x in attach.get(pos, []))
        cls = f"band {surf}".strip()
        out.append(f'<section class="{cls}"{anchor}{tag}>'
                   f'<div class="wrap">{inner}{extra}</div></section>')
    return "\n".join(out)


def faq_html(page: dict, links: str) -> str:
    if not page.get("faqs"):
        return ""
    rows = []
    for i, (q, a) in enumerate(page["faqs"]):
        # an answer is either one string or a list of paragraphs, and the
        # address has to match: `faqs.i.1` for the first, `faqs.i.1.j` for the
        # second, or an edit rewrites the wrong node
        if isinstance(a, list):
            paras = "".join(f'<p{at(f"faqs.{i}.1.{j}", links)}>{e(p)}</p>'
                            for j, p in enumerate(a))
        else:
            paras = f'<p{at(f"faqs.{i}.1", links)}>{e(a)}</p>'
        rows.append(f'<details{" open" if i == 0 else ""}>'
                    f'<summary{at(f"faqs.{i}.0", links)}>{e(q)}</summary>'
                    f'{paras}</details>')
    return f"""<section class="band paper" id="faq">
  <div class="wrap">
    <div class="faq">
      <div class="eyebrow">Questions patients actually ask</div>
      <h2 style="margin-top:10px"{at("faq_h2", links)}>{e(page.get('faq_h2', 'Before you come in'))}</h2>
      <div style="margin-top:26px">{''.join(rows)}</div>
      <div class="byline">
        <span>Medically reviewed by <b>{REVIEWER}</b></span>
        <span class="dot"></span><span>Last reviewed {REVIEWED}</span>
      </div>
    </div>
  </div>
</section>"""


def related_html(page: dict, links: str) -> str:
    if not page.get("related"):
        return ""
    cards = "".join(
        f'<a href="{href(slug, links)}">'
        f'<h3{at(f"related.{i}.1", links)}>{e(t)}</h3>'
        f'<p{at(f"related.{i}.2", links)}>{e(b)}</p>'
        f'<div class="go">Read this →</div></a>'
        for i, (slug, t, b) in enumerate(page["related"])
    )
    return f"""<section class="band">
  <div class="wrap">
    <div class="head-block"><div class="eyebrow">Keep reading</div>
      <h2{at("related_h2", links)}>{e(page.get('related_h2', 'Related on this site'))}</h2></div>
    <div class="cols related">{cards}</div>
  </div>
</section>"""


def sources_html(page: dict, links: str) -> str:
    """The reference list.

    Deliberately plain and at the foot of the page: it is there to be checked,
    not to decorate. Every link is `rel="nofollow noopener"` and opens in a new
    tab — a patient mid-way through reading about their own condition should not
    lose the page, and the clinic is not trying to pass authority outward.
    """
    ids = page.get("sources") or []
    if not ids:
        return ""
    rows = []
    for i in ids:
        title, publisher, url = REFERENCES[i]
        # An organisation whose page title is its own name would otherwise print
        # twice, one line under the other, which reads like a rendering fault.
        byline = f"<span>{e(publisher)}</span>" if publisher != title else ""
        rows.append(
            f'<li><a href="{url}" rel="nofollow noopener" target="_blank">'
            f"{e(title)}</a>{byline}</li>")
    return f"""<section class="band" id="sources">
  <div class="wrap">
    <div class="refs">
      <div class="eyebrow">References</div>
      <p class="refs-note">The clinical statements on this page follow the
        guidance and evidence below. They are independent sources. None of them
        is connected to this clinic, and none of them sells the treatments
        described here.</p>
      <ol>{''.join(rows)}</ol>
    </div>
  </div>
</section>"""


# ── schema.org ───────────────────────────────────────────────────────────────
# One clinic. `alternateName` is the load-bearing field: it is how a search engine
# reconciles the Google listing, the Practo profile and this site as one practice
# rather than three, and it is the only reason the reviews earned under the old
# name still count towards the new one.
CLINICS = [
    {
        "@type": "MedicalClinic",
        "name": BRAND_PLAIN,
        "alternateName": [FORMER_PLAIN, "BNR Skin and Vitiligo Centre"],
        "url": SITE + "/locations/secunderabad/",
        "address": {"@type": "PostalAddress", "streetAddress": STREET,
                    "addressLocality": CITY, "postalCode": PINCODE,
                    "addressRegion": "Telangana", "addressCountry": "IN"},
        # Primary first: Google reads the first entry as the number to show.
        "telephone": [PHONE_SHOW, PHONE_ALT_SHOW, "+91 40 7964 5852"],
        "hasMap": MAPS,
        "openingHours": HOURS_SCHEMA,
        # The catchment, stated rather than inferred. Secunderabad and Hyderabad
        # are separate names in local search — someone in Trimulgherry does not
        # search "Hyderabad" — and the colonies are what "near me" resolves
        # against. India is here because vitiligo surgery genuinely draws
        # patients from outside the state; it is not a claim to be everywhere.
        "areaServed": [
            {"@type": "City", "name": "Secunderabad"},
            {"@type": "City", "name": "Hyderabad"},
            {"@type": "State", "name": "Telangana"},
            {"@type": "Country", "name": "India"},
            *({"@type": "Place", "name": n} for n in AREAS_SERVED),
        ],
    },
]

# The medical council registration number.
#
# Left empty until the clinic supplies it, and deliberately NOT invented. It is
# the one credential a reader can independently verify against a public
# register, which makes it the strongest single authorship signal on a medical
# site — and it is also required of Indian practitioners by the National Medical
# Commission's advertising code. When it arrives, set it here: it appears in the
# doctor's schema, on the about page and in the footer, from this one constant.
REGISTRATION = ""          # e.g. "TSMC/FMR/12345"
REGISTRATION_COUNCIL = "Telangana State Medical Council"


def _credential(name: str) -> dict:
    return {"@type": "EducationalOccupationalCredential",
            "credentialCategory": "degree", "name": name}


PHYSICIAN = {
    "@type": "Physician",
    "@id": SITE + "/about/dr-khagendra-varada/#physician",
    "name": "Dr. (Lt Col) Khagendra Varada",
    "honorificPrefix": "Dr.",
    "jobTitle": "Consultant Dermatologist and Dermatosurgeon",
    "description": (
        "Dermatologist and dermatosurgeon with 45 years in practice, including "
        "25 years as a specialist in the Indian Army Medical Corps. Practises in "
        "Karkhana, Secunderabad, with a long-standing focus on vitiligo surgery "
        "and psoriasis."),
    "medicalSpecialty": ["Dermatology", "Dermatologic Surgery"],
    "url": SITE + "/about/dr-khagendra-varada/",
    "image": SITE + "/assets/img/dr-varada-hero.webp",
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "Osmania Medical College"},
    "hasCredential": [
        _credential("MBBS, Osmania Medical College"),
        _credential("Diploma in Practical Dermatology, Cardiff University, UK"),
        _credential("Diploma in Dermatology, AAAM"),
    ],
    "memberOf": {"@type": "Organization", "name": "Indian Medical Association"},
    # What this doctor is an authority *on*. Left implicit, the entity is just a
    # name attached to a clinic; stated, it is the claim a knowledge graph and an
    # answer engine can actually match a vitiligo or psoriasis question against.
    "knowsAbout": [
        "Vitiligo", "Vitiligo surgery", "Melanocyte transplantation",
        "Narrowband UVB phototherapy", "Excimer laser", "Psoriasis",
        "Psoriatic arthritis", "Atopic dermatitis", "Acne", "Alopecia areata",
        "Androgenetic alopecia", "Dermatophytosis", "Keloid", "Dermatosurgery",
    ],
    "worksFor": {"@type": "MedicalClinic", "@id": SITE + "/#clinic",
                 "name": BRAND_PLAIN, "url": SITE},
    "sameAs": [PRACTO_REVIEWS],
}

if REGISTRATION:
    PHYSICIAN["identifier"] = {
        "@type": "PropertyValue",
        "propertyID": "Medical council registration",
        "name": REGISTRATION_COUNCIL,
        "value": REGISTRATION,
    }


def schema(page: dict) -> str:
    url = SITE + URLS.get(page["slug"], "/")
    graph: list[dict] = []

    if page["slug"] == "index":
        graph.append({
            "@type": "MedicalClinic",
            "@id": SITE + "/#clinic",
            "name": BRAND_PLAIN,
            "alternateName": [FORMER_PLAIN, "Dr Varada's Ageless Aesthetics"],
            "url": SITE,
            "description": page["meta"],
            "medicalSpecialty": ["Dermatology", "Dermatologic Surgery"],
            "areaServed": [{"@type": "City", "name": "Secunderabad"},
                           {"@type": "City", "name": "Hyderabad"},
                           {"@type": "Country", "name": "India"}],
            "location": CLINICS,
            "address": CLINICS[0]["address"],
            "telephone": CLINICS[0]["telephone"],
            "hasMap": MAPS,
            "sameAs": [PRACTO_REVIEWS, MAPS],
            # Appointments are taken in a WhatsApp conversation and nowhere else,
            # so that is what the machine-readable booking action has to say.
            "potentialAction": {
                "@type": "CommunicateAction",
                "name": "Book an appointment on WhatsApp",
                "target": WHATSAPP,
            },
        })
        graph.append(PHYSICIAN)
        # The site name and logo, stated rather than inferred.
        #
        # Google was rendering the result as "Dr. Varada's: Dermatologist in
        # Hyderabad & Secunderabad" — it had decided the site name for itself
        # and reordered our title around it. `WebSite.name` is the documented
        # way to tell it what the site is called, and `Organization.logo` is
        # what it reads for the icon beside the listing.
        graph.append({
            "@type": "WebSite",
            "@id": SITE + "/#website",
            "url": SITE + "/",
            "name": BRAND_PLAIN,
            "alternateName": ["Dr. Varada's", FORMER_PLAIN],
            "inLanguage": "en-IN",
            "publisher": {"@id": SITE + "/#clinic"},
        })
        graph.append({
            "@type": "Organization",
            "@id": SITE + "/#organisation",
            "name": BRAND_PLAIN,
            "alternateName": FORMER_PLAIN,
            "url": SITE + "/",
            "logo": {"@type": "ImageObject",
                     "url": SITE + "/assets/logos/favicon-512.png",
                     "width": 512, "height": 512},
            "telephone": PHONE_SHOW,
            "address": CLINICS[0]["address"],
            "sameAs": [PRACTO_REVIEWS, MAPS],
        })
    elif page.get("schema_type") == "Physician":
        graph.append(PHYSICIAN)
    elif page.get("schema_type") == "MedicalClinic":
        graph.append(dict(CLINICS[page["clinic_index"]], **{"@id": url + "#clinic"}))
    else:
        node = {
            "@type": "MedicalWebPage",
            "@id": url + "#page",
            "url": url,
            "name": page["title"],
            "description": page["meta"],
            "inLanguage": "en-IN",
            "lastReviewed": REVIEWED_ISO,
            "reviewedBy": {"@id": PHYSICIAN["@id"]},
            "about": {"@type": "MedicalCondition", "name": page["condition"]}
            if page.get("condition") else None,
            "audience": {"@type": "Patient"},
            # The same reference list the reader sees, in the form a machine can
            # follow. `citation` is what lets a crawler or an answer engine check
            # a claim against its source instead of taking the page's word for
            # it — the difference between content that can be quoted and content
            # that can only be read.
            "citation": [
                {"@type": "CreativeWork", "name": REFERENCES[i][0],
                 "publisher": {"@type": "Organization", "name": REFERENCES[i][1]},
                 "url": REFERENCES[i][2]}
                for i in page.get("sources", [])
            ] or None,
        }
        graph.append({k: v for k, v in node.items() if v is not None})

    if page.get("faqs"):
        graph.append({
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer",
                                    "text": " ".join(a) if isinstance(a, list) else a}}
                for q, a in page["faqs"]
            ],
        })

    # The clinic entity, on EVERY page.
    #
    # It used to appear on three (home, the location page, the doctor page), so
    # 58 of 61 pages carried no business identity at all. For a practice whose
    # traffic is overwhelmingly "dermatologist near me", that is the single
    # biggest structured-data gap: a searcher landing on /vitiligo-treatment-
    # hyderabad/ from a local query gave Google no address, no phone and no
    # opening hours on the page that ranked.
    #
    # A compact node repeating the @id of the full one on the home page — same
    # identifier, so the two are one entity rather than sixty-one businesses,
    # and self-contained so it resolves without Google having crawled home first.
    if page["slug"] != "index" and page.get("schema_type") not in ("Physician", "MedicalClinic"):
        graph.append({
            "@type": "MedicalClinic",
            "@id": SITE + "/#clinic",
            "name": BRAND_PLAIN,
            "alternateName": FORMER_PLAIN,
            "url": SITE,
            "address": CLINICS[0]["address"],
            "telephone": CLINICS[0]["telephone"],
            "medicalSpecialty": ["Dermatology", "Dermatologic Surgery"],
            "hasMap": MAPS,
            "sameAs": [PRACTO_REVIEWS, MAPS],
        })

    if page.get("crumbs"):
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
        for i, (label, slug) in enumerate(page["crumbs"], start=2):
            entry = {"@type": "ListItem", "position": i, "name": html.unescape(label)}
            if slug:
                entry["item"] = SITE + URLS.get(slug, "/")
            items.append(entry)
        graph.append({"@type": "BreadcrumbList", "itemListElement": items})

    doc = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, indent=2, ensure_ascii=False) + "</script>")


LANGS = {"te": "te-IN", "hi": "hi-IN"}


def page_lang(page: dict) -> str:
    """The document language, taken from the page rather than hardcoded.

    The Telugu and Hindi pages declared `lang="en-IN"`, which contradicts their
    own hreflang tags, tells a screen reader to read Telugu with English
    phonetics, and is a WCAG 3.1.1 (Level A) failure. A page's language is a
    property of the page, so it comes from the page.
    """
    prefix = page["slug"].split("-", 1)[0]
    return page.get("lang") or LANGS.get(prefix, "en-IN")


# ── the whole page ───────────────────────────────────────────────────────────
def render(page: dict, links: str = "preview") -> str:
    """A complete standalone HTML5 document. The pages used to be authored as Open
    Design artifact bodies (OD's wrapper supplied doctype, charset and viewport);
    the repo is now the only surface, so each page must stand on its own —
    file://, python -m http.server and the WordPress deploy all get the same file."""
    # Everything from the H1 to the booking band is the page's own content, so it
    # goes in <main>: that is what gives a screen-reader user, and the skip link,
    # one jump past the utility bar and the whole navigation.
    main = "\n".join(filter(None, [
        page_head(page, links),
        ticker() if page.get("ticker") else "",
        render_body(page, links),
        faq_html(page, links),
        sources_html(page, links),
        related_html(page, links),
        booking(page),
    ]))
    body = "\n".join(filter(None, [
        f'<a class="skip" href="#main">Skip to content</a>',
        utility(links),
        header(links),
        crumbs(page, links),
        f'<main id="main">\n{main}\n</main>',
        footer(links),
    ]))
    return "\n".join([
        "<!doctype html>",
        f'<html lang="{page_lang(page)}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<!-- {page['slug']} · template {page['template']} · "
        f"{SITE}{URLS.get(page['slug'], '/')} -->",
        head(page, links),
        schema(page),
        "</head>",
        "<body>",
        body,
        "</body>",
        "</html>",
        "",
    ])
