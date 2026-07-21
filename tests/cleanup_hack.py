"""Check users, delete backdoors, and fix the hack."""
import requests
import base64
import re

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}
SITE = 'https://fracktal.in'
API = f'{SITE}/wp-json/wp/v2'

# ═══════════════════════════════════════════════════════════
# 1. LIST ALL USERS
# ═══════════════════════════════════════════════════════════
print("=== USERS ===")
r = requests.get(f'{API}/users?per_page=50', headers=H, timeout=15)
if r.status_code == 200:
    users = r.json()
    for u in users:
        name = u.get('name', '?')
        slug = u.get('slug', '?')
        roles = u.get('roles', [])
        user_id = u.get('id', '?')
        flag = '⚠️ ADMIN' if 'administrator' in roles else ''
        print(f"  [{user_id}] {name} (@{slug}) roles={roles} {flag}")
    print(f"  Total: {len(users)} users")
else:
    print(f"  Error: {r.status_code} - {r.text[:200]}")

# ═══════════════════════════════════════════════════════════
# 2. TRY TO REINSTALL WP CORE
# ═══════════════════════════════════════════════════════════
print("\n=== CORE REINSTALL ===")
# Try the WordPress upgrade API
try:
    r_upgrade = requests.post(
        f'{SITE}/wp-admin/admin-ajax.php',
        headers=H,
        data={
            'action': 'update-core',
            'version': '',  # Will use latest
        },
        timeout=30
    )
    print(f"  Upgrade API: {r_upgrade.status_code}")
    print(f"  Response: {r_upgrade.text[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# Try direct core update endpoint
try:
    # WordPress has a built-in core update mechanism
    r_core = requests.get(
        f'{SITE}/wp-admin/update-core.php',
        headers=H,
        timeout=15
    )
    # Check if there's a reinstall button/form
    has_reinstall = 're-install' in r_core.text.lower()
    print(f"  Core update page: {r_core.status_code}")
    print(f"  Has reinstall option: {has_reinstall}")
except Exception as e:
    print(f"  Error: {e}")

# ═══════════════════════════════════════════════════════════
# 3. TRY TO DELETE BACKDOOR FILES VIA WP FILE EDITOR
# ═══════════════════════════════════════════════════════════
print("\n=== BACKDOOR FILES ===")
backdoors = [
    'wp-content/uploads/2021/10/vwlx9o.php',
    'wp-content/uploads/2024/01/w9glu.php',
    'wp-content/uploads/et-fonts/1a2o0sd.php',
    'wp-content/uploads/wpmc-trash/elementor/pqmnj4l.php',
    'wp-content/uploads/wpforms/cache/index.php',
    'wp-content/wflogs/img/content/img/2023/uploads/ekf/admin.php',
    'wp-content/wphb-logs/assets/docs/archive/tymu/lhki/index.php',
]

for path in backdoors:
    # Check if file is accessible
    r_file = requests.head(f'{SITE}/{path}', timeout=10)
    status = r_file.status_code
    icon = '❌' if status in [200, 403] else '✅'
    print(f"  {icon} {path} -> HTTP {status}")

# Try to delete via WordPress REST API media endpoint (if they're in media)
# Check if any are registered as media items
print("\n  Checking if backdoors are in media library...")
for path in backdoors:
    filename = path.split('/')[-1]
    r_media = requests.get(
        f'{API}/media?search={filename}',
        headers=H, timeout=10)
    if r_media.status_code == 200:
        items = r_media.json()
        if items:
            for item in items:
                print(f"  Found in media: ID={item['id']} -> {item.get('source_url','')}")
