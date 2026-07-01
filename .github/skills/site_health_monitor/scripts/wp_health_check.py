#!/usr/bin/env python3
"""
WordPress Site Health Checker

Comprehensive health audit for WordPress + Hostinger:
uptime, PHP errors, WP Site Health API, cron jobs, disk usage,
database stats, SSL certs, PHP config, and system limits.

Usage:
    python wp_health_check.py --action full
    python wp_health_check.py --action quick
    python wp_health_check.py --action php-errors --lines 200
"""

import os, sys, json, argparse, base64, ssl, socket
from pathlib import Path
from datetime import datetime, timedelta
import requests
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


def _wp_get(ep, params=None, timeout=15):
    r = requests.get(f"{API}/{ep.lstrip('/')}", headers=HEADERS,
                     params=params, timeout=timeout)
    r.raise_for_status()
    return r.json(), dict(r.headers)


def _check_uptime(url=None):
    """Basic uptime check — response time and status code."""
    target = url or WP_URL
    try:
        start = datetime.now()
        r = requests.get(target, headers={"User-Agent": "Mozilla/5.0"},
                         timeout=15, allow_redirects=True)
        elapsed = (datetime.now() - start).total_seconds()
        return {
            "url": target, "status_code": r.status_code,
            "response_time_ms": round(elapsed * 1000, 1),
            "redirect_count": len(r.history),
            "final_url": r.url,
            "ok": r.status_code < 400,
        }
    except requests.ConnectionError:
        return {"url": target, "status_code": 0, "error": "Connection refused", "ok": False}
    except requests.Timeout:
        return {"url": target, "status_code": 0, "error": "Timeout", "ok": False}
    except Exception as e:
        return {"url": target, "status_code": 0, "error": str(e), "ok": False}


def _check_ssl(domain=None):
    """Check SSL certificate expiry and details."""
    host = domain or WP_URL.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        days_left = (not_after - datetime.now()).days
        return {
            "domain": host, "issuer": dict(x[0] for x in cert.get("issuer", [])),
            "expires": not_after.isoformat(), "days_left": days_left,
            "valid": days_left > 0,
            "severity": "critical" if days_left < 7 else (
                "warning" if days_left < 30 else "ok"),
        }
    except Exception as e:
        return {"domain": host, "error": str(e), "valid": False}


def _check_wp_health():
    """WordPress Site Health API scores."""
    try:
        r = requests.get(f"{WP_URL}/wp-json/wp-site-health/v1",
                         headers=HEADERS, timeout=15)
        if r.status_code == 200:
            tests = r.json()
            return {
                "api_available": True,
                "total_tests": len(tests),
                "good": len([t for t in tests if t.get("status") == "good"]),
                "recommended": len([t for t in tests if t.get("status") == "recommended"]),
                "critical": len([t for t in tests if t.get("status") == "critical"]),
                "critical_items": [
                    {"test": t.get("label", ""), "description": t.get("description", "")[:150]}
                    for t in tests if t.get("status") == "critical"
                ],
                "recommended_items": [
                    {"test": t.get("label", ""), "description": t.get("description", "")[:150]}
                    for t in tests if t.get("status") == "recommended"
                ][:10],
            }
        return {"api_available": False, "status_code": r.status_code}
    except Exception as e:
        return {"api_available": False, "error": str(e)}


