"""Inspect header menu structure from raw HTML."""
import requests
import re

r = requests.get('https://fracktal.in', headers={'User-Agent': 'Mozilla/5.0'})
html = r.text

# Find data-elementor-type="header"
header_match = re.search(r'<div[^>]*data-elementor-type="header"[^>]*>', html)
if header_match:
    # Get header section
    start = header_match.start()
    # Find the closing of this div (approximate)
    depth = 0
    end = start
    for i in range(start, min(start + 15000, len(html))):
        if html[i:i+4] == '<div':
            depth += 1
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                end = i + 6
                break
    
    header_html = html[start:end]
    print(f"Header length: {len(header_html)} chars")
    
    # Find all elementor-widget-n-menu in header
    n_menu_matches = list(re.finditer(r'<div[^>]*elementor-widget-n-menu[^>]*>', header_html))
    print(f"\nFound {len(n_menu_matches)} n-menu widgets in header:")
    for i, m in enumerate(n_menu_matches):
        snippet = m.group(0)
        # Check for hidden classes
        has_hidden = 'elementor-hidden' in snippet
        has_mobile = 'e-n-menu-mobile' in snippet
        has_dropdown = 'e-n-menu-layout-dropdown' in snippet
        print(f"  Widget {i}: hidden={has_hidden}, mobile={has_mobile}, dropdown={has_dropdown}")
        # Show data-settings
        settings = re.search(r'data-settings="([^"]*)"', snippet)
        if settings:
            print(f"    settings: {settings.group(1)[:200]}")
    
    # Find ALL elementor-widget-* in header
    all_widgets = list(re.finditer(r'elementor-widget-(\S+)', header_html))
    widget_types = set()
    for m in all_widgets:
        t = m.group(1).rstrip('"')
        if not t.startswith('elementor'):
            widget_types.add(t)
    print(f"\nAll widget types in header: {sorted(widget_types)}")
    
    # Search for any mega-menu or nav-menu
    for pattern in ['mega-menu', 'nav-menu', 'e-n-menu-content', 'e-n-menu-heading']:
        count = len(re.findall(pattern, header_html))
        if count:
            print(f"  {pattern}: {count} occurrences")

else:
    print("No header found with data-elementor-type='header'")
    # Try alternative
    alt = re.search(r'<header[^>]*>', html)
    if alt:
        print(f"Found <header> at position {alt.start()}")
