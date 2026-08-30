"""The link_authority skill's two checkers, offline.

`authority_audit.py` and `post_gate.py` read live sites; every judgment they
make is a pure function over text, and those are what is pinned here. Each
test is a way the checker has been, or could plausibly be, wrong in a way
that would report a healthy site as broken or a broken one as healthy:

  · a robots.txt `Disallow: /*?add-to-cart=` was read as disallowing `/`,
    so every crawler on a WooCommerce site showed as "blocked by choice"
    and the one real refusal (a 429 to GPTBot) was buried among them;
  · a WordPress comment form's "Name *" label was reported as the byline;
  · JSON-LD that lives only in <head> must be reported as head-only,
    because one deploy path keeps only <body>.

No network: `get` is monkeypatched wherever a check would fetch.
"""
from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".github" / "skills" / "link_authority" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pg = _load("post_gate")
aa = _load("authority_audit")


# ── robots.txt ───────────────────────────────────────────────────────────────
ROBOTS = """
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Disallow: /*?add-to-cart=

User-agent: GPTBot
Disallow: /wp-admin/
Allow: /

User-agent: ClaudeBot
User-agent: PerplexityBot
Disallow: /

Sitemap: https://x.example/sitemap_index.xml
"""


def test_wildcard_rule_does_not_swallow_root():
    g = aa.parse_robots(ROBOTS)
    assert aa.robots_verdict(g, "Bingbot", "/") == ("allow", "*")
    assert aa.robots_verdict(g, "Bingbot", "/p?add-to-cart=3") == ("disallow", "*")
    assert aa.robots_verdict(g, "Bingbot", "/wp-admin/") == ("disallow", "*")


def test_specific_group_beats_star_and_shared_groups_expand():
    g = aa.parse_robots(ROBOTS)
    assert aa.robots_verdict(g, "GPTBot", "/") == ("allow", "GPTBot")
    assert aa.robots_verdict(g, "ClaudeBot", "/") == ("disallow", "ClaudeBot")
    assert aa.robots_verdict(g, "PerplexityBot", "/") == ("disallow", "PerplexityBot")
    assert g["__sitemaps__"] == [("sitemap", "https://x.example/sitemap_index.xml")]


def test_allow_beats_disallow_at_equal_length_and_dollar_anchors():
    g = aa.parse_robots("User-agent: *\nDisallow: /a\nAllow: /a\nDisallow: /*.pdf$\n")
    assert aa.robots_verdict(g, "x", "/a")[0] == "allow"
    assert aa.robots_verdict(g, "x", "/f.pdf")[0] == "disallow"
    assert aa.robots_verdict(g, "x", "/f.pdfx")[0] == "allow"


def test_no_robots_means_allowed():
    assert aa.robots_verdict({}, "GPTBot", "/") == ("allow", "none")


# ── JSON-LD placement and shape ──────────────────────────────────────────────
HEAD_ONLY = """<html><head><title>t</title>
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[
 {"@type":"BlogPosting","headline":"H","datePublished":"2026-08-01","author":{"@id":"#p"}},
 {"@type":"Person","@id":"#p","name":"Ada Lovelace","url":"https://x.example/author/ada/"}]}</script>
</head><body><article><p>body text here is long enough to count as a paragraph ok.</p></article></body></html>"""


def test_article_schema_location_is_visible():
    head, body = pg.split_head_body(HEAD_ONLY)
    assert pg.article_node(pg.jsonld_nodes(head)) is not None
    assert pg.article_node(pg.jsonld_nodes(body)) is None


def test_author_resolves_id_reference_into_graph():
    nodes = pg.jsonld_nodes(HEAD_ONLY)
    art = pg.article_node(nodes)
    au = pg.author_of(art, nodes)
    assert au["name"] == "Ada Lovelace" and au["url"].endswith("/author/ada/")


def test_author_reference_with_name_still_follows_id():
    """Yoast's shape: the article's author carries a name AND an @id; the
    typed Person with the url lives elsewhere in the graph. The gate once
    stopped at the reference and reported 'untyped, no url'."""
    html = ('<script type="application/ld+json">{"@graph":['
            '{"@type":"Article","author":{"name":"Ada","@id":"https://x.example/#/schema/person/1"}},'
            '{"@type":"Person","@id":"https://x.example/#/schema/person/1","name":"Ada Lovelace",'
            '"url":"https://x.example/author/ada/"}]}</script>')
    nodes = pg.jsonld_nodes(html)
    au = pg.author_of(pg.article_node(nodes), nodes)
    assert pg.types_of(au) == {"Person"} and au["url"].endswith("/author/ada/")


def test_author_string_and_list_forms():
    assert pg.author_of({"author": "Bob"}, [])["name"] == "Bob"
    assert pg.author_of({"author": [{"@type": "Person", "name": "C"}]}, [])["name"] == "C"
    assert pg.author_of({}, []) is None


def test_broken_jsonld_block_is_skipped_not_fatal():
    html = '<script type="application/ld+json">{not json</script>' \
           '<script type="application/ld+json">{"@type":"NewsArticle"}</script>'
    assert pg.types_of(pg.article_node(pg.jsonld_nodes(html))) == {"NewsArticle"}


