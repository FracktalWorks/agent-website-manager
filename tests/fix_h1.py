"""Fix H1 on fracktal.in homepage via Elementor API"""
import requests, base64, json

auth = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
h = {'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'}

HOME_ID = 2309

# Try Elementor document API
print("=== Elementor Document API ===")
r = requests.get(
    f'https://fracktal.in/wp-json/elementor/v1/documents/{HOME_ID}',
    headers=h, timeout=15)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    doc = r.json()
    print(f"Keys: {list(doc.keys())[:15]}")
    if 'elements' in doc:
        elements = doc['elements']
        print(f"Elements type: {type(elements).__name__}")
        if isinstance(elements, list):
            print(f"Element count: {len(elements)}")
            for i, el in enumerate(elements[:5]):
                wt = el.get('widgetType', '')
                et = el.get('elType', '')
                sid = el.get('id', '')
                print(f"  [{i}] elType={et} widget={wt} id={sid}")
    else:
        print(f"No elements key. Available: {list(doc.keys())}")
else:
    print(f"Error: {r.text[:300]}")

# Try to access the Elementor data via post meta API  
print("\n=== Post Meta API ===")
r2 = requests.get(
    f'https://fracktal.in/wp-json/wp/v2/pages/{HOME_ID}',
    headers=h,
    params={'_fields': 'id,title,meta'},
    timeout=15)
if r2.status_code == 200:
    page = r2.json()
    meta = page.get('meta', {})
    print(f"Meta keys: {list(meta.keys())}")
    elem_data = meta.get('_elementor_data', '')
    print(f"Has _elementor_data: {bool(elem_data)}")
    if elem_data:
        data = json.loads(elem_data) if isinstance(elem_data, str) else elem_data
        print(f"Data type: {type(data).__name__}, length: {len(data) if isinstance(data, list) else 'N/A'}")

# Try elementor-pro endpoint
print("\n=== Elementor Pro API ===")
try:
    r3 = requests.get(
        f'https://fracktal.in/wp-json/elementor-pro/v1/documents/{HOME_ID}',
        headers=h, timeout=15)
    print(f"Status: {r3.status_code}")
    if r3.status_code == 200:
        print(f"Keys: {list(r3.json().keys())[:15]}")
    else:
        print(f"Body: {r3.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Try the elementor-one endpoint that we saw in namespaces
print("\n=== Elementor One API ===")
try:
    r4 = requests.get(
        f'https://fracktal.in/wp-json/elementor-one/v1',
        headers=h, timeout=15)
    print(f"Status: {r4.status_code}")
    if r4.status_code == 200:
        print(f"Body: {json.dumps(r4.json())[:300]}")
except Exception as e:
    print(f"Error: {e}")

# Direct post meta approach: refresh page to trigger Elementor meta exposure
print("\n=== Attempting to update page to expose Elementor meta ===")
# Elementor stores data in _elementor_data post meta
# We can try updating the page which might expose it
r5 = requests.post(
    f'https://fracktal.in/wp-json/wp/v2/pages/{HOME_ID}',
    headers=h,
    json={'meta': {'_elementor_edit_mode': 'builder'}},
    timeout=15)
print(f"Edit mode set: {r5.status_code}")
if r5.status_code == 200:
    new_meta = r5.json().get('meta', {})
    elem = new_meta.get('_elementor_data', '')
    print(f"Elementor data now visible: {bool(elem)}")
    if elem:
        print(f"Data length: {len(elem)}")
