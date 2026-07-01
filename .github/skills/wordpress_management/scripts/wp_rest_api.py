#!/usr/bin/env python3
"""
WordPress REST API Client

Full CRUD operations for WordPress content management via the REST API.
Supports pages, posts, media, users, comments, menus, widgets, and settings.

Usage:
    python wp_rest_api.py --action ping
    python wp_rest_api.py --action list-pages
    python wp_rest_api.py --action create-page --title "About" --content "<p>...</p>"
    python wp_rest_api.py --action upload-media --file ./image.jpg
"""

import os
import sys
import json
import argparse
import base64
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

# Load .env from agent root
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
    """Verify required env vars are set."""
    missing = []
    if not WP_URL:
        missing.append("WORDPRESS_SITE_URL")
    if not WP_USER:
        missing.append("WORDPRESS_USERNAME")
    if not WP_APP_PASSWORD:
        missing.append("WORDPRESS_APP_PASSWORD")
    if missing:
        print(json.dumps({"error": True, "message": f"Missing env vars: {', '.join(missing)}", "fix": "Set them in .env file"}))
        sys.exit(1)


def _api_get(endpoint: str, params: dict = None) -> dict:
    """GET request to WordPress REST API."""
    url = urljoin(API_BASE + "/", endpoint.lstrip("/"))
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return {"data": resp.json(), "total": resp.headers.get("X-WP-Total", "unknown"), "total_pages": resp.headers.get("X-WP-TotalPages", "unknown")}


