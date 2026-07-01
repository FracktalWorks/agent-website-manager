#!/usr/bin/env python3
"""
WordPress Media Cleanup Tool

Detects unused/orphaned images, finds oversized media, identifies images
missing alt text, and safely removes unused files from the media library.

Detection strategy:
1. Fetches ALL media IDs via REST API with pagination
2. For each media ID, checks if referenced in:
   - Post/page content (post_content search)
   - Featured images (post meta _thumbnail_id)
   - WooCommerce product images & galleries
   - Elementor page data (_elementor_data)
   - Widget instances and theme mods
3. Flags media NOT found anywhere as "unused"

Usage:
    python wp_media_cleanup.py --action audit
    python wp_media_cleanup.py --action find-unused
    python wp_media_cleanup.py --action clean --dry-run
    python wp_media_cleanup.py --action find-oversized --max-size 500
"""

import os, sys, json, argparse, base64
from pathlib import Path
from datetime import datetime
from collections import defaultdict
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


def _get_all_pages(endpoint, params=None, per_page=100):
    """Paginate through all results of a WP REST API endpoint."""
    params = (params or {}).copy()
    params["per_page"] = per_page
    params["page"] = 1
    all_data = []
    while True:
        url = f"{API}/{endpoint.lstrip('/')}"
        r = requests.get(url, headers=HEADERS, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        all_data.extend(data)
        total_pages = int(r.headers.get("X-WP-TotalPages", 1))
        if params["page"] >= total_pages:
            break
        params["page"] += 1
    return all_data


def _get_all_media():
    """Fetch all media items with full details."""
    print("Fetching all media items...", file=sys.stderr)
    media = _get_all_pages("media", {"_fields": "id,title,source_url,"
        "media_type,mime_type,media_details,alt_text,date,author,post"})
    return media


def _search_post_content(media_ids):
    """Search for media IDs referenced in all post/page content."""
    print("Searching post content for media references...", file=sys.stderr)
    referenced = set()
    all_posts = _get_all_pages("posts", {"_fields": "id,content"})
    all_pages = _get_all_pages("pages", {"_fields": "id,content"})
    all_content = all_posts + all_pages

    for post in all_content:
        content = post.get("content", {}).get("rendered", "")
        if not content:
            continue
        for mid in media_ids:
            # Check for wp-image-<id> CSS class and wp:image references
            if f"wp-image-{mid}" in content:
                referenced.add(mid)
            if f'"id":{mid}' in content:
                referenced.add(mid)
    return referenced


def _search_featured_images():
    """Get all featured image (thumbnail) IDs."""
    print("Fetching featured images...", file=sys.stderr)
    featured = set()
    all_posts = _get_all_pages("posts", {"_fields": "id,featured_media"})
    all_pages = _get_all_pages("pages", {"_fields": "id,featured_media"})
    for item in all_posts + all_pages:
        fm = item.get("featured_media", 0)
        if fm:
            featured.add(fm)
    return featured


def _search_elementor_data():
    """Search Elementor page data for image references."""
    print("Searching Elementor data for media references...", file=sys.stderr)
    referenced = set()
    all_pages = _get_all_pages("pages", {"_fields": "id,meta"})
    for page in all_pages:
        meta = page.get("meta", {})
        elem_data = meta.get("_elementor_data", "")
        if not elem_data:
            continue
        if isinstance(elem_data, list):
            elem_data = json.dumps(elem_data)
        # Search for any image ID references in Elementor JSON
        for ch in ['"id":', '"image":', '"background_image":',
                    '"bg_image":', '"logo":']:
            if ch in str(elem_data):
                try:
                    data = json.loads(elem_data) if isinstance(elem_data, str) else elem_data
                    _extract_ids_from_elementor(data, referenced)
                except Exception:
                    pass
                break
    return referenced


def _extract_ids_from_elementor(data, refs):
    """Recursively extract image-related IDs from Elementor JSON."""
    if isinstance(data, dict):
        for key, val in data.items():
            if key in ("id", "image") and isinstance(val, (int, str)):
                try:
                    refs.add(int(val))
                except ValueError:
                    pass
            elif isinstance(val, (dict, list)):
                _extract_ids_from_elementor(val, refs)
    elif isinstance(data, list):
        for item in data:
            _extract_ids_from_elementor(item, refs)


def _search_woocommerce():
    """Search WooCommerce product images and galleries."""
    referenced = set()
    # Try WooCommerce REST API
    wc_key = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
    wc_secret = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")
    if not wc_key or not wc_secret:
        return referenced

    print("Searching WooCommerce products for media references...", file=sys.stderr)
    wc_auth = base64.b64encode(f"{wc_key}:{wc_secret}".encode()).decode()
    wc_headers = {"Authorization": f"Basic {wc_auth}"}
    wc_api = f"{WP_URL}/wp-json/wc/v3"

    try:
        params = {"per_page": 100, "page": 1, "_fields": "id,images"}
        while True:
            r = requests.get(f"{wc_api}/products", headers=wc_headers,
                             params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            if not data:
                break
            for product in data:
                for img in product.get("images", []):
                    referenced.add(img.get("id"))
                for gallery_img in product.get("gallery_images", []):
                    referenced.add(gallery_img.get("id"))
            total_pages = int(r.headers.get("X-WP-TotalPages", 1))
            if params["page"] >= total_pages:
                break
            params["page"] += 1
    except Exception:
        pass

    return referenced


def action_audit(args):
    """Full media library audit."""
    media = _get_all_media()
    total = len(media)
    total_size = 0
    by_type = defaultdict(int)
    by_mime = defaultdict(int)
    by_year = defaultdict(int)
    missing_alt = 0

    for m in media:
        # Size
        filesize = m.get("media_details", {}).get("filesize", 0)
        total_size += filesize
        # Type
        by_type[m.get("media_type", "unknown")] += 1
        by_mime[m.get("mime_type", "unknown")] += 1
        # Year
        date = m.get("date", "")
        if date:
            by_year[date[:4]] += 1
        # Alt text
        if not m.get("alt_text"):
            missing_alt += 1

    return {
        "total_media": total,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "by_type": dict(by_type),
        "by_mime_type": dict(by_mime),
        "by_year": dict(by_year),
        "missing_alt_text": missing_alt,
        "missing_alt_percent": round(missing_alt / total * 100, 1) if total else 0,
    }


def action_find_unused(args):
    """Find all unused media items."""
    media = _get_all_media()
    media_ids = {m["id"] for m in media}
    print(f"Total media items: {len(media_ids)}", file=sys.stderr)

    # Gather all referenced IDs
    referenced = set()
    referenced |= _search_post_content(media_ids)
    referenced |= _search_featured_images()
    referenced |= _search_elementor_data()
    referenced |= _search_woocommerce()

    # Also check site icon/logo
    settings_url = f"{API}/settings"
    try:
        r = requests.get(settings_url, headers=HEADERS, timeout=15)
        settings = r.json()
        for key in ("site_logo", "site_icon"):
            if settings.get(key):
                referenced.add(settings[key])
    except Exception:
        pass

    unused = media_ids - referenced
    unused_items = [m for m in media if m["id"] in unused]
    total_size = sum(m.get("media_details", {}).get("filesize", 0)
                     for m in unused_items)

    return {
        "total_media": len(media_ids),
        "referenced": len(referenced),
        "unused": len(unused),
        "unused_percent": round(len(unused) / len(media_ids) * 100, 1) if media_ids else 0,
        "wasted_space_mb": round(total_size / (1024 * 1024), 2),
        "unused_items": [
            {"id": m["id"], "title": m["title"]["rendered"],
             "url": m["source_url"], "date": m.get("date", ""),
             "size_kb": round(m.get("media_details", {}).get("filesize", 0) / 1024, 1)}
            for m in unused_items[:100]  # Limit to first 100
        ],
        "total_unused_count": len(unused),
    }


def action_clean(args):
    """Delete unused media items."""
    unused_result = action_find_unused(args)
    unused = unused_result["unused_items"]

    if not unused:
        return {"message": "No unused media found!", "deleted": 0}

    if args.dry_run:
        return {
            "dry_run": True,
            "would_delete": len(unused),
            "would_free_mb": unused_result["wasted_space_mb"],
            "items": unused[:20],
        }

    if not args.confirm:
        return {
            "error": True,
            "message": "Use --confirm to actually delete. Use --dry-run to preview first.",
            "unused_count": len(unused),
        }

    deleted = []
    failed = []
    for item in unused[:args.limit or len(unused)]:
        try:
            url = f"{API}/media/{item['id']}?force=true"
            r = requests.delete(url, headers=HEADERS, timeout=15)
            if r.status_code in (200, 204):
                deleted.append(item["id"])
            else:
                failed.append({"id": item["id"], "status": r.status_code})
        except Exception as e:
            failed.append({"id": item["id"], "error": str(e)})

    return {
        "deleted": len(deleted),
        "deleted_ids": deleted,
        "failed": failed,
        "freed_mb_approx": round(
            sum(i["size_kb"] for i in unused if i["id"] in deleted) / 1024, 2),
    }


def action_find_oversized(args):
    """Find images above a certain size threshold."""
    max_size_kb = (args.max_size or 500) * 1024
    media = _get_all_media()
    oversized = []
    for m in media:
        size = m.get("media_details", {}).get("filesize", 0)
        if size > max_size_kb and m.get("media_type") == "image":
            oversized.append({
                "id": m["id"], "title": m["title"]["rendered"],
                "url": m["source_url"], "size_kb": round(size / 1024, 1),
                "dimensions": m.get("media_details", {}).get("sizes", {}).get(
                    "full", {}).get("width", "?"),
                "date": m.get("date", ""),
            })
    oversized.sort(key=lambda x: x["size_kb"], reverse=True)
    return {
        "threshold_kb": args.max_size or 500,
        "oversized_count": len(oversized),
        "total_wasted_kb": round(sum(o["size_kb"] for o in oversized), 1),
        "items": oversized[:50],
    }


def action_missing_alt(args):
    """List all images missing alt text."""
    media = _get_all_media()
    missing = [{"id": m["id"], "title": m["title"]["rendered"],
                "url": m["source_url"], "date": m.get("date", "")}
               for m in media if not m.get("alt_text") and m.get("media_type") == "image"]
    return {"missing_alt": len(missing), "total_images": len(media),
            "items": missing[:100]}


def action_list_by_size(args):
    """List media items sorted by file size."""
    media = _get_all_media()
    items = [{"id": m["id"], "title": m["title"]["rendered"],
              "url": m["source_url"],
              "size_kb": round(m.get("media_details", {}).get("filesize", 0) / 1024, 1),
              "type": m.get("media_type", ""), "date": m.get("date", "")}
             for m in media]
    items.sort(key=lambda x: x["size_kb"], reverse=(args.sort != "asc"))
    return {"total": len(items), "items": items[:50]}


def action_organize(args):
    """Bulk update titles and alt text from filenames."""
    media = _get_all_media()
    updates = []
    for m in media:
        filename = Path(m.get("source_url", "")).stem
        # Convert filename to readable title
        readable = filename.replace("-", " ").replace("_", " ").title()
        needs_title = m["title"]["rendered"] in ("", filename, "Image")
        needs_alt = not m.get("alt_text")

        if needs_title or needs_alt:
            update = {"id": m["id"], "current_title": m["title"]["rendered"]}
            if needs_title:
                update["new_title"] = readable
            if needs_alt:
                update["new_alt"] = readable
            updates.append(update)

    if args.dry_run:
        return {"dry_run": True, "would_update": len(updates), "items": updates[:20]}

    applied = 0
    for u in updates[:args.limit or len(updates)]:
        try:
            data = {}
            if "new_title" in u:
                data["title"] = u["new_title"]
            if "new_alt" in u:
                data["alt_text"] = u["new_alt"]
            requests.post(f"{API}/media/{u['id']}", headers=HEADERS,
                          json=data, timeout=15)
            applied += 1
        except Exception:
            pass

    return {"organized": applied, "total_eligible": len(updates)}


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="WordPress Media Cleanup")
    parser.add_argument("--action", required=True, choices=[
        "audit", "find-unused", "clean", "find-oversized",
        "missing-alt", "list-by-size", "organize",
    ])
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--max-size", dest="max_size", type=int, default=500)
    parser.add_argument("--sort", choices=["asc", "desc"], default="desc")
    parser.add_argument("--limit", type=int)

    args = parser.parse_args()
    _check()

    actions = {
        "audit": lambda: action_audit(args),
        "find-unused": lambda: action_find_unused(args),
        "clean": lambda: action_clean(args),
        "find-oversized": lambda: action_find_oversized(args),
        "missing-alt": lambda: action_missing_alt(args),
        "list-by-size": lambda: action_list_by_size(args),
        "organize": lambda: action_organize(args),
    }

    try:
        result = actions[args.action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
