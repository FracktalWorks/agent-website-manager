import sqlite3

db_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\workspaceStorage\36039b9fa8dfce70ad8963c66ee27245\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Search for Copilot tool-related keys
cursor.execute("SELECT key FROM ItemTable WHERE lower(key) LIKE '%copilot%' AND lower(key) LIKE '%tool%'")
rows = cursor.fetchall()
print('Copilot tool keys:')
for r in rows:
    print('  ' + r[0])

# Search for disabled
cursor.execute("SELECT key FROM ItemTable WHERE lower(key) LIKE '%disabled%'")
rows = cursor.fetchall()
print('\nDisabled keys:')
for r in rows:
    print('  ' + r[0])

# Search for mcp in GitHub Copilot chat related
cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%GitHub.copilot%' AND lower(key) LIKE '%mcp%'")
rows = cursor.fetchall()
print('\nGitHub Copilot MCP keys:')
for r in rows:
    print('  ' + r[0])

conn.close()
