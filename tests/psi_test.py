import json, os, requests

API_KEY = "AIzaSyD0Yb8d0jkKVE4an6nLb-g70p_mNZ93Vr0"
URL = "https://fracktal.in"

for strategy in ["mobile", "desktop"]:
    print(f"\n--- {strategy.upper()} ---")
    r = requests.get(
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
        params={"url": URL, "key": API_KEY, "strategy": strategy},
        timeout=60
    )
    data = r.json()

    if "error" in data:
        print(f"ERROR: {data['error']['message']}")
        continue

    lh = data.get("lighthouseResult", {})
    cats = lh.get("categories", {})

    for k, v in cats.items():
        score = v.get("score", 0)
        emoji = "🟢" if score >= 0.9 else "🟠" if score >= 0.5 else "🔴"
        print(f"  {k:20s}: {emoji} {score*100:.0f}/100")

    audits = lh.get("audits", {})
    metrics = [
        ("first-contentful-paint", "FCP"),
        ("largest-contentful-paint", "LCP"),
        ("total-blocking-time", "TBT"),
        ("cumulative-layout-shift", "CLS"),
        ("speed-index", "SI"),
        ("interactive", "TTI"),
    ]
    for audit_key, label in metrics:
        val = audits.get(audit_key, {}).get("displayValue", "N/A")
        print(f"  {label:20s}: {val}")
