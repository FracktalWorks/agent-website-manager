"""Final verification of all fixes."""
import requests
import re

SITE = 'https://fracktal.in'

print("=== SECURITY HEADERS ===")
r = requests.get(SITE, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
for h in ['X-Frame-Options', 'X-Content-Type-Options',
           'Strict-Transport-Security', 'Referrer-Policy']:
    val = r.headers.get(h, 'MISSING')
    icon = '✅' if val != 'MISSING' else '❌'
    print(f"  {icon} {h}: {val}")

print("\n=== CLOAKING CHECK (Googlebot) ===")
r2 = requests.get(SITE, headers={'User-Agent': 'Googlebot/2.1'}, timeout=20)
title = re.findall(r'<title>(.*?)</title>', r2.text)
has_jp = bool(re.search(r'[\u3040-\u309f\u30a0-\u30ff]', r2.text))
print(f"  Title: {title[0][:80] if title else 'NONE'}")
print(f"  Japanese spam: {has_jp}")

print("\n=== SITEMAP ===")
r3 = requests.get(f'{SITE}/sitemap_index.xml', timeout=15)
print(f"  Status: {r3.status_code}")
if r3.status_code == 200:
    sm_count = len(re.findall(r'<sitemap>', r3.text))
    url_count = len(re.findall(r'<url>', r3.text))
    print(f"  Sub-sitemaps: {sm_count}, URLs: {url_count}")

print("\n✅ VERIFICATION COMPLETE")
