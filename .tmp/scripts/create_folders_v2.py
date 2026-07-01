"""Create folder structure via FileBird API — uses 'title' parameter."""
import requests, base64, os, json, time
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
FB = f"{SITE}/wp-json/filebird/v1"

FOLDERS = [
    "Fracktal Care",
    "Products",
    "Hero Images",
    "Materials",
    "Blog Covers",
    "Team & Company",
    "Documents",
    "Videos",
    "Icons & UI",
    "Services",
    "Uncategorized",
]

# First get existing folders to avoid duplicates
r = requests.get(f"{FB}/get-folders", headers=H, timeout=10)
existing_tree = r.json().get("tree", [])
existing_names = {f["title"]: f["id"] for f in existing_tree}
print(f"Existing folders: {len(existing_names)}")

created = 0
for name in FOLDERS:
    if name in existing_names:
        print(f"  Skip (exists): {name} (ID {existing_names[name]})")
        continue
    time.sleep(0.3)
    r2 = requests.post(
        f"{FB}/new-folder",
        headers=H,
        json={"title": name, "parent": 0},
        timeout=10,
    )
    if r2.status_code == 200:
        data = r2.json()
        if isinstance(data, list) and data:
            fid = data[0].get("id", "?")
        else:
            fid = data.get("id", "?")
        print(f"  Created: {name} (ID {fid})")
        created += 1
    else:
        print(f"  FAILED: {name} — HTTP {r2.status_code}")

print(f"\nDone. Created {created} new folders.")
print("Go to Media > Library to see the folder tree.")
