import sqlite3, json

db_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\workspaceStorage\36039b9fa8dfce70ad8963c66ee27245\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Read the MCP-related values
key1 = 'mcp.config.ws0.higgsfield-https://mcp.higgsfield.ai/ https://mcp.higgsfield.ai/mcp'
key2 = 'workspace-dot-mcp.0.higgsfield-https://mcp.higgsfield.ai/ https://mcp.higgsfield.ai/mcp'
key3 = 'mcpToolCache'

for key in [key1, key2, key3]:
    cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
    row = cursor.fetchone()
    if row:
        val = row[0]
        print('=== ' + key + ' ===')
        try:
            parsed = json.loads(val)
            print(json.dumps(parsed, indent=2)[:3000])
        except:
            print(val[:2000])
        print()
    else:
        print('=== ' + key + ' === NOT FOUND')
        print()

conn.close()
