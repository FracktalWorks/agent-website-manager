"""Inject CSS fixes for homepage hero and header dropdown."""
import requests
from requests.auth import HTTPBasicAuth

WP = 'https://fracktal.in'
auth = HTTPBasicAuth('vjvarada', 'eBZmsn9ovjOvcvtW14bZPbsx')

# CSS to fix both issues
css = """/* Fix 1: Hero slides widget width */
.elementor-element-b245d39 { width: 100% !important; }

/* Fix 2: Mega menu dropdown - ensure panel doesn't overlap & block menu items */
.elementor-widget-n-menu.e-n-menu-layout-horizontal .e-n-menu-heading {
    z-index: 1000;
}
.elementor-widget-n-menu .e-n-menu-content.e-active {
    pointer-events: auto;
}
.elementor-widget-n-menu .e-n-menu-title {
    z-index: 1001;
    position: relative;
}"""

# Try POST to update settings
print("Injecting CSS via WordPress settings...")
r = requests.post(
    f'{WP}/wp-json/wp/v2/settings',
    auth=auth,
    json={'hello_elementor_settings_hello_style': css},
    timeout=15
)
print(f'Response: {r.status_code}')
if r.ok:
    updated = r.json()
    result = updated.get('hello_elementor_settings_hello_style', 'NOT RETURNED')
    if result:
        print(f'CSS applied successfully! ({len(result)} chars)')
    else:
        print('CSS value is empty - may not have been saved')
else:
    print(f'Error: {r.text[:500]}')

# Verify by reading back
r2 = requests.get(f'{WP}/wp-json/wp/v2/settings', auth=auth, timeout=10)
settings = r2.json()
saved = settings.get('hello_elementor_settings_hello_style', '')
if saved:
    print(f'\nVerified: CSS is saved ({len(saved)} chars)')
else:
    print('\nWARNING: CSS may not have been saved')
    # Try alternative: check if the setting needs to be registered
    print('The setting might not be registered for REST API updates.')
