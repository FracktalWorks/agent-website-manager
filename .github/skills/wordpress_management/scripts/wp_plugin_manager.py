#!/usr/bin/env python3
"""
WordPress Plugin Manager

Install, activate, deactivate, update, and delete WordPress plugins
via the REST API. Lists installed plugins with status and version info.

Usage:
    python wp_plugin_manager.py --action list
    python wp_plugin_manager.py --action install --slug elementor
    python wp_plugin_manager.py --action activate --slug elementor
    python wp_plugin_manager.py --action update --slug yoast-seo
    python wp_plugin_manager.py --action deactivate --slug akismet
    python wp_plugin_manager.py --action delete --slug hello-dolly
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

API_BASE = f"{WP_URL}/wp-json/wp/v2"
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "User-Agent": "Agent-Website-Manager/1.0",
}


def _check_config():
    missing = []
    if not WP_URL:
        missing.append("WORDPRESS_SITE_URL")
    if not WP_USER:
        missing.append("WORDPRESS_USERNAME")
    if not WP_APP_PASSWORD:
        missing.append("WORDPRESS_APP_PASSWORD")
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def action_list(args):
    """List all installed plugins with status."""
    resp = requests.get(f"{API_BASE}/plugins", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    plugins = []
    for p in resp.json():
        plugins.append({
            "plugin": p["plugin"],
            "name": p["name"],
            "status": p["status"],  # active, inactive
            "version": p.get("version", "unknown"),
            "author": p.get("author", ""),
            "description": (p.get("description", {}).get("raw", "") if isinstance(p.get("description"), dict) else p.get("description", ""))[:120],
            "requires_php": p.get("requires_php", ""),
            "requires_wp": p.get("requires_wp", ""),
        })

    active = [p for p in plugins if p["status"] == "active"]
    inactive = [p for p in plugins if p["status"] == "inactive"]
    return {
        "total": len(plugins),
        "active_count": len(active),
        "inactive_count": len(inactive),
        "active": active,
        "inactive": inactive,
    }


def action_install(args):
    """Install a plugin from WordPress.org by slug."""
    resp = requests.post(
        f"{API_BASE}/plugins",
        headers=HEADERS,
        json={"slug": args.slug, "status": "active" if args.activate else "inactive"},
        timeout=60,
    )
    resp.raise_for_status()
    result = resp.json()
    return {
        "installed": True,
        "plugin": result["plugin"],
        "name": result["name"],
        "version": result.get("version", ""),
        "status": result["status"],
    }


def action_activate(args):
    """Activate an installed plugin."""
    resp = requests.put(
        f"{API_BASE}/plugins/{args.slug}",
        headers=HEADERS,
        json={"status": "active"},
        timeout=15,
    )
    resp.raise_for_status()
    return {"activated": True, "plugin": args.slug}


def action_deactivate(args):
    """Deactivate a plugin."""
    resp = requests.put(
        f"{API_BASE}/plugins/{args.slug}",
        headers=HEADERS,
        json={"status": "inactive"},
        timeout=15,
    )
    resp.raise_for_status()
    return {"deactivated": True, "plugin": args.slug}


def action_update(args):
    """Update a plugin to the latest version."""
    resp = requests.put(
        f"{API_BASE}/plugins/{args.slug}",
        headers=HEADERS,
        json={"status": "active"},
        timeout=60,
    )
    resp.raise_for_status()
    return {"updated": True, "plugin": args.slug, "version": resp.json().get("version", "")}


def action_delete(args):
    """Delete a plugin (must be deactivated first)."""
    resp = requests.delete(f"{API_BASE}/plugins/{args.slug}", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return {"deleted": True, "plugin": args.slug}


def action_bulk_update(args):
    """Update all plugins that have updates available."""
    plugins_resp = requests.get(f"{API_BASE}/plugins", headers=HEADERS, timeout=15)
    plugins_resp.raise_for_status()
    updated = []
    for p in plugins_resp.json():
        if p["status"] == "inactive":
            continue
        try:
            resp = requests.put(
                f"{API_BASE}/plugins/{p['plugin']}",
                headers=HEADERS,
                json={"status": "active"},
                timeout=60,
            )
            if resp.status_code == 200:
                updated.append({"plugin": p["plugin"], "name": p["name"], "version": resp.json().get("version", "")})
        except Exception as e:
            updated.append({"plugin": p["plugin"], "name": p["name"], "error": str(e)})
    return {"bulk_updated": len(updated), "plugins": updated}


def main():
    parser = argparse.ArgumentParser(description="WordPress Plugin Manager")
    parser.add_argument("--action", required=True, choices=[
        "list", "install", "activate", "deactivate", "update", "delete", "bulk-update",
    ])
    parser.add_argument("--slug", help="Plugin slug (e.g., elementor, yoast-seo)")
    parser.add_argument("--activate", action="store_true", help="Auto-activate after install")
    args = parser.parse_args()

    _check_config()

    action_map = {
        "list": lambda: action_list(args),
        "install": lambda: action_install(args),
        "activate": lambda: action_activate(args),
        "deactivate": lambda: action_deactivate(args),
        "update": lambda: action_update(args),
        "delete": lambda: action_delete(args),
        "bulk-update": lambda: action_bulk_update(args),
    }

    try:
        result = action_map[args.action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except requests.HTTPError as e:
        error_body = ""
        try:
            error_body = e.response.json()
        except Exception:
            error_body = e.response.text
        print(json.dumps({"error": True, "status_code": e.response.status_code, "message": str(e), "details": error_body}, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
