import requests, base64, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
WP_URL = "https://fracktal.in"
AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}

# 1. Check Elementor kits (site settings stored here)
print("=== ELEMENTOR KITS ===")
r = requests.get(f'{WP_URL}/wp-json/elementor/v1/kits', headers=H, timeout=15)
if r.status_code == 200:
    kits = r.json()
    if isinstance(kits, list):
        for k in kits:
            print(f"Kit ID: {k.get('id')} | Title: {k.get('title',{}).get('rendered','?')}")
            # Check meta for favicon settings
            meta = k.get('meta', {})
            for key in meta:
                if 'favicon' in key.lower() or 'icon' in key.lower() or 'logo' in key.lower() or 'identity' in key.lower():
                    print(f"  META {key}: {str(meta[key])[:200]}")
    else:
        print(f"Kits type: {type(kits)}, keys: {list(kits.keys())[:10]}")

# 2. Check Elementor page settings for homepage
print("\n=== HOMEPAGE ELEMENTOR SETTINGS ===")
r2 = requests.get(
    f'{WP_URL}/wp-json/wp/v2/pages/2309',
    headers=H, timeout=15)
page = r2.json()
meta = page.get('meta', {})
for key in meta:
    if 'favicon' in key.lower() or 'icon' in key.lower() or 'elementor' in key.lower():
        val = str(meta[key])[:300]
        print(f"  {key}: {val}")

# 3. Check theme mods for favicon
print("\n=== SITE ICON INFO ===")
r3 = requests.get(f'{WP_URL}/wp-json/wp/v2/settings', headers=H, timeout=15)
settings = r3.json()
site_icon = settings.get('site_icon', 0)
print(f"Site icon ID: {site_icon}")

# Get site icon media
if site_icon:
    r4 = requests.get(f'{WP_URL}/wp-json/wp/v2/media/{site_icon}', headers=H, timeout=15)
    m = r4.json()
    print(f"Site icon URL: {m['source_url']}")
    print(f"Site icon size: {m['media_details']['width']}x{m['media_details']['height']}")

# 4. Check if Elementor has a custom header template
print("\n=== ELEMENTOR TEMPLATES ===")
try:
    r5 = requests.get(
        f'{WP_URL}/wp-json/wp/v2/elementor_library',
        headers=H,
        params={'elementor_library_type': 'header', 'per_page': 10},
        timeout=15)
    if r5.status_code == 200:
        templates = r5.json()
        for t in templates:
            ttype = t.get('meta', {}).get('_elementor_template_type', '?')
            print(f"  Template: {t['title']['rendered']} (type: {ttype})")
except Exception as e:
    print(f"  Error: {e}")

# 5. Search ALL post meta for favicon references
print("\n=== SEARCHING FOR FAVICON REFERENCES ===")
try:
    r6 = requests.get(
        f'{WP_URL}/wp-json/wp/v2/pages',
        headers=H,
        params={'search': 'Favicon-', 'per_page': 5},
        timeout=15)
    if r6.status_code == 200:
        pages = r6.json()
        for p in pages:
            print(f"  Page: {p['title']['rendered']} (ID: {p['id']}, status: {p['status']})")
except Exception as e:
    print(f"  Error: {e}")
