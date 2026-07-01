"""Fix H1 on fracktal.in homepage using EMCP MCP tools"""
import requests, base64, json

AUTH = 'Basic ' + base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': AUTH, 'Content-Type': 'application/json'}
URL = 'https://fracktal.in/wp-json/mcp/emcp-tools-server'

def mcp_call(method, params=None, sid=None):
    headers = dict(H)
    if sid:
        headers['Mcp-Session-Id'] = sid
    payload = {'jsonrpc': '2.0', 'method': method, 'id': 1}
    if params:
        payload['params'] = params
    r = requests.post(URL, headers=headers, json=payload, timeout=30)
    return r.json(), r.headers

# Initialize
resp, headers = mcp_call('initialize', {
    'protocolVersion': '2024-11-05',
    'capabilities': {},
    'clientInfo': {'name': 'Agent', 'version': '1.0'}
})
sid = headers.get('Mcp-Session-Id', '')
print(f"Session: {sid[:20]}...")

# Get page structure
resp, _ = mcp_call('tools/call', {
    'name': 'emcp-tools-get-page-structure',
    'arguments': {'post_id': 2309}
}, sid=sid)

data = json.loads(resp['result']['content'][0]['text'])
structure = data['structure']

# Recursively find heading widgets
headings = []
def find_headings(elements):
    if isinstance(elements, list):
        for el in elements:
            if isinstance(el, dict):
                wt = el.get('widgetType', '')
                if wt == 'heading':
                    ss = el.get('settings_summary', {})
                    headings.append({
                        'id': el.get('id', ''),
                        'title': str(ss.get('title', ''))[:80],
                        'html_tag': ss.get('header_size', '?'),
                    })
                find_headings(el.get('elements', []))

find_headings(structure)

print(f"\nFound {len(headings)} heading widgets:")
for h in headings:
    print(f"  {h['id']}  tag={h['html_tag']:6s}  \"{h['title']}\"")

# Find non-H1 headings
non_h1 = [h for h in headings if h['html_tag'] != 'h1']
print(f"\n{len(non_h1)} non-H1 headings found.")

# The first heading that looks like the page title should be H1
# Usually it's the first heading on the page or one with the site name
if non_h1:
    target = non_h1[0]  # Start with first non-H1
    print(f"\nConverting '{target['title']}' (ID: {target['id']}) from {target['html_tag']} to h1...")

    # Update the element
    resp, _ = mcp_call('tools/call', {
        'name': 'emcp-tools-update-element',
        'arguments': {
            'post_id': 2309,
            'element_id': target['id'],
            'settings': {'header_size': 'h1'}
        }
    }, sid=sid)

    result_text = resp['result']['content'][0]['text']
    print(f"Result: {result_text[:300]}")
    
    if '"success":true' in result_text or 'error' not in result_text.lower():
        print("\n✅ H1 FIX APPLIED!")
    else:
        print("\n⚠️ Check result above")
else:
    print("All headings already H1!")
