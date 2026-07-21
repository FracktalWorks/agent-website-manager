import requests, re

# Check favicon
r = requests.head('https://fracktal.in/favicon.ico', timeout=15, allow_redirects=True)
print(f'favicon.ico status: {r.status_code}')
print(f'favicon.ico content-type: {r.headers.get("content-type","N/A")}')

# Check homepage
r2 = requests.get('https://fracktal.in', headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
title = re.findall(r'<title>(.*?)</title>', r2.text)
print(f'Homepage <title>: {title}')

meta_desc = re.findall(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', r2.text)
print(f'Meta description: {meta_desc[:1]}')

og_title = re.findall(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', r2.text)
print(f'OG title: {og_title[:1]}')

fav_links = re.findall(r'<link[^>]*?(?:favicon|icon)[^>]*?>', r2.text, re.I)
print(f'Favicon links in HTML: {len(fav_links)}')
for l in fav_links:
    print(f'  {l[:150]}')

# Check for LiteSpeed JS chunk error
has_693 = '693.js' in r2.text
print(f'References litespeed 693.js: {has_693}')

# Check security headers
print(f'\nSecurity headers:')
for h in ['X-Frame-Options','X-Content-Type-Options','Strict-Transport-Security','Referrer-Policy']:
    val = r2.headers.get(h, 'MISSING')
    print(f'  {h}: {val}')

# Check robots.txt
r3 = requests.get('https://fracktal.in/robots.txt', timeout=10)
print(f'\nrobots.txt status: {r3.status_code}')
if r3.status_code == 200:
    print(r3.text[:500])
