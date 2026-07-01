#!/usr/bin/env python3
"""
Elementor Page Builder Operations

Manage Elementor pages, templates, kits, and widgets via the WordPress REST API.
Elementor stores page data as JSON in the _elementor_data post meta field.
This script reads, writes, and manipulates that JSON structure.

Usage:
    python wp_elementor.py --action status
    python wp_elementor.py --action get-page --id 42
    python wp_elementor.py --action list-templates
    python wp_elementor.py --action create-template --name "Hero" --type section
    python wp_elementor.py --action kit-export --output ./kit.json
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
    "User-Agent": "Agent-Website-Manager/1.0",
}
API_BASE = f"{WP_URL}/wp-json"


def _check_config():
    missing = []
    if not WP_URL:
        missing.append("WORDPRESS_SITE_URL")
    if not WP_USER:
        missing.append("WORDPRESS_USERNAME")
    if not WP_APP_PASSWORD:
        missing.append("WORDPRESS_APP_PASSWORD")
    if missing:
        print(json.dumps({
            "error": True,
            "message": f"Missing env vars: {', '.join(missing)}"
        }, indent=2))
        sys.exit(1)


def _api_get(endpoint: str, params: dict = None) -> dict:
    """GET request helper."""
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _api_post(endpoint: str, data: dict) -> dict:
    """POST request helper."""
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    resp = requests.post(url, headers=HEADERS, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def action_status(args):
    """Check Elementor status on the site."""
    # Check if Elementor is active
    plugins = _api_get("wp/v2/plugins")
    elementor = None
    elementor_pro = None
    for p in plugins:
        if p.get("plugin", "").startswith("elementor/"):
            elementor = p
        if p.get("plugin", "").startswith("elementor-pro/"):
            elementor_pro = p

    # Check Elementor REST API availability
    elementor_api = False
    try:
        _api_get("elementor/v1/")
        elementor_api = True
    except Exception:
        pass

    return {
        "elementor_installed": elementor is not None,
        "elementor_active": elementor["status"] == "active" if elementor else False,
        "elementor_version": elementor.get("version", "") if elementor else "",
        "elementor_pro_active": elementor_pro is not None and elementor_pro.get("status") == "active",
        "elementor_rest_api": elementor_api,
        "site_url": WP_URL,
    }


def action_get_page(args):
    """Get a page's Elementor data."""
    # Fetch the page
    page = _api_get(f"wp/v2/pages/{args.id}")
    # Fetch Elementor meta
    elementor_data = _api_get(f"wp/v2/pages/{args.id}?_fields=meta")
    meta = elementor_data.get("meta", {})

    return {
        "page": {
            "id": page["id"],
            "title": page["title"]["rendered"],
            "status": page["status"],
            "link": page["link"],
        },
        "elementor_data": meta.get("_elementor_data", ""),
        "elementor_version": meta.get("_elementor_version", ""),
        "elementor_edit_mode": meta.get("_elementor_edit_mode", ""),
        "elementor_css": meta.get("_elementor_css", ""),
        "elementor_template_type": meta.get("_elementor_template_type", ""),
    }


def action_update_page(args):
    """Update Elementor data on an existing page."""
    if not args.layout_file and not args.layout_json:
        print(json.dumps({
            "error": True,
            "message": "Provide --layout-file or --layout-json with Elementor data"
        }, indent=2))
        sys.exit(1)

    # Load layout data
    if args.layout_file:
        with open(args.layout_file, "r", encoding="utf-8") as f:
            layout_data = json.load(f)
    else:
        layout_data = json.loads(args.layout_json)

    # Update page meta with Elementor data
    meta_update = {
        "meta": {
            "_elementor_data": json.dumps(layout_data) if isinstance(layout_data, (dict, list)) else layout_data,
            "_elementor_edit_mode": "builder",
            "_elementor_version": args.version or "3.20.0",
        }
    }
    if args.template_type:
        meta_update["meta"]["_elementor_template_type"] = args.template_type

    result = _api_post(f"wp/v2/pages/{args.id}", meta_update)
    return {
        "updated": True,
        "page_id": result["id"],
        "title": result["title"]["rendered"],
        "link": result["link"],
    }