def _check_php_info():
    """PHP configuration info via WordPress REST API and headers."""
    info = {}
    # Header-based detection
    try:
        r = requests.get(WP_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        info["php_version_header"] = r.headers.get("x-powered-by", "hidden")
        info["server"] = r.headers.get("server", "hidden")
    except Exception:
        pass

    # Try to get system info from various endpoints
    try:
        r = requests.get(f"{API}/settings", headers=HEADERS, timeout=10)
        settings = r.json()
        info["wp_version"] = r.headers.get("X-WP-Version", "unknown")
    except Exception:
        info["wp_version"] = "unknown"

    return {
        **info,
        "recommended_php": "8.2+",
        "recommended_memory_limit": "256M",
        "recommended_max_execution": "300",
        "recommended_upload_max": "64M",
        "recommended_post_max": "64M",
    }


def _check_db_stats():
    """Database statistics via WordPress REST API."""
    try:
        # Count all post types
        posts, ph = _wp_get("posts", {"per_page": 1, "status": "any"})
        total_posts = int(ph.get("X-WP-Total", 0))

        pages, pgh = _wp_get("pages", {"per_page": 1, "status": "any"})
        total_pages = int(pgh.get("X-WP-Total", 0))

        media, mh = _wp_get("media", {"per_page": 1})
        total_media = int(mh.get("X-WP-Total", 0))

        users, uh = _wp_get("users", {"per_page": 1})
        total_users = int(uh.get("X-WP-Total", 0))

        comments, ch = _wp_get("comments", {"per_page": 1})
        total_comments = int(ch.get("X-WP-Total", 0))

        return {
            "posts": total_posts, "pages": total_pages,
            "media": total_media, "users": total_users,
            "comments": total_comments,
            "total_records": total_posts + total_pages + total_media + total_users + total_comments,
            "recommendations": [
                "Run wp db optimize to reclaim overhead",
                "Delete post revisions older than 90 days",
                "Delete expired transients: wp transient delete --expired",
            ],
        }
    except Exception as e:
        return {"error": str(e)}


def _check_cron_health():
    """Check WordPress cron system."""
    try:
        # Check if the site is serving cron requests
        r = requests.get(f"{WP_URL}/wp-cron.php?doing_wp_cron", timeout=10)
        cron_running = r.status_code in (200, 204, 302)
    except Exception:
        cron_running = False

    return {
        "wp_cron_accessible": cron_running,
        "note": "For detailed cron job listing, use WP-CLI: wp cron event list",
        "recommendation": "Consider using a real server cron job instead of WP-Cron for reliability.",
        "server_cron_command": f"*/15 * * * * wget -q -O - {WP_URL}/wp-cron.php?doing_wp_cron >/dev/null 2>&1",
    }


def _check_surface():
    """Check attack surface indicators."""
    checks = {}
    # XML-RPC
    try:
        r = requests.post(f"{WP_URL}/xmlrpc.php",
                          data="<methodCall><methodName>system.listMethods</methodName></methodCall>",
                          headers={"Content-Type": "text/xml"}, timeout=10)
        checks["xmlrpc_enabled"] = r.status_code == 200
    except Exception:
        checks["xmlrpc_enabled"] = False

    # User enumeration via REST API
    try:
        r = requests.get(f"{API}/users", headers=HEADERS, timeout=10)
        checks["rest_user_enumeration"] = r.status_code == 200 and len(r.json()) > 0
    except Exception:
        checks["rest_user_enumeration"] = False

    # Debug mode detection (simplified)
    checks["recommendations"] = []
    if checks.get("xmlrpc_enabled"):
        checks["recommendations"].append("Disable XML-RPC if not needed")
    if checks.get("rest_user_enumeration"):
        checks["recommendations"].append("Consider restricting REST API user endpoint")

    return checks


# ═══════════════════════════════════════════════════════════════════════════
# ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

def action_full(args):
    """Run all health checks."""
    return {
        "timestamp": datetime.now().isoformat(),
        "site": WP_URL,
        "uptime": _check_uptime(),
        "ssl": _check_ssl(),
        "wp_health": _check_wp_health(),
        "php_info": _check_php_info(),
        "db_stats": _check_db_stats(),
        "cron": _check_cron_health(),
        "surface": _check_surface(),
    }


def action_quick(args):
    """Quick status check — uptime + response code."""
    return {
        "uptime": _check_uptime(),
        "ssl_days": _check_ssl().get("days_left", "unknown"),
    }


def action_wp_health(args):
    return _check_wp_health()


def action_php_errors(args):
    """Report PHP error log location and how to access."""
    return {
        "error_log_location": f"{WP_URL}/wp-content/debug.log (if WP_DEBUG_LOG is enabled)",
        "note": "PHP error logs can be accessed via Hostinger hPanel → Advanced → PHP Error Logs, "
                "or via Hostinger MCP: python hostinger_mcp.py --action php-error-logs --domain yourdomain.com",
        "enable_debug_log": "Add to wp-config.php:\n"
                            "define('WP_DEBUG', true);\n"
                            "define('WP_DEBUG_LOG', true);\n"
                            "define('WP_DEBUG_DISPLAY', false);",
    }


def action_debug_log(args):
    return {
        "debug_log_path": "wp-content/debug.log",
        "note": "Use Hostinger MCP file manager to view: "
                "python hostinger_mcp.py --action list-files --path /public_html/wp-content/",
        "wp_cli_command": "wp eval 'echo ini_get(\"error_log\");'",
    }


def action_cron_health(args):
    return _check_cron_health()


def action_disk_usage(args):
    return {
        "note": "Use Hostinger MCP for disk usage: python hostinger_mcp.py --action hosting-info",
        "hostinger_ui": "Check hPanel → Hosting → Dashboard for disk usage",
    }


def action_db_stats(args):
    return _check_db_stats()


def action_php_info(args):
    return _check_php_info()


def action_ssl_check(args):
    return _check_ssl(args.domain if hasattr(args, 'domain') else None)


def action_uptime(args):
    results = []
    for i in range(args.repeat or 1):
        results.append(_check_uptime())
        if i < (args.repeat or 1) - 1 and hasattr(args, 'interval'):
            import time
            time.sleep(args.interval or 10)
    if len(results) == 1:
        return results[0]
    avg = sum(r.get("response_time_ms", 0) for r in results) / len(results)
    return {"checks": len(results), "avg_response_ms": round(avg, 1),
            "results": results}


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Site Health Checker")
    parser.add_argument("--action", required=True, choices=[
        "full", "quick", "wp-health", "php-errors", "debug-log",
        "cron-health", "disk-usage", "db-stats", "php-info",
        "ssl-check", "uptime",
    ])
    parser.add_argument("--lines", type=int, default=100)
    parser.add_argument("--domain")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--interval", type=int, default=10)

    args = parser.parse_args()
    _check()

    actions = {
        "full": lambda: action_full(args),
        "quick": lambda: action_quick(args),
        "wp-health": lambda: action_wp_health(args),
        "php-errors": lambda: action_php_errors(args),
        "debug-log": lambda: action_debug_log(args),
        "cron-health": lambda: action_cron_health(args),
        "disk-usage": lambda: action_disk_usage(args),
        "db-stats": lambda: action_db_stats(args),
        "php-info": lambda: action_php_info(args),
        "ssl-check": lambda: action_ssl_check(args),
        "uptime": lambda: action_uptime(args),
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
