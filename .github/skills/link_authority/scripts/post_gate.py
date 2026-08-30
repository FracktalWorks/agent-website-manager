#!/usr/bin/env python
"""Gate an article: will Discover, Top Stories, an answer engine and a
journalist all be able to pick it up and point at it?

    python post_gate.py https://example.com/blog/some-post/ [URL ...]
    python post_gate.py --feed https://example.com/feed/ --n 8
    python post_gate.py --html dist/blog/post.html --url https://example.com/blog/post/

The deterministic half of the link_authority skill's newsroom track. It reads
a page the way the three consumers of an article do -- Google Discover, the
Top Stories carousel and an LLM answer engine -- and reports what each would
refuse. Run it on every article before publish (--html) and on the live URL
after, because the two have disagreed.

WHY EACH CHECK EXISTS. Each one has been a real silent failure:

  article schema    Twenty product pages and thirty-seven FAQ pages once
                    shipped their JSON-LD in <head>, and the deploy path kept
                    only <body>. Everything validated locally; nothing was
                    live. The gate reads the page it is given and says WHERE
                    the schema sits, so head-only schema is visible.
  datePublished     Discover and Top Stories are date-driven surfaces. A post
                    with no machine-readable date is an evergreen page to
                    them -- invisible.
  byline            Google's June 2026 Discover update weighted first-hand,
                    named authorship above anything else it shipped that
                    year. "admin" is not an author; an author link that 404s
                    is worse than none.
  og:image >= 1200  Discover's card needs a large image. Below 1200px wide the
                    page qualifies for the text-only feed, which nobody reads.
  max-image-preview Without `max-image-preview:large` in the robots meta,
                    Google shows a thumbnail even when the image is large.
  answer-first      Answer engines quote the first paragraph that states a
                    fact. An opening that clears its throat is never quoted.
  cites something   A page that links to no source gives nobody a reason to
                    link back. Outbound citations are the price of inbound.

Output is a report, not a rewrite: exit 1 if any URL FAILs, 0 otherwise.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (compatible; post-gate/1.0; "
      "+https://github.com/agent-website-manager)")
TIMEOUT = 25
OK, WARN, FAIL, INFO = "OK", "WARN", "FAIL", "--"
ARTICLE_TYPES = {"NewsArticle", "BlogPosting", "Article", "TechArticle",
                 "ScholarlyArticle", "ReportageNewsArticle"}
MIN_IMAGE_WIDTH = 1200
MIN_WORDS = 400
MIN_LEAD_WORDS = 20
MAX_HEADLINE = 110
PLACEHOLDER_AUTHORS = {"admin", "administrator", "editor", "staff", "team",
                       "user", "author", "wpadmin", "webmaster"}


def get(url: str, **kw):
    try:
        return requests.get(url, headers={"User-Agent": UA},
                            timeout=TIMEOUT, **kw)
    except requests.RequestException as e:
        return e


# ------------------------------------------------------------ pure helpers
# (everything below `get` is offline and covered by tests/test_link_authority.py)

def split_head_body(html: str) -> tuple[str, str]:
    """The head and the rest. Schema that only lives in the head is a risk
    on deploy paths that keep the body alone."""
    m = re.search(r"</head\s*>", html, re.I)
    if not m:
        return "", html
    return html[:m.end()], html[m.end():]


_LD = re.compile(r"<script[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>"
                 r"(.*?)</script>", re.I | re.S)


def jsonld_nodes(fragment: str) -> list[dict]:
    """Every typed node in every JSON-LD block, @graph flattened, nested
    nodes included (so a Person nested in an article is findable by @id)."""
    out: list[dict] = []
    for raw in _LD.findall(fragment):
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue
        _walk(data, out)
    return out


def _walk(node, out: list[dict]) -> None:
    if isinstance(node, dict):
        if "@type" in node:
            out.append(node)
        for v in node.values():
            _walk(v, out)
    elif isinstance(node, list):
        for v in node:
            _walk(v, out)


def types_of(node: dict) -> set[str]:
    t = node.get("@type", [])
    return set(t) if isinstance(t, list) else {t}


def article_node(nodes: list[dict]) -> dict | None:
    for n in nodes:
        if types_of(n) & ARTICLE_TYPES:
            return n
    return None


def author_of(article: dict, nodes: list[dict]) -> dict | None:
    """The author node, following an @id reference into the graph."""
    a = article.get("author")
    if isinstance(a, list):
        a = a[0] if a else None
    if isinstance(a, str):
        return {"name": a}
    if not isinstance(a, dict):
        return None
    # Yoast writes `{"name": ..., "@id": ...}` and keeps the typed Person
    # (with its url and sameAs) elsewhere in the graph. Follow the @id
    # whenever there is one; the reference's own fields fill any gaps.
    if "@id" in a:
        for n in nodes:
            if n is not a and n.get("@id") == a["@id"] and "@type" in n:
                return {**a, **n}
    return a


def visible_date(soup: BeautifulSoup) -> str | None:
    t = soup.find("time", attrs={"datetime": True})
    if t:
        return t["datetime"]
    for attrs in ({"property": "article:published_time"},
                  {"name": "article:published_time"},
                  {"itemprop": "datePublished"}, {"name": "date"},
                  {"name": "dc.date"}):
        m = soup.find("meta", attrs=attrs)
        if m and m.get("content"):
            return m["content"]
    return None


def _clean_name(text: str) -> str:
    name = re.sub(r"^(by|written by|posted by)\s*:?\s*", "", text.strip(),
                  flags=re.I).strip()
    # "Name *" is a comment-form label, not a person; so is anything tiny.
    if len(name) < 2 or len(name) > 80 or name.endswith("*"):
        return ""
    return name


def byline(soup: BeautifulSoup, base: str = "") -> tuple[str | None, str | None]:
    """(name, url), read the way a reader does: a linked author name first.
    Searches the article body with forms and comment blocks removed, because
    a WordPress comment form has `class="comment-form-author"` and a label
    that reads "Name *" -- which is exactly what a naive selector returns."""
    scope = soup.find("article") or soup.find("main") or soup
    scope = BeautifulSoup(str(scope), "html.parser")
    for t in scope.find_all(["form", "nav", "footer"]):
        t.decompose()
    for t in scope.select('[id*="comment"], [class*="comment"]'):
        t.decompose()
    for a in scope.select('a[rel~="author"], a[href*="/author/"]'):
        name = _clean_name(a.get_text(" ", strip=True))
        if name:
            return name, urljoin(base, a["href"])
    for sel in ('[class*="byline"]', '[itemprop="author"]',
                '[class*="author-name"]', '[class*="author"]'):
        for el in scope.select(sel):
            name = _clean_name(el.get_text(" ", strip=True))
            if name:
                return name, None
    m = soup.find("meta", attrs={"name": "author"})
    if m and m.get("content"):
        return _clean_name(m["content"]) or None, None
    return None, None


def og_image(soup: BeautifulSoup, base: str) -> str | None:
    m = (soup.find("meta", attrs={"property": "og:image"})
         or soup.find("meta", attrs={"name": "og:image"}))
    if m and m.get("content"):
        return urljoin(base, m["content"])
    return None


def image_dims(data: bytes) -> tuple[int, int] | None:
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:
            return im.size
    except Exception:
        return None


SKIP = ("nav", "header", "footer", "aside", "script", "style", "noscript",
        "form", "figure")


def paragraphs(soup: BeautifulSoup) -> list[str]:
    """Running text of the article body: <article>, else <main>, else body;
    chrome removed; short fragments (captions, labels) ignored."""
    root = soup.find("article") or soup.find("main") or soup.body or soup
    root = BeautifulSoup(str(root), "html.parser")
    for t in root.find_all(list(SKIP)):
        t.decompose()
    out = []
    for p in root.find_all("p"):
        txt = p.get_text(" ", strip=True)
        if len(txt.split()) >= 8:
            out.append(txt)
    return out


def word_count(paras: list[str]) -> int:
    return sum(len(p.split()) for p in paras)


def links(soup: BeautifulSoup, base: str) -> tuple[int, list[str]]:
    """(internal link count, external URLs) within the article body."""
    host = urlparse(base).netloc.lower().removeprefix("www.")
    root = soup.find("article") or soup.find("main") or soup
    internal, external = 0, []
    for a in root.find_all("a", href=True):
        u = urljoin(base, a["href"])
        p = urlparse(u)
        if p.scheme not in ("http", "https"):
            continue
        h = p.netloc.lower().removeprefix("www.")
        if h == host:
            internal += 1
        else:
            external.append(u)
    return internal, external


def feed_items(xml_text: str | bytes) -> list[dict]:
    """RSS <item> and Atom <entry> as {title, link, date, author}."""
    data = xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []
    items = []
    for it in root.iter():
        if it.tag.split("}")[-1] not in ("item", "entry"):
            continue
        d = {"title": "", "link": "", "date": "", "author": ""}
        for c in it:
            ct = c.tag.split("}")[-1]
            if ct == "title":
                d["title"] = (c.text or "").strip()
            elif ct == "link":
                d["link"] = d["link"] or (c.text or c.get("href") or "").strip()
            elif ct in ("pubDate", "published", "updated", "date"):
                d["date"] = d["date"] or (c.text or "").strip()
            elif ct in ("creator", "author"):
                d["author"] = ((c.text or "").strip()
                               or " ".join((x.text or "") for x in c).strip())
        items.append(d)
    return items


# ------------------------------------------------------------------ SEO rows

TITLE_RANGE = (40, 60)       # Google shows ~60; under 40 names a page, not describes it
DESC_RANGE = (70, 165)


def head_ok(url: str) -> bool:
    """HEAD an image URL; monkeypatched in tests. Falls back to GET for hosts
    that refuse HEAD."""
    try:
        hdr = {"User-Agent": UA}
        r = requests.head(url, timeout=15, allow_redirects=True, headers=hdr)
        if r.status_code == 405:
            r = requests.get(url, timeout=15, stream=True, headers=hdr)
        return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


def article_images(soup: BeautifulSoup, base: str) -> list[tuple[str, str]]:
    """(src, alt) for every picture inside the article body. Lazy-loaded
    pictures keep the real file in data-src; the src is a placeholder."""
    scope = soup.find("article") or soup.find("main") or soup
    out = []
    for img in scope.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if not src or src.startswith("data:"):
            continue
        # alt="" is a declaration that the image is decorative (an avatar
        # beside a byline); only a MISSING alt attribute is a defect.
        alt = img.get("alt")
        out.append((urljoin(base, src), "decorative" if alt == "" else (alt or "").strip()))
    return out


def seo_rows(soup: BeautifulSoup, url: str) -> list[tuple[str, str, str]]:
    rows = []
    t = soup.title.get_text(strip=True) if soup.title else ""
    lo, hi = TITLE_RANGE
    rows.append((OK if lo <= len(t) <= hi else WARN, "title length",
                 f"{len(t)} chars" + ("" if lo <= len(t) <= hi else f" (want {lo}-{hi}): {t[:70]}")))
    md = soup.find("meta", attrs={"name": "description"})
    d = (md.get("content") or "").strip() if md else ""
    lo, hi = DESC_RANGE
    if not d:
        rows.append((WARN, "meta description", "missing: Google writes its own"))
    else:
        rows.append((OK if lo <= len(d) <= hi else WARN, "meta description",
                     f"{len(d)} chars" + ("" if lo <= len(d) <= hi else f" (want {lo}-{hi})")))
    h1 = soup.find_all("h1")
    rows.append((OK if len(h1) == 1 else FAIL, "h1", f"{len(h1)} on the page"))
    scope = soup.find("article") or soup
    heads = [h.name for h in scope.find_all(["h2", "h3", "h4"])]
    h2 = heads.count("h2")
    jump = bool(heads) and heads[0] != "h2"
    rows.append((OK if h2 >= 2 and not jump else WARN, "headings",
                 f"{h2} h2, {heads.count('h3')} h3"
                 + (" (first subheading is not an h2)" if jump else "")
                 + ("" if h2 >= 2 else " (fewer than 2 h2: no scannable outline)")))
    imgs = article_images(soup, url)
    noalt = [s for s, a in imgs if not a]
    broken = [s for s, _ in imgs if not head_ok(s)]
    if not imgs:
        rows.append((WARN, "images", "none in the article"))
    else:
        rows.append((OK if not noalt else WARN, "image alt",
                     f"{len(imgs)} images" + (f", {len(noalt)} without alt" if noalt else ", all with alt")))
        rows.append((OK if not broken else FAIL, "images load",
                     "all 200" if not broken else f"{len(broken)} broken: " + broken[0][-60:]))
    return rows


# ------------------------------------------------------------------ gate

def gate(url: str, html: str | None = None) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []

    def row(s, label, detail=""):
        rows.append((s, label, detail))

    if html is None:
        r = get(url)
        if isinstance(r, Exception):
            row(FAIL, "fetch", str(r)[:90])
            return rows
        if r.status_code != 200:
            row(FAIL, "fetch", f"HTTP {r.status_code}")
            return rows
        html, url = r.text, r.url

    head, body = split_head_body(html)
    soup = BeautifulSoup(html, "html.parser")
    head_nodes, body_nodes = jsonld_nodes(head), jsonld_nodes(body)
    nodes = head_nodes + body_nodes
    art = article_node(nodes)
    dated = False
    if not art:
        row(FAIL, "article schema",
            "no NewsArticle/BlogPosting/Article JSON-LD on this page")
    else:
        where = "body" if article_node(body_nodes) else "head"
        row(OK, "article schema",
            f"{'/'.join(sorted(types_of(art) & ARTICLE_TYPES))} in <{where}>")
        h = str(art.get("headline") or "")
        if not h:
            row(WARN, "schema headline", "missing")
        elif len(h) > MAX_HEADLINE:
            row(WARN, "schema headline",
                f"{len(h)} chars; Google truncates around {MAX_HEADLINE}")
        if not art.get("datePublished"):
            row(FAIL, "schema datePublished",
                "missing: a page with no date is not news to any surface")
        else:
            dated = True
            row(OK, "schema datePublished", str(art["datePublished"])[:25])
        au = author_of(art, nodes)
        if not au or not au.get("name"):
            row(WARN, "schema author",
                "none: Discover (June 2026) weights named, first-hand bylines")
        elif str(au["name"]).strip().lower() in PLACEHOLDER_AUTHORS:
            row(WARN, "schema author", f"'{au['name']}' is a role, not a person")
        else:
            t = "/".join(sorted(types_of(au))) if "@type" in au else "untyped"
            row(OK if t == "Person" else WARN, "schema author",
                f"{au['name']} ({t}){' + url' if au.get('url') else ', no url'}")
        if not art.get("image"):
            row(WARN, "schema image", "missing")
        if not art.get("publisher"):
            row(INFO, "schema publisher",
                "missing (Organization + logo helps Top Stories)")

    vd = visible_date(soup)
    row(OK if vd else FAIL, "visible date",
        vd[:25] if vd else "no <time datetime> or article:published_time")
    dated = dated or bool(vd)

    name, aurl = byline(soup, url)
    named = False
    if not name:
        row(WARN, "byline", "no author name on the page")
    elif name.strip().lower() in PLACEHOLDER_AUTHORS:
        row(WARN, "byline", f"'{name}' is not a person")
    elif aurl:
        r2 = get(aurl)
        ok = not isinstance(r2, Exception) and r2.status_code == 200
        named = ok
        row(OK if ok else WARN, "byline",
            f"{name} -> {aurl}" + ("" if ok else " (author page is not 200)"))
    else:
        row(WARN, "byline",
            f"{name}, unlinked: give the author a page with credentials")

    big_image = False
    ogi = og_image(soup, url)
    if not ogi:
        row(FAIL, "og:image", "none: no share card, no Discover card")
    else:
        r3 = get(ogi)
        if isinstance(r3, Exception) or r3.status_code != 200:
            row(WARN, "og:image", f"not fetchable: {ogi}")
        else:
            dims = image_dims(r3.content)
            if not dims:
                row(WARN, "og:image", "undecodable image")
            elif dims[0] < MIN_IMAGE_WIDTH:
                row(FAIL, "og:image",
                    f"{dims[0]}x{dims[1]}: Discover needs >= {MIN_IMAGE_WIDTH}px wide")
            else:
                big_image = True
                row(OK, "og:image", f"{dims[0]}x{dims[1]}")

    rm = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    rc = ((rm.get("content") if rm else "") or "").replace(" ", "").lower()
    preview = "max-image-preview:large" in rc
    if "noindex" in rc:
        row(FAIL, "robots meta", rc)
    elif preview:
        row(OK, "robots meta", "max-image-preview:large")
    else:
        row(WARN, "robots meta",
            "no max-image-preview:large: Discover shows a thumbnail at best")

    can = soup.find("link", rel=lambda v: v and "canonical" in v)
    if not can or not can.get("href"):
        row(WARN, "canonical", "missing")
    else:
        c = urljoin(url, can["href"])
        same = c.rstrip("/") == url.rstrip("/")
        row(OK if same else WARN, "canonical",
            c if same else f"points elsewhere: {c}")

    paras = paragraphs(soup)
    wc = word_count(paras)
    row(OK if wc >= MIN_WORDS else WARN, "length",
        f"{wc} words" + ("" if wc >= MIN_WORDS
                         else f" (< {MIN_WORDS}: thin for a citable piece)"))
    lead = len(paras[0].split()) if paras else 0
    row(OK if lead >= MIN_LEAD_WORDS else WARN, "answer-first lead",
        f"first paragraph {lead} words"
        + ("" if lead >= MIN_LEAD_WORDS else ": open with the fact"))
    internal, external = links(soup, url)
    row(OK if internal >= 2 else WARN, "internal links", str(internal))
    row(OK if external else WARN, "outbound citations",
        str(len(external)) if external
        else "0: a page that cites nothing gives nobody a reason to cite it")

    t = soup.title.get_text(strip=True) if soup.title else ""
    if len(t) > MAX_HEADLINE:
        row(WARN, "title", f"{len(t)} chars")

    # --- on-page SEO: the things that decide whether the piece can rank
    for s_, label, detail in seo_rows(soup, url):
        row(s_, label, detail)

    ready = dated and big_image and preview and named and "noindex" not in rc
    row(OK if ready else WARN, "Discover-ready",
        "date + byline page + large image + preview" if ready
        else "not yet (needs date, linked author, >=1200px image, preview meta)")
    return rows


def print_rows(url: str, rows) -> bool:
    print(f"\n{url}")
    failed = False
    for s, label, detail in rows:
        failed = failed or s == FAIL
        print(f"  {s:4} {label:22} {detail}")
    return failed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--feed", help="RSS/Atom feed to take article URLs from")
    ap.add_argument("--n", type=int, default=8, help="how many feed items")
    ap.add_argument("--html", help="a local built page to gate before deploy")
    ap.add_argument("--url", help="the URL the --html page will live at")
    ap.add_argument("--json", help="write the rows here as JSON")
    a = ap.parse_args()

    targets: list[tuple[str, str | None]] = [(u, None) for u in a.urls]
    if a.feed:
        r = get(a.feed)
        if isinstance(r, Exception) or r.status_code != 200:
            print(f"feed {a.feed}: {r if isinstance(r, Exception) else r.status_code}")
            return 2
        items = feed_items(r.content)[: a.n]
        targets += [(i["link"], None) for i in items if i["link"]]
    if a.html:
        if not a.url:
            ap.error("--html needs --url")
        with open(a.html, encoding="utf-8") as f:
            targets.append((a.url, f.read()))
    if not targets:
        ap.error("give URLs, --feed, or --html")

    report, any_fail = {}, False
    for url, html in targets:
        rows = gate(url, html)
        report[url] = rows
        any_fail = print_rows(url, rows) or any_fail
    fails = sum(1 for rows in report.values()
                if any(s == FAIL for s, _, _ in rows))
    ready = sum(1 for rows in report.values()
                if any(l == "Discover-ready" and s == OK for s, l, _ in rows))
    print(f"\n{len(report)} article(s): {fails} with FAIL, {ready} Discover-ready")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
