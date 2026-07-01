"""Parallel batch assign — classify all media then assign with threading."""
import requests, time, re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'
VMF = f'{BASE}/wp-json/vmfo/v1'
WP = f'{BASE}/wp-json/wp/v2'
WORKERS = 15  # Parallel API calls

# ── Step 1: Quick classification (no API calls needed) ────────
print('1. Classifying media...')
r = requests.get(f'{WP}/media', auth=AUTH,
    params={'per_page': 1, '_fields': 'id'},
    timeout=15)
total_media = int(r.headers.get('X-WP-Total', 0))
print(f'   Total media: {total_media}')

# Get all media IDs + basic metadata in bulk
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
print(f'   Fetched {len(all_media)} items with metadata')

# Get post types for attachment parents
post_types = {}
for pt in ['posts', 'pages', 'product']:
    page_num = 1
    while True:
        r = requests.get(f'{WP}/{pt}', auth=AUTH,
            params={'per_page': 100, 'page': page_num, '_fields': 'id,type'},
            timeout=30)
        if r.status_code != 200 or not r.json():
            break
        for p in r.json():
            post_types[p['id']] = p['type']
        page_num += 1
        if len(r.json()) < 100:
            break

blog_ids = {k for k, v in post_types.items() if v == 'post'}
product_ids = {k for k, v in post_types.items() if v == 'product'}

# Get VMF folder IDs
r = requests.get(f'{VMF}/folders', auth=AUTH, timeout=15)
folder_map = {}
for f in r.json():
    # Normalize &amp; to &
    name = f['name'].replace('&amp;', '&')
    folder_map[name] = f['id']
print(f'   Folders: {folder_map}')

# Classify
assignments = defaultdict(list)  # folder_id -> [media_ids]
for m in all_media:
    mid = m['id']
    author = m.get('author', 0)
    if author == 4144:
        continue  # Kiran -> Fracktal Care

    src = (m.get('source_url', '') or '').lower()
    title = ((m.get('title', {}) or {}).get('rendered', '') or '').lower()
    alt = (m.get('alt_text', '') or '').lower()
    slug = (m.get('slug', '') or '').lower()
    post_parent = m.get('post', 0)
    combined = f'{title} {alt} {slug} {src}'

    details = m.get('media_details', {}) or {}
    w = int(details.get('width', 0) or 0)
    h = int(details.get('height', 0) or 0)

    assigned = False

    # Blog
    if post_parent in blog_ids:
        assignments[folder_map['Blog & Content']].append(mid)
        assigned = True
    elif any(kw in combined for kw in ['blog', 'article', 'news', 'event', 'exhibition', 'award']):
        assignments[folder_map['Blog & Content']].append(mid)
        assigned = True

    # Banner/Hero — wide images
    if not assigned and w > 0 and h > 0 and (w / max(h, 1)) > 2.0:
        assignments[folder_map['Banners & Hero']].append(mid)
        assigned = True
    elif not assigned and any(kw in combined for kw in ['banner', 'hero', 'slider']):
        assignments[folder_map['Banners & Hero']].append(mid)
        assigned = True

    # Product
    if not assigned:
        product_kw = ['julia', 'apollo', 'fracktal', 'extruder', 'filament',
                      'nozzle', 'enclosure', 'printhead', 'sinter', 'sla', 'fdm', 'sls']
        if any(kw in combined for kw in product_kw):
            assignments[folder_map['Product Photos']].append(mid)
            assigned = True

    # Team
    if not assigned:
        if any(kw in combined for kw in ['team', 'office', 'staff', 'workshop', 'factory']):
            assignments[folder_map['Team & Office']].append(mid)
            assigned = True

    # Product page attachment
    if not assigned and post_parent in product_ids:
        assignments[folder_map['Product Photos']].append(mid)
        assigned = True

    # Default -> Uncategorized
    if not assigned:
        assignments[folder_map['Uncategorized']].append(mid)

# Report
print('\n2. Classification:')
grand = 0
for fid, ids in assignments.items():
    fname = [k for k, v in folder_map.items() if v == fid][0]
    print(f'   {fname}: {len(ids)}')
    grand += len(ids)
print(f'   TOTAL to assign: {grand}')

# ── Step 2: Parallel assignment ───────────────────────────────
print('\n3. Assigning with {WORKERS} parallel workers...')

def assign_one(fid, mid):
    """Assign one media item to a folder. Returns (success, mid)."""
    try:
        r = requests.post(f'{VMF}/folders/{fid}/media',
                         auth=AUTH, json={'media_id': mid}, timeout=30)
        return (r.status_code in (200, 201), mid)
    except Exception:
        return (False, mid)

for fid, ids in assignments.items():
    fname = [k for k, v in folder_map.items() if v == fid][0]
    total = len(ids)
    if total == 0:
        continue
    done = 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(assign_one, fid, mid): mid for mid in ids}
        for future in as_completed(futures):
            success, mid = future.result()
            if success:
                done += 1
            if done % 100 == 0:
                elapsed = time.time() - start
                rate = done / max(elapsed, 0.1)
                eta = (total - done) / max(rate, 0.01)
                print(f'   {fname}: {done}/{total} '
                      f'({rate:.1f}/s, ETA {eta:.0f}s)')
    elapsed = time.time() - start
    print(f'   {fname}: {done}/{total} DONE ({elapsed:.0f}s)')

# ── Step 3: Final verification ───────────────────────────────
print('\n4. Final summary:')
r = requests.get(f'{VMF}/folders', auth=AUTH, timeout=15)
total = 0
for f in r.json():
    fn = f['name']
    fc = f['count']
    total += fc
    bar = chr(9608) * min(50, fc // 5) if fc else ''
    print(f'   {fn:25s} {fc:>5d}  {bar}')
print(f'   {"─"*25} {"─"*5}')
print(f'   {"TOTAL":25s} {total:>5d}  (of 1785)')
