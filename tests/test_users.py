"""Quick test: can we query users with small per_page?"""
import requests
import base64

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}

# Test small query
r = requests.get(
    'https://fracktal.in/wp-json/wp/v2/users',
    params={'per_page': 5},
    headers=H, timeout=30)

print(f'Status: {r.status_code}')
print(f'Total users: {r.headers.get("X-WP-Total", "?")}')

if r.status_code == 200:
    users = r.json()
    for u in users:
        print(f'  [{u["id"]}] {u["name"]} roles={u["roles"]}')

# Quick hardening: disable registration
print('\n--- Disabling user registration ---')
r2 = requests.post(
    'https://fracktal.in/wp-json/wp/v2/settings',
    headers=H_JSON,
    json={'users_can_register': False},
    timeout=15)
print(f'Result: {r2.status_code}')

# Verify
r3 = requests.get(
    'https://fracktal.in/wp-json/wp/v2/settings',
    headers=H, timeout=15)
if r3.status_code == 200:
    s = r3.json()
    print(f'Registration open: {s.get("users_can_register", "?")}')
    print(f'Default role: {s.get("default_role", "?")}')
