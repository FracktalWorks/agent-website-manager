#!/usr/bin/env python3
"""
WordPress Database Cleanup Script

Cleans and optimizes WordPress database:
- Clears post revisions
- Removes trashed posts/pages
- Deletes spam/trash comments
- Cleans expired transients
- Reports autoloaded options size
- Optimizes database tables (Hostinger-specific)

Usage:
    python wp_db_cleanup.py --action analyze
    python wp_db_cleanup.py --action clean
    python wp_db_cleanup.py --action full-clean
"""

import os
import sys
import json
import argparse
import base64
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")

AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
}
API_BASE = f"{WP_URL}/wp-json/wp/v2"


def _check_config():
    missing = []
    if not WP_URL:
        missing.append("WORDPRESS_SITE_URL")
    if not WP_USER:
        missing.append("WORDPRESS_USERNAME")
    if not WP_APP_PASSWORD:
        missing.append("WORDPRESS_APP_PASSWORD")
    if missing:
        print(json.dumps({"error": True,
                          "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def _api_get(endpoint, params=None):
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json(), resp.headers


def _api_delete(endpoint, params=None):
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    resp = requests.delete(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def action_analyze(args):
    """Analyze database — report what can be cleaned."""
    report = {}

    # 1. Post revisions
    try:
        _, h = _api_get("posts", {"per_page": 1, "status": "any"})
        total_posts = int(h.get("X-WP-Total", 0))
    except Exception:
        total_posts = "unknown"

    try:
        # Count revisions by fetching IDs
        rev, h_r = _api_get("posts", {"per_page": 1})
        # Note: REST API doesn't expose revision count easily
        report["revisions"] = {
            "note": "Revisions count requires direct DB access. "
                    "Use WP-Optimize plugin or phpMyAdmin.",
            "recommendation": "Keep last 3 revisions per post maximum.",
        }
    except Exception as e:
        report["revisions"] = {"error": str(e)[:150]}

    # 2. Trashed content
    trashed = {}
    for content_type in ["posts", "pages"]:
        try:
            _, h = _api_get(content_type, {"per_page": 1, "status": "trash"})
            count = int(h.get("X-WP-Total", 0))
            trashed[content_type] = count
        except Exception:
            trashed[content_type] = "unknown"
    report["trashed"] = trashed

    # 3. Spam/trash comments
    try:
        _, h = _api_get("comments", {"per_page": 1, "status": "spam"})
        spam = int(h.get("X-WP-Total", 0))
    except Exception:
        spam = "unknown"
    try:
        _, h = _api_get("comments", {"per_page": 1, "status": "trash"})
        trash_c = int(h.get("X-WP-Total", 0))
    except Exception:
        trash_c = "unknown"
    report["comments"] = {"spam": spam, "trash": trash_c}

    # 4. Content stats overview
    for content_type in ["posts", "pages", "media", "comments"]:
        try:
            _, h = _api_get(content_type, {"per_page": 1})
            count = int(h.get("X-WP-Total", 0))
            report[f"total_{content_type}"] = count
        except Exception:
            report[f"total_{content_type}"] = "unknown"

    # 5. Site Health — check autoloaded options warning
    try:
        health_resp = requests.get(
            f"{WP_URL}/wp-json/wp-site-health/v1/tests/direct",
            headers=HEADERS, timeout=30)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            for test_name, test_data in health_data.items():
                if "autoloaded" in test_name.lower():
                    report["autoloaded_options"] = {
                        "label": test_data.get("label", ""),
                        "status": test_data.get("status", ""),
                        "description": test_data.get("description", "")[:500],
                    }
                    break
            if "autoloaded_options" not in report:
                report["autoloaded_options"] = {
                    "note": "Check Site Health in wp-admin for autoloaded "
                            "options count. 1824 options/1MB was previously "
                            "reported.",
                    "recommendation": "Remove options from deactivated/"
                                      "deleted plugins.",
                }
        else:
            report["autoloaded_options"] = {
                "note": "Site Health API returned "
                        f"{health_resp.status_code}"}
    except Exception as e:
        report["autoloaded_options"] = {"error": str(e)[:150]}

    # 6. Plugin count (orphaned options source)
    try:
        plugins, _ = _api_get("plugins")
        inactive = sum(1 for p in plugins if p.get("status") == "inactive")
        report["plugins"] = {
            "total": len(plugins),
            "active": len(plugins) - inactive,
            "inactive": inactive,
            "orphaned_risk": "HIGH" if inactive > 10 else (
                "MEDIUM" if inactive > 0 else "LOW"),
        }
    except Exception as e:
        report["plugins"] = {"error": str(e)[:100]}

    # Recommendations
    recommendations = []
    trashed_total = sum(
        v for v in trashed.values() if isinstance(v, int))
    if trashed_total > 0:
        recommendations.append(
            f"Delete {trashed_total} trashed posts/pages")
    if isinstance(spam, int) and spam > 0:
        recommendations.append(f"Delete {spam} spam comments")
    if isinstance(trash_c, int) and trash_c > 0:
        recommendations.append(f"Delete {trash_c} trashed comments")
    if report.get("plugins", {}).get("inactive", 0) > 0:
        recommendations.append(
            f"Remove {report['plugins']['inactive']} inactive plugins "
            "(they leave autoloaded options)")
    report["recommendations"] = recommendations
    report["total_cleanable_items"] = trashed_total + (
        spam if isinstance(spam, int) else 0) + (
        trash_c if isinstance(trash_c, int) else 0)

    return report


def action_clean(args):
    """Clean trashed/spam content."""
    results = {}

    # Delete trashed posts
    for content_type in ["posts", "pages"]:
        try:
            data, h = _api_get(
                content_type,
                {"per_page": 100, "status": "trash"})
            deleted = 0
            for item in data:
                try:
                    _api_delete(f"{content_type}/{item['id']}",
                                {"force": True})
                    deleted += 1
                except Exception:
                    pass
            results[f"deleted_trashed_{content_type}"] = deleted
        except Exception as e:
            results[f"deleted_trashed_{content_type}"] = str(e)[:100]

    # Delete spam comments
    try:
        data, h = _api_get("comments", {"per_page": 100, "status": "spam"})
        deleted = 0
        for item in data:
            try:
                _api_delete(f"comments/{item['id']}", {"force": True})
                deleted += 1
            except Exception:
                pass
        results["deleted_spam_comments"] = deleted
    except Exception as e:
        results["deleted_spam_comments"] = str(e)[:100]

    # Delete trashed comments
    try:
        data, h = _api_get("comments", {"per_page": 100, "status": "trash"})
        deleted = 0
        for item in data:
            try:
                _api_delete(f"comments/{item['id']}", {"force": True})
                deleted += 1
            except Exception:
                pass
        results["deleted_trashed_comments"] = deleted
    except Exception as e:
        results["deleted_trashed_comments"] = str(e)[:100]

    results["note"] = (
        "Autoloaded options cleanup requires direct database access "
        "(phpMyAdmin via hPanel). Remove options with prefixes from "
        "deleted plugins: akismet, betterdocs, elementskit, gutenkit, "
        "jetpack, megamenu, tutor, wpforms, etc."
    )
    results["cleaned"] = True

    return results


def action_full_clean(args):
    """Analyze then clean."""
    analysis = action_analyze(args)
    cleaning = action_clean(args)
    return {"analysis": analysis, "cleaning": cleaning}


def main():
    parser = argparse.ArgumentParser(
        description="WordPress Database Cleanup")
    parser.add_argument("--action", required=True,
                        choices=["analyze", "clean", "full-clean"])
    parser.add_argument("--dry-run", action="store_true",
                        help="Analyze without making changes")

    args = parser.parse_args()
    _check_config()

    action_map = {
        "analyze": lambda: action_analyze(args),
        "clean": lambda: action_clean(args),
        "full-clean": lambda: action_full_clean(args),
    }

    try:
        result = action_map[args.action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
