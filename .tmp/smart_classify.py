"""Analyze media library — classify images by usage, content, and patterns."""
import requests, json, re
from collections import defaultdict
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'
WP = f'{BASE}/wp-json/wp/v2'
VMF = f'{BASE}/wp-json/vmfo/v1'

# ── Step 1: Get all posts/pages to check image usage ──────────
print('1. Scanning site content for image usage...')
post_types = ['post', 'page', 'product']
content_images = defaultdict(set)  # image_url -> {post_slug, ...}
post_categories = {}  # post_id -> type

for pt in post_types:
    page = 1
    while True:
        r = requests.get(f'{WP}/{pt}s', auth=AUTH,
                        params={'per_page': 100, 'page': page, 'status': 'publish'},
                        timeout=30)
        if r.status_code != 200 or not r.json():
            break
        for p in r.json():
            pid = p['id']
            slug = p.get('slug', '')
            content = (p.get('content', {}) or {}).get('rendered', '')
            post_categories[pid] = {
                'type': pt,
                'slug': slug,
                'title': (p.get('title', {}) or {}).get('rendered', '')
            }
            # Extract image URLs from content
            urls = re.findall(r'https?://fracktal\.in/wp-content/uploads/[^\s"\']+\.(?:jpg|jpeg|png|gif|webp)', content)
            for url in urls:
                # Strip size suffix like -150x150 or -scaled
                base_url = re.sub(r'-\d+x\d+(?=\.(?:jpg|jpeg|png|gif|webp))', '', url)
                base_url = re.sub(r'-scaled(?=\.(?:jpg|jpeg|png|gif|webp))', '', base_url)
                content_images[base_url].add(slug)
        page += 1
        if len(r.json()) < 100:
            break

print(f'   Posts/pages scanned. Found {len(content_images)} unique content images')

# ── Step 2: Categorize posts ──────────────────────────────────
blog_posts = {k: v for k, v in post_categories.items() if v['type'] == 'post'}
product_pages = {k: v for k, v in post_categories.items() if v['type'] == 'product'}
pages = {k: v for k, v in post_categories.items() if v['type'] == 'page'}

print(f'   Blog posts: {len(blog_posts)}')
print(f'   Product pages: {len(product_pages)}')
print(f'   Other pages: {len(pages)}')

# ── Step 3: Get all media with metadata ────────────────────────
print('\n2. Analyzing media library...')
all_media = []
page = 1
while True:
    r = requests.get(f'{WP}/media', auth=AUTH,
                    params={'per_page': 100, 'page': page, '_fields': 'id,title,alt_text,slug,source_url,author,date,mime_type,media_details,post'},
                    timeout=30)
    if r.status_code != 200:
        break
    batch = r.json()
    if not batch:
        break
    all_media.extend(batch)
    page += 1
    total_hdr = r.headers.get('X-WP-Total', '?')
    print(f'   Page {page-1}: {len(batch)} items (total: {total_hdr})', end='\r')
    if len(batch) < 100:
        break

print(f'\n   Total media items: {len(all_media)}')

# ── Step 4: Classify each image ───────────────────────────────
print('\n3. Classifying images...')
categories = defaultdict(list)
uncategorized = []

# Author mapping
author_images = defaultdict(list)
for m in all_media:
    author_images[m.get('author', 0)].append(m['id'])

