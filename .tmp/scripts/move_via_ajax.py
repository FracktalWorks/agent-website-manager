"""Move files to FileBird folders using session auth + admin AJAX."""
import requests, re, os
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")

# Login
session = requests.Session()
r = session.post(
    f"{SITE}/wp-login.php",
    data={"log": USER, "pwd": PW, "rememberme": "forever"},
    timeout=15,
    allow_redirects=True,
)
print(f"Login: HTTP {r.status_code}, cookies: {len(session.cookies)}")

# Get upload page for nonce
r2 = session.get(f"{SITE}/wp-admin/upload.php", timeout=15)

# Extract nonce from the page
nonce = None
patterns = [
    r'"filebird_nonce"\s*:\s*"([a-f0-9]+)"',
    r"filebird_nonce\s*=\s*'([a-f0-9]+)'",
    r'filebird_nonce["\s=]+"([a-f0-9]+)"',
    r'"_ajax_nonce"\s*:\s*"([a-f0-9]+)"',
]
for pat in patterns:
    m = re.search(pat, r2.text)
    if m:
        nonce = m.group(1)
        print(f"Found nonce via pattern: {pat[:50]}... -> {nonce[:16]}")
        break

if not nonce:
    # Try to get nonce from the REST API headers
    print("Trying REST API nonce...")
    r3 = session.get(f"{SITE}/wp-json/filebird/v1/get-folders", timeout=10)
    nonce = r3.headers.get("X-WP-Nonce", "")
    if nonce:
        print(f"REST nonce: {nonce[:16]}")
    else:
        print("No nonce found anywhere. Cannot move files.")
        exit(1)

# Move file
test_id = 31405
folder_id = 1

# Try different AJAX actions
actions = [
    {
        "action": "filebird_ajax_set_folder",
        "nonce": nonce,
        "ids[]": test_id,
        "folder": folder_id,
    },
    {
        "action": "filebird_set_folder",
        "nonce": nonce,
        "ids": str(test_id),
        "folder": str(folder_id),
    },
    {
        "action": "fbv_set_folder",
        "_ajax_nonce": nonce,
        "ids": [test_id],
        "folder": folder_id,
    },
]

for i, data in enumerate(actions):
    r = session.post(
        f"{SITE}/wp-admin/admin-ajax.php",
        data=data,
        timeout=15,
    )
    print(f"Attempt {i+1} ({data['action']}): HTTP {r.status_code} — {r.text[:150]}")
