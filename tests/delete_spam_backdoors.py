"""Delete spam users and check backdoor files in media library."""
import requests
import base64

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}
API = 'https://fracktal.in/wp-json/wp/v2'

# ═══════════════════════════════════════════════════════════
# 1. DELETE SPAM USERS
# ═══════════════════════════════════════════════════════════
print("=== DELETING SPAM USERS ===")
# Get users with no roles (subscribers/spam)
r = requests.get(f'{API}/users?per_page=100', headers=H, timeout=15)
users = r.json() if r.status_code == 200 else []
print(f"Total users returned: {len(users)}")

# Identify real vs spam users
real_users = []
spam_users = []
for u in users:
    roles = u.get('roles', [])
    name = u.get('name', '')
    slug = u.get('slug', '')
    uid = u.get('id', 0)
    
    # Real users have roles or recognizable names
    if 'administrator' in roles or 'editor' in roles or 'author' in roles:
        real_users.append(u)
        print(f"  KEEP [{uid}] {name} roles={roles}")
    elif 'vjvarada' in slug.lower() or 'fracktal' in slug.lower() or 'admin' in slug.lower():
        real_users.append(u)
        print(f"  KEEP [{uid}] {name} (@{slug}) roles={roles}")
    elif name and not name[0].isdigit() and len(name) > 3 and ' ' in name:
        # Might be a real person
        real_users.append(u)
        print(f"  REVIEW [{uid}] {name} (@{slug}) roles={roles}")
    else:
        spam_users.append(u)

print(f"\nReal/Review users: {len(real_users)}")
print(f"Spam users to delete: {len(spam_users)}")

# Delete spam users (reassign content to user 1)
deleted = 0
for u in spam_users[:20]:  # Limit to 20 per run for safety
    uid = u.get('id')
    name = u.get('name', '?')
    try:
        r_del = requests.delete(
            f'{API}/users/{uid}?reassign=1&force=true',
            headers=H_JSON,
            timeout=10)
        if r_del.status_code in [200, 201]:
            print(f"  ✅ Deleted [{uid}] {name}")
            deleted += 1
        else:
            print(f"  ❌ Failed [{uid}] {name}: {r_del.status_code} {r_del.text[:100]}")
    except Exception as e:
        print(f"  ❌ Error [{uid}] {name}: {e}")

print(f"\nDeleted: {deleted}/{len(spam_users)}")

# ═══════════════════════════════════════════════════════════
# 2. CHECK BACKDOORS IN MEDIA LIBRARY
# ═══════════════════════════════════════════════════════════
print("\n=== CHECKING BACKDOORS IN MEDIA ===")
backdoor_names = [
    'vwlx9o.php', 'w9glu.php', '1a2o0sd.php', 
    'pqmnj4l.php', 'admin.php', 'index.php'
]
for name in backdoor_names:
    r = requests.get(f'{API}/media?search={name}', headers=H, timeout=10)
    if r.status_code == 200:
        items = r.json()
        if items:
            for item in items:
                mid = item['id']
                src = item.get('source_url', '')
                print(f"  FOUND in media: ID={mid} -> {src}")
                # Try to delete it
                r_del = requests.delete(
                    f'{API}/media/{mid}?force=true',
                    headers=H_JSON, timeout=10)
                print(f"    Delete: {r_del.status_code}")
        else:
            print(f"  Not in media: {name}")

# ═══════════════════════════════════════════════════════════
# 3. VERIFY CLOAKING IS STILL GONE
# ═══════════════════════════════════════════════════════════
print("\n=== VERIFY CLOAKING ===")
import re
for ua_name, ua_str in [
    ('Googlebot', 'Googlebot/2.1'),
    ('Bingbot', 'bingbot/2.0'),
    ('Normal', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
]:
    r = requests.get('https://fracktal.in',
                     headers={'User-Agent': ua_str}, timeout=15)
    title = re.findall(r'<title>(.*?)</title>', r.text)
    has_jp = bool(re.search(r'[\u3040-\u309f\u30a0-\u30ff]', r.text))
    status = '❌ JAPANESE SPAM' if has_jp else '✅ CLEAN'
    print(f"  {ua_name}: {status} | title={title[0][:70] if title else 'NONE'}")
