"""Comprehensive speed, SEO, and LLM audit for fracktal.in"""
import requests, re, json, time
from urllib.parse import urljoin

WP_URL = "https://fracktal.in"

results = {}

# ═════════════════════════════════════════════════════════════
# 1. SPEED & PERFORMANCE AUDIT
# ═════════════════════════════════════════════════════════════
print("=" * 60)
print("SPEED & PERFORMANCE AUDIT")
print("=" * 60)

# Fetch homepage and analyze
start = time.time()
r = requests.get(WP_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
ttfb = r.elapsed.total_seconds()
html = r.text
total_time = time.time() - start
total_size_kb = len(r.content) / 1024

results['speed'] = {
    'total_size_kb': round(total_size_kb, 1),
    'ttfb_seconds': round(ttfb, 3),
    'total_load_seconds': round(total_time, 2),
    'http_status': r.status_code,
}

print(f"  Total size: {total_size_kb:.0f} KB")
print(f"  Time to first byte: {ttfb:.3f}s")
print(f"  Total time: {total_time:.2f}s")

# Count resources
css_count = len(re.findall(r'<link[^>]*stylesheet[^>]*>', html, re.I))
js_count = len(re.findall(r'<script[^>]*src=', html, re.I))
img_count = len(re.findall(r'<img[^>]*src=', html, re.I))
inline_css = len(re.findall(r'<style[^>]*>', html, re.I))
inline_js = len(re.findall(r'<script[^>]*>[^<]+</script>', html, re.I))
fonts = len(re.findall(r'googleapis|google-fonts|typekit|fonts\.gstatic', html, re.I))

results['speed']['resources'] = {
    'css_files': css_count, 'js_files': js_count,
    'images': img_count, 'inline_css_blocks': inline_css,
    'inline_js_blocks': inline_js, 'external_fonts': fonts
}

print(f"  Resources: {css_count} CSS, {js_count} JS, {img_count} images, "
      f"{inline_css} inline CSS, {fonts} external fonts")

# Check render-blocking resources
render_blocking = re.findall(
    r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html, re.I)
results['speed']['render_blocking_css'] = len(render_blocking)

# Check for async/defer on scripts
scripts = re.findall(r'<script[^>]*>', html, re.I)
async_scripts = [s for s in scripts if 'async' in s or 'defer' in s]
sync_scripts = [s for s in scripts if 'async' not in s and 'defer' not in s and 'src=' in s]
results['speed']['async_defer_scripts'] = len(async_scripts)
results['speed']['sync_blocking_scripts'] = len(sync_scripts)
print(f"  Render-blocking: {len(render_blocking)} CSS, {len(sync_scripts)} sync JS")

# Check for lazy loading
lazy_images = len(re.findall(r'loading=["\']lazy["\']', html, re.I))
results['speed']['lazy_loaded_images'] = lazy_images
print(f"  Lazy-loaded images: {lazy_images}")

# Check gzip/brotli compression
content_encoding = r.headers.get('Content-Encoding', 'none')
results['speed']['compression'] = content_encoding
print(f"  Compression: {content_encoding}")

# Check cache headers
cache_control = r.headers.get('Cache-Control', 'not set')
results['speed']['cache_control'] = cache_control
print(f"  Cache-Control: {cache_control}")

# Check for oversized images in HTML
large_imgs = re.findall(r'<img[^>]*src="([^"]+)"[^>]*>', html, re.I)
results['speed']['total_img_tags'] = len(large_imgs)

# ═════════════════════════════════════════════════════════════
# 2. SEO DEEP-DIVE
# ═════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SEO DEEP-DIVE")
print("=" * 60)

seo = {}

# H1 tags
h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.DOTALL)
seo['h1_count'] = len(h1s)
seo['h1_texts'] = [re.sub(r'<[^>]+>', '', h).strip()[:100] for h in h1s]
print(f"  H1 tags: {len(h1s)} — {seo['h1_texts']}")

# H2-H6 hierarchy
for level in [2, 3, 4]:
    tags = re.findall(f'<h{level}[^>]*>(.*?)</h{level}>', html, re.I | re.DOTALL)
    seo[f'h{level}_count'] = len(tags)
    print(f"  H{level} tags: {len(tags)}")

