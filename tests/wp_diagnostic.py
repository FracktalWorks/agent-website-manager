#!/usr/bin/env python3
"""Comprehensive WordPress site diagnostic script for fracktal.in"""

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

def api_get(endpoint, params=None):
    url = f"{WP_URL}/wp-json/wp/v2/{endpoint}"
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json(), r.headers

def api_get_raw(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json(), r.headers

report = {}

# 1. Site Info
print("=" * 60)
print("1. SITE INFORMATION")
print("=" * 60)
try:
    info, _ = api_get_raw(f"{WP_URL}/wp-json/")
    report["site"] = {
        "name": info.get("name", ""),
        "description": info.get("description", ""),
        "url": info.get("url", ""),
        "namespaces": info.get("namespaces", []),
    }
    print(f"  Site Name: {info.get('name', 'N/A')}")
    print(f"  Description: {info.get('description', 'N/A')}")
    print(f"  Available API namespaces: {len(info.get('namespaces', []))}")
    for ns in info.get("namespaces", []):
        print(f"    - {ns}")
except Exception as e:
    print(f"  ERROR: {e}")

# 2. Settings
print("\n" + "=" * 60)
print("2. SITE SETTINGS")
print("=" * 60)
try:
    settings, _ = api_get("settings")
    report["settings"] = settings
    for k in ["title", "description", "url", "email", "timezone", "date_format", 
              "posts_per_page", "show_on_front", "page_on_front", "page_for_posts"]:
        print(f"  {k}: {settings.get(k, 'N/A')}")
except Exception as e:
    print(f"  ERROR: {e}")

# 3. Plugins
print("\n" + "=" * 60)
print("3. PLUGINS")
print("=" * 60)
try:
    plugins, _ = api_get("plugins")
    report["plugins"] = {"total": len(plugins), "active": 0, "inactive": 0, "items": []}
    for p in sorted(plugins, key=lambda x: (x["status"], x["plugin"])):
        status_icon = "✅" if p["status"] == "active" else "❌"
        print(f"  {status_icon} {p['plugin']:45s} v{p['version']:10s} | {p['status']}")
        report["plugins"]["items"].append({
            "plugin": p["plugin"], "name": p.get("name", ""),
            "version": p["version"], "status": p["status"]
        })
        if p["status"] == "active":
            report["plugins"]["active"] += 1
        else:
            report["plugins"]["inactive"] += 1
    print(f"\n  Total: {len(plugins)} | Active: {report['plugins']['active']} | Inactive: {report['plugins']['inactive']}")
except Exception as e:
    print(f"  ERROR: {e}")

# 4. Themes
print("\n" + "=" * 60)
print("4. THEMES")
print("=" * 60)
try:
    themes, _ = api_get("themes")
    report["themes"] = {"total": len(themes), "items": []}
    for t in sorted(themes, key=lambda x: x.get("status", ""), reverse=True):
        status_icon = "✅ ACTIVE" if t.get("status") == "active" else "   inactive"
        print(f"  {status_icon}  {t['stylesheet']:30s} v{t.get('version', '?')}")
        report["themes"]["items"].append({
            "stylesheet": t["stylesheet"], "name": t.get("name", ""),
            "version": t.get("version", ""), "status": t.get("status", "")
        })
    print(f"\n  Total themes: {len(themes)}")
except Exception as e:
    print(f"  ERROR: {e}")

# 5. Users
print("\n" + "=" * 60)
print("5. USERS")
print("=" * 60)
try:
    users, _ = api_get("users", {"per_page": 50, "roles": "administrator"})
    report["users"] = {"total_admin": len(users), "items": []}
    for u in users:
        print(f"  User: {u['name']} ({u['slug']}) | Roles: {u.get('roles', [])} | ID: {u['id']}")
        report["users"]["items"].append({
            "id": u["id"], "name": u["name"], "slug": u["slug"], "roles": u.get("roles", [])
        })
except Exception as e:
    print(f"  ERROR: {e}")

# 6. Content Stats
print("\n" + "=" * 60)
print("6. CONTENT STATS")
print("=" * 60)
try:
    pages, h = api_get("pages", {"per_page": 1})
    report["pages_total"] = int(h.get("X-WP-Total", 0))
    print(f"  Pages: {report['pages_total']}")
except: report["pages_total"] = "error"

try:
    posts, h = api_get("posts", {"per_page": 1})
    report["posts_total"] = int(h.get("X-WP-Total", 0))
    print(f"  Posts: {report['posts_total']}")
except: report["posts_total"] = "error"

try:
    media, h = api_get("media", {"per_page": 1})
    report["media_total"] = int(h.get("X-WP-Total", 0))
    print(f"  Media items: {report['media_total']}")
except: report["media_total"] = "error"

try:
    comments, h = api_get("comments", {"per_page": 1})
    report["comments_total"] = int(h.get("X-WP-Total", 0))
    print(f"  Comments: {report['comments_total']}")
except: report["comments_total"] = "error"

# 7. WooCommerce check
print("\n" + "=" * 60)
print("7. WooCommerce")
print("=" * 60)
try:
    wc_info, _ = api_get_raw(f"{WP_URL}/wp-json/wc/v3/system_status")
    print("  WooCommerce: ACTIVE")
    env = wc_info.get("environment", {})
    print(f"  WC Version: {env.get('version', 'N/A')}")
    print(f"  WC Database Version: {env.get('database_version', 'N/A')}")
    report["woocommerce"] = {"active": True, "version": env.get("version", "")}
except Exception as e:
    print(f"  WooCommerce: NOT detected or error")
    report["woocommerce"] = {"active": False}

# 8. Security checks (non-intrusive)
print("\n" + "=" * 60)
print("8. QUICK SECURITY CHECKS")
print("=" * 60)
security = {}
try:
    r = requests.get(f"{WP_URL}/xmlrpc.php", timeout=10)
    security["xmlrpc"] = "ENABLED" if "XML-RPC server accepts POST requests only" in r.text else "DISABLED"
    print(f"  XML-RPC: {security['xmlrpc']}")
except: security["xmlrpc"] = "unknown"

try:
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/users", timeout=10)
    security["user_enum"] = "BLOCKED" if r.status_code in [401, 403] else "EXPOSED"
    print(f"  User enumeration via REST: {security['user_enum']}")
except: security["user_enum"] = "unknown"

try:
    r = requests.get(f"{WP_URL}/wp-admin/install.php", timeout=10)
    security["install_accessible"] = "YES" if r.status_code == 200 else "NO (good)"
    print(f"  Install script accessible: {security['install_accessible']}")
except: security["install_accessible"] = "unknown"

report["security"] = security

# 9. Response performance
print("\n" + "=" * 60)
print("9. PERFORMANCE CHECK")
print("=" * 60)
import time
for url, label in [
    (f"{WP_URL}/", "Homepage"),
    (f"{WP_URL}/wp-login.php", "Login"),
    (f"{WP_URL}/wp-json/", "REST API Root"),
]:
    try:
        start = time.time()
        r = requests.get(url, timeout=15)
        elapsed = time.time() - start
        size_kb = len(r.content) / 1024
        print(f"  {label:15s}: {r.status_code} | {size_kb:7.1f} KB | {elapsed:.2f}s")
    except Exception as e:
        print(f"  {label:15s}: ERROR - {str(e)[:60]}")

# Save report
report_path = Path(__file__).parent.parent / "outputs" / "fracktal" / "diagnostic_report.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
with open(report_path, "w") as f:
    json.dump(report, f, indent=2)
print(f"\nFull report saved to: {report_path}")
