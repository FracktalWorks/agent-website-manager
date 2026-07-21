"""Submit sitemap to Google Search Console and request indexing."""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add .tmp/scripts to path
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '.tmp', 'scripts'))

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly",
          "https://www.googleapis.com/auth/webmasters"]

SITE_URL = os.getenv("GOOGLE_SEARCH_CONSOLE_SITE", "https://fracktal.in/")
SITE_URL = SITE_URL.rstrip('/') + '/'

def get_creds():
    """Get GSC credentials."""
    token_path = os.path.join(
        os.path.dirname(__file__), '..', '.tmp', 'scripts', 'token_gsc.json')
    
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("❌ Need to re-authenticate. Run fetch_search_console.py first.")
            return None
    return creds

print("=== GOOGLE SEARCH CONSOLE SUBMISSION ===")
creds = get_creds()
if not creds:
    sys.exit(1)

service = build("webmasters", "v3", credentials=creds)
site = SITE_URL.replace('https://', 'sc-domain:').rstrip('/')

print(f"Site: {SITE_URL}")
print(f"GSC identifier: {site}")

# 1. Submit sitemap
print("\n--- 1. Submit Sitemap ---")
sitemaps_to_submit = [
    f'{SITE_URL}sitemap_index.xml',
    f'{SITE_URL}page-sitemap.xml',
    f'{SITE_URL}post-sitemap.xml',
]

for sitemap_url in sitemaps_to_submit:
    try:
        service.sitemaps().submit(
            siteUrl=site,
            feedpath=sitemap_url,
        ).execute()
        print(f"  ✅ Submitted: {sitemap_url}")
    except Exception as e:
        err = str(e)
        if 'already' in err.lower() or 'duplicate' in err.lower():
            print(f"  ⚠️ Already submitted: {sitemap_url}")
        else:
            print(f"  ❌ Error: {sitemap_url} - {err[:150]}")

# 2. Check existing sitemaps
print("\n--- 2. Sitemap Status ---")
try:
    sitemaps_list = service.sitemaps().list(siteUrl=site).execute()
    for sm in sitemaps_list.get('sitemap', []):
        path = sm.get('path', '?')
        last_submitted = sm.get('lastSubmitted', '?')
        warnings = sm.get('warnings', 0)
        errors = sm.get('errors', 0)
        print(f"  {path}: submitted={last_submitted} warnings={warnings}"
              f" errors={errors}")
except Exception as e:
    print(f"  Could not list sitemaps: {e}")

# 3. Request indexing of homepage + key pages
print("\n--- 3. Request Indexing ---")
key_urls = [
    SITE_URL,
    f'{SITE_URL}carbon-fiber-nylon/',
    f'{SITE_URL}abs-acrylonitrile-butadiene-styrene/',
    f'{SITE_URL}nylon/',
    f'{SITE_URL}3d-printing-services/',
    f'{SITE_URL}3d-printer-manufacturer-india/',
    f'{SITE_URL}snowflake/',
    f'{SITE_URL}twindragon/',
]

for url in key_urls:
    try:
        # Check current indexing status
        request_body = {
            'url': url,
        }
        # Note: URL Inspection API may require different scopes
        # For now, just request via the URL Notifications API
        service.urlNotifications().publish(
            siteUrl=site,
            body={'url': url, 'type': 'URL_UPDATED'},
        ).execute()
        print(f"  ✅ Indexing requested: {url}")
    except Exception as e:
        err = str(e)
        if '403' in err or 'permission' in err.lower():
            print(f"  ⚠️ Need verify ownership: {url}")
        elif 'not found' in err.lower():
            print(f"  ⚠️ URL Notification API not available: {url}")
        else:
            print(f"  ⚠️ {url}: {err[:100]}")

# 4. Recent crawl stats
print("\n--- 4. Recent Search Performance ---")
from datetime import datetime, timedelta
try:
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = service.searchanalytics().query(
        siteUrl=site,
        body={
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['date'],
            'rowLimit': 7,
        },
    ).execute()
    
    rows = response.get('rows', [])
    total_clicks = sum(r.get('clicks', 0) for r in rows)
    total_impressions = sum(r.get('impressions', 0) for r in rows)
    print(f"  Last 7 days: {total_clicks} clicks, {total_impressions} impressions")
except Exception as e:
    print(f"  Could not fetch: {e}")

print("\n✅ Google Search Console submission complete!")
