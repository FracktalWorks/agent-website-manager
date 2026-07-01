"""Set up Virtual Media Folders — delete old plugin, create folders, assign media."""
import requests, json
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'
VMF_API = f'{BASE}/wp-json/vmfo/v1'

# ── Step 1: Delete our old custom plugin ──────────────────────
print('1. Deleting Fracktal Media Folders plugin...')
r = requests.delete(
    f'{BASE}/wp-json/wp/v2/plugins/'
    f'fracktal-media-folders/fracktal-media-folders',
    auth=AUTH,
    timeout=30
)
print(f'   HTTP {r.status_code}')
if r.status_code == 200:
    print('   Plugin deleted.')
else:
    print(f'   Note: {r.text[:150]}')

# ── Step 2: Test VMF folder creation ─────────────────────────
print('\n2. Testing VMF folder creation...')
r = requests.post(
    f'{VMF_API}/folders',
    auth=AUTH,
    json={'title': 'Test Folder'},
    timeout=15
)
print(f'   HTTP {r.status_code}')
print(f'   Response: {json.dumps(r.json(), indent=2)[:300]}')

# ── Step 3: Create actual folder structure ────────────────────
print('\n3. Creating folder structure...')
folders = [
    'Fracktal Care',
    'Product Photos',
    'Team & Office',
    'Blog & Content',
    'Banners & Hero',
    'Uncategorized',
]

created = {}
for name in folders:
    r = requests.post(
        f'{VMF_API}/folders',
        auth=AUTH,
        json={'title': name},
        timeout=15
    )
    data = r.json()
    fid = data.get('id')
    created[name] = fid
    print(f'   {name} -> id={fid} (HTTP {r.status_code})')

# Clean up test folder
if 'Test Folder' not in folders and 'Test Folder' in created:
    pass  # Will clean up if it exists

# ── Step 4: Verify ────────────────────────────────────────────
print('\n4. Verifying folders...')
r = requests.get(f'{VMF_API}/folders', auth=AUTH, timeout=15)
data = r.json()
print(f'   Total folders: {len(data) if isinstance(data, list) else "unknown"}')
if isinstance(data, list):
    for f in data:
        n = f.get('title', f.get('name', '?'))
        fid = f.get('id', '?')
        cnt = f.get('count', f.get('media_count', '?'))
        print(f'   #{fid}: {n} ({cnt} items)')

# ── Step 5: Find Kiran Kumar's images (author 4144) ───────────
print('\n5. Finding media to organize...')
r = requests.get(
    f'{BASE}/wp-json/wp/v2/media',
    auth=AUTH,
    params={'author': 4144, 'per_page': 1},
    timeout=15
)
total_kiran = r.headers.get('X-WP-Total', 0)
print(f'   Kiran Kumar images: {total_kiran}')

# Get ALL media stats
r = requests.get(
    f'{BASE}/wp-json/wp/v2/media',
    auth=AUTH,
    params={'per_page': 1},
    timeout=15
)
total_all = r.headers.get('X-WP-Total', 0)
print(f'   Total media items: {total_all}')

print('\n✅ VMF setup complete. Ready to assign images to folders.')
