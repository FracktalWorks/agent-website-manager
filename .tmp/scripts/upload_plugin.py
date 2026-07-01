"""
Upload and activate a WordPress plugin zip via admin upload endpoint.
Uses Basic Auth (application password) which works for both REST API and admin.
"""
import requests
import sys
import re
from pathlib import Path
from requests.auth import HTTPBasicAuth

# ── Config ──────────────────────────────────────────────────────
SITE_URL = "https://fracktal.in"
USERNAME = "vjvarada"
APP_PASSWORD = "eBZmsn9ovjOvcvtW14bZPbsx"
ZIP_PATH = Path(__file__).parent.parent.parent / "outputs" / "fracktal" / "fracktal-media-folders.zip"

session = requests.Session()
session.headers.update({"User-Agent": "Agent-Website-Manager/1.0"})

# ── Step 0: Login via wp-login.php to get session cookies ──────
print("[0] Logging into WordPress admin...")
login_resp = session.post(
    f"{SITE_URL}/wp-login.php",
    data={
        "log": USERNAME,
        "pwd": APP_PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": f"{SITE_URL}/wp-admin/",
        "testcookie": "1",
    },
    allow_redirects=False,
)
print(f"  Login status: {login_resp.status_code}")
if login_resp.status_code not in (302, 200):
    print("  ERROR: Login failed")
    sys.exit(1)
# Follow redirects to establish session
if login_resp.status_code == 302:
    redirect_url = login_resp.headers.get("Location", "")
    print(f"  Redirect: {redirect_url}")
    # Check for cookies
    cookies = session.cookies.get_dict()
    print(f"  Cookies: {list(cookies.keys())}")
    # Check if login actually succeeded (not redirected back to login)
    if "wp-login" in redirect_url:
        print("  ERROR: Login redirected back to login page — credentials may be wrong")
        sys.exit(1)

# ── Step 1: Get plugin upload page & extract nonce ─────────────
print("[1] Fetching plugin upload page...")
resp = session.get(f"{SITE_URL}/wp-admin/plugin-install.php?tab=upload")
resp.raise_for_status()

# Extract nonce from the HTML form
match = re.search(r'name="_wpnonce"\s+value="([^"]+)"', resp.text)
if not match:
    print("ERROR: Could not find nonce. Response preview:")
    print(resp.text[:2000])
    sys.exit(1)
nonce = match.group(1)
print(f"  Got nonce: {nonce[:20]}...")

# Also extract wp_http_referer
match2 = re.search(r'name="_wp_http_referer"\s+value="([^"]*)"', resp.text)
wp_http_referer = match2.group(1) if match2 else "/wp-admin/plugin-install.php?tab=upload"

# ── Step 2: Upload the plugin zip ──────────────────────────────
print(f"[2] Uploading plugin from: {ZIP_PATH}")
print(f"  Zip size: {ZIP_PATH.stat().st_size:,} bytes")

with open(ZIP_PATH, "rb") as f:
    files = {
        "pluginzip": ("fracktal-media-folders.zip", f, "application/zip"),
    }
    data = {
        "_wpnonce": nonce,
        "_wp_http_referer": wp_http_referer,
        "install-plugin-submit": "Install Now",
    }
    resp = session.post(
        f"{SITE_URL}/wp-admin/update.php?action=upload-plugin",
        files=files,
        data=data,
    )

print(f"  Status: {resp.status_code}")
print(f"  URL: {resp.url}")

# Check for success
if resp.status_code == 200 and "plugin-install" in resp.url:
    # Look for success message
    if "Plugin installed successfully" in resp.text or "Plugin installed" in resp.text:
        print("  SUCCESS: Plugin uploaded!")
    elif "already installed" in resp.text:
        print("  INFO: Plugin already installed")
    else:
        print("  WARNING: Unexpected response, checking for errors...")
        if "error" in resp.text.lower():
            # Extract error message
            err_match = re.search(r'<div[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</div>', resp.text, re.DOTALL)
            if err_match:
                print(f"  ERROR: {re.sub(r'<[^>]+>', '', err_match.group(1)).strip()}")
            else:
                print("  Could not determine result. Response snippet:")
                print(resp.text[:1000])
else:
    print(f"  Response snippet: {resp.text[:500]}")

# ── Step 3: Activate the plugin via REST API ───────────────────
print("[3] Activating plugin via REST API...")
resp = session.put(
    f"{SITE_URL}/wp-json/wp/v2/plugins/fracktal-media-folders/fracktal-media-folders",
    json={"status": "active"},
)
print(f"  Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    print(f"  Plugin status: {data.get('status', 'unknown')}")
    print("  DONE! Plugin is active.")
elif resp.status_code == 404:
    print("  Plugin not found via REST API. Trying alternative activation...")
    # Try activating via plugins admin page
    resp = session.get(f"{SITE_URL}/wp-admin/plugins.php")
    # Extract activation nonce
    activate_match = re.search(
        r'fracktal-media-folders[^"]*[^>]*>Activate[^<]*</a>',
        resp.text
    )
    if activate_match:
        # Extract URL from the activation link
        link_match = re.search(r'href="([^"]+)"', activate_match.group(0))
        if link_match:
            activate_url = link_match.group(1).replace("&amp;", "&")
            resp = session.get(f"{SITE_URL}{activate_url}")
            print(f"  Activation status: {resp.status_code}")
            if resp.status_code == 200:
                print("  DONE! Plugin should be active.")
            else:
                print(f"  WARNING: Activation response: {resp.status_code}")
        else:
            print("  Could not parse activation link")
    else:
        print("  Could not find activation link on plugins page")
else:
    print(f"  WARNING: {resp.json() if resp.text else 'No response body'}")

print("\n── Done ──")
