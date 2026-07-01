"""Create VMF folders with correct param."""
import requests, json
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
API = 'https://fracktal.in/wp-json/vmfo/v1/folders'

folders = [
    'Fracktal Care', 'Product Photos', 'Team & Office',
    'Blog & Content', 'Banners & Hero', 'Uncategorized'
]

for name in folders:
    r = requests.post(API, auth=auth, json={'name': name}, timeout=15)
    d = r.json()
    fid = d.get('id', 'FAIL')
    print(f'{name} -> id={fid} (HTTP {r.status_code})')
    if r.status_code != 201:
        print(f'  Error: {json.dumps(d, indent=2)[:300]}')

print('\nVerify:')
r = requests.get(API, auth=auth, timeout=15)
for f in r.json():
    fol_name = f.get('name', '?')
    fol_id = f.get('id', '?')
    fol_count = f.get('count', '?')
    print(f'  #{fol_id}: {fol_name} ({fol_count} items)')
