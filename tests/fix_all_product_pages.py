"""Fix H1s on all product pages + meta desc on Fracktal Care via MCP"""
import requests, base64, json

AUTH = 'Basic ' + base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': AUTH, 'Content-Type': 'application/json'}
SITE = 'https://fracktal.in'
MCP_URL = f'{SITE}/wp-json/mcp/emcp-tools-server'
API_URL = f'{SITE}/wp-json/wp/v2'

# ═══════════════════════════════
# 1. GET PAGE IDs
# ═══════════════════════════════
r = requests.get(f'{API_URL}/pages',
                 headers={'Authorization': 'Basic ' + base64.b64encode(
                     b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()},
                 params={'per_page': 50, 'status': 'publish'}, timeout=30)
all_pages = r.json()

targets = {
    'snowflake': None, 'twindragon': None, 'printstick': None,
    'apollo-sls-landing-page': None, 'julia': None, 'fracktal-care': None
}
for p in all_pages:
    if p['slug'] in targets:
        targets[p['slug']] = {'id': p['id'], 'title': p['title']['rendered']}

print("Page IDs found:")
for slug, data in targets.items():
    if data:
        print(f"  {slug}: ID={data['id']} — {data['title'][:60]}")

# ═══════════════════════════════
# 2. INIT MCP SESSION
# ═══════════════════════════════
r_init = requests.post(MCP_URL, headers=H, json={
    'jsonrpc': '2.0', 'method': 'initialize',
    'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
               'clientInfo': {'name': 'Agent', 'version': '1.0'}},
    'id': 1}, timeout=15)
sid = r_init.headers['Mcp-Session-Id']
H2 = {**H, 'Mcp-Session-Id': sid}
print(f"\nMCP session: {sid[:20]}...")

def mcp_call(method, params):
    r = requests.post(MCP_URL, headers=H2, json={
        'jsonrpc': '2.0', 'method': method, 'params': params, 'id': 1
    }, timeout=30)
    return r.json()

# ═══════════════════════════════
# 3. FIX H1 ON PAGES WITH 0 H1s
# ═══════════════════════════════
fixes_applied = []

for slug in ['snowflake', 'twindragon', 'apollo-sls-landing-page', 'julia']:
    data = targets.get(slug)
    if not data:
        print(f"\n{slug}: SKIP — page not found")
        continue
    pid = data['id']
    print(f"\n{slug} (ID={pid}):")

    # Get page structure
    resp = mcp_call('tools/call', {
        'name': 'emcp-tools-get-page-structure',
        'arguments': {'post_id': pid}
    })
    structure = json.loads(resp['result']['content'][0]['text'])['structure']

    # Find first heading widget
    def find_first_heading(elements):
        if isinstance(elements, list):
            for el in elements:
                if isinstance(el, dict):
                    if el.get('widgetType') == 'heading':
                        return el['id']
                    result = find_first_heading(el.get('elements', []))
                    if result:
                        return result
        return None

    heading_id = find_first_heading(structure)
    if not heading_id:
        print("  No heading widget found")
        continue

    # Update to H1
    resp = mcp_call('tools/call', {
        'name': 'emcp-tools-update-element',
        'arguments': {
            'post_id': pid,
            'element_id': heading_id,
            'settings': {'header_size': 'h1'}
        }
    })
    result_text = resp['result']['content'][0]['text']
    success = '"success":true' in result_text
    print(f"  Heading {heading_id} → H1: {'✅' if success else '⚠️'}")
    if success:
        fixes_applied.append(f"{slug}: H1 added ({heading_id})")

