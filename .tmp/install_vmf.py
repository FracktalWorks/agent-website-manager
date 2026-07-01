"""Install Virtual Media Folders via WordPress REST API."""
import requests
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'

# Step 1: Install VMF from WordPress.org
print('Installing Virtual Media Folders...')
r = requests.post(
    f'{BASE}/wp-json/wp/v2/plugins',
    auth=AUTH,
    json={'slug': 'virtual-media-folders', 'status': 'active'},
    timeout=60
)
print(f'Install: HTTP {r.status_code}')
if r.status_code in (200, 201):
    data = r.json()
    print(f"  Name: {data.get('name')}")
    print(f"  Version: {data.get('version')}")
    print(f"  Status: {data.get('status')}")
else:
    print(f'  Error: {r.text[:300]}')

# Step 2: Verify VMF API is live
print('\nVerifying VMF REST API...')
r2 = requests.get(f'{BASE}/wp-json/vmfo/v1/folders', auth=AUTH, timeout=15)
print(f'VMF folders: HTTP {r2.status_code}')
if r2.status_code == 200:
    folders = r2.json()
    print(f'  Folders: {len(folders) if isinstance(folders, list) else "?"}')
else:
    print(f'  Response: {r2.text[:200]}')

# Step 3: Deactivate our custom plugin
print('\nDeactivating Fracktal Media Folders...')
r3 = requests.put(
    f'{BASE}/wp-json/wp/v2/plugins/fracktal-media-folders/fracktal-media-folders',
    auth=AUTH,
    json={'status': 'inactive'},
    timeout=30
)
print(f'Deactivate: HTTP {r3.status_code}')
if r3.status_code == 200:
    print(f'  Status: {r3.json().get("status")}')
else:
    print(f'  Error: {r3.text[:200]}')
