"""
Open Design ↔ Agent Website Manager Bridge

Connects Open Design's design generation capabilities with WordPress deployment.
Generates production-quality pages using Open Design design systems and deploys
them directly to WordPress via the REST API.

Usage:
    python .tmp/scripts/open_design_bridge.py list-systems
    python .tmp/scripts/open_design_bridge.py sync-system fracktal-works
    python .tmp/scripts/open_design_bridge.py deploy --html <file> --title "Page" --slug "slug"
    python .tmp/scripts/open_design_bridge.py deploy-elementor --html <file> --title "Page"

Requirements:
    pip install requests python-dotenv beautifulsoup4
"""

import os
import sys
import json
import shutil
import argparse
import base64
import re
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
DESIGN_SYSTEMS_DIR = REPO_ROOT / "agent-data" / "design-systems"
OUTPUTS_DIR = REPO_ROOT / "outputs" / "design_pages"
OD_REPO = Path("C:/Users/VijayRaghavVarada/Documents/Github/open-design")
OD_DESIGN_SYSTEMS = OD_REPO / "design-systems"
HTML2ELEMENTOR_DIR = REPO_ROOT / ".github" / "skills" / "elementor_builder" / "scripts"

# ── Helpers ────────────────────────────────────────────────────────────────

def load_env():
    """Load .env from repo root."""
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")

def wp_api(path: str, method: str = "GET", data: dict = None) -> dict:
    """Call WordPress REST API."""
    import requests as r
    load_env()
    site = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
    user = os.getenv("WORDPRESS_USERNAME", "")
    pwd = os.getenv("WORDPRESS_APP_PASSWORD", "")
    if not all([site, user, pwd]):
        raise RuntimeError("WORDPRESS_SITE_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD required in .env")
    url = f"{site}/wp-json/wp/v2/{path.lstrip('/')}"
    auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
    if method == "GET":
        resp = r.get(url, headers=headers, timeout=30)
    elif method == "POST":
        resp = r.post(url, headers=headers, json=data, timeout=30)
    elif method == "PUT":
        resp = r.put(url, headers=headers, json=data, timeout=30)
    else:
        raise ValueError(f"Unsupported method: {method}")
    if not resp.ok:
        print(f"  ❌ WP API error [{resp.status_code}]: {resp.text[:300]}")
        resp.raise_for_status()
    return resp.json() if resp.text else {}


def wp_upload_file(file_path: Path | str, title: str = "") -> dict:
    """Upload a file to WordPress media library. Returns media item JSON."""
    import requests as r
    load_env()
    site = os.getenv("WORDPRESS_SITE_URL", "").rstrip("/")
    user = os.getenv("WORDPRESS_USERNAME", "")
    pwd = os.getenv("WORDPRESS_APP_PASSWORD", "")
    auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    url = f"{site}/wp-json/wp/v2/media"
    fpath = Path(file_path)

    # Determine MIME type
    import mimetypes
    mime, _ = mimetypes.guess_type(str(fpath))
    if not mime:
        mime = "application/octet-stream"

    with open(fpath, "rb") as f:
        resp = r.post(
            url,
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": mime,
                "Content-Disposition": f'attachment; filename="{fpath.name}"',
            },
            data=f.read(),
            timeout=60,
        )
    if not resp.ok:
        print(f"  ❌ Media upload error [{resp.status_code}]: {resp.text[:300]}")
        resp.raise_for_status()
    result = resp.json()
    # Set title via update
    if title:
        r.post(
            f"{site}/wp-json/wp/v2/media/{result['id']}",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json",
            },
            json={"title": title},
            timeout=30,
        )
    return result


def extract_body_content(html_path: Path) -> str:
    """Extract body content from HTML, embed <style> as base64 data URI
    so WordPress doesn't strip the styles."""
    from bs4 import BeautifulSoup

    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Extract <style> tag content, encode as base64 data URI
    style_tag = soup.find("style")
    css_data_uri = ""
    if style_tag and style_tag.string:
        css_content = style_tag.string.strip()
        if css_content:
            import base64 as b64
            encoded = b64.b64encode(css_content.encode("utf-8")).decode("ascii")
            css_data_uri = (
                f'<link rel="stylesheet" '
                f'href="data:text/css;base64,{encoded}" '
                f'type="text/css" media="all">'
            )
            print(f"  📎 CSS embedded as data URI ({len(encoded)} chars base64)")

    # Get body content (inner HTML only, no <body> wrapper)
    body = soup.find("body")
    if body:
        for tag in body(["script", "meta", "style"]):
            tag.decompose()
        body_html = body.decode_contents()
    else:
        body_html = str(soup)

    if css_data_uri:
        body_html = css_data_uri + "\n" + body_html

    return body_html


