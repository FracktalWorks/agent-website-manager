"""Pull inbound-link data from the Bing Webmaster API (free tier).

The referring-domains baseline should not depend on a paid backlink tool:
Bing Webmaster Tools exposes its link index through a free API once the site
is verified there and an API key exists (BWMT > Settings > API access).

    python bing_links.py https://fracktal.in/ --out outputs/fracktal/bing-links.json

Reads the key from env BING_WEBMASTER_API_KEY (a repo .env is loaded when
python-dotenv is present). A freshly connected property answers with an
empty index for days; the script says so rather than writing a zero
baseline anyone might mistake for a measurement.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).resolve().parents[4] / ".env")
    load_dotenv()
except ImportError:
    pass
import os

API = "https://ssl.bing.com/webmaster/api.svc/json"


def call(method: str, **params):
    params["apikey"] = os.environ["BING_WEBMASTER_API_KEY"]
    url = f"{API}/{method}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":
                                               "link-authority/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["d"]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    site = args[0]
    out = None
    if "--out" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])

    sites = {s["Url"]: s["IsVerified"] for s in call("GetUserSites")}
    if site not in sites:
        print(f"  site {site} not in BWMT account; have: {list(sites)}")
        return 1
    print(f"  {site} verified={sites[site]}")

    pages, page = [], 0
    while True:
        d = call("GetLinkCounts", siteUrl=site, page=page)
        pages.extend(d.get("Links") or [])
        total = d.get("TotalPages", 0)
        page += 1
        if page >= total:
            break
        time.sleep(1)  # be gentle; there is no hurry

    if not pages:
        print("  Bing's link index for this property is still EMPTY — "
              "normal for a fresh connection. Re-run in a week; do not "
              "record 0 as a baseline.")
        return 0

    total_links = sum(p.get("Count", 0) for p in pages)
    print(f"  {len(pages)} linked page(s), {total_links} inbound links "
          f"known to Bing")
    for p in pages[:15]:
        print(f"    {p.get('Count', 0):>6}  {p.get('Url', '')}")
    if out:
        out.write_text(json.dumps(
            {"site": site, "pulled": time.strftime("%Y-%m-%d"),
             "pages": pages}, indent=1), encoding="utf-8")
        print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
