# -*- coding: utf-8 -*-
"""Full-site internal-linking / orphan audit.

Crawls every content URL in the site's XML sitemaps, counts how many *distinct
other pages* link to each one, and separates site-wide chrome (nav/footer,
present on ~all pages) from real contextual links. Surfaces:
  - ORPHANS      : 0 inbound links (nothing links to them)
  - contextual   : linked from some page bodies (thin = <= 2)
  - GLOBAL       : in the nav/footer (linked from most pages)

Usage:
  python link_audit.py                 # crawl every sitemap, full report
  python link_audit.py --max 300       # cap URLs crawled
  python link_audit.py --workers 16
Outputs: outputs/<slug>/link_audit.json  (+ printed summary)
"""
import os, sys, re, argparse, concurrent.futures as cf
from urllib.parse import urljoin, urlparse
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp_client as wp

CHROME_FRACTION = 0.60          # linked from >= this share of pages => nav/footer
THIN_MAX = 2                    # <= this many contextual inbound = "thin"


def norm(u, base):
    if not u:
        return None
    u = u.strip()
    if u.startswith(("mailto:", "tel:", "#", "javascript:", "data:")):
        return None
    u = urljoin(base, u)
    p = urlparse(u)
    if p.scheme not in ("http", "https"):
        return None
    host = p.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    site_host = urlparse(wp.SITE).netloc.lower().replace("www.", "")
    if site_host not in host:
        return None                                   # internal only
    path = p.path or "/"
    if not path.endswith("/"):
        path += "/"
    if re.search(r"\.(jpg|jpeg|png|webp|gif|svg|pdf|zip|css|js|ico)/?$", path, re.I):
        return None
    if any(seg in path for seg in ("/wp-json/", "/wp-content/", "/wp-admin/", "/feed/")):
        return None
    return f"https://{site_host}{path}"


def discover_sitemaps():
    """Return sub-sitemap URLs from sitemap_index.xml (falls back to /sitemap.xml)."""
    for idx in (f"{wp.SITE}/sitemap_index.xml", f"{wp.SITE}/sitemap.xml"):
        xml = wp.fetch(idx)
        locs = re.findall(r"<loc>(.*?)</loc>", xml)
        subs = [l for l in locs if l.endswith(".xml")]
        if subs:
            return subs
        if locs:                                      # flat sitemap of page URLs
            return [idx]
    return []


def collect_urls():
    kind_of, targets = {}, []
    for sm in discover_sitemaps():
        kind = re.sub(r"-sitemap\.xml$|\.xml$", "", sm.rsplit("/", 1)[-1]) or "page"
        for loc in re.findall(r"<loc>(.*?)</loc>", wp.fetch(sm)):
            n = norm(unescape(loc), wp.SITE)
            if n and n not in kind_of:
                kind_of[n] = kind
                targets.append(n)
    return targets, kind_of


def crawl(url):
    html = wp.fetch(url)
    if not html:
        return url, None, None
    title = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if m:
        title = unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    out = set()
    for h in re.findall(r'href=["\']([^"\']+)["\']', html):
        n = norm(h, url)
        if n and n != url:
            out.add(n)
    return url, title, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0, help="cap number of URLs crawled")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    if not wp.SITE:
        print("WORDPRESS_SITE_URL not set in .env"); return
    print(f"Site: {wp.SITE}\nCollecting sitemap URLs...")
    targets, kind_of = collect_urls()
    if args.max:
        targets = targets[:args.max]
    print(f"  {len(targets)} content URLs\nCrawling...")

    titles, outlinks, errors = {}, {}, []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for url, title, out in ex.map(crawl, targets):
            if out is None:
                errors.append(url); continue
            titles[url] = title; outlinks[url] = out

    inbound = {t: set() for t in targets}
    for src, outs in outlinks.items():
        for dst in outs:
            if dst in inbound and dst != src:
                inbound[dst].add(src)

    n = len(outlinks)
    chrome_cut = CHROME_FRACTION * max(n, 1)
    rows = []
    for t in targets:
        c = len(inbound[t])
        cls = ("GLOBAL" if c >= chrome_cut else "ORPHAN" if c == 0 else "contextual")
        rows.append({"url": t, "kind": kind_of[t], "title": titles.get(t, ""),
                     "inbound": c, "class": cls,
                     "linked_from": sorted(inbound[t])})
    rows.sort(key=lambda r: (r["inbound"], r["url"]))

    orphans = [r for r in rows if r["class"] == "ORPHAN"]
    thin = [r for r in rows if r["class"] == "contextual" and r["inbound"] <= THIN_MAX]
    glob = [r for r in rows if r["class"] == "GLOBAL"]

    report = {"site": wp.SITE, "crawled": n, "errors": errors,
              "summary": {"total": len(rows), "orphans": len(orphans),
                          "thin": len(thin), "global": len(glob)}, "rows": rows}
    path = wp.save("link_audit.json", report)

    print(f"\nCrawled {n} pages ({len(errors)} errors)")
    print(f"SUMMARY: {len(orphans)} orphans | {len(thin)} thin (<= {THIN_MAX}) | "
          f"{len(glob)} nav/footer | {len(rows)} total\n")
    print(f"ORPHANS ({len(orphans)}):")
    for r in orphans:
        print(f"  [{r['kind']:10}] {r['url']}")
    print(f"\nTHIN ({len(thin)}):")
    for r in thin:
        print(f"  {r['inbound']} in  {r['url']}")
    print(f"\nFull data -> {path}")


if __name__ == "__main__":
    main()
