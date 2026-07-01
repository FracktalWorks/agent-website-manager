#!/usr/bin/env python3
"""
WordPress Content Auditor

Broken link detection, orphan page finder, thin content checker,
duplicate meta data detector, redirect chain analyzer, and internal
link structure analysis.

Usage:
    python wp_content_audit.py --action full
    python wp_content_audit.py --action broken-links
    python wp_content_audit.py --action orphans
"""

import os, sys, json, argparse, base64
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
API = f"{WP_URL}/wp-json/wp/v2"


def _check():
    missing = [v for v, k in [("WP_URL", WP_URL), ("WP_USER", WP_USER),
                ("WP_APP_PASSWORD", WP_APP_PASSWORD)] if not k]
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def _get_all_posts(post_type="pages", per_page=50):
    """Get all published items of a given type."""
    all_items = []
    params = {"per_page": per_page, "page": 1, "status": "publish",
              "_fields": "id,title,link,slug,content,modified,meta,yoast_head_json"}
    while True:
        r = requests.get(f"{API}/{post_type}", headers=HEADERS,
                         params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        all_items.extend(data)
        total_pages = int(r.headers.get("X-WP-TotalPages", 1))
        if params["page"] >= total_pages:
            break
        params["page"] += 1
    return all_items


def _extract_links(html_content, base_url):
    """Extract all links from HTML content."""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        links.append({"href": href, "full_url": full_url,
                      "internal": parsed.netloc == urlparse(WP_URL).netloc,
                      "text": a.get_text(strip=True)[:100]})
    return links


def _check_link(url):
    """Check if a URL is accessible."""
    try:
        r = requests.head(url, headers={"User-Agent": "Mozilla/5.0"},
                          timeout=10, allow_redirects=True)
        return {"url": url, "status": r.status_code,
                "ok": r.status_code < 400, "redirects": len(r.history),
                "final_url": r.url}
    except requests.ConnectionError:
        return {"url": url, "status": 0, "ok": False, "error": "Connection refused"}
    except requests.Timeout:
        return {"url": url, "status": 0, "ok": False, "error": "Timeout"}
    except Exception as e:
        return {"url": url, "status": 0, "ok": False, "error": str(e)[:100]}


# ═══════════════════════════════════════════════════════════════════════════
# BROKEN LINKS
# ═══════════════════════════════════════════════════════════════════════════

def action_broken_links(args):
    """Find broken internal links."""
    print("Fetching all pages and posts...", file=sys.stderr)
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")
    all_content = pages + posts

    # Collect all links
    all_links = []
    for item in all_content:
        content = item.get("content", {}).get("rendered", "")
        links = _extract_links(content, item.get("link", WP_URL))
        for link in links:
            if link["internal"]:
                all_links.append({"page_id": item["id"],
                                  "page_title": item["title"]["rendered"],
                                  "page_url": item["link"],
                                  "link_url": link["full_url"],
                                  "link_text": link["text"]})

    # Deduplicate and check unique links
    unique_urls = list(set(l["link_url"] for l in all_links))
    print(f"Checking {len(unique_urls)} unique internal links...", file=sys.stderr)

    broken = []
    for url in unique_urls[:args.limit or 200]:
        result = _check_link(url)
        if not result["ok"]:
            # Find which pages link to this broken URL
            linked_from = [l for l in all_links if l["link_url"] == url]
            broken.append({"broken_url": url, "status": result["status"],
                           "error": result.get("error", ""),
                           "linked_from": [
                               {"page": l["page_title"], "url": l["page_url"]}
                               for l in linked_from[:5]],
                           "total_linked_from": len(linked_from)})

    broken.sort(key=lambda x: x["total_linked_from"], reverse=True)
    return {"total_links_checked": len(unique_urls), "broken_count": len(broken),
            "broken_links": broken, "recommendation": "Fix or redirect broken links. "
            "Use a 301 redirect for moved pages."}


def action_broken_external(args):
    """Check external (outbound) links."""
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")
    all_content = pages + posts

    external_links = []
    for item in all_content:
        content = item.get("content", {}).get("rendered", "")
        links = _extract_links(content, item.get("link", WP_URL))
        for link in links:
            if not link["internal"]:
                external_links.append({"page_id": item["id"],
                                       "page_title": item["title"]["rendered"],
                                       "external_url": link["full_url"],
                                       "link_text": link["text"]})

    unique_external = list(set(l["external_url"] for l in external_links))
    print(f"Checking {len(unique_external)} external links...", file=sys.stderr)

    broken = []
    for url in unique_external[:args.limit or 50]:
        result = _check_link(url)
        if not result["ok"]:
            linked_from = [l for l in external_links if l["external_url"] == url]
            broken.append({"url": url, "status": result["status"],
                           "linked_from_count": len(linked_from),
                           "pages": [l["page_title"] for l in linked_from[:3]]})

    return {"external_checked": len(unique_external), "broken_external": len(broken),
            "broken": broken}


# ═══════════════════════════════════════════════════════════════════════════
# ORPHAN PAGES
# ═══════════════════════════════════════════════════════════════════════════

def action_orphans(args):
    """Find pages with zero inbound internal links."""
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")

    # Build link graph
    all_page_urls = {p["link"]: {"id": p["id"], "title": p["title"]["rendered"]}
                     for p in pages}
    linked_to = set()

    for item in pages + posts:
        content = item.get("content", {}).get("rendered", "")
        links = _extract_links(content, item.get("link", WP_URL))
        for link in links:
            if link["internal"] and link["full_url"] in all_page_urls:
                linked_to.add(link["full_url"])

    orphans = []
    for url, info in all_page_urls.items():
        if url not in linked_to:
            orphans.append({"id": info["id"], "title": info["title"], "url": url})

    # Exclude pages that are likely intentional (front page, posts page, etc.)
    likely_intentional = []
    true_orphans = []
    for o in orphans:
        slug = o["url"].rstrip("/").split("/")[-1]
        if slug in ("", "home", "blog", "shop"):
            likely_intentional.append(o)
        else:
            true_orphans.append(o)

    return {
        "total_pages": len(pages),
        "orphaned_pages": len(true_orphans),
        "likely_intentional": len(likely_intentional),
        "orphans": true_orphans,
        "intentional_orphans": likely_intentional,
        "recommendation": "Add internal links to orphan pages from related content, "
                          "or add them to navigation/sitemap.",
    }


# ═══════════════════════════════════════════════════════════════════════════
# CONTENT QUALITY
# ═══════════════════════════════════════════════════════════════════════════

def action_thin_content(args):
    """Find pages with low word count."""
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")
    min_words = args.min_words or 300

    thin = []
    for item in pages + posts:
        content = item.get("content", {}).get("rendered", "")
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(text.split())
        if 0 < word_count < min_words:
            thin.append({"id": item["id"], "title": item["title"]["rendered"],
                         "url": item["link"], "word_count": word_count,
                         "type": "page" if "page" in item.get("type", "") else "post"})

    thin.sort(key=lambda x: x["word_count"])
    return {"min_word_threshold": min_words, "thin_content_count": len(thin),
            "items": thin, "recommendation": "Expand thin pages to 300+ words for better SEO."}


def action_duplicate_titles(args):
    """Find duplicate meta titles across pages."""
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")
    all_items = pages + posts

    titles = defaultdict(list)
    for item in all_items:
        title = item.get("title", {}).get("rendered", "")
        if title:
            titles[title].append({"id": item["id"], "url": item["link"],
                                  "type": item.get("type", "")})

    duplicates = {t: items for t, items in titles.items() if len(items) > 1}
    return {"duplicate_titles": len(duplicates),
            "items": {t: items for t, items in list(duplicates.items())[:20]},
            "recommendation": "Each page should have a unique title tag."}


def action_duplicate_descriptions(args):
    """Check for duplicate meta descriptions from Yoast."""
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")

    descs = defaultdict(list)
    for item in pages + posts:
        yoast = item.get("yoast_head_json", {})
        desc = yoast.get("description", "")
        if desc:
            descs[desc].append({"id": item["id"], "title": item["title"]["rendered"]})

    duplicates = {d: items for d, items in descs.items() if len(items) > 1}
    return {"duplicate_descriptions": len(duplicates),
            "items": {d[:80]: items for d, items in list(duplicates.items())[:20]}}


def action_missing_meta(args):
    """Find pages missing essential meta tags."""
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")

    missing = []
    for item in pages + posts:
        yoast = item.get("yoast_head_json", {})
        issues = []
        if not yoast.get("title"):
            issues.append("title")
        if not yoast.get("description"):
            issues.append("meta_description")
        if not yoast.get("og_title"):
            issues.append("og_title")
        if not yoast.get("og_image"):
            issues.append("og_image")
        if issues:
            missing.append({"id": item["id"], "title": item["title"]["rendered"],
                            "url": item["link"], "missing": issues})

    return {"missing_meta": len(missing), "items": missing[:50],
            "recommendation": "Install and configure Yoast SEO or RankMath for proper meta tags."}


def action_link_structure(args):
    """Analyze internal link structure."""
    pages = _get_all_posts("pages")
    posts = _get_all_posts("posts")

    # Count inbound links per page
    all_page_urls = {p["link"]: {"id": p["id"], "title": p["title"]["rendered"],
                                  "inbound": 0, "outbound": 0}
                     for p in pages}

    for item in pages + posts:
        content = item.get("content", {}).get("rendered", "")
        links = _extract_links(content, item.get("link", WP_URL))
        internal_links = [l for l in links if l["internal"]]
        # Count outbound from this page
        if item["link"] in all_page_urls:
            all_page_urls[item["link"]]["outbound"] = len(internal_links)
        # Count inbound to target pages
        for link in internal_links:
            if link["full_url"] in all_page_urls:
                all_page_urls[link["full_url"]]["inbound"] += 1

    # Most linked-to pages
    ranked = sorted(all_page_urls.values(), key=lambda x: x["inbound"], reverse=True)
    dead_ends = [p for p in ranked if p["outbound"] == 0]

    return {
        "total_pages": len(pages),
        "most_linked": ranked[:10],
        "dead_end_pages": len(dead_ends),
        "dead_ends": dead_ends[:20],
        "avg_inbound_links": round(sum(p["inbound"] for p in ranked) / max(len(ranked), 1), 1),
        "recommendation": "Every page should have at least 2-3 inbound internal links. "
                          "Dead-end pages should link to related content.",
    }


def action_report(args):
    """Generate a prioritized content health report."""
    orphan_result = action_orphans(args)
    broken_result = action_broken_links(args)
    thin_result = action_thin_content(args)
    dup_result = action_duplicate_titles(args)
    link_result = action_link_structure(args)

    priorities = []
    if broken_result["broken_count"] > 0:
        priorities.append({"priority": 1, "issue": "Broken internal links",
                           "count": broken_result["broken_count"],
                           "action": "Fix or redirect broken links"})
    if orphan_result["orphaned_pages"] > 0:
        priorities.append({"priority": 2, "issue": "Orphan pages",
                           "count": orphan_result["orphaned_pages"],
                           "action": "Add internal links to orphan pages"})
    if thin_result["thin_content_count"] > 0:
        priorities.append({"priority": 3, "issue": "Thin content",
                           "count": thin_result["thin_content_count"],
                           "action": "Expand pages to 300+ words"})
    if dup_result["duplicate_titles"] > 0:
        priorities.append({"priority": 4, "issue": "Duplicate titles",
                           "count": dup_result["duplicate_titles"],
                           "action": "Make each page title unique"})
    if link_result["dead_end_pages"] > 0:
        priorities.append({"priority": 5, "issue": "Dead-end pages",
                           "count": link_result["dead_end_pages"],
                           "action": "Add outbound links to dead-end pages"})

    return {
        "timestamp": datetime.now().isoformat(),
        "site": WP_URL,
        "content_health_score": round(
            max(0, 100 - (broken_result["broken_count"] * 5)
                - (orphan_result["orphaned_pages"] * 3)
                - (thin_result["thin_content_count"] * 2)), 1),
        "prioritized_fixes": sorted(priorities, key=lambda x: x["priority"]),
    }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Content Auditor")
    parser.add_argument("--action", required=True, choices=[
        "full", "broken-links", "broken-external", "orphans",
        "thin-content", "duplicate-titles", "duplicate-descriptions",
        "missing-meta", "redirect-chains", "link-structure",
        "audit", "report",
    ])
    parser.add_argument("--min-words", dest="min_words", type=int, default=300)
    parser.add_argument("--type", choices=["page", "post"], default="page")
    parser.add_argument("--limit", type=int, default=200)

    args = parser.parse_args()
    _check()

    actions = {
        "broken-links": lambda: action_broken_links(args),
        "broken-external": lambda: action_broken_external(args),
        "orphans": lambda: action_orphans(args),
        "thin-content": lambda: action_thin_content(args),
        "duplicate-titles": lambda: action_duplicate_titles(args),
        "duplicate-descriptions": lambda: action_duplicate_descriptions(args),
        "missing-meta": lambda: action_missing_meta(args),
        "link-structure": lambda: action_link_structure(args),
        "report": lambda: action_report(args),
        "full": lambda: {
            "broken_links": action_broken_links(args),
            "orphans": action_orphans(args),
            "thin_content": action_thin_content(args),
            "duplicate_titles": action_duplicate_titles(args),
            "link_structure": action_link_structure(args),
        },
        "redirect-chains": lambda: {
            "note": "Redirect chain detection requires crawling the site. "
                    "Use a dedicated crawler like Screaming Frog or run a "
                    "manual check via: curl -sI -L <url>",
        },
        "audit": lambda: {
            "pages": action_broken_links(args),
            "note": "Use --type post for blog posts audit",
        },
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
