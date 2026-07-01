#!/usr/bin/env python3
"""
WordPress Image Optimizer

Compress images, convert to WebP format, regenerate thumbnails,
and strip EXIF metadata. Works on the WordPress media library.

Usage:
    python wp_image_optimize.py --action compress --quality 85
    python wp_image_optimize.py --action convert-webp --quality 80
    python wp_image_optimize.py --action regenerate-thumbnails
    python wp_image_optimize.py --action optimize-all
"""

import os, sys, json, argparse, base64, io, tempfile
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}"}
API = f"{WP_URL}/wp-json/wp/v2"

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def _check():
    missing = [v for v, k in [("WP_URL", WP_URL), ("WP_USER", WP_USER),
                ("WP_APP_PASSWORD", WP_APP_PASSWORD)] if not k]
    if missing:
        print(json.dumps({"error": True, "message": f"Missing: {', '.join(missing)}"}))
        sys.exit(1)
    if not HAS_PILLOW:
        print(json.dumps({"error": True,
                          "message": "Pillow not installed. Run: pip install Pillow"}))
        sys.exit(1)


def _get_all_media(media_type="image"):
    """Paginate through all media items."""
    params = {"per_page": 100, "page": 1, "media_type": media_type}
    all_data = []
    while True:
        r = requests.get(f"{API}/media", headers=HEADERS, params=params, timeout=60)
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


def _download_image(url):
    """Download an image and return PIL Image object."""
    r = requests.get(url, headers={"User-Agent": "Agent-Website-Manager/1.0"},
                     timeout=30)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)), r.content


def _upload_image(pil_img, filename, alt_text=""):
    """Upload a PIL Image back to WordPress."""
    buf = io.BytesIO()
    # Determine format
    fmt = "JPEG" if filename.lower().endswith((".jpg", ".jpeg")) else "PNG"
    if filename.lower().endswith(".webp"):
        fmt = "WEBP"
    pil_img.save(buf, format=fmt, optimize=True)
    buf.seek(0)

    upload_headers = {**HEADERS, "Content-Disposition": f'attachment; filename="{filename}"'}
    files = {"file": (filename, buf, f"image/{fmt.lower()}")}
    data = {"alt_text": alt_text}

    r = requests.post(f"{API}/media", headers=HEADERS, files=files,
                      data=data, timeout=60)
    r.raise_for_status()
    return r.json()


def action_compress(args):
    """Compress images — resize if too large, optimize quality."""
    media = _get_all_media()
    quality = args.quality or 85
    max_width = args.max_width or 1920
    compressed = []
    skipped = []

    for m in media[:args.limit or len(media)]:
        size_kb = m.get("media_details", {}).get("filesize", 0) / 1024
        # Skip already-small images
        if size_kb < (args.min_size or 50):
            skipped.append({"id": m["id"], "reason": f"Already small ({size_kb:.0f}KB)"})
            continue

        try:
            img, original_bytes = _download_image(m["source_url"])
            original_size = len(original_bytes)

            # Resize if wider than max_width
            if img.width > max_width:
                ratio = max_width / img.width
                new_h = int(img.height * ratio)
                img = img.resize((max_width, new_h), Image.LANCZOS)

            # Re-save with compression
            buf = io.BytesIO()
            fmt = img.format or "JPEG"
            if fmt == "PNG":
                img.save(buf, format="PNG", optimize=True)
            else:
                img = img.convert("RGB")  # Remove alpha for JPEG
                img.save(buf, format="JPEG", quality=quality, optimize=True)

            new_size = buf.tell()
            savings_pct = round((1 - new_size / original_size) * 100, 1)

            # Upload compressed version
            buf.seek(0)
            filename = Path(m["source_url"]).name
            files = {"file": (filename, buf, f"image/{fmt.lower()}")}
            r = requests.post(f"{API}/media", headers=HEADERS, files=files,
                              data={"alt_text": m.get("alt_text", "")}, timeout=60)
            r.raise_for_status()

            compressed.append({
                "id": m["id"], "title": m["title"]["rendered"],
                "original_kb": round(original_size / 1024, 1),
                "new_kb": round(new_size / 1024, 1),
                "saved_pct": savings_pct,
            })

        except Exception as e:
            skipped.append({"id": m["id"], "reason": str(e)[:100]})

    total_saved = sum(c["original_kb"] - c["new_kb"] for c in compressed)
    return {
        "action": "compress",
        "compressed": len(compressed),
        "skipped": len(skipped),
        "total_saved_kb": round(total_saved, 1),
        "items": compressed[:50],
    }


