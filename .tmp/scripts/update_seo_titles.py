#!/usr/bin/env python3
"""Update page SEO settings via WordPress REST API"""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

site = os.getenv("WORDPRESS_SITE_URL")
user = os.getenv("WORDPRESS_USERNAME")
pw = os.getenv("WORDPRESS_APP_PASSWORD")

auth = base64.b64encode(f"{user}:{pw}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# 1. Update /3dprinters/ page (post_id 26689)
data = {
    "title": "Made in India 3D Printers \u2014 Industrial & Desktop | Fracktal Works",
    "excerpt": (
        "India's premier 3D printer manufacturer. Explore Fracktal Works' "
        "range of indigenously designed and manufactured industrial FDM, SLS, "
        "and desktop 3D printers, built in Bangalore. Make in India additive "
        "manufacturing solutions."
    ),
}
r = requests.post(f"{site}/wp-json/wp/v2/pages/26689", headers=headers, json=data)
print(f"[1] /3dprinters/ (26689): HTTP {r.status_code}")
if r.status_code == 200:
    j = r.json()
    t = j.get("title", {}).get("rendered", "N/A")
    print(f"    Title: {t}")
else:
    print(f"    Error: {r.text[:200]}")

# 2. Update homepage (post_id 2309) excerpt only — title is fine
data2 = {
    "excerpt": (
        "Fracktal Works is India's premier manufacturer of industrial and "
        "desktop 3D printers. Pioneering indigenous additive manufacturing "
        "in Bangalore since 2013. Make in India 3D printers for every industry."
    ),
}
r2 = requests.post(f"{site}/wp-json/wp/v2/pages/2309", headers=headers, json=data2)
print(f"[2] Homepage (2309): HTTP {r2.status_code}")
if r2.status_code != 200:
    print(f"    Error: {r2.text[:200]}")
else:
    print("    Excerpt updated OK")

# 3. Update /about-us/ page title for manufacturer signal
data3 = {
    "title": "About Us — India's 3D Printer Manufacturer | Fracktal Works",
}
r3 = requests.post(f"{site}/wp-json/wp/v2/pages/4029", headers=headers, json=data3)
print(f"[3] /about-us/ (4029): HTTP {r3.status_code}")
if r3.status_code == 200:
    j = r3.json()
    t = j.get("title", {}).get("rendered", "N/A")
    print(f"    Title: {t}")
else:
    print(f"    Error: {r3.text[:200]}")

print("\nDone. All existing pages updated with India/manufacturer SEO signals.")
