"""Query GSC for material-related search terms."""
import sys, json
sys.path.insert(0, '.tmp/scripts')
from fetch_search_console import fetch_search_analytics

material_terms = [
    'pla', 'abs', 'petg', 'tpu', 'nylon', 'asa', 'polycarbonate',
    'carbon fiber', 'filament', 'pp ', ' pc ', 'peek', 'ultem',
    'hips', 'pva', '3d print', '3d printer'
]

for site in ['sc-domain:fracktal.in', 'https://fracktal.in/', 'https://www.fracktal.in/']:
    print(f'\n=== Trying: {site} ===')
    result = fetch_search_analytics(site, '2026-04-15', '2026-07-14', ['query'], 100)
    if result and result.get('rows'):
        rows = result.get('rows', [])
        matched = []
        for r in rows:
            query = ' '.join(r['keys']).lower()
            if any(m in query for m in material_terms):
                matched.append(r)
        print(f'Total queries: {len(rows)}, Material-related: {len(matched)}')
        for r in matched[:30]:
            q = r['keys'][0]
            print(f'  {q[:45]:45s} | clicks:{r["clicks"]:>5} | impr:{r["impressions"]:>7} | pos:{r["position"]:>6.1f}')
        break
    else:
        print(f'  No data or error: {result}')
