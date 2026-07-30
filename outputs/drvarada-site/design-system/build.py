"""Build the Open Design brand kit for Dr. Varada's Skin & Hair Center.

Shape mirrors a kit Open Design already renders correctly (`.od/design-systems/
fracktal-in`): cards reference siblings (`../colors_and_type.css`, `../logos/*.svg`)
rather than inlining them, which is what the daemon's artifact bundler expects and what
keeps each card a few KB instead of ninety.

  DESIGN.md                             entry / source of truth
  brand.json                            machine-readable brand record
  metadata.json                         title, category, status, artifactMode, provenance
  colors_and_type.css                   tokens + band/component classes + inlined faces
  guide.md, README.md
  logos/                                all 42 lockups and marks, plus the icon ladder
  preview/<name>.html                   a Design System card
  preview/<name>.html.artifact.json     its sidecar — without this it is not a card
  context/input-DESIGN.md

Everything derives from system/variables.css, so tokens, JSON and cards cannot drift
from the stylesheet the site actually loads.
"""
import json
import pathlib
import re
import shutil

HERE = pathlib.Path(__file__).resolve().parent
BRAND_DIR = HERE.parent / "brand"
CSS = (HERE / "system" / "variables.css").read_text(encoding="utf-8")
FONTS = (HERE / "system" / "fonts.css").read_text(encoding="utf-8").strip()
BRAND = json.loads((HERE / "brand.json").read_text(encoding="utf-8"))

KIT = HERE / "kit"

ROOT_BLOCK = re.search(r":root\s*\{(.*?)\n\}", CSS, re.S).group(1)
TOKENS = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", ROOT_BLOCK))
TOKENS = {k: " ".join(v.split()) for k, v in TOKENS.items()}

GROUPS = {
    "surface": ["--ground", "--paper", "--tint", "--dark"],
    "ink": ["--ink", "--ink-2", "--ink-3", "--on-dark", "--on-dark-str", "--dark-line"],
    "identity": ["--navy"],
    "accent": ["--mint", "--mint-dp", "--mint-sf", "--apricot", "--apr-dp", "--apr-sf",
               "--lilac", "--lil-dp", "--lil-sf", "--gold"],
    "line": ["--line", "--line-2", "--shadow"],
    "geometry": ["--r", "--r-sm", "--r-pill", "--unit", "--band-pad", "--wrap"],
    "type": ["--display", "--body", "--mono", "--t-hero", "--t-h2", "--t-h3",
             "--t-card", "--t-body", "--t-small", "--t-eyebrow"],
}

# ---------------------------------------------------------------- logo system

FORMS = [
    ("horizontal", "Horizontal", "3.3 : 1",
     "The default. Site header, letterhead, email signature, any wide strip.", 160),
    ("horizontal-tagline", "Horizontal + tagline", "2.7 : 1",
     "Same, where there is room to say what you do — ads, brochure covers, "
     "presentation title slides.", 260),
    ("stacked", "Stacked", "1.2 : 1",
     "Square-ish spaces: signage, a clinic board, a social post, a stamp.", 170),
    ("stacked-tagline", "Stacked + tagline", "1.1 : 1",
     "The fullest expression. Reception wall, brochure front, poster.", 260),
    ("wordmark", "Wordmark", "4.2 : 1",
     "Where the symbol already appears nearby, or is too small to survive.", 160),
    ("wordmark-tagline", "Wordmark + tagline", "3.3 : 1",
     "Document footers, certificates, anywhere the name must carry the tagline "
     "alone.", 260),
]

WAYS = [
    ("light", "Light", "#FFFFFF", "White or porcelain grounds. The primary."),
    ("dark", "Dark", "#1E3A63", "Navy, ink or photographic grounds. A considered "
     "re-step, not an inversion."),
    ("flat-navy", "Flat navy", "#EDF6F2", "One-colour brand navy: signage, embroidery, "
     "screen print, stamps."),
    ("mono-dark", "Mono ink", "#FFFFFF", "One colour ink: fax, forms, engraving, "
     "newspaper."),
    ("mono-light", "Mono white", "#12202F", "One-colour knockout: dark print, etched "
     "glass, merchandise."),
    ("adaptive", "Adaptive",
     "linear-gradient(90deg,#FFFFFF 0 50%,#12202F 50% 100%)",
     "Web only. Follows the viewer's colour scheme and honours data-theme."),
]

ICON_TIERS = [
    ("full", "128 px and up", 36, "7-tone ramp",
     "Every path of the source artwork, untouched"),
    ("compact", "44 – 96 px", 32, "3 tones",
     "Sub-pixel specks culled, ramp flattened, 3-unit dilation"),
    ("micro", "24 – 40 px", 14, "2 tones",
     "Field normalised to discs, follicle dilated 8 units"),
    ("nano", "16 – 20 px", 9, "2 tones",
     "Field normalised to discs, follicle dilated 10 units"),
]


def write_tokens(dest):
    out = {"$schema": "https://design-tokens.org/draft", "groups": {}}
    for group, names in GROUPS.items():
        out["groups"][group] = {n: TOKENS[n] for n in names if n in TOKENS}
    missing = set(TOKENS) - {n for names in GROUPS.values() for n in names}
    if missing:
        out["groups"]["ungrouped"] = {n: TOKENS[n] for n in sorted(missing)}
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return sum(len(v) for v in out["groups"].values())


# ---------------------------------------------------------------- card chrome

