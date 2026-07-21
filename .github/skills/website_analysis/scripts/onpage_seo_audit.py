# -*- coding: utf-8 -*-
"""On-page SEO audit of live-rendered pages.

For each URL, fetches the live HTML and extracts the real SEO signals a search
engine / LLM sees: title, meta description, canonical, robots, Open Graph /
Twitter, JSON-LD schema types, heading hierarchy, image alt coverage, word
count, and internal-link count. Distinguishes the design content (`.od-embed`
or <main>) from the shared nav/footer chrome where possible.

Usage:
  python onpage_seo_audit.py --url https://site.com/page/ [--url ...]
  python onpage_seo_audit.py --sitemap page          # audit every URL in page-sitemap.xml
  python onpage_seo_audit.py --slug my-page          # resolve via WORDPRESS_SITE_URL
Outputs: outputs/<slug>/onpage_seo_audit.json (+ printed summary)
"""
import os, sys, re, json, argparse
from html import unescape
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp_client as wp

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("This script needs beautifulsoup4:  pip install beautifulsoup4"); sys.exit(1)


def _schema_types(soup):
    out = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            out.append("(unparseable)"); continue

        def walk(d):
            r = []
            if isinstance(d, dict):
                for g in d.get("@graph", []):
                    r += walk(g)
                if "@type" in d:
                    t = d["@type"]; r += t if isinstance(t, list) else [t]
            elif isinstance(d, list):
                for x in d:
                    r += walk(x)
            return r
        out += walk(data)
    return sorted(set(out))


def audit_url(url):
    html = wp.fetch(url)
    if not html:
        return {"url": url, "error": "fetch failed"}
    soup = BeautifulSoup(html, "html.parser")

    def meta(name=None, prop=None):
        m = soup.find("meta", attrs={"name": name}) if name else soup.find("meta", attrs={"property": prop})
        return (m.get("content") or "").strip() if m else None

    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    desc = meta(name="description") or ""
    canonical = soup.find("link", rel="canonical")
    plugin = "RankMath" if "rank-math" in html.lower() or "rank math" in html.lower() else \
             ("Yoast" if "yoast" in html.lower() or "wpseo" in html.lower() else "unknown")

    # content scope: prefer .od-embed, else <main>, else <body>
    scope = soup.find(class_="od-embed") or soup.find("main") or soup.body or soup
    hs = {lvl: [h.get_text(" ", strip=True) for h in scope.find_all(lvl)] for lvl in ("h1", "h2", "h3")}
    imgs = scope.find_all("img")
    no_alt = [i for i in imgs if not (i.get("alt") or "").strip()]
    text = re.sub(r"\s+", " ", scope.get_text(" ", strip=True))
    site_host = urlparse(wp.SITE).netloc.replace("www.", "")
    links = scope.find_all("a", href=True)
    internal = [a["href"] for a in links if site_host in a["href"] or a["href"].startswith("/")]

    issues = []
    if not title: issues.append("missing <title>")
    elif len(title) > 62: issues.append(f"title too long ({len(title)})")
    if not desc: issues.append("missing meta description")
    elif len(desc) > 160: issues.append(f"meta description too long ({len(desc)})")
    if len(hs["h1"]) == 0: issues.append("no H1")
    elif len(hs["h1"]) > 1: issues.append(f"{len(hs['h1'])} H1s")
    if no_alt: issues.append(f"{len(no_alt)} content images missing alt")
    if len(text.split()) < 300: issues.append("thin content (<300 words)")

    return {
        "url": url, "seo_plugin": plugin,
        "title": title, "title_len": len(title),
        "meta_description": desc, "desc_len": len(desc),
        "canonical": canonical.get("href") if canonical else None,
        "robots": meta(name="robots"),
        "og_title": meta(prop="og:title"), "og_image": meta(prop="og:image"),
        "schema_types": _schema_types(soup),
        "h1": hs["h1"], "h2_count": len(hs["h2"]), "h3_count": len(hs["h3"]),
        "content_images": len(imgs), "images_missing_alt": len(no_alt),
        "word_count": len(text.split()),
        "internal_links": len(internal),
        "issues": issues,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", default=[], help="URL(s) to audit")
    ap.add_argument("--slug", action="append", default=[], help="slug(s) under WORDPRESS_SITE_URL")
    ap.add_argument("--sitemap", help="audit every URL in <name>-sitemap.xml (e.g. page, post)")
    args = ap.parse_args()

    urls = list(args.url) + [f"{wp.SITE}/{s.strip('/')}/" for s in args.slug]
    if args.sitemap:
        xml = wp.fetch(f"{wp.SITE}/{args.sitemap}-sitemap.xml")
        urls += [unescape(u) for u in re.findall(r"<loc>(.*?)</loc>", xml)]
    if not urls:
        print("Give --url, --slug, or --sitemap"); return

    results = [audit_url(u) for u in urls]
    path = wp.save("onpage_seo_audit.json", {"site": wp.SITE, "results": results})
    for r in results:
        print("=" * 70)
        if r.get("error"):
            print(f"{r['url']}  ERROR: {r['error']}"); continue
        print(f"{r['url']}")
        print(f"  title({r['title_len']}): {r['title']}")
        print(f"  desc({r['desc_len']}): {r['meta_description'][:90]}")
        print(f"  H1={r['h1']}  schema={r['schema_types']}")
        print(f"  words={r['word_count']} imgs={r['content_images']} no-alt={r['images_missing_alt']} internal-links={r['internal_links']}")
        print(f"  ISSUES: {r['issues'] or 'none'}")
    print(f"\nFull data -> {path}")


if __name__ == "__main__":
    main()
