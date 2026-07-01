"""Fix button URLs in exported Elementor JSON — convert button_url strings to link objects."""
import json, os

base = os.path.expanduser(
    r"~\AppData\Roaming\Code\User\workspaceStorage"
    r"\783e5fb25a03f96702d0d46dfbd10868\GitHub.copilot-chat"
    r"\chat-session-resources\a0ab7162-d9cd-4a5d-9d74-883be805c3cb"
)

for d in sorted(os.listdir(base), reverse=True):
    dp = os.path.join(base, d)
    if os.path.isdir(dp) and d.startswith("call_00_C4LP"):
        cf = os.path.join(dp, "content.json")
        with open(cf, "r", encoding="utf-8") as f:
            exported = json.load(f)

        data = exported.get("json", exported.get("data", []))

        def fix_buttons(obj):
            if isinstance(obj, dict):
                if obj.get("widgetType") == "button":
                    s = obj.get("settings", {})
                    burl = s.get("button_url", "")
                    if burl:
                        s["link"] = {
                            "url": burl,
                            "is_external": "",
                            "nofollow": "",
                        }
                        txt = s.get("text", "?")
                        print("Fixed: {} -> {}".format(txt, burl))
                for v in obj.values():
                    fix_buttons(v)
            elif isinstance(obj, list):
                for item in obj:
                    fix_buttons(item)

        fix_buttons(data)

        out_path = os.path.join(os.getcwd(), ".tmp", "fixed_page.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print("Saved to {} ({} chars)".format(out_path, len(json.dumps(data))))
        break
