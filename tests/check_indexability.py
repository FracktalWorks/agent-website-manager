"""Check for noindex, verify meta, and prepare GSC submission."""
import requests, base64, re
from urllib.parse import urljoin

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
SITE = 'https://fracktal.in'
API = f'{SITE}/wp-json/wp/v2'

# Check key pages for robots meta / noindex
key_slugs = [
    '',  # homepage
    'carbon-fiber-nylon',
    'abs-acrylonitrile-butadiene-styrene',
    'pet-g-polyethylene-terephthalate-glycol',
    'tpu-thermoplastic-polyurethane',
    'nylon',
    'pva-polyvinyl-alcohol',
    '3d-printing-services',
    'consulting-services',
    'materialdryer',
    'vaccum-casting',
    'snowflake',
    'twindragon',
    '3d-printer-manufacturer-india',
]

print("=== INDEXABILITY CHECK ===")
for slug in key_slugs:
    url = f'{SITE}/{slug}' if slug else SITE
    try:
        r = requests.get(url, headers={'User-Agent': 'Googlebot'},
                        timeout=15, allow_redirects=True)
        html = r.text.lower()
        has_noindex = 'noindex' in html and 'meta name="robots"' in html
        has_canonical = 'canonical' in html
        title_match = re.search(r'<title>(.*?)</title>', r.text, re.I)
        title = title_match.group(1) if title_match else 'NO TITLE'
        status = r.status_code
        final_url = r.url
        
        # Check for noindex specifically
        robots_meta = re.findall(
            r'<meta[^>]*name="robots"[^>]*content="([^"]*)"', r.text, re.I)
        noindex_found = any('noindex' in rm for rm in robots_meta)
        
        icon = '❌ NOINDEX' if noindex_found else '✅'
        print(f"{icon} [{status}] {slug or '/'} -> {title[:80]}")
        if robots_meta:
            print(f"    robots meta: {robots_meta}")
        if final_url != url:
            print(f"    redirected to: {final_url}")
    except Exception as e:
        print(f"❌ ERROR {slug}: {e}")

# Check sitemap
print("\n=== SITEMAP CHECK ===")
r_sm = requests.get(f'{SITE}/sitemap_index.xml', timeout=15)
print(f"sitemap_index.xml: {r_sm.status_code}")
if r_sm.status_code == 200:
    # Count sitemaps
    sm_count = len(re.findall(r'<sitemap>', r_sm.text))
    print(f"  Sub-sitemaps: {sm_count}")
    # Count URLs
    url_count = len(re.findall(r'<url>', r_sm.text))
    print(f"  URLs in index: {url_count}")

# Check for any page sitemaps  
r_page_sm = requests.get(f'{SITE}/page-sitemap.xml', timeout=10)
print(f"page-sitemap.xml: {r_page_sm.status_code}")
if r_page_sm.status_code == 200:
    page_urls = len(re.findall(r'<url>', r_page_sm.text))
    print(f"  Page URLs: {page_urls}")
