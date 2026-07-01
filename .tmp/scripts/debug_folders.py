"""Debug FileBird folder assignment."""
import requests, base64, os, json
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# Check current folder contents
r = requests.get(f"{SITE}/wp-json/filebird/v1/get-folders", headers=H, timeout=10)
data = r.json()
tree = data.get("tree", [])
print("=== Current Folders ===")
for f in tree:
    fid = f.get("id", "?")
    title = f.get("title", "?")
    count = f.get("data-count", 0)
    print(f"  [{fid}] {title}: {count} files")
print()
print("Actual attachment counts:", data.get("attachmentsCount", {}).get("actual", []))

# Try the public API with a single image
test_id = 31405
r2 = requests.post(
    f"{SITE}/wp-json/filebird/public/v1/folder/set-attachment",
    headers=H,
    json={"folder_id": 1, "attachment_ids": [test_id]},
    timeout=15,
)
print(f"Public API test (ID {test_id}): HTTP {r2.status_code}")
if r2.status_code != 200:
    print(f"  Error: {r2.text[:200]}")

# If public API failed, try fetching with WP nonce
if r2.status_code != 200:
    print("\nTrying with nonce...")
    # Get nonce from admin
    r3 = requests.get(f"{SITE}/wp-admin/admin-ajax.php", headers=H, timeout=10)
    print(f"  Admin AJAX: HTTP {r3.status_code}")
