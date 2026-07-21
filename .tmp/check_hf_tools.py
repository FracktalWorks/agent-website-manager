import sqlite3, json

db_path = r'c:\Users\VijayRaghavVarada\AppData\Roaming\Code\User\workspaceStorage\36039b9fa8dfce70ad8963c66ee27245\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT value FROM ItemTable WHERE key = 'mcpToolCache'")
row = cursor.fetchone()
cache = json.loads(row[0])

# Find Higgsfield server entry
for server in cache.get('serverTools', []):
    srv_name = server[0]
    srv_data = server[1]
    if 'higgsfield' in srv_name.lower():
        print('Server:', srv_name)
        tools = srv_data.get('tools', [])
        print('Total tools:', len(tools))
        for t in tools:
            name = t.get('name', 'N/A')
            vis = t.get('visibility', 'N/A')
            print('  ' + name + ' | visibility=' + str(vis))
        break
else:
    print('Higgsfield server entry not found in cache')
    # Print all server names
    print('\nAvailable servers:')
    for server in cache.get('serverTools', []):
        print('  ' + server[0])

conn.close()
