import sqlite3, os

db_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\globalStorage\GitHub.copilot-chat\session-store.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print('Tables:', tables)

for table in tables:
    cursor.execute("SELECT COUNT(*) FROM " + table)
    count = cursor.fetchone()[0]
    print('  ' + table + ': ' + str(count) + ' rows')

conn.close()

# Also check api.json
api_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\globalStorage\GitHub.copilot-chat\api.json'
if os.path.exists(api_path):
    with open(api_path) as f:
        content = f.read()
    print('\napi.json (first 2000 chars):')
    print(content[:2000])