def action_convert_webp(args):
    """Convert JPEG/PNG images to WebP format."""
    media = _get_all_media()
    quality = args.quality or 80
    converted = []
    skipped = []

    for m in media[:args.limit or len(media)]:
        mime = m.get("mime_type", "")
        if "webp" in mime.lower():
            skipped.append({"id": m["id"], "reason": "Already WebP"})
            continue
        if mime not in ("image/jpeg", "image/png"):
            skipped.append({"id": m["id"], "reason": f"Not JPEG/PNG ({mime})"})
            continue

        try:
            img, _ = _download_image(m["source_url"])
            buf = io.BytesIO()
            img = img.convert("RGB")
            img.save(buf, format="WEBP", quality=quality, method=6)
            buf.seek(0)

            name = Path(m["source_url"]).stem + ".webp"
            files = {"file": (name, buf, "image/webp")}
            r = requests.post(f"{API}/media", headers=HEADERS, files=files,
                              data={"alt_text": m.get("alt_text", "")}, timeout=60)
            r.raise_for_status()

            converted.append({
                "original_id": m["id"], "original_title": m["title"]["rendered"],
                "new_id": r.json()["id"], "webp_url": r.json()["source_url"],
            })
        except Exception as e:
            skipped.append({"id": m["id"], "reason": str(e)[:100]})

    return {"action": "convert-webp", "converted": len(converted),
            "skipped": len(skipped), "items": converted[:50]}


def action_regenerate_thumbnails(args):
    """Report which images need thumbnail regeneration.
    Note: Actual regeneration requires WP-CLI or a plugin on the server side.
    This identifies images with missing thumbnail sizes."""
    media = _get_all_media()
    needs_regeneration = []

    for m in media:
        missing = m.get("missing_image_sizes", [])
        if missing:
            needs_regeneration.append({
                "id": m["id"], "title": m["title"]["rendered"],
                "missing_sizes": missing,
            })

    return {
        "action": "regenerate-thumbnails",
        "total_images": len(media),
        "needs_regeneration": len(needs_regeneration),
        "items": needs_regeneration[:100],
        "note": "To actually regenerate, use the WordPress admin or WP-CLI. "
                "This script identifies which images need it.",
        "wp_cli_command": "wp media regenerate --yes",
    }


def action_optimize_all(args):
    """Run all optimizations: compress + convert to WebP + audit."""
    results = {}

    print("Step 1/3: Compressing images...", file=sys.stderr)
    class Args: pass
    comp_args = Args(); comp_args.quality = 85; comp_args.max_width = 1920
    comp_args.min_size = 50; comp_args.limit = args.limit
    results["compress"] = action_compress(comp_args)

    print("Step 2/3: Converting to WebP...", file=sys.stderr)
    webp_args = Args(); webp_args.quality = 80; webp_args.limit = args.limit
    results["convert_webp"] = action_convert_webp(webp_args)

    print("Step 3/3: Checking thumbnails...", file=sys.stderr)
    results["thumbnails"] = action_regenerate_thumbnails(args)

    total_saved = results["compress"].get("total_saved_kb", 0)
    return {
        "action": "optimize-all",
        "total_saved_kb": round(total_saved, 1),
        "converted_to_webp": results["convert_webp"].get("converted", 0),
        "needs_thumbnail_regeneration": results["thumbnails"].get("needs_regeneration", 0),
        "details": results,
    }


def main():
    parser = argparse.ArgumentParser(description="WordPress Image Optimizer")
    parser.add_argument("--action", required=True, choices=[
        "compress", "convert-webp", "regenerate-thumbnails", "optimize-all",
    ])
    parser.add_argument("--quality", type=int, default=85)
    parser.add_argument("--max-width", dest="max_width", type=int, default=1920)
    parser.add_argument("--min-size", dest="min_size", type=int, default=50)
    parser.add_argument("--limit", type=int)

    args = parser.parse_args()
    _check()

    actions = {
        "compress": lambda: action_compress(args),
        "convert-webp": lambda: action_convert_webp(args),
        "regenerate-thumbnails": lambda: action_regenerate_thumbnails(args),
        "optimize-all": lambda: action_optimize_all(args),
    }

    try:
        print(json.dumps(actions[args.action](), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
