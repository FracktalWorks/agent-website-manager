"""Search Console, from the command line.

WHY THIS EXISTS
  Site Kit connects Search Console to WordPress, but it will not tell you the
  things that actually matter after a launch: whether the sitemap was ever
  submitted, how many of the 61 URLs Google has indexed, and whether a given
  page is eligible to appear at all. Those live in the Search Console API, and
  the answers change daily during the first months of a site's life.

  It also owns the one piece of setup Site Kit cannot do: a **Domain property**.
  Site Kit verifies `https://drvarada.com/` — a URL-prefix property, which is
  blind to `http://`, to `www.`, and to any subdomain. A Domain property covers
  every one of them, and is the form Google itself recommends. It can only be
  verified by DNS, so this exposes the TXT record to add and the check to run
  once it has propagated.

AUTH
  OAuth desktop client from GOOGLE_APPLICATION_CREDENTIALS, token cached in
  `.tmp/scripts/token_gsc.json` next to the one the fracktal.in scripts use.
  Sign in as the account that owns the property — vjvarada@gmail.com.

  Note: while the Cloud project's consent screen is in "Testing", Google expires
  refresh tokens after seven days. A `RefreshError: invalid_grant` here means
  exactly that and nothing worse — re-run with `--reauth`. Publishing the
  consent screen removes the expiry.

USAGE
    python searchconsole.py status                 properties, sitemaps, coverage
    python searchconsole.py sitemap                submit sitemap.xml
    python searchconsole.py inspect <url>          is this URL indexed, and why not
    python searchconsole.py coverage               inspect a sample of all 61
    python searchconsole.py domain-token           the DNS TXT record to add
    python searchconsole.py domain-verify          verify + add the Domain property
    python searchconsole.py queries [--days 28]    what the site is being found for
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / ".tmp" / "scripts"))

from google.auth.transport.requests import Request           # noqa: E402
from google.oauth2.credentials import Credentials            # noqa: E402
from google_auth_oauthlib.flow import InstalledAppFlow       # noqa: E402
from googleapiclient.discovery import build                  # noqa: E402
from googleapiclient.errors import HttpError                 # noqa: E402

SITE = "https://drvarada.com/"
DOMAIN = "drvarada.com"
SITEMAP = "https://drvarada.com/sitemap.xml"

# Scopes are requested per command, not all at once.
#
# A consent screen still in "Testing" only grants the scopes it has been
# configured with, and asking for one it does not declare fails the whole flow
# with a bare `access_denied` — which reads exactly like the user clicking
# cancel. These three are known-good: the previous token in this project held
# them. `siteverification` is only needed to create a Domain property, so it is
# requested only by the two commands that do that, and a failure there cannot
# take the everyday commands down with it.
SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/indexing",
]
SCOPES_VERIFY = SCOPES + ["https://www.googleapis.com/auth/siteverification"]

# Commands that need to prove domain ownership; everything else uses SCOPES.
NEEDS_VERIFY = {"domain-token", "domain-verify"}

TOKEN = REPO / ".tmp" / "scripts" / "token_gsc.json"
CLIENT = REPO / ".tmp" / "credentials.json"


def plain(s: str) -> str:
    """Windows consoles are cp1252; an arrow must never crash a report."""
    return s.encode(sys.stdout.encoding or "utf-8", "replace").decode(
        sys.stdout.encoding or "utf-8", "replace")


def out(s: str = "") -> None:
    print(plain(s))


# ── auth ─────────────────────────────────────────────────────────────────────
def credentials(scopes: list[str], reauth: bool = False) -> Credentials:
    creds = None
    if TOKEN.exists() and not reauth:
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN), scopes)
        except Exception:
            creds = None
        # A cached token only helps if it actually carries the scopes this
        # command needs; otherwise the call fails much later with a confusing
        # 403 rather than here, where the fix is obvious.
        if creds and not set(scopes) <= set(creds.scopes or []):
            out("  cached token is missing a scope this command needs "
                "— signing in again")
            creds = None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token and not reauth:
        try:
            creds.refresh(Request())
            TOKEN.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except Exception as ex:
            out(f"  stored token could not be refreshed ({type(ex).__name__}) "
                f"— opening a browser to sign in again")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), scopes)
    out()
    out("  A BROWSER TAB IS OPENING NOW.")
    out("  Sign in as vjvarada@gmail.com and click Allow.")
    out("  If it says the app is blocked or unverified, choose Advanced ->")
    out("  'Go to ... (unsafe)' — that is this project's own OAuth client,")
    out("  and it is unverified only because it was never submitted for review.")
    out()
    creds = flow.run_local_server(port=0, prompt="consent")
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    out(f"  token saved -> {TOKEN}")
    return creds


def resolve_property(sc) -> str:
    """The property to query, discovered rather than assumed.

    Site Kit reports its `propertyID` as `https://drvarada.com/`, which reads
    like a URL-prefix property — but the property this account actually owns is
    `sc-domain:drvarada.com`. Hardcoding either one produces a 403 that looks
    like a permissions problem and is really a naming one, so ask the API.

    A Domain property is preferred where both exist: it is the superset, so a
    sitemap submitted there covers `www.` and `http://` as well.
    """
    entries = [e["siteUrl"] for e in
               sc.sites().list().execute().get("siteEntry", [])]
    for candidate in (f"sc-domain:{DOMAIN}", SITE, SITE.rstrip("/")):
        if candidate in entries:
            return candidate
    raise SystemExit(
        f"  no Search Console property for {DOMAIN} on this account.\n"
        f"  properties visible: {entries or 'none'}")


def services(command: str, reauth: bool = False):
    scopes = SCOPES_VERIFY if command in NEEDS_VERIFY else SCOPES
    c = credentials(scopes, reauth)
    sv = (build("siteVerification", "v1", credentials=c, cache_discovery=False)
          if command in NEEDS_VERIFY else None)
    return build("searchconsole", "v1", credentials=c,
                 cache_discovery=False), sv


# ── commands ─────────────────────────────────────────────────────────────────
def cmd_status(sc, sv, args) -> int:
    out()
    out("  properties this account can see")
    entries = sc.sites().list().execute().get("siteEntry", [])
    if not entries:
        out("    none — the account signed in owns no properties")
    for s in sorted(entries, key=lambda e: e["siteUrl"]):
        mark = " <- this site" if DOMAIN in s["siteUrl"] else ""
        out(f"    {s['permissionLevel']:<22} {s['siteUrl']}{mark}")

    has_domain = any(e["siteUrl"] == f"sc-domain:{DOMAIN}" for e in entries)
    has_prefix = any(e["siteUrl"] == SITE for e in entries)
    out()
    out(f"  URL-prefix property {SITE}   {'present' if has_prefix else 'MISSING'}")
    out(f"  Domain property     sc-domain:{DOMAIN}    "
        f"{'present' if has_domain else 'not set up — see domain-token'}")

    for prop in ([SITE] if has_prefix else []) + (
            [f"sc-domain:{DOMAIN}"] if has_domain else []):
        out()
        out(f"  sitemaps on {prop}")
        try:
            maps = sc.sitemaps().list(siteUrl=prop).execute().get("sitemap", [])
        except HttpError as ex:
            out(f"    could not read ({ex.status_code})")
            continue
        if not maps:
            out("    none submitted — run `python searchconsole.py sitemap`")
        for m in maps:
            n = sum(int(c.get("submitted", 0)) for c in m.get("contents", []))
            out(f"    {m['path']}")
            out(f"      last downloaded {m.get('lastDownloaded', 'never')[:10]}  "
                f"submitted {n}  errors {m.get('errors', 0)}  "
                f"warnings {m.get('warnings', 0)}")
    return 0


def cmd_sitemap(sc, sv, args) -> int:
    prop = resolve_property(sc)
    out()
    try:
        sc.sitemaps().submit(siteUrl=prop, feedpath=SITEMAP).execute()
        out(f"  submitted {SITEMAP} to {prop}")
    except HttpError as ex:
        out(f"  failed ({ex.status_code}): {ex.reason}")
        return 1
    out("  Google fetches it within a day or so; re-run `status` to see counts")
    return 0


def _inspect(sc, url: str, prop: str) -> dict:
    body = {"inspectionUrl": url, "siteUrl": prop, "languageCode": "en-IN"}
    r = sc.urlInspection().index().inspect(body=body).execute()
    return r.get("inspectionResult", {})


def cmd_inspect(sc, sv, args) -> int:
    r = _inspect(sc, args.url, resolve_property(sc))
    idx = r.get("indexStatusResult", {})
    out()
    out(f"  {args.url}")
    out(f"    verdict          {idx.get('verdict')}")
    out(f"    coverage         {idx.get('coverageState')}")
    out(f"    robots           {idx.get('robotsTxtState')}")
    out(f"    indexing allowed {idx.get('indexingState')}")
    out(f"    last crawled     {idx.get('lastCrawlTime', 'never')}")
    out(f"    canonical (them) {idx.get('googleCanonical', '-')}")
    out(f"    canonical (us)   {idx.get('userCanonical', '-')}")
    if r.get("mobileUsabilityResult"):
        out(f"    mobile           {r['mobileUsabilityResult'].get('verdict')}")
    if r.get("richResultsResult"):
        kinds = [d.get("richResultType")
                 for d in r["richResultsResult"].get("detectedItems", [])]
        out(f"    rich results     {', '.join(kinds) or 'none detected'}")
    return 0


def cmd_coverage(sc, sv, args) -> int:
    """Inspect every built URL. The API is rate-limited, so this is slow on
    purpose — 2000 inspections a day is the quota and one run of 61 is fine."""
    sys.path.insert(0, str(Path(__file__).parent))
    import build as site_build                                  # noqa: E402
    from content.urls import URLS                                # noqa: E402
    urls = [f"https://{DOMAIN}{URLS[p['slug']]}" for p in site_build.PAGES]
    prop = resolve_property(sc)
    out()
    out(f"  inspecting {len(urls)} URLs against {prop}")
    tally: dict[str, list[str]] = {}
    for i, u in enumerate(urls, 1):
        try:
            idx = _inspect(sc, u, prop).get("indexStatusResult", {})
            state = idx.get("coverageState", "unknown")
        except HttpError as ex:
            state = f"API error {ex.status_code}"
        tally.setdefault(state, []).append(u)
        print(plain(f"    {i:>3}/{len(urls)}  {state:<45}"), end="\r")
        time.sleep(0.6)
    out(" " * 70)
    out()
    for state, us in sorted(tally.items(), key=lambda kv: -len(kv[1])):
        out(f"  {len(us):>3}  {state}")
        if len(us) <= 12 and "Submitted and indexed" not in state:
            for u in us:
                out(f"         {u}")
    return 0


def cmd_domain_token(sc, sv, args) -> int:
    r = sv.webResource().getToken(body={
        "verificationMethod": "DNS_TXT",
        "site": {"type": "INET_DOMAIN", "identifier": DOMAIN},
    }).execute()
    out()
    out("  Add this DNS TXT record, then run `domain-verify`:")
    out()
    out(f"    host / name   @        (that is, {DOMAIN} itself)")
    out("    type          TXT")
    out(f"    value         {r['token']}")
    out("    TTL           leave the default")
    out()
    out("  Hostinger hPanel -> Domains -> DNS / Nameservers -> Manage DNS records.")
    out("  Adding it does NOT replace the existing records; TXT records coexist,")
    out("  and this one is inert apart from proving ownership.")
    return 0


def cmd_domain_verify(sc, sv, args) -> int:
    out()
    try:
        sv.webResource().insert(
            verificationMethod="DNS_TXT",
            body={"site": {"type": "INET_DOMAIN", "identifier": DOMAIN}},
        ).execute()
        out(f"  verified ownership of {DOMAIN} by DNS")
    except HttpError as ex:
        out(f"  not verified yet ({ex.status_code}): {ex.reason}")
        out("  DNS can take anywhere from minutes to a few hours to propagate.")
        return 1
    try:
        sc.sites().add(siteUrl=f"sc-domain:{DOMAIN}").execute()
        out(f"  added Domain property sc-domain:{DOMAIN} to Search Console")
    except HttpError as ex:
        out(f"  property add failed ({ex.status_code}): {ex.reason}")
        return 1
    try:
        sc.sitemaps().submit(siteUrl=f"sc-domain:{DOMAIN}", feedpath=SITEMAP).execute()
        out(f"  submitted {SITEMAP} to the Domain property too")
    except HttpError as ex:
        out(f"  sitemap submit failed ({ex.status_code}): {ex.reason}")
    return 0


def cmd_queries(sc, sv, args) -> int:
    end = date.today() - timedelta(days=2)      # GSC data lags ~2 days
    start = end - timedelta(days=args.days)
    body = {"startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": [args.dimension], "rowLimit": 40}
    r = sc.searchanalytics().query(
        siteUrl=resolve_property(sc), body=body).execute()
    rows = r.get("rows", [])
    out()
    out(f"  {args.dimension}s, {start} to {end}")
    if not rows:
        out("    no data yet — normal for a site Google has only just started")
        out("    crawling; impressions usually appear within one to three weeks")
        return 0
    out(f"    {'':<52} {'clicks':>7} {'impr':>8} {'ctr':>6} {'pos':>6}")
    for row in rows:
        k = row["keys"][0][:50]
        out(f"    {k:<52} {row['clicks']:>7.0f} {row['impressions']:>8.0f} "
            f"{row['ctr']*100:>5.1f}% {row['position']:>6.1f}")
    return 0


COMMANDS = {
    "status": cmd_status, "sitemap": cmd_sitemap, "inspect": cmd_inspect,
    "coverage": cmd_coverage, "domain-token": cmd_domain_token,
    "domain-verify": cmd_domain_verify, "queries": cmd_queries,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=sorted(COMMANDS))
    ap.add_argument("url", nargs="?", help="for `inspect`")
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--dimension", default="query",
                    choices=["query", "page", "country", "device"])
    ap.add_argument("--reauth", action="store_true",
                    help="ignore the cached token and sign in again")
    args = ap.parse_args()
    if args.command == "inspect" and not args.url:
        ap.error("inspect needs a URL")
    sc, sv = services(args.command, args.reauth)
    return COMMANDS[args.command](sc, sv, args)


if __name__ == "__main__":
    raise SystemExit(main())