def action_list_templates(args):
    """List Elementor templates (saved as elementor_library posts)."""
    params = {
        "per_page": args.per_page or 50,
        "page": args.page or 1,
        "meta_key": "_elementor_template_type",
    }
    if args.type:
        params["elementor_library_type"] = args.type

    try:
        templates = _api_get("wp/v2/elementor_library", params)
    except Exception:
        # Fallback: query via posts
        try:
            templates = _api_get("wp/v2/posts", {
                "per_page": 50,
                "meta_key": "_elementor_template_type",
                "orderby": "date",
                "order": "desc",
            })
        except Exception:
            return {"templates": [], "note": "Elementor library endpoint not available. Is Elementor Pro active?"}

    items = []
    for t in templates:
        items.append({
            "id": t["id"],
            "title": t["title"]["rendered"],
            "type": t.get("meta", {}).get("_elementor_template_type", "unknown"),
            "status": t["status"],
            "date": t["date"],
            "modified": t["modified"],
        })

    return {
        "templates": items,
        "total": len(items),
        "types": list(set(i["type"] for i in items)),
    }


def action_create_template(args):
    """Create a new Elementor template (section, page, header, etc.)."""
    data = {
        "title": args.name,
        "status": "publish",
        "meta": {
            "_elementor_template_type": args.type or "section",
            "_elementor_edit_mode": "builder",
            "_elementor_version": "3.20.0",
        }
    }

    if args.layout_file:
        with open(args.layout_file, "r", encoding="utf-8") as f:
            layout = json.load(f)
        data["meta"]["_elementor_data"] = json.dumps(layout)

    if args.display_conditions:
        try:
            data["meta"]["_elementor_conditions"] = json.dumps(
                json.loads(args.display_conditions)
            )
        except json.JSONDecodeError:
            data["meta"]["_elementor_conditions"] = args.display_conditions

    try:
        result = _api_post("wp/v2/elementor_library", data)
    except Exception:
        # Fallback: create as a regular page with template type
        result = _api_post("wp/v2/pages", data)

    return {
        "created": True,
        "template": {
            "id": result["id"],
            "title": result["title"]["rendered"],
            "type": args.type or "section",
            "status": result["status"],
            "link": result.get("link", ""),
        }
    }


