import requests
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')
r = requests.get('https://fracktal.in/wp-json/vmfo/v1/folders', auth=auth, timeout=15)
folders = r.json()
total = 0
for f in folders:
    name = f.get('name', '?')
    cnt = f.get('count', 0)
    total += cnt
    bar = chr(9608) * min(40, cnt // 10) if cnt else ''
    print(f'  {name:25s} {cnt:>5d} {bar}')
print(f'  {"─"*25} {"─"*5}')
print(f'  {"TOTAL":25s} {total:>5d}')