# ── byline, date, image, text ────────────────────────────────────────────────
WP_POST = """<html><head><meta name="author" content="admin"></head><body>
<article>
 <h1>Title</h1>
 <p class="byline">By <a href="/author/ada/" rel="author">Ada Lovelace</a></p>
 <time datetime="2026-08-01T09:00:00+05:30">1 Aug 2026</time>
 <p>First paragraph states the fact plainly with enough words to be quoted by an engine that wants a lead.</p>
 <p>Second paragraph with a <a href="/materials/">link</a> and <a href="https://other.example/x">a citation</a> and more words here.</p>
 <div id="comments"><form class="comment-form"><label class="comment-form-author">Name *</label></form></div>
</article>
<footer><p>Footer text that should never be counted as running copy of the article at all.</p></footer>
</body></html>"""


def test_byline_prefers_linked_author_over_meta():
    soup = BeautifulSoup(WP_POST, "html.parser")
    name, url = pg.byline(soup, "https://x.example/post/")
    assert name == "Ada Lovelace" and url == "https://x.example/author/ada/"


def test_comment_form_label_is_not_a_byline():
    html = WP_POST.replace('<p class="byline">By <a href="/author/ada/" rel="author">Ada Lovelace</a></p>', "")
    name, _ = pg.byline(BeautifulSoup(html, "html.parser"))
    assert name != "Name *"
    assert name == "admin"          # falls through to meta, which the gate then flags


def test_visible_date_time_then_meta():
    assert pg.visible_date(BeautifulSoup(WP_POST, "html.parser")).startswith("2026-08-01")
    m = '<meta property="article:published_time" content="2026-07-01">'
    assert pg.visible_date(BeautifulSoup(m, "html.parser")) == "2026-07-01"
    assert pg.visible_date(BeautifulSoup("<p>x</p>", "html.parser")) is None


def test_paragraphs_skip_chrome_and_fragments():
    paras = pg.paragraphs(BeautifulSoup(WP_POST, "html.parser"))
    assert len(paras) == 2 and paras[0].startswith("First paragraph")
    assert not any("Footer" in p for p in paras)


def test_links_split_internal_external():
    internal, external = pg.links(BeautifulSoup(WP_POST, "html.parser"), "https://x.example/post/")
    assert internal == 2                      # /author/ada/ and /materials/
    assert external == ["https://other.example/x"]


def _png(w: int, h: int) -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (200, 30, 30)).save(buf, "PNG")
    return buf.getvalue()


def test_image_dims_reads_pixels_not_metadata():
    assert pg.image_dims(_png(1300, 700)) == (1300, 700)
    assert pg.image_dims(b"not an image") is None


# ── feeds and cadence ────────────────────────────────────────────────────────
RSS = """<?xml version="1.0"?><rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>
<item><title>A</title><link>https://x.example/a/</link><pubDate>Mon, 03 Aug 2026 10:00:00 +0000</pubDate><dc:creator>ada</dc:creator></item>
<item><title>B</title><link>https://x.example/b/</link><pubDate>Mon, 20 Jul 2026 10:00:00 +0000</pubDate></item>
</channel></rss>"""
ATOM = """<feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>C</title><link href="https://x.example/c/"/><published>2026-08-10T00:00:00Z</published>
<author><name>Ada</name></author></entry></feed>"""


def test_feed_items_rss_and_atom():
    rss = pg.feed_items(RSS)
    assert [i["link"] for i in rss] == ["https://x.example/a/", "https://x.example/b/"]
    assert rss[0]["author"] == "ada"
    atom = pg.feed_items(ATOM)
    assert atom[0]["link"] == "https://x.example/c/" and atom[0]["author"] == "Ada"
    assert pg.feed_items("<html>not a feed") == []


def test_cadence_is_median_gap_and_needs_three_dates():
    d = [aa.parse_date(s) for s in ("Mon, 03 Aug 2026 10:00:00 +0000",
                                    "2026-07-20T10:00:00Z", "2026-07-06T10:00:00Z")]
    assert aa.cadence_days(d) == 14
    assert aa.cadence_days(d[:2]) is None
    assert aa.parse_date("garbage") is None


# ── entity ───────────────────────────────────────────────────────────────────
def test_sameas_platforms_recognise_hosts():
    got = aa.sameas_platforms(["https://www.linkedin.com/company/1/", "https://x.com/brand",
                               "https://github.com/brand", "https://unknown.example/"])
    assert got == {"linkedin", "x", "github"}


def test_org_node_accepts_subtypes_and_sameas():
    assert aa.org_node([{"@type": "MedicalClinic", "name": "c"}])["name"] == "c"
    assert aa.org_node([{"@type": "Thing", "sameAs": ["u"]}]) is not None
    assert aa.org_node([{"@type": "WebPage"}]) is None


