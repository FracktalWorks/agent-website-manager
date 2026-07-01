#!/usr/bin/env python3
"""
WordPress Security Scanner

Vulnerability scanning, security header audit, SSL/TLS analysis,
XML-RPC check, user audit, File permissions recommendations,
and hardening checklist generation.

Usage:
    python wp_security_scan.py --action full
    python wp_security_scan.py --action vuln-scan
    python wp_security_scan.py --action headers
"""

import os, sys, json, argparse, base64, ssl, socket
from pathlib import Path
from datetime import datetime
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


# ═══════════════════════════════════════════════════════════════════════════
# VULNERABILITY SCAN
# ═══════════════════════════════════════════════════════════════════════════

def _check_plugin_vulns():
    """Check installed plugins for known issues via WordPress.org API."""
    try:
        r = requests.get(f"{API}/plugins", headers=HEADERS, timeout=15)
        r.raise_for_status()
        plugins = r.json()
    except Exception as e:
        return {"error": str(e)}

    results = []
    for p in plugins:
        slug = p.get("plugin", "").split("/")[0]
        version = p.get("version", "")
        status = p.get("status", "unknown")

        # Check WordPress.org for latest version
        try:
            wp_r = requests.get(
                f"https://api.wordpress.org/plugins/info/1.0/{slug}.json",
                timeout=10)
            if wp_r.status_code == 200:
                info = wp_r.json()
                latest = info.get("version", "")
                last_updated = info.get("last_updated", "")[:10]
                is_outdated = version != latest and latest != ""
            else:
                latest = "unknown"
                last_updated = "unknown"
                is_outdated = False
        except Exception:
            latest = "fetch_error"
            last_updated = ""
            is_outdated = False

        results.append({
            "slug": slug, "name": p.get("name", slug),
            "installed_version": version, "latest_version": latest,
            "status": status,
            "outdated": is_outdated,
            "last_updated": last_updated,
            "risk": "high" if is_outdated and status == "active" else (
                "medium" if is_outdated else "low"),
        })

    outdated = [r for r in results if r.get("outdated")]
    active_outdated = [r for r in outdated if r.get("status") == "active"]

    return {
        "total_plugins": len(results),
        "outdated": len(outdated),
        "active_outdated": len(active_outdated),
        "active_outdated_plugins": active_outdated,
        "all_plugins": results,
        "recommendation": "Update all active outdated plugins immediately. "
                          "Test on staging first.",
    }


def _check_theme_vulns():
    """Check active theme version."""
    try:
        r = requests.get(f"{API}/themes", headers=HEADERS, timeout=15)
        r.raise_for_status()
        themes = r.json()
    except Exception as e:
        return {"error": str(e)}

    active = [t for t in themes if t.get("status") == "active"]
    if not active:
        return {"error": "No active theme found"}

    theme = active[0]
    slug = theme.get("stylesheet", "")
    version = theme.get("version", "")

    # Check WordPress.org for theme updates
    try:
        wp_r = requests.get(
            f"https://api.wordpress.org/themes/info/1.1/?action=theme_information"
            f"&request[slug]={slug}", timeout=10)
        if wp_r.status_code == 200 and wp_r.json():
            info = wp_r.json()
            latest = info.get("version", "")
            is_outdated = version != latest and latest != ""
        else:
            latest = "check_wp_org"
            is_outdated = False
    except Exception:
        latest = "fetch_error"
        is_outdated = False

    return {
        "theme": slug, "name": theme.get("name", ""),
        "installed_version": version, "latest_version": latest,
        "outdated": is_outdated,
    }


# ═══════════════════════════════════════════════════════════════════════════
# SECURITY HEADERS
# ═══════════════════════════════════════════════════════════════════════════

SECURITY_HEADERS = {
    "Content-Security-Policy": {"severity": "high",
        "note": "Controls which resources can be loaded. XSS protection."},
    "Strict-Transport-Security": {"severity": "high",
        "note": "Forces HTTPS. Required for SSL sites."},
    "X-Frame-Options": {"severity": "medium",
        "note": "Prevents clickjacking. Use DENY or SAMEORIGIN."},
    "X-Content-Type-Options": {"severity": "medium",
        "note": "Prevents MIME type sniffing. Should be nosniff."},
    "Referrer-Policy": {"severity": "low",
        "note": "Controls referrer information sent with requests."},
    "Permissions-Policy": {"severity": "low",
        "note": "Controls browser features (camera, mic, etc)."},
    "X-XSS-Protection": {"severity": "low",
        "note": "Legacy XSS filter. Modern browsers ignore this."},
}


