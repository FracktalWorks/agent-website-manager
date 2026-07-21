"""Check WordPress 7 available APIs and AI/block capabilities."""
import requests
import base64
import json

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}

# Get all routes
r = requests.get('https://fracktal.in/wp-json/', headers=H, timeout=15)
data = r.json()
routes = data.get('routes', {})
namespaces = data.get('namespaces', [])

print(f"=== WordPress 7 API Namespaces ({len(namespaces)}) ===")
for ns in sorted(namespaces):
    route_count = sum(1 for k in routes if k.startswith('/' + ns.replace('/', '\\/')))
    print(f"  {ns} ({route_count} routes)")

# Key AI/block/modern features
print("\n=== BLOCK EDITOR / AI-RELATED ENDPOINTS ===")
ai_keywords = [
    'block-renderer', 'block-pattern', 'block-type',
    'template', 'template-part', 'global-style',
    'navigation', 'font', 'font-face',
    'ai', 'machine', 'llm', 'chat',
    'pattern-directory', 'block-directory',
    'reusable-block', 'wp_block',
    'site-editor', 'edit-site',
    'style-book', 'theme-json',
]
for kw in ai_keywords:
    matches = [k for k in routes if kw in k.lower()]
    if matches:
        print(f"\n  [{kw}] ({len(matches)} routes):")
        for m in sorted(matches)[:8]:
            methods = routes[m].get('methods', ['GET'])
            print(f"    {','.join(methods)} {m}")

# Check if we can access block types
print("\n=== BLOCK TYPES ===")
r_blocks = requests.get(
    'https://fracktal.in/wp-json/wp/v2/block-types',
    headers=H, timeout=15)
if r_blocks.status_code == 200:
    blocks = r_blocks.json()
    print(f"  Registered blocks: {len(blocks)}")
    ai_blocks = [b for b in blocks if any(
        w in str(b.get('name', '')).lower()
        for w in ['ai', 'chat', 'generate', 'copilot', 'assist']
    )]
    if ai_blocks:
        print(f"  AI-related blocks: {len(ai_blocks)}")
        for b in ai_blocks:
            print(f"    - {b.get('name')}: {b.get('title')}")
    else:
        print("  No AI-specific blocks found")
else:
    print(f"  Block types API: {r_blocks.status_code}")

# Check Site Editor / FSE availability
print("\n=== FULL SITE EDITING ===")
r_templates = requests.get(
    'https://fracktal.in/wp-json/wp/v2/templates',
    headers=H, timeout=15)
print(f"  Templates API: {r_templates.status_code}")

r_template_parts = requests.get(
    'https://fracktal.in/wp-json/wp/v2/template-parts',
    headers=H, timeout=15)
print(f"  Template Parts API: {r_template_parts.status_code}")

r_global_styles = requests.get(
    'https://fracktal.in/wp-json/wp/v2/global-styles',
    headers=H, timeout=15)
print(f"  Global Styles API: {r_global_styles.status_code}")

# Check wp/v2/settings for AI-related options
print("\n=== AI-RELATED SETTINGS ===")
r_settings = requests.get(
    'https://fracktal.in/wp-json/wp/v2/settings',
    headers=H, timeout=15)
if r_settings.status_code == 200:
    s = r_settings.json()
    ai_keys = [k for k in s if any(
        w in k.lower() for w in ['ai', 'block', 'pattern', 'site_editor']
    )]
    for k in sorted(ai_keys):
        print(f"  {k}: {str(s[k])[:100]}")

print("\n✅ WP 7 API check complete")
