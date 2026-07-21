"""Add fetchpriority=high to hero slider images via Elementor JSON."""
import requests
import base64
import json

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}

# Get homepage Elementor data
r = requests.get(
    'https://fracktal.in/wp-json/wp/v2/pages/2309',
    headers=H, timeout=15)
page = r.json()
el_data_str = page.get('meta', {}).get('_elementor_data', '')

if not el_data_str:
    print('No Elementor data found')
    exit()

el_data = json.loads(el_data_str)
print(f'Elementor data loaded: {len(json.dumps(el_data))} chars')


# Recursively find slider/slides widgets and add fetchpriority
def add_fetchpriority(elements, depth=0):
    """Add fetchpriority=high to img elements in sliders."""
    changes = 0
    if isinstance(elements, list):
        for el in elements:
            changes += add_fetchpriority(el, depth + 1)
    elif isinstance(elements, dict):
        widget = elements.get('widgetType', '')
        el_type = elements.get('elType', '')

        # Check if this is a slider or slides widget
        is_slider = 'slides' in str(widget).lower()
        if is_slider:
            print(f'  Found slider at depth {depth}: {widget}')

        # Look for image widgets inside sliders
        if 'image' in str(widget).lower():
            settings = elements.get('settings', {})
            img = settings.get('image', {})
            if img:
                # Add custom attributes for fetchpriority
                custom_attr = settings.get('custom_attributes', '')
                if 'fetchpriority' not in str(custom_attr):
                    if custom_attr:
                        custom_attr += '|fetchpriority|high'
                    else:
                        custom_attr = 'fetchpriority|high'
                    settings['_custom_attributes'] = custom_attr
                    changes += 1
                    print(f'    Added fetchpriority to image')

        # Add to background images in sections
        if el_type == 'widget' and 'image' in str(widget).lower():
            settings = elements.get('settings', {})
            bg = settings.get('background_image', {})
            if bg:
                custom_attr = settings.get('custom_attributes', '')
                if 'fetchpriority' not in str(custom_attr):
                    settings['_custom_attributes'] = (
                        custom_attr + '|fetchpriority|high'
                        if custom_attr else 'fetchpriority|high')
                    changes += 1

        # Recurse into nested elements
        for key, value in elements.items():
            if key not in ('settings', 'elements', 'widgetType'):
                continue
            if isinstance(value, (list, dict)):
                changes += add_fetchpriority(value, depth + 1)

    return changes


changes = add_fetchpriority(el_data)
print(f'Changes made: {changes}')

if changes > 0:
    # Save updated Elementor data
    updated = json.dumps(el_data)
    r2 = requests.post(
        'https://fracktal.in/wp-json/wp/v2/pages/2309',
        headers=H_JSON,
        json={'meta': {'_elementor_data': updated}},
        timeout=15)
    print(f'Save result: {r2.status_code}')
    if r2.status_code == 200:
        print('✅ fetchpriority added to slider images')
else:
    print('No image widgets found in sliders — may need manual edit')
