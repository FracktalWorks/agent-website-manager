"""Fix favicon and submit to Google."""
import requests
import base64
import io
import os
from PIL import Image
from pathlib import Path

AUTH = base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H = {'Authorization': 'Basic ' + AUTH}
H_JSON = {'Authorization': 'Basic ' + AUTH, 'Content-Type': 'application/json'}
API = 'https://fracktal.in/wp-json/wp/v2'
SITE = 'https://fracktal.in'

# ═══════════════════════════════════════════════════════════
# 1. FAVICON FIX
# ═══════════════════════════════════════════════════════════
print("=== FAVICON FIX ===")

# Get current site icon
r = requests.get(f'{API}/settings', headers=H, timeout=15)
settings = r.json()
current_icon_id = settings.get('site_icon', 0)
print(f"Current site icon ID: {current_icon_id}")

# Get the icon image URL
if current_icon_id:
    r_icon = requests.get(f'{API}/media/{current_icon_id}', headers=H, timeout=15)
    if r_icon.status_code == 200:
        icon_data = r_icon.json()
        icon_url = icon_data.get('source_url', '')
        print(f"Icon URL: {icon_url}")

# Download the current icon PNG
r_img = requests.get(icon_url, timeout=15)
if r_img.status_code == 200:
    img = Image.open(io.BytesIO(r_img.content))
    print(f"Image size: {img.size}, mode: {img.mode}")
    
    # Convert to .ico format (32x32)
    img_resized = img.resize((32, 32), Image.LANCZOS)
    if img_resized.mode != 'RGBA':
        img_resized = img_resized.convert('RGBA')
    
    ico_buffer = io.BytesIO()
    img_resized.save(ico_buffer, format='ICO', sizes=[(32, 32)])
    ico_buffer.seek(0)
    
    # Upload as new media item
    files = {
        'file': ('favicon.ico', ico_buffer, 'image/x-icon'),
    }
    r_upload = requests.post(
        f'{API}/media',
        headers={'Authorization': 'Basic ' + AUTH},
        files=files,
        timeout=30)
    
    if r_upload.status_code in [200, 201]:
        new_media = r_upload.json()
        new_id = new_media['id']
        new_url = new_media.get('source_url', '')
        print(f"Uploaded favicon.ico: ID={new_id}")
        print(f"URL: {new_url}")
        
        # Set as site icon
        r_set = requests.post(
            f'{API}/settings',
            headers=H_JSON,
            json={'site_icon': new_id},
            timeout=15)
        print(f"Set as site icon: {r_set.status_code}")
    else:
        print(f"Upload failed: {r_upload.status_code}")
        print(r_upload.text[:300])
else:
    print(f"Failed to download icon: {r_img.status_code}")

# Verify
print("\nVerifying favicon...")
r_fav = requests.head(f'{SITE}/favicon.ico', allow_redirects=True, timeout=10)
print(f"favicon.ico status: {r_fav.status_code}")

# Also check the WordPress site icon URL
r_settings2 = requests.get(f'{API}/settings', headers=H, timeout=15)
s2 = r_settings2.json()
print(f"site_icon: {s2.get('site_icon')}")
print(f"site_icon_url: {s2.get('site_icon_url', 'N/A')}")
