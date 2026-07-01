import requests, json
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')

# Test 1: Check if plugin routes exist
r = requests.get('https://fracktal.in/wp-json/fracktal/v1/folders', auth=auth)
print(f'Folders API: {r.status_code}')

# Test 2: Create a test folder
r2 = requests.post('https://fracktal.in/wp-json/fracktal/v1/folders',
    auth=auth, json={'name': 'Test Folder', 'parent': 0})
print(f'Create folder: {r2.status_code} - {r2.json()}')

# Test 3: List with item_count
r3 = requests.get('https://fracktal.in/wp-json/fracktal/v1/folders?flat=1', auth=auth)
print(f'Flat list: {r3.status_code}')
data = r3.json()
for f in data:
    ic = f.get('item_count', '?')
    name = f.get('name', '?')
    fid = f.get('id', '?')
    print(f'  Folder #{fid}: {name} (items: {ic})')

# Cleanup test folder
if data:
    fid = data[0].get('id')
    r4 = requests.delete(f'https://fracktal.in/wp-json/fracktal/v1/folders/{fid}', auth=auth)
    print(f'Delete folder: {r4.status_code} - {r4.json()}')
