# -*- coding: utf-8 -*-
"""External full-site crawl + on-page SEO audit for any site (no auth needed).

Usage: python crawl_atlas.py https://example.com  [--max 400]
Writes: <out>/crawl.json  with per-URL signals, link graph, orphans, broken links.
"""
import sys, re, json, time, argparse, collections
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (compatible; site-audit/1.0; +https://example.com/bot)"}
S = requests.Session(); S.headers.update(UA)

SKIP_EXT = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|pdf|zip|mp4|mp3|css|js|ico|woff2?|ttf|avif)(\?|$)", re.I)


def norm(u):
    u, _ = urldefrag(u)
    return u.rstrip("/") + "/" if urlparse(u).path and not urlparse(u).path.endswith("/") and "." not in urlparse(u).path.split("/")[-1] else u


def schema_types(soup):
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


def audit(url, host):
    rec = {"url": url}
    t0 = time.time()
    try:
        r = S.get(url, timeout=40, allow_redirects=True)
    except Exception as e:
        rec["error"] = str(e)[:120]; return rec, []
    rec["status"] = r.status_code
    rec["ttfb_ms"] = int(r.elapsed.total_seconds() * 1000)
    rec["total_ms"] = int((time.time() - t0) * 1000)
    rec["final_url"] = r.url
    rec["redirected"] = (r.url.rstrip("/") != url.rstrip("/"))
    rec["html_kb"] = round(len(r.content) / 1024, 1)
    ct = r.headers.get("Content-Type", "")
    if "text/html" not in ct or r.status_code >= 400:
        return rec, []
    soup = BeautifulSoup(r.text, "html.parser")

    def meta(name=None, prop=None):
        m = soup.find("meta", attrs={"name": name}) if name else soup.find("meta", attrs={"property": prop})
        return (m.get("content") or "").strip() if m and m.get("content") else None

    title = soup.title.get_text(strip=True) if soup.title else ""
    desc = meta(name="description") or ""
    can = soup.find("link", rel="canonical")
    rec.update({
        "title": title, "title_len": len(title),
        "meta_description": desc, "desc_len": len(desc),
        "canonical": can.get("href") if can else None,
        "robots_meta": meta(name="robots"),
        "og_title": meta(prop="og:title"), "og_desc": meta(prop="og:description"),
        "og_image": meta(prop="og:image"), "og_type": meta(prop="og:type"),
        "twitter_card": meta(name="twitter:card"),
        "viewport": bool(meta(name="viewport")),
        "lang": (soup.html.get("lang") if soup.html else None),
        "schema_types": schema_types(soup),
        "hreflang": [l.get("hreflang") for l in soup.find_all("link", rel="alternate") if l.get("hreflang")],
        "favicon": bool(soup.find("link", rel=lambda v: v and "icon" in v)),
    })
    scope = soup.find("main") or soup.body or soup
    for tag in scope.find_all(["script", "style", "noscript"]):
        tag.decompose()
    rec["h1"] = [h.get_text(" ", strip=True)[:120] for h in scope.find_all("h1")]
    rec["h2"] = [h.get_text(" ", strip=True)[:120] for h in scope.find_all("h2")][:25]
    rec["h3_count"] = len(scope.find_all("h3"))
    imgs = scope.find_all("img")
    rec["images"] = len(imgs)
    rec["images_no_alt"] = len([i for i in imgs if not (i.get("alt") or "").strip()])
    rec["images_lazy"] = len([i for i in imgs if (i.get("loading") or "") == "lazy"])
    text = re.sub(r"\s+", " ", scope.get_text(" ", strip=True))
    rec["word_count"] = len(text.split())
    rec["text_sample"] = text[:600]

    # assets
    rec["scripts"] = len(soup.find_all("script", src=True))
    rec["stylesheets"] = len(soup.find_all("link", rel="stylesheet"))
    rec["inline_style_kb"] = round(sum(len(s.get_text()) for s in soup.find_all("style")) / 1024, 1)

    # links
    links, ext = [], []
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if h.startswith(("mailto:", "tel:", "javascript:", "#", "whatsapp:")):
            if h.startswith(("mailto:", "tel:")):
                ext.append(h)
            continue
        full = norm(urljoin(url, h))
        p = urlparse(full)
        if p.netloc.replace("www.", "") == host:
            if not SKIP_EXT.search(full):
                links.append((full, a.get_text(" ", strip=True)[:80]))
        else:
            ext.append(full)
    rec["internal_links"] = len(links)
    rec["external_links"] = len(set(ext))
    rec["external_targets"] = sorted(set(ext))[:40]
    return rec, links


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--max", type=int, default=400)
    ap.add_argument("--out", default="crawl.json")
    args = ap.parse_args()
    site = args.site.rstrip("/")
    host = urlparse(site).netloc.replace("www.", "")

    # seed from sitemaps
    seeds, sitemap_urls = [norm(site + "/")], []
    idx = S.get(site + "/wp-sitemap.xml", timeout=30)
    for sm in re.findall(r"<loc>(.*?)</loc>", idx.text):
        if sm.endswith(".xml"):
            sitemap_urls.append(sm)
            try:
                sub = S.get(sm, timeout=30).text
                seeds += [norm(u) for u in re.findall(r"<loc>(.*?)</loc>", sub)]
            except Exception:
                pass
    seeds = list(dict.fromkeys(seeds))
    sitemap_set = set(seeds)

    seen, queue, results = set(), collections.deque(seeds), []
    inbound = collections.defaultdict(set)
    anchors = collections.defaultdict(list)
    while queue and len(results) < args.max:
        u = queue.popleft()
        if u in seen:
            continue
        seen.add(u)
        rec, links = audit(u, host)
        rec["in_sitemap"] = u in sitemap_set
        results.append(rec)
        print(f"[{len(results)}] {rec.get('status')} {u}", flush=True)
        for tgt, anchor in links:
            inbound[tgt].add(u)
            anchors[tgt].append(anchor)
            if tgt not in seen and len(seen) + len(queue) < args.max * 2:
                queue.append(tgt)

    for rec in results:
        srcs = inbound.get(rec["url"], set()) - {rec["url"]}
        rec["inbound_count"] = len(srcs)
        rec["inbound_sample"] = sorted(srcs)[:6]
        rec["anchors"] = sorted(set(a for a in anchors.get(rec["url"], []) if a))[:6]

    # broken internal link targets discovered but not crawled
    all_targets = set(inbound)
    unchecked = [u for u in all_targets if u not in seen]
    broken = []
    for u in unchecked[:120]:
        try:
            r = S.get(u, timeout=25, allow_redirects=True)
            if r.status_code >= 400:
                broken.append({"url": u, "status": r.status_code, "from": sorted(inbound[u])[:4]})
        except Exception as e:
            broken.append({"url": u, "status": "ERR " + str(e)[:60], "from": sorted(inbound[u])[:4]})

    data = {"site": site, "sitemaps": sitemap_urls, "crawled": len(results),
            "sitemap_urls": sorted(sitemap_set), "results": results,
            "broken_targets": broken, "uncrawled_targets": sorted(unchecked)[:200]}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nDone. {len(results)} pages -> {args.out}")


if __name__ == "__main__":
    main()
