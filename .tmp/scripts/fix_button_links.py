"""Fix button links in Elementor page by patching _elementor_data via REST API.
The build-page tool stores button URLs as button_url (string), but Elementor
expects link (object: {url, is_external, nofollow}). This script converts them.
"""
import requests, base64, os, json
from dotenv import load_dotenv
load_dotenv()

SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
POST_ID = 31829

auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

# Get current page data
r = requests.get(f"{SITE}/wp-json/wp/v2/pages/{POST_ID}", headers=headers)
page = r.json()
meta = page.get("meta", {})
elem_data_str = meta.get("_elementor_data", "[]")

if isinstance(elem_data_str, list):
    data = elem_data_str
else:
    data = json.loads(elem_data_str)


def fix_buttons(obj):
    if isinstance(obj, dict):
        if obj.get("widgetType") == "button":
            s = obj.get("settings", {})
            burl = s.get("button_url", "")
            if burl:
                s["link"] = {
                    "url": burl,
                    "is_external": "",
                    "nofollow": "",
                }
                txt = s.get("text", "?")
                print(f"Fixed: {txt} -> {burl}")
        for v in obj.values():
            fix_buttons(v)
    elif isinstance(obj, list):
        for item in obj:
            fix_buttons(item)


fix_buttons(data)

# Write back
fixed_json = json.dumps(data)
r2 = requests.post(
    f"{SITE}/wp-json/wp/v2/pages/{POST_ID}",
    headers={**headers, "Content-Type": "application/json"},
    json={"meta": {"_elementor_data": fixed_json}},
)
print(f"Update: HTTP {r2.status_code}")
if r2.status_code != 200:
    print(r2.text[:300])
else:
    print("Buttons fixed successfully.")
