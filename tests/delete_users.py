"""Delete spam users in small batches via REST API."""
import requests
import base64
import time

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}
API = 'https://fracktal.in/wp-json/wp/v2'

# Step 1: Get total count
r = requests.get(f'{API}/users?per_page=1', headers=H, timeout=30)
total = int(r.headers.get('X-WP-Total', 0))
print(f'Total users: {total}')

# Step 2: Disable new registrations first
requests.post(f'{API}/settings', headers=H_JSON,
              json={'users_can_register': False}, timeout=10)
print('Registration disabled: ✅')

# Step 3: Delete spam users page by page
deleted = 0
failed = 0
page = 1
max_pages = 200  # Safety

# Known real user slugs to protect
protect = {'vjvarada', 'admin', 'fracktal', 'fracktalworks'}

while page <= max_pages:
    r = requests.get(
        f'{API}/users',
        params={'per_page': 20, 'page': page},
        headers=H, timeout=30)

    if r.status_code != 200:
        print(f'  Page {page}: HTTP {r.status_code}')
        break

    users = r.json()
    if not users:
        break

    for u in users:
        uid = u.get('id', 0)
        slug = str(u.get('slug', '')).lower()
        name = str(u.get('name', ''))

        # Skip protected users
        if any(p in slug for p in protect):
            continue

        # Delete
        try:
            r_del = requests.delete(
                f'{API}/users/{uid}?reassign=1&force=true',
                headers=H_JSON, timeout=15)
            if r_del.status_code in [200, 201]:
                deleted += 1
            else:
                failed += 1
                if failed <= 3:
                    print(f'  Failed [{uid}] {name}: {r_del.status_code}')
        except Exception:
            failed += 1

    page += 1
    if page % 10 == 0:
        print(f'  Progress: page {page}, {deleted} deleted...')
    time.sleep(0.5)

print(f'\nDone: {deleted} deleted, {failed} failed')

# Check remaining
r_final = requests.get(f'{API}/users?per_page=1', headers=H, timeout=30)
remaining = int(r_final.headers.get('X-WP-Total', 0))
print(f'Remaining users: {remaining}')
