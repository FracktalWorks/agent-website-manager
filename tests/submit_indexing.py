"""Submit URLs for instant indexing via Google Indexing API."""
import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/indexing']
KEY_PATH = Path(__file__).parent.parent / '.tmp' / 'scripts' / 'service-account.json'

if not KEY_PATH.exists():
    print("❌ Service account key not found at:", KEY_PATH)
    exit(1)

creds = service_account.Credentials.from_service_account_file(
    str(KEY_PATH), scopes=SCOPES)
service = build('indexing', 'v3', credentials=creds)

urls = [
    'https://fracktal.in/',
    'https://fracktal.in/carbon-fiber-nylon/',
    'https://fracktal.in/abs-acrylonitrile-butadiene-styrene/',
    'https://fracktal.in/pet-g-polyethylene-terephthalate-glycol/',
    'https://fracktal.in/tpu-thermoplastic-polyurethane/',
    'https://fracktal.in/nylon/',
    'https://fracktal.in/pva-polyvinyl-alcohol/',
    'https://fracktal.in/3d-printing-services/',
    'https://fracktal.in/consulting-services/',
    'https://fracktal.in/materialdryer/',
    'https://fracktal.in/vaccum-casting/',
    'https://fracktal.in/snowflake/',
    'https://fracktal.in/twindragon/',
    'https://fracktal.in/3d-printer-manufacturer-india/',
]

print("=== GOOGLE INDEXING API — SUBMITTING URLs ===")
success = 0
failed = 0

for url in urls:
    label = url.split('/')[-2] or 'homepage'
    try:
        resp = service.urlNotifications().publish(
            body={'url': url, 'type': 'URL_UPDATED'}
        ).execute()
        notify_time = resp.get('urlNotificationMetadata', {}).get(
            'latestUpdate', {}).get('notifyTime', 'now')
        print(f"  ✅ {label}")
        success += 1
    except Exception as e:
        err = str(e)
        if '403' in err or 'permission' in err.lower():
            print(f"  ❌ {label}: Permission denied")
            print(f"     Add this email as Owner in GSC:")
            with open(KEY_PATH) as f:
                key_data = json.load(f)
            print(f"     {key_data.get('client_email', 'unknown')}")
            break
        else:
            print(f"  ⚠️ {label}: {err[:100]}")
            failed += 1

print(f"\n✅ Submitted: {success} | ❌ Failed: {failed} | Total: {len(urls)}")

if success > 0:
    print("Google will crawl these pages within minutes to hours!")
