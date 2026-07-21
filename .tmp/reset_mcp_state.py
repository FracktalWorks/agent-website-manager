import sqlite3

db_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\workspaceStorage\36039b9fa8dfce70ad8963c66ee27245\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Delete the MCP tool cache to force re-fetch
cursor.execute("DELETE FROM ItemTable WHERE key = 'mcpToolCache'")
cursor.execute("DELETE FROM ItemTable WHERE key = 'mcp.extCachedServers'")

# Also clear the Higgsfield config entries
cursor.execute("DELETE FROM ItemTable WHERE key LIKE '%higgsfield%'")

conn.commit()
print('Deleted rows:', cursor.rowcount)

# Verify
cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%higgsfield%' OR key LIKE '%mcpTool%'")
remaining = cursor.fetchall()
print('Remaining Higgsfield/MCP keys:', remaining)

conn.close()
print('Done. Restart VS Code for changes to take effect.')
