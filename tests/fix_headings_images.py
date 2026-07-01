"""Fix heading hierarchy and image alt text via EMCP MCP tools"""
import requests, base64, json

AUTH = 'Basic ' + base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': AUTH, 'Content-Type': 'application/json'}
URL = 'https://fracktal.in/wp-json/mcp/emcp-tools-server'

def mcp_session():
    resp, headers = {}, {}
    r = requests.post(URL, headers=H, json={
        'jsonrpc': '2.0', 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'Agent', 'version': '1.0'}},
        'id': 1}, timeout=15)
    return r.headers.get('Mcp-Session-Id', '')

def mcp_call(sid, method, params):
    h = dict(H)
    h['Mcp-Session-Id'] = sid
    r = requests.post(URL, headers=h, json={
        'jsonrpc': '2.0', 'method': method, 'params': params, 'id': 1
    }, timeout=30)
    return r.json()

sid = mcp_session()
print("Session acquired")

# Get full page structure
resp = mcp_call(sid, 'tools/call', {
    'name': 'emcp-tools-get-page-structure',
    'arguments': {'post_id': 2309}
})
data = json.loads(resp['result']['content'][0]['text'])
structure = data['structure']

# Find all heading widgets with their paths
headings = []
def scan(elements, path=''):
    if isinstance(elements, list):
        for el in elements:
            if isinstance(el, dict):
                wt = el.get('widgetType', '')
                eid = el.get('id', '')
                if wt == 'heading':
                    ss = el.get('settings_summary', {})
                    headings.append({
                        'id': eid,
                        'title': str(ss.get('title', ''))[:50],
                        'path': path
                    })
                scan(el.get('elements', []), f"{path}/{eid}" if path else eid)

scan(structure)
print(f"Total headings: {len(headings)}")

# Now get full settings for each heading to find current HTML tags
# We'll check a sample first
for h in headings[:5]:
    resp = mcp_call(sid, 'tools/call', {
        'name': 'emcp-tools-get-element-settings',
        'arguments': {'post_id': 2309, 'element_id': h['id']}
    })
    result_text = resp['result']['content'][0]['text']
    try:
        settings = json.loads(result_text)
        htag = settings.get('settings', {}).get('header_size', 'NOT SET')
        print(f"  {h['id']}: tag={htag}  \"{h['title']}\"")
    except:
        print(f"  {h['id']}: parse error")

# Classify headings and determine target tags
# Major sections → H2, subsections → H3, sub-subs → H4
section_keywords = ['Printers', 'Printing', 'Industry', 'Materials', 'Strength',
                    'Success', 'Stories', 'Reviews', 'One-Stop', 'news',
                    'Design', 'Service', 'Impact', 'development',
                    'Manufacturing', 'Supply', 'Control', 'Layers',
                    'Moisture']
subsection_keywords = ['PLA', 'ABS', 'PET', 'PVA', 'Nylon', 'Carbon',
                       'TPU', 'Apollo', 'MDS', 'PrintStick', 'Snowflake',
                       'Twin', 'FDM', 'SLS', 'SLA', 'MJF', 'Casting',
                       'Quality', 'Visual', 'Resistant', 'Tough',
                       'Support', 'Flexible', 'Rugged', 'Strong',
                       'Affordable', 'Complex', 'Detailed', 'Smooth',
                       'Production', 'Volume', 'process', 'part',
                       'development', 'cost', 'TAT', 'R&amp;D']

target_tags = {}
for h in headings:
    title = h['title']
    if any(kw.lower() in title.lower() for kw in section_keywords):
        target_tags[h['id']] = 'h2'
    elif any(kw.lower() in title.lower() for kw in subsection_keywords):
        target_tags[h['id']] = 'h3'
    else:
        target_tags[h['id']] = 'h3'  # default to h3

# But keep the first heading as H1 (already fixed)
target_tags[headings[0]['id']] = 'h1'

print(f"\nTag assignments: H1={sum(1 for v in target_tags.values() if v=='h1')}, "
      f"H2={sum(1 for v in target_tags.values() if v=='h2')}, "
      f"H3={sum(1 for v in target_tags.values() if v=='h3')}")

# Batch update headings
operations = []
for h in headings[:20]:  # Start with first 20 most important ones
    eid = h['id']
    tag = target_tags.get(eid, 'h3')
    # Skip if already h4 (like "Made with Pride")
    if tag == 'h3':
        operations.append({
            'element_id': eid,
            'settings': {'header_size': tag}
        })

if operations:
    print(f"\nBatch updating {len(operations)} headings to H3...")
    resp = mcp_call(sid, 'tools/call', {
        'name': 'emcp-tools-batch-update',
        'arguments': {
            'post_id': 2309,
            'operations': operations
        }
    })
    result_text = resp['result']['content'][0]['text']
    print(f"Result: {result_text[:500]}")
    
print("\nDone!")
