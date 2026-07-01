"""Check if Virtual Media Folders is installed."""
import requests, json
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in'

# Check VMF API
r = requests.get(f'{BASE}/wp-json/vmfo/v1/folders', auth=AUTH, timeout=15)
print(f'VMF REST API: {r.status_code}')
if r.status_code == 200:
    print('VMF is already installed!')
    data = r.json()
    print(f'Folders: {len(data) if isinstance(data, list) else "?"} ')
    print(json.dumps(data, indent=2)[:400])
else:
    print('VMF not installed yet — need to install it')

# Check active folder-related plugins
r2 = requests.get(f'{BASE}/wp-json/wp/v2/plugins?status=active', auth=AUTH, timeout=15)
if r2.status_code == 200:
    keywords = ['virtual', 'folder', 'fracktal', 'filebird', 'vmf', 'media']
    for p in r2.json():
        name = (p.get('name', '') or p.get('plugin', '')).lower()
        if any(kw in name for kw in keywords):
            ver = p.get('version', '?')
            status = p.get('status', '?')
            print(f'  Active: {p.get("name", p.get("plugin"))} v{ver} [{status}]')

# Check our custom plugin tables
r3 = requests.get(f'{BASE}/wp-json/fracktal/v1/folders', auth=AUTH, timeout=15)
print(f'\nFracktal plugin API: {r3.status_code}')
if r3.status_code == 200:
    folders = r3.json()
    print(f'  Our folders remaining: {len(folders)}')
    for f in folders:
        n = f.get('name', '?')
        fid = f.get('id', '?')
        ic = f.get('item_count', 0)
        print(f'  #{fid}: {n} ({ic} items)')
