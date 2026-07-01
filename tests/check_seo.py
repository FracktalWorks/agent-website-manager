import requests, re, json

html = requests.get('https://fracktal.in/', timeout=15).text

def extract(pattern, text, group=1):
    m = re.search(pattern, text, re.I)
    return m.group(group).strip() if m else "MISSING"

results = {
    "title": extract(r'<title>(.*?)</title>', html),
    "meta_description": extract(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)', html),
    "og_title": extract(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)', html),
    "og_description": extract(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']+)', html),
    "og_image": extract(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)', html),
    "canonical": extract(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', html),
    "robots": extract(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)', html),
}

# Favicon count
icon_links = re.findall(r'<link[^>]*icon[^>]*>', html, re.I)
results["favicon_links_count"] = len(icon_links)
results["favicon_links"] = [re.search(r'href=["\']([^"\']+)', l).group(1) for l in icon_links]

# Check sitemap
try:
    r = requests.get('https://fracktal.in/wp-sitemap.xml', timeout=10)
    results["sitemap"] = f"OK ({r.status_code})"
except Exception as e:
    results["sitemap"] = f"ERROR: {e}"

# Check security headers
try:
    r = requests.get('https://fracktal.in/', timeout=10)
    headers = r.headers
    results["security_headers"] = {
        "X-Frame-Options": headers.get("X-Frame-Options", "MISSING"),
        "X-Content-Type-Options": headers.get("X-Content-Type-Options", "MISSING"),
        "Referrer-Policy": headers.get("Referrer-Policy", "MISSING"),
        "Strict-Transport-Security": headers.get("Strict-Transport-Security", "MISSING"),
        "Content-Security-Policy": headers.get("Content-Security-Policy", "MISSING"),
    }
except: pass

print(json.dumps(results, indent=2))
