"""Test meta keys and find the right one for FileBird folders."""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

test_id = 31405
folder_id = 1
keys = [
    "_filebird_folder",
    "_filebird_folder_id",
    "fbv_folder_id",
    "_fbv_folder",
]

for key in keys:
    r = requests.post(
        f"{SITE}/wp-json/wp/v2/media/{test_id}",
        headers=H,
        json={"meta": {key: folder_id}},
        timeout=10,
    )
    print(f"meta['{key}'] = {folder_id}: HTTP {r.status_code}")

# Check folders
r2 = requests.get(
    f"{SITE}/wp-json/filebird/v1/get-folders",
    headers=H, timeout=10,
)
tree = r2.json().get("tree", [])
for f in tree:
    fid = f.get("id", "?")
    title = f.get("title", "?")
    count = f.get("data-count", 0)
    if count > 0:
        print(f"  [{fid}] {title}: {count} files!")
    else:
        print(f"  [{fid}] {title}: {count} files")
