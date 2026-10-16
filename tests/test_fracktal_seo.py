"""What a crawler sees — the defects every other gate reports as success.

`build.py` proves the 84 pages render, `verify.py` proves they lay out clean at
five widths, `imgfit.py` proves each picture meets its frame. All three passed,
for months, on a site where:

  · not one page carried an Open Graph tag, so every link pasted into WhatsApp
    — the route most Fracktal enquiries actually arrive by — rendered as a bare
    grey URL;
  · 71 of 84 pages carried no structured data at all;
  · ten of the twelve material pages shipped a Product schema claiming the page
    lived at `/materials/petg/` while the canonical tag four lines above it
    said `/pet-g-polyethylene-terephthalate-glycol/`;
  · 14,562 placed images gave the browser no way to know how tall they would
    be, so every page reflowed under the reader as the pictures arrived;
  · 64 meta descriptions ran past the end of the search result.

None of that is visible in a rendered page, which is why looking at rendered
pages never found it. `seo.py` is the full tool; these are the parts CI can run
without a browser, plus the rule each one exists to keep.

The two findings `seo.py` deliberately does NOT raise are pinned here as well,
because a gate that later starts flagging them has become a gate people ignore.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import urllib.parse
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "fracktal-site" / "site"
DIST = SITE / "dist-prod"

pytestmark = pytest.mark.skipif(
    not (SITE / "seo.py").exists(),
    reason="fracktal site not in this checkout")


def _load(name: str):
    """Import one of this site's modules under a name of its own.

    Every generated site has a `chrome.py`; importing this one as plain
    `chrome` hands it to whichever test imports `chrome` next. See
    test_fracktal_image_fit for the three unrelated failures that caused.
    """
    spec = importlib.util.spec_from_file_location(f"fracktal_{name}",
                                                  SITE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _urls() -> dict[str, str]:
    """This site's slug->URL map, loaded without claiming the name `content`.

    `content` is a package name every generated site uses. Putting this site's
    on `sys.path` and importing it registers `content`, `content.urls` and
    everything they pull in — and hands them to whichever test imports
    `content` next. That is not hypothetical: it failed three drvarada tests in
    `test_site_engine.py` the first time this file was written.
    """
    spec = importlib.util.spec_from_file_location(
        "fracktal_urls", SITE / "content" / "urls.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.URLS


@pytest.fixture(scope="module")
def seo():
    return _load("seo")


@pytest.fixture(scope="module")
def chrome():
    """The renderer, with the whole page set — then every import undone.

    `breadcrumbs()` needs the other pages, and the only way to get them is to
    import this site's `content` package for real. So: import it, take what is
    needed, then put `sys.path` and `sys.modules` back exactly as they were.
    """
    mod = _load("chrome")
    mod.URLS = _urls()
    shared = ("content", "chrome", "siteconf")

    # Whoever ran first may already own these names, and `content` is a package
    # every generated site has. Borrowing the namespace means taking it AND
    # giving it back: without the pop, drvarada's `content` is already in
    # `sys.modules` and this import finds no `content.materials`; without the
    # restore, drvarada's next test gets fracktal's pages. Both were observed.
    stashed = {k: sys.modules.pop(k) for k in list(sys.modules)
               if k.split(".")[0] in shared}
    sys.path.insert(0, str(SITE))
    try:
        siteconf = _load("siteconf")
        pages = [p for n in siteconf.MODULES
                 for p in importlib.import_module(f"content.{n}").PAGES]
        mod.PAGES_BY_SLUG = {p["slug"]: p for p in pages}
        mod.ALL_PAGES = pages
        yield mod
    finally:
        sys.path.remove(str(SITE))
        for k in list(sys.modules):
            if k.split(".")[0] in shared:
                del sys.modules[k]
        sys.modules.update(stashed)


@pytest.fixture(scope="module")
def built():
    if not DIST.exists() or not list(DIST.glob("*.html")):
        pytest.skip("dist-prod/ not built")
    return DIST


# ---------------------------------------------------------------- the parser

def test_parser_reads_a_page_the_way_a_crawler_does(seo):
    """Regex would find the second title here. An HTML parser finds neither."""
    p = seo.Page()
    p.feed('<html lang="en-IN"><head><title>Real</title>'
           '<meta name="description" content="d">'
           '<link rel="canonical" href="https://x/">'
           '</head><body><!-- <title>Fake</title> -->'
           '<h1>One</h1><h2>Two</h2>'
           '<img src="a.png" alt="a" width="2" height="1">'
           '<a href="/x/">go</a></body></html>')
    assert p.title == "Real"
    assert p.canonical == "https://x/"
    assert p.lang == "en-IN"
    assert p.headings == [(1, "One"), (2, "Two")]
    assert p.imgs[0]["width"] == "2"
    assert p.hrefs == ["/x/"]


# --------------------------------------------------------- the rules it keeps

def _audit(seo, html: str, slug: str = "p", url: str = "/p/"):
    """One page, judged on its own — no uniqueness, orphan or sitemap checks."""
    p = seo.Page()
    p.feed(html)
    return seo.audit({slug: p}, {slug: url}, site_wide=False)


# The title is a realistic length, not a placeholder letter. `seo.py`
# gained a 40-character FLOOR after twelve material pages shipped
# titles like "PLA Filament — Fracktal Works" and passed as clean —
# a one-character title is no longer a sound page, and this fixture
# claims to be one.
GOOD = (
    '<html lang="en-IN"><head>'
    '<title>A Realistic Page Title of Sixty Characters | Fracktal</title>'
    '<meta name="viewport" content="width=device-width">'
    '<meta name="description" content="{d}">'
    '<link rel="canonical" href="https://fracktal.in/p/">'
    '<link rel="icon" href="i.png">'
    '<meta property="og:title" content="T">'
    '<meta property="og:image" content="i.png">'
    '<meta name="twitter:card" content="summary_large_image">'
    '<script type="application/ld+json">{{"@type":"Thing",'
    '"url":"https://fracktal.in/p/"}}</script>'
    '</head><body><h1>H</h1>{body}</body></html>'
)
FILLER = " word" * 400


def _page(body: str = "", desc: str = "d" * 120) -> str:
    return GOOD.format(d=desc, body=body + FILLER)


def test_a_sound_page_raises_nothing(seo):
    assert _audit(seo, _page()) == {}


def test_missing_share_card_is_a_defect(seo):
    """The WhatsApp preview. Absent for 84 pages and nothing said a word."""
    bad = _audit(seo, _page().replace('<meta property="og:image" '
                                      'content="i.png">', ""))
    assert "no Open Graph card" in bad


def test_schema_url_must_equal_the_canonical(seo):
    """Two answers to 'where does this page live' is the bug that shipped."""
    bad = _audit(seo, _page().replace('"url":"https://fracktal.in/p/"',
                                      '"url":"https://fracktal.in/elsewhere/"'))
    assert "schema url is not the canonical" in bad


def test_image_without_intrinsic_size_is_a_defect(seo):
    """No width/height means the page reflows under the reader — that is CLS."""
    bad = _audit(seo, _page('<img src="a.png" alt="a">'))
    assert "img has no width/height" in bad
    assert not _audit(seo, _page('<img src="a.png" alt="a" '
                                 'width="2" height="1">'))


def test_description_outside_the_serp_window_is_a_defect(seo):
    assert "meta description outside 70-165" in _audit(seo, _page(desc="d" * 240))
    assert "meta description outside 70-165" in _audit(seo, _page(desc="short"))


def test_heading_outline_must_start_at_h1_and_not_skip(seo):
    """The home page opened with eight carousel captions before its h1."""
    assert "first heading is not h1" in _audit(
        seo, _page().replace("<h1>H</h1>", "<h2>C</h2><h1>H</h1>"))
    assert "heading level skipped" in _audit(
        seo, _page("<h3>skipped past h2</h3>"))


def test_a_page_with_no_structured_data_is_a_defect(seo):
    bad = _audit(seo, re.sub(r"<script type=\"application/ld\+json\">.*?"
                             r"</script>", "", _page(), flags=re.S))
    assert "no structured data" in bad


def test_links_to_pages_this_project_does_not_build_are_not_broken(seo):
    """`/contact-us/` lives on fracktal.in. All thirteen were checked: 200."""
    assert not _audit(seo, _page('<a href="/contact-us/">c</a>'))
    assert "internal link to unknown path" in _audit(
        seo, _page('<a href="/no-such-page/">x</a>'))


# ------------------------------------------------------- the rendered output

def test_every_built_page_passes(seo, built):
    pages = {}
    for f in seo.built_pages(built):
        p = seo.Page()
        p.feed(f.read_text(encoding="utf-8"))
        pages[f.stem] = p
    bad = seo.audit(pages, _urls())
    assert not bad, json.dumps({k: v[:4] for k, v in bad.items()}, indent=1)


def test_the_marquee_hides_its_duplicate_copy_from_screen_readers(built):
    """1,809 empty alts, every one deliberate. `seo.py` must keep ignoring them.

    The logo strip renders its roster twice so the scroll can loop seamlessly.
    The second copy is `aria-hidden` with an empty alt, so the reader hears
    thirty company names once rather than sixty. Pinned because a future gate
    that starts calling this a defect is a gate people learn to ignore.
    """
    html = (built / "3dprinters.html").read_text(encoding="utf-8")
    track = html.split('class="logo-track"')[1].split("</div></div>")[0]
    named = len(re.findall(r'alt="[^"]+"', track))
    blank = len(re.findall(r'alt=""', track))
    assert named and blank == named, f"{named} named, {blank} blank"
    assert 'aria-hidden="true"' in track


# ------------------------------------------------------ the derived metadata

def test_breadcrumbs_never_point_at_a_page_that_is_not_built(chrome):
    """`/compare/fdm-vs-sla-vs-sls/` has no `/compare/` page — skip, not guess."""
    live = set(chrome.URLS.values()) | {"/"}
    for page in chrome.ALL_PAGES:
        crumbs = chrome.breadcrumbs(page)
        if not crumbs:
            continue
        items = crumbs["itemListElement"]
        assert [i["position"] for i in items] == list(range(1, len(items) + 1))
        for i in items:
            assert i["item"].replace(chrome.SITE, "") in live, i
        assert items[-1]["item"] == chrome.page_url(page["slug"])


# ------------------------------------------------------------------ mobile

def test_footer_sections_ship_open(built):
    """The fold is JavaScript's job; the MARKUP must work without it.

    78 links, and none can be dropped — the twenty city pages and the HSN
    guide are linked from nowhere else, so cutting the row orphans 21 pages.
    So the footer folds on a phone instead, and `<details open>` is which way
    round that has to fail: script off, the footer is merely long, which is
    what it was before. Ship them closed and every link is behind a control
    nothing can operate. `mobile.py` measures the folded result; this pins the
    fallback, which no browser test would ever exercise.
    """
    html = (built / "petg.html").read_text(encoding="utf-8")
    foot = html.split('<footer class="fw-foot"')[1]
    opens = re.findall(r'<details class="fw-foot__(?:col|cities)" open>', foot)
    assert len(opens) >= 5, f"only {len(opens)} footer sections ship open"
    assert "<details class=\"fw-foot__col\">" not in foot
    assert foot.count('class="fw-foot__chev"') == len(opens)


def test_every_footer_link_survives_the_fold(built):
    """Collapsing is a display decision. A crawler must still see all 78."""
    counts = set()
    for name in ("petg.html", "home.html", "landing.html", "3dprinters.html"):
        foot = (built / name).read_text(encoding="utf-8") \
            .split('<footer class="fw-foot"')[1]
        counts.add(len(re.findall(r"<a [^>]*href=", foot)))
    assert len(counts) == 1, f"footer link count differs per page: {counts}"
    assert counts.pop() >= 70


def test_the_radar_has_a_short_label_for_every_long_one(chrome):
    """Nine full property names do not fit around a polygon on a 342px column.

    At the size that makes them readable they clip and overlap — looked at,
    rejected. The short set is what lets the whole chart stay on screen AND be
    read, so it has to stay in step with the long one: same length, same
    order, and every entry actually shorter.
    """
    long_, short = chrome.RADAR_AXES, chrome.RADAR_AXES_SHORT
    assert len(short) == len(long_) == 9
    for a, b in zip(long_, short):
        assert b and len(b) <= len(a), f"{b!r} is not shorter than {a!r}"


def test_faq_schema_is_built_only_from_real_questions(chrome):
    """The accordion is also a spec widget. 'Build Size' is not a Question."""
    spec = {"slug": "x", "title": "T", "h1": "H", "sections": [
        {"kind": "accordion", "items": [
            {"q": "Build Size", "a": "200 x 200 x 200 mm"},
            {"q": "Accuracy", "a": "50 microns"}]}]}
    assert chrome.faq_schema(spec) is None

    real = {"slug": "x", "title": "T", "h1": "H", "sections": [
        {"kind": "accordion", "items": [
            {"q": "Is it enclosed?", "a": "<p>Yes.</p>"},
            {"q": "What does it cost?", "a": "Not published."}]}]}
    out = chrome.faq_schema(real)
    assert out["@type"] == "FAQPage"
    assert len(out["mainEntity"]) == 2
    # HTML is markup, not an answer's text.
    assert out["mainEntity"][0]["acceptedAnswer"]["text"] == "Yes."


# ── the rebuild replaces a live site, so moved URLs need somewhere to land ───
def _redirects():
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location(
        "fk_redirects", SITE / "content" / "redirects.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_every_redirect_lands_on_a_page_this_site_builds(chrome):
    """A 301 into a 404 is worse than the 404 it replaced: it spends the
    crawler's budget and still loses the ranking.

    Since the blog and KB passes (2026-08-30), redirect targets legitimately
    include WordPress-owned URLs the build never produces: blog posts are in
    seo.py's OFF_BUILD allowlist (each verified live when added), and KB docs
    live under /kb/ on the docs CPT. For /kb/ targets the check is the prefix
    plus not-self — the doc slugs exist only in WordPress, and each of those
    301s was read back live when the KB was restructured."""
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("fk_seo", SITE / "seo.py")
    seo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = seo
    spec.loader.exec_module(seo)
    valid = set(chrome.URLS.values()) | seo.OFF_BUILD
    dead = {old: new for old, new in _redirects().REDIRECTS.items()
            if new not in valid
            and not (new.startswith("/kb/") and new != old)}
    assert not dead, f"redirect target is not a page: {dead}"


def test_no_redirect_shadows_a_page_that_still_exists(chrome):
    """The eight industry pages and nine of the twelve materials KEPT their
    original WordPress URLs on purpose. Redirecting one of those would send a
    live, ranking page to somewhere else on arrival."""
    paths = set(chrome.URLS.values())
    clash = sorted(old for old in _redirects().REDIRECTS if old in paths)
    assert not clash, f"redirect source is still a live page: {clash}"


def test_the_front_page_is_not_redirected():
    """WordPress serves the front page at `/`. The rebuild's home canonical
    says `/home/`; that is a canonical to fix, not a hop to put in front of
    every visitor and every crawler."""
    assert "/" not in _redirects().REDIRECTS


def test_the_build_ships_the_redirect_rules():
    out = SITE / "dist-prod" / "redirects.htaccess"
    assert out.exists(), "dist-prod carries no redirect rules"
    text = out.read_text(encoding="utf-8")
    for old, new in _redirects().REDIRECTS.items():
        assert f" {new} [R=301,L]" in text, f"{old} missing from the rules"


# ── the trail is drawn, not only described ──────────────────────────────────
def test_a_child_page_draws_a_link_to_its_hub(chrome):
    """`BreadcrumbList` markup with no visible trail is the worst of both: it
    describes navigation the visitor cannot see, and — measured on the built
    site with header and footer stripped — it left `/applications/`,
    `/3dprinters/` and `/materials/` with ZERO in-content inbound links."""
    page = next(p for p in chrome.ALL_PAGES
                if p["slug"] == "app-drone-parts")
    out = chrome.crumb_nav(page, "production")
    assert 'class="fw-crumbs"' in out
    assert 'aria-label="Breadcrumb"' in out
    assert 'href="/applications/"' in out
    assert 'aria-current="page"' in out


def test_the_front_page_draws_no_trail(chrome):
    """"Home > Home" is not wayfinding."""
    page = next(p for p in chrome.ALL_PAGES if p["slug"] == "home")
    assert chrome.crumb_nav(page, "production") == ""


def test_the_breadcrumb_style_lives_where_every_page_can_see_it():
    """Rule 1: a page's own stylesheet REPLACES site.css. chrome.css is the
    only sheet all 84 pages load, so anywhere else is an unstyled `<ol>` on
    the twelve material pages."""
    css = (SITE / "assets" / "chrome.css").read_text(encoding="utf-8")
    assert ".fw-crumbs" in css


# ── the front page is "/" ───────────────────────────────────────────────────
def test_the_front_page_lives_at_the_root(chrome):
    """`/home/` is not a URL fracktal.in serves — the live sitemap carries
    `https://fracktal.in/` and no `/home/` at all. While the map said
    `/home/`, every page on the site aimed its canonical, its `og:url`, its
    breadcrumb root and its sitemap entry at a 404."""
    assert chrome.URLS["home"] == "/"
    # `/home/about-us/` is a real live URL and keeps its path even though
    # nothing is served at its parent segment.
    assert chrome.URLS["about"] == "/home/about-us/"


def test_the_logo_points_at_the_front_page():
    """The header and footer logos are on all 84 pages, so a stale path here
    is 168 broken internal links, which is exactly what it was."""
    nav = json.loads((SITE / "content" / "nav.json").read_text(encoding="utf-8"))
    assert nav["brand"]["home"] == "/"


def test_the_home_page_links_out_to_what_it_advertises(chrome):
    """It names eight materials and five processes. Each of those cards used
    to go nowhere, on the page with the most authority to pass — the whole
    home page linked to nine pages, not one of them a material."""
    page = next(p for p in chrome.ALL_PAGES if p["slug"] == "home")
    html = "".join(chrome.render(page, "production"))
    for path in ("/pla-polylactic-acid/", "/cf-nylon/", "/nylon/",
                 "/tpu-thermoplastic-polyurethane/", "/fdm-3d-printing/",
                 "/sls-3d-printing/", "/vaccum-casting/"):
        assert f'href="{path}"' in html, f"home page does not link to {path}"


# ── the schema has to survive the DEPLOY, not just the build ────────────────
def test_generated_schema_reaches_the_deployed_body(chrome):
    """Structured data in the <head> does not exist on the live site.

    `deploy.py cmd_prep` keeps only what lies between <body> and </body> —
    `elementor_canvas` drops the head. Every node chrome generates used to be
    emitted in the head, so Product on 20 pages and FAQPage on 37 were built,
    passed `seo.py`, passed every test here, and were then thrown away on the
    way to WordPress. The live pages carried Yoast's generic graph and nothing
    else, and no gate could tell, because every gate read the BUILT page and
    the defect was in the DEPLOYED one.

    So this asserts on the artifact that actually ships.
    """
    for slug, expect in (("julia", {"Product", "FAQPage"}),
                         ("nylon", {"Product"}),
                         ("home", {"FAQPage"})):
        page = next(p for p in chrome.ALL_PAGES if p["slug"] == slug)
        html = chrome.render(page, "production")
        body = html[html.find("<body>"):html.rfind("</body>")]
        found = set()
        for block in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                body, re.S):
            found.add(json.loads(block).get("@type"))
        missing = expect - found
        assert not missing, (
            f"{slug}: {sorted(missing)} is emitted outside <body>, so the "
            f"canvas deploy will drop it. Body carries {sorted(found)}.")


def test_breadcrumbs_stay_out_of_the_deployed_body(chrome):
    """Yoast emits its own BreadcrumbList on every live page. Shipping a
    second one with different labels for the same URL is a worse answer than
    one, so ours is deliberately head-only — present for preview, absent from
    the deployed body."""
    page = next(p for p in chrome.ALL_PAGES if p["slug"] == "julia")
    html = chrome.render(page, "production")
    body = html[html.find("<body>"):html.rfind("</body>")]
    assert "BreadcrumbList" in html, "breadcrumbs should still be built"
    assert "BreadcrumbList" not in body, (
        "our BreadcrumbList reached the deployed body — it would compete "
        "with the one Yoast already emits live")


# ------------------------------------------------------------------ WhatsApp
#
# The number is on the WhatsApp Business API and it is the route most Fracktal
# enquiries actually arrive by, so the click-to-chat link is on all 96 pages —
# in the header, in the drawer, in the footer, at the end of every CTA band and
# as a floating button. Five places, one builder, and these are the rules that
# builder has to keep. Every one of them is a way the link can be present in
# the markup and dead in the visitor's hand.

def test_the_whatsapp_number_is_in_the_form_the_endpoint_accepts(chrome):
    """`wa.me` takes full international, digits only.

    A `+`, a space or a dash resolves to WhatsApp's "phone number shared via
    url is invalid" page — which looks like a working link right up until
    somebody taps it. The number is also the SAME one `tel:` dials; two
    numbers for one desk is how a company ends up answering only one.
    """
    assert chrome.WHATSAPP_NUMBER.isdigit(), (
        f"{chrome.WHATSAPP_NUMBER!r} is not digits-only — wa.me will reject "
        f"it and the link will 404 for every visitor")
    assert chrome.WHATSAPP_NUMBER.startswith("91"), "country code missing"
    digits = re.sub(r"\D", "", chrome.PHONE)
    assert digits == chrome.WHATSAPP_NUMBER, (
        f"WhatsApp ({chrome.WHATSAPP_NUMBER}) and the phone number "
        f"({digits}) have drifted apart")


def test_every_page_carries_exactly_one_floating_whatsapp_button(chrome):
    for slug in ("home", "julia", "contact-us", "privacy-policy"):
        page = next(p for p in chrome.ALL_PAGES if p["slug"] == slug)
        html = chrome.render(page, "production")
        assert html.count('class="fw-wa-float"') == 1, (
            f"{slug}: expected exactly one floating WhatsApp button")
        body = html[html.find("<body>"):html.rfind("</body>")]
        assert "fw-wa-float" in body, (
            f"{slug}: the floating button is outside <body> and the canvas "
            f"deploy would drop it — see the schema head-vs-body defect")


def test_the_prefilled_message_names_the_page_it_came_from(chrome):
    """96 pages route to one number. Which page the visitor was on is the one
    thing the person answering cannot work out for themselves."""
    page = next(p for p in chrome.ALL_PAGES if p["slug"] == "julia")
    html = chrome.render(page, "production")
    link = re.search(r'https://wa\.me/[^"]+', html).group(0)
    assert "Julia" in urllib.parse.unquote(link), (
        "the WhatsApp prefill does not name the page")


def test_the_home_page_prefill_does_not_read_as_machine_output(chrome):
    """The home `h1` is a sales headline, not a name for the page. "I'm on
    your 3D Printers & 3D Printing Services, Built for Production page" is not
    a sentence anybody types, and a visitor deletes a line that reads that way
    — taking the context with it."""
    page = next(p for p in chrome.ALL_PAGES if p["slug"] == "home")
    html = chrome.render(page, "production")
    link = re.search(r'https://wa\.me/[^"]+', html).group(0)
    assert urllib.parse.unquote(link).endswith(chrome.WA_OPENER_PLAIN)


def test_the_renderer_does_not_leak_the_last_page_it_rendered(chrome):
    """`_WA_PAGE` is module state with one writer. If `render` ever returns
    without clearing it, a bare `whatsapp()` — the live editor, a test, a
    partial render — silently claims to come from whatever ran last."""
    page = next(p for p in chrome.ALL_PAGES if p["slug"] == "julia")
    chrome.render(page, "production")
    assert chrome._WA_PAGE == ""
    assert urllib.parse.unquote(chrome.whatsapp()).endswith(
        chrome.WA_OPENER_PLAIN)


def test_the_closing_cta_band_carries_a_whatsapp_button(chrome):
    """83 of the 96 pages end on this band, which is why the button is added
    by the renderer and not written into 83 JSON files."""
    band = {"kind": "ctaband", "h2": "h", "body": "b",
            "buttons": [{"label": "Get a Quote", "href": "/contact-us/",
                         "style": "primary"}]}
    out = chrome.blk_ctaband(band, "production")
    assert "fw-wa-btn" in out and "wa.me" in out
    assert "Get a Quote" in out, "the page's own buttons must survive"
    off = chrome.blk_ctaband({**band, "whatsapp": False}, "production")
    assert "wa.me" not in off, "`whatsapp: false` must opt a band out"


def test_the_whatsapp_button_never_borrows_a_page_stylesheet_name(chrome):
    """`.btn--solid` and `.btn--ghost` were authored on the contact page and
    no stylesheet has ever defined either, so both buttons rendered as a bare
    `.btn` — no fill, no border — on a near-black band. Readable, therefore
    never reported. The WhatsApp button must not repeat that: `.btn` sizes it
    and `.fw-wa-btn` (chrome.css, loaded by every page) colours it."""
    page = next(p for p in chrome.ALL_PAGES if p["slug"] == "contact-us")
    html = chrome.render(page, "production")
    for dead in ("btn--solid", "btn--ghost", "btn-whatsapp", "btn--whatsapp"):
        assert dead not in html, (
            f"{dead} is emitted and no stylesheet defines it")
    chrome_css = (SITE / "assets" / "chrome.css").read_text(encoding="utf-8")
    for cls in ("fw-wa-btn", "fw-wa-float", "fw-head__wa", "fw-foot__wa"):
        assert f".{cls}" in chrome_css, (
            f".{cls} is emitted but chrome.css — the only sheet every page "
            f"loads — does not define it")


# ------------------------------------------------------------- material data
#
# The material pages are the site's evidence. Every number on them is supposed
# to come from `content/material-database.json` and nowhere else — and the one
# place that rule was broken was the one place no gate could look: a value
# baked into a JavaScript file that only a browser ever evaluates.

def test_the_radar_plots_the_page_its_own_material(seo):
    """`site.js` must take the primary material FROM THE PAGE.

    It used to declare `const PRIMARY_KEY = 'cf-pa'` inside its own IIFE,
    shadowing the per-page value `chrome.py` injects. Eleven of the twelve
    material pages therefore drew CARBON-FIBRE NYLON's nine scores as their
    own — in the page's colour, under the page's name in the legend, beside
    the page's real numbers in the table. CF-Nylon was right, because the file
    was ported from that page.

    Nothing else could see it: the SVG was valid, the polygon had nine points,
    and the colours were server-rendered and correct. Only the SHAPE was
    another material's, and shape is not something a build, a linter or a
    screenshot diff has an opinion about.
    """
    raw = (SITE / "assets" / "site.js").read_text(encoding="utf-8")
    # Comment lines are stripped first: the fix is explained in a comment that
    # QUOTES the bad line, and a gate that fires on its own explanation is a
    # gate somebody deletes. Whole-line `//` only — enough here, and it cannot
    # damage a `https://` inside a string the way a general strip would.
    js = "\n".join(l for l in raw.splitlines() if not l.lstrip().startswith("//"))
    assert "const PRIMARY_KEY = 'cf-pa'" not in js, (
        "site.js has gone back to hardcoding the primary material — every "
        "material page will plot CF-PA's profile as its own")
    assert re.search(r"typeof PRIMARY_KEY\s*!==\s*'undefined'", js), (
        "site.js no longer reads PRIMARY_KEY from the page")
    assert "FRACKTAL_MATERIALS[MY_KEY]" in js, (
        "the radar's primary polygon is no longer driven by the page's key")


def test_no_material_page_states_a_number_the_database_contradicts(chrome):
    """Every figure on a material page is a claim about a measured property,
    and the database is the only place those are allowed to come from.

    Five property cards had drifted: PETG claimed 20-30 % elongation where the
    database's range stops at 25, ABS claimed 5-10 % where the database's own
    value is 15, and Polycarbonate quoted impact in J/m — the only J/m figure
    on a site that states every other impact in kJ/m², so it could not be
    compared with anything.
    """
    db = json.loads((SITE / "content" / "material-database.json")
                    .read_text(encoding="utf-8"))["materials"]
    field = {"tensile strength": "tensileStrength",
             "heat deflection": "heatDeflection",
             "heat deflection (hdt)": "heatDeflection",
             "density": "density", "flexural modulus": "flexuralModulus",
             "flexural strength": "flexuralStrength",
             "izod impact": "izodImpact", "impact strength": "izodImpact",
             "impact resistance": "izodImpact",
             "elongation at break": "elongationAtBreak"}

    def num(s):
        m = re.search(r"-?\d+(?:\.\d+)?", str(s).replace(",", ""))
        return float(m.group(0)) if m else None

    wrong = []
    for page in chrome.ALL_PAGES:
        key = page.get("material")
        if not key:
            continue
        specs = db[key].get("specs", {})
        for s in page["sections"]:
            if s.get("kind") != "props":
                continue
            for c in s["cards"]:
                f = field.get(c["name"].strip().lower())
                spec = specs.get(f) if f else None
                shown = num(c["value"])
                if not spec or shown is None:
                    continue
                lo, hi = spec.get("range") or [spec["value"], spec["value"]]
                if isinstance(lo, str) or not (float(lo) <= shown <= float(hi)):
                    wrong.append(
                        f"{page['slug']}: {c['name']} = {c['value']!r}, "
                        f"database says {spec['value']} "
                        f"{spec.get('unit', '')} "
                        f"(range {spec.get('range')})")
                unit = str(spec.get("unit", ""))
                if unit and unit not in str(c["value"]) and "%" not in unit:
                    wrong.append(
                        f"{page['slug']}: {c['name']} = {c['value']!r} is "
                        f"not stated in {unit}, so it cannot be compared "
                        f"with the other pages")
    assert not wrong, "material pages disagree with the database:\n  " + \
        "\n  ".join(wrong)
