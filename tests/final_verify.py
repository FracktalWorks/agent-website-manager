"""Final verification: check cloaking on all key pages."""
import requests
import re

UA = 'Googlebot/2.1'
SITE = 'https://fracktal.in'

pages = [
    ('/', ''),
    ('Carbon Fiber Nylon', 'carbon-fiber-nylon'),
    ('ABS', 'abs-acrylonitrile-butadiene-styrene'),
    ('PET-G', 'pet-g-polyethylene-terephthalate-glycol'),
    ('TPU', 'tpu-thermoplastic-polyurethane'),
    ('Nylon', 'nylon'),
    ('PVA', 'pva-polyvinyl-alcohol'),
    ('3D Printing Services', '3d-printing-services'),
    ('Consulting', 'consulting-services'),
    ('Material Dryer', 'materialdryer'),
    ('Vacuum Casting', 'vaccum-casting'),
    ('Snowflake', 'snowflake'),
    ('Twin Dragon', 'twindragon'),
    ('Manufacturer India', '3d-printer-manufacturer-india'),
]

print("=== CLOAKING CHECK (Googlebot UA) ===")
clean = 0
infected = 0
for label, slug in pages:
    url = f'{SITE}/{slug}' if slug else SITE
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=20)
        title_match = re.search(r'<title>(.*?)</title>', r.text)
        title = title_match.group(1) if title_match else 'NO TITLE'
        has_jp = bool(re.search(r'[\u3040-\u309f\u30a0-\u30ff]', r.text))
        
        if has_jp:
            status = '❌ JAPANESE SPAM'
            infected += 1
        elif 'Fracktal' in title or 'fracktal' in title.lower():
            status = '✅'
            clean += 1
        else:
            status = '⚠️ UNKNOWN'
        
        print(f"  {status} [{r.status_code}] {label}: {title[:85]}")
    except Exception as e:
        print(f"  ❌ ERROR {label}: {e}")

print(f"\nClean: {clean} | Infected: {infected} | Total: {len(pages)}")
if infected == 0:
    print("✅ CLOAKING IS GONE — All pages serve correct content to Googlebot")
else:
    print(f"❌ {infected} pages still infected!")

# Also verify backdoor files
print("\n=== BACKDOOR FILES CHECK ===")
backdoors = [
    'wp-content/uploads/2021/10/vwlx9o.php',
    'wp-content/uploads/2024/01/w9glu.php',
    'wp-content/uploads/et-fonts/1a2o0sd.php',
    'wp-content/uploads/wpmc-trash/elementor/pqmnj4l.php',
    'wp-content/uploads/wpforms/cache/index.php',
    'wp-content/wflogs/img/content/img/2023/uploads/ekf/admin.php',
    'wp-content/wphb-logs/assets/docs/archive/tymu/lhki/index.php',
]
for path in backdoors:
    try:
        r = requests.head(f'{SITE}/{path}', timeout=10, allow_redirects=True)
        if r.status_code == 200:
            print(f"  ❌ STILL ACTIVE: {path} (HTTP 200)")
        elif r.status_code == 404:
            print(f"  ✅ GONE: {path} (HTTP 404)")
        else:
            print(f"  ⚠️ {path} (HTTP {r.status_code})")
    except Exception as e:
        print(f"  ⚠️ ERROR {path}: {e}")
