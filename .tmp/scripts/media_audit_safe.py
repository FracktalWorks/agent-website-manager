#!/usr/bin/env python3
"""
Safe media library audit — read-only, no changes.
Reports: total count, total size, unused images, oversized images, missing alt text.
"""
import requests, base64, os, json
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}
API = f"{SITE}/wp-json/wp/v2"


def fetch_all(endpoint, params=None):
    """Paginate through all results."""
    results = []
    page = 1
    while True:
        p = {"per_page": 100, "page": page}
        if params:
            p.update(params)
        r = requests.get(f"{API}/{endpoint}", headers=headers, params=p)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


# ── Fetch all media ──
print("Fetching media library...")
media = fetch_all("media")
total_media = len(media)
def safe_filesize(item):
    """Get filesize as int, handling string values from API."""
    size = item.get("media_details", {}) or {}
    val = size.get("filesize", 0) or 0
    return int(val)

total_size = sum(safe_filesize(item) for item in media)
print(f"Total media items: {total_media}")
print(f"Total storage: {total_size / 1024 / 1024:.1f} MB")
print()

# ── By type ──
by_type = defaultdict(lambda: {"count": 0, "size": 0})
for item in media:
    mtype = item.get("mime_type", "unknown").split("/")[1] if "/" in item.get("mime_type", "") else "unknown"
    by_type[mtype]["count"] += 1
    by_type[mtype]["size"] += safe_filesize(item)

print("By format:")
for fmt, info in sorted(by_type.items(), key=lambda x: x[1]["size"], reverse=True):
    print(f"  {fmt:10s}: {info['count']:>4} files, {info['size']/1024/1024:>7.1f} MB")
print()

# ── Oversized (>500KB) ──
oversized = [
    (item["id"], item["title"]["rendered"], safe_filesize(item))
    for item in media
    if safe_filesize(item) > 500 * 1024
]
oversized.sort(key=lambda x: x[2], reverse=True)
print(f"Oversized images (>500KB): {len(oversized)}")
for mid, name, size in oversized[:15]:
    print(f"  ID {mid:>6}: {size/1024/1024:>6.1f} MB — {name[:60]}")
print()

# ── Missing alt text ──
missing_alt = [
    (item["id"], item["title"]["rendered"])
    for item in media
    if not item.get("alt_text") and "image" in item.get("mime_type", "")
]
print(f"Images missing alt text: {len(missing_alt)}")
if missing_alt:
    print(f"  First 10: {', '.join(str(m[0]) for m in missing_alt[:10])}")
print()

# ── Check which media are used in pages/posts ──
print("Checking media usage in content...")
all_pages = fetch_all("pages", {"status": "publish,draft"})
all_pages += fetch_all("posts", {"status": "publish,draft"})

used_ids = set()
# Check content + excerpt for media URLs
for page in all_pages:
    content = page.get("content", {}).get("rendered", "")
    excerpt = page.get("excerpt", {}).get("rendered", "")
    combined = content + " " + excerpt
    # Check for each media ID
    for item in media:
        mid = item["id"]
        url = item.get("source_url", "")
        if url and url in combined:
            used_ids.add(mid)
        # Also check attachment ID in wp-content/uploads path
        if f"wp-content/uploads/" in combined and str(mid) not in used_ids:
            # Check if the image filename appears in content
            filename = url.split("/")[-1] if url else ""
            if filename and filename in combined:
                used_ids.add(mid)

# Check featured images
for page in all_pages:
    fid = page.get("featured_media")
    if fid:
        used_ids.add(fid)

# Check _elementor_data for media references
print("Checking Elementor data...")
for page in all_pages:
    elem_data = page.get("meta", {}).get("_elementor_data", "")
    if elem_data and isinstance(elem_data, str) and len(elem_data) > 10:
        for item in media:
            mid = item["id"]
            if str(mid) in elem_data:
                used_ids.add(mid)
            url = item.get("source_url", "")
            if url and url in elem_data:
                used_ids.add(mid)

used_count = len(used_ids)
unused = [item for item in media if item["id"] not in used_ids]
print(f"Media used in content: {used_count}")
print(f"Potentially unused: {len(unused)}")
if unused:
    unused.sort(key=lambda x: safe_filesize(x), reverse=True)
    unused_size = sum(safe_filesize(u) for u in unused)
    print(f"Unused storage: {unused_size / 1024 / 1024:.1f} MB")
    print("Top 10 unused by size:")
    for item in unused[:10]:
        size = safe_filesize(item)
        print(f"  ID {item['id']:>6}: {size/1024/1024:>6.1f} MB — {item['title']['rendered'][:60]}")

# Save report
report = {
    "total_media": total_media,
    "total_size_mb": round(total_size / 1024 / 1024, 1),
    "by_type": {
        k: {"count": v["count"], "size_mb": round(v["size"]/1024/1024, 1)}
        for k, v in by_type.items()
    },
    "oversized_count": len(oversized),
    "missing_alt_count": len(missing_alt),
    "used_count": used_count,
    "unused_count": len(unused),
    "unused_size_mb": round(
        sum(safe_filesize(u) for u in unused) / 1024 / 1024, 1
    ),
    "unused_ids": [u["id"] for u in unused],
}
with open("outputs/_memory/media_audit.json", "w") as f:
    json.dump(report, f, indent=2)
print(f"\nReport saved to outputs/_memory/media_audit.json")
