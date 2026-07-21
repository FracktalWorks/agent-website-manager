import sqlite3, json

db_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\workspaceStorage\36039b9fa8dfce70ad8963c66ee27245\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get ALL keys containing 'higgsfield'
cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%higgsfield%'")
hf_keys = cursor.fetchall()
print('Higgsfield keys:')
for k in hf_keys:
    print('  ' + k[0])

# Get ALL keys containing 'disabled' or 'approv' or 'visibility'
for term in ['disabled', 'approv', 'visib']:
    cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%' || ? || '%'", (term,))
    rows = cursor.fetchall()
    if rows:
        print('\nKeys with "' + term + '":')
        for r in rows:
            print('  ' + r[0])

conn.close()
