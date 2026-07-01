#!/usr/bin/env python3
"""Fix critical issues on fracktal.in: meta description, OG tags, favicon."""

import os, base64, json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

WP_URL = os.getenv("WORDPRESS_SITE_URL", "https://fracktal.in").rstrip("/")
WP_USER = os.getenv("WORDPRESS_USERNAME", "vjvarada")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "eBZmsn9ovjOvcvtW14bZPbsx")
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
}
API_BASE = f"{WP_URL}/wp-json/wp/v2"

results = {}

# ═══════════════════════════════════════════════════════════════
# 1. FIX META DESCRIPTION
# ═══════════════════════════════════════════════════════════════
# Get homepage page ID from settings
r = requests.get(f"{API_BASE}/settings", headers=HEADERS, timeout=15)
settings = r.json()
homepage_id = settings.get("page_on_front", 2309)
print(f"Homepage ID: {homepage_id}")

# Set site tagline as better description
new_tagline = ("India's Leading 3D Printer Manufacturer | "
               "Snowflake, Twin Dragon, Apollo SLS & PrintStick")
try:
    r2 = requests.post(
        f"{API_BASE}/settings",
        headers=HEADERS,
        json={"description": new_tagline},
        timeout=15)
    results["tagline_updated"] = r2.status_code == 200
    print(f"Tagline updated: {results['tagline_updated']}")
except Exception as e:
    results["tagline_updated"] = str(e)[:100]

# Set page excerpt as meta description on homepage
meta_desc = ("Fracktal Works is India's premier manufacturer of "
             "industrial and desktop 3D printers. Explore our range: "
             "Snowflake high-precision, Twin Dragon dual-extrusion, "
             "Apollo SLS production-grade, and PrintStick adhesion solutions.")
try:
    r3 = requests.post(
        f"{API_BASE}/pages/{homepage_id}",
        headers=HEADERS,
        json={"excerpt": meta_desc},
        timeout=15)
    results["meta_description_set"] = r3.status_code == 200
    print(f"Meta description set: {results['meta_description_set']}")
    if r3.status_code != 200:
        print(f"  Error: {r3.text[:200]}")
except Exception as e:
    results["meta_description_set"] = str(e)[:100]

# Also set Yoast-compatible meta via post meta
try:
    r4 = requests.post(
        f"{API_BASE}/pages/{homepage_id}",
        headers=HEADERS,
        json={
            "meta": {
                "_yoast_wpseo_metadesc": meta_desc,
                "_yoast_wpseo_title": ("Fracktal - 3D Printers & "
                                       "Additive Manufacturing Solutions"),
            }
        },
        timeout=15)
    results["yoast_meta_set"] = r4.status_code == 200
    print(f"Yoast meta set: {results['yoast_meta_set']}")
except Exception as e:
    results["yoast_meta_set"] = str(e)[:100]

# ═══════════════════════════════════════════════════════════════
# 2. FIX FAVICON — Generate favicon.ico + remove duplicates
# ═══════════════════════════════════════════════════════════════
# The WP site icon is set. Check if we can force favicon.ico generation
# by re-saving the site icon setting
site_icon_id = settings.get("site_icon", 30153)
print(f"\nSite icon ID: {site_icon_id}")

# Check Elementor kit for duplicate favicon settings
try:
    kit_r = requests.get(
        f"{WP_URL}/wp-json/elementor/v1/kits",
        headers=HEADERS, timeout=15)
    if kit_r.status_code == 200:
        kits = kit_r.json()
        print(f"Elementor kits: {len(kits) if isinstance(kits, list) else 'not list'}")
except Exception as e:
    print(f"Elementor kit check: {e}")

# Check Elementor global settings for site icon
try:
    global_r = requests.get(
        f"{WP_URL}/wp-json/elementor/v1/globals",
        headers=HEADERS, timeout=15)
    if global_r.status_code == 200:
        data = global_r.json()
        results["elementor_globals"] = "accessible"
        print("Elementor globals accessible")
except Exception as e:
    print(f"Elementor globals error: {e}")

# Remove old favicon media (Favicon-100x100.png, Favicon-300x300.png)
old_favicons = []
try:
    media_r = requests.get(
        f"{API_BASE}/media",
        headers=HEADERS,
        params={"search": "Favicon-100x100", "per_page": 5},
        timeout=15)
    for m in media_r.json():
        if "Favicon-100x100" in m.get("source_url", ""):
            old_favicons.append(m["id"])
except Exception as e:
    print(f"Media search error: {e}")

try:
    media_r2 = requests.get(
        f"{API_BASE}/media",
        headers=HEADERS,
        params={"search": "Favicon-300x300", "per_page": 5},
        timeout=15)
    for m in media_r2.json():
        if "Favicon-300x300" in m.get("source_url", ""):
            old_favicons.append(m["id"])
except Exception as e:
    print(f"Media search error: {e}")

results["old_favicon_media_ids"] = old_favicons
print(f"Old favicon media IDs to clean: {old_favicons}")

# ═══════════════════════════════════════════════════════════════
# 3. SET OPEN GRAPH TAGS
# ═══════════════════════════════════════════════════════════════
# Without a SEO plugin, we set OG-compatible meta via post meta
og_title = "Fracktal - 3D Printers and Additive Manufacturing Solutions"
og_desc = meta_desc
og_image = ("https://fracktal.in/wp-content/uploads/2025/09/"
            "cropped-512x512-Logo.png")

# Store OG data in post meta for Elementor to potentially use
# Also try to set Facebook/OG meta via known meta keys
og_meta = {
    "_yoast_wpseo_opengraph-title": og_title,
    "_yoast_wpseo_opengraph-description": og_desc,
    "_yoast_wpseo_opengraph-image": og_image,
    "_yoast_wpseo_twitter-title": og_title,
    "_yoast_wpseo_twitter-description": og_desc,
    "_yoast_wpseo_twitter-image": og_image,
}
try:
    # Update homepage meta with OG data
    current_page = requests.get(
        f"{API_BASE}/pages/{homepage_id}",
        headers=HEADERS, timeout=15).json()
    existing_meta = current_page.get("meta", {})

    # Merge new OG meta with existing
    merged_meta = {**existing_meta, **og_meta}
    r5 = requests.post(
        f"{API_BASE}/pages/{homepage_id}",
        headers=HEADERS,
        json={"meta": merged_meta},
        timeout=15)
    results["og_tags_set"] = r5.status_code == 200
    print(f"OG tags set: {results['og_tags_set']}")
    if r5.status_code != 200:
        print(f"  Error: {r5.text[:200]}")
except Exception as e:
    results["og_tags_set"] = str(e)[:100]

# ═══════════════════════════════════════════════════════════════
# 4. ADD SCHEMA / structured data basics
# ═══════════════════════════════════════════════════════════════
schema_meta = {
    "_schema_json": json.dumps({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Fracktal Works",
        "url": "https://fracktal.in",
        "description": meta_desc,
        "logo": og_image,
        "sameAs": []
    })
}
try:
    merged_meta2 = {**merged_meta, **schema_meta}
    r6 = requests.post(
        f"{API_BASE}/pages/{homepage_id}",
        headers=HEADERS,
        json={"meta": merged_meta2},
        timeout=15)
    results["schema_set"] = r6.status_code == 200
    print(f"Schema markup set: {results['schema_set']}")
except Exception as e:
    results["schema_set"] = str(e)[:100]

print(f"\n{'='*50}")
print(json.dumps(results, indent=2))
