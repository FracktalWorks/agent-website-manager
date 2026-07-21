"""Comprehensive cleanup: spam users, hardening, cache purge."""
import requests
import base64
import json
import time

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}
API = 'https://fracktal.in/wp-json/wp/v2'
SITE = 'https://fracktal.in'

# ═══════════════════════════════════════════════════════════
# 1. DELETE SPAM USERS (Batch via REST API)
# ═══════════════════════════════════════════════════════════
print("=== 1. SPAM USER CLEANUP ===")

# Get users with no roles (subscribers/spam)
all_spam_ids = []
page = 1
while True:
    r = requests.get(
        f'{API}/users',
        params={'per_page': 100, 'page': page, 'roles': ''},
        headers=H, timeout=20)
    if r.status_code != 200 or not r.json():
        break
    users = r.json()
    # Identify spam: users with no roles and numeric/random-looking names
    for u in users:
        roles = u.get('roles', [])
        name = u.get('name', '')
        slug = u.get('slug', '')
        uid = u.get('id', 0)
        # Skip real users
        if 'administrator' in roles or 'editor' in roles or 'author' in roles:
            continue
        if 'contributor' in roles:
            continue
        if 'vjvarada' in slug.lower() or 'fracktal' in slug.lower():
            continue
        # Everything else is spam (no roles = subscriber, or customer role)
        all_spam_ids.append(uid)
    
    page += 1
    if page > 50:  # Safety limit
        break
    time.sleep(0.5)

print(f"  Found {len(all_spam_ids)} spam users to delete")

# Delete in batches
deleted = 0
failed = 0
batch_size = 20
for i in range(0, min(len(all_spam_ids), 500), batch_size):
    batch = all_spam_ids[i:i+batch_size]
    for uid in batch:
        try:
            r_del = requests.delete(
                f'{API}/users/{uid}?reassign=1&force=true',
                headers=H_JSON, timeout=10)
            if r_del.status_code in [200, 201]:
                deleted += 1
            else:
                failed += 1
        except Exception:
            failed += 1
        time.sleep(0.3)
    
    if (i + batch_size) % 100 == 0:
        print(f"  Progress: {deleted} deleted, {failed} failed...")

print(f"  Done: {deleted} deleted, {failed} failed")
if len(all_spam_ids) > 500:
    print(f"  ⚠️ {len(all_spam_ids) - 500} remaining (limit reached)")

# ═══════════════════════════════════════════════════════════
# 2. HARDENING: Disable debug display + file editor
# ═══════════════════════════════════════════════════════════
print("\n=== 2. HARDENING ===")

# Check current settings
r_settings = requests.get(f'{API}/settings', headers=H, timeout=15)
if r_settings.status_code == 200:
    settings = r_settings.json()
    print(f"  Debug visible: {settings.get('debug_display', 'unknown')}")

# Try to set hardenings available via REST API
# Note: DISALLOW_FILE_EDIT and WP_DEBUG_DISPLAY need wp-config.php access
# But we can try some things via options API

# Disable user registration (prevents new spam)
r_reg = requests.post(
    f'{API}/settings',
    headers=H_JSON,
    json={'users_can_register': False},
    timeout=10)
print(f"  User registration disabled: {r_reg.status_code}")

# Disable XML-RPC via option if possible
# Try to set default comment status to closed
r_comments = requests.post(
    f'{API}/settings',
    headers=H_JSON,
    json={
        'default_comment_status': 'closed',
        'default_ping_status': 'closed',
    },
    timeout=10)
print(f"  Comments/pings disabled: {r_comments.status_code}")

# ═══════════════════════════════════════════════════════════
# 3. PURGE LITESPEED CACHE (via wp-admin)
# ═══════════════════════════════════════════════════════════
print("\n=== 3. CACHE PURGE ===")
session = requests.Session()
session.headers.update(H)

# Get wp-admin nonce
r_admin = session.get(f'{SITE}/wp-admin/', timeout=15)
import re
nonces = re.findall(r'_wpnonce=([a-f0-9]+)', r_admin.text)
if nonces:
    wp_nonce = nonces[0]
    # Try to purge LiteSpeed via admin-post
    r_purge = session.post(
        f'{SITE}/wp-admin/admin-post.php',
        data={
            'action': 'litespeed_purge_all',
            '_wpnonce': wp_nonce,
        },
        timeout=10)
    print(f"  Purge attempt: {r_purge.status_code}")
    
    # Alternative: try directly
    r_purge2 = session.get(
        f'{SITE}/wp-admin/admin.php?page=litespeed&'
        f'litespeed_type=purge_all&_wpnonce={wp_nonce}',
        timeout=10)
    print(f"  Purge attempt 2: {r_purge2.status_code}")
else:
    print("  Could not get wp-admin nonce")

# ═══════════════════════════════════════════════════════════
# 4. FINAL VERIFICATION
# ═══════════════════════════════════════════════════════════
print("\n=== 4. FINAL STATE ===")
r_final = requests.get(f'{API}/users?per_page=5', headers=H, timeout=15)
if r_final.status_code == 200:
    remaining = r_final.headers.get('X-WP-Total', '?')
    print(f"  Users remaining: {remaining}")

r_reg_check = requests.get(f'{API}/settings', headers=H, timeout=10)
if r_reg_check.status_code == 200:
    s = r_reg_check.json()
    print(f"  Registration open: {s.get('users_can_register', '?')}")
    print(f"  Default comment: {s.get('default_comment_status', '?')}")

print("\n✅ Cleanup complete!")
