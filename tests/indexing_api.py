"""Use Google Indexing API to request immediate indexing of key pages."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '.tmp', 'scripts'))

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/indexing",
]

# Auth
token_path = os.path.join(
    os.path.dirname(__file__), '..', '.tmp', 'scripts', 'token_gsc.json')
creds = Credentials.from_authorized_user_file(token_path, SCOPES)
if creds.expired:
    creds.refresh(Request())

# Phase 1 + key pages
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

print("=== GOOGLE INDEXING API — URL NOTIFICATIONS ===")
try:
    service = build('indexing', 'v3', credentials=creds)
    
    for url in urls:
        try:
            resp = service.urlNotifications().publish(
                body={
                    'url': url,
                    'type': 'URL_UPDATED',
                }
            ).execute()
            notified = resp.get('urlNotificationMetadata', {}).get(
                'latestUpdate', {}).get('notifyTime', 'unknown')
            print(f"  ✅ {url.split('/')[-2] or 'homepage'}")
            print(f"     Notified at: {notified}")
        except Exception as e:
            err = str(e)
            if '403' in err:
                print(f"  ❌ PERMISSION DENIED: {url}")
                print(f"     Indexing API requires service account added")
                print(f"     as owner in Google Search Console.")
                break
            elif '404' in err or 'not found' in err.lower():
                print(f"  ❌ API not enabled: Indexing API needs to be")
                print(f"     enabled in Google Cloud Console.")
                print(f"     Go to: https://console.cloud.google.com/apis/")
                print(f"     library/indexing.googleapis.com")
                break
            else:
                print(f"  ⚠️ {url}: {err[:120]}")
    
except Exception as e:
    print(f"  ❌ Build error: {e}")

print("\n✅ Attempted indexing for {len(urls)} URLs")