def action_kit_export(args):
    """Export Elementor kit settings (global colors, typography, etc.)."""
    # Elementor kit data is stored in the 'elementor_active_kit' option
    kit_id = None
    try:
        settings = _api_get("elementor/v1/globals")
    except Exception:
        settings = {}

    kit_data = {
        "exported_at": "",
        "site_url": WP_URL,
        "globals": settings,
        "note": "Full kit export requires Elementor Pro REST API. "
                "Use Elementor → Tools → Export Kit for complete export.",
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(kit_data, f, indent=2)
        return {"exported": True, "file": str(output_path)}

    return kit_data


def action_kit_import(args):
    """Import Elementor kit settings from a JSON file."""
    if not args.file:
        return {"error": True, "message": "Provide --file with kit JSON"}

    with open(args.file, "r", encoding="utf-8") as f:
        kit_data = json.load(f)

    # Elementor kit import via REST API
    try:
        result = _api_post("elementor/v1/kits/import", kit_data)
        return {"imported": True, "result": result}
    except Exception as e:
        return {
            "partial": True,
            "message": f"Kit import via REST API failed: {e}. "
                       "Use Elementor → Tools → Import Kit for full import.",
            "kit_data_keys": list(kit_data.keys()) if isinstance(kit_data, dict) else [],
        }


def action_responsive_check(args):
    """Check responsive settings for a page."""
    page_data = action_get_page(args)
    elementor_data = page_data.get("elementor_data", "")

    if not elementor_data:
        return {"error": True, "message": "No Elementor data found for this page"}

    try:
        if isinstance(elementor_data, str):
            elementor_data = json.loads(elementor_data)
    except json.JSONDecodeError:
        return {"error": True, "message": "Could not parse Elementor data"}

    # Analyze responsive breakpoints
    breakpoints = {
        "mobile": {"width": 767, "visible": 0, "hidden": 0},
        "tablet": {"width": 1024, "visible": 0, "hidden": 0},
        "desktop": {"width": 9999, "visible": 0, "hidden": 0},
    }

    def _analyze_element(el, bp_stats):
        """Recursively analyze element responsiveness."""
        if isinstance(el, dict):
            resp = el.get("responsive", {})
            show_on = el.get("show_on", "desktop")
            # Count visibility settings
            for bp in bp_stats:
                if show_on == bp:
                    bp_stats[bp]["visible"] += 1
            for child in el.get("elements", []):
                _analyze_element(child, bp_stats)
        elif isinstance(el, list):
            for item in el:
                _analyze_element(item, bp_stats)

    _analyze_element(elementor_data, breakpoints)

    return {
        "page_id": page_data["page"]["id"],
        "page_title": page_data["page"]["title"],
        "breakpoints": breakpoints,
        "recommendations": [
            "Check mobile view at 767px width",
            "Check tablet view at 1024px width",
            "Verify all critical content is visible on mobile",
        ],
    }


def action_list_elementor_pages(args):
    """List pages built with Elementor (have _elementor_data meta)."""
    params = {
        "per_page": args.per_page or 50,
        "page": args.page or 1,
        "meta_key": "_elementor_edit_mode",
        "meta_value": "builder",
        "orderby": "modified",
        "order": "desc",
    }
    result = _api_get("wp/v2/pages", params)
    pages = []
    for p in result:
        pages.append({
            "id": p["id"],
            "title": p["title"]["rendered"],
            "slug": p["slug"],
            "status": p["status"],
            "modified": p["modified"],
            "link": p["link"],
            "template": p.get("template", ""),
        })
    return {
        "elementor_pages": pages,
        "total": len(pages),
        "hint": "These pages have _elementor_edit_mode=builder",
    }


def action_get_globals(args):
    """Get Elementor global settings (colors, typography, etc.)."""
    try:
        globals_data = _api_get("elementor/v1/globals")
        colors = globals_data.get("colors", {})
        typography = globals_data.get("typography", {})
        return {
            "colors": {
                k: {"title": v.get("title", ""), "value": v.get("value", "")}
                for k, v in colors.items()
            } if isinstance(colors, dict) else {},
            "typography": {
                k: {"title": v.get("title", "")}
                for k, v in typography.items()
            } if isinstance(typography, dict) else {},
        }
    except Exception as e:
        return {"error": True, "message": str(e),
                "hint": "Elementor globals API may require Elementor Pro"}


def action_get_document(args):
    """Get full Elementor document data for a page (REST API format)."""
    if not args.id:
        return {"error": True, "message": "Provide --id with page ID"}
    try:
        doc = _api_get(f"elementor/v1/documents/{args.id}")
        return {"document": doc}
    except Exception as e:
        return {"error": True, "message": str(e),
                "hint": "Try --action get-page for meta-based access"}


def action_save_document(args):
    """Save Elementor document data to a page."""
    if not args.id:
        return {"error": True, "message": "Provide --id with page ID"}
    if not args.layout_json:
        return {"error": True, "message": "Provide --layout-json with Elementor data"}
    try:
        layout = json.loads(args.layout_json)
        meta_update = {
            "meta": {
                "_elementor_data": json.dumps(layout),
                "_elementor_edit_mode": "builder",
                "_elementor_version": args.version or "3.20.0",
            }
        }
        if args.template_type:
            meta_update["meta"]["_elementor_template_type"] = args.template_type

        result = _api_post(f"wp/v2/pages/{args.id}", meta_update)
        return {
            "saved": True,
            "page_id": result["id"],
            "title": result["title"]["rendered"],
            "link": result["link"],
        }
    except Exception as e:
        return {"error": True, "message": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Elementor Page Builder Operations"
    )
    parser.add_argument("--action", required=True, choices=[
        "status", "get-page", "update-page",
        "list-templates", "create-template",
        "kit-export", "kit-import",
        "responsive-check",
        "list-elementor-pages", "get-globals",
        "get-document", "save-document",
    ])
    parser.add_argument("--id", type=int, help="Page/template ID")
    parser.add_argument("--name", help="Template name")
    parser.add_argument("--type", help="Template type (section, page, header, footer, etc.)")
    parser.add_argument("--layout-file", dest="layout_file", help="JSON file with Elementor layout data")
    parser.add_argument("--layout-json", dest="layout_json", help="JSON string with Elementor layout data")
    parser.add_argument("--version", help="Elementor version")
    parser.add_argument("--template-type", dest="template_type")
    parser.add_argument("--display-conditions", dest="display_conditions")
    parser.add_argument("--output", help="Output file path for exports")
    parser.add_argument("--file", help="Input file path for imports")
    parser.add_argument("--breakpoint", choices=["mobile", "tablet", "desktop"])
    parser.add_argument("--per-page", dest="per_page", type=int)
    parser.add_argument("--page", type=int)

    args = parser.parse_args()
    _check_config()

    action_map = {
        "status": lambda: action_status(args),
        "get-page": lambda: action_get_page(args),
        "update-page": lambda: action_update_page(args),
        "list-templates": lambda: action_list_templates(args),
        "create-template": lambda: action_create_template(args),
        "kit-export": lambda: action_kit_export(args),
        "kit-import": lambda: action_kit_import(args),
        "responsive-check": lambda: action_responsive_check(args),
        "list-elementor-pages": lambda: action_list_elementor_pages(args),
        "get-globals": lambda: action_get_globals(args),
        "get-document": lambda: action_get_document(args),
        "save-document": lambda: action_save_document(args),
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
        print(json.dumps({
            "error": True,
            "status_code": e.response.status_code,
            "message": str(e),
            "details": error_body
        }, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
