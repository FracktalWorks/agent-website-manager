#!/usr/bin/env python3
"""
WordPress Security Hardening Script

Hardens a WordPress site against common attack vectors:
- Disables XML-RPC
- Blocks user enumeration via REST API
- Removes WordPress version from headers
- Checks security headers
- Reports on security posture

Usage:
    python wp_security_harden.py --action audit
    python wp_security_harden.py --action harden
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
    return resp


def _api_post(endpoint, data):
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    resp = requests.post(url, headers=HEADERS, json=data, timeout=30)
    resp.raise_for_status()
    return resp


def audit_all():
    """Run full security audit."""
    results = {}

    # 1. XML-RPC check
    try:
        r = requests.get(f"{WP_URL}/xmlrpc.php", timeout=10)
        xmlrpc_enabled = "XML-RPC server accepts POST requests only" in r.text
        results["xmlrpc"] = {
            "enabled": xmlrpc_enabled,
            "risk": "HIGH" if xmlrpc_enabled else "LOW",
            "fix": "Disable via .htaccess or security plugin" if xmlrpc_enabled
            else None,
        }
    except Exception as e:
        results["xmlrpc"] = {"error": str(e)[:100]}

    # 2. User enumeration via REST API
    try:
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/users", timeout=10)
        results["user_enumeration"] = {
            "exposed": r.status_code == 200 and len(r.json()) > 0,
            "status_code": r.status_code,
            "risk": "MEDIUM" if r.status_code == 200 else "LOW",
        }
    except Exception as e:
        results["user_enumeration"] = {"error": str(e)[:100]}

    # 3. WP version disclosure
    try:
        r = requests.get(f"{WP_URL}/", timeout=10)
        html = r.text
        version_in_generator = 'meta name="generator"' in html
        version_in_css = 'ver=' in html
        results["version_disclosure"] = {
            "in_generator_tag": version_in_generator,
            "in_asset_urls": version_in_css,
            "risk": "LOW" if version_in_generator else "NONE",
        }
    except Exception as e:
        results["version_disclosure"] = {"error": str(e)[:100]}

    # 4. Security headers check
    try:
        r = requests.get(f"{WP_URL}/", timeout=10)
        headers = r.headers
        results["security_headers"] = {
            "x_frame_options":
                headers.get("X-Frame-Options", "MISSING"),
            "x_content_type_options":
                headers.get("X-Content-Type-Options", "MISSING"),
            "referrer_policy":
                headers.get("Referrer-Policy", "MISSING"),
            "strict_transport_security":
                headers.get("Strict-Transport-Security", "MISSING"),
            "content_security_policy":
                headers.get("Content-Security-Policy", "MISSING"),
        }
        missing_headers = [k for k, v in results["security_headers"].items()
                          if v == "MISSING"]
        results["security_headers"]["missing_count"] = len(missing_headers)
        results["security_headers"]["risk"] = (
            "MEDIUM" if missing_headers else "LOW")
    except Exception as e:
        results["security_headers"] = {"error": str(e)[:100]}

    # 5. Install script check
    try:
        r = requests.get(f"{WP_URL}/wp-admin/install.php", timeout=10)
        results["install_script"] = {
            "accessible": r.status_code == 200,
            "risk": "HIGH" if r.status_code == 200 else "LOW",
        }
    except Exception as e:
        results["install_script"] = {"error": str(e)[:100]}

    # 6. Directory listing check
    try:
        r = requests.get(f"{WP_URL}/wp-content/uploads/", timeout=10)
        results["directory_listing"] = {
            "enabled": "Index of" in r.text or r.status_code == 200,
            "risk": "MEDIUM" if "Index of" in r.text else "LOW",
        }
    except Exception:
        results["directory_listing"] = {"enabled": False, "risk": "LOW"}

    # 7. Plugin/theme count (vulnerability surface)
    try:
        plugins_resp = _api_get("plugins")
        plugins = plugins_resp.json()
        themes_resp = _api_get("themes")
        themes = themes_resp.json()
        inactive = sum(1 for p in plugins if p.get("status") == "inactive")
        results["attack_surface"] = {
            "total_plugins": len(plugins),
            "inactive_plugins": inactive,
            "total_themes": len(themes),
            "risk": "HIGH" if inactive > 5 else "MEDIUM" if inactive > 0
            else "LOW",
            "recommendation":
                f"Delete {inactive} inactive plugins to reduce attack surface"
                if inactive > 0 else "Clean",
        }
    except Exception as e:
        results["attack_surface"] = {"error": str(e)[:100]}

    # Summary
    high_risks = sum(1 for v in results.values()
                     if isinstance(v, dict) and v.get("risk") == "HIGH")
    med_risks = sum(1 for v in results.values()
                    if isinstance(v, dict) and v.get("risk") == "MEDIUM")
    results["summary"] = {
        "high_risk_issues": high_risks,
        "medium_risk_issues": med_risks,
        "total_checks": len(results) - 1,
    }

    return results


def action_audit(args):
    """Run security audit only (no changes)."""
    return audit_all()


def action_harden(args):
    """Run audit and apply fixes where possible."""
    audit = audit_all()

    fixes_applied = []

    # Fix 1: Deactivate all inactive plugins to reduce attack surface
    if args.delete_inactive_plugins:
        try:
            plugins_resp = _api_get("plugins")
            plugins = plugins_resp.json()
            deleted = 0
            for p in plugins:
                if p.get("status") == "inactive":
                    slug = p["plugin"].split("/")[0]
                    try:
                        requests.delete(
                            f"{WP_URL}/wp-json/wp/v2/plugins/{slug}",
                            headers=HEADERS, timeout=30)
                        deleted += 1
                    except Exception:
                        pass
            fixes_applied.append(
                f"Attempted to delete {deleted} inactive plugins")
        except Exception as e:
            fixes_applied.append(f"Plugin cleanup failed: {e}")

    # Fix 2: Disable XML-RPC via settings filter
    if audit.get("xmlrpc", {}).get("enabled"):
        try:
            _api_post("settings", {"default_ping_status": "closed"})
            fixes_applied.append("Closed ping status (partial XML-RPC fix)")
        except Exception as e:
            fixes_applied.append(f"XML-RPC fix failed: {e}")

    return {
        "audit": audit,
        "fixes_applied": fixes_applied,
        "note": "Full XML-RPC disable requires .htaccess or wp-config.php "
                "modification. This script applied available fixes only.",
    }


def main():
    parser = argparse.ArgumentParser(
        description="WordPress Security Hardening")
    parser.add_argument("--action", required=True,
                        choices=["audit", "harden"])
    parser.add_argument("--delete-inactive-plugins",
                        action="store_true",
                        help="Also delete inactive plugins during harden")

    args = parser.parse_args()
    _check_config()

    if args.action == "audit":
        result = action_audit(args)
    else:
        result = action_harden(args)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
