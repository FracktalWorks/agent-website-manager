#!/usr/bin/env python3
"""
Deep-analyze existing Elementor pages to extract design patterns.
Used to rebuild the 3D Printer Manufacturer page with real site patterns.
"""
import json, os, glob

BASE = os.path.expanduser(
    r"~\AppData\Roaming\Code\User\workspaceStorage"
    r"\783e5fb25a03f96702d0d46dfbd10868\GitHub.copilot-chat"
    r"\chat-session-resources\a0ab7162-d9cd-4a5d-9d74-883be805c3cb"
)

def load_export(prefix):
    for d in os.listdir(BASE):
        dp = os.path.join(BASE, d)
        if os.path.isdir(dp) and d.startswith(prefix):
            cf = os.path.join(dp, "content.json")
            if os.path.exists(cf):
                with open(cf, "r", encoding="utf-8") as f:
                    return json.load(f).get("json", [])
    return []

def walk_elements(elements, depth=0):
    """Walk Elementor element tree and yield (depth, element) tuples."""
    for el in elements:
        yield (depth, el)
        if "elements" in el:
            yield from walk_elements(el["elements"], depth + 1)

def summarize_page(name, prefix):
    """Print a structured summary of a page's design patterns."""
    els = load_export(prefix)
    if not els:
        print(f"\n=== {name}: NOT FOUND ===")
        return

    print(f"\n{'='*70}")
    print(f"  {name} ({len(els)} top-level elements)")
    print(f"{'='*70}")

    for depth, el in walk_elements(els):
        indent = "  " * depth
        etype = el.get("elType", "?")
        wtype = el.get("widgetType", "")
        settings = el.get("settings", {})
        title = settings.get("_title", settings.get("title", ""))
        tag = settings.get("title_tag", "")

        if etype == "container":
            bg = settings.get("background_background", "")
            bg_color = settings.get("background_color", "")
            overlay_color = settings.get("background_overlay_color", "")
            bg_img = settings.get("background_image", {}).get("url", "")
            min_h = settings.get("min_height", {})
            mh_val = f"{min_h.get('size','')}{min_h.get('unit','')}" if min_h else ""
            pad = settings.get("padding", {})
            gap = settings.get("flex_gap", {})
            flex_dir = settings.get("flex_direction", "")
            layout = settings.get("layout", "")
            cw = settings.get("content_width", "")

            parts = [f"container"]
            if title:
                parts.append(f"'{title}'")
            if bg:
                parts.append(f"bg={bg}")
            if bg_color:
                parts.append(f"bg_color={bg_color}")
            if overlay_color:
                parts.append(f"overlay={overlay_color}")
            if bg_img:
                parts.append(f"img={os.path.basename(bg_img)[:50]}")
            if mh_val:
                parts.append(f"min_h={mh_val}")
            if flex_dir:
                parts.append(f"flex={flex_dir}")
            if layout:
                parts.append(f"layout={layout}")
            if cw:
                parts.append(f"width={cw}")
            if gap:
                parts.append(f"gap={gap.get('size','')}{gap.get('unit','')}")

            print(f"{indent}[{' | '.join(parts)}]")

        elif etype == "widget":
            wtitle = settings.get("title", "") or settings.get("text", "") or ""
            if len(wtitle) > 80:
                wtitle = wtitle[:77] + "..."
            tc = settings.get("title_color", "")
            ts = settings.get("title_size", "")
            txt = settings.get("text", "")
            if txt and len(txt) > 60:
                txt = txt[:57] + "..."
            btn_url = settings.get("button_url", "")
            btn_txt = settings.get("button_text", "") or settings.get("text", "")
            img_url = settings.get("image", {}).get("url", "") if isinstance(settings.get("image"), dict) else ""

            parts = [f"widget:{wtype}"]
            if tag:
                parts.append(f"<{tag}>")
            if wtitle:
                parts.append(f"title='{wtitle}'")
            if tc:
                parts.append(f"color={tc}")
            if ts:
                parts.append(f"size={ts}")
            if btn_url:
                parts.append(f"btn->{btn_url[:40]}")
            if img_url:
                parts.append(f"img={os.path.basename(img_url)[:40]}")

            print(f"{indent}[{' | '.join(parts)}]")

        elif etype == "section":
            bg = settings.get("background_background", "")
            bg_img = settings.get("background_image", {}).get("url", "")
            print(f"{indent}[section | bg={bg} | img={os.path.basename(bg_img)[:50] if bg_img else 'none'}]")

        elif etype == "column":
            cs = settings.get("_column_size", "")
            print(f"{indent}[column | size={cs}]")


if __name__ == "__main__":
    # Summarize key pages
    summarize_page("3D Printers (/3dprinters/)", "call_00_fWuoc")
    summarize_page("Homepage (/)", "call_00_WpzW7")
    summarize_page("Julia Product Page", "call_01_wIeKg")
