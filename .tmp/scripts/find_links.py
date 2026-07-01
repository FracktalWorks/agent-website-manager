"""Find all widgets with link/button_url in a page export."""
import json, os

base = os.path.expanduser(
    r"~\AppData\Roaming\Code\User\workspaceStorage"
    r"\783e5fb25a03f96702d0d46dfbd10868\GitHub.copilot-chat"
    r"\chat-session-resources\a0ab7162-d9cd-4a5d-9d74-883be805c3cb"
)

TARGET = "call_00_fWuoc"

for d in sorted(os.listdir(base), reverse=True):
    dp = os.path.join(base, d)
    if os.path.isdir(dp) and d.startswith(TARGET):
        cf = os.path.join(dp, "content.json")
        with open(cf, "r", encoding="utf-8") as f:
            data = json.load(f)

        def find_all(obj):
            if isinstance(obj, dict):
                wt = obj.get("widgetType", obj.get("elType", ""))
                s = obj.get("settings", {})
                button_url = s.get("button_url", "")
                link = s.get("link", "")
                url = s.get("url", "")
                cta_link = s.get("cta_link", "")
                website_link = s.get("website_link", "")
                button = s.get("button", {})

                if button_url or link or url or cta_link or website_link:
                    title = str(s.get("title", s.get("text", "")))[:80]
                    print(f"--- {wt}: {title} ---")
                    print(f"  button_url = {button_url}")
                    print(f"  link = {link}")
                    print(f"  url = {url}")
                    print(f"  cta_link = {cta_link}")
                    print(f"  website_link = {website_link}")
                    if button:
                        print(f"  button = {button}")
                    print()

                for k, v in obj.items():
                    find_all(v)
            elif isinstance(obj, list):
                for item in obj:
                    find_all(item)

        find_all(data)
        break