CHROME = """<!-- @dsCard group="{group}" -->
<title>{title}</title>
<link rel="stylesheet" href="../colors_and_type.css">
<style>
body {{ margin:0; padding:40px 34px 60px; background:var(--ground); }}
.sheet {{ max-width:1000px; margin:0 auto; }}
.sheet > header {{ margin-bottom:30px; }}
.sheet h1 {{ font-size:34px; }}
.sheet header p {{ margin-top:8px; }}
.grid {{ display:grid; gap:14px; margin-top:22px; }}
.sw {{ border:1px solid var(--line); border-radius:var(--r-sm); overflow:hidden;
      background:var(--paper); }}
.sw .chip {{ height:92px; }}
.sw .meta {{ padding:11px 14px; display:flex; flex-direction:column; gap:2px; }}
.sw .meta b {{ font:600 13.5px/1.3 var(--body); color:var(--ink); }}
.sw .meta code {{ font:500 12px/1.4 var(--mono); color:var(--ink-3); }}
.sw .meta span {{ font:400 12px/1.45 var(--body); color:var(--ink-3); }}
.note {{ margin-top:26px; padding:16px 20px; background:var(--paper);
        border:1px solid var(--line); border-left:3px solid var(--navy);
        border-radius:0 var(--r-sm) var(--r-sm) 0; }}
.note p {{ font-size:14.5px; max-width:80ch; }}
h2.sec {{ font-size:19px; margin:38px 0 4px; }}
h3.sub {{ font-size:15.5px; margin:26px 0 2px; font-family:var(--body);
         font-weight:700; letter-spacing:0; }}
.tablewrap {{ overflow-x:auto; margin-top:20px; }}
table {{ border-collapse:collapse; width:100%; font-size:14.5px; min-width:520px; }}
th {{ text-align:left; font:600 11px/1.3 var(--body); letter-spacing:.1em;
     text-transform:uppercase; color:var(--ink-2);
     border-bottom:2px solid var(--ink); padding:0 14px 9px 0; vertical-align:bottom; }}
td {{ border-bottom:1px solid var(--line); padding:10px 14px 10px 0;
     vertical-align:top; }}
td:last-child, th:last-child {{ padding-right:0; }}
.num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
.stage {{ display:flex; align-items:center; justify-content:center; padding:26px; }}
.stage img {{ width:100%; height:auto; display:block; }}
.yes b, .no b {{ font:600 11px/1 var(--body); letter-spacing:.1em;
                text-transform:uppercase; }}
.yes b {{ color:var(--mint-dp); }}
.no b {{ color:#9A5320; }}
</style>
<div class="sheet">
<header>
  <div class="eyebrow">{eyebrow}</div>
  <h1>{title}</h1>
  <p>{lede}</p>
</header>
{body}
</div>
"""

SIDECAR = {
    "version": 1, "kind": "html", "renderer": "html", "status": "complete",
    "exports": ["html", "pdf", "zip"],
    "metadata": {"inferred": False, "reconciled": True},
}

CARDS = []


def page(name, group, eyebrow, title, lede, body):
    html = CHROME.format(group=group, title=title, eyebrow=eyebrow, lede=lede, body=body)
    p = KIT / "preview" / name
    p.write_text(html, encoding="utf-8")
    side = dict(SIDECAR, title=f"preview/{name}", entry=f"preview/{name}")
    (KIT / "preview" / f"{name}.artifact.json").write_text(
        json.dumps(side, indent=2) + "\n", encoding="utf-8")
    CARDS.append((name, group, title))
    return p


def table(headers, rows, cls=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="tablewrap"><table class="{cls}"><tr>{head}</tr>'
            f'{body}</table></div>')


def swatches(rows, cols="repeat(auto-fit,minmax(190px,1fr))"):
    cells = "".join(
        f'<div class="sw"><div class="chip" style="background:{val}"></div>'
        f'<div class="meta"><b>{label}</b><code>{token}</code>'
        f'<span>{use}</span></div></div>'
        for label, token, val, use in rows)
    return f'<div class="grid" style="grid-template-columns:{cols}">{cells}</div>'


# ---------------------------------------------------------------- brand cards

def build_logo_matrix():
    """Every lockup form in every colourway — the full 36, plus the 6 symbol-only."""
    sections = []
    for form, label, ratio, _use, _min in FORMS:
        cells = "".join(
            f'<div class="sw"><div class="stage" style="background:{bg}">'
            f'<img src="../logos/logo-{form}-{way}.svg" alt="{label}, {name}">'
            f'</div><div class="meta"><b>{name}</b>'
            f'<code>logo-{form}-{way}.svg</code></div></div>'
            for way, name, bg, _d in WAYS)
        sections.append(
            f'<h2 class="sec">{label}</h2>'
            f'<p style="font-size:13.5px">{ratio}</p>'
            f'<div class="grid" style="grid-template-columns:'
            f'repeat(auto-fit,minmax(240px,1fr))">{cells}</div>')

    marks = "".join(
        f'<div class="sw"><div class="stage" style="background:{bg}">'
        f'<div style="width:74px"><img src="../logos/logo-mark-{way}.svg" '
        f'alt="Symbol, {name}"></div></div>'
        f'<div class="meta"><b>{name}</b><code>logo-mark-{way}.svg</code></div></div>'
        for way, name, bg, _d in WAYS)

    body = ("".join(sections)
            + '<h2 class="sec">Symbol only</h2>'
            '<p style="font-size:13.5px">No wordmark. Use where the name already '
            'appears nearby — a watermark, a section divider, the corner of a '
            'document.</p>'
            f'<div class="grid" style="grid-template-columns:'
            f'repeat(auto-fit,minmax(150px,1fr))">{marks}</div>'
            '<div class="note"><p><b>42 files in total</b> — six lockup forms across six '
            'colourways, plus the symbol in the same six. Every letterform is outlined, '
            'so the artwork carries no font dependency and renders identically on a '
            'machine that has never seen Gabarito or Manrope.</p></div>'
            '<div class="note"><p>The <b>adaptive</b> cells sit on a split ground '
            'on purpose. An adaptive SVG resolves against the <b>viewer&rsquo;s '
            'colour scheme</b>, not the surface behind it, so referenced through an '
            '<code>&lt;img&gt;</code> it can land light-on-light. Inline it in the '
            'page — where <code>data-theme</code> reaches it — or pick the fixed '
            '<code>-light</code> / <code>-dark</code> file instead.</p></div>')
    return page("brand-logo-matrix.html", "Brand", "Logo", "Every lockup",
                "Six forms × six colourways, plus the symbol on its own.", body)