# Image alt text
imgs_with_alt = len(re.findall(r'<img[^>]*alt=["\'][^"\']+["\'][^>]*>', html, re.I))
imgs_total = len(re.findall(r'<img[^>]*>', html, re.I))
imgs_without_alt = imgs_total - imgs_with_alt
seo['images_missing_alt'] = imgs_without_alt
seo['images_total'] = imgs_total
print(f"  Images missing alt text: {imgs_without_alt}/{imgs_total}")

# Internal vs external links
all_links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\']', html, re.I)
internal = [l for l in all_links if 'fracktal.in' in l or l.startswith('/') or l.startswith('#')]
external = [l for l in all_links if l.startswith('http') and 'fracktal.in' not in l]
seo['internal_links'] = len(internal)
seo['external_links'] = len(external)
print(f"  Links: {len(internal)} internal, {len(external)} external")

# Check for nofollow/sponsored
nofollow = len(re.findall(r'rel=["\'][^"\']*nofollow', html, re.I))
seo['nofollow_links'] = nofollow

# Check for sitemap reference in robots.txt
try:
    robots = requests.get(f'{WP_URL}/robots.txt', timeout=10).text
    seo['sitemap_in_robots'] = 'Sitemap:' in robots
except:
    seo['sitemap_in_robots'] = 'unknown'
print(f"  Sitemap in robots.txt: {seo['sitemap_in_robots']}")

# SSL check
seo['ssl_active'] = WP_URL.startswith('https')
print(f"  HTTPS: {seo['ssl_active']}")

# WWW redirect check
try:
    www_r = requests.get('https://www.fracktal.in/', timeout=10, allow_redirects=True)
    seo['www_redirects'] = www_r.url
except:
    seo['www_redirects'] = 'failed'
print(f"  www.fracktal.in → {seo['www_redirects']}")

results['seo'] = seo

# ═════════════════════════════════════════════════════════════
# 3. LLM DISCOVERABILITY AUDIT
# ═════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("LLM DISCOVERABILITY AUDIT")
print("=" * 60)

llm = {}

# Structured data (Schema.org)
schema_types = []
jsonld_blocks = re.findall(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    html, re.I | re.DOTALL)
for block in jsonld_blocks:
    try:
        data = json.loads(block)
        if isinstance(data, dict):
            graph = data.get('@graph', [data])
            if not isinstance(graph, list):
                graph = [graph]
            for item in graph:
                stype = item.get('@type', 'Unknown')
                schema_types.append(stype if isinstance(stype, str) else str(stype))
    except:
        pass

llm['schema_types'] = schema_types
print(f"  Schema types: {schema_types}")

# Check for LLMs.txt (emerging standard)
try:
    llms_r = requests.get(f'{WP_URL}/llms.txt', timeout=5)
    llm['llms_txt'] = llms_r.status_code == 200
except:
    llm['llms_txt'] = False
print(f"  llms.txt: {llm['llms_txt']}")

# Check for robots.txt LLM directives
# (Google-Extended, GPTBot, anthropic-ai, etc.)
try:
    has_ai_bots = any(bot in robots.lower() for bot in
                      ['google-extended', 'gptbot', 'claudebot', 'anthropic',
                       'perplexity', 'ccbot'])
    llm['ai_bot_directives'] = has_ai_bots
    # Check specific bots
    for bot in ['Google-Extended', 'GPTBot', 'CCBot', 'anthropic-ai']:
        if bot.lower() in robots.lower():
            print(f"  Bot directive found: {bot}")
except:
    llm['ai_bot_directives'] = 'unknown'
print(f"  AI bot directives in robots.txt: {llm['ai_bot_directives']}")

# Content quality for LLMs
# - Word count
text_content = re.sub(r'<[^>]+>', ' ', html)
text_content = re.sub(r'\s+', ' ', text_content).strip()
word_count = len(text_content.split())
llm['word_count'] = word_count
print(f"  Homepage word count: {word_count}")

# - Meta description quality
meta_desc_match = re.search(
    r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)',
    html, re.I)
desc = meta_desc_match.group(1) if meta_desc_match else ''
llm['meta_description_length'] = len(desc)
llm['meta_description'] = desc[:200]
print(f"  Meta description length: {len(desc)} chars")

