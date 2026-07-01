"""Try multiple approaches to move files to FileBird folders."""
import requests, base64, os, json
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

test_ids = [31405, 31404, 31403]
formats = [
    {"ids": test_ids, "folder": 1},
    {"ids": test_ids, "folder": "1"},
    {"attachment_ids": test_ids, "folder_id": 1},
    {"ids": test_ids, "folder": {"id": 1}},
    {"data": json.dumps({"ids": test_ids, "folder": 1})},
]

print("=== Trying different move formats ===")
for i, fmt in enumerate(formats):
    r = requests.post(
        f"{SITE}/wp-json/filebird/v1/pt-set-folder",
        headers=H, json=fmt, timeout=10,
    )
    body = r.json() if r.text else {}
    print(f"Format {i+1}: HTTP {r.status_code} -> {body}")

# Refresh counter
print("\n=== Refreshing counter ===")
r = requests.get(
    f"{SITE}/wp-json/filebird/v1/set-folder-counter",
    headers=H, timeout=10,
)
print(f"Counter: HTTP {r.status_code} -> {r.json()}")

# Check
print("\n=== Folder contents ===")
r = requests.get(f"{SITE}/wp-json/filebird/v1/get-folders", headers=H, timeout=10)
tree = r.json().get("tree", [])
for f in tree:
    fid = f.get("id", "?")
    title = f.get("title", "?")
    count = f.get("data-count", 0)
    print(f"  [{fid}] {title}: {count} files")
