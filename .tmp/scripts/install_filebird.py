"""Install FileBird media library folder plugin."""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()
SITE = os.getenv("WORDPRESS_SITE_URL")
USER = os.getenv("WORDPRESS_USERNAME")
PW = os.getenv("WORDPRESS_APP_PASSWORD")
auth = base64.b64encode(f"{USER}:{PW}".encode()).decode()
H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

slug = "filebird"
print(f"Installing {slug}...")

# Try installing
r = requests.post(
    f"{SITE}/wp-json/wp/v2/plugins",
    headers=H, json={"slug": slug, "status": "active"}, timeout=30,
)

if r.status_code == 201:
    print("FileBird installed and activated!")
    print("Go to Media > Library — folder tree appears on the left.")
elif r.status_code == 400:
    data = r.json()
    msg = str(data).lower()
    if "already" in msg:
        print("Already installed, activating...")
        r2 = requests.get(
            f"{SITE}/wp-json/wp/v2/plugins?search={slug}",
            headers=H, timeout=15,
        )
        for p in r2.json():
            pname = str(p.get("textdomain", "") + p.get("name", "")).lower()
            if slug in pname:
                plugin_path = p.get("plugin", "")
                r3 = requests.put(
                    f"{SITE}/wp-json/wp/v2/plugins/{plugin_path}",
                    headers=H, json={"status": "active"}, timeout=15,
                )
                print(f"Activated: HTTP {r3.status_code}")
                break
    else:
        print(f"Error: {r.text[:200]}")
else:
    print(f"HTTP {r.status_code}: {r.text[:200]}")
