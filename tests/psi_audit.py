"""Check PageSpeed Insights scores for desktop and mobile."""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv('PAGESPEED_API_KEY')
URL = 'https://fracktal.in'

print("=== PAGESPEED INSIGHTS ===")
for strategy in ['mobile', 'desktop']:
    r = requests.get(
        f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed',
        params={'url': URL, 'strategy': strategy, 'key': KEY},
        timeout=60)
    data = r.json()
    cats = data.get('lighthouseResult', {}).get('categories', {})
    perf = cats.get('performance', {})
    score = perf.get('score', 0) * 100

    # Audits
    audits = data.get('lighthouseResult', {}).get('audits', {})
    
    print(f"\n{'='*50}")
    print(f"  {strategy.upper()} — Score: {score:.0f}/100")
    print(f"{'='*50}")
    
    # Core metrics
    metrics = [
        ('first-contentful-paint', 'FCP'),
        ('largest-contentful-paint', 'LCP'),
        ('total-blocking-time', 'TBT'),
        ('cumulative-layout-shift', 'CLS'),
        ('speed-index', 'Speed Index'),
        ('interactive', 'TTI'),
    ]
    
    for audit_id, label in metrics:
        a = audits.get(audit_id, {})
        display = a.get('displayValue', 'N/A')
        score_pct = a.get('score', 0) * 100 if a.get('score') is not None else 'N/A'
        icon = '🟢' if a.get('score', 0) >= 0.9 else '🟡' if a.get('score', 0) >= 0.5 else '🔴'
        print(f"  {icon} {label}: {display} (score: {score_pct})")
    
    # Top opportunities (worst first)
    print(f"\n  --- TOP OPPORTUNITIES ---")
    opportunities = []
    for aid, a in audits.items():
        if a.get('details', {}).get('type') == 'opportunity':
            opportunities.append((a.get('numericValue', 0), a.get('title', aid)))
    opportunities.sort(reverse=True)
    for savings, title in opportunities[:5]:
        if savings > 0:
            print(f"  🔧 {title}: save {savings:.0f}ms")
    
    # Top diagnostics
    print(f"\n  --- TOP DIAGNOSTICS ---")
    diagnostics = []
    for aid, a in audits.items():
        if a.get('details', {}).get('type') == 'table' and (a.get('score') or 0) < 0.5:
            diagnostics.append((a.get('score') or 0, a.get('title', aid)))
    diagnostics.sort()
    for score_d, title in diagnostics[:5]:
        print(f"  ⚠️ {title}")
