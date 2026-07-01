#!/usr/bin/env python3
"""
Google Analytics Data API — Fetch metrics for fracktal.in.

Auth: OAuth 2.0 Desktop App (credentials.json → token.json)
Uses: GOOGLE_ANALYTICS_PROPERTY_ID from .env

Usage:
    python fetch_analytics.py                     # Last 30 days summary
    python fetch_analytics.py --days 90           # Last 90 days
    python fetch_analytics.py --metric activeUsers,sessions,bounceRate
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

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

# ── Auth ──────────────────────────────────────────────────────────

def get_credentials():
    """OAuth 2.0 flow — reuses token.json, prompts browser if needed."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "token_ga.json")
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

# ── GA4 API ───────────────────────────────────────────────────────

def run_report(property_id, start_date, end_date, metrics, dimensions=None):
    """Fetch a GA4 report."""
    creds = get_credentials()
    if not creds:
        return None

    service = build("analyticsdata", "v1beta", credentials=creds)

    request_body = {
        "dateRanges": [{"startDate": start_date, "endDate": end_date}],
        "metrics": [{"name": m} for m in metrics],
    }
    if dimensions:
        request_body["dimensions"] = [{"name": d} for d in dimensions]

    try:
        response = service.properties().runReport(
            property=f"properties/{property_id}",
            body=request_body,
        ).execute()
        return response
    except Exception as e:
        print(f"❌ GA API error: {e}")
        return None


def print_report(response, title="Google Analytics Report"):
    """Pretty-print a GA4 report response."""
    if not response:
        return

    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

    # Print headers
    headers = []
    for dim in response.get("dimensionHeaders", []):
        headers.append(dim.get("name", "?"))
    for met in response.get("metricHeaders", []):
        headers.append(met.get("name", "?"))

    print(f"  {' | '.join(h.ljust(20) for h in headers)}")
    print(f"  {'-'*60}")

    for row in response.get("rows", []):
        vals = []
        for dv in row.get("dimensionValues", []):
            vals.append(dv.get("value", "-"))
        for mv in row.get("metricValues", []):
            vals.append(mv.get("value", "-"))
        print(f"  {' | '.join(v.ljust(20) for v in vals)}")

    # Totals
    if "rowCount" in response:
        print(f"\n  Total rows: {response['rowCount']}")


# ── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch Google Analytics 4 data")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument(
        "--property-id",
        help="GA4 Property ID (default: from GOOGLE_ANALYTICS_PROPERTY_ID env)",
    )
    parser.add_argument(
        "--metric",
        default="activeUsers,sessions,screenPageViews,bounceRate,averageSessionDuration",
        help="Comma-separated metric names",
    )
    parser.add_argument(
        "--dimension",
        default="date",
        help="Comma-separated dimension names (e.g. date, pagePath, deviceCategory)",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    property_id = args.property_id or os.getenv("GOOGLE_ANALYTICS_PROPERTY_ID")
    if not property_id:
        print("❌ GOOGLE_ANALYTICS_PROPERTY_ID not set in .env or --property-id")
        print("   Find it in GA4 Admin → Property Settings → Property ID")
        sys.exit(1)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    metrics = [m.strip() for m in args.metric.split(",")]
    dimensions = [d.strip() for d in args.dimension.split(",")] if args.dimension else None

    print(f"📊 Fetching GA4 data: {start_date} → {end_date}")
    print(f"   Property: {property_id}")
    print(f"   Metrics: {', '.join(metrics)}")

    response = run_report(property_id, start_date, end_date, metrics, dimensions)

    if not response:
        sys.exit(1)

    if args.json:
        print(json.dumps(response, indent=2))
    else:
        print_report(response)


if __name__ == "__main__":
    main()
