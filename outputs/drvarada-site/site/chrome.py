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

# ── constants ────────────────────────────────────────────────────────────────
SITE = "https://drvarada.com"
BRAND = "Dr. Varada's Skin &amp; Hair Center"
BRAND_PLAIN = "Dr. Varada's Skin & Hair Center"

# Practo is the only booking path. Every CTA on every page terminates here; the clinic
# team already runs on Practo and a second queue would break their workflow.
# These are the real profiles (carried over from home-v3, the finalized homepage):
PRACTO = ("https://www.practo.com/hyderabad/doctor/"
          "dr-khagendra-varada-dermatologist-cosmetologist-1")
PRACTO_JH = ("https://www.practo.com/hyderabad/clinic/"
             "dr-varada-s-ageless-aesthetics-jubilee-hills")
PRACTO_WM = PRACTO            # → West Marredpally deep link once its profile is confirmed
PRACTO_ONLINE = PRACTO        # → the doctor profile carries the video-consult button

# Placeholders the clinic still has to supply. Kept as named constants so a single
# edit fills them everywhere and so `build.py` can report exactly what is outstanding.
PHONE = "tel:+91"
WHATSAPP = "https://wa.me/91"

REVIEWER = "Dr. (Lt Col) Khagendra Varada, MBBS, Dip. Practical Dermatology (Cardiff)"
REVIEWED = "29 July 2026"


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
        ("__In Hyderabad", None, None),
        ("Vitiligo treatment in Hyderabad", "vitiligo-treatment-hyderabad", None),
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
        ("__In Hyderabad", None, None),
        ("Psoriasis treatment in Hyderabad", "psoriasis-treatment-hyderabad", None),
        ("Consult online, anywhere in India", "psoriasis-online-consultation", None),
    ]),
    ("Skin", None, [
        ("__Conditions", None, None),
        ("Acne &amp; acne scars", "acne-treatment-hyderabad", None),
        ("Skin allergy &amp; rashes", "skin-allergy-rashes-treatment", None),
        ("Eczema &amp; atopic dermatitis", "eczema-atopic-dermatitis-treatment", None),
        ("__Aesthetic", None, None),
        ("Botox &amp; anti-ageing", "anti-aging-botox-hyderabad", None),
        ("Skin boosters", "skin-boosters-hyderabad", None),
        ("RF skin tightening", "rf-skin-tightening-hyderabad", None),
        ("Chemical peels", "chemical-peels-hyderabad", None),
        ("Laser hair reduction", "laser-hair-reduction-hyderabad", None),
        ("Moles, warts &amp; skin tags", "dermatosurgery-hyderabad", None),
    ]),
    ("Hair", None, [
        ("Hair loss", "hair-loss-treatment-hyderabad", None),
        ("Alopecia areata", "alopecia-treatment-hyderabad", None),
        ("Hair grafting surgery", "hair-grafting-hyderabad", None),
        ("Dandruff", "dandruff-treatment", None),
        ("Premature greying", "premature-greying-treatment", None),
    ]),
    ("Results", "results", None),
    ("The doctor", "about-dr-khagendra-varada", None),
    ("Visit", "contact", [
        ("Jubilee Hills clinic", "locations-jubilee-hills", "Mon–Sat, 1:30–8 pm"),
        ("West Marredpally clinic", "locations-west-marredpally", "Mon–Sat, 7–9 am"),
        ("Contact &amp; directions", "contact", None),
        ("Patient stories", "patient-stories", None),
    ]),
]

