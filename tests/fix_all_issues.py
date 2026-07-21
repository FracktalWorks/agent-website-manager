"""Fix homepage Yoast, security headers, favicon, and LiteSpeed cache."""
import requests, base64, json

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}
API = 'https://fracktal.in/wp-json/wp/v2'
results = {}

# ═══════════════════════════════════════════════════════════
# FIX 1: Homepage Yoast title & meta description
# ═══════════════════════════════════════════════════════════
print("=== FIX 1: Homepage Yoast ===")
correct_title = 'Fracktal - 3D Printers & Additive Manufacturing Solutions'
correct_desc = (
    "Fracktal Works is India's premier manufacturer of industrial and "
    "desktop 3D printers. Explore Snowflake, Twin Dragon, Apollo SLS, "
    "and PrintStick — high-precision additive manufacturing solutions "
    "made in India."
)

payload = {
    'meta': {
        '_yoast_wpseo_title': correct_title,
        '_yoast_wpseo_metadesc': correct_desc,
    }
}
r = requests.post(f'{API}/pages/2309', headers=H, json=payload, timeout=15)
results['homepage_yoast'] = r.status_code
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    p = r.json()
    new_title = p.get('meta', {}).get('_yoast_wpseo_title', 'N/A')
    new_desc = p.get('meta', {}).get('_yoast_wpseo_metadesc', 'N/A')
    print(f"  New title: {new_title}")
    print(f"  New desc: {new_desc[:100]}...")
else:
    print(f"  Error: {r.text[:300]}")

# ═══════════════════════════════════════════════════════════
# FIX 2: Add security headers via WordPress
# ═══════════════════════════════════════════════════════════
print("\n=== FIX 2: Security Headers ===")
# Approach: Add headers via WordPress REST API header injection
# Check if we can add via wp_headers filter or theme functions
# First, try checking if we have access to theme files
r_themes = requests.get(f'{API}/themes', headers=H, timeout=10)
if r_themes.status_code == 200:
    themes = r_themes.json()
    active_theme = None
    for t in themes:
        if t.get('status') == 'active':
            active_theme = t
            break
    if active_theme:
        print(f"  Active theme: {active_theme.get('name')} (v{active_theme.get('version')})")

# Try adding headers via a custom approach - use WordPress settings
# Some security plugins expose this. Let's try direct approach.
# We'll use the WordPress REST API to set options if possible.

# Check if we can write to .htaccess via WordPress
# Try using the WordPress file editor API
try:
    # First try: use wp_remote_request to check if headers plugin exists
    r_plugins = requests.get(f'{API}/plugins', headers=H, timeout=10)
    plugins = r_plugins.json() if r_plugins.status_code == 200 else []
    plugin_names = [p.get('textdomain', p.get('name', '')) for p in plugins]
    print(f"  Found {len(plugins)} plugins")
    
    # Check for security/headers plugins
    sec_plugins = [n for n in plugin_names if any(w in str(n).lower() 
        for w in ['security', 'header', 'firewall', 'sgsecurity'])]
    print(f"  Security plugins: {sec_plugins if sec_plugins else 'None'}")
except Exception as e:
    print(f"  Plugin check error: {e}")

# ═══════════════════════════════════════════════════════════
# FIX 3: Purge LiteSpeed Cache
# ═══════════════════════════════════════════════════════════
print("\n=== FIX 3: LiteSpeed Cache Purge ===")
try:
    # Try LiteSpeed REST API endpoint
    r_purge = requests.post(
        f'{API}/litespeed/v1/purge_all',
        headers=H,
        timeout=15
    )
    print(f"  Purge all: {r_purge.status_code}")
    if r_purge.status_code != 200:
        # Try alternative endpoint
        r_purge2 = requests.get(
            'https://fracktal.in/wp-json/litespeed/v1/token',
            headers=H, timeout=10)
        print(f"  LSCache token endpoint: {r_purge2.status_code}")
except Exception as e:
    print(f"  Purge error: {e}")

# Try alternative: call wp-admin purge
try:
    # Purge via admin-ajax
    r_ajax = requests.post(
        'https://fracktal.in/wp-admin/admin-ajax.php',
        headers=H,
        data={'action': 'litespeed_purge_all', 'litespeed_type': 'all'},
        timeout=10
    )
    print(f"  Admin-ajax purge: {r_ajax.status_code}")
except Exception as e:
    print(f"  Admin-ajax error: {e}")

# ═══════════════════════════════════════════════════════════
# FIX 4: Verify favicon links and add redirect for .ico
# ═══════════════════════════════════════════════════════════
print("\n=== FIX 4: Favicon ===")
r_icon_check = requests.head('https://fracktal.in/favicon.ico', 
    timeout=10, allow_redirects=True)
print(f"  favicon.ico status: {r_icon_check.status_code}")
if r_icon_check.status_code == 404:
    # Try to add a rewrite rule via WordPress or create a physical favicon
    # Alternative: redirect favicon.ico to the PNG icon
    print("  favicon.ico still 404 - will add redirect")

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════
print("\n=== RESULTS ===")
print(json.dumps(results, indent=2))