def _check_security_headers():
    """Audit security-related HTTP headers."""
    try:
        r = requests.get(WP_URL, headers={"User-Agent": "Mozilla/5.0"},
                         timeout=10, allow_redirects=True)
        headers = dict(r.headers)
    except Exception as e:
        return {"error": str(e)}

    results = {}
    for header, info in SECURITY_HEADERS.items():
        present = header in headers
        results[header] = {
            "present": present,
            "value": headers.get(header, "")[:200] if present else "missing",
            "severity": info["severity"],
            "note": info["note"],
        }

    total = len(SECURITY_HEADERS)
    present = sum(1 for r in results.values() if r["present"])
    score = round(present / total * 100) if total > 0 else 0

    return {
        "security_header_score": f"{score}/100",
        "headers": results,
        "recommendation": "Add missing security headers via .htaccess or a "
                          "security plugin like 'Headers Security Advanced'.",
    }


# ═══════════════════════════════════════════════════════════════════════════
# SSL / TLS AUDIT
# ═══════════════════════════════════════════════════════════════════════════

def _check_ssl():
    """Detailed SSL/TLS analysis."""
    host = WP_URL.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                tls_version = ssock.version()

        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
        days_left = (not_after - datetime.now()).days

        return {
            "domain": host, "tls_version": tls_version,
            "cipher": {"name": cipher[0], "bits": cipher[1], "protocol": cipher[2]},
            "issuer": dict(x[0] for x in cert.get("issuer", [])),
            "issued": not_before.isoformat(),
            "expires": not_after.isoformat(),
            "days_left": days_left,
            "valid": days_left > 0,
            "san": cert.get("subjectAltName", []),
            "severity": "critical" if days_left < 7 else (
                "warning" if days_left < 30 else "ok"),
        }
    except Exception as e:
        return {"domain": host, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# MISCELLANEOUS CHECKS
# ═══════════════════════════════════════════════════════════════════════════

def _check_xmlrpc():
    """Check if XML-RPC is enabled."""
    try:
        r = requests.post(f"{WP_URL}/xmlrpc.php",
                          data="<methodCall><methodName>system.listMethods</methodName></methodCall>",
                          headers={"Content-Type": "text/xml"}, timeout=10)
        return {
            "enabled": r.status_code == 200,
            "risk": "high" if r.status_code == 200 else "none",
            "recommendation": "Disable XML-RPC if not using it (Jetpack, mobile app). "
                              "Add to .htaccess: <Files xmlrpc.php> deny from all </Files>",
        }
    except Exception:
        return {"enabled": False, "risk": "none"}


def _check_user_audit():
    """Audit user accounts for security issues."""
    try:
        users, uh = requests.get(f"{API}/users", headers=HEADERS,
                                 params={"per_page": 100, "roles": "administrator"},
                                 timeout=15).json(), {}
        admin_count = len(users)
        idle_admins = []
        for u in users:
            idle_admins.append({"id": u["id"], "name": u["name"], "slug": u["slug"]})
    except Exception as e:
        return {"error": str(e)}

    issues = []
    if admin_count > 3:
        issues.append(f"{admin_count} admin accounts — reduce to minimum needed")
    for admin in idle_admins:
        if admin["slug"] in ("admin", "administrator", "root"):
            issues.append(
                f"User '{admin['slug']}' has a predictable admin username — "
                "rename or create a new admin and delete this one")

    return {
        "admin_count": admin_count,
        "admins": idle_admins,
        "issues": issues,
        "recommendation": "Use unique admin usernames. Limit admin accounts to 2-3 max.",
    }


def _check_misconfig():
    """Check for common WordPress security misconfigurations."""
    checks = {}

    # Check if debug mode might be on
    try:
        r = requests.get(WP_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        checks["server_header_visible"] = "server" in r.headers
    except Exception:
        pass

    # Check if directory listing is disabled
    try:
        r = requests.get(f"{WP_URL}/wp-includes/", timeout=10)
        checks["directory_listing_wp_includes"] = r.status_code == 200 and "Index of" in r.text
    except Exception:
        checks["directory_listing_wp_includes"] = False

    # Check readme.html
    try:
        r = requests.get(f"{WP_URL}/readme.html", timeout=10)
        checks["readme_accessible"] = r.status_code == 200
    except Exception:
        checks["readme_accessible"] = False

    # Check wp-config.php accessibility
    try:
        r = requests.get(f"{WP_URL}/wp-config.php", timeout=10)
        checks["wp_config_accessible"] = r.status_code == 200
    except Exception:
        checks["wp_config_accessible"] = False

    recommendations = []
    if checks.get("readme_accessible"):
        recommendations.append("Delete or block access to readme.html")
    if checks.get("wp_config_accessible"):
        recommendations.append("CRITICAL: wp-config.php is publicly accessible!")

    return {**checks, "recommendations": recommendations}


def _generate_checklist():
    """Generate a security hardening checklist."""
    return {
        "critical": [
            "☐ Update WordPress core to latest version",
            "☐ Update all active plugins to latest versions",
            "☐ Update active theme to latest version",
            "☐ Delete unused plugins and themes",
            "☐ Install SSL certificate and force HTTPS",
            "☐ Change database table prefix from 'wp_'",
            "☐ Use strong, unique passwords for all admin accounts",
        ],
        "high": [
            "☐ Disable XML-RPC if not needed",
            "☐ Block wp-config.php from web access",
            "☐ Delete readme.html and license.txt",
            "☐ Disable file editing (define('DISALLOW_FILE_EDIT', true))",
            "☐ Add security headers (HSTS, CSP, X-Frame-Options)",
            "☐ Enable Two-Factor Authentication for admins",
            "☐ Change default admin username",
        ],
        "medium": [
            "☐ Disable directory listing",
            "☐ Limit login attempts (install login limiter plugin)",
            "☐ Set proper file permissions (644 files, 755 dirs)",
            "☐ Disable PHP error display (WP_DEBUG_DISPLAY = false)",
            "☐ Setup automated backups (daily/weekly)",
            "☐ Install a security plugin (Wordfence or Sucuri)",
        ],
        "low": [
            "☐ Remove WordPress version from header",
            "☐ Disable REST API user enumeration",
            "☐ Add Content-Security-Policy header",
            "☐ Setup uptime monitoring",
            "☐ Regular security audit (use this agent weekly!)",
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

def action_full(args):
    return {
        "timestamp": datetime.now().isoformat(),
        "site": WP_URL,
        "vulnerabilities": {
            "plugins": _check_plugin_vulns(),
            "theme": _check_theme_vulns(),
        },
        "security_headers": _check_security_headers(),
        "ssl": _check_ssl(),
        "xmlrpc": _check_xmlrpc(),
        "users": _check_user_audit(),
        "misconfig": _check_misconfig(),
    }


def main():
    parser = argparse.ArgumentParser(description="Security Scanner")
    parser.add_argument("--action", required=True, choices=[
        "full", "vuln-scan", "check-plugin", "permissions",
        "headers", "xmlrpc-check", "misconfig", "ssl-audit",
        "user-audit", "hardening-status", "checklist",
    ])
    parser.add_argument("--slug")
    parser.add_argument("--version")
    args = parser.parse_args()
    _check()

    actions = {
        "full": lambda: action_full(args),
        "vuln-scan": lambda: {"plugins": _check_plugin_vulns(),
                               "theme": _check_theme_vulns()},
        "headers": lambda: _check_security_headers(),
        "xmlrpc-check": lambda: _check_xmlrpc(),
        "misconfig": lambda: _check_misconfig(),
        "ssl-audit": lambda: _check_ssl(),
        "user-audit": lambda: _check_user_audit(),
        "checklist": lambda: _generate_checklist(),
        "permissions": lambda: {
            "recommended": {"directories": "755", "files": "644",
                            "wp_config": "400 or 440"},
            "wp_cli_check": "find . -type f -not -perm 644",
            "note": "Full permissions check requires Hostinger MCP file access.",
        },
        "check-plugin": lambda: {
            "slug": args.slug, "version": args.version,
            "wpvulndb_url": f"https://wpscan.com/plugin/{args.slug}",
            "note": "Check wpvulndb.com for known vulnerabilities.",
        },
        "hardening-status": lambda: {
            "checklist": _generate_checklist(),
            "note": "Run 'checklist' action for detailed hardening steps.",
        },
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
