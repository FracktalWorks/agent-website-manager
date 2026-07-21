"""Fix remaining issues: LiteSpeed cache, security headers, favicon."""
import requests, base64, re, json

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}
API = 'https://fracktal.in/wp-json/wp/v2'

# ═══════════════════════════════════════════════════════════
# 1. LITESPEED CACHE PURGE
# ═══════════════════════════════════════════════════════════
print("=== LITESPEED CACHE PURGE ===")
session = requests.Session()
session.headers.update(H)

# Find the LiteSpeed plugin
r = requests.get(f'{API}/plugins', headers=H, timeout=15)
plugins = r.json() if r.status_code == 200 else []
ls_plugin = None
for p in plugins:
    name = (p.get('name', '') or '').lower()
    if 'litespeed' in name or 'cache' in name:
        ls_plugin = p
        print(f"  Found: {p.get('name')} (status={p.get('status')})")

if ls_plugin:
    # Try to access LiteSpeed admin to get nonce
    try:
        r_ls = session.get(
            'https://fracktal.in/wp-admin/admin.php?page=litespeed',
            timeout=15, allow_redirects=True)
        print(f"  Admin page status: {r_ls.status_code}")
        
        # Extract nonce
        nonce_match = re.search(r'"litespeed_nonce"[^>]*value="([^"]+)"', r_ls.text)
        if nonce_match:
            nonce = nonce_match.group(1)
            print(f"  Got nonce: {nonce[:10]}...")
            
            # Purge all
            r_purge = session.post(
                'https://fracktal.in/wp-admin/admin.php?page=litespeed',
                data={
                    'litespeed_type': 'purge_all',
                    'litespeed_nonce': nonce,
                },
                timeout=15)
            print(f"  Purge result: {r_purge.status_code}")
            
            # Also try emoji/css purge
            for ptype in ['purge_all', 'purge_all_cssjs']:
                r_emoji = session.post(
                    'https://fracktal.in/wp-admin/admin-post.php',
                    data={
                        'action': 'litespeed_purge_all',
                        'litespeed_type': ptype,
                        '_wpnonce': nonce,
                    },
                    timeout=10)
                print(f"  Purge {ptype}: {r_emoji.status_code}")
        else:
            print("  No nonce found in page")
    except Exception as e:
        print(f"  LiteSpeed error: {e}")
else:
    print("  LiteSpeed plugin NOT found in active plugins")
    # Check all plugins for litespeed
    r_all = requests.get(f'{API}/plugins', headers=H, timeout=15)
    if r_all.status_code == 200:
        for p in r_all.json():
            n = (p.get('name', '') or '').lower()
            if 'litespeed' in n or 'cache' in n:
                print(f"  Plugin found (not active?): {p.get('name')} status={p.get('status')}")

# ═══════════════════════════════════════════════════════════
# 2. SECURITY HEADERS
# ═══════════════════════════════════════════════════════════
print("\n=== SECURITY HEADERS ===")
# Try to add headers via WordPress REST API
# Check if we can add mu-plugin or use a code snippet plugin
r_snippets = requests.get(f'{API}/plugins?search=code-snippets', headers=H, timeout=10)
if r_snippets.status_code == 200:
    snips = r_snippets.json()
    for s in snips:
        print(f"  Snippet plugin: {s.get('name')} status={s.get('status')}")

# Try direct .htaccess modification via WordPress
# Check if file editor is available
r_editor = requests.get(
    'https://fracktal.in/wp-admin/theme-editor.php',
    headers=H, timeout=15, allow_redirects=True)
print(f"  Theme editor access: {r_editor.status_code}")

# Check if we can read current .htaccess by requesting it
r_htaccess = requests.get(
    'https://fracktal.in/.htaccess',
    headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
print(f"  .htaccess accessible: {r_htaccess.status_code}")

# ═══════════════════════════════════════════════════════════
# 3. FAVICON FIX
# ═══════════════════════════════════════════════════════════
print("\n=== FAVICON FIX ===")
# Check what icon images exist in media library
r_icon = requests.get(
    f'{API}/media?search=cropped-512x512-Logo&media_type=image',
    headers=H, timeout=10)
if r_icon.status_code == 200:
    icons = r_icon.json()
    for icon in icons:
        src = icon.get('source_url', '')
        if '512' in src or 'logo' in src.lower():
            print(f"  Icon media: {icon.get('id')} -> {src[:100]}")

# Try to force site icon regeneration
r_site_icon = requests.post(
    f'{API}/settings',
    headers=H_JSON,
    json={'site_icon': 30382},
    timeout=10)
print(f"  Site icon re-trigger: {r_site_icon.status_code}")

# Verify current state
r_fav = requests.head('https://fracktal.in/favicon.ico', 
    allow_redirects=True, timeout=10)
print(f"  favicon.ico final status: {r_fav.status_code}")