def build_logo_usage():
    """The decision tables — which form, which colourway, how small, how much air."""
    form_rows = [
        (f'<code>logo-{f}-*</code>', f'<b>{label}</b>', f'<span class="num">{ratio}</span>',
         use, f'<span class="num">{mn} px</span>')
        for f, label, ratio, use, mn in FORMS]
    way_rows = [
        (f'<code>*-{w}</code>', f'<b>{name}</b>', desc) for w, name, _bg, desc in WAYS]

    place_rows = [
        ("Website header", "<code>horizontal</code> or <code>adaptive</code>",
         "46 px tall — the symbol alone is not enough for brand recall"),
        ("Letterhead / email signature", "<code>horizontal</code>", "Light ground"),
        ("Brochure cover, ad, title slide", "<code>horizontal-tagline</code>",
         "Room for the promise"),
        ("Clinic signage / board", "<code>stacked</code> or <code>flat-navy</code>",
         "One colour survives vinyl and paint"),
        ("Reception wall, poster", "<code>stacked-tagline</code>", "The fullest form"),
        ("Certificate, document footer", "<code>wordmark-tagline</code>",
         "The symbol would compete with the seal"),
        ("Favicon, app icon, avatar", "<b>icon tier</b> — never a lockup",
         "See the icon ladder card"),
        ("Practo / Google / social avatar", "<code>profile-512.png</code>",
         "Compact tier — built for a 48 px display, not a 512 px file"),
        ("Embroidery, stamp, screen print", "<code>*-flat-navy</code>",
         "The grey ramp cannot reproduce"),
        ("Watermark on a document", "<code>logo-mark-mono-*</code>",
         "Symbol only, one colour"),
    ]

    body = ('<h2 class="sec">Which form</h2>'
            + table(["File", "Form", "Ratio", "Use it for", "Min width"], form_rows)
            + '<h2 class="sec">Which colourway</h2>'
            + table(["Suffix", "Name", "When"], way_rows)
            + '<h2 class="sec">Which one goes where</h2>'
            + table(["Destination", "Use", "Why"], place_rows)
            + '<h2 class="sec">Clear space</h2>'
            '<p style="margin-top:10px">Keep clear on all four sides by the <b>cap '
            'height of the &ldquo;D&rdquo; in &ldquo;Dr.&rdquo;</b> Nothing sits inside '
            'that margin. Each file already carries about a third of it inside its own '
            'viewBox, so the logo never sits flush against its container even when '
            'placed carelessly.</p>'
            '<div class="note"><p>Minimum widths were measured by rendering and reading, '
            'not by rule of thumb. Below them the descriptor&rsquo;s letterspacing closes '
            'up and the tagline breaks into grey noise. <b>Below a tagline form&rsquo;s '
            'floor, drop to the form without a tagline</b> rather than shrinking '
            'further.</p></div>'
            '<div class="note"><p>The wordmark is set in the brand&rsquo;s own faces — '
            'Gabarito for the name, Manrope for the descriptor and tagline — the same '
            'pairing the website uses, so the logo and the site speak in one '
            'voice.</p></div>')
    return page("brand-logo-usage.html", "Brand", "Logo", "When to use what",
                "Three decisions: which form, which colourway, and how small it may go.",
                body)


def build_logo_misuse():
    dont = [
        ("Re-set the type", "The outlines exist precisely so nobody needs the fonts. "
         "Live text renders differently on every machine."),
        ("Restack or re-space the lines", "Six forms already exist. Use the one that "
         "fits the space."),
        ("Recolour outside the six colourways", "Including tinting the symbol to match "
         "a campaign."),
        ("Stretch or squash", "Always scale both dimensions together."),
        ("Put <code>-light</code> on a dark ground", "There is a <code>-dark</code> "
         "file for that, and it is a re-step rather than an inversion."),
        ("Add shadows, outlines, gradients or bevels", "The mark carries its own "
         "depth through the cell ramp."),
        ("Use a lockup as an avatar", "It becomes illegible in a circular crop. The "
         "icon ladder exists for this."),
        ("Rotate, or set on a busy photograph", "If a photo is unavoidable, use "
         "<code>-mono-light</code> over a darkened area."),
    ]
    rows = [(f'<span class="no"><b>Don\'t</b></span> {what}', why) for what, why in dont]
    body = (table(["Never", "Why"], rows)
            + '<div class="note"><p>The one rule that catches most mistakes: <b>if you '
            'are about to modify the artwork, the answer is a different file, not an '
            'edit.</b> Forty-two permutations exist so nobody has to improvise.</p></div>')
    return page("brand-logo-misuse.html", "Brand", "Logo", "Misuse",
                "What not to do, and the file to reach for instead.", body)


