import requests, base64, json
AUTH='Basic '+base64.b64encode(b'vjvarada:eBZmsn9ovjOvcvtW14bZPbsx').decode()
H={'Authorization':AUTH,'Content-Type':'application/json'}
MCP='https://fracktal.in/wp-json/mcp/emcp-tools-server'

r=requests.post(MCP,headers=H,json={'jsonrpc':'2.0','method':'initialize',
    'params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'A','version':'1'}},'id':1},timeout=15)
sid=r.headers['Mcp-Session-Id']
H2={**H,'Mcp-Session-Id':sid}

for name,pid in [('snowflake',15598),('twindragon',22712),('julia',1909)]:
    r2=requests.post(MCP,headers=H2,json={'jsonrpc':'2.0','method':'tools/call',
        'params':{'name':'emcp-tools-get-page-structure','arguments':{'post_id':pid}},'id':2},timeout=30)
    data=json.loads(r2.json()['result']['content'][0]['text'])
    structure=data['structure']
    def fh(els):
        if isinstance(els,list):
            for e in els:
                if isinstance(e,dict):
                    if e.get('widgetType')=='heading':return e['id']
                    r=fh(e.get('elements',[]))
                    if r:return r
        return None
    hid=fh(structure)
    if hid:
        r3=requests.post(MCP,headers=H2,json={'jsonrpc':'2.0','method':'tools/call',
            'params':{'name':'emcp-tools-update-element','arguments':{'post_id':pid,'element_id':hid,'settings':{'header_size':'h1'}}},'id':3},timeout=30)
        result_text=r3.json()['result']['content'][0]['text']
        ok='success' in result_text
        print(f"{name}: {hid} -> H1 {'OK' if ok else 'FAIL: '+result_text[:80]}")
    else:
        print(f"{name}: No heading found")
