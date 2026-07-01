#!/usr/bin/env python3
"""
WordPress SEO Analyzer

Analyzes on-page SEO for WordPress pages/posts and generates
actionable optimization recommendations. Checks meta titles, descriptions,
heading structure, content length, keyword usage, image alt text, internal
links, and readability.

Usage:
    python wp_seo_analyze.py --url https://mysite.com/my-page
    python wp_seo_analyze.py --id 42 --type page
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a page and return BeautifulSoup object."""
    resp = requests.get(url, headers={"User-Agent": "Agent-Website-Manager/1.0"}, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser"), resp.text


def analyze_seo(soup: BeautifulSoup, raw_html: str, url: str) -> dict:
    """Run full SEO analysis on a page."""
    issues = []
    passes = []
    recommendations = []

    # 1. Title tag
    title_tag = soup.find("title")
    title_text = title_tag.get_text().strip() if title_tag else ""
    if not title_text:
        issues.append({"check": "Title tag", "severity": "high", "detail": "Missing <title> tag"})
    elif len(title_text) < 30:
        issues.append({"check": "Title tag", "severity": "medium", "detail": f"Title too short ({len(title_text)} chars). Aim for 50-60 chars."})
    elif len(title_text) > 70:
        issues.append({"check": "Title tag", "severity": "low", "detail": f"Title too long ({len(title_text)} chars). Keep under 60 chars."})
    else:
        passes.append({"check": "Title tag", "detail": f"Good length ({len(title_text)} chars)"})

    # 2. Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_content = meta_desc.get("content", "") if meta_desc else ""
    if not desc_content:
        issues.append({"check": "Meta description", "severity": "high", "detail": "Missing meta description"})
    elif len(desc_content) < 120:
        issues.append({"check": "Meta description", "severity": "medium", "detail": f"Description too short ({len(desc_content)} chars). Aim for 150-160 chars."})
    elif len(desc_content) > 165:
        issues.append({"check": "Meta description", "severity": "low", "detail": f"Description too long ({len(desc_content)} chars)."})
    else:
        passes.append({"check": "Meta description", "detail": f"Good length ({len(desc_content)} chars)"})

    # 3. H1 tag
    h1_tags = soup.find_all("h1")
    if not h1_tags:
        issues.append({"check": "H1 heading", "severity": "high", "detail": "Missing <h1> tag — every page needs one H1"})
    elif len(h1_tags) > 1:
        issues.append({"check": "H1 heading", "severity": "medium", "detail": f"Multiple H1 tags ({len(h1_tags)}). Use only one H1 per page."})
    else:
        passes.append({"check": "H1 heading", "detail": f"Single H1: '{h1_tags[0].get_text().strip()[:80]}'"})

    # 4. Heading hierarchy
    headings = []
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        if tags:
            headings.append({"level": f"h{level}", "count": len(tags), "texts": [t.get_text().strip()[:80] for t in tags[:5]]})
    if not any(h["level"] == "h2" for h in headings):
        recommendations.append("Add H2 subheadings to break content into scannable sections.")
    if not any(h["level"] == "h3" for h in headings if len(headings) > 2):
        recommendations.append("Consider adding H3 sub-subheadings for detailed content sections.")

    # 5. Content length
    body = soup.find("body")
    text = body.get_text(separator=" ", strip=True) if body else ""
    word_count = len(text.split())
    if word_count < 300:
        issues.append({"check": "Content length", "severity": "medium", "detail": f"Thin content ({word_count} words). Aim for 300+ words for SEO."})
    elif word_count < 600:
        recommendations.append(f"Content is moderate ({word_count} words). For competitive topics, aim for 1000+ words.")
    else:
        passes.append({"check": "Content length", "detail": f"Good ({word_count} words)"})

    # 6. Images with alt text
    images = soup.find_all("img")
    imgs_without_alt = [img.get("src", "")[:80] for img in images if not img.get("alt")]
    if imgs_without_alt:
        issues.append({"check": "Image alt text", "severity": "medium", "detail": f"{len(imgs_without_alt)} image(s) missing alt text", "images": imgs_without_alt[:5]})
    else:
        passes.append({"check": "Image alt text", "detail": f"All {len(images)} images have alt text"})

    # 7. Canonical URL
    canonical = soup.find("link", rel="canonical")
    if not canonical:
        issues.append({"check": "Canonical URL", "severity": "medium", "detail": "Missing canonical URL tag"})
    else:
        passes.append({"check": "Canonical URL", "detail": canonical.get("href", "")})

    # 8. Open Graph tags
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    missing_og = []
    if not og_title:
        missing_og.append("og:title")
    if not og_desc:
        missing_og.append("og:description")
    if not og_image:
        missing_og.append("og:image")
    if missing_og:
        issues.append({"check": "Open Graph tags", "severity": "low", "detail": f"Missing: {', '.join(missing_og)}"})
    else:
        passes.append({"check": "Open Graph tags", "detail": "All essential OG tags present"})

    # 9. Internal links
    links = soup.find_all("a", href=True)
    internal_links = [l for l in links if WP_URL in l["href"] or l["href"].startswith("/")]
    external_links = [l for l in links if l["href"].startswith("http") and WP_URL not in l["href"]]
    if len(internal_links) < 3:
        recommendations.append("Add more internal links to other pages on your site.")
    else:
        passes.append({"check": "Internal links", "detail": f"{len(internal_links)} internal, {len(external_links)} external"})

    # 10. Schema / Structured data
    schemas = soup.find_all("script", type="application/ld+json")
    if not schemas:
        recommendations.append("Add structured data (Schema.org) for rich snippets in search results.")
    else:
        passes.append({"check": "Structured data", "detail": f"{len(schemas)} schema block(s) found"})

    # Score
    total_checks = len(issues) + len(passes)
    score = round((len(passes) / total_checks * 100), 1) if total_checks > 0 else 0

    return {
        "url": url,
        "seo_score": f"{score}/100",
        "word_count": word_count,
        "title": title_text,
        "meta_description": desc_content,
        "headings": headings,
        "image_count": len(images),
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "issues": sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]),
        "passes": passes,
        "recommendations": recommendations,
    }


def main():
    parser = argparse.ArgumentParser(description="WordPress SEO Analyzer")
    parser.add_argument("--url", help="Full URL to analyze (e.g., https://mysite.com/page)")
    parser.add_argument("--id", type=int, help="WordPress post/page ID (uses WORDPRESS_SITE_URL)")
    parser.add_argument("--type", default="page", choices=["page", "post"], help="Content type (for --id)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON only")

    args = parser.parse_args()

    if not args.url and not args.id:
        print(json.dumps({"error": True, "message": "Provide --url or --id"}))
        sys.exit(1)

    url = args.url
    if not url:
        url = f"{WP_URL}/?p={args.id}" if args.type == "post" else f"{WP_URL}/?page_id={args.id}"

    try:
        soup, raw_html = fetch_page(url)
        result = analyze_seo(soup, raw_html, url)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"SEO ANALYSIS: {url}")
            print(f"{'='*60}")
            print(f"Score: {result['seo_score']}")
            print(f"Words: {result['word_count']}")
            print(f"\n--- Issues ({len(result['issues'])}) ---")
            for issue in result["issues"]:
                print(f"  [{issue['severity'].upper()}] {issue['check']}: {issue['detail']}")
            print(f"\n--- Passed ({len(result['passes'])}) ---")
            for p in result["passes"]:
                print(f"  ✓ {p['check']}: {p['detail']}")
            if result["recommendations"]:
                print(f"\n--- Recommendations ---")
                for r in result["recommendations"]:
                    print(f"  💡 {r}")
            print()

    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
