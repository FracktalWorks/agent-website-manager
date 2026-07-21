import sqlite3, json, os

ws_base = os.path.expandvars(r'%APPDATA%\Code\User\workspaceStorage')
for d in os.listdir(ws_base):
    ws_json = os.path.join(ws_base, d, 'workspace.json')
    if os.path.exists(ws_json):
        with open(ws_json) as f:
            ws = json.load(f)
        if 'agent-website-manager' in ws.get('folder', ''):
            print(f'Found workspace: {d}')
            state_db = os.path.join(ws_base, d, 'state.vscdb')
            if os.path.exists(state_db):
                conn = sqlite3.connect(state_db)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                for t in tables:
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM {t[0]}')
                        count = cursor.fetchone()[0]
                        print(f'  {t[0]}: {count} rows')
                        # Check for MCP-related content
                        if count > 0 and count < 100:
                            cursor.execute(f'SELECT * FROM {t[0]}')
                            rows = cursor.fetchall()
                            for row in rows:
                                row_str = str(row)
                                if 'mcp' in row_str.lower() or 'hostinger' in row_str.lower():
                                    print(f'    MCP-related: {row_str[:200]}')
                    except Exception as e:
                        print(f'  {t[0]}: error - {e}')
                conn.close()
            break
