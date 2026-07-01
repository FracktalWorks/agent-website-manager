"""Comprehensive product page + SEO + performance audit for fracktal.in"""
import requests, base64, json, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed

AUTH = 'Basic ' + base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': AUTH, 'User-Agent': 'Mozilla/5.0 (compatible; AuditBot/1.0)'}
SITE = 'https://fracktal.in'

# ═══════════════════════════════════════════
# 1. GET ALL PAGES
# ═══════════════════════════════════════════
print("=" * 70)
print("1. PAGE INVENTORY")
print("=" * 70)

r = requests.get(f'{SITE}/wp-json/wp/v2/pages',
                 headers=H,
                 params={'per_page': 100, 'status': 'publish', 'order': 'asc', 'orderby': 'title'},
                 timeout=20)
pages = r.json()
total_pages = int(r.headers.get('X-WP-Total', len(pages)))
print(f"Total published pages: {total_pages}")

# Identify product/landing pages
product_slugs = [
    'snowflake', 'twindragon', 'apollo-sls-landing-page', 'printstick',
    'julia', 'fracktal-care', 'shop', 'product', 'cart', 'checkout',
    'contact-us', 'about-us', 'blog', 'careers'
]
product_pages = []
other_pages = []
for p in pages:
    slug = p['slug']
    is_product = any(ps in slug.lower() for ps in product_slugs)
    (product_pages if is_product else other_pages).append(p)

print(f"Product/landing pages: {len(product_pages)}")
print(f"Other pages: {len(other_pages)}")

# ═══════════════════════════════════════════
# 2. PRODUCT PAGES DEEP AUDIT
# ═══════════════════════════════════════════
print("\n" + "=" * 70)
print("2. PRODUCT PAGE AUDIT (Desktop + Mobile)")
print("=" * 70)

page_report = {}

def audit_page(p):
    pid = p['id']
    slug = p['slug']
    title = p['title']['rendered']
    url = f"{SITE}/{slug}/"
    report = {'id': pid, 'slug': slug, 'title': title, 'url': url}

    # Fetch desktop version
    try:
        r = requests.get(url, headers={**H, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                        timeout=20)
        html = r.text
        size_kb = len(r.content) / 1024
        ttfb = r.elapsed.total_seconds()

        report['desktop'] = {
            'status': r.status_code,
            'size_kb': round(size_kb, 1),
            'ttfb_s': round(ttfb, 2),
        }

        # Meta checks
        title_match = re.search(r'<title>(.*?)</title>', html, re.I)
        report['title_tag'] = title_match.group(1) if title_match else 'MISSING'

        desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)', html, re.I)
        report['meta_description'] = desc_match.group(1)[:120] if desc_match else 'MISSING'
        report['meta_description_length'] = len(desc_match.group(1)) if desc_match else 0

        # H1 check
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.DOTALL)
        report['h1_count'] = len(h1_matches)
        report['h1_text'] = [re.sub(r'<[^>]+>', '', h).strip()[:60] for h in h1_matches]

        # OG tags
        report['og_title'] = bool(re.search(r'og:title', html, re.I))
        report['og_image'] = bool(re.search(r'og:image', html, re.I))

        # Canonical
        can_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', html, re.I)
        report['canonical'] = can_match.group(1) if can_match else 'MISSING'

        # Image count + alt text
        imgs = re.findall(r'<img[^>]*>', html, re.I)
        imgs_no_alt = len([i for i in imgs if 'alt="' not in i.lower() or 'alt=""' in i.lower()])
        report['total_images'] = len(imgs)
        report['images_missing_alt'] = imgs_no_alt

        # Schema check
        report['has_schema'] = 'application/ld+json' in html

        # Word count
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        report['word_count'] = len(text.split())

        # Mobile viewport
        report['has_viewport'] = 'viewport' in html.lower()

    except Exception as e:
        report['desktop'] = {'error': str(e)[:100]}

    # Fetch mobile version
    try:
        r_mob = requests.get(url, headers={**H, 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'},
                            timeout=20)
        html_mob = r_mob.text
        size_mob = len(r_mob.content) / 1024
        ttfb_mob = r_mob.elapsed.total_seconds()

        report['mobile'] = {
            'status': r_mob.status_code,
            'size_kb': round(size_mob, 1),
            'ttfb_s': round(ttfb_mob, 2),
        }

        # Mobile-specific checks
        report['mobile_redirect'] = 'mobile' in r_mob.url.lower() or 'm.' in r_mob.url.lower()
        report['responsive_images'] = 'srcset' in html_mob or 'sizes' in html_mob

    except Exception as e:
        report['mobile'] = {'error': str(e)[:100]}

    return report

# Audit key product pages
key_pages = [p for p in pages if p['slug'] in [
    'snowflake', 'twindragon', 'apollo-sls-landing-page', 'printstick',
    'julia', 'fracktal-care', 'home'
]]

if not key_pages:
    # Fallback: get any pages that look like products
    key_pages = [p for p in product_pages[:7]]

# Also add homepage
homepage = [p for p in pages if p['slug'] == 'home' or p['id'] == 2309]
key_pages = homepage + key_pages

print(f"Auditing {len(key_pages)} key pages...")

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(audit_page, p): p for p in key_pages}
    for future in as_completed(futures):
        result = future.result()
        page_report[result['slug']] = result

