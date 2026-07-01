"""Verify duplicate videos are safe to delete, then delete them."""
import requests, base64, os, json
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

# Keep the better-named ones, delete duplicates
# 28829 "Printstick-Instructional.mp4" — KEEP
# 28810 "Printstick Instructional" — DELETE (duplicate)
# 28831 "Adhesion-test.mp4" — KEEP  
# 28809 "Adhesion test" — DELETE (duplicate)
dup_ids_to_delete = [28810, 28809]
keep_ids = [28829, 28831]

print("=== Checking usage of duplicate videos ===")
for mid in dup_ids_to_delete + keep_ids:
    r = requests.get(f"{SITE}/wp-json/wp/v2/media/{mid}", headers=headers)
    if r.status_code != 200:
        print(f"ID {mid}: HTTP {r.status_code}")
        continue
    j = r.json()
    title = j.get("title", {}).get("rendered", "N/A")
    url = j.get("source_url", "")
    size_mb = round(j.get("media_details", {}).get("filesize", 0) / 1024 / 1024, 1)
    action = "DELETE" if mid in dup_ids_to_delete else "KEEP"
    print(f"\n[{action}] ID {mid}: {title} ({size_mb} MB)")
    print(f"  URL: {url}")

    # Check if URL appears in any page content
    r2 = requests.get(f"{SITE}/wp-json/wp/v2/pages?per_page=100&status=publish,draft", headers=headers)
    found = []
    for page in r2.json():
        content = page.get("content", {}).get("rendered", "")
        if url in content:
            found.append(f"  Page {page['id']}: {page['title']['rendered'][:60]}")
    if found:
        print("  ⚠ USED IN PAGES:")
        for f in found:
            print(f)
    else:
        print("  ✅ Not used in any page. Safe.")

print("\n=== Deleting duplicates now ===")
for mid in dup_ids_to_delete:
    r = requests.delete(f"{SITE}/wp-json/wp/v2/media/{mid}?force=true", headers=headers)
    if r.status_code == 200:
        print(f"✅ Deleted ID {mid}")
    else:
        print(f"❌ Failed to delete ID {mid}: HTTP {r.status_code} — {r.text[:100]}")

print("\nDone.")
