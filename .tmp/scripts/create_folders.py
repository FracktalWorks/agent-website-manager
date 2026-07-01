"""Create folder structure and organize media via FileBird API."""
import requests, base64, os, json
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}"}
FB = f"{SITE}/wp-json/filebird/v1"
FB_PUB = f"{SITE}/wp-json/filebird/public/v1"


def api(method, path, data=None):
    url = f"{FB}/{path}"
    if method == "GET":
        r = requests.get(url, headers=H, timeout=15)
    elif method == "POST":
        r = requests.post(url, headers=H, json=data, timeout=15)
    else:
        r = requests.put(url, headers=H, json=data, timeout=15)
    return r


# Step 1: Get existing folders
print("=== Current Folders ===")
r = api("GET", "get-folders")
if r.status_code == 200:
    folders = r.json().get("data", {}).get("folders", [])
    for f in folders:
        print(f"  [{f['id']}] {f['text']} (parent: {f.get('parent',0)})")
else:
    print(f"Error: {r.status_code} — {r.text[:200]}")

# Step 2: Create folder structure
DESIRED_FOLDERS = [
    ("Products", 0),
    ("Products/Snowflake", 0),  # will fix parent after creation
    ("Products/Julia", 0),
    ("Products/Twin Dragon", 0),
    ("Products/Volterra", 0),
    ("Products/Apollo SLS", 0),
    ("Products/PrintStick", 0),
    ("Products/Material Dryer", 0),
    ("Hero Images", 0),
    ("Materials", 0),
    ("Blog Covers", 0),
    ("Team & Company", 0),
    ("Documents", 0),
    ("Videos", 0),
    ("Icons & UI", 0),
    ("Services", 0),
    ("Fracktal Care", 0),
]

created = {}
print("\n=== Creating Folders ===")
for name, parent in DESIRED_FOLDERS:
    parts = name.split("/")
    display_name = parts[-1]
    r = api("POST", "new-folder", {"name": display_name, "parent": parent})
    if r.status_code in (200, 201):
        fid = r.json().get("data", {}).get("id", "?")
        created[name] = fid
        print(f"  Created: {name} -> ID {fid}")
    else:
        # Might already exist
        print(f"  {name}: HTTP {r.status_code} (may already exist)")

print(f"\nTotal folders created: {len(created)}")
print("\nNow go to Media > Library to drag images into these folders.")
