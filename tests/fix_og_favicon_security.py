"""Fix OG tags, favicon, and security on fracktal.in"""
import requests, base64, json, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
WP_URL = "https://fracktal.in"
AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}

results = {}

# ═════════════════════════════════════════════════════════════
# 1. TRY JETPACK OG TAGS
# ═════════════════════════════════════════════════════════════
print("=== JETPACK OG TAGS ===")
try:
    r = requests.get(f'{WP_URL}/wp-json/jetpack/v4/settings', headers=H, timeout=15)
    if r.status_code == 200:
        jp = r.json()
        print(f"  Connected: {jp.get('is_connected')}")
        # Try to enable SEO tools if available
        if not jp.get('seo_tools', True):
            r2 = requests.post(
                f'{WP_URL}/wp-json/jetpack/v4/settings',
                headers=H, json={'seo_tools': True}, timeout=15)
            results['jetpack_seo_enabled'] = r2.status_code == 200
            print(f"  SEO tools enabled: {results['jetpack_seo_enabled']}")
        else:
            results['jetpack_seo'] = 'already_enabled'
            print("  SEO tools already enabled")
    else:
        print(f"  Jetpack API: {r.status_code}")
        results['jetpack_seo'] = f'status_{r.status_code}'
except Exception as e:
    print(f"  Error: {e}")
    results['jetpack_seo'] = str(e)[:100]

# ═════════════════════════════════════════════════════════════
# 2. FIX FAVICON — Force WordPress to regenerate
# ═════════════════════════════════════════════════════════════
print("\n=== FAVICON FIX ===")
# Re-save site icon to trigger favicon regeneration
try:
    r3 = requests.post(
        f'{WP_URL}/wp-json/wp/v2/settings',
        headers=H,
        json={'site_icon': 30153},  # Re-set same icon to trigger regeneration
        timeout=15)
    results['favicon_retriggered'] = r3.status_code == 200
    print(f"  Site icon re-triggered: {results['favicon_retriggered']}")
except Exception as e:
    print(f"  Error: {e}")

# Try to serve favicon via WordPress's built-in handler
try:
    r4 = requests.get(
        f'{WP_URL}/index.php',
        headers=H,
        params={'favicon': '1'},
        timeout=10)
    print(f"  WordPress favicon handler: {r4.status_code}")
except Exception as e:
    print(f"  Handler error: {e}")

# ═════════════════════════════════════════════════════════════
# 3. SECURITY HARDENING
# ═════════════════════════════════════════════════════════════
print("\n=== SECURITY HARDENING ===")

# 3a. Disable XML-RPC pingbacks
try:
    r5 = requests.post(
        f'{WP_URL}/wp-json/wp/v2/settings',
        headers=H,
        json={
            'default_ping_status': 'closed',
            'default_pingback_flag': '',
        },
        timeout=15)
    results['pingbacks_disabled'] = r5.status_code == 200
    print(f"  Pingbacks disabled: {results['pingbacks_disabled']}")
except Exception as e:
    print(f"  Error: {e}")

# 3b. Set site to discourage search engines from indexing wp-admin, etc.
# (WordPress handles this via robots.txt, already OK)

# 3c. Note: Full XML-RPC disable and install.php blocking
# require .htaccess or wp-config.php changes (file system access needed)
results['manual_fixes_needed'] = [
    "Add to .htaccess: <Files xmlrpc.php>deny from all</Files>",
    "Add to .htaccess: <Files install.php>deny from all</Files>",
    "Add security headers to .htaccess:",
    "  Header set X-Frame-Options 'SAMEORIGIN'",
    "  Header set X-Content-Type-Options 'nosniff'",
    "  Header set Referrer-Policy 'strict-origin-when-cross-origin'",
    "  Header set Strict-Transport-Security 'max-age=31536000'",
]

# ═════════════════════════════════════════════════════════════
# 4. VERIFY FIXES
# ═════════════════════════════════════════════════════════════
print("\n=== VERIFICATION ===")
try:
    vr = requests.get(f'{WP_URL}/?v={os.urandom(4).hex()}', timeout=15)
    html = vr.text

    results['meta_desc_present'] = 'meta name="description"' in html
    results['og_tags_present'] = 'og:title' in html
    results['favicon_links'] = html.count('rel="icon"')
    results['favicon_ico_status'] = requests.head(
        f'{WP_URL}/favicon.ico', timeout=10).status_code

    print(f"  Meta description: {results['meta_desc_present']}")
    print(f"  OG tags: {results['og_tags_present']}")
    print(f"  Favicon links: {results['favicon_links']}")
    print(f"  favicon.ico status: {results['favicon_ico_status']}")
except Exception as e:
    print(f"  Verify error: {e}")

# ═════════════════════════════════════════════════════════════
# 5. ADD CUSTOM HTML OG TAGS VIA WORDPRESS HOOK
# ═════════════════════════════════════════════════════════════
# Since we have REST API access, try to add OG via Elementor custom code
print("\n=== CUSTOM OG FIX ===")
homepage_id = 2309
og_html_snippet = (
    '<meta property="og:title" content="Fracktal - 3D Printers and '
    'Additive Manufacturing Solutions">'
    '<meta property="og:description" content="India\'s premier '
    'manufacturer of industrial and desktop 3D printers. Snowflake, '
    'Twin Dragon, Apollo SLS, and PrintStick.">'
    '<meta property="og:image" content="https://fracktal.in/'
    'wp-content/uploads/2025/09/cropped-512x512-Logo.png">'
    '<meta property="og:url" content="https://fracktal.in/">'
    '<meta property="og:type" content="website">'
    '<meta name="twitter:card" content="summary_large_image">'
)

# Store in Elementor page custom code if available
try:
    r7 = requests.post(
        f'{WP_URL}/wp-json/wp/v2/pages/{homepage_id}',
        headers=H,
        json={
            'meta': {
                '_elementor_custom_code_head': og_html_snippet,
            }
        },
        timeout=15)
    results['og_custom_code'] = r7.status_code == 200
    print(f"  OG custom code added: {results['og_custom_code']}")
except Exception as e:
    results['og_custom_code'] = str(e)[:100]
    print(f"  Error: {e}")

# Final output
print(f"\n{'='*50}")
print(json.dumps(results, indent=2))
