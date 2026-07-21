# -*- coding: utf-8 -*-
"""Site inventory + lightweight health probe (the 'what exists / is it OK' pass).

REST-only signals that feed the Architecture and Health reports:
  - Every content URL from the XML sitemaps, grouped by type
  - Registered post types + published counts (catches stranded/mismatched CPTs)
  - Active vs inactive plugins (catches a disabled plugin that stranded content)
  - HTTP status of a set of key URLs (catches 404s / redirects)

Deeper DB-level health (table bloat, autoload size, stuck imports) needs the
database — get a phpMyAdmin link via the Hostinger MCP
(`hosting_getPhpMyAdminLinkV1`) and run read-only SQL; see SKILL.md.

Usage:
  python site_inventory.py
  python site_inventory.py --check https://site.com/kb/ --check https://site.com/shop/
Outputs: outputs/<slug>/site_inventory.json (+ printed summary)
"""
import os, sys, re, argparse
from collections import Counter, defaultdict
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp_client as wp


def sitemap_inventory():
    idx = wp.fetch(f"{wp.SITE}/sitemap_index.xml")
    subs = [l for l in re.findall(r"<loc>(.*?)</loc>", idx) if l.endswith(".xml")]
    by_type, total = {}, 0
    for sm in subs:
        name = re.sub(r"-sitemap\.xml$", "", sm.rsplit("/", 1)[-1])
        urls = [unescape(u) for u in re.findall(r"<loc>(.*?)</loc>", wp.fetch(sm))]
        by_type[name] = {"count": len(urls), "urls": urls}
        total += len(urls)
    return {"sitemaps": subs, "by_type": by_type, "total_urls": total}


def posttype_counts():
    try:
        types = wp.req("types")
    except Exception as e:
        return {"error": str(e)}
    out = {}
    for key, meta in types.items():
        rb = meta.get("rest_base")
        if not rb:
            continue
        try:
            _, headers = wp.req_with_headers(f"{rb}?per_page=1&status=publish")
            out[key] = {"rest_base": rb, "published": int(headers.get("X-WP-Total", 0) or 0)}
        except Exception:
            out[key] = {"rest_base": rb, "published": None}
    return out


def plugin_status():
    try:
        plugins = wp.req("plugins")
    except Exception as e:
        return {"error": str(e)}
    active = [p["plugin"] for p in plugins if p.get("status") == "active"]
    inactive = [{"plugin": p["plugin"], "name": p.get("name")}
                for p in plugins if p.get("status") == "inactive"]
    return {"total": len(plugins), "active": len(active), "inactive": inactive}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="append", default=[], help="extra URL(s) to status-check")
    args = ap.parse_args()
    if not wp.SITE:
        print("WORDPRESS_SITE_URL not set"); return

    inv = sitemap_inventory()
    types = posttype_counts()
    plugins = plugin_status()

    checks = {u: wp.status_of(u) for u in args.check}

    report = {"site": wp.SITE, "inventory": inv, "post_types": types,
              "plugins": plugins, "url_checks": checks}
    path = wp.save("site_inventory.json", report)

    print(f"Site: {wp.SITE}")
    print(f"\nSITEMAP INVENTORY ({inv['total_urls']} URLs):")
    for name, d in inv["by_type"].items():
        print(f"  {name:16} {d['count']}")
    print("\nPOST TYPES (published counts):")
    if "error" not in types:
        for k, v in sorted(types.items(), key=lambda x: -(x[1]['published'] or 0)):
            print(f"  {k:20} {v['rest_base']:16} {v['published']}")
    print("\nPLUGINS:")
    if "error" not in plugins:
        print(f"  {plugins['active']} active / {plugins['total']} total")
        for p in plugins["inactive"]:
            print(f"    inactive: {p['plugin']}  {p['name']}")
    if checks:
        print("\nURL CHECKS:")
        for u, c in checks.items():
            print(f"  [{c}] {u}")
    print(f"\nFull data -> {path}")


if __name__ == "__main__":
    main()