def extract_meta_description(html_path: Path) -> str:
    """Extract meta description from HTML."""
    from bs4 import BeautifulSoup
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"]
    # Fallback: first 160 chars of text
    text = soup.get_text()
    return text.strip()[:160]


# ── Commands ───────────────────────────────────────────────────────────────

def cmd_list_systems():
    """List available design systems."""
    print("\n📐 Available Design Systems\n")
    print(f"  {'System':<30} {'Source':<40}")
    print(f"  {'-'*30} {'-'*40}")
    
    # Local systems
    if DESIGN_SYSTEMS_DIR.exists():
        for d in sorted(DESIGN_SYSTEMS_DIR.iterdir()):
            if d.is_dir() and (d / "DESIGN.md").exists():
                print(f"  {d.name:<30} agent-data/design-systems/")
    
    # Open Design systems
    if OD_DESIGN_SYSTEMS.exists():
        for d in sorted(OD_DESIGN_SYSTEMS.iterdir()):
            if d.is_dir() and (d / "DESIGN.md").exists():
                local = DESIGN_SYSTEMS_DIR / d.name
                status = "✅ synced" if local.exists() else "📥 available"
                print(f"  {d.name:<30} {status}")
    
    print()


def cmd_sync_system(name: str):
    """Sync a design system from Open Design to agent-data."""
    src = OD_DESIGN_SYSTEMS / name
    if not src.exists():
        print(f"  ❌ Design system '{name}' not found in Open Design at {src}")
        print(f"  Available: {', '.join(sorted(d.name for d in OD_DESIGN_SYSTEMS.iterdir() if d.is_dir()))}")
        return
    
    dst = DESIGN_SYSTEMS_DIR / name
    dst.mkdir(parents=True, exist_ok=True)
    
    for fname in ["DESIGN.md", "brand.json", "guide.md"]:
        s = src / fname
        if s.exists():
            shutil.copy2(s, dst / fname)
            print(f"  ✅ {fname}")
    
    # Copy logos
    logos_src = src / "logos"
    logos_dst = dst / "logos"
    if logos_src.exists():
        if logos_dst.exists():
            shutil.rmtree(logos_dst)
        shutil.copytree(logos_src, logos_dst)
        print(f"  ✅ logos/ ({len(list(logos_dst.iterdir()))} files)")
    
    print(f"\n  📐 Design system '{name}' synced to agent-data/design-systems/{name}/")


def cmd_deploy(html_path: str, title: str, slug: str, page_type: str = "page",
               page_id: int = None, status: str = "draft", parent: int = 0):
    """Deploy an HTML page to WordPress."""
    html_file = Path(html_path)
    if not html_file.exists():
        print(f"  ❌ HTML file not found: {html_path}")
        return
    
    print(f"\n  🚀 Deploying '{title}' to WordPress...")
    print(f"     Source: {html_file}")
    print(f"     Slug: {slug}")
    print(f"     Status: {status}")
    
    content = extract_body_content(html_file)
    meta_desc = extract_meta_description(html_file)
    
    payload = {
        "title": title,
        "slug": slug,
        "content": content,
        "status": status,
        "parent": parent,
        "meta": {
            "_yoast_wpseo_metadesc": meta_desc,
        }
    }
    
    if page_type == "post":
        payload["type"] = "post"
    
    try:
        if page_id:
            result = wp_api(f"{page_type}s/{page_id}", method="PUT", data=payload)
            action = "Updated"
        else:
            result = wp_api(f"{page_type}s", method="POST", data=payload)
            action = "Created"
        
        page_url = result.get("link", f"{os.getenv('WORDPRESS_SITE_URL', '')}/?p={result.get('id', '?')}")
        print(f"  ✅ {action} page: {result.get('id')} — {page_url}")
        print(f"     View: {page_url}")
        print(f"     Edit: {os.getenv('WORDPRESS_SITE_URL', '')}/wp-admin/post.php?post={result.get('id')}&action=edit")
        
    except Exception as e:
        print(f"  ❌ Deployment failed: {e}")


def _split_top_level_commas(sel: str) -> list[str]:
    """Split a selector list on top-level commas only (not commas inside
    :not()/:is()/etc.)."""
    parts, depth, buf = [], 0, []
    for ch in sel:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return parts


