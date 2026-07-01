"""Inspect button widgets in exported page to find link issues."""
import json, os

base = os.path.expanduser(
    r"~\AppData\Roaming\Code\User\workspaceStorage"
    r"\783e5fb25a03f96702d0d46dfbd10868\GitHub.copilot-chat"
    r"\chat-session-resources\a0ab7162-d9cd-4a5d-9d74-883be805c3cb"
)

for d in sorted(os.listdir(base), reverse=True):
    dp = os.path.join(base, d)
    if os.path.isdir(dp) and d.startswith("call_00_l01ZZ"):
        cf = os.path.join(dp, "content.json")
        with open(cf, "r") as f:
            data = json.load(f)

        def find_buttons(obj, depth=0):
            if isinstance(obj, dict):
                if obj.get("widgetType") == "button":
                    s = obj.get("settings", {})
                    txt = s.get("text", "?")
                    print(f"Button: text='{txt}'")
                    for k, v in sorted(s.items()):
                        if "url" in k.lower() or "link" in k.lower():
                            print(f"  {k} = {v}")
                    print()
                for k, v in obj.items():
                    find_buttons(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    find_buttons(item, depth + 1)

        find_buttons(data)
        break