def build_icons():
    ladder = "".join(
        f'<div style="text-align:center"><div style="width:{px}px">'
        f'<img src="../logos/icon-{tier}-navy.svg" alt="{tier} at {px}px"></div>'
        f'<div class="eyebrow" style="margin-top:10px">{px} px</div>'
        f'<div style="font:500 10.5px var(--mono);color:var(--ink-3);margin-top:4px">'
        f'{tier}</div></div>'
        for tier, px in (("nano", 16), ("nano", 20), ("micro", 24), ("micro", 32),
                         ("micro", 40), ("compact", 48), ("compact", 64),
                         ("compact", 96), ("full", 128)))

    tier_rows = [(f'<code>{t}</code>', f'<span class="num">{band}</span>',
                  f'<span class="num">{n}</span>', tones, how)
                 for t, band, n, tones, how in ICON_TIERS]

    platform_rows = [
        ("Practo profile photo", "<code>profile-512.png</code>", "compact", "~64 px"),
        ("Google Business Profile", "<code>profile-512.png</code>", "compact",
         "40 – 120 px"),
        ("Instagram &amp; Facebook", "<code>profile-512.png</code>", "compact",
         "32 – 110 px"),
        ("WhatsApp Business", "<code>profile-512.png</code>", "compact", "48 px"),
        ("Browser tab", "<code>favicon.svg</code> + <code>favicon.ico</code>",
         "compact / nano + micro", "16 – 20 px"),
        ("iOS home screen", "<code>apple-touch-icon.png</code>", "compact, hard square",
         "60 – 180 px"),
        ("Android / PWA", "<code>icon-192.png</code>, <code>icon-512.png</code>",
         "compact / full", "48 – 192 px"),
    ]

    body = (f'<div style="display:flex;gap:24px;align-items:flex-end;flex-wrap:wrap;'
            f'background:var(--paper);border:1px solid var(--line);'
            f'border-radius:var(--r-sm);padding:30px 26px 22px;margin-top:20px">'
            f'{ladder}</div>'
            '<div class="note"><p><b>Pick the tier by the size the icon is displayed at, '
            'not the size of the file you upload.</b> Practo, Google, Instagram and '
            'WhatsApp all ask for a 512 px upload, then show it at 40–96 px through '
            'their own downscaler. Hand them the full mark and that downscaler mashes '
            'the 34-element field into grey.</p></div>'
            '<h2 class="sec">How each tier is made</h2>'
            + table(["Tier", "Display size", "Elements", "Colour", "Construction"],
                    tier_rows)
            + '<p style="margin-top:20px">Two techniques do the work. <b>Dilation</b> '
            'strokes each path in its own fill colour — without it a 23-unit dot renders '
            'at half a pixel and disappears. <b>Disc normalisation</b> applies below '
            'roughly 40 px, where irregular outlines anti-alias into grey mush; equal '
            'discs at each element&rsquo;s own centroid land cleanly on the pixel '
            'grid.</p>'
            '<h2 class="sec">Which file goes where</h2>'
            + table(["Destination", "Upload", "Built from", "Shown at"], platform_rows)
            + '<div class="note"><p><code>favicon.ico</code> holds three separately '
            'rendered images — 16 px from nano, 32 and 48 from micro — rather than one '
            'image resampled three times. It must sit at the site root: some crawlers '
            'request <code>/favicon.ico</code> directly and ignore the '
            '<code>&lt;link&gt;</code>.</p></div>')
    return page("brand-icons.html", "Brand", "Icons", "Icon ladder",
                "One mark, four tiers. The icon is never a reduced symbol.", body)


# ---------------------------------------------------------------- foundations

def build_colors_primary():
    surfaces = [
        ("Ground", "--ground", TOKENS["--ground"], "Default page surface"),
        ("Paper", "--paper", TOKENS["--paper"], "Cards, white bands"),
        ("Tint", "--tint", TOKENS["--tint"], "Process and reassurance bands"),
        ("Dark", "--dark", TOKENS["--dark"], "Punctuation bands only"),
    ]
    accents = []
    for label, base, deep, soft in (("Mint", "--mint", "--mint-dp", "--mint-sf"),
                                    ("Apricot", "--apricot", "--apr-dp", "--apr-sf"),
                                    ("Lilac", "--lilac", "--lil-dp", "--lil-sf")):
        accents += [
            (label, base, TOKENS[base], "Fills, CTA bands"),
            (f"{label} deep", deep, TOKENS[deep], "Text on the soft variant"),
            (f"{label} soft", soft, TOKENS[soft], "Tinted card fills"),
        ]
    body = ('<h2 class="sec">Surfaces</h2>' + swatches(surfaces)
            + '<h2 class="sec">Accents</h2>'
            + swatches(accents, "repeat(auto-fit,minmax(160px,1fr))")
            + '<div class="note"><p>Accent colour belongs to the <b>category</b>, not the '
            'instance: mint for chronic conditions, apricot for aesthetics, lilac for '
            'trichology. A designer never picks the accent — the content type does.'
            '</p></div>'
            '<div class="note"><p>Never set body copy in a pastel. Each accent carries a '
            '<b>deep</b> pair for text and a <b>soft</b> pair for fills; use them as a '
            'pair, never the base alone behind words.</p></div>')
    return page("colors-primary.html", "Colors", "Palette", "Primary colour",
                "Four surfaces the page alternates between, and three accent families.",
                body)


def build_colors_neutrals():
    inks = [
        ("Ink", "--ink", TOKENS["--ink"], "Body and headings on light"),
        ("Ink 2", "--ink-2", TOKENS["--ink-2"], "Secondary text, descriptions"),
        ("Ink 3", "--ink-3", TOKENS["--ink-3"], "Metadata, captions, eyebrows"),
        ("Navy", "--navy", TOKENS["--navy"], "Identity only — logo, icons, print"),
    ]
    ondark = [
        ("On dark", "--on-dark", "rgba(240,245,248,.76)", "Body text on a dark band"),
        ("On dark strong", "--on-dark-str", "#FFFFFF", "Headings on a dark band"),
        ("Dark line", "--dark-line", "rgba(255,255,255,.14)", "Hairlines on dark"),
    ]
    body = ('<h2 class="sec">Ink &amp; identity</h2>' + swatches(inks)
            + '<h2 class="sec">On dark bands</h2>'
            '<div class="band on-dark" style="border-radius:var(--r-sm);padding:22px;'
            'margin-top:14px">' + swatches(ondark) + '</div>'
            '<div class="note"><p><b>Navy versus ink is deliberate.</b> '
            '<code>--navy</code> <code>#1E3A63</code> is the identity colour and belongs '
            'to the logo, the icon tiles and anything printed. <code>--ink</code> '
            '<code>#12202F</code> is the interface colour: text, dark bands, footer. '
            'They are close on purpose and do different jobs — do not unify them.'
            '</p></div>')
    return page("colors-neutrals.html", "Colors", "Palette", "Neutrals",
                "Three inks on light, three on dark, and the one identity navy.", body)


