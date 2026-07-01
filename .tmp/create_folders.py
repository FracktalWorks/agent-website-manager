"""Create the folder structure for Fracktal media library."""
import requests, time
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
BASE = 'https://fracktal.in/wp-json/fracktal/v1/folders'

# 1. Delete all existing folders
r = requests.get(BASE + '?flat=1', auth=AUTH, timeout=30)
existing = r.json()
for f in existing:
    fid = f['id']
    rd = requests.delete(f'{BASE}/{fid}', auth=AUTH, timeout=30)
    print(f'Deleted folder #{fid}: {f["name"]} ({rd.status_code})')

# 2. Create folder structure
folders = [
    'Fracktal Care',
    'Product Photos',
    'Team & Office',
    'Blog & Content',
    'Banners & Hero',
    'Uncategorized',
]

created = []
for name in folders:
    r = requests.post(BASE, auth=AUTH, json={'name': name, 'parent': 0}, timeout=30)
    data = r.json()
    created.append(data)
    print(f'Created: {name} -> id={data["id"]} ({r.status_code})')

# 3. Verify final state
r = requests.get(BASE + '?flat=1', auth=AUTH, timeout=30)
final = r.json()
print(f'\nFinal folder count: {len(final)}')
for f in final:
    print(f'  #{f["id"]}: {f["name"]} ({f.get("item_count", 0)} items)')
