#!/usr/bin/env python3
"""
Apply Phase 1 SEO Meta Rewrites
Updates Yoast SEO title and meta description for high-impression,
low-CTR pages.
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WORDPRESS_SITE_URL")
WP_USER = os.getenv("WORDPRESS_USERNAME")
WP_PASS = os.getenv("WORDPRESS_APP_PASSWORD")

if not all([WP_URL, WP_USER, WP_PASS]):
    raise ValueError("Missing WordPress credentials in .env")

API_BASE = f"{WP_URL.rstrip('/')}/wp-json/wp/v2"
auth = HTTPBasicAuth(WP_USER, WP_PASS)


def update_page_meta(page_id: int, title: str, meta_desc: str, slug: str):
    """Update Yoast SEO meta fields for a page."""

    # Update via post meta endpoint
    meta_updates = {
        "_yoast_wpseo_title": title,
        "_yoast_wpseo_metadesc": meta_desc
    }

    url = f"{API_BASE}/pages/{page_id}"

    # WordPress REST API supports meta updates in the main endpoint
    response = requests.post(
        url,
        json={"meta": meta_updates},
        auth=auth,
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    if response.status_code in [200, 201]:
        print(f"✅ Updated /{slug}/")
        print(f"   Title: {title}")
        print(f"   Meta:  {meta_desc[:80]}...")
        return True
    else:
        err = response.text[:200]
        print(f"❌ Failed /{slug}/ - {response.status_code}: {err}")
        return False


def main():
    # Load the rewrites
    rewrite_path = "outputs/seo/phase1_meta_rewrites.json"
    with open(rewrite_path, "r", encoding="utf-8") as f:
        rewrites = json.load(f)

    print(f"Applying Phase 1 meta rewrites to {len(rewrites)} pages...\n")

    success_count = 0
    fail_count = 0

    for page_id, data in rewrites.items():
        success = update_page_meta(
            int(page_id),
            data["new_title"],
            data["new_meta_description"],
            data["slug"]
        )

        if success:
            success_count += 1
        else:
            fail_count += 1

        print()  # Blank line between updates

    print("\n" + "="*60)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed:  {fail_count}")
    print(f"📊 Total:   {len(rewrites)}")

    if success_count > 0:
        print("\n🎯 Next: Monitor CTR changes in Google Search Console")
        print("   over the next 7-14 days")


if __name__ == "__main__":
    main()