def build_typography():
    rows = [
        ("Hero", "--t-hero", "var(--display)", 600, "One per page. Tracking −.03em"),
        ("Section head", "--t-h2", "var(--display)", 600, "text-wrap: balance"),
        ("Sub head", "--t-h3", "var(--display)", 600, ""),
        ("Card title", "--t-card", "var(--display)", 600, ""),
        ("Body", "--t-body", "var(--body)", 400, "Cap running text near 65 characters"),
        ("Small", "--t-small", "var(--body)", 400, "Captions, footnotes"),
    ]
    specimens = "".join(
        f'<div style="border-top:1px solid var(--line);padding:22px 0">'
        f'<div class="eyebrow">{label} &middot; {TOKENS[tok]} &middot; {wt}</div>'
        f'<div style="font-family:{fam};font-weight:{wt};font-size:{TOKENS[tok]};'
        f'letter-spacing:-.03em;line-height:1.1;margin-top:10px">'
        f'Vitiligo &amp; psoriasis care</div>'
        + (f'<p style="margin-top:8px;font-size:13.5px">{note}</p>' if note else '')
        + '</div>'
        for label, tok, fam, wt, note in rows)
    body = (specimens
            + '<h2 class="sec">Eyebrow &amp; statistic</h2>'
            '<div style="display:flex;gap:44px;flex-wrap:wrap;margin-top:16px;'
            'align-items:flex-end">'
            '<div><div class="eyebrow">Trichology</div>'
            '<p style="font-size:13px;margin-top:8px">12px, .14em, uppercase</p></div>'
            '<div><div class="stat" style="font-size:62px">45</div>'
            '<p style="font-size:13px;margin-top:8px">Tabular numerals, always</p></div>'
            '</div>'
            '<div class="note"><p>Headings sit at <b>600, not 700</b>. At display sizes '
            'Gabarito&rsquo;s 700 turns shouty, which is the wrong register for a medical '
            'practice. Gabarito carries every heading, statistic and label; Manrope '
            'carries every sentence a patient actually reads.</p></div>')
    return page("typography-specimens.html", "Type", "Typography", "Typography",
                "Gabarito for display, Manrope for text. One scale, no improvisation.",
                body)


def build_spacing():
    scale = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
    bars = "".join(
        f'<div style="display:flex;align-items:center;gap:14px;padding:5px 0">'
        f'<code style="min-width:64px">{n * 4}px</code>'
        f'<div style="height:14px;width:{n * 4}px;background:var(--mint);'
        f'border-radius:3px"></div>'
        f'<span style="font-size:12.5px;color:var(--ink-3)">{n} &times; unit</span></div>'
        for n in scale)
    rows = [("<code>--unit</code>", TOKENS["--unit"],
             "Base unit — every gap and pad is a multiple of it"),
            ("<code>--band-pad</code>", TOKENS["--band-pad"],
             "Vertical padding on every section band"),
            ("<code>--wrap</code>", TOKENS["--wrap"], "Maximum content width")]
    body = (f'<div style="margin-top:18px">{bars}</div>'
            + table(["Token", "Value", "Applies to"], rows)
            + '<div class="note"><p>Lay out sibling groups with flex or grid '
            '<code>gap</code>, not per-element margins that silently collapse or double. '
            'Wide content — tables, code — scrolls inside its own container so the page '
            'body never scrolls sideways.</p></div>')
    return page("spacing-tokens.html", "Spacing", "Spacing", "Spacing",
                "A 4px base unit. Everything is a multiple of it.", body)


def build_radius():
    shapes = "".join(
        f'<div style="text-align:center"><div style="width:112px;height:84px;'
        f'background:var(--mint-sf);border:1px solid var(--line);'
        f'border-radius:{TOKENS[t]}"></div>'
        f'<div class="eyebrow" style="margin-top:10px">{n}</div></div>'
        for n, t in (("Card 26px", "--r"), ("Small 14px", "--r-sm"),
                     ("Pill", "--r-pill")))
    body = (f'<div style="display:flex;gap:26px;flex-wrap:wrap;margin-top:20px">'
            f'{shapes}</div>'
            '<h2 class="sec">Elevation</h2>'
            '<div class="grid" style="grid-template-columns:'
            'repeat(auto-fit,minmax(230px,1fr))">'
            '<div class="card"><b style="font:600 14px var(--body)">Hairline</b>'
            '<p style="margin-top:6px;font-size:13.5px">The default. Border, no '
            'shadow.</p></div>'
            '<div class="card lifted"><b style="font:600 14px var(--body)">Lifted</b>'
            '<p style="margin-top:6px;font-size:13.5px">One shadow token, used '
            'sparingly.</p></div></div>'
            '<div class="note"><p>There is exactly one shadow. Depth comes from the band '
            'rhythm, not from stacking elevations.</p></div>')
    return page("radius-shadows.html", "Spacing", "Geometry", "Radius &amp; elevation",
                "Three radii and a single shadow.", body)


# ---------------------------------------------------------------- layout

def build_bands():
    order = [("band", "Ground", "the resting state"),
             ("band paper", "Paper", "where cards need to lift"),
             ("band tinted", "Tint", "process, reassurance"),
             ("band on-dark", "Dark", "punctuation only")]
    strips = "".join(
        f'<div class="{cls}" style="padding:36px 30px;border-radius:var(--r-sm);'
        f'margin-top:12px">'
        f'<div class="eyebrow">{name}</div>'
        f'<h3 style="margin-top:8px">A section sits here</h3>'
        f'<p style="margin-top:6px{";color:var(--on-dark)" if "on-dark" in cls else ""}">'
        f'Used for {use}.</p></div>'
        for cls, name, use in order)
    body = (strips
            + '<h2 class="sec">The order a page runs in</h2>'
            + table(["#", "Band", "Section"], [
                ("1", "<code>dark</code>", "Utility bar — hours, both clinics, rating"),
                ("2", "<code>ground</code>", "Hero"),
                ("3", "<code>paper</code>", "Symptom finder — &ldquo;what brings you "
                 "in?&rdquo;"),
                ("4", "<code>ground</code>", "Service pillars"),
                ("5", "<code>dark</code>", "Specialty spotlight — vitiligo &amp; "
                 "psoriasis"),
                ("6", "<code>paper</code>", "Results"),
                ("7", "<code>tint</code>", "How it works"),
                ("8", "<code>ground</code>", "The doctor"),
                ("9", "<code>paper</code>", "Locations, stories, FAQ"),
                ("10", "<code>mint</code>", "Booking CTA"),
                ("11", "<code>dark</code>", "Footer"),
            ])
            + '<div class="note"><p>The page is <b>light-committed</b>. Healthcare and '
            'skincare audiences expect light grounds, and clinical before/after '
            'photography only reads truthfully on light. Dark is <b>punctuation, not a '
            'theme</b>: three per page is the ceiling.</p></div>'
            '<div class="note"><p>Never place two dark bands adjacent, and never open a '
            'page on a dark band other than the utility bar.</p></div>')
    return page("layout-bands.html", "Layout", "Rhythm", "Band rhythm",
                "Sections alternate between four surfaces so a long page has a pulse.",
                body)


