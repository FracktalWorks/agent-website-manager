"""Find and fix the H1 heading on fracktal.in homepage"""
import requests, base64, json, copy

auth = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
h = {'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'}
HOME_ID = 2309

# Re-trigger meta visibility then get the page
requests.post(
    f'https://fracktal.in/wp-json/wp/v2/pages/{HOME_ID}',
    headers=h,
    json={'meta': {'_elementor_edit_mode': 'builder'}},
    timeout=15)

r = requests.get(
    f'https://fracktal.in/wp-json/wp/v2/pages/{HOME_ID}',
    headers=h, timeout=15)
page = r.json()
elem_str = page.get('meta', {}).get('_elementor_data', '')
if not elem_str:
    print("ERROR: Still no Elementor data")
    exit(1)

elem_data = json.loads(elem_str)
print(f"Elementor data loaded: {type(elem_data).__name__}")
print(f"Top-level items: {len(elem_data) if isinstance(elem_data, list) else 'N/A'}")

# Search for ALL heading widgets and widgets that could be the H1
headings_found = []

def search_widgets(data, path=""):
    """Recursively search for heading/title widgets."""
    if isinstance(data, dict):
        wt = data.get('widgetType', '')
        et = data.get('elType', '')
        settings = data.get('settings', {})
        title = settings.get('title', '')

        # Look for heading or page-title widgets
        if wt == 'heading' or 'title' in wt.lower():
            headings_found.append({
                'id': data.get('id', '?'),
                'widgetType': wt,
                'elType': et,
                'title_preview': str(title)[:120] if title else '(empty)',
                'header_size': settings.get('header_size', '?'),
                'html_tag': settings.get('title_tag', settings.get('html_tag', '?')),
                'path': path,
                'settings_keys': [k for k in settings.keys()
                                  if any(x in k.lower() for x in
                                         ['tag', 'size', 'html', 'title', 'head'])]
            })

        # Recurse into children
        for key, val in data.items():
            if isinstance(val, (dict, list)):
                new_path = f"{path}.{key}" if path else key
                search_widgets(val, new_path)

    elif isinstance(data, list):
        for i, item in enumerate(data):
            search_widgets(item, f"{path}[{i}]")

search_widgets(elem_data)

print(f"\nFound {len(headings_found)} heading/title widgets:")
print("-" * 80)

for hw in headings_found[:20]:
    print(f"  ID: {hw['id']}")
    print(f"  Type: {hw['widgetType']}")
    print(f"  Title: {hw['title_preview']}")
    print(f"  Header size: {hw['header_size']}")
    print(f"  HTML tag settings: {hw['settings_keys']}")
    print(f"  Path: {hw['path'][:100]}")
    print()

# Find the closest candidate for H1 (usually the first heading with the page title)
if headings_found:
    best = headings_found[0]
    print("=" * 60)
    print(f"BEST H1 CANDIDATE: {best['id']}")
    print(f"  Current title: {best['title_preview']}")
    print(f"  Current header_size: {best['header_size']}")
    print(f"  Path: {best['path']}")

    # Now modify it to H1
    path_parts = best['path'].split('.')
    current = elem_data

    # Navigate to the widget using the path
    for part in path_parts:
        if part.startswith('elements['):
            idx = int(part[9:-1])
            current = current['elements'][idx]
        elif part == 'elements':
            current = current['elements']
        elif part.startswith('['):
            idx = int(part[1:-1])
            current = current[idx]
        elif part in current:
            current = current[part]
        else:
            print(f"  WARNING: Could not navigate to {part}")
            break

    # Now current should be at the widget settings level
    # The heading widget's HTML tag is usually in settings.header_size
    if 'settings' in current:
        old_tag = current['settings'].get('header_size', 'not set')
        current['settings']['header_size'] = 'h1'
        print(f"  Changed header_size from '{old_tag}' to 'h1'")

        # Also check for alternative tag fields
        for tag_field in ['title_tag', 'html_tag', 'heading_tag']:
            if tag_field in current['settings']:
                old = current['settings'][tag_field]
                current['settings'][tag_field] = 'h1'
                print(f"  Changed {tag_field} from '{old}' to 'h1'")

        # Save back
        updated_elem_data = json.dumps(elem_data)
        print(f"\n  Updated Elementor data size: {len(updated_elem_data)} bytes")

        r2 = requests.post(
            f'https://fracktal.in/wp-json/wp/v2/pages/{HOME_ID}',
            headers=h,
            json={
                'meta': {
                    '_elementor_data': updated_elem_data,
                    '_elementor_edit_mode': 'builder',
                }
            },
            timeout=30)
        print(f"  Save status: {r2.status_code}")
        if r2.status_code == 200:
            print(f"  ✅ H1 FIX APPLIED!")
        else:
            print(f"  Error: {r2.text[:300]}")
else:
    print("No heading widgets found. The title might be in the page content, not Elementor.")
