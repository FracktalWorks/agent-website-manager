#!/usr/bin/env python3
"""
WordPress Performance Analyzer

Analyzes page speed, measures Core Web Vitals, identifies performance
bottlenecks, and generates optimization recommendations. Uses Google
PageSpeed Insights API (optional key for higher quotas) or falls back
to basic HTTP timing analysis.

Usage:
    python wp_performance.py --action analyze --url https://mysite.com
    python wp_performance.py --action analyze-all
    python wp_performance.py --action web-vitals --url https://mysite.com
"""

import os, sys, json, argparse, time
from pathlib import Path
from urllib.parse import urljoin
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")
PSI_KEY = os.getenv("PAGESPEED_API_KEY", "")


def _http_headers_analysis(url):
    """Analyze HTTP response headers for caching and performance."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"},
                         timeout=15, allow_redirects=True)
        headers = dict(r.headers)
        elapsed = r.elapsed.total_seconds()
        size_kb = round(len(r.content) / 1024, 1)

        checks = {
            "cache_control": "cache-control" in headers,
            "gzip_enabled": headers.get("content-encoding") == "gzip",
            "server_header": headers.get("server", "hidden"),
            "x_cache": headers.get("x-litespeed-cache", headers.get("x-cache", "not detected")),
            "cdn": any(h in str(headers).lower() for h in ["x-cdn", "cf-cache", "x-hw"]),
            "keep_alive": headers.get("connection", "").lower() == "keep-alive",
            "vary": headers.get("vary", ""),
        }

        return {
            "url": url, "status": r.status_code,
            "response_time_seconds": round(elapsed, 3),
            "page_size_kb": size_kb,
            "checks": checks,
            "raw_headers": {k: v[:200] for k, v in headers.items()},
        }
    except Exception as e:
        return {"url": url, "error": str(e)}


def action_analyze(args):
    """Analyze a single URL using available methods."""
    url = args.url or WP_URL
    result = {"url": url, "methods": {}}

    # HTTP timing analysis (always available)
    result["methods"]["http_headers"] = _http_headers_analysis(url)

    # Try PageSpeed Insights if API key is available
    if PSI_KEY:
        try:
            psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {"url": url, "key": PSI_KEY, "strategy": args.strategy or "mobile"}
            r = requests.get(psi_url, params=params, timeout=30)
            psi = r.json()
            lighthouse = psi.get("lighthouseResult", {})
            audits = lighthouse.get("audits", {})
            result["methods"]["pagespeed_insights"] = {
                "performance_score": lighthouse.get("categories", {}).get(
                    "performance", {}).get("score", 0) * 100,
                "fcp": audits.get("first-contentful-paint", {}).get("displayValue", ""),
                "lcp": audits.get("largest-contentful-paint", {}).get("displayValue", ""),
                "tbt": audits.get("total-blocking-time", {}).get("displayValue", ""),
                "cls": audits.get("cumulative-layout-shift", {}).get("displayValue", ""),
                "si": audits.get("speed-index", {}).get("displayValue", ""),
            }
        except Exception as e:
            result["methods"]["pagespeed_insights"] = {"error": str(e)}
    else:
        result["methods"]["pagespeed_insights"] = {
            "note": "Set PAGESPEED_API_KEY in .env for Google PageSpeed Insights data."
        }

    # Compile recommendations
    recs = []
    http_result = result["methods"]["http_headers"]
    if "error" not in http_result:
        c = http_result.get("checks", {})
        if not c.get("cache_control"):
            recs.append("Enable browser caching via LiteSpeed Cache plugin")
        if not c.get("x_cache") or c["x_cache"] == "not detected":
            recs.append("Enable page caching (LSCache or similar)")
        if not c.get("gzip_enabled"):
            recs.append("Enable GZIP/Brotli compression")
        if not c.get("cdn"):
            recs.append("Set up CDN (Hostinger CDN or Cloudflare)")
        if http_result.get("page_size_kb", 0) > 1000:
            recs.append(f"Page is large ({http_result['page_size_kb']}KB). "
                        "Optimize images and minify assets.")

    result["recommendations"] = recs
    return result


def action_analyze_all(args):
    """Analyze all core pages of the WordPress site."""
    # Fetch all published pages and posts
    auth = __import__('base64').b64encode(
        f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}

    urls = [WP_URL]
    try:
        # Get pages
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/pages",
                         headers=headers, params={"per_page": 20, "status": "publish"},
                         timeout=15)
        for p in r.json():
            urls.append(p.get("link", ""))

        # Get posts
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts",
                         headers=headers, params={"per_page": 20, "status": "publish"},
                         timeout=15)
        for p in r.json():
            urls.append(p.get("link", ""))
    except Exception:
        pass

    urls = list(set(urls))[:args.limit or 10]
    results = []
    for url in urls:
        results.append(_http_headers_analysis(url))

    # Sort by response time (slowest first)
    results.sort(key=lambda x: x.get("response_time_seconds", 0), reverse=True)

    avg_time = sum(r.get("response_time_seconds", 0) for r in results) / max(len(results), 1)
    return {"pages_analyzed": len(results), "average_response_time": round(avg_time, 3),
            "slowest_pages": results[:5], "all_results": results}


def action_web_vitals(args):
    """Measure Core Web Vitals for a URL."""
    url = args.url or WP_URL

    if not PSI_KEY:
        return {"error": True, "message": "PAGESPEED_API_KEY required for Web Vitals data."}

    try:
        import base64 as b64
        psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {"url": url, "key": PSI_KEY, "strategy": args.strategy or "mobile",
                  "category": "performance"}
        r = requests.get(psi_url, params=params, timeout=30)
        data = r.json()
        audits = data.get("lighthouseResult", {}).get("audits", {})

        return {
            "url": url, "strategy": args.strategy or "mobile",
            "lcp": {
                "value": audits.get("largest-contentful-paint", {}).get("displayValue", ""),
                "score": audits.get("largest-contentful-paint", {}).get("score", 0),
            },
            "fid_inp": {
                "value": audits.get("interaction-to-next-paint", {}).get("displayValue",
                         audits.get("max-potential-fid", {}).get("displayValue", "N/A")),
            },
            "cls": {
                "value": audits.get("cumulative-layout-shift", {}).get("displayValue", ""),
                "score": audits.get("cumulative-layout-shift", {}).get("score", 0),
            },
            "tbt": {
                "value": audits.get("total-blocking-time", {}).get("displayValue", ""),
                "score": audits.get("total-blocking-time", {}).get("score", 0),
            },
            "fcp": {
                "value": audits.get("first-contentful-paint", {}).get("displayValue", ""),
            },
            "speed_index": {
                "value": audits.get("speed-index", {}).get("displayValue", ""),
            },
            "overall_score": round(data.get("lighthouseResult", {}).get("categories", {}).get(
                "performance", {}).get("score", 0) * 100),
        }
    except Exception as e:
        return {"error": True, "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="WordPress Performance Analyzer")
    parser.add_argument("--action", required=True,
                        choices=["analyze", "analyze-all", "web-vitals", "full-audit"])
    parser.add_argument("--url")
    parser.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    parser.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    if args.action == "full-audit":
        url = args.url or WP_URL
        print(json.dumps({
            "mobile": action_web_vitals(type('', (), {
                'url': url, 'strategy': 'mobile'})()),
            "desktop": action_web_vitals(type('', (), {
                'url': url, 'strategy': 'desktop'})()),
        }, indent=2))
        return

    actions = {
        "analyze": lambda: action_analyze(args),
        "analyze-all": lambda: action_analyze_all(args),
        "web-vitals": lambda: action_web_vitals(args),
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