def build_grid():
    rows = [
        ("Mobile", "&lt; 640 px", "1 column", "Mobile dock appears below 720 px"),
        ("Tablet", "640 – 960 px", "2 columns", "Bento collapses to pairs"),
        ("Desktop", "&gt; 960 px", "3 – 4 columns",
         f'Content caps at <code>{TOKENS["--wrap"]}</code>'),
    ]
    cols = "".join(
        '<div style="background:var(--mint-sf);border-radius:6px;height:120px"></div>'
        for _ in range(12))
    body = (f'<div style="display:grid;grid-template-columns:repeat(12,1fr);gap:12px;'
            f'margin-top:20px;background:var(--paper);border:1px solid var(--line);'
            f'border-radius:var(--r-sm);padding:22px">{cols}</div>'
            '<p style="margin-top:12px;font-size:13.5px">Twelve columns, 12 px gutters, '
            f'capped at <code>{TOKENS["--wrap"]}</code> with 22 px side padding.</p>'
            + table(["Breakpoint", "Width", "Columns", "Notes"], rows)
            + '<div class="note"><p>Grids are declared with <code>auto-fit</code> and '
            '<code>minmax()</code> rather than fixed column counts, so a bento reflows '
            'without a breakpoint for every arrangement.</p></div>')
    return page("layout-grid.html", "Layout", "Grid", "Grid &amp; breakpoints",
                "Twelve columns, three breakpoints, one maximum width.", body)


# ---------------------------------------------------------------- components

def build_buttons():
    body = """
<h2 class="sec">Buttons</h2>
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:16px;align-items:center">
  <a class="btn btn-primary" href="#">Book on Practo</a>
  <a class="btn btn-secondary" href="#">See treatments</a>
</div>
<div class="band on-dark" style="padding:26px 24px;border-radius:var(--r-sm);
     margin-top:16px">
  <a class="btn btn-on-dark" href="#">Book on Practo</a>
</div>
<div class="note"><p>The primary button <b>always</b> goes to Practo. The clinic team
already runs on Practo, so a parallel booking form would split the queue and break their
workflow. Phone and WhatsApp sit below it, never beside it as an equal choice. Label the
destination &mdash; never &ldquo;Submit&rdquo;.</p></div>

<h2 class="sec">Hierarchy</h2>
<p style="margin-top:10px">One primary button per view. If two actions look equally
important, the page has not decided what it wants the patient to do.</p>
"""
    return page("components-buttons.html", "Components", "Components", "Buttons",
                "Two levels, one destination.", body)


def build_cards():
    body = """
<h2 class="sec">Category cards</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(230px,1fr))">
  <div class="card chronic"><div class="eyebrow">Chronic</div>
    <h3 style="margin-top:8px">Vitiligo</h3>
    <p style="margin-top:6px;font-size:14.5px">Repigmentation, phototherapy,
    grafting.</p></div>
  <div class="card aesthetic"><div class="eyebrow">Aesthetics</div>
    <h3 style="margin-top:8px">Skin boosters</h3>
    <p style="margin-top:6px;font-size:14.5px">Bespoke topical and peel
    protocols.</p></div>
  <div class="card trichology"><div class="eyebrow">Trichology</div>
    <h3 style="margin-top:8px">Pattern hair loss</h3>
    <p style="margin-top:6px;font-size:14.5px">Diagnosis first, then a plan.</p></div>
</div>
<div class="note"><p>Card colour is decided by the content type, not by the
designer.</p></div>

<h2 class="sec">Statistic block</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(170px,1fr))">
  <div class="card"><div class="stat" style="font-size:44px">45</div>
    <p style="margin-top:6px;font-size:13.5px">years in practice</p></div>
  <div class="card"><div class="stat" style="font-size:44px">25</div>
    <p style="margin-top:6px;font-size:13.5px">in the Army Medical Corps</p></div>
  <div class="card"><div class="stat" style="font-size:44px">65</div>
    <p style="margin-top:6px;font-size:13.5px">patient stories on Practo</p></div>
</div>
<div class="note"><p>Every number must be attributable. &ldquo;45 years in practice&rdquo;
is verifiable; &ldquo;thousands of happy patients&rdquo; is not &mdash; do not write
it.</p></div>
"""
    return page("components-cards.html", "Components", "Components", "Cards",
                "Category cards, statistics, and the rule behind both.", body)


def build_forms():
    chips = "".join(
        f'<a href="#" style="display:inline-flex;align-items:center;gap:9px;'
        f'background:var(--paper);border:1px solid var(--line);'
        f'border-radius:var(--r-pill);padding:12px 18px;text-decoration:none;'
        f'color:var(--ink);font:500 14.5px var(--body)">'
        f'<span style="width:8px;height:8px;border-radius:50%;background:var({dot})">'
        f'</span>{label} &rarr;</a>'
        for label, dot in (("White patches on skin", "--mint"),
                           ("Red, scaly, flaking patches", "--mint"),
                           ("Hair falling more than usual", "--lilac"),
                           ("Patchy bald spots", "--lilac"),
                           ("Fine lines &amp; laxity", "--apricot"),
                           ("Unwanted hair", "--apricot")))
    body = (f'<h2 class="sec">Symptom finder</h2>'
            f'<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:16px">'
            f'{chips}</div>'
            '<div class="note"><p>Chips, not a dropdown. A patient recognises '
            '&ldquo;patchy white skin&rdquo; and does not yet recognise '
            '&ldquo;vitiligo&rdquo; &mdash; so the entry point is written in their words '
            'and the dot carries the category colour.</p></div>'
            '<h2 class="sec">Inputs</h2>'
            '<p style="margin-top:10px">The site collects <b>no patient data</b>. There '
            'are no booking forms, no contact forms and no newsletter capture: booking '
            'is Practo, and everything else is a phone number. That is a deliberate '
            'reduction in liability as much as in friction &mdash; health data collected '
            'on a marketing site is a burden nobody needs.</p>'
            '<div class="note"><p>If a form is ever genuinely required, it gets its own '
            'review. Do not add one to a page because a template has a slot for '
            'it.</p></div>')
    return page("components-forms.html", "Components", "Components", "Entry points",
                "How a patient starts — and why there are no forms.", body)


