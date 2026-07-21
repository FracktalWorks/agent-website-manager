import sqlite3, json, os

db_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\workspaceStorage\36039b9fa8dfce70ad8963c66ee27245\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

# Look for MCP-related or tool approval keys
cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%mcp%' OR key LIKE '%higgsfield%' OR key LIKE '%tool%' OR key LIKE '%approv%'")
rows = cursor.fetchall()
print('Relevant keys found:', len(rows))
for row in rows:
    print('  ' + row[0])

# Also dump all keys to see what's there
cursor.execute("SELECT key FROM ItemTable")
all_keys = cursor.fetchall()
mcp_keys = [k[0] for k in all_keys if 'mcp' in k[0].lower() or 'higgsfield' in k[0].lower() or 'approv' in k[0].lower() or 'tool' in k[0].lower()]
print('\nMCP/tool-related from all keys:')
for k in mcp_keys:
    print('  ' + k)

conn.close()
