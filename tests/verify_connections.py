"""Verify all connections: WordPress REST API, Elementor, Hostinger MCP readiness."""
import requests
from requests.auth import HTTPBasicAuth
import json

WP = 'https://fracktal.in'
auth = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')

print('=' * 60)
print('CONNECTIVITY VERIFICATION')
print('=' * 60)

# 1. WordPress REST API
print('\n--- 1. WordPress REST API ---')
try:
    r = requests.get(f'{WP}/wp-json/wp/v2/pages/2309', auth=auth, timeout=10)
    print(f'  Pages API:     {r.status_code} OK' if r.ok else f'  Pages API:     {r.status_code} FAIL')
    if r.ok:
        page = r.json()
        print(f'  Page title:    {page.get("title",{}).get("rendered","N/A")}')
        print(f'  Elementor:     {"Yes" if "elementor" in page.get("content",{}).get("rendered","") else "No"}')
except Exception as e:
    print(f'  Pages API:     FAIL - {e}')

try:
    r2 = requests.get(f'{WP}/wp-json/wp/v2/settings', auth=auth, timeout=10)
    print(f'  Settings API:  {r2.status_code} OK' if r2.ok else f'  Settings API:  {r2.status_code} FAIL')
except Exception as e:
    print(f'  Settings API:  FAIL - {e}')

try:
    r3 = requests.get(f'{WP}/wp-json/wp/v2/users/me', auth=auth, timeout=10)
    print(f'  Users API:     {r3.status_code} OK - {r3.json().get("name","?")}' if r3.ok else f'  Users API:     {r3.status_code} FAIL')
except Exception as e:
    print(f'  Users API:     FAIL - {e}')

# 2. Elementor endpoints
print('\n--- 2. Elementor ---')
try:
    r4 = requests.get(f'{WP}/wp-json/elementor/v1/globals', auth=auth, timeout=10)
    print(f'  Globals API:   {r4.status_code} OK' if r4.ok else f'  Globals API:   {r4.status_code}')
except Exception as e:
    print(f'  Globals API:   FAIL - {e}')

# 3. Theme
print('\n--- 3. Theme ---')
try:
    r5 = requests.get(f'{WP}/wp-json/wp/v2/themes', auth=auth, timeout=10)
    themes = [t for t in r5.json() if t.get('status') == 'active']
    print(f'  Active theme:  {themes[0]["name"]} ({themes[0]["stylesheet"]})' if themes else '  Unknown')
except Exception as e:
    print(f'  Themes API:    FAIL - {e}')

# 4. Check homepage slides widget data
print('\n--- 4. Homepage Hero Slides (Elementor Widget b245d39) ---')
try:
    r6 = requests.get(f'{WP}/wp-json/wp/v2/pages/2309', auth=auth, timeout=10)
    content = r6.json().get('content', {}).get('rendered', '')
    has_slides = 'elementor-widget-slides' in content
    has_swiper = 'swiper' in content
    print(f'  Slides widget: {"Present" if has_slides else "MISSING"}')
    print(f'  Swiper JS:     {"Present" if has_swiper else "MISSING"}')
except Exception as e:
    print(f'  Page fetch:    FAIL - {e}')

# 5. Check for CSS that might cause width:0
print('\n--- 5. Checking for problematic CSS ---')
try:
    r7 = requests.get(f'{WP}/wp-json/wp/v2/pages?per_page=1&slug=custom-css', auth=auth, timeout=10)
    print(f'  Custom CSS page: {r7.status_code}')
except:
    pass

print('\n' + '=' * 60)
print('VERIFICATION COMPLETE')
print('=' * 60)
