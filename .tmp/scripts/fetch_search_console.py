#!/usr/bin/env python3
"""
Google Search Console API — Fetch search performance for fracktal.in.

Auth: OAuth 2.0 Desktop App (credentials.json → token.json)
Uses: GOOGLE_SEARCH_CONSOLE_SITE from .env

Usage:
    python fetch_search_console.py                    # Last 30 days top queries
    python fetch_search_console.py --days 90          # Last 90 days
    python fetch_search_console.py --dimension page   # Top pages
    python fetch_search_console.py --dimension query  # Top queries (default)
    python fetch_search_console.py --dimension country
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# ── Auth ──────────────────────────────────────────────────────────

def get_credentials():
    """OAuth 2.0 flow — reuses token_gsc.json, prompts browser if needed."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "token_gsc.json")
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print(f"❌ OAuth credentials not found at: {creds_path}")
                print("   Download OAuth 2.0 Client ID JSON from Google Cloud Console")
                print("   and save it as .tmp/credentials.json")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

# ── GSC API ───────────────────────────────────────────────────────

def fetch_search_analytics(site_url, start_date, end_date, dimensions=None, row_limit=25):
    """Query the Search Console Search Analytics API."""
    creds = get_credentials()
    if not creds:
        return None

    service = build("webmasters", "v3", credentials=creds)

    request_body = {
        "startDate": start_date,
        "endDate": end_date,
        "rowLimit": row_limit,
    }
    if dimensions:
        request_body["dimensions"] = dimensions

    try:
        response = service.searchanalytics().query(
            siteUrl=site_url, body=request_body
        ).execute()
        return response
    except Exception as e:
        print(f"❌ GSC API error: {e}")
        return None


def print_results(response, title="Search Console Report"):
    """Pretty-print GSC results."""
    if not response:
        return

    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

    rows = response.get("rows", [])
    if not rows:
        print("  No data found for this period.")
        return

    # Figure out which dimensions we have
    keys = list(rows[0]["keys"])
    header = " | ".join(k.ljust(30) for k in keys)
    header += " | Clicks | Impressions | CTR    | Position"
    print(f"  {header}")
    print(f"  {'-'*65}")

    for row in rows:
        vals = " | ".join(k.ljust(30) for k in row["keys"])
        vals += f" | {row['clicks']:>6} | {row['impressions']:>11} | {row['ctr']*100:>5.1f}% | {row['position']:>7.1f}"
        print(f"  {vals}")

    print(f"\n  Total rows: {len(rows)}")


# ── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch Google Search Console data")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument(
        "--site",
        help="Site URL in GSC (default: from GOOGLE_SEARCH_CONSOLE_SITE env)",
    )
    parser.add_argument(
        "--dimension",
        default="query",
        help="Dimension: query, page, country, device, searchAppearance (or comma-sep combo)",
    )
    parser.add_argument("--limit", type=int, default=25, help="Max rows to return")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    site_url = args.site or os.getenv("GOOGLE_SEARCH_CONSOLE_SITE")
    if not site_url:
        print("❌ GOOGLE_SEARCH_CONSOLE_SITE not set in .env or --site")
        print("   This should be the exact URL as it appears in Search Console")
        print("   (e.g. 'sc_domain:fracktal.in' for domain property, or 'https://fracktal.in/')")
        sys.exit(1)

    # Normalize: if just a domain, prefix with sc_domain: for domain properties
    if not site_url.startswith("http") and not site_url.startswith("sc_"):
        site_url = f"sc_domain:{site_url}"

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    dimensions = [d.strip() for d in args.dimension.split(",")]

    print(f"🔍 Fetching GSC data: {start_date} → {end_date}")
    print(f"   Site: {site_url}")
    print(f"   Dimension: {', '.join(dimensions)}")

    response = fetch_search_analytics(site_url, start_date, end_date, dimensions, args.limit)

    if not response:
        sys.exit(1)

    if args.json:
        print(json.dumps(response, indent=2))
    else:
        print_results(response)


if __name__ == "__main__":
    main()
