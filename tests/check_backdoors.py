"""Quick check: all backdoor files gone?"""
import requests

backdoors = [
    'wp-content/uploads/2021/10/vwlx9o.php',
    'wp-content/uploads/2024/01/w9glu.php',
    'wp-content/uploads/et-fonts/1a2o0sd.php',
    'wp-content/uploads/wpmc-trash/elementor/pqmnj4l.php',
    'wp-content/uploads/wpforms/cache/index.php',
    'wp-content/wflogs/img/content/img/2023/uploads/ekf/admin.php',
    'wp-content/wphb-logs/assets/docs/archive/tymu/lhki/index.php',
]

all_gone = True
for path in backdoors:
    try:
        r = requests.head(f'https://fracktal.in/{path}', timeout=10)
        if r.status_code == 200:
            print(f'❌ STILL THERE: {path}')
            all_gone = False
        elif r.status_code == 404:
            print(f'✅ GONE: {path}')
        else:
            print(f'⚠️ {path} -> HTTP {r.status_code}')
    except Exception as e:
        print(f'⚠️ ERROR {path}: {e}')

if all_gone:
    print('\n🎉 ALL 7 BACKDOOR FILES DELETED! Site is clean.')
else:
    print('\n⚠️ Some files remain.')
