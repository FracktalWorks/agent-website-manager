#!/usr/bin/env python3
"""Cleanup: Delete unnecessary inactive plugins from fracktal.in"""

import os, sys, json, base64
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

# Plugins to KEEP (even if inactive) - payment, shipping, SEO, security, analytics
KEEP_INACTIVE = [
    "facebook-for-woocommerce/facebook-for-woocommerce",
    "google-site-kit/google-site-kit",
    "really-simple-ssl/rlrsssl-really-simple-ssl",
    "shiprocket/class-shiprocket-woocommerce-shipping",
    "woo-razorpay/woo-razorpay",
    "woocommerce-gateway-stripe/woocommerce-gateway-stripe",
    "wordpress-seo-premium/wp-seo-premium",
    "wordpress-seo/wp-seo",
    "wpforms-lite/wpforms",
    "litespeed-cache/litespeed-cache",
    "jetpack/jetpack",
]

# Get all plugins
r = requests.get(f"{WP_URL}/wp-json/wp/v2/plugins", headers=HEADERS, timeout=30)
r.raise_for_status()
all_plugins = r.json()

deleted = []
kept = []
failed = []

for plugin in all_plugins:
    plugin_file = plugin["plugin"]
    status = plugin["status"]
    
    if status == "active":
        print(f"  KEEP (active): {plugin_file}")
        kept.append(plugin_file)
        continue
    
    if plugin_file in KEEP_INACTIVE:
        print(f"  KEEP (reserved): {plugin_file}")
        kept.append(plugin_file)
        continue
    
    # Delete this plugin
    plugin_slug = plugin_file.split("/")[0]
    try:
        del_r = requests.delete(
            f"{WP_URL}/wp-json/wp/v2/plugins/{plugin_slug}",
            headers=HEADERS,
            timeout=30
        )
        if del_r.status_code in [200, 202, 204]:
            print(f"  DELETED: {plugin_file}")
            deleted.append(plugin_file)
        else:
            print(f"  FAILED ({del_r.status_code}): {plugin_file} — {del_r.text[:100]}")
            failed.append(plugin_file)
    except Exception as e:
        print(f"  ERROR: {plugin_file} — {e}")
        failed.append(plugin_file)

print(f"\n{'='*50}")
print(f"RESULTS: {len(deleted)} deleted | {len(kept)} kept | {len(failed)} failed")
if deleted:
    print(f"\nDeleted plugins ({len(deleted)}):")
    for d in deleted:
        print(f"  - {d}")
if failed:
    print(f"\nFailed to delete ({len(failed)}):")
    for f in failed:
        print(f"  - {f}")
