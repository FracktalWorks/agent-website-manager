"""Quick product page SEO + mobile audit"""
import requests, re

SITE = 'https://fracktal.in'
MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
DESKTOP_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

pages = [
    ('snowflake', 'Snowflake'),
    ('twindragon', 'Twin Dragon'),
    ('printstick', 'PrintStick'),
    ('apollo-sls-landing-page', 'Apollo SLS'),
    ('julia', 'Julia'),
    ('fracktal-care', 'Fracktal Care'),
    ('', 'Homepage'),
]

print(f"{'Page':25s} | {'Size':>6s} | {'H1':>3s} | {'Desc':>6s} | {'OG':>3s} | {'Schema':>6s} | {'AltOK':>5s}")
print("-" * 95)

for slug, name in pages:
    url = f"{SITE}/{slug}" if slug else SITE
    try:
        r = requests.get(url, headers={'User-Agent': MOBILE_UA}, timeout=20)
        html = r.text
        size_kb = len(r.content) / 1024

        title = re.search(r'<title>(.*?)</title>', html, re.I)
        desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)', html, re.I)
        h1s = len(re.findall(r'<h1[^>]*>', html, re.I))
        og = bool(re.search(r'og:title', html, re.I))
        schema = 'application/ld+json' in html

        imgs = re.findall(r'<img[^>]*>', html, re.I)
        imgs_no_alt = sum(1 for i in imgs if 'alt="' not in i.lower())
        alt_ok = len(imgs) - imgs_no_alt

        desc_text = desc.group(1)[:40] if desc else 'MISSING'
        desc_len = len(desc.group(1)) if desc else 0

        print(f"{name:25s} | {size_kb:5.0f}KB | {h1s:3d} | {desc_len:4d}c | {'Y' if og else 'N':3s} | {'Y' if schema else 'N':6s} | {alt_ok:3d}/{len(imgs)}")

    except Exception as e:
        print(f"{name:25s} | ERROR: {str(e)[:50]}")
