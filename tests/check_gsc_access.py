"""Try both domain and URL-prefix GSC properties."""
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/indexing']
KEY_PATH = Path(__file__).parent.parent / '.tmp' / 'scripts' / 'service-account.json'

creds = service_account.Credentials.from_service_account_file(
    str(KEY_PATH), scopes=SCOPES)

# First check which property we have access to
from googleapiclient.discovery import build as build2
wmt = build2('webmasters', 'v3', credentials=creds)

print("=== CHECKING PROPERTY ACCESS ===")
try:
    sites = wmt.sites().list().execute()
    for s in sites.get('siteEntry', []):
        url = s.get('siteUrl', '?')
        level = s.get('permissionLevel', '?')
        print(f"  {url} -> {level}")
except Exception as e:
    print(f"  List error: {e}")

# Try domain property
try:
    wmt.sitemaps().list(siteUrl='sc-domain:fracktal.in').execute()
    print("  ✅ Domain property accessible")
except Exception as e:
    print(f"  Domain property: {str(e)[:100]}")

# Try URL-prefix property  
try:
    wmt.sitemaps().list(siteUrl='https://fracktal.in/').execute()
    print("  ✅ URL-prefix property accessible")
except Exception as e:
    print(f"  URL-prefix: {str(e)[:100]}")
