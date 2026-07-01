"""Update robots.txt via Yoast SEO file editor"""
import requests, base64, re

AUTH = 'Basic ' + base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': AUTH}
S = requests.Session()
S.headers.update(H)

URL = 'https://fracktal.in/wp-admin/admin.php'
PARAMS = {'page': 'wpseo_tools', 'tool': 'file-editor'}

# Step 1: GET the page to get nonce
r = S.get(URL, params=PARAMS, timeout=15)
html = r.text

# Check if robots.txt textarea exists or if we need to create it first
if 'name="robotsnew"' in html:
    print("Robots.txt editor found - can edit directly")
elif 'name="create_robots"' in html:
    print("Need to create robots.txt first - clicking create...")
    # Extract nonce for create
    nonce_m = re.search(r'name="_wpnonce" value="([a-f0-9]+)"', html)
    if nonce_m:
        nonce = nonce_m.group(1)
        r2 = S.post(URL, params=PARAMS, data={
            '_wpnonce': nonce,
            'create_robots': 'Create'
        }, timeout=15)
        html = r2.text
        if 'name="robotsnew"' in html:
            print("Robots.txt created! Now editing...")
        else:
            print("Failed to create robots.txt")
            print(r2.text[:500])
else:
    print("Neither create nor edit found. Page content:")
    print(html[:1000])
    exit()

# Step 2: Extract nonce for save
nonce_m = re.search(r'name="_wpnonce" value="([a-f0-9]+)"', html)
if not nonce_m:
    print("Could not find nonce")
    exit()
nonce = nonce_m.group(1)
print(f"Nonce: {nonce[:10]}...")

# Step 3: Build new robots.txt
new_robots = """User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Disallow: /wp-content/uploads/wc-logs/
Disallow: /wp-content/uploads/woocommerce_transient_files/
Disallow: /wp-content/uploads/woocommerce_uploads/
Disallow: /*?add-to-cart=
Disallow: /*?*add-to-cart=

# AI Crawlers - allow public content, block admin
User-agent: Google-Extended
Disallow: /wp-admin/
Allow: /

User-agent: GPTBot
Disallow: /wp-admin/
Allow: /

User-agent: CCBot
Disallow: /wp-admin/
Allow: /

Sitemap: https://fracktal.in/sitemap_index.xml"""

# Step 4: POST the update
r3 = S.post(URL, params=PARAMS, data={
    '_wpnonce': nonce,
    'robotsnew': new_robots,
}, timeout=15)

# Step 5: Verify
print(f"Save status: {r3.status_code}")
if 'updated' in r3.text.lower() or 'saved' in r3.text.lower() or r3.status_code == 200:
    r4 = requests.get('https://fracktal.in/robots.txt', timeout=10)
    print("\n=== NEW robots.txt ===")
    print(r4.text)
else:
    print("Save may have failed. Response:")
    print(r3.text[:500])
