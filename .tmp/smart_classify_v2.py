"""Fast smart classify — metadata-based, no content scanning."""
import requests, re
from collections import defaultdict
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'
VMF = f'{BASE}/wp-json/vmfo/v1'
WP = f'{BASE}/wp-json/wp/v2'

# ── Get ALL media with metadata ───────────────────────────────
print('Fetching all media...')
all_media = []
page = 1
while True:
    r = requests.get(f'{WP}/media', auth=AUTH,
        params={'per_page': 100, 'page': page,
                '_fields': 'id,title,alt_text,slug,source_url,author,date,mime_type,post'},
        timeout=60)
    if r.status_code != 200:
        break
    batch = r.json()
    if not batch:
        break
    all_media.extend(batch)
    total = r.headers.get('X-WP-Total', '?')
    print(f'   Page {page}: {len(batch)} / {total}', end='\r')
    page += 1
    if len(batch) < 100:
        break

print(f'\n   Total: {len(all_media)} media items')

# ── Also get all posts (just IDs, slugs, types) ───────────────
print('\nFetching post metadata...')
post_info = {}  # post_id -> {type, slug}
for pt in ['posts', 'pages', 'product']:
    page = 1
    while True:
        r = requests.get(f'{WP}/{pt}', auth=AUTH,
            params={'per_page': 100, 'page': page,
                    '_fields': 'id,slug,type,categories'},
            timeout=30)
        if r.status_code != 200 or not r.json():
            break
        for p in r.json():
            post_info[p['id']] = {'type': p['type'], 'slug': p['slug']}
        page += 1
        if len(r.json()) < 100:
            break

blog_ids = {k for k, v in post_info.items() if v['type'] == 'post'}
product_ids = {k for k, v in post_info.items() if v['type'] == 'product'}
print(f'   Posts: {len(blog_ids)} | Products: {len(product_ids)} | Pages: {len(post_info)-len(blog_ids)-len(product_ids)}')

# ── Classify ──────────────────────────────────────────────────
print('\nClassifying...')
categories = defaultdict(list)
uncategorized = []

for m in all_media:
    mid = m['id']
    src = (m.get('source_url', '') or '').lower()
    title = ((m.get('title', {}) or {}).get('rendered', '') or '').lower()
    alt = (m.get('alt_text', '') or '').lower()
    slug = (m.get('slug', '') or '').lower()
    author = m.get('author', 0)
    post_parent = m.get('post', 0)  # attached to this post
    mime = m.get('mime_type', '')
    combined = f'{title} {alt} {slug} {src}'
    date_str = m.get('date', '')

    # Skip already-assigned (author 4144 = Kiran)
    if author == 4144:
        continue

    assigned = False

    # 1. Attached to blog post
    if post_parent and post_parent in blog_ids:
        categories['Blog & Content'].append(mid)
        assigned = True

    # 2. Product keywords in filename/metadata
    if not assigned:
        product_kw = [
            'printer', 'print', 'julia', 'fracktal', 'machine', '3d',
            'extruder', 'filament', 'nozzle', 'bed', 'enclosure', 'product',
            'manufacturing', 'cnc', 'fabrication', 'prototyping', 'printhead'
        ]
        if any(kw in combined for kw in product_kw):
            categories['Product Photos'].append(mid)
            assigned = True

    # 3. Team/office
    if not assigned:
        team_kw = ['team', 'office', 'staff', 'employee', 'people', 'group photo',
                   'workshop', 'factory', 'facility']
        if any(kw in combined for kw in team_kw):
            categories['Team & Office'].append(mid)
            assigned = True

    # 4. Banner/hero
    if not assigned:
        hero_kw = ['banner', 'hero', 'slider', 'header', 'background', 'cover',
                   'homepage', 'landing']
        if any(kw in combined for kw in hero_kw):
            categories['Banners & Hero'].append(mid)
            assigned = True

    # 5. Blog keywords
    if not assigned:
        blog_kw = ['blog', 'article', 'news', 'event', 'exhibition', 'trade show',
                   'conference', 'award', 'tutorial', 'guide', 'how-to', 'review']
        if any(kw in combined for kw in blog_kw):
            categories['Blog & Content'].append(mid)
            assigned = True

    # 6. If attached to product page
    if not assigned and post_parent and post_parent in product_ids:
        categories['Product Photos'].append(mid)
        assigned = True

    if not assigned:
        uncategorized.append(mid)

# ── Report ────────────────────────────────────────────────────
print('\n--- Classification Results ---')
vmf_folders = {
    'Blog & Content': 364,
    'Product Photos': 362,
    'Team & Office': 363,
    'Banners & Hero': 365,
}

total_classified = 0
for cat, ids in sorted(categories.items()):
    print(f'  {cat}: {len(ids)}')
    total_classified += len(ids)
print(f'  Uncategorized: {len(uncategorized)}')
print(f'  Already in Fracktal Care: 233 (Kiran)')
print(f'  TOTAL: {total_classified + len(uncategorized) + 233}')

# ── Samples ───────────────────────────────────────────────────
print('\n--- Sample matches ---')
for cat, ids in categories.items():
    shown = 0
    for mid in ids[:3]:
        media = next((x for x in all_media if x['id'] == mid), None)
        if media:
            t = ((media.get('title', {}) or {}).get('rendered', '') or '?')[:70]
            print(f'  [{cat}] #{mid}: {t}')
            shown += 1

# ── Assign to VMF ─────────────────────────────────────────────
print('\n--- Assigning to VMF folders ---')
for cat, ids in categories.items():
    fid = vmf_folders.get(cat)
    if not fid:
        continue
    done = 0
    for mid in ids:
        r = requests.post(f'{VMF}/folders/{fid}/media',
                         auth=AUTH, json={'media_id': mid}, timeout=10)
        if r.status_code in (200, 201):
            done += 1
    print(f'  {cat}: {done}/{len(ids)}')

# Move remaining to Uncategorized
fid_uncat = 366
print(f'  Uncategorized: assigning {len(uncategorized)}...')
done = 0
for mid in uncategorized:
    r = requests.post(f'{VMF}/folders/{fid_uncat}/media',
                     auth=AUTH, json={'media_id': mid}, timeout=10)
    if r.status_code in (200, 201):
        done += 1
print(f'  Uncategorized: {done}/{len(uncategorized)}')

# ── Final verification ────────────────────────────────────────
print('\n--- Final folder summary ---')
r = requests.get(f'{VMF}/folders', auth=AUTH, timeout=15)
grand_total = 0
for f in r.json():
    fn = f.get('name', '?')
    fc = f.get('count', 0)
    grand_total += fc
    bar = '█' * min(40, fc // 10)
    print(f'  {fn:20s} {fc:>5d} {bar}')
print(f'  {"─"*20} {"─"*5}')
print(f'  {"TOTAL":20s} {grand_total:>5d}')