# Print results
for slug, report in sorted(page_report.items()):
    d = report.get('desktop', {})
    m = report.get('mobile', {})

    print(f"\n--- {report['title'][:70]} ---")
    print(f"  URL: {report['url']}")
    print(f"  Desktop: {d.get('status','?')} | {d.get('size_kb','?')}KB | TTFB:{d.get('ttfb_s','?')}s")
    print(f"  Mobile:  {m.get('status','?')} | {m.get('size_kb','?')}KB | TTFB:{m.get('ttfb_s','?')}s")
    print(f"  Title: {report['title_tag'][:80]}")
    print(f"  Meta Desc: {report['meta_description'][:100] if report.get('meta_description') else 'MISSING'} ({report.get('meta_description_length',0)} chars)")
    print(f"  H1s: {report['h1_count']} — {report['h1_text']}")
    print(f"  Images: {report['total_images']} ({report['images_missing_alt']} missing alt)")
    print(f"  Word Count: {report['word_count']}")
    print(f"  OG: title={report['og_title']} image={report['og_image']}")
    print(f"  Schema: {report['has_schema']}")
    print(f"  Canonical: {report['canonical']}")

    issues = []
    if report['h1_count'] == 0:
        issues.append("NO H1")
    if report['h1_count'] > 1:
        issues.append(f"MULTIPLE H1s ({report['h1_count']})")
    if report.get('meta_description') == 'MISSING':
        issues.append("NO META DESC")
    if report.get('meta_description_length', 0) < 120:
        issues.append(f"SHORT META DESC ({report['meta_description_length']} chars)")
    if report['images_missing_alt'] > 0:
        issues.append(f"{report['images_missing_alt']} IMAGES MISSING ALT")
    if not report['og_title']:
        issues.append("NO OG TAGS")
    if report['word_count'] < 300 and report['slug'] != 'home':
        issues.append(f"THIN CONTENT ({report['word_count']} words)")
    if d.get('size_kb', 0) > 500:
        issues.append(f"LARGE PAGE ({d['size_kb']}KB)")
    if issues:
        print(f"  ⚠️  ISSUES: {', '.join(issues)}")
    else:
        print(f"  ✅ All checks passed")

# ═══════════════════════════════════════════
# 3. INDIA-SPECIFIC SEO CHECK
# ═══════════════════════════════════════════
print("\n" + "=" * 70)
print("3. INDIA-SPECIFIC SEO ANALYSIS")
print("=" * 70)

# Check for hreflang tags
r_home = requests.get(SITE, headers=H, timeout=15)
home_html = r_home.text
has_hreflang = 'hreflang' in home_html.lower()
print(f"Hreflang tags (regional targeting): {'YES' if has_hreflang else 'MISSING'}")

# Check geo-meta tags
has_geo = 'geo.region' in home_html.lower() or 'geo.position' in home_html.lower()
print(f"Geo meta tags: {'YES' if has_geo else 'MISSING'}")

# Check for India-specific signals
india_signals = {
    'in_domain': '.in' in SITE,
    'india_mentioned': 'india' in home_html.lower() or 'indian' in home_html.lower(),
    'inr_prices': '₹' in home_html or 'INR' in home_html or 'rs.' in home_html.lower(),
    'india_address': any(x in home_html.lower() for x in ['bangalore', 'mumbai', 'delhi', 'bengaluru', 'india']),
}
for signal, present in india_signals.items():
    print(f"  {signal}: {'✅' if present else '❌'}")

# Check Google My Business / Local SEO signals
has_local_biz = any(x in home_html.lower() for x in ['localbusiness', 'local business', 'openinghours'])
print(f"LocalBusiness schema: {'YES' if has_local_biz else 'MISSING'}")

