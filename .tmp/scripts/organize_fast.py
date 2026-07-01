"""Targeted media organization — only categorized items, fast execution."""
import requests, base64, os, re, time
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

PATTERNS = {
    "snowflake": "Snowflake 3D Printer",
    "julia": "Julia 3D Printer",
    "twindragon|twin.dragon|td.600|td600": "Twin Dragon 3D Printer",
    "volterra": "Volterra 3D Printer",
    "apollo|sls": "Apollo SLS 3D Printer",
    "printstick|print.stick": "PrintStick",
    "filament.dryer|material.dryer|dryer": "Material Dryer",
    "all.printers|7.machines": "Fracktal 3D Printer Lineup",
    "hero.image.with.printers": "Fracktal Hero Image",
    "holding.3d": "Fracktal Founders",
    "fracktal.blog": "Fracktal Blog Cover",
    "abs|acrylonitrile": "ABS Material",
    "pla|polylactic": "PLA Material",
    "nylon": "Nylon Material",
    "tpu|thermoplastic": "TPU Material",
    "pet.g|petg": "PET-G Material",
    "carbon.fiber": "Carbon Fiber Nylon Material",
    "pva|polyvinyl": "PVA Material",
    "pc.polycarbonate": "Polycarbonate Material",
}


def fetch_all_media():
    media = []
    page = 1
    while True:
        r = requests.get(
            f"{SITE}/wp-json/wp/v2/media?per_page=100&page={page}",
            headers=H, timeout=60,
        )
        if r.status_code != 200 or not r.json():
            break
        media.extend(r.json())
        if len(r.json()) < 100:
            break
        page += 1
    return media


def normalize_filename(url):
    name = os.path.basename((url or "").lower())
    name = re.sub(r"[-_\d]+", ".", name)
    name = re.sub(r"\.+", ".", name)
    return name


def clean_title_from_url(url):
    name = os.path.basename((url or ""))
    name = re.sub(r"\.[^.]+$", "", name)
    name = re.sub(r"[-_]\d+x\d+.*", "", name)
    name = re.sub(r"[-_](scaled|compressed|processed|e\d+).*", "", name, flags=re.I)
    name = re.sub(r"[-_]+", " ", name).strip().title()
    return name


print("Fetching media...")
media = fetch_all_media()
print(f"Total: {len(media)} items")

titles_done = 0
alts_done = 0
skipped = 0

for item in media:
    filename = normalize_filename(item.get("source_url", ""))
    matched_label = None
    for pattern, label in PATTERNS.items():
        if re.search(pattern, filename, re.I):
            matched_label = label
            break

    if not matched_label:
        skipped += 1
        continue

    mid = item["id"]
    orig = clean_title_from_url(item.get("source_url", ""))
    new_title = f"{matched_label} \u2014 {orig}"[:100]
    old_title = item.get("title", {}).get("rendered", "")

    # Update title if different
    if new_title != old_title:
        try:
            r = requests.post(
                f"{SITE}/wp-json/wp/v2/media/{mid}",
                headers=H, json={"title": new_title}, timeout=15,
            )
            if r.status_code == 200:
                titles_done += 1
        except Exception:
            pass

    # Add alt text if missing
    if not item.get("alt_text") and "image" in item.get("mime_type", ""):
        try:
            r = requests.post(
                f"{SITE}/wp-json/wp/v2/media/{mid}",
                headers=H, json={"alt_text": matched_label}, timeout=15,
            )
            if r.status_code == 200:
                alts_done += 1
        except Exception:
            pass

    if titles_done % 50 == 0 and titles_done > 0:
        print(f"  {titles_done} titles updated...")
        time.sleep(0.3)

print(f"\nDone! {titles_done} titles updated, {alts_done} alt texts added")
print(f"Skipped {skipped} uncategorized items (safe to handle later)")