# ── the whole gate, offline ──────────────────────────────────────────────────
GOOD = """<html><head><title>Good post</title>
<link rel="canonical" href="https://x.example/blog/good/">
<meta name="robots" content="index, max-image-preview:large">
<meta property="og:image" content="https://x.example/hero.png">
</head><body>
<script type="application/ld+json">{"@type":"NewsArticle","headline":"Good post",
 "datePublished":"2026-08-01","image":"https://x.example/hero.png",
 "author":{"@type":"Person","name":"Ada Lovelace","url":"https://x.example/author/ada/"},
 "publisher":{"@type":"Organization","name":"X"}}</script>
<article>
 <h1>Good post</h1>
 <p class="byline"><a href="/author/ada/" rel="author">Ada Lovelace</a></p>
 <time datetime="2026-08-01">1 Aug 2026</time>
 <p>The lead paragraph states the finding directly with a number and enough words for an engine to lift as the answer.</p>
""" + "".join(f"<p>Paragraph {i} carries a further forty or so words of substance about the subject so the piece is not thin and reads as a real article for a real reader who came for the facts.</p>" for i in range(12)) + """
 <p>See <a href="/materials/">materials</a>, <a href="/printers/">printers</a> and <a href="https://other.example/study">the study</a>.</p>
</article></body></html>"""


class _Resp:
    def __init__(self, status=200, content=b"", url=""):
        self.status_code, self.content, self.url = status, content, url
        self.text = content.decode("utf-8", "ignore")


def test_good_page_is_discover_ready(monkeypatch):
    monkeypatch.setattr(pg, "get", lambda url, **kw: _Resp(200, _png(1600, 900) if url.endswith(".png") else b"<html>author</html>", url))
    rows = pg.gate("https://x.example/blog/good/", GOOD)
    assert not [l for s, l, _ in rows if s == pg.FAIL]
    assert ("OK", "Discover-ready") in [(s, l) for s, l, _ in rows]
    assert any(l == "article schema" and "<body>" in d for _, l, d in rows)


def test_bad_page_fails_on_the_right_things(monkeypatch):
    monkeypatch.setattr(pg, "get", lambda url, **kw: _Resp(200, _png(800, 600), url))
    html = "<html><head><title>t</title><meta property='og:image' content='/small.png'></head>" \
           "<body><p>Short body without any date or schema at all, just a few words.</p></body></html>"
    rows = pg.gate("https://x.example/blog/bad/", html)
    fails = {l for s, l, _ in rows if s == pg.FAIL}
    assert fails == {"article schema", "visible date", "og:image", "h1"}
    assert ("WARN", "Discover-ready") in [(s, l) for s, l, _ in rows]


def test_noindex_is_a_fail_and_kills_readiness(monkeypatch):
    monkeypatch.setattr(pg, "get", lambda url, **kw: _Resp(200, _png(1600, 900), url))
    html = GOOD.replace("index, max-image-preview:large", "noindex, max-image-preview:large")
    rows = pg.gate("https://x.example/blog/good/", html)
    assert any(l == "robots meta" and s == pg.FAIL for s, l, _ in rows)
    assert ("WARN", "Discover-ready") in [(s, l) for s, l, _ in rows]


# ── on-page SEO rows ─────────────────────────────────────────────────────────
def test_seo_rows_measure_title_meta_headings_and_images(monkeypatch):
    monkeypatch.setattr(pg, "head_ok", lambda url: url.endswith("ok.jpg"))
    html = GOOD.replace("<title>Good post</title>",
                        "<title>3D Printed Jigs, Fixtures and Gauges: A Design Guide</title>"
                        '<meta name="description" content="' + "x" * 120 + '">')                .replace("<h1>Good post</h1>",
                        "<h1>Good post</h1><h2>One</h2><h3>Sub</h3><h2>Two</h2>"
                        '<img src="/a-ok.jpg" alt="a jig"><img data-src="/b-gone.jpg" src="data:x">'
                        '<img src="/c-ok.jpg" alt="">')
    rows = {l: (s, d) for s, l, d in pg.seo_rows(pg.BeautifulSoup(html, "html.parser"), "https://x.example/p/")}
    assert rows["title length"][0] == pg.OK
    assert rows["meta description"][0] == pg.OK
    assert rows["h1"][0] == pg.OK
    assert rows["headings"][0] == pg.OK and rows["headings"][1].startswith("2 h2, 1 h3")
    assert rows["image alt"][0] == pg.WARN and "1 without alt" in rows["image alt"][1]  # alt="" (decorative) does not count
    assert rows["images load"][0] == pg.FAIL and "b-gone.jpg" in rows["images load"][1]


def test_seo_rows_flag_short_title_missing_meta_and_heading_jump():
    html = "<html><head><title>Short</title></head><body><h1>t</h1><h1>u</h1><article><h3>x</h3></article></body></html>"
    rows = {l: (s, d) for s, l, d in pg.seo_rows(pg.BeautifulSoup(html, "html.parser"), "https://x.example/p/")}
    assert rows["title length"][0] == pg.WARN
    assert rows["meta description"] == (pg.WARN, "missing: Google writes its own")
    assert rows["h1"][0] == pg.FAIL
    assert rows["headings"][0] == pg.WARN and "not an h2" in rows["headings"][1]
    assert rows["images"] == (pg.WARN, "none in the article")