def build_navigation():
    body = """
<h2 class="sec">Utility bar</h2>
<div class="band on-dark" style="padding:12px 20px;border-radius:var(--r-sm);
     margin-top:14px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;
     font-size:13px">
  <span>Jubilee Hills &middot; Mon–Sat 1:30–8 pm &nbsp;|&nbsp; West Marredpally &middot;
  Mon–Sat 7–9 am</span>
  <span>&#9733; 5.0 on Practo — 65 patient stories &rarr;</span>
</div>

<h2 class="sec">Header</h2>
<div style="background:var(--paper);border:1px solid var(--line);
     border-radius:var(--r-sm);padding:16px 20px;margin-top:14px;display:flex;
     align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap">
  <div style="width:190px"><img src="../logos/logo-horizontal-light.svg"
       alt="Dr. Varada's Skin & Hair Center" style="width:100%;height:auto;display:block">
  </div>
  <a class="btn btn-primary" href="#">Book on Practo</a>
</div>
<div class="note"><p>The header carries the <b>horizontal lockup</b>, not the symbol
alone &mdash; a mark without the name earns no brand recall on a first visit. It sits at
46 px tall.</p></div>

<h2 class="sec">Mobile dock</h2>
<div style="background:var(--paper);border:1px solid var(--line);
     border-radius:var(--r-pill);padding:10px 12px;margin-top:14px;display:flex;gap:10px;
     max-width:420px">
  <a class="btn btn-primary" href="#" style="flex:1;justify-content:center">Book</a>
  <a class="btn btn-secondary" href="#" style="flex:1;justify-content:center">Call</a>
</div>
<div class="note"><p>Fixed to the bottom below 720 px. Two actions only. It appears after
the hero scrolls out, never over it.</p></div>
"""
    return page("components-navigation.html", "Components", "Components", "Navigation",
                "Utility bar, header and the mobile dock.", body)


# ---------------------------------------------------------------- practice

def build_voice():
    ok = [
        ("&ldquo;Vitiligo, psoriasis, acne, hair loss and modern aesthetics&rdquo;",
         "Names the conditions a patient searches for"),
        ("&ldquo;45 years — 25 of them in the Army Medical Corps&rdquo;",
         "Verifiable, specific, and it earns trust without adjectives"),
        ("&ldquo;You don't need to know the name of the condition&rdquo;",
         "Meets the patient where they are"),
    ]
    bad = [
        ("&ldquo;Best dermatologist in Hyderabad&rdquo;",
         "Superlative — prohibited by IMC advertising rules"),
        ("&ldquo;Permanent cure for vitiligo&rdquo;",
         "Cure claim, and clinically untrue"),
        ("&ldquo;Thousands of happy patients&rdquo;",
         "Unattributable number"),
        ("&ldquo;Painless, guaranteed results&rdquo;",
         "Guarantee — prohibited, and no procedure can promise it"),
    ]
    body = ('<h2 class="sec">Write like this</h2>'
            + table(["Line", "Why it works"],
                    [(f'<span class="yes"><b>Yes</b></span> {a}', b) for a, b in ok])
            + '<h2 class="sec">Never write this</h2>'
            + table(["Line", "Why it fails"],
                    [(f'<span class="no"><b>No</b></span> {a}', b) for a, b in bad])
            + '<div class="note"><p>Write the way a senior consultant speaks in a '
            'consulting room: short declarative sentences, no hedging, no hype. Lead with '
            'the patient&rsquo;s own words — someone searches &ldquo;white patches on '
            'skin&rdquo;, not &ldquo;vitiligo management protocol&rdquo;.</p></div>'
            '<div class="note"><p><b>Indian Medical Council advertising rules bind every '
            'page.</b> No cure claims, no guarantees, no superlatives, no comparison to a '
            'named competitor. This is not a style preference — it is the condition of '
            'the practice advertising at all.</p></div>')
    return page("content-voice.html", "Content", "Voice", "Voice &amp; compliance",
                "How the practice sounds, and the lines it may not cross.", body)


def build_imagery():
    body = """
<h2 class="sec">Clinical photography</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">
  <div class="card" style="background:var(--mint-sf)">
    <div class="eyebrow" style="color:var(--mint-dp)">Required</div>
    <p style="margin-top:8px;font-size:14.5px">Written patient consent, on file, before
    any before/after image is published.</p></div>
  <div class="card" style="background:var(--mint-sf)">
    <div class="eyebrow" style="color:var(--mint-dp)">Required</div>
    <p style="margin-top:8px;font-size:14.5px">Same lighting, same distance, same angle.
    A flattering angle is a misleading result.</p></div>
  <div class="card" style="background:var(--apr-sf)">
    <div class="eyebrow" style="color:var(--apr-dp)">Required</div>
    <p style="margin-top:8px;font-size:14.5px">State the interval and that results
    vary. Never imply a typical outcome.</p></div>
</div>
<div class="note"><p>This is the reason the site is <b>light-committed</b>. Clinical
photography only reads truthfully on a light ground; a dark surround shifts perceived
skin tone and quietly flatters the result.</p></div>

<h2 class="sec">Portraits &amp; clinic</h2>
<p style="margin-top:10px">Natural light, real rooms, no stock. The doctor photographed
at eye level, unhurried. If an asset does not exist yet, ship a labelled placeholder
rather than a stock substitute &mdash; a stock clinic reads as a stock clinic.</p>
<div class="note"><p>Outstanding: a portrait of Dr. Varada, and consented before/after
sets for vitiligo and psoriasis.</p></div>
"""
    return page("imagery.html", "Content", "Imagery", "Imagery",
                "What may be photographed, and what must be true about it.", body)