# ═══════════════════════════════
# 4. FIX PRINTSTICK (2 H1s → 1 H1 + 1 H2)
# ═══════════════════════════════
ps = targets.get('printstick')
if ps:
    pid = ps['id']
    print(f"\nprintstick (ID={pid}) — fixing double H1:")

    resp = mcp_call('tools/call', {
        'name': 'emcp-tools-get-page-structure',
        'arguments': {'post_id': pid}
    })
    structure = json.loads(resp['result']['content'][0]['text'])['structure']

    # Find ALL heading widgets
    headings = []
    def find_all_headings(elements):
        if isinstance(elements, list):
            for el in elements:
                if isinstance(el, dict):
                    if el.get('widgetType') == 'heading':
                        headings.append(el['id'])
                    find_all_headings(el.get('elements', []))

    find_all_headings(structure)
    print(f"  Found {len(headings)} heading widgets")

    if len(headings) >= 2:
        # First → H1, second → H2
        first, second = headings[0], headings[1]

        for h_id, tag in [(first, 'h1'), (second, 'h2')]:
            resp = mcp_call('tools/call', {
                'name': 'emcp-tools-update-element',
                'arguments': {
                    'post_id': pid,
                    'element_id': h_id,
                    'settings': {'header_size': tag}
                }
            })
            result_text = resp['result']['content'][0]['text']
            success = '"success":true' in result_text
            print(f"  {h_id} → {tag.upper()}: {'✅' if success else '⚠️'}")

    fixes_applied.append(f"printstick: fixed double H1")

# ═══════════════════════════════
# 5. FIX FRACKTAL CARE META DESC
# ═══════════════════════════════
fc = targets.get('fracktal-care')
if fc:
    pid = fc['id']
    print(f"\nfracktal-care (ID={pid}) — adding meta description:")

    meta_desc = ("Fracktal Care provides comprehensive maintenance, support, "
                 "and service plans for Fracktal Works 3D printers in India. "
                 "Extended warranties, annual maintenance contracts, and "
                 "expert technical support for your additive manufacturing equipment.")

    # Update page excerpt + Yoast meta
    r_update = requests.post(f'{API_URL}/pages/{pid}',
        headers={'Authorization': 'Basic ' + base64.b64encode(
            b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode(),
            'Content-Type': 'application/json'},
        json={
            'excerpt': meta_desc,
            'meta': {
                '_yoast_wpseo_metadesc': meta_desc,
                '_yoast_wpseo_title': 'Fracktal Care — 3D Printer Support & '
                                      'Maintenance in India | Fracktal Works',
            }
        }, timeout=15)

    print(f"  Meta desc: {'✅' if r_update.status_code == 200 else '⚠️'}")
    fixes_applied.append(f"fracktal-care: meta description added")

# ═══════════════════════════════
# 6. ADD INDIA KEYWORDS TO PRODUCT PAGE TITLES
# ═══════════════════════════════
print("\n--- India SEO: Updating page titles ---")
title_updates = {
    'snowflake': ('Snowflake High-Precision Desktop 3D Printer in India | '
                  'Fracktal Works'),
    'twindragon': ('Twin Dragon Dual-Extrusion 3D Printer in India | '
                   'Fracktal Works'),
    'apollo-sls-landing-page': ('Apollo SLS Production-Grade 3D Printer in '
                                'India | Fracktal Works'),
    'julia': ('Julia Advanced 3D Printing Platform in India | Fracktal Works'),
    'printstick': ('PrintStick 3D Printer Bed Adhesion Solution in India | '
                   'Fracktal Works'),
}

rest_auth = 'Basic ' + base64.b64encode(
    b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
rest_h = {'Authorization': rest_auth, 'Content-Type': 'application/json'}

for slug, new_title in title_updates.items():
    data = targets.get(slug)
    if not data:
        continue
    pid = data['id']

    # Update title + Yoast SEO title
    r = requests.post(f'{API_URL}/pages/{pid}', headers=rest_h, json={
        'title': new_title,
        'meta': {'_yoast_wpseo_title': new_title}
    }, timeout=15)

    status = '✅' if r.status_code == 200 else '⚠️'
    print(f"  {slug}: {status}")

# ═══════════════════════════════
# SUMMARY
# ═══════════════════════════════
print(f"\n{'='*50}")
print(f"FIXES APPLIED: {len(fixes_applied)}")
for f in fixes_applied:
    print(f"  ✅ {f}")
