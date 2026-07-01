"""Deploy agent-file-manager plugin to fracktal.in and edit .htaccess"""
import os, base64, json, zipfile, io
import requests
from pathlib import Path

WP_URL = "https://fracktal.in"
AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}

# ═════════════════════════════════════════════════════════════
# 1. CREATE PLUGIN ZIP IN MEMORY
# ═════════════════════════════════════════════════════════════
plugin_dir = Path(__file__).parent.parent / "agent-data/plugins/agent-file-manager"
plugin_file = plugin_dir / "agent-file-manager.php"

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(plugin_file, "agent-file-manager/agent-file-manager.php")

zip_data = zip_buffer.getvalue()
print(f"Plugin ZIP size: {len(zip_data)} bytes")

# ═════════════════════════════════════════════════════════════
# 2. TRY UPLOADING VIA REST API
# ═════════════════════════════════════════════════════════════
print("\n=== UPLOADING PLUGIN ===")

# Try multipart upload to plugins endpoint
files = {
    'file': ('agent-file-manager.zip', zip_data, 'application/zip')
}
try:
    r = requests.post(
        f'{WP_URL}/wp-json/wp/v2/plugins',
        headers={'Authorization': f'Basic {AUTH}'},
        files=files,
        timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:300]}")
    if r.status_code in [200, 201]:
        print("PLUGIN UPLOADED!")
        # Activate it
        r2 = requests.put(
            f'{WP_URL}/wp-json/wp/v2/plugins/agent-file-manager',
            headers={'Authorization': f'Basic {AUTH}',
                     'Content-Type': 'application/json'},
            json={'status': 'active'},
            timeout=15)
        print(f"Activation: {r2.status_code}")
except Exception as e:
    print(f"Upload failed: {e}")
    # Try alternative: use admin-ajax
    print("\nTrying admin-ajax upload...")
    try:
        # Need to get a nonce first
        # This approach typically doesn't work without browser session
        print("Admin-ajax approach requires browser session. Skipping.")
    except Exception as e2:
        print(f"Admin-ajax also failed: {e2}")

# ═════════════════════════════════════════════════════════════
# 3. ALTERNATIVE: INSTALL WP FILE MANAGER FROM WP.ORG
# ═════════════════════════════════════════════════════════════
print("\n=== PLAN B: Install WP File Manager from WordPress.org ===")
try:
    r3 = requests.post(
        f'{WP_URL}/wp-json/wp/v2/plugins',
        headers={'Authorization': f'Basic {AUTH}',
                 'Content-Type': 'application/json'},
        json={'slug': 'wp-file-manager'},
        timeout=60)
    print(f"Install status: {r3.status_code}")
    if r3.status_code in [200, 201]:
        print("WP File Manager installed!")
        # Activate
        r4 = requests.put(
            f'{WP_URL}/wp-json/wp/v2/plugins/wp-file-manager',
            headers={'Authorization': f'Basic {AUTH}',
                     'Content-Type': 'application/json'},
            json={'status': 'active'},
            timeout=15)
        print(f"Activation: {r4.status_code} — {r4.text[:200]}")
    else:
        print(f"Response: {r3.text[:300]}")
except Exception as e:
    print(f"Install error: {e}")