# - Check for FAQ/HowTo schema (LLMs love these)
has_faq = 'FAQPage' in str(schema_types) or 'faq' in html.lower()
has_howto = 'HowTo' in str(schema_types)
llm['has_faq_schema'] = has_faq
llm['has_howto_schema'] = has_howto
print(f"  FAQ Schema: {has_faq}, HowTo Schema: {has_howto}")

# - Content freshness
last_modified = r.headers.get('Last-Modified', 'unknown')
llm['last_modified_header'] = last_modified

# Check for modified date in meta
date_modified = re.search(
    r'<meta[^>]*property=["\']article:modified_time["\'][^>]*content=["\']([^"\']+)',
    html, re.I)
llm['article_modified_time'] = date_modified.group(1) if date_modified else 'missing'
print(f"  Article modified time: {llm['article_modified_time']}")

# Check for clear page title / purpose
title_match = re.search(r'<title>(.*?)</title>', html, re.I)
llm['title'] = title_match.group(1) if title_match else 'missing'
llm['title_length'] = len(llm['title']) if isinstance(llm['title'], str) else 0
print(f"  Title: {llm['title']}")
print(f"  Title length: {llm['title_length']} chars")

results['llm'] = llm

# ═════════════════════════════════════════════════════════════
# 4. MISSING OPPORTUNITIES
# ═════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MISSING OPPORTUNITIES")
print("=" * 60)

missing = []

# Check image WebP usage
webp_imgs = len(re.findall(r'\.webp["\'?]', html, re.I))
png_imgs = len(re.findall(r'\.png["\'?]', html, re.I))
jpg_imgs = len(re.findall(r'\.(jpg|jpeg)["\'?]', html, re.I))
print(f"  Image formats: {webp_imgs} WebP, {png_imgs} PNG, {jpg_imgs} JPG")
results['speed']['webp_usage'] = webp_imgs
results['speed']['png_usage'] = png_imgs
results['speed']['jpg_usage'] = jpg_imgs

if png_imgs > 5:
    missing.append(f"Convert {png_imgs} PNG images to WebP for ~30% size reduction")

# Check for preconnect/preload
preconnects = len(re.findall(r'rel=["\']preconnect["\']', html, re.I))
preloads = len(re.findall(r'rel=["\']preload["\']', html, re.I))
print(f"  Preconnects: {preconnects}, Preloads: {preloads}")
results['speed']['preconnects'] = preconnects
results['speed']['preloads'] = preloads

# Check font-display
font_display = re.findall(r'font-display:\s*(\w+)', html, re.I)
print(f"  Font-display settings: {font_display}")

# Check for critical CSS inlining
has_critical_css = 'critical' in html.lower() and 'css' in html.lower()
print(f"  Critical CSS inlining: {has_critical_css}")

# Check for unused CSS/JS (LiteSpeed Cache should handle)
lscache_active = 'litespeed' in html.lower() or 'lscache' in html.lower()
print(f"  LiteSpeed Cache active on page: {lscache_active}")

results['opportunities'] = missing

# ═════════════════════════════════════════════════════════════
# 5. CORE WEB VITALS ESTIMATION
# ═════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CORE WEB VITALS ESTIMATES")
print("=" * 60)

# Estimate LCP (Largest Contentful Paint) based on TTFB + resource loading
# Rough heuristic: TTFB + time to load largest image
lcp_estimate = ttfb + (total_time - ttfb) * 0.7  # 70% of remaining time
print(f"  Estimated LCP: ~{lcp_estimate:.1f}s (should be <2.5s)")

# Count total DOM elements (rough)
dom_elements = len(re.findall(r'<\w+[>\s]', html, re.I))
print(f"  Estimated DOM elements: ~{dom_elements}")
results['speed']['dom_elements'] = dom_elements

# CLS risk factors
has_dimensionless_images = len(re.findall(
    r'<img(?!.*width)(?!.*height)[^>]*>', html, re.I))
print(f"  Images without dimensions (CLS risk): {has_dimensionless_images}")

# Save full report
with open('outputs/fracktal/performance_audit.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nFull report saved.")
