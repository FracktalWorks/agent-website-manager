"""Move all images by author 4144 (Kiran Kumar) to Fracktal Care folder."""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
AUTHOR_ID = 4144
FOLDER_ID = 1  # Fracktal Care

# Fetch all media by this author
media = []
page = 1
while True:
    r = requests.get(
        f"{SITE}/wp-json/wp/v2/media?author={AUTHOR_ID}&per_page=100&page={page}",
        headers=H, timeout=30,
    )
    if r.status_code != 200 or not r.json():
        break
    items = r.json()
    media.extend(items)
    if len(items) < 100:
        break
    page += 1

print("Images by Kiran Kumar (author 4144):", len(media))
for m in media:
    title = m.get("title", {}).get("rendered", "N/A")
    url = m.get("source_url", "")
    mime = m.get("mime_type", "")
    mid = m["id"]
    print(f"  ID {mid}: [{mime}] {title[:60]}")

if not media:
    print("No images found for this author.")
    exit()

# Move to Fracktal Care folder
ids = [m["id"] for m in media]
r = requests.post(
    f"{SITE}/wp-json/filebird/public/v1/folder/set-attachment",
    headers=H,
    json={"folder_id": FOLDER_ID, "attachment_ids": ids},
    timeout=30,
)
print(f"\nMove {len(ids)} items to Fracktal Care folder (ID {FOLDER_ID}):")
print(f"  HTTP {r.status_code}")
if r.status_code == 200:
    print("  Done! Refresh Media > Library to see them in the folder.")
else:
    print(f"  {r.text[:200]}")
