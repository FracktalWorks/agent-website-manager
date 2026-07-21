"""Clear cached MCP data from VS Code workspace state database."""
import sqlite3, json, os

ws_base = os.path.expandvars(r'%APPDATA%\Code\User\workspaceStorage')
target = None
for d in os.listdir(ws_base):
    ws_json = os.path.join(ws_base, d, 'workspace.json')
    if os.path.exists(ws_json):
        with open(ws_json, encoding='utf-8') as f:
            ws = json.load(f)
        if 'agent-website-manager' in ws.get('folder', ''):
            target = os.path.join(ws_base, d, 'state.vscdb')
            break

if not target:
    print('Workspace state DB not found')
    exit(1)

conn = sqlite3.connect(target)
cursor = conn.cursor()

keys_to_clear = [
    'mcpToolCache',
    'mcp.extCachedServers',
    'mcpInputs',
    'workbench.view.extension.hostinger-sidebar.state',
]

for key in keys_to_clear:
    cursor.execute("DELETE FROM ItemTable WHERE key = ?", (key,))
    if cursor.rowcount > 0:
        print(f'Cleared: {key} ({cursor.rowcount} row(s))')
    else:
        print(f'Not found: {key}')

conn.commit()
conn.close()
print('\nDone. Reload VS Code for changes to take effect.')
