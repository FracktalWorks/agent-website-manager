import requests, base64, json
AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}

# Check settings
r = requests.get('https://fracktal.in/wp-json/wp/v2/settings', headers=H, timeout=10)
s = r.json()
front_id = s.get('page_on_front', 0)
show_on = s.get('show_on_front', '')
print(f'Front page ID: {front_id}')
print(f'Show on front: {show_on}')

# Get front page status
if front_id:
    r2 = requests.get(f'https://fracktal.in/wp-json/wp/v2/pages/{front_id}', headers=H, timeout=10)
    p = r2.json()
    print(f'Status: {p.get("status")}')
    print(f'Title: {p.get("title",{}).get("rendered","")}')
    print(f'Password protected: {p.get("password","")}')

# Also check if any security-related plugins have a block list
r3 = requests.get('https://fracktal.in/wp-json/', headers=H, timeout=10)
routes = r3.json().get('routes', {})
sec_routes = [k for k in routes if any(w in k.lower() for w in ['block', 'ban', '403', 'firewall', 'security', 'lockout', 'jetpack-protect'])]
print(f'\nSecurity routes: {sec_routes[:10]}')