def build_accessibility():
    pairs = [
        ("Ink on ground", "#12202F", "#F8F5F3", "15.8", "AAA"),
        ("Ink 2 on ground", "#53616D", "#F8F5F3", "6.4", "AA"),
        ("Ink 3 on paper", "#7C8794", "#FFFFFF", "4.0", "AA large only"),
        ("Mint deep on mint soft", "#0B6353", "#DFF3EC", "7.4", "AAA"),
        ("Apricot deep on apricot soft", "#9A5320", "#FCEBDD", "5.9", "AA"),
        ("Lilac deep on lilac soft", "#514697", "#EAE7F8", "7.1", "AAA"),
        ("On-dark on dark", "rgba(240,245,248,.76)", "#12202F", "9.8", "AAA"),
    ]
    rows = [(f'<b>{n}</b>',
             f'<span class="sw" style="display:inline-block;width:14px;height:14px;'
             f'border-radius:4px;vertical-align:-2px;margin-right:7px;'
             f'background:{fg}"></span><code>{fg}</code>',
             f'<span class="sw" style="display:inline-block;width:14px;height:14px;'
             f'border-radius:4px;vertical-align:-2px;margin-right:7px;'
             f'border:1px solid var(--line);background:{bg}"></span><code>{bg}</code>',
             f'<span class="num">{ratio}:1</span>', f'<b>{lvl}</b>')
            for n, fg, bg, ratio, lvl in pairs]
    body = (table(["Pair", "Foreground", "Background", "Contrast", "WCAG"], rows)
            + '<div class="note"><p><code>--ink-3</code> is the one token that does not '
            'clear AA at body size. It is for eyebrows, captions and metadata — set at '
            '12–14 px <b>semibold or uppercase</b>, never for a sentence someone has to '
            'read.</p></div>'
            '<h2 class="sec">Focus &amp; motion</h2>'
            '<p style="margin-top:10px">Every interactive element takes a visible focus '
            'ring: <code>2px solid var(--mint-dp)</code> at <code>3px</code> offset. The '
            'ticker, the canvas field and every transition stop under '
            '<code>prefers-reduced-motion</code>.</p>'
            '<div class="note"><p>Tap targets are 44 px minimum — which is why '
            '<code>--controlHeight</code> is 44 and buttons pad to 15 px vertical. '
            'Patients using this site are frequently older.</p></div>')
    return page("accessibility.html", "Content", "Access", "Accessibility",
                "Measured contrast pairs, focus, motion and tap targets.", body)


# ---------------------------------------------------------------- assembly

GUIDE = """# Using this design system

`DESIGN.md` is the source of truth. Read it first; everything else renders or encodes it.

## Read order

1. `DESIGN.md` — palette, typography, band rhythm, components, voice, booking rule.
2. `colors_and_type.css` — link it, or paste it into the first `<style>` block of a
   generated artifact. It carries the tokens, the two brand faces as data URIs, and the
   band and component classes.
3. `brand.json` — the same system machine-readable, when you need roles rather than prose.
4. `preview/*.html` — what each part is supposed to look like.

## Do

- Alternate section surfaces: `--ground` → `--paper` → `--tint`, with `--dark` as
  punctuation only.
- Let the content type pick the accent: mint = chronic, apricot = aesthetics,
  lilac = trichology.
- Send every call to action to Practo.
- Keep running text near 65 characters and give digits `tabular-nums`.
- Pick a logo file, never modify one — there are 42 permutations.

## Avoid

- More than three dark bands in a page, or two adjacent.
- Body copy set on a pastel — use the `-dp` deep pair on the `-sf` soft fill.
- Unifying `--navy` and `--ink`. Navy is the logo; ink is the interface.
- A lockup in an avatar slot — that is what the icon ladder is for.
- Cure claims, guarantees, superlatives, or any number you cannot attribute. Indian
  Medical Council advertising rules apply to every page.
"""


def assemble():
    if KIT.exists():
        shutil.rmtree(KIT)
    (KIT / "preview").mkdir(parents=True)
    (KIT / "logos").mkdir()
    (KIT / "context").mkdir()

    shutil.copy2(HERE / "DESIGN.md", KIT / "DESIGN.md")
    shutil.copy2(HERE / "DESIGN.md", KIT / "context" / "input-DESIGN.md")
    shutil.copy2(HERE / "brand.json", KIT / "brand.json")
    shutil.copy2(HERE / "README.md", KIT / "README.md")
    (KIT / "guide.md").write_text(GUIDE, encoding="utf-8")
    (KIT / "colors_and_type.css").write_text(FONTS + "\n\n" + CSS, encoding="utf-8")
    n_tokens = write_tokens(KIT / "design-tokens.json")

    # every logo permutation, straight from the brand build — 36 lockups, 6 marks,
    # the icon ladder and the raster exports
    n_logos = 0
    for src in sorted((BRAND_DIR / "lockups").glob("*.svg")):
        shutil.copy2(src, KIT / "logos" / src.name)
        n_logos += 1
    for src in sorted(BRAND_DIR.glob("logo-mark-*.svg")):
        shutil.copy2(src, KIT / "logos" / src.name)
        n_logos += 1
    for src in sorted((BRAND_DIR / "icons").iterdir()):
        if src.suffix.lower() in {".svg", ".png", ".ico"}:
            shutil.copy2(src, KIT / "logos" / src.name)
            n_logos += 1

    meta = {
        "title": BRAND["title"],
        "category": "Brands",
        "surface": "web",
        "status": "published",
        "artifactMode": "agent-managed",
        "provenance": {
            "companyBlurb": BRAND["description"],
            "sourceUrl": BRAND["sourceUrl"],
            "authoredBy": "agent",
        },
    }
    (KIT / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n",
                                       encoding="utf-8")
    return n_tokens, n_logos


BUILDERS = [
    build_logo_matrix, build_logo_usage, build_logo_misuse, build_icons,
    build_colors_primary, build_colors_neutrals, build_typography,
    build_spacing, build_radius, build_bands, build_grid,
    build_buttons, build_cards, build_forms, build_navigation,
    build_voice, build_imagery, build_accessibility,
]


if __name__ == "__main__":
    n_tokens, n_logos = assemble()
    for fn in BUILDERS:
        p = fn()
        print(f"  {p.name:34} {p.stat().st_size:>7} B")
    print(f"\n  {len(CARDS)} cards, {n_tokens} tokens, {n_logos} brand assets")
    print(f"  kit -> {KIT}")
