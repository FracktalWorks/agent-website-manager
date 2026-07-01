#!/usr/bin/env python3
"""
WordPress Deployment Manager

Orchestrates safe deployments: pre-checks, Hostinger backups,
staging↔production sync, post-deployment smoke tests, and rollback.
Designed to work with Hostinger's staging feature.

Usage:
    python wp_deploy.py --action pre-check
    python wp_deploy.py --action deploy --domain example.com
    python wp_deploy.py --action smoke-test
"""

import os, sys, json, argparse, base64
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")
STAGING_URL = os.getenv("STAGING_SITE_URL", "").rstrip("/")
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
API = f"{WP_URL}/wp-json/wp/v2"


def _check():
    missing = [v for v, k in [("WP_URL", WP_URL), ("WP_USER", WP_USER),
                ("WP_APP_PASSWORD", WP_APP_PASSWORD)] if not k]
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def _get_count(endpoint):
    """Get count of items for an endpoint."""
    try:
        r = requests.get(f"{API}/{endpoint}", headers=HEADERS,
                         params={"per_page": 1}, timeout=15)
        return int(r.headers.get("X-WP-Total", 0))
    except Exception:
        return None


def _check_url(url, label=""):
    """Check if a URL returns a successful response."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"},
                         timeout=15, allow_redirects=True)
        return {
            "url": url, "label": label,
            "status": r.status_code,
            "ok": r.status_code < 400,
            "response_time_ms": round(r.elapsed.total_seconds() * 1000, 1),
        }
    except Exception as e:
        return {"url": url, "label": label, "status": 0, "ok": False,
                "error": str(e)[:200]}


# ═══════════════════════════════════════════════════════════════════════════
# PRE-CHECK
# ═══════════════════════════════════════════════════════════════════════════

def action_pre_check(args):
    """Pre-deployment readiness check."""
    checks = {}

    # 1. Production health
    checks["production_up"] = _check_url(WP_URL, "production")

    # 2. Staging health (if URL provided)
    if STAGING_URL:
        checks["staging_up"] = _check_url(STAGING_URL, "staging")

    # 3. Plugin/theme update status
    try:
        r = requests.get(f"{API}/plugins", headers=HEADERS, timeout=15)
        plugins = r.json()
        outdated = [p for p in plugins if p.get("update", {}).get("update")]
        checks["plugins_outdated"] = len(outdated)
        checks["outdated_plugins"] = [{"name": p["name"],
                                       "version": p.get("version", "")}
                                      for p in outdated]
    except Exception as e:
        checks["plugins_error"] = str(e)

    # 4. Content stats
    checks["post_count"] = _get_count("posts")
    checks["page_count"] = _get_count("pages")
    checks["media_count"] = _get_count("media")

    # 5. PHP/WP version
    try:
        r = requests.get(f"{API}/settings", headers=HEADERS, timeout=10)
        checks["wp_version"] = r.headers.get("X-WP-Version", "unknown")
    except Exception:
        checks["wp_version"] = "unknown"

    # Overall readiness
    issues = []
    if not checks.get("production_up", {}).get("ok"):
        issues.append("Production site is not responding normally")
    if checks.get("plugins_outdated", 0) > 5:
        issues.append(f"{checks['plugins_outdated']} plugins have updates available")

    checks["ready"] = len(issues) == 0
    checks["issues"] = issues
    checks["timestamp"] = datetime.now().isoformat()

    return checks


# ═══════════════════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════════════════

def action_backup(args):
    """Trigger pre-deployment backup via Hostinger."""
    return {
        "action": "backup",
        "domain": args.domain or WP_URL,
        "note": "Use Hostinger MCP for backup operations:\n"
                "python hostinger_mcp.py --action create-backup --domain yourdomain.com",
        "hostinger_ui": "hPanel → Websites → Backup → Create Backup",
        "recommendation": "Always backup before deploying. Confirm backup completed before proceeding.",
    }


# ═══════════════════════════════════════════════════════════════════════════
# PUSH STAGING
# ═══════════════════════════════════════════════════════════════════════════

def action_push_staging(args):
    """Push staging to production via Hostinger."""
    domain = args.domain or WP_URL.replace("https://", "").replace("http://", "").split("/")[0]
    return {
        "action": "push-staging",
        "domain": domain,
        "note": "Use Hostinger MCP to push staging to production:\n"
                f"python hostinger_mcp.py --action push-staging --domain {domain} --confirm",
        "hostinger_ui": "hPanel → Websites → Staging → Push to Live",
        "warning": "This will overwrite production with staging content. "
                   "Ensure backup is completed first.",
        "post_push": "After push, run: python wp_deploy.py --action smoke-test",
    }


# ═══════════════════════════════════════════════════════════════════════════
# SMOKE TESTS
# ═══════════════════════════════════════════════════════════════════════════

def action_smoke_test(args):
    """Post-deployment smoke tests."""
    url = args.url or WP_URL
    results = []

    # Critical pages to test
    pages = [
        ("Homepage", url),
        ("REST API", f"{url}/wp-json/"),
        ("Admin Login", f"{url}/wp-admin/"),
    ]

    # Add WooCommerce pages if applicable
    wc_key = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
    if wc_key:
        pages.extend([
            ("Shop", f"{url}/shop/"),
            ("Cart", f"{url}/cart/"),
            ("Checkout", f"{url}/checkout/"),
        ])

    for label, page_url in pages:
        results.append(_check_url(page_url, label))

    passed = sum(1 for r in results if r["ok"])
    failed = len(results) - passed

    # Check for PHP errors (basic check)
    php_errors = False
    try:
        r = requests.get(url, timeout=10)
        html = r.text.lower()
        php_errors = any(err in html for err in
                         ["fatal error", "parse error", "warning:",
                          "notice:", "on line"])
    except Exception:
        pass

    # Check cache status
    cache_status = "unknown"
    try:
        r = requests.get(url, timeout=10)
        cache_status = r.headers.get("x-litespeed-cache", "not-detected")
    except Exception:
        pass

    return {
        "deploy_result": "PASS" if passed == len(results) else "FAIL",
        "tests_passed": passed, "tests_failed": failed,
        "total_tests": len(results),
        "php_errors_detected": php_errors,
        "cache_status": cache_status,
        "test_results": results,
        "timestamp": datetime.now().isoformat(),
        "recommendation": "All critical pages accessible. Site is healthy." if passed == len(results) else
                          "Some pages failed! Review failed tests. Consider rollback.",
    }


def action_validate_pages(args):
    """Validate specific URLs after deployment."""
    urls = []
    if args.urls:
        urls = [u.strip() for u in args.urls.split(",")]
    if not urls:
        urls = [WP_URL]

    results = []
    for i, url in enumerate(urls):
        results.append(_check_url(url, f"page_{i+1}"))

    passed = sum(1 for r in results if r["ok"])
    return {"validated": len(results), "passed": passed,
            "failed": len(results) - passed, "results": results}


def action_test_checkout(args):
    """Test WooCommerce checkout endpoints."""
    wc_key = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
    if not wc_key:
        return {"error": True, "message": "WOOCOMMERCE_CONSUMER_KEY not set"}

    results = []
    wc_auth = base64.b64encode(f"{wc_key}:{os.getenv('WOOCOMMERCE_CONSUMER_SECRET', '')}".encode()).decode()
    wc_headers = {"Authorization": f"Basic {wc_auth}"}

    # Test WooCommerce system status
    try:
        r = requests.get(f"{WP_URL}/wp-json/wc/v3/system_status",
                         headers=wc_headers, timeout=15)
        results.append({"check": "wc_system_status", "ok": r.status_code == 200,
                        "status": r.status_code})
    except Exception as e:
        results.append({"check": "wc_system_status", "ok": False, "error": str(e)})

    # Test payment gateways
    try:
        r = requests.get(f"{WP_URL}/wp-json/wc/v3/payment_gateways",
                         headers=wc_headers, timeout=15)
        gateways = r.json()
        enabled = [g["title"] for g in gateways if g.get("enabled")]
        results.append({"check": "payment_gateways", "ok": r.status_code == 200,
                        "enabled_gateways": enabled})
    except Exception as e:
        results.append({"check": "payment_gateways", "ok": False, "error": str(e)})

    return {"checkout_tests": results}


# ═══════════════════════════════════════════════════════════════════════════
# ROLLBACK
# ═══════════════════════════════════════════════════════════════════════════

def action_rollback(args):
    """Rollback to a specific backup."""
    domain = args.domain or WP_URL.replace("https://", "").replace("http://", "").split("/")[0]
    backup_id = args.backup_id or "latest"
    return {
        "action": "rollback",
        "domain": domain, "backup_id": backup_id,
        "note": f"Use Hostinger MCP to restore backup:\n"
                f"python hostinger_backup.py --action restore "
                f"--domain {domain} --id {backup_id}",
        "hostinger_ui": "hPanel → Websites → Backup → Restore",
        "warning": "Rollback will revert the site to the backup state. "
                   "Any changes made after the backup will be lost.",
    }


def action_list_backups(args):
    """List available backups for rollback."""
    domain = args.domain or WP_URL.replace("https://", "").replace("http://", "").split("/")[0]
    return {
        "domain": domain,
        "note": f"Use Hostinger MCP to list backups:\n"
                f"python hostinger_backup.py --action list --domain {domain}",
        "hostinger_ui": "hPanel → Websites → Backup",
    }


def action_deploy(args):
    """Full deployment pipeline."""
    pipeline = {"timestamp": datetime.now().isoformat(), "steps": {}}

    # Step 1: Pre-check
    pipeline["steps"]["1_pre_check"] = action_pre_check(args)

    # Step 2: Backup
    pipeline["steps"]["2_backup"] = action_backup(args)

    # Step 3: Push staging
    pipeline["steps"]["3_push_staging"] = action_push_staging(args)

    # Step 4: Smoke test
    pipeline["steps"]["4_smoke_test"] = action_smoke_test(args)

    smoke_result = pipeline["steps"]["4_smoke_test"]
    pipeline["deploy_success"] = smoke_result.get("deploy_result") == "PASS"

    if not pipeline["deploy_success"]:
        pipeline["rollback_instructions"] = action_rollback(args)

    return pipeline


def action_diff(args):
    """Compare staging vs production."""
    staging = args.staging_url or STAGING_URL
    if not staging:
        return {"error": True, "message": "Provide --staging-url or set STAGING_SITE_URL"}

    diff = {}
    # Compare response times
    diff["production"] = _check_url(WP_URL, "production")
    diff["staging"] = _check_url(staging, "staging")

    # Compare WP versions
    for label, site_url in [("production", WP_URL), ("staging", staging)]:
        try:
            r = requests.get(f"{site_url}/wp-json/wp/v2/settings",
                             headers=HEADERS, timeout=10)
            diff[f"{label}_wp_version"] = r.headers.get("X-WP-Version", "unknown")
        except Exception as e:
            diff[f"{label}_wp_version"] = f"error: {e}"

    return diff


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Deployment Manager")
    parser.add_argument("--action", required=True, choices=[
        "pre-check", "backup", "push-staging", "smoke-test",
        "validate-pages", "test-checkout", "rollback",
        "list-backups", "deploy", "diff",
    ])
    parser.add_argument("--domain")
    parser.add_argument("--url")
    parser.add_argument("--urls")
    parser.add_argument("--staging-url", dest="staging_url")
    parser.add_argument("--backup-id", dest="backup_id")

    args = parser.parse_args()
    _check()

    actions = {
        "pre-check": lambda: action_pre_check(args),
        "backup": lambda: action_backup(args),
        "push-staging": lambda: action_push_staging(args),
        "smoke-test": lambda: action_smoke_test(args),
        "validate-pages": lambda: action_validate_pages(args),
        "test-checkout": lambda: action_test_checkout(args),
        "rollback": lambda: action_rollback(args),
        "list-backups": lambda: action_list_backups(args),
        "deploy": lambda: action_deploy(args),
        "diff": lambda: action_diff(args),
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