for m in all_media:
    mid = m['id']
    src_url = m.get('source_url', '')
    title = (m.get('title', {}) or {}).get('rendered', '')
    alt = m.get('alt_text', '')
    slug = m.get('slug', '')
    mime = m.get('mime_type', '')
    post_id = m.get('post')  # attached/uploaded to post
    author_id = m.get('author', 0)

    # Clean source URL for matching
    clean_url = re.sub(r'-\d+x\d+(?=\.(?:jpg|jpeg|png|gif|webp))', '', src_url)
    clean_url = re.sub(r'-scaled(?=\.(?:jpg|jpeg|png|gif|webp))', '', clean_url)

    # Determine category
    assigned = False

    # Rule 1: Used in blog posts
    used_in = content_images.get(clean_url, set()) | content_images.get(src_url, set())
    blog_usage = [s for s in used_in if s in [v['slug'] for v in blog_posts.values()]]
    if blog_usage:
        categories['Blog & Content'].append(mid)
        assigned = True

    # Rule 2: Attached to a blog post
    if not assigned and post_id and post_id in blog_posts:
        categories['Blog & Content'].append(mid)
        assigned = True

    # Rule 3: Product-related keywords in title/alt/slug
    if not assigned:
        combined = f'{title} {alt} {slug} {src_url}'.lower()
        product_keywords = ['printer', 'print', 'julia', 'fracktal', 'machine', 'product',
                          '3d', 'extruder', 'filament', 'nozzle', 'bed', 'enclosure']
        if any(kw in combined for kw in product_keywords):
            categories['Product Photos'].append(mid)
            assigned = True

    # Rule 4: Team/banner/hero keywords
    if not assigned:
        combined = f'{title} {alt} {slug}'.lower()
        if any(kw in combined for kw in ['team', 'office', 'staff', 'employee', 'people']):
            categories['Team & Office'].append(mid)
            assigned = True
        elif any(kw in combined for kw in ['banner', 'hero', 'slider', 'header', 'background']):
            categories['Banners & Hero'].append(mid)
            assigned = True

    # Rule 5: Attached to product pages
    if not assigned and post_id and post_id in product_pages:
        categories['Product Photos'].append(mid)
        assigned = True

    # Rule 6: Kiran Kumar already assigned — skip
    if author_id == 4144:
        continue  # Already in Fracktal Care

    # Unassigned
    if not assigned:
        uncategorized.append(mid)

# ── Step 5: Report ───────────────────────────────────────────
print('\n4. Classification results:')
total_classified = 0
for cat, ids in sorted(categories.items()):
    print(f'   {cat}: {len(ids)} images')
    total_classified += len(ids)
print(f'   Uncategorized: {len(uncategorized)} images')
print(f'   Already in Fracktal Care: 233 (Kiran Kumar)')
print(f'   Total: {total_classified + len(uncategorized) + 233}')

# ── Step 6: Sample of each category ───────────────────────────
print('\n5. Sample images per category:')
for cat, ids in categories.items():
    sample_ids = ids[:3]
    for mid in sample_ids:
        media = next((m for m in all_media if m['id'] == mid), None)
        if media:
            title = (media.get('title', {}) or {}).get('rendered', '?')[:60]
            print(f'   [{cat}] #{mid}: {title}')

# ── Step 7: Assign to VMF folders ─────────────────────────────
vmf_folder_map = {
    'Blog & Content': 364,
    'Product Photos': 362,
    'Team & Office': 363,
    'Banners & Hero': 365,
}
print('\n6. Assigning images to VMF folders...')
for cat, ids in categories.items():
    fid = vmf_folder_map.get(cat)
    if not fid:
        continue
    assigned_count = 0
    for mid in ids:
        r = requests.post(f'{VMF}/folders/{fid}/media',
                         auth=AUTH, json={'media_id': mid}, timeout=10)
        if r.status_code in (200, 201):
            assigned_count += 1
    print(f'   {cat}: assigned {assigned_count}/{len(ids)}')

# Move remaining to Uncategorized
print(f'\n   Uncategorized: assigning {len(uncategorized)} to folder #366...')
count = 0
for mid in uncategorized:
    r = requests.post(f'{VMF}/folders/366/media',
                     auth=AUTH, json={'media_id': mid}, timeout=10)
    if r.status_code in (200, 201):
        count += 1
print(f'   Assigned {count}/{len(uncategorized)}')

# ── Step 8: Final verification ───────────────────────────────
print('\n7. Final folder summary:')
r = requests.get(f'{VMF}/folders', auth=AUTH, timeout=15)
total = 0
for f in r.json():
    fn = f.get('name', '?')
    fc = f.get('count', 0)
    total += fc
    print(f'   {fn}: {fc} items')
print(f'   ─────────────────')
print(f'   TOTAL: {total} items')