# Check for India-specific keywords in title/meta
title = re.search(r'<title>(.*?)</title>', home_html, re.I)
meta_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)', home_html, re.I)
india_kw = ['india', 'indian', 'bangalore', 'mumbai', 'delhi', 'bengaluru']
title_text = title.group(1) if title else ''
meta_text = meta_desc.group(1) if meta_desc else ''
has_india_in_title = any(kw in title_text.lower() for kw in india_kw)
has_india_in_meta = any(kw in meta_text.lower() for kw in india_kw)
print(f"'India' in title: {'YES' if has_india_in_title else 'MISSING'}")
print(f"'India' in meta desc: {'YES' if has_india_in_meta else 'MISSING'}")

# Check sitemap for India-specific URLs
try:
    r_sitemap = requests.get(f'{SITE}/sitemap_index.xml', timeout=10)
    sitemap_ok = r_sitemap.status_code == 200
except:
    sitemap_ok = False
print(f"Sitemap accessible: {'YES' if sitemap_ok else 'NO'}")

# ═══════════════════════════════════════════
# 4. WORDPRESS PERFORMANCE CHECK
# ═══════════════════════════════════════════
print("\n" + "=" * 70)
print("4. WORDPRESS HEALTH & SLUGGISHNESS CHECK")
print("=" * 70)

# Check plugin count
try:
    r_plugins = requests.get(f'{SITE}/wp-json/wp/v2/plugins', headers=H, timeout=15)
    plugins = r_plugins.json()
    active = sum(1 for p in plugins if p['status'] == 'active')
    inactive = sum(1 for p in plugins if p['status'] == 'inactive')
    print(f"Plugins: {len(plugins)} total, {active} active, {inactive} inactive")
    if inactive > 0:
        print(f"  ⚠️  {inactive} inactive plugins should be deleted")
    if len(plugins) > 20:
        print(f"  ⚠️  High plugin count ({len(plugins)}) — each adds load")
except Exception as e:
    print(f"Plugins check failed: {e}")

# Check for database bloat (revisions via REST)
try:
    r_posts = requests.get(f'{SITE}/wp-json/wp/v2/posts', headers=H,
                          params={'per_page': 1}, timeout=15)
    post_count = int(r_posts.headers.get('X-WP-Total', 0))
    r_pages = requests.get(f'{SITE}/wp-json/wp/v2/pages', headers=H,
                          params={'per_page': 1}, timeout=15)
    page_count = int(r_pages.headers.get('X-WP-Total', 0))
    r_media = requests.get(f'{SITE}/wp-json/wp/v2/media', headers=H,
                          params={'per_page': 1}, timeout=15)
    media_count = int(r_media.headers.get('X-WP-Total', 0))
    print(f"Content: {post_count} posts, {page_count} pages, {media_count} media items")
    if media_count > 500:
        print(f"  ⚠️  Large media library ({media_count} items) — consider cleanup")
except Exception as e:
    print(f"Content count check failed: {e}")

# Check PHP version and limits
try:
    r_php = requests.get(SITE, headers=H, timeout=10)
    php_version = r_php.headers.get('X-Powered-By', 'unknown')
    print(f"PHP: {php_version}")
except:
    pass

# Check for render-blocking resources (quick scan)
try:
    css_count = len(re.findall(r'<link[^>]*stylesheet[^>]*>', home_html, re.I))
    js_count = len(re.findall(r'<script[^>]*src=[^>]*>', home_html, re.I))
    print(f"Render-blocking resources: ~{css_count} CSS files, ~{js_count} JS files")
    if css_count > 3:
        print(f"  ⚠️  {css_count} CSS files — consider combining")
except:
    pass

# ═══════════════════════════════════════════
# 5. CORE WEB VITALS ESTIMATE
# ═══════════════════════════════════════════
print("\n" + "=" * 70)
print("5. CORE WEB VITALS ESTIMATE")
print("=" * 70)

# Quick LCP estimate based on largest image
try:
    start = time.time()
    r_cwv = requests.get(SITE, headers=H, timeout=15)
    ttfb = r_cwv.elapsed.total_seconds()
    total = time.time() - start
    size_kb = len(r_cwv.content) / 1024
    print(f"Homepage: TTFB={ttfb:.2f}s | Total={total:.2f}s | Size={size_kb:.1f}KB")
    lcp_est = ttfb + (total - ttfb) * 0.6
    print(f"Estimated LCP: ~{lcp_est:.1f}s (target <2.5s)")
    print(f"Estimated FCP: ~{ttfb:.1f}s (target <1.8s)")
    if size_kb > 1000:
        print(f"  ⚠️  Homepage >1MB — heavy for mobile users")
except:
    pass

# Save report
report_path = 'outputs/fracktal/product_audit.json'
import os
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump({'page_report': {k: v for k, v in page_report.items()}}, f, indent=2, default=str)
print(f"\nFull report saved to: {report_path}")
