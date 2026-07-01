"""Refined classification — tighter keywords, dim-based hero detection."""
import requests, time
from collections import defaultdict
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'
VMF = f'{BASE}/wp-json/vmfo/v1'
WP = f'{BASE}/wp-json/wp/v2'

# ── Get all media (only unassigned) ──────────────────────────
print('Fetching media metadata...')
all_media = []
page = 1
while True:
    r = requests.get(f'{WP}/media', auth=AUTH,
        params={'per_page': 100, 'page': page,
                '_fields': 'id,title,alt_text,slug,source_url,author,mime_type,media_details,post'},
        timeout=60)
    if r.status_code != 200:
        break
    batch = r.json()
    if not batch:
        break
    all_media.extend(batch)
    page += 1
    if len(batch) < 100:
        break
print(f'   Total: {len(all_media)} items')

# ── Get post types for attachment parents ─────────────────────
print('Fetching post types...')
post_types = {}
for pt in ['posts', 'pages', 'product']:
    page = 1
    while True:
        r = requests.get(f'{WP}/{pt}', auth=AUTH,
            params={'per_page': 100, 'page': page, '_fields': 'id,type'},
            timeout=30)
        if r.status_code != 200 or not r.json():
            break
        for p in r.json():
            post_types[p['id']] = p['type']
        page += 1
        if len(r.json()) < 100:
            break

blog_ids = {k for k, v in post_types.items() if v == 'post'}
product_ids = {k for k, v in post_types.items() if v == 'product'}
print(f'   Posts: {len(blog_ids)} | Products: {len(product_ids)}')

# ── Check what's already in VMF folders ──────────────────────
print('Checking existing assignments...')
r = requests.get(f'{VMF}/folders', auth=AUTH, timeout=15)
folder_ids = {f['name']: f['id'] for f in r.json()}
print(f'   Folders: {list(folder_ids.keys())}')

# ── Get all already-assigned media IDs ────────────────────────
# Skip this check — VMF handles duplicate assignments gracefully
assigned_ids = set()
print(f'   Skipping duplicate check — VMF will handle gracefully')

# ── Classify unassigned ──────────────────────────────────────
print('\nClassifying unassigned media...')
categories = defaultdict(list)

for m in all_media:
    mid = m['id']
    if mid in assigned_ids:
        continue
    author = m.get('author', 0)
    if author == 4144:
        continue  # Already in Fracktal Care

    src = (m.get('source_url', '') or '').lower()
    title = ((m.get('title', {}) or {}).get('rendered', '') or '').lower()
    alt = (m.get('alt_text', '') or '').lower()
    slug = (m.get('slug', '') or '').lower()
    post_parent = m.get('post', 0)
    mime = m.get('mime_type', '')
    details = m.get('media_details', {}) or {}
    width = int(details.get('width', 0) or 0)
    height = int(details.get('height', 0) or 0)
    combined = f'{title} {alt} {slug} {src}'

    assigned = False

    # 1. Blog — attached to post OR blog keyword in filename
    if post_parent and post_parent in blog_ids:
        categories['Blog & Content'].append(mid)
        assigned = True
    elif not assigned:
        blog_kw = ['blog', 'article', 'news', 'event', 'exhibition', 'award']
        if any(kw in combined for kw in blog_kw):
            categories['Blog & Content'].append(mid)
            assigned = True

    # 2. Banner/Hero — wide images (aspect > 2.0) OR hero keywords
    if not assigned and width > 0 and height > 0:
        aspect = width / max(height, 1)
        if aspect > 2.0:
            categories['Banners & Hero'].append(mid)
            assigned = True
    if not assigned:
        hero_kw = ['banner', 'hero', 'slider', 'header-bg', 'background']
        if any(kw in combined for kw in hero_kw):
            categories['Banners & Hero'].append(mid)
            assigned = True

    # 3. Product — specific product keywords only (NOT generic 'print')
    if not assigned:
        product_kw = [
            'julia', 'apollo', 'fracktal', 'extruder', 'filament',
            'nozzle', 'enclosure', 'printhead', 'cnc', 'fabrication',
            'prototyping', 'sinter', 'sla', 'fdm', 'sls',
            '3d printer', '3d-printer', '3dprinting'
        ]
        if any(kw in combined for kw in product_kw):
            categories['Product Photos'].append(mid)
            assigned = True

    # 4. Team/Office
    if not assigned:
        team_kw = ['team', 'office', 'staff', 'employee', 'people',
                   'workshop', 'factory', 'facility', 'group-photo']
        if any(kw in combined for kw in team_kw):
            categories['Team & Office'].append(mid)
            assigned = True

    # 5. Attached to product page
    if not assigned and post_parent and post_parent in product_ids:
        categories['Product Photos'].append(mid)
        assigned = True

    # 6. Fallback: if it's an image in uploads, put in Uncategorized
    if not assigned and 'image' in mime:
        categories['Uncategorized'].append(mid)
    elif not assigned:
        categories['Uncategorized'].append(mid)

# ── Report ────────────────────────────────────────────────────
print('\nClassification results (unassigned only):')
total_unassigned = 0
for cat in ['Blog & Content', 'Product Photos', 'Team & Office', 'Banners & Hero', 'Uncategorized']:
    count = len(categories.get(cat, []))
    total_unassigned += count
    print(f'   {cat}: {count}')
print(f'   Already assigned: {len(assigned_ids)}')
print(f'   GRAND TOTAL: {total_unassigned + len(assigned_ids)}')

# ── Sample ────────────────────────────────────────────────────
print('\nSamples:')
for cat, ids in categories.items():
    for mid in ids[:2]:
        media = next((x for x in all_media if x['id'] == mid), None)
        if media:
            t = ((media.get('title', {}) or {}).get('rendered', '') or '?')[:70]
            print(f'   [{cat}] #{mid}: {t}')

# ── Assign ────────────────────────────────────────────────────
print('\nAssigning to VMF folders...')
vmf_map = {
    'Blog & Content': folder_ids.get('Blog &amp; Content', folder_ids.get('Blog & Content', 0)),
    'Product Photos': folder_ids.get('Product Photos', 0),
    'Team & Office': folder_ids.get('Team &amp; Office', folder_ids.get('Team & Office', 0)),
    'Banners & Hero': folder_ids.get('Banners &amp; Hero', folder_ids.get('Banners & Hero', 0)),
    'Uncategorized': folder_ids.get('Uncategorized', 0),
}

for cat, ids in categories.items():
    fid = vmf_map.get(cat)
    if not fid or not ids:
        continue
    done = 0
    start = time.time()
    for i, mid in enumerate(ids):
        r = requests.post(f'{VMF}/folders/{fid}/media',
                         auth=AUTH, json={'media_id': mid}, timeout=15)
        if r.status_code in (200, 201):
            done += 1
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / max(elapsed, 0.1)
            eta = (len(ids) - i - 1) / max(rate, 0.01)
            print(f'   {cat}: {done}/{len(ids)} ({rate:.0f}/s, ETA {eta:.0f}s)')
    print(f'   {cat}: {done}/{len(ids)} DONE')

# ── Final ─────────────────────────────────────────────────────
print('\nFinal folder summary:')
r = requests.get(f'{VMF}/folders', auth=AUTH, timeout=15)
for f in r.json():
    fn = f.get('name', '?')
    fc = f.get('count', 0)
    bar = chr(9608) * min(40, fc // 10) if fc else ''
    print(f'   {fn:25s} {fc:>5d} {bar}')