def _prefix_selector(sel: str, scope: str) -> str:
    """Prefix each selector in a list with `scope`. :root/html/body become the
    scope itself (the wrapper stands in for the document root); `*` becomes
    `scope *`; everything else becomes a descendant of the scope."""
    out = []
    for raw in _split_top_level_commas(sel):
        p = raw.strip()
        if not p:
            continue
        replaced = None
        for lead in (":root", "html", "body"):
            if p == lead:
                replaced = scope
                break
            if p.startswith(lead) and len(p) > len(lead) and p[len(lead)] in " >+~.:#[":
                replaced = scope + p[len(lead):]
                break
        if replaced is not None:
            out.append(replaced)
        elif p == "*":
            out.append(f"{scope} *")
        else:
            out.append(f"{scope} {p}")
    return ", ".join(out)


def _scope_css(css: str, scope: str = ".od-embed") -> str:
    """Prefix every selector in `css` with `scope` so the design's generic rules
    (body, h2, a, .wrap…) can't leak onto the theme's header/footer when the page
    uses a header/footer template. Brace-aware, pure-Python (no deps): @media /
    @supports / @container recurse; @keyframes / @font-face / @page are kept
    verbatim; :root/html/body are rewritten to the scope. (Caveat: a literal `{`
    or `}` inside a string value could confuse brace counting — Open Design CSS
    doesn't do that.)"""
    import re
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)  # strip comments
    n = len(css)

    def read_block(start: int) -> tuple[str, int]:
        depth, j = 0, start
        while j < n:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
                if depth == 0:
                    return css[start + 1:j], j + 1
            j += 1
        return css[start + 1:], n

    out, i = [], 0
    while i < n:
        if css[i].isspace():
            i += 1
            continue
        brace = css.find("{", i)
        semi = css.find(";", i)
        if brace == -1:
            break
        if semi != -1 and semi < brace:  # statement at-rule, e.g. @import ...;
            out.append(css[i:semi + 1].strip())
            i = semi + 1
            continue
        prelude = css[i:brace].strip()
        inner, after = read_block(brace)
        if prelude.startswith("@"):
            kw = prelude.split(None, 1)[0].lower()
            if kw in ("@media", "@supports", "@container", "@layer", "@-moz-document"):
                out.append(f"{prelude} {{\n{_scope_css(inner, scope)}\n}}")
            else:  # @keyframes, @font-face, @page — keep verbatim
                out.append(f"{prelude} {{{inner}}}")
        else:
            out.append(f"{_prefix_selector(prelude, scope)} {{{inner}}}")
        i = after
    return "\n".join(out)


