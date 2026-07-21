"""Check if Hello Elementor outputs custom CSS."""
import requests
import re

r = requests.get('https://fracktal.in', headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
html = r.text

# Look for hello-elementor style output
patterns = [
    'hello-elementor-theme-style',
    'hello-elementor-custom',
    'hello-style',
    'width: 100% !important',
    'pointer-events: auto',
]

for pat in patterns:
    count = html.count(pat)
    print(f"'{pat}': {count} occurrences")

# Check all style tags with IDs
style_ids = re.findall(r'<style[^>]*id="([^"]*)"[^>]*>', html)
print(f"\nStyle tag IDs: {style_ids}")

# Check if any inline style contains our CSS
if 'b245d39' in html:
    # Find context around b245d39 in style tags
    for m in re.finditer(r'<style[^>]*>.*?b245d39.*?</style>', html, re.DOTALL):
        print(f"\nStyle with b245d39: {m.group()[:300]}...")