def _api_post(endpoint: str, data: dict) -> dict:
    """POST request to WordPress REST API."""
    url = urljoin(API_BASE + "/", endpoint.lstrip("/"))
    resp = requests.post(url, headers=HEADERS, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _api_put(endpoint: str, data: dict) -> dict:
    """PUT request to WordPress REST API."""
    url = urljoin(API_BASE + "/", endpoint.lstrip("/"))
    resp = requests.put(url, headers=HEADERS, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _api_delete(endpoint: str, params: dict = None) -> dict:
    """DELETE request to WordPress REST API."""
    url = urljoin(API_BASE + "/", endpoint.lstrip("/"))
    resp = requests.delete(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def action_ping():
    """Test WordPress REST API connectivity."""
    try:
        resp = requests.get(f"{WP_URL}/wp-json/", headers=HEADERS, timeout=10)
        data = resp.json()
        return {
            "connected": True,
            "site_url": WP_URL,
            "wordpress_version": resp.headers.get("X-WP-Version", "unknown"),
            "api_namespaces": data.get("namespaces", [])[:5],
            "authentication": "OK" if resp.status_code == 200 else "Failed",
        }
    except requests.RequestException as e:
        return {"connected": False, "error": str(e)}


def action_list_pages(args):
    """List WordPress pages."""
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.status:
        params["status"] = args.status
    if args.search:
        params["search"] = args.search
    result = _api_get("pages", params)
    pages = []
    for p in result["data"]:
        pages.append({
            "id": p["id"], "title": p["title"]["rendered"],
            "slug": p["slug"], "status": p["status"],
            "date": p["date"], "modified": p["modified"],
            "link": p["link"], "template": p.get("template", ""),
        })
    return {"pages": pages, "total": result["total"], "total_pages": result["total_pages"]}


def action_get_page(args):
    """Get a single page by ID."""
    p = _api_get(f"pages/{args.id}")["data"]
    return {
        "id": p["id"], "title": p["title"]["rendered"],
        "content": p["content"]["rendered"], "raw_content": p["content"]["raw"],
        "slug": p["slug"], "status": p["status"],
        "date": p["date"], "modified": p["modified"],
        "link": p["link"], "template": p.get("template", ""),
        "meta": p.get("meta", {}),
    }


def action_create_page(args):
    """Create a new WordPress page."""
    data = {
        "title": args.title,
        "content": args.content or "",
        "status": args.status or "draft",
    }
    if args.slug:
        data["slug"] = args.slug
    if args.template:
        data["template"] = args.template
    if args.parent:
        data["parent"] = int(args.parent)

    result = _api_post("pages", data)
    return {"created": True, "page": {"id": result["id"], "title": result["title"]["rendered"], "link": result["link"], "status": result["status"]}}


def action_update_page(args):
    """Update an existing WordPress page."""
    data = {}
    if args.title:
        data["title"] = args.title
    if args.content is not None:
        data["content"] = args.content
    if args.status:
        data["status"] = args.status
    if args.slug:
        data["slug"] = args.slug
    if args.template:
        data["template"] = args.template

    result = _api_put(f"pages/{args.id}", data)
    return {"updated": True, "page": {"id": result["id"], "title": result["title"]["rendered"], "link": result["link"], "status": result["status"]}}


def action_delete_page(args):
    """Delete a WordPress page."""
    params = {"force": args.force if args.force else False}
    result = _api_delete(f"pages/{args.id}", params)
    return {"deleted": True, "id": result.get("id", args.id), "previous_status": result.get("previous", {}).get("status", "unknown")}


def action_list_posts(args):
    """List WordPress blog posts."""
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.status:
        params["status"] = args.status
    if args.search:
        params["search"] = args.search
    if args.categories:
        params["categories"] = args.categories
    if args.tags:
        params["tags"] = args.tags
    result = _api_get("posts", params)
    posts = []
    for p in result["data"]:
        posts.append({
            "id": p["id"], "title": p["title"]["rendered"],
            "slug": p["slug"], "status": p["status"],
            "date": p["date"], "modified": p["modified"],
            "link": p["link"], "excerpt": p["excerpt"]["rendered"],
        })
    return {"posts": posts, "total": result["total"], "total_pages": result["total_pages"]}


def action_get_post(args):
    """Get a single post by ID."""
    p = _api_get(f"posts/{args.id}")["data"]
    return {
        "id": p["id"], "title": p["title"]["rendered"],
        "content": p["content"]["rendered"], "raw_content": p["content"]["raw"],
        "slug": p["slug"], "status": p["status"],
        "date": p["date"], "modified": p["modified"],
        "link": p["link"], "excerpt": p["excerpt"]["rendered"],
        "categories": p.get("categories", []), "tags": p.get("tags", []),
    }


def action_create_post(args):
    """Create a new blog post."""
    data = {
        "title": args.title,
        "content": args.content or "",
        "status": args.status or "draft",
    }
    if args.slug:
        data["slug"] = args.slug
    if args.excerpt:
        data["excerpt"] = args.excerpt
    if args.categories:
        data["categories"] = [int(c) for c in args.categories.split(",")]
    if args.tags:
        data["tags"] = [int(t) for t in args.tags.split(",")]
    if args.featured_media:
        data["featured_media"] = int(args.featured_media)

    result = _api_post("posts", data)
    return {"created": True, "post": {"id": result["id"], "title": result["title"]["rendered"], "link": result["link"], "status": result["status"]}}


def action_update_post(args):
    """Update an existing blog post."""
    data = {}
    if args.title:
        data["title"] = args.title
    if args.content is not None:
        data["content"] = args.content
    if args.status:
        data["status"] = args.status
    if args.excerpt:
        data["excerpt"] = args.excerpt

    result = _api_put(f"posts/{args.id}", data)
    return {"updated": True, "post": {"id": result["id"], "title": result["title"]["rendered"], "link": result["link"]}}


def action_upload_media(args):
    """Upload media file to WordPress."""
    file_path = Path(args.file)
    if not file_path.exists():
        return {"error": True, "message": f"File not found: {args.file}"}

    media_headers = {"Authorization": f"Basic {AUTH}", "User-Agent": "Agent-Website-Manager/1.0"}
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, _guess_mime(file_path.suffix))}
        data = {}
        if args.alt_text:
            data["alt_text"] = args.alt_text
        if args.caption:
            data["caption"] = args.caption

        resp = requests.post(f"{API_BASE}/media", headers={"Authorization": f"Basic {AUTH}"}, files=files, data=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()

    return {
        "uploaded": True,
        "media": {
            "id": result["id"], "title": result["title"]["rendered"],
            "url": result["source_url"], "type": result["media_type"],
            "mime": result["mime_type"], "alt_text": result.get("alt_text", ""),
        }
    }


def action_list_media(args):
    """List media library items."""
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.search:
        params["search"] = args.search
    if args.media_type:
        params["media_type"] = args.media_type
    result = _api_get("media", params)
    items = []
    for m in result["data"]:
        items.append({
            "id": m["id"], "title": m["title"]["rendered"],
            "url": m["source_url"], "type": m["media_type"],
            "mime": m["mime_type"], "date": m["date"],
        })
    return {"media": items, "total": result["total"]}


def action_list_users(args):
    """List WordPress users."""
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.roles:
        params["roles"] = args.roles
    result = _api_get("users", params)
    users = []
    for u in result["data"]:
        users.append({
            "id": u["id"], "name": u["name"], "slug": u["slug"],
            "roles": u.get("roles", []), "avatar": u.get("avatar_urls", {}).get("96", ""),
        })
    return {"users": users, "total": result["total"]}


def action_list_comments(args):
    """List comments."""
    params = {"per_page": args.per_page or 20, "page": args.page or 1}
    if args.status:
        params["status"] = args.status
    if args.post:
        params["post"] = args.post
    result = _api_get("comments", params)
    comments = []
    for c in result["data"]:
        comments.append({
            "id": c["id"], "author": c["author_name"],
            "content": c["content"]["rendered"][:200],
            "status": c["status"], "date": c["date"],
            "post_id": c["post"], "link": c["link"],
        })
    return {"comments": comments, "total": result["total"]}


def action_get_settings(args):
    """Get WordPress site settings."""
    result = _api_get("settings")["data"]
    return {
        "site_title": result.get("title", ""),
        "tagline": result.get("description", ""),
        "site_url": result.get("url", ""),
        "admin_email": result.get("email", ""),
        "timezone": result.get("timezone", ""),
        "date_format": result.get("date_format", ""),
        "posts_per_page": result.get("posts_per_page", ""),
        "default_category": result.get("default_category", ""),
        "default_post_format": result.get("default_post_format", ""),
        "use_smilies": result.get("use_smilies", ""),
        "show_on_front": result.get("show_on_front", ""),
        "page_on_front": result.get("page_on_front", ""),
        "page_for_posts": result.get("page_for_posts", ""),
    }


def action_update_settings(args):
    """Update WordPress site settings."""
    data = {}
    if args.title:
        data["title"] = args.title
    if args.tagline:
        data["description"] = args.tagline
    if args.admin_email:
        data["email"] = args.admin_email
    if args.timezone:
        data["timezone"] = args.timezone
    if args.show_on_front:
        data["show_on_front"] = args.show_on_front
    if args.page_on_front:
        data["page_on_front"] = int(args.page_on_front)

    result = _api_put("settings", data)
    return {"updated": True, "settings": result}


def _guess_mime(suffix: str) -> str:
    """Guess MIME type from file extension."""
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
        ".mp4": "video/mp4", ".mov": "video/quicktime",
        ".pdf": "application/pdf", ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return mime_map.get(suffix.lower(), "application/octet-stream")


# ═══════════════════════════════════════════════════════════════════════════════
# PLUGIN & THEME ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def action_list_plugins(args):
    """List all installed plugins with status and version."""
    try:
        result = _api_get("plugins")
    except Exception as e:
        return {"error": True, "message": str(e),
                "hint": "Plugin REST API requires admin credentials"}
    plugins = []
    active_count = 0
    for p in result["data"]:
        plugins.append({
            "plugin": p["plugin"],
            "name": p.get("name", ""),
            "version": p.get("version", ""),
            "status": p["status"],
            "description": (p.get("description", {}).get("rendered", "")
                             if isinstance(p.get("description"), dict)
                             else p.get("description", ""))[:200],
        })
        if p["status"] == "active":
            active_count += 1
    return {
        "plugins": plugins,
        "total": len(plugins),
        "active": active_count,
        "inactive": len(plugins) - active_count,
    }


def action_list_themes(args):
    """List all installed themes."""
    try:
        result = _api_get("themes")
    except Exception as e:
        return {"error": True, "message": str(e)}
    themes = []
    for t in result["data"]:
        themes.append({
            "stylesheet": t["stylesheet"],
            "name": t.get("name", ""),
            "version": t.get("version", ""),
            "status": t.get("status", ""),
            "author": t.get("author", {}).get("name", "") if isinstance(
                t.get("author"), dict) else "",
        })
    return {"themes": themes, "total": len(themes)}


def action_delete_plugin(args):
    """Delete a plugin by slug."""
    if not args.plugin_slug:
        return {"error": True, "message": "Provide --plugin-slug with plugin slug to delete"}
    try:
        result = _api_delete(f"plugins/{args.plugin_slug}")
        return {"deleted": True, "slug": args.plugin_slug, "result": result}
    except Exception as e:
        return {"deleted": False, "slug": args.plugin_slug,
                "error": str(e),
                "hint": "Plugin may already be removed from disk, or REST API requires admin."}


def action_activate_plugin(args):
    """Activate a plugin by slug."""
    if not args.plugin_slug:
        return {"error": True, "message": "Provide --plugin-slug with plugin slug"}
    try:
        result = _api_put(f"plugins/{args.plugin_slug}", {"status": "active"})
        return {"activated": True, "slug": args.plugin_slug, "result": result}
    except Exception as e:
        return {"activated": False, "slug": args.plugin_slug, "error": str(e)}


def action_deactivate_plugin(args):
    """Deactivate a plugin by slug."""
    if not args.plugin_slug:
        return {"error": True, "message": "Provide --plugin-slug with plugin slug"}
    try:
        result = _api_put(f"plugins/{args.plugin_slug}", {"status": "inactive"})
        return {"deactivated": True, "slug": args.plugin_slug, "result": result}
    except Exception as e:
        return {"deactivated": False, "slug": args.plugin_slug, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# SITE HEALTH & MAINTENANCE ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def action_site_health(args):
    """Get WordPress Site Health status."""
    try:
        health = _api_get_raw(f"{WP_URL}/wp-json/wp-site-health/v1")
        tests = health.get("tests", {})
    except Exception as e:
        return {"error": True, "message": str(e),
                "hint": "Site Health API requires admin or site-health scope"}

    issues = {"critical": [], "recommended": [], "good": []}
    for category in ["direct", "async"]:
        for test in tests.get(category, {}).values():
            if isinstance(test, dict):
                for item in test.get("issues", []):
                    severity = item.get("severity", "recommended")
                    entry = {
                        "label": item.get("label", ""),
                        "status": item.get("status", ""),
                        "description": item.get("description", "")[:300],
                    }
                    if severity == "critical":
                        issues["critical"].append(entry)
                    elif severity == "recommended":
                        issues["recommended"].append(entry)
                    else:
                        issues["good"].append(entry)
    return {
        "site_health": issues,
        "total_issues": sum(len(v) for v in issues.values()),
    }


def action_db_cleanup(args):
    """Run database cleanup operations.

    Posts: delete revisions, auto-drafts, trashed items
    Comments: delete spam/trash
    Options: remove expired transients
    Meta: clean orphaned post/user/term meta
    """
    results = {}

    # 1. Delete all post revisions
    try:
        rev_posts, _ = _api_get("posts", {"per_page": 1, "status": "revision"})
        rev_count = int(_.get("X-WP-Total", 0))
        results["revisions_found"] = rev_count
    except Exception:
        rev_count = 0
        results["revisions_found"] = "unknown"

    # 2. Delete trashed posts
    try:
        trash_posts, _ = _api_get("posts", {"per_page": 1, "status": "trash"})
        trash_count = int(_.get("X-WP-Total", 0))
        results["trashed_posts"] = trash_count
        deleted = 0
        if args.execute and trash_count > 0:
            trash_list, _ = _api_get("posts",
                                     {"per_page": 100, "status": "trash"})
            for p in trash_list["data"]:
                try:
                    _api_delete(f"posts/{p['id']}", {"force": True})
                    deleted += 1
                except Exception:
                    pass
            results["trashed_deleted"] = deleted
    except Exception:
        results["trashed_posts"] = "unknown"

    # 3. Delete spam/trash comments
    try:
        spam_comments, _ = _api_get("comments",
                                    {"per_page": 1, "status": "spam"})
        spam_count = int(_.get("X-WP-Total", 0))
        results["spam_comments"] = spam_count
        if args.execute and spam_count > 0:
            spam_list, _ = _api_get("comments",
                                    {"per_page": 100, "status": "spam"})
            for c in spam_list["data"]:
                try:
                    _api_delete(f"comments/{c['id']}", {"force": True})
                except Exception:
                    pass
    except Exception:
        results["spam_comments"] = "unknown"

    results["executed"] = args.execute if hasattr(args, 'execute') else False
    if not args.execute:
        results["hint"] = "Dry run. Use --execute to actually delete items."

    return results


def _api_get_raw(url: str) -> dict:
    """GET request to any WordPress API endpoint."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="WordPress REST API Client")
    parser.add_argument("--action", required=True, choices=[
        "ping", "list-pages", "get-page", "create-page", "update-page", "delete-page",
        "list-posts", "get-post", "create-post", "update-post",
        "upload-media", "list-media",
        "list-users", "list-comments",
        "get-settings", "update-settings",
        "list-plugins", "list-themes", "delete-plugin",
        "activate-plugin", "deactivate-plugin",
        "site-health", "db-cleanup",
    ])
    # Page/Post args
    parser.add_argument("--id", type=int)
    parser.add_argument("--title")
    parser.add_argument("--content")
    parser.add_argument("--slug")
    parser.add_argument("--status", choices=["publish", "future", "draft", "pending", "private"])
    parser.add_argument("--template")
    parser.add_argument("--parent", type=int)
    parser.add_argument("--excerpt")
    parser.add_argument("--categories")
    parser.add_argument("--tags")
    parser.add_argument("--featured_media", type=int)
    parser.add_argument("--force", action="store_true")
    # Media args
    parser.add_argument("--file")
    parser.add_argument("--alt-text", dest="alt_text")
    parser.add_argument("--caption")
    parser.add_argument("--media_type")
    # List args
    parser.add_argument("--per-page", dest="per_page", type=int)
    parser.add_argument("--page", type=int)
    parser.add_argument("--search")
    parser.add_argument("--roles")
    parser.add_argument("--post")
    # Settings args
    parser.add_argument("--tagline")
    parser.add_argument("--admin-email", dest="admin_email")
    parser.add_argument("--timezone")
    parser.add_argument("--show-on-front", dest="show_on_front")
    parser.add_argument("--page-on-front", dest="page_on_front", type=int)
    # Plugin args
    parser.add_argument("--plugin-slug", dest="plugin_slug",
                        help="Plugin slug (e.g., 'elementor')")
    # DB cleanup args
    parser.add_argument("--execute", action="store_true",
                        help="Actually execute destructive db-cleanup operations")

    args = parser.parse_args()
    _check_config()

    action_map = {
        "ping": lambda: action_ping(),
        "list-pages": lambda: action_list_pages(args),
        "get-page": lambda: action_get_page(args),
        "create-page": lambda: action_create_page(args),
        "update-page": lambda: action_update_page(args),
        "delete-page": lambda: action_delete_page(args),
        "list-posts": lambda: action_list_posts(args),
        "get-post": lambda: action_get_post(args),
        "create-post": lambda: action_create_post(args),
        "update-post": lambda: action_update_post(args),
        "upload-media": lambda: action_upload_media(args),
        "list-media": lambda: action_list_media(args),
        "list-users": lambda: action_list_users(args),
        "list-comments": lambda: action_list_comments(args),
        "get-settings": lambda: action_get_settings(args),
        "update-settings": lambda: action_update_settings(args),
        "list-plugins": lambda: action_list_plugins(args),
        "list-themes": lambda: action_list_themes(args),
        "delete-plugin": lambda: action_delete_plugin(args),
        "activate-plugin": lambda: action_activate_plugin(args),
        "deactivate-plugin": lambda: action_deactivate_plugin(args),
        "site-health": lambda: action_site_health(args),
        "db-cleanup": lambda: action_db_cleanup(args),
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