def build_canvas_content(html_path: Path, scope_css: bool = False) -> str:
    """Build post_content for a direct-HTML (non-Elementor) page.

    Hoists every <style> into one block and wraps the design's <body> markup in
    a single Gutenberg Custom HTML block, scoped under a `.od-embed` div. On the
    `elementor_canvas` template (chrome-free) this renders the Open Design page
    verbatim — no widget conversion, no kit globals, no per-post CSS regen. The
    admin app-password has `unfiltered_html`, so the raw <style>/markup is stored
    and served intact. See open_design_integration/SKILL.md.

    When `scope_css` is True (header/footer templates), every CSS selector is
    prefixed with `.od-embed` so the design's generic rules don't restyle the
    theme's header/footer chrome."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    css = "\n".join(s.get_text() for s in soup.find_all("style"))
    # Preserve JSON-LD structured data (FAQPage, Product, etc.) — it's valid SEO
    # markup, not styling or executable JS, so it must survive the strip below.
    # (Re-emitted inside the block; Google reads JSON-LD anywhere in the document.)
    ld_scripts = [s.decode() for s in soup.find_all(
        "script", attrs={"type": "application/ld+json"})]
    for s in soup.find_all(["style", "script"]):
        s.decompose()
    body = soup.find("body")
    body_html = body.decode_contents() if body else str(soup)
    if scope_css:
        css = _scope_css(css, ".od-embed")
    ld_block = ("\n" + "\n".join(ld_scripts)) if ld_scripts else ""
    inner = (f'<div class="od-embed">\n<style>\n{css}\n</style>\n'
             f'{body_html}\n</div>{ld_block}')
    return f'<!-- wp:html -->\n{inner}\n<!-- /wp:html -->'


def cmd_deploy_canvas(html_path: str, title: str, slug: str = None,
                      page_id: int = None, status: str = "draft",
                      header_footer: bool = False):
    """Deploy an Open Design HTML page DIRECTLY (no Elementor) as a Custom HTML
    block. This is the preferred path for design-system pages — highest fidelity,
    one REST write, no conversion or CSS-regeneration steps.

    Default template is the chrome-free `elementor_canvas`. Pass
    `header_footer=True` to use `elementor_header_footer` instead (keeps the
    site's Elementor header + footer, full-width content); the design's CSS is
    then scoped under `.od-embed` so it can't restyle the header/footer chrome.
    See open_design_integration/SKILL.md."""
    html_file = Path(html_path)
    if not html_file.exists():
        print(f"  ❌ HTML file not found: {html_path}")
        return
    if not slug:
        slug = re.sub(r'[^a-z0-9-]', '-', title.lower()).strip('-')

    template = "elementor_header_footer" if header_footer else "elementor_canvas"
    content = build_canvas_content(html_file, scope_css=header_footer)
    meta_desc = extract_meta_description(html_file)
    payload = {
        "title": title,
        "slug": slug,
        "content": content,
        "status": status,
        "template": template,
        "meta": {
            "_yoast_wpseo_metadesc": meta_desc,
            # Disable Elementor on this post so the frontend renders post_content
            # (our HTML) instead of any stale _elementor_data.
            "_elementor_edit_mode": "",
        },
    }
    chrome = "with site header/footer" if header_footer else "chrome-free canvas"
    print(f"\n  🚀 Deploying '{title}' as a direct-HTML page ({chrome})...")
    print(f"     Template: {template}")
    print(f"     Content: {len(content)} chars (1 Custom HTML block)")
    try:
        if page_id:
            result = wp_api(f"pages/{page_id}", method="PUT", data=payload)
            action = "Updated"
        else:
            result = wp_api("pages", method="POST", data=payload)
            action = "Created"
        page_url = result.get("link", "")
        print(f"  ✅ {action} canvas page: {result.get('id')}")
        print(f"     View: {page_url}")
        print(f"     Template: {result.get('template') or '(default)'}")
    except Exception as e:
        print(f"  ❌ Canvas deployment failed: {e}")


def _merge_kit_into_active_kit(kit_settings: dict) -> None:
    """Merge converted colors/typography globals into the site's active Elementor
    kit, deduped by _id. Without this, converted widgets referencing __globals__
    color/font IDs render with Elementor's defaults instead of the design's colors."""
    kits = wp_api("elementor_library?elementor_library_type=kit&per_page=1")
    if not kits:
        print("  ⚠️  No active Elementor kit found — skipping global color/font merge")
        return
    kit_id = kits[0]["id"]
    kit_post = wp_api(f"elementor_library/{kit_id}?context=edit")
    page_settings = kit_post.get("meta", {}).get("_elementor_page_settings", {}) or {}

    for key in ("system_colors", "custom_colors"):
        existing = {c["_id"]: c for c in page_settings.get(key, [])}
        for c in kit_settings.get(key, []):
            existing[c["_id"]] = c
        page_settings[key] = list(existing.values())

    for key in ("system_typography", "custom_typography"):
        existing = {t["_id"]: t for t in page_settings.get(key, [])}
        for t in kit_settings.get(key, []):
            existing[t["_id"]] = t
        page_settings[key] = list(existing.values())

    wp_api(f"elementor_library/{kit_id}", method="PUT",
           data={"meta": {"_elementor_page_settings": page_settings}})
    print("  ✅ Merged color/typography globals into active kit")


def _flush_elementor_css(page_id: int) -> None:
    """Clear cached CSS so the newly written _elementor_data actually renders.
    Elementor regenerates '_elementor_css' lazily; an empty meta update forces it."""
    wp_api(f"pages/{page_id}", method="PUT", data={"meta": {"_elementor_css": ""}})
    print("  ✅ Flushed Elementor CSS cache")


def cmd_deploy_elementor(html_path: str, title: str, slug: str = None,
                         page_id: int = None, status: str = "draft"):
    """Deploy HTML as an Elementor page via the html2elementor converter
    (CSS-cascade-aware — do not hand-roll a simpler HTML-widget conversion here;
    see elementor_builder/SKILL.md for why)."""
    html_file = Path(html_path)
    if not html_file.exists():
        print(f"  ❌ HTML file not found: {html_path}")
        return

    if str(HTML2ELEMENTOR_DIR) not in sys.path:
        sys.path.insert(0, str(HTML2ELEMENTOR_DIR))
    from html2elementor import convert

    html = html_file.read_text(encoding="utf-8")
    meta_desc = extract_meta_description(html_file)

    if not slug:
        slug = re.sub(r'[^a-z0-9-]', '-', title.lower()).strip('-')

    result = convert(html, html_path=str(html_file))
    elementor_data = result["layout"]

    payload = {
        "title": title,
        "slug": slug,
        "status": status,
        "meta": {
            "_elementor_data": json.dumps(elementor_data, ensure_ascii=False),
            "_elementor_edit_mode": "builder",
            "_elementor_template_type": "wp-page",
            "_elementor_version": "3.27.0",
            "_yoast_wpseo_metadesc": meta_desc,
        }
    }

    print(f"\n  🎨 Deploying Elementor page '{title}' via html2elementor...")
    print(f"     Sections converted: {len(elementor_data)}")

    try:
        if page_id:
            result_post = wp_api(f"pages/{page_id}", method="PUT", data=payload)
            action = "Updated"
        else:
            result_post = wp_api("pages", method="POST", data=payload)
            action = "Created"

        _merge_kit_into_active_kit(result["kit"])
        _flush_elementor_css(result_post["id"])

        page_url = result_post.get("link", "")
        print(f"  ✅ {action} Elementor page: {result_post.get('id')}")
        print(f"     View: {page_url}")
        print(f"     Edit with Elementor: {os.getenv('WORDPRESS_SITE_URL', '')}/wp-admin/post.php?post={result_post.get('id')}&action=elementor")
        print("     Next: run verify_fidelity.py against this page — see elementor_builder/SKILL.md")

    except Exception as e:
        print(f"  ❌ Elementor deployment failed: {e}")


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Open Design ↔ Agent Website Manager Bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python open_design_bridge.py list-systems
  python open_design_bridge.py sync-system fracktal-works
  python open_design_bridge.py deploy --html outputs/design_pages/home.html --title "Home" --slug "home"
  python open_design_bridge.py deploy --html page.html --title "About" --slug "about" --id 123
  python open_design_bridge.py deploy-elementor --html page.html --title "Landing Page"
        """
    )
    sub = parser.add_subparsers(dest="command")
    
    # list-systems
    sub.add_parser("list-systems", help="List available design systems")
    
    # sync-system
    sync_p = sub.add_parser("sync-system", help="Sync design system from Open Design")
    sync_p.add_argument("name", help="Design system name (e.g. fracktal-works)")
    
    # deploy
    deploy_p = sub.add_parser("deploy", help="Deploy HTML page to WordPress")
    deploy_p.add_argument("--html", required=True, help="Path to HTML file")
    deploy_p.add_argument("--title", required=True, help="Page title")
    deploy_p.add_argument("--slug", required=True, help="URL slug")
    deploy_p.add_argument("--type", default="page", choices=["page", "post"], help="Content type")
    deploy_p.add_argument("--id", type=int, help="Existing page ID to update")
    deploy_p.add_argument("--status", default="draft", choices=["draft", "publish", "pending"])
    deploy_p.add_argument("--parent", type=int, default=0, help="Parent page ID")
    
    # deploy-canvas (direct HTML, no Elementor — preferred for design pages)
    canvas_p = sub.add_parser("deploy-canvas",
                              help="Deploy HTML directly (no Elementor) on the canvas template")
    canvas_p.add_argument("--html", required=True, help="Path to HTML file")
    canvas_p.add_argument("--title", required=True, help="Page title")
    canvas_p.add_argument("--slug", help="URL slug (auto-generated if omitted)")
    canvas_p.add_argument("--id", type=int, help="Existing page ID to update")
    canvas_p.add_argument("--status", default="draft", choices=["draft", "publish", "pending"])
    canvas_p.add_argument("--header-footer", action="store_true",
                          help="Keep the site's Elementor header/footer (uses "
                               "elementor_header_footer template + scopes the "
                               "design CSS under .od-embed)")

    # deploy-elementor
    elem_p = sub.add_parser("deploy-elementor", help="Deploy HTML as Elementor page")
    elem_p.add_argument("--html", required=True, help="Path to HTML file")
    elem_p.add_argument("--title", required=True, help="Page title")
    elem_p.add_argument("--slug", help="URL slug (auto-generated if omitted)")
    elem_p.add_argument("--id", type=int, help="Existing page ID to update")
    elem_p.add_argument("--status", default="draft", choices=["draft", "publish", "pending"])

    args = parser.parse_args()
    
    if args.command == "list-systems":
        cmd_list_systems()
    elif args.command == "sync-system":
        cmd_sync_system(args.name)
    elif args.command == "deploy":
        cmd_deploy(args.html, args.title, args.slug, args.type, args.id, args.status, args.parent)
    elif args.command == "deploy-canvas":
        cmd_deploy_canvas(args.html, args.title, args.slug, args.id, args.status,
                          args.header_footer)
    elif args.command == "deploy-elementor":
        cmd_deploy_elementor(args.html, args.title, args.slug, args.id, args.status)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
