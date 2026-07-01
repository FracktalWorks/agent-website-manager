"""Test VMF media assignment and then bulk assign."""
import requests, json
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'
VMF = f'{BASE}/wp-json/vmfo/v1'
WP = f'{BASE}/wp-json/wp/v2'

# ── Step 1: Test single media assignment ──────────────────────
print('1. Testing single media assignment...')
r = requests.get(WP + '/media', auth=AUTH, params={'author': 4144, 'per_page': 3}, timeout=15)
media = r.json()
for m in media:
    title = (m.get('title', {}) or {}).get('rendered', '?')[:60]
    print(f'   ID={m["id"]}: {title}')

if media:
    test_id = media[0]['id']
    FID = 361  # Fracktal Care
    r2 = requests.post(f'{VMF}/folders/{FID}/media', auth=AUTH, json={'media_id': test_id}, timeout=15)
    print(f'\n   Add #{test_id} -> folder #{FID}: HTTP {r2.status_code}')
    if r2.status_code in (200, 201):
        print(f'   Response: {json.dumps(r2.json(), indent=2)[:300]}')
    else:
        print(f'   Error: {r2.text[:300]}')

# ── Step 2: Check folder count ────────────────────────────────
print('\n2. Checking folder count...')
r3 = requests.get(f'{VMF}/folders/{FID}', auth=AUTH, timeout=15)
if r3.status_code == 200:
    f = r3.json()
    fol_name = f.get('name', '?')
    fol_count = f.get('count', '?')
    print(f'   {fol_name}: {fol_count} items')
else:
    print(f'   Error: {r3.text[:200]}')

# ── Step 3: Bulk assign all Kiran images to Fracktal Care ─────
print('\n3. Bulk assigning all 233 Kiran Kumar images to Fracktal Care...')
page = 1
assigned = 0
while True:
    r = requests.get(WP + '/media', auth=AUTH, params={'author': 4144, 'per_page': 100, 'page': page}, timeout=30)
    if r.status_code != 200:
        break
    batch = r.json()
    if not batch:
        break
    for m in batch:
        requests.post(f'{VMF}/folders/{FID}/media', auth=AUTH, json={'media_id': m['id']}, timeout=15)
        assigned += 1
    print(f'   Page {page}: assigned {len(batch)} items (total: {assigned})')
    page += 1

# ── Step 4: Verify ────────────────────────────────────────────
print('\n4. Final verification...')
r = requests.get(f'{VMF}/folders', auth=AUTH, timeout=15)
for f in r.json():
    fol_name = f.get('name', '?')
    fol_id = f.get('id', '?')
    fol_count = f.get('count', '?')
    print(f'   #{fol_id}: {fol_name} ({fol_count} items)')