FOOTER = [
    ("Vitiligo", [
        ("Vitiligo treatment", "vitiligo"),
        ("Graft surgery", "vitiligo-graft-surgery"),
        ("Phototherapy", "vitiligo-phototherapy"),
        ("In Hyderabad", "vitiligo-treatment-hyderabad"),
        ("Consult online", "vitiligo-online-consultation"),
    ]),
    ("Psoriasis", [
        ("Psoriasis treatment", "psoriasis"),
        ("Scalp psoriasis", "psoriasis-scalp"),
        ("Triggers &amp; diet", "psoriasis-triggers-and-diet"),
        ("In Hyderabad", "psoriasis-treatment-hyderabad"),
        ("Consult online", "psoriasis-online-consultation"),
    ]),
    ("Skin &amp; hair", [
        ("Acne", "acne-treatment-hyderabad"),
        ("Eczema", "eczema-atopic-dermatitis-treatment"),
        ("Hair loss", "hair-loss-treatment-hyderabad"),
        ("Alopecia areata", "alopecia-treatment-hyderabad"),
        ("Botox &amp; anti-ageing", "anti-aging-botox-hyderabad"),
    ]),
    ("Visit", [
        ("Jubilee Hills", "locations-jubilee-hills"),
        ("West Marredpally", "locations-west-marredpally"),
        ("The doctor", "about-dr-khagendra-varada"),
        ("Results", "results"),
        ("Patient stories", "patient-stories"),
        ("తెలుగులో చదవండి", "te-vitiligo"),
        ("हिन्दी में पढ़ें", "hi-vitiligo"),
    ]),
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


def asset(path: str, links: str) -> str:
    """A stylesheet/image URL that resolves from wherever the page is served.

    Preview pages are flat files, so a relative path is right. Production URLs
    are nested (`/vitiligo/leucoderma/`), where a relative `assets/…` would
    resolve against the page's directory and 404 — so production gets a
    root-absolute path.
    """
    return f"assets/{path}" if links == "preview" else f"/assets/{path}"


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


def img(im: dict, links: str, cls: str = "", address: str = "") -> str:
    """An <img> from an image dict: {src, alt, w, h, focus}.

    `w`/`h` are the intrinsic pixel size, emitted so the browser reserves the
    right box before the file arrives (no layout shift). `focus` is an
    object-position — the honest way to "crop" a responsive image, since the
    rendered aspect ratio is set by CSS and only the focal point is a content
    decision.
    """
    dims = (f' width="{int(im["w"])}" height="{int(im["h"])}"'
            if im.get("w") and im.get("h") else "")
    style = f' style="object-position:{im["focus"]}"' if im.get("focus") else ""
    klass = f' class="{cls}"' if cls else ""
    return (f'<img{klass} src="{asset(im["src"], links)}" alt="{e(im["alt"])}"'
            f'{dims}{style} loading="lazy" decoding="async"'
            f'{at(address, links, "od-img")}>')


# ── head, header, footer ─────────────────────────────────────────────────────
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
<meta name="theme-color" content="{THEME_COLOR}">
<link rel="icon" href="{asset("logos/favicon.svg", links)}" type="image/svg+xml">
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
    <span><b>Jubilee Hills</b> Mon–Sat 1:30–8 pm &nbsp;·&nbsp; <b>West Marredpally</b> Mon–Sat 7–9 am</span>
    <a href="{PRACTO}" rel="noopener"><b>★ 5.0 on Practo</b> — 65 patient stories →</a>
  </div>
</div>"""


def header(links: str) -> str:
    items = []
    for label, slug, panel in NAV:
        if not panel:
            items.append(f'<a href="{href(slug, links)}">{label}</a>')
            continue
        rows = []
        for plabel, pslug, note in panel:
            if plabel.startswith("__"):
                rows.append(f'<p class="grp">{plabel[2:]}</p>')
                continue
            sub = f"<small>{note}</small>" if note else ""
            rows.append(f'<a href="{href(pslug, links)}">{plabel}{sub}</a>')
        top = href(slug, links) if slug else "#"
        items.append(
            f'<div class="menu"><a href="{top}">{label}</a>'
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
            rows.insert(0, f'<a href="{href(slug, links)}"><b>{label} — '
                           f'overview</b></a>')
        groups.append(f'<details><summary>{label}</summary>'
                      f'<div>{"".join(rows)}</div></details>')

    return f"""<!-- header -->
<header class="head">
  <div class="wrap">
    <a class="logo" href="{href('index', links)}" aria-label="{BRAND} — home">
      <img src="{asset("logos/logo-header.svg", links)}" alt="{BRAND}">
    </a>
    <nav aria-label="Main">
      {nav}
      <a class="btn btn-primary" href="{PRACTO}" rel="noopener">Book on Practo</a>
    </nav>
    <details class="mnav">
      <summary aria-label="Menu"><span></span><span></span><span></span></summary>
      <nav aria-label="Main, mobile">
        {"".join(groups)}
        <a class="btn btn-primary" href="{PRACTO}" rel="noopener">Book on Practo</a>
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
    cols = []
    for title, items in FOOTER:
        rows = "".join(f'<a href="{href(s, links)}">{l}</a>' for l, s in items)
        cols.append(f"<div><h4>{title}</h4>{rows}</div>")
    return f"""<!-- footer — dark 3 of 3 -->
<footer>
  <div class="wrap">
    <div class="cols">
      <div>
        <div class="logo"><img src="{asset("logos/logo-footer.svg", links)}" alt="{BRAND}"></div>
        <p style="margin-top:16px;font-size:14.5px;max-width:32ch;color:var(--on-dark)">
          Dermatology, trichology and aesthetics in Hyderabad. Formerly BNR Skin &amp;
          Vitiligo Hospital.</p>
      </div>
      {''.join(cols)}
    </div>
    <div class="legal">
      <span>© {BRAND} · Regenerate · Restore · Reveal</span>
      <span>Information here is general and is not a substitute for consultation.</span>
    </div>
  </div>
</footer>

<div class="dock">
  <a class="btn btn-primary" href="{PRACTO}" rel="noopener">Book on Practo</a>
  <a class="btn btn-secondary" href="{PHONE}">Call</a>
</div>"""


def booking(page: dict) -> str:
    b = page.get("booking") or {}
    title = b.get("h2", "The first appointment is a diagnosis.")
    body = b.get("p", "Not a treatment plan sold on the spot. Book a time and bring your history.")
    label = b.get("cta", "Book on Practo")
    link = b.get("url", PRACTO)
    return f"""<!-- booking band — mint -->
<section class="booking" id="book">
  <div class="wrap">
    <h2>{e(title)}</h2>
    <p style="max-width:58ch">{e(body)}</p>
    <div class="acts">
      <a class="btn btn-dark" href="{link}" rel="noopener">{label}</a>
      <a class="btn btn-secondary btn-line" href="{WHATSAPP}" rel="noopener">WhatsApp your photos</a>
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
    for n, (label, link) in enumerate(page.get("acts", [("Book on Practo", PRACTO)])):
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
        floats = "".join(
            f'<div class="float {p}"><div class="stat"{at(f"portrait.{n}.0", links)}>{v}</div>'
            f'<small{at(f"portrait.{n}.1", links)}>{e(l)}</small></div>'
            for n, ((v, l), p) in enumerate(zip(portrait, ("a", "b")))
        )
        photo = page.get("photo")
        if photo:
            aside = (f'<div class="media has-img" style="{PORTRAIT_RADIUS}">'
                     f'{img(photo, links, "fill", "photo")}{floats}</div>')
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


def _para(items) -> str:
    out = []
    for it in items:
        if isinstance(it, list):
            lis = "".join(f"<li>{e(x)}</li>" for x in it)
            out.append(f"<ul>{lis}</ul>")
        elif it.startswith("1."):
            lis = "".join(f"<li>{e(x)}</li>" for x in it[2:].split("|"))
            out.append(f"<ol>{lis}</ol>")
        else:
            out.append(f"<p>{e(it)}</p>")
    return "".join(out)


def blk_prose(s, links, a=''):
    return _headblock(s, links, a) + f'<div class="prose">{_para(s["body"])}</div>'


def blk_cards(s, links, a=''):
    accent = s.get("accent", "")
    cards = []
    for it in s["items"]:
        eb = f'<div class="eyebrow">{e(it["eyebrow"])}</div>' if it.get("eyebrow") else ""
        body = f"<p>{e(it['body'])}</p>" if it.get("body") else ""
        lis = ""
        if it.get("list"):
            lis = "<ul>" + "".join(f"<li>{e(x)}</li>" for x in it["list"]) + "</ul>"
        cards.append(f'<article class="card {accent}">{eb}<h3>{e(it["title"])}</h3>{body}{lis}</article>')
    return _headblock(s, links, a) + f'<div class="cols">{"".join(cards)}</div>'


def blk_steps(s, links, a=''):
    steps = "".join(
        f'<div class="step"><h3>{e(i["title"])}</h3><p>{e(i["body"])}</p></div>' for i in s["items"]
    )
    return _headblock(s, links, a) + f'<div class="steps">{steps}</div>'


def blk_table(s, links, a=''):
    thead = "".join(f"<th>{e(h)}</th>" for h in s["head"])
    rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in s["rows"])
    note = f'<p class="tnote">{e(s["note"])}</p>' if s.get("note") else ""
    return (_headblock(s, links, a) + f'<div class="tablewrap"><table><thead><tr>{thead}</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>{note}")


def blk_checklist(s, links, a=''):
    lis = "".join(f"<li>{e(x)}</li>" for x in s["items"])
    return _headblock(s, links, a) + f'<ul class="checks">{lis}</ul>'


def blk_callout(s, links, a=''):
    cls = " warn" if s.get("warn") else ""
    return f'<div class="callout{cls}"><h4>{e(s["title"])}</h4><p>{e(s["body"])}</p></div>'


def blk_quote(s, links, a=''):
    return (f'<div class="quote"><blockquote>“{e(s["text"])}”</blockquote>'
            f'<cite>{e(s.get("cite", "Dr. (Lt Col) Khagendra Varada"))}</cite></div>')


def blk_stats(s, links, a=''):
    cards = "".join(
        f'<div class="card"><div class="stat">{e(v)}</div><p>{e(l)}</p></div>' for v, l in s["items"]
    )
    return _headblock(s, links, a) + f'<div class="stats">{cards}</div>'


def blk_chips(s, links, a=''):
    chips = "".join(
        f'<a class="chip" href="{href(sl, links)}"><i style="background:var(--{c})"></i>{e(t)} →</a>'
        for t, sl, c in s["items"]
    )
    return _headblock(s, links, a) + f'<div class="chips">{chips}</div>'


def blk_split(s, links, a=''):
    """The one dark band a page is allowed. Rendered by render_section, not here."""
    cards = "".join(
        f'<div class="qcard"><h3>{e(i["title"])}</h3><p>{e(i["body"])}</p></div>' for i in s["items"]
    )
    cta = ""
    if s.get("cta"):
        label, link = s["cta"]
        cta = (f'<a class="btn btn-on-dark" style="margin-top:26px" '
               f'href="{href(link, links)}" rel="noopener">{e(label)}</a>')
    left = []
    if s.get("eyebrow"):
        left.append(f'<div class="eyebrow">{e(s["eyebrow"])}</div>')
    left.append(f"<h2>{e(s['h2'])}</h2>")
    for p in s.get("body", []):
        left.append(f'<p style="margin-top:16px">{e(p)}</p>')
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
        sf, dp = PILLAR_ACCENTS[it["accent"]]
        rows = []
        for entry in it["list"]:
            label, slug, flag = (entry if len(entry) == 3 else (*entry, None))
            badge = f'<span class="flag">{e(flag)}</span>' if flag else ""
            rows.append(f'<li><a href="{href(slug, links)}">{label}</a>{badge}</li>')
        go_label, go_slug = it["go"]
        cards.append(
            f'<article class="pcard">'
            f'<div class="ptag" style="background:var(--{sf});color:var(--{dp})">'
            f"{n:02d}</div>"
            f'<h3>{e(it["title"])}</h3><p>{e(it["body"])}</p>'
            f'<ul>{"".join(rows)}</ul>'
            f'<a class="go" href="{href(go_slug, links)}" '
            f'style="color:var(--{dp})">{e(go_label)} →</a></article>'
        )
    return _headblock(s, links, a) + f'<div class="bento">{"".join(cards)}</div>'


def blk_quotes(s, links, a=''):
    """The social-proof band from home-v3: rating strip + verified Practo stories."""
    quotes = "".join(
        f'<div class="q"><p>“{e(text)}”</p><footer>{e(src)}</footer></div>'
        for text, src in s["items"]
    )
    return _headblock(s, links, a) + f"""<div class="rating">
      <span class="big">5.0</span>
      <span class="meta"><span class="stars">★★★★★</span><br>
        65 verified stories on Practo · 97% recommend ·
        <a href="{PRACTO_JH}" rel="noopener">Read them all →</a></span>
    </div>
    <div class="quotes">{quotes}</div>"""


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
        paras = "".join(f"<p>{e(p)}</p>" for p in (a if isinstance(a, list) else [a]))
        rows.append(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary>{paras}</details>')
    return f"""<section class="band paper" id="faq">
  <div class="wrap">
    <div class="faq">
      <div class="eyebrow">Questions patients actually ask</div>
      <h2 style="margin-top:10px">{e(page.get('faq_h2', 'Before you come in'))}</h2>
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
        f'<a href="{href(s, links)}"><h3>{e(t)}</h3><p>{e(b)}</p>'
        f'<div class="go">Read this →</div></a>' for s, t, b in page["related"]
    )
    return f"""<section class="band">
  <div class="wrap">
    <div class="head-block"><div class="eyebrow">Keep reading</div>
      <h2>{e(page.get('related_h2', 'Related on this site'))}</h2></div>
    <div class="cols related">{cards}</div>
  </div>
</section>"""


