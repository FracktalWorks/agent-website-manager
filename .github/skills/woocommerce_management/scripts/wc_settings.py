#!/usr/bin/env python3
"""
WooCommerce Settings Manager

View and update WooCommerce store settings via REST API.
General, products, tax, shipping, payments, accounts, emails, advanced.

Usage:
    python wc_settings.py --action get --group general
    python wc_settings.py --action update --group products --option weight_unit --value kg
"""

import os, sys, json, argparse, base64
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WC_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
WC_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")
AUTH = base64.b64encode(f"{WC_KEY}:{WC_SECRET}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Content-Type": "application/json"}
API = f"{WP_URL}/wp-json/wc/v3"


def _check():
    missing = [v for v, k in [("WP_URL", WP_URL), ("WC_KEY", WC_KEY),
                ("WC_SECRET", WC_SECRET)] if not k]
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)


def _get(ep):
    r = requests.get(f"{API}/{ep.lstrip('/')}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def _put(ep, data):
    r = requests.put(f"{API}/{ep.lstrip('/')}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


SETTINGS_GROUPS = [
    "general", "products", "tax", "shipping", "payments",
    "accounts", "emails", "advanced",
]


def action_get(args):
    """Get settings for a group."""
    group = args.group or "general"
    if group not in SETTINGS_GROUPS:
        return {"error": True, "message": f"Unknown group: {group}",
                "valid": SETTINGS_GROUPS}

    settings = _get(f"settings/{group}")
    result = []
    for s in settings:
        result.append({
            "id": s.get("id", ""), "label": s.get("label", ""),
            "value": s.get("value", ""), "type": s.get("type", ""),
            "description": s.get("description", "")[:100],
        })
    return {"group": group, "settings": result, "count": len(result)}


def action_update(args):
    """Update a specific setting."""
    if not args.option or args.value is None:
        return {"error": True, "message": "Provide --option and --value"}
    group = args.group or "general"
    if group not in SETTINGS_GROUPS:
        return {"error": True, "message": f"Unknown group: {group}"}

    # Fetch current settings for this group
    current = _get(f"settings/{group}")

    # Build the update payload — WooCommerce batch updates
    batch_data = {"update": []}
    found = False
    for s in current:
        if s.get("id") == args.option:
            s["value"] = args.value
            batch_data["update"].append(s)
            found = True
            break

    if not found:
        return {"error": True, "message": f"Option '{args.option}' not found in group '{group}'"}

    result = _put(f"settings/{group}/batch", batch_data)
    return {"updated": True, "group": group, "option": args.option,
            "new_value": args.value}


def action_list_groups(args):
    """List all settings groups with option counts."""
    groups = {}
    for group in SETTINGS_GROUPS:
        try:
            settings = _get(f"settings/{group}")
            groups[group] = {
                "count": len(settings),
                "key_options": [s["id"] for s in settings[:5]],
            }
        except Exception as e:
            groups[group] = {"error": str(e)}
    return {"groups": groups}


def main():
    parser = argparse.ArgumentParser(description="WooCommerce Settings Manager")
    parser.add_argument("--action", required=True,
                        choices=["get", "update", "list-groups"])
    parser.add_argument("--group", choices=SETTINGS_GROUPS)
    parser.add_argument("--option")
    parser.add_argument("--value")
    args = parser.parse_args()
    _check()

    actions = {
        "get": lambda: action_get(args),
        "update": lambda: action_update(args),
        "list-groups": lambda: action_list_groups(args),
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
