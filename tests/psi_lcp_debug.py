import requests, json, sys

API_KEY='AIzaSyD0Yb8d0jkKVE4an6nLb-g70p_mNZ93Vr0'
url='https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
params={'url':'https://fracktal.in','key':API_KEY,'strategy':'mobile','category':'performance'}
r=requests.get(url,params=params,timeout=30)
d=r.json()

audits=['largest-contentful-paint-element','lcp-lazy-loaded','uses-optimized-images',
        'uses-responsive-images','prioritize-lcp-image','total-byte-weight','dom-size',
        'render-blocking-resources']
for aid in audits:
    a=d['lighthouseResult']['audits'].get(aid,{})
    if a:
        print(f"--- {a['title']} ---")
        print(f"Score: {a.get('score','N/A')}")
        print(f"Display: {a.get('displayValue','N/A')}")
        if a.get('details') and a['details'].get('items'):
            for item in a['details']['items'][:5]:
                print(f"  {json.dumps(item)[:300]}")
        print()