# ── schema.org ───────────────────────────────────────────────────────────────
CLINICS = [
    {
        "@type": "MedicalClinic",
        "name": "Dr. Varada's Skin & Hair Center — Jubilee Hills",
        "url": SITE + "/locations/jubilee-hills/",
        "address": {"@type": "PostalAddress", "addressLocality": "Jubilee Hills",
                    "addressRegion": "Telangana", "addressCountry": "IN",
                    "streetAddress": "TODO — street address, character-identical to GBP"},
        "telephone": "TODO — clinic number",
        "openingHours": "Mo-Sa 13:30-20:00",
    },
    {
        "@type": "MedicalClinic",
        "name": "Dr. Varada's Skin & Hair Center — West Marredpally",
        "url": SITE + "/locations/west-marredpally/",
        "address": {"@type": "PostalAddress", "addressLocality": "West Marredpally",
                    "addressRegion": "Telangana", "addressCountry": "IN",
                    "streetAddress": "TODO — street address, character-identical to GBP"},
        "telephone": "TODO — clinic number",
        "openingHours": "Mo-Sa 07:00-09:00",
    },
]

PHYSICIAN = {
    "@type": "Physician",
    "@id": SITE + "/about/dr-khagendra-varada/#physician",
    "name": "Dr. (Lt Col) Khagendra Varada",
    "medicalSpecialty": ["Dermatology", "Dermatologic Surgery"],
    "url": SITE + "/about/dr-khagendra-varada/",
    "alumniOf": "Osmania Medical College",
    "hasCredential": [
        "MBBS, Osmania Medical College",
        "Diploma in Practical Dermatology, Cardiff University, UK",
        "Diploma in Dermatology, AAAM",
    ],
    "memberOf": "Indian Medical Association",
    "worksFor": {"@type": "MedicalClinic", "name": BRAND_PLAIN, "url": SITE},
}


def schema(page: dict) -> str:
    url = SITE + URLS.get(page["slug"], "/")
    graph: list[dict] = []

    if page["slug"] == "index":
        graph.append({
            "@type": "MedicalClinic",
            "@id": SITE + "/#clinic",
            "name": BRAND_PLAIN,
            "alternateName": "BNR Skin & Vitiligo Hospital",
            "url": SITE,
            "description": page["meta"],
            "medicalSpecialty": ["Dermatology", "Dermatologic Surgery"],
            "areaServed": [{"@type": "City", "name": "Hyderabad"},
                           {"@type": "Country", "name": "India"}],
            "location": CLINICS,
            "sameAs": ["TODO — Practo profile URLs", "TODO — Google Business Profile"],
        })
        graph.append(PHYSICIAN)
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
            "lastReviewed": "2026-07-29",
            "reviewedBy": {"@id": PHYSICIAN["@id"]},
            "about": {"@type": "MedicalCondition", "name": page["condition"]}
            if page.get("condition") else None,
            "audience": {"@type": "Patient"},
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
