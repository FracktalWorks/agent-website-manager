#!/usr/bin/env python
"""Workspace shell — the app window Open Design used to be.

    python hub.py              # serve http://127.0.0.1:8780, open browser
    python hub.py --no-open    # serve only

A persistent shell around everything this repo can show, so nothing is ever a
dead end: a top tab bar whose ⌂ Home is always one click away, and a
contextual sidebar beside a viewer pane. Opening a project or a design system
adds a tab (Open Design's prefix-encoded tab ids: `project:x`, `ds:y`); each
tab keeps its iframe alive, so switching never reloads an editor mid-edit.
Tabs survive page reloads (localStorage) and the hash routes them, so the
browser's back/forward buttons walk the tab history.

**Home** — every generated site under `outputs/*/site` as a card with a live,
scaled-down iframe of its own editor (SSE reload makes edits appear here as
they happen), plus the searchable 152-package design-system corpus with
palette swatches parsed from each `tokens.css`.

**A project tab** — the site's live editor, with the sidebar listing every
page from `dist/site-manifest.json` (filterable; click to open in the pane).
The editor announces its current page over cross-origin postMessage, so the
list tracks navigation done inside the frame too.

**A design-system tab** — the package's own `components.html` fixture with
its colour/type/spacing previews in the sidebar, the `brandkit.py apply <id>`
command, and a quick switcher over all systems.

The shell never edits anything itself: it launches editors and serves files.
That is why its only POST endpoints are "start this editor" and "stop the one
you started", and why they are pinned to loopback Origin/Host like the
editor's own mutating routes.
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import threading
import webbrowser
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"
CORPUS = ROOT / "agent-data" / "design-systems"
PORT = 8780
HUB_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}

# The corpus carries CJK names; Windows consoles default to cp1252 and a
# print() mid-request would otherwise raise and kill the handler thread.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(ROOT / ".tmp" / "scripts"))
try:
    import design_systems as _ds
except Exception:                                     # noqa: BLE001
    _ds = None


# ── projects ─────────────────────────────────────────────────────────────────

def discover_projects() -> list[dict]:
    """Every site in outputs/, with a stable port each.

    drvarada-site keeps 8789 — its editor's default, which the parity tests
    and the existing VS Code task already point at. Everything else counts up
    from 8791 in name order, so a project's port never depends on what else
    happens to exist that day.
    """
    sites = sorted(p for p in OUTPUTS.glob("*/site/build.py"))
    out, nxt = [], 8791
    for b in sites:
        site = b.parent
        pid = site.parent.name
        if pid == "drvarada-site":
            port = 8789
        else:
            port = nxt
            nxt += 1
        title, pages = pid.replace("-", " ").title(), 0
        manifest = site / "dist" / "site-manifest.json"
        try:
            m = json.loads(manifest.read_text(encoding="utf-8"))
            pages = len(m.get("pages", []))
            first = (m.get("pages") or [{}])[0].get("title", "")
            # "Dermatologist in Hyderabad … | Dr. Varada's" → the brand half
            if "|" in first:
                title = first.rsplit("|", 1)[1].strip() or title
            site_url = m.get("site", "")
        except (OSError, json.JSONDecodeError):
            site_url = ""
        out.append({"id": pid, "dir": str(site), "title": title,
                    "pages": pages, "port": port, "site": site_url,
                    "mtime": manifest.stat().st_mtime
                    if manifest.exists() else 0.0})
    # Open Design sorts its project shelf by recency, and it is the right
    # call: the site you touched last is the one you came back for.
    out.sort(key=lambda p: -p["mtime"])
    return out


def port_alive(port: int) -> bool:
    probe = socket.socket()
    probe.settimeout(0.25)
    try:
        return probe.connect_ex(("127.0.0.1", port)) == 0
    finally:
        probe.close()


_spawned: dict[str, subprocess.Popen] = {}


def start_editor(project: dict) -> dict:
    if port_alive(project["port"]):
        return {"ok": True, "url": f"http://127.0.0.1:{project['port']}/",
                "already": True}
    proc = subprocess.Popen(
        [sys.executable, "editor.py", "--no-open", "--port",
         str(project["port"])],
        cwd=project["dir"], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    _spawned[project["id"]] = proc
    # editor.py binds before it builds, so a short wait is enough to know the
    # server exists; the page itself shows "building…" until the build lands.
    for _ in range(40):
        if port_alive(project["port"]):
            return {"ok": True, "url": f"http://127.0.0.1:{project['port']}/"}
        if proc.poll() is not None:
            break
        threading.Event().wait(0.15)
    return {"error": "the editor did not come up — run it by hand to see why: "
                     f"cd {project['dir']} && python editor.py"}


def stop_editor(project: dict) -> dict:
    proc = _spawned.pop(project["id"], None)
    if proc is None:
        return {"error": "that editor was not started from the hub — stop it "
                         "in its own terminal"}
    proc.terminate()
    return {"ok": True}


_apply_lock = threading.Lock()


def create_project(req: dict) -> dict:
    """Open Design's home-composer flow, grounded: '+ New project' runs the
    real scaffolder, so what appears on the shelf builds, verifies and edits
    from its first minute. Optionally restyles it into a corpus brand."""
    name = str(req.get("name") or "").strip().lower()
    title = str(req.get("title") or "").strip() or name.replace("-", " ").title()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,30}", name):
        return {"error": "Name must be a short slug: letters, digits, dashes."}
    if (OUTPUTS / f"{name}-site").exists():
        return {"error": f"outputs/{name}-site already exists."}
    script = (ROOT / ".github" / "skills" / "site_generator" / "scripts"
              / "new_site.py")
    if not _apply_lock.acquire(blocking=False):
        return {"error": "another build is already running — wait for it"}
    try:
        r = subprocess.run(
            [sys.executable, str(script), name, "--title", title],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=600,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        if r.returncode != 0:
            return {"error": "\n".join(out.splitlines()[-12:])
                    or "new_site.py failed"}
        ds = str(req.get("ds") or "")
        note = ""
        if ds and re.fullmatch(r"[\w-]+", ds) and (CORPUS / ds).is_dir():
            r2 = subprocess.run(
                [sys.executable, "brandkit.py", "apply", ds],
                cwd=str(OUTPUTS / f"{name}-site" / "site"),
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=300,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            note = ("brand applied: " + ds if r2.returncode == 0 else
                    "brandkit refused " + ds + " — site keeps its defaults:\n"
                    + "\n".join(((r2.stdout or "") + (r2.stderr or ""))
                                .splitlines()[-6:]))
        return {"ok": True, "id": f"{name}-site",
                "output": "\n".join(out.splitlines()[-8:]), "note": note}
    except subprocess.TimeoutExpired:
        return {"error": "the scaffold timed out"}
    finally:
        _apply_lock.release()


def ds_brief(req: dict) -> dict:
    """'+ Create design system' — the deterministic half is writing a brief
    the agent picks up; the measuring and authoring is agent work
    (design_system_management §4), not something a button should fake."""
    name = str(req.get("name") or "").strip()
    if not name:
        return {"error": "Give the system a name."}
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "unnamed"
    briefs = ROOT / "inputs" / "briefs"
    briefs.mkdir(parents=True, exist_ok=True)
    f = briefs / f"design-system-{slug}.md"
    if f.exists():
        return {"error": f"a brief for '{slug}' already exists: "
                         f"inputs/briefs/{f.name}"}
    src = str(req.get("source") or "").strip()
    notes = str(req.get("notes") or "").strip()
    f.write_text(
        f"# Design-system brief — {name}\n\n"
        f"- requested: {__import__('time').strftime('%Y-%m-%d %H:%M')}\n"
        f"- source to measure: {src or '(none given — path B, seeded from the notes)'}\n\n"
        f"## Notes from the user\n\n{notes or '(none)'}\n\n"
        "## For the agent\n\n"
        "Build this with `.github/skills/design_system_management/SKILL.md` "
        "§4 (path A if a source URL is given — measure, don't recall; "
        "path B otherwise) and §4b for the site-owned package shape "
        "(`system/variables.css` + `kit/metadata.json` + `kit/preview/*.html`) "
        "so it appears in the workspace shell automatically.\n",
        encoding="utf-8")
    return {"ok": True, "file": f"inputs/briefs/{f.name}"}


def apply_design(project: dict, ds_id: str) -> dict:
    """Open Design's design-system picker flow, adapted: restyle a project
    into a corpus brand from the shell.

    The work is the site's own `brandkit.py apply` — OKLab derivation and the
    AA contrast gate included — so the shell adds reach, not a second
    implementation. The site's file watcher sees the changed CSS and rebuilds,
    which live-reloads every open editor view of that project by itself.
    """
    if not re.fullmatch(r"[\w-]+", ds_id) or not (CORPUS / ds_id).is_dir():
        return {"error": f"no design system called '{ds_id}'"}
    if not (Path(project["dir"]) / "brandkit.py").exists():
        return {"error": "this project has no brandkit.py"}
    if not _apply_lock.acquire(blocking=False):
        return {"error": "another apply is already running — wait for it"}
    try:
        r = subprocess.run(
            [sys.executable, "brandkit.py", "apply", ds_id],
            cwd=project["dir"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        tail = "\n".join(out.splitlines()[-14:])
        return {"ok": r.returncode == 0, "output": tail} if r.returncode == 0 \
            else {"error": tail or "brandkit refused the apply"}
    except subprocess.TimeoutExpired:
        return {"error": "brandkit timed out after 300s"}
    finally:
        _apply_lock.release()


# ── design systems ───────────────────────────────────────────────────────────

COLOR_RE = re.compile(
    r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8}\b|oklch\([^)]*\)|rgba?\([^)]*\)|"
    r"hsla?\([^)]*\))")
FONT_RE = re.compile(r"--(?:font|type)[\w-]*\s*:\s*([^;]+);")
_ds_cache: list[dict] | None = None


def swatches(css: str) -> list[str]:
    """A palette summary in declaration order — bg and ink first by convention,
    accents after — capped at six distinct values."""
    seen, out = set(), []
    for _name, value in COLOR_RE.findall(css):
        v = value.strip()
        if v.lower() in seen:
            continue
        seen.add(v.lower())
        out.append(v)
        if len(out) == 6:
            break
    return out


def _read_css(f: Path) -> str:
    try:
        return f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _fonts(css: str) -> list[str]:
    fonts = [f.split(",")[0].strip().strip("'\"")
             for f in FONT_RE.findall(css)[:2]]
    return [f for f in fonts if f and not f.startswith("--")]


def corpus_index() -> list[dict]:
    """The 152 vendored packages — static, so parsed once per process."""
    global _ds_cache
    if _ds_cache is not None:
        return _ds_cache
    meta = {}
    if _ds is not None:
        try:
            meta = {m["id"]: m for m in _ds.list_systems()}
        except Exception:                             # noqa: BLE001
            meta = {}
    out = []
    for d in sorted(CORPUS.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        css = _read_css(d / "tokens.css")
        m = meta.get(d.name, {})
        files = ([["components", "components.html"]]
                 if (d / "components.html").exists() else [])
        if (d / "preview").is_dir():
            files += [[p.stem, f"preview/{p.stem}.html"]
                      for p in sorted((d / "preview").glob("*.html"))]
        out.append({
            "id": d.name, "scope": "official", "base": f"/ds/{d.name}/",
            "name": m.get("name") or d.name.replace("-", " ").title(),
            "category": m.get("category") or "",
            "blurb": m.get("blurb") or "",
            "legacy": bool(m.get("legacy")),
            "swatches": swatches(css),
            "fonts": _fonts(css),
            "files": files,
        })
    _ds_cache = out
    return out


# The order a user system's preview pages should lead with — the pages that
# read as "this is the brand" — before the alphabetical rest.
USER_PREVIEW_LEAD = ("colors-primary", "typography-specimens",
                     "components-buttons", "components-cards")


def user_index() -> list[dict]:
    """Site-owned design systems, discovered in place and re-read every
    request — the live editor's tokens panel writes `system/variables.css`,
    and a stale swatch row would misreport the one system the user actually
    edits. Contract (what makes a directory ingestible): `system/variables.css`
    holding the `:root` tokens; optionally `kit/metadata.json` (title,
    category, status), `brand.json` (tagline), `kit/preview/*.html`."""
    out = []
    for d in sorted(OUTPUTS.glob("*/design-system")):
        tokens = d / "system" / "variables.css"
        if not tokens.exists():
            tokens = d / "kit" / "colors_and_type.css"
            if not tokens.exists():
                continue
        site = d.parent.name
        meta, brand = {}, {}
        for target, f in ((meta, d / "kit" / "metadata.json"),
                          (brand, d / "brand.json")):
            try:
                target.update(json.loads(f.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                pass
        css = _read_css(tokens)
        previews = {p.stem: f"kit/preview/{p.name}"
                    for p in sorted((d / "kit" / "preview").glob("*.html"))} \
            if (d / "kit" / "preview").is_dir() else {}
        files = [[stem, previews.pop(stem)] for stem in USER_PREVIEW_LEAD
                 if stem in previews]
        files += [[stem, path] for stem, path in previews.items()]
        out.append({
            "id": f"mine-{site}", "scope": "mine", "base": f"/dsu/{site}/",
            "name": meta.get("title") or brand.get("title")
            or site.replace("-", " ").title(),
            "category": "Your systems",
            "blurb": brand.get("tagline") or meta.get("category") or "",
            "legacy": False,
            "swatches": swatches(css),
            "fonts": _fonts(css),
            "files": files,
        })
    return out


def design_index() -> list[dict]:
    return user_index() + corpus_index()


# ── page ─────────────────────────────────────────────────────────────────────

def render_home(projects: list[dict]) -> str:
    cards = []
    for p in projects:
        running = port_alive(p["port"])
        url = f"http://127.0.0.1:{p['port']}/"
        thumb = (
            f'<div class="thumb"><iframe src="{url}" loading="lazy" '
            'tabindex="-1"></iframe></div>' if running else
            '<div class="thumb empty"><span>editor not running</span></div>')
        cards.append(
            f'<article class="proj" data-id="{escape(p["id"])}" '
            f'data-port="{p["port"]}" data-title="{escape(p["title"])}">'
            + thumb +
            '<div class="meta">'
            f'<h3>{escape(p["title"])}</h3>'
            f'<p>{escape(p["id"])} · {p["pages"]} pages'
            + (f' · <span data-mtime="{p["mtime"]:.0f}"></span>'
               if p["mtime"] else "")
            + (f' · <a href="{escape(p["site"])}" target="_blank" rel="noopener">'
               f'{escape(p["site"].replace("https://", ""))}</a>' if p["site"]
               else "") + "</p>"
            '<div class="acts">'
            '<button class="btn primary" data-open>'
            + ("Open" if running else "Start &amp; open") + "</button>"
            + ('<button class="btn" data-stop>Stop</button>'
               if running and p["id"] in _spawned else "")
            + '</div></div>'
            f'<span class="dot{" on" if running else ""}"></span>'
            "</article>")

    systems = design_index()
    ds_cards = []
    for s in systems:
        sw = "".join(f'<i style="background:{escape(c)}"></i>'
                     for c in s["swatches"])
        fonts = escape(" · ".join(s["fonts"][:2]))
        mine = s["scope"] == "mine"
        ds_cards.append(
            f'<article class="ds{" mine" if mine else ""}" '
            f'data-id="{escape(s["id"])}" '
            f'data-dsname="{escape(s["name"])}" '
            f'data-name="{escape(s["id"] + " " + s["name"] + " " + s["category"] + " " + s["blurb"]).lower()}" '
            f'data-cat="{escape(s["category"])}">'
            f'<div class="sw">{sw or "<i></i>"}</div>'
            f'<h4>{escape(s["name"])}'
            + (' <em class="yours">yours</em>' if mine else "")
            + (' <em>legacy</em>' if s["legacy"] else "") + "</h4>"
            f'<p class="cat">{escape(s["category"])}</p>'
            f'<p class="blurb">{escape(s["blurb"])}</p>'
            + (f'<p class="fonts">{fonts}</p>' if fonts else "")
            + (f'<code>python brandkit.py apply {escape(s["id"])}</code>'
               if not mine else
               '<code>edited live by its site’s editor (Tokens panel)</code>')
            + "</article>")

    cats = sorted({s["category"] for s in systems if s["category"]})
    options = "".join(f'<option>{escape(c)}</option>' for c in cats)
    n_mine = sum(1 for s in systems if s["scope"] == "mine")
    count = (f"{n_mine} yours · {len(systems) - n_mine} vendored"
             if n_mine else f"{len(systems)} vendored")
    # The sidebar needs each system's file list without a round trip per
    # system; ship the index once, as data.
    ds_data = {s["id"]: {"name": s["name"], "scope": s["scope"],
                         "base": s["base"], "files": s["files"],
                         "sw": s["swatches"][:6], "blurb": s["blurb"]}
               for s in systems}

    return HOME_TMPL \
        .replace("{{PROJECTS}}", "".join(cards) or
                 "<p class='none'>No sites yet — scaffold one with "
                 "<code>python .github/skills/site_generator/scripts/"
                 "new_site.py &lt;name&gt;</code></p>") \
        .replace("{{DS}}", "".join(ds_cards)) \
        .replace("{{DS_COUNT}}", count) \
        .replace("{{CATS}}", options) \
        .replace("{{DSDATA}}", json.dumps(ds_data).replace("</", "<\\/"))


HOME_TMPL = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Website Manager — workspace</title>
<style>
:root { --bg:#0f1218; --top:#0b0d12; --panel:#14171e; --line:#2a2f3a;
  --fg:#e8ebf2; --mut:#8b93a4; --blue:#2f6df6; }
* { box-sizing:border-box }
html, body { height:100% }
body { margin:0; background:var(--bg); color:var(--fg);
  font:14px/1.5 system-ui,sans-serif; display:flex; flex-direction:column;
  overflow:hidden }

/* ── persistent top bar: home + tabs, always reachable ── */
#top { flex:0 0 40px; display:flex; align-items:stretch; gap:2px;
  background:var(--top); border-bottom:1px solid var(--line);
  padding:6px 8px 0 }
.tab { display:flex; align-items:center; gap:8px; max-width:220px;
  padding:0 12px; border:1px solid transparent; border-bottom:0;
  border-radius:8px 8px 0 0; background:none; color:var(--mut);
  font:600 12.5px/1 system-ui; cursor:pointer; white-space:nowrap }
.tab .t { overflow:hidden; text-overflow:ellipsis }
.tab:hover { color:var(--fg) }
.tab.active { background:var(--bg); border-color:var(--line);
  color:var(--fg) }
.tab .x { display:grid; place-items:center; width:16px; height:16px;
  border-radius:4px; font-size:11px; color:var(--mut) }
.tab .x:hover { background:#2a3140; color:#fff }
#tabs { display:flex; align-items:stretch; gap:2px; overflow-x:auto;
  scrollbar-width:none }
.tab.dragging { opacity:.85 }
#qs-btn { margin-left:auto; align-self:center; width:28px; height:28px;
  border:1px solid transparent; border-radius:8px; background:none;
  color:var(--mut); font-size:15px; cursor:pointer }
#qs-btn:hover { color:var(--fg); border-color:var(--line) }

/* ── quick switcher (Ctrl+P), Open Design's Cmd+P surface ── */
#qs { position:fixed; inset:0; z-index:50; background:rgba(5,7,10,.55) }
#qs[hidden] { display:none }
#qs-box { width:min(560px, calc(100vw - 40px)); margin:12vh auto 0;
  background:var(--panel); border:1px solid var(--line); border-radius:14px;
  box-shadow:0 30px 90px rgba(0,0,0,.6); overflow:hidden }
#qs-in { width:100%; border:0; outline:none; background:none; color:var(--fg);
  font:15px system-ui; padding:14px 16px;
  border-bottom:1px solid var(--line) }
#qs-list { max-height:46vh; overflow:auto; padding:6px }
.qs-row { display:flex; gap:10px; align-items:center; width:100%;
  padding:8px 10px; border:0; border-radius:8px; background:none;
  color:var(--fg); font:500 13px system-ui; cursor:pointer; text-align:left }
.qs-row small { color:var(--mut); margin-left:auto; flex:0 0 auto }
.qs-row.sel { background:var(--blue); color:#fff }
.qs-row.sel small { color:#dfe8ff }

/* ── modal dialogs (new project / new design system) ── */
#side-toggle { align-self:center; width:28px; height:28px; margin-left:6px;
  border:1px solid transparent; border-radius:8px; background:none;
  color:var(--mut); font-size:13px; cursor:pointer }
#side-toggle:hover { color:var(--fg); border-color:var(--line) }
body.no-side #side { display:none }
h2 .h2btn { margin-left:10px; text-transform:none; letter-spacing:0;
  font-size:12px; padding:5px 10px; vertical-align:1px }
#modal { position:fixed; inset:0; z-index:60; background:rgba(5,7,10,.6) }
#modal[hidden] { display:none }
#modal-box { width:min(640px, calc(100vw - 40px)); margin:9vh auto 0;
  background:var(--panel); border:1px solid var(--line); border-radius:14px;
  box-shadow:0 30px 90px rgba(0,0,0,.6); padding:18px 20px }
#modal-box h3 { margin:0 0 12px; font-size:15px }
#modal-box label { display:block; margin-bottom:10px; font-size:11.5px;
  font-weight:600; text-transform:uppercase; letter-spacing:.04em;
  color:var(--mut) }
#modal-box input[type=text], #modal-box textarea { display:block; width:100%;
  margin-top:5px; font:13px system-ui; padding:8px 10px; border-radius:8px;
  border:1px solid var(--line); background:#0e1116; color:var(--fg) }
#modal-box textarea { resize:vertical }
.pick { display:grid; grid-template-columns:1fr 200px; gap:10px;
  border:1px solid var(--line); border-radius:10px; padding:8px;
  margin-top:5px }
.pick-list { max-height:200px; overflow:auto }
.pick-group { font-size:10px; letter-spacing:.08em; text-transform:uppercase;
  color:var(--mut); padding:6px 8px 3px }
.pick-item { display:block; width:100%; text-align:left; padding:6px 8px;
  border:0; border-radius:7px; background:none; color:var(--fg);
  font:500 12.5px system-ui; cursor:pointer }
.pick-item:hover { background:#1d222c }
.pick-item.on { background:var(--blue); color:#fff }
.pick-side { border-left:1px solid var(--line); padding-left:10px;
  font-size:11.5px; color:var(--mut) }
.pick-side .sw { display:flex; height:18px; border-radius:5px;
  overflow:hidden; border:1px solid var(--line); margin-bottom:7px }
.pick-side .sw i { flex:1 }
.modal-acts { display:flex; gap:8px; justify-content:flex-end;
  margin-top:14px }
.modal-out { font:11px ui-monospace,monospace; white-space:pre-wrap;
  background:#0e1116; border-radius:8px; padding:8px 10px; margin-top:10px;
  max-height:180px; overflow:auto; color:var(--mut) }

/* ── shell: contextual sidebar + content ── */
#wrap { flex:1; display:flex; min-height:0 }
#side { flex:0 0 236px; border-right:1px solid var(--line);
  background:var(--top); overflow-y:auto; padding:10px 8px }
#side h5 { margin:10px 6px 6px; font-size:10.5px; text-transform:uppercase;
  letter-spacing:.08em; color:var(--mut) }
.sitem { display:flex; align-items:center; gap:7px; width:100%;
  padding:6px 8px; border:0; border-radius:7px; background:none;
  color:var(--fg); font:500 12.5px/1.3 system-ui; cursor:pointer;
  text-align:left }
.sitem small { color:var(--mut); font-size:10.5px; margin-left:auto;
  flex:0 0 auto }
.sitem:hover { background:#1d222c }
.sitem.on { background:var(--blue); color:#fff }
.sitem.on small { color:#dfe8ff }
.sitem.mono { font-family:ui-monospace,monospace; font-size:12px }
#side input { width:100%; margin:2px 0 6px; font:12.5px system-ui;
  padding:7px 9px; border-radius:7px; border:1px solid var(--line);
  background:#0e1116; color:var(--fg) }
#side .hint { margin:8px 6px; font-size:11px; color:var(--mut) }

#content { flex:1; position:relative; min-width:0 }
.view { position:absolute; inset:0; display:none }
.view.on { display:block }
section.view { overflow-y:auto }
iframe.view { width:100%; height:100%; border:0; background:#fff }

/* ── home view (grids) ── */
h2 { font-size:13px; text-transform:uppercase; letter-spacing:.08em;
  color:var(--mut); margin:22px 24px 12px }
.projects { display:grid; gap:16px; padding:0 24px;
  grid-template-columns:repeat(auto-fill,minmax(300px,1fr)) }
.proj { position:relative; background:var(--panel);
  border:1px solid var(--line); border-radius:14px; overflow:hidden }
/* Open Design's thumbnail trick: a 16/9 container-query box, the iframe laid
   out at 1280×720 and scaled by 100cqw/1280 — so the preview always fits the
   card exactly, whatever width the grid gives it. */
.thumb { aspect-ratio:16/9; container-type:inline-size; overflow:hidden;
  background:#0a0c10 }
.thumb iframe { width:1280px; height:720px; border:0;
  transform:scale(calc(100cqw / 1280px)); transform-origin:0 0;
  pointer-events:none }
.thumb.empty { display:grid; place-items:center; color:var(--mut);
  font-size:12.5px }
.meta { padding:12px 14px 14px }
.meta h3 { margin:0 0 2px; font-size:14.5px }
.meta p { margin:0 0 10px; color:var(--mut); font-size:12px }
.meta a { color:inherit }
.acts { display:flex; gap:8px }
.btn { font:600 12.5px/1 system-ui; padding:8px 12px; border-radius:8px;
  border:1px solid var(--line); background:#1d222c; color:var(--fg);
  cursor:pointer; text-decoration:none; display:inline-block }
.btn.primary { background:var(--blue); border-color:var(--blue); color:#fff }
.btn:hover { filter:brightness(1.15) }
.dot { position:absolute; top:10px; right:10px; width:9px; height:9px;
  border-radius:50%; background:#555; box-shadow:0 0 0 3px rgba(0,0,0,.35) }
.dot.on { background:#31c07a }
.dsbar { display:flex; gap:10px; padding:0 24px 12px; align-items:center }
.dsbar input, .dsbar select { font:13px system-ui; padding:8px 10px;
  border-radius:8px; border:1px solid var(--line); background:#0e1116;
  color:var(--fg) }
.dsbar input { width:280px }
.dsgrid { display:grid; gap:12px; padding:0 24px 40px;
  grid-template-columns:repeat(auto-fill,minmax(240px,1fr)) }
.ds { background:var(--panel); border:1px solid var(--line);
  border-radius:12px; padding:12px 14px; cursor:pointer }
.ds:hover { border-color:#46506a }
.ds .sw { display:flex; height:22px; border-radius:6px; overflow:hidden;
  border:1px solid var(--line); margin-bottom:9px; pointer-events:none }
.ds .sw i { flex:1 }
.ds h4 { margin:0; font-size:13.5px }
.ds h4 em { font-style:normal; font-size:10px; color:var(--mut);
  border:1px solid var(--line); border-radius:4px; padding:1px 4px;
  vertical-align:2px }
.ds.mine { border-color:#3d5f9e }
.ds h4 em.yours { background:var(--blue); border-color:var(--blue);
  color:#fff }
.ds .cat { margin:1px 0 4px; font-size:11px; color:var(--mut);
  text-transform:uppercase; letter-spacing:.05em }
.ds .blurb { margin:0 0 6px; font-size:12px; color:#c6ccd8 }
.ds .fonts { margin:0 0 6px; font-size:11.5px; color:var(--mut) }
.ds code { display:block; font:11px ui-monospace,monospace;
  color:var(--mut); background:#0e1116; border-radius:6px; padding:5px 7px;
  overflow-x:auto; white-space:nowrap }
.none { color:var(--mut); padding:0 24px }
</style></head><body>

<nav id="top">
  <button class="tab active" data-key="home"><span class="t">⌂ Workspace</span></button>
  <div id="tabs"></div>
  <button id="side-toggle" title="Toggle sidebar">▙</button>
  <button id="qs-btn" title="Jump anywhere (Ctrl+P)">⌕</button>
</nav>
<div id="modal" hidden><div id="modal-box"></div></div>
<div id="qs" hidden><div id="qs-box">
  <input id="qs-in" placeholder="Jump to a page, project or design system…">
  <div id="qs-list"></div>
</div></div>
<div id="wrap">
  <aside id="side"></aside>
  <main id="content">
    <section class="view on" id="view-home">
      <h2 id="sec-projects">Projects
        <button id="new-proj" class="btn h2btn">+ New project</button></h2>
      <div class="projects">{{PROJECTS}}</div>
      <h2 id="sec-ds">Design systems <span style="text-transform:none">({{DS_COUNT}})</span>
        <button id="new-ds" class="btn h2btn">+ Create</button></h2>
      <div class="dsbar">
        <input id="q" type="search" placeholder="Search — brand, mood, category…">
        <select id="cat"><option value="">All categories</option>{{CATS}}</select>
      </div>
      <div class="dsgrid">{{DS}}</div>
    </section>
  </main>
</div>

<script id="dsdata" type="application/json">{{DSDATA}}</script>
<script>
"use strict";
const DS = JSON.parse(document.getElementById('dsdata').textContent);
const $ = s => document.querySelector(s);
const content = $('#content'), side = $('#side'), tabsBox = $('#tabs');

/* ── tab model — Open Design's prefix-encoded tab ids ("project:x", "ds:y"),
   one kept-alive iframe per tab so switching never reloads an editor ── */
let tabs = new Map();            // key -> {key,kind,id,title,url,btn,frame,pages,current}
let active = 'home';

function projectMeta(id) {
  const card = document.querySelector('.proj[data-id="' + id + '"]');
  return card ? { title: card.dataset.title, port: +card.dataset.port } : null;
}

function makeTabBtn(t) {
  const b = document.createElement('button');
  b.className = 'tab';
  b.dataset.key = t.key;
  b.innerHTML = '<span class="t"></span><span class="x" title="Close">✕</span>';
  b.querySelector('.t').textContent =
    (t.kind === 'ds' ? '◈ ' : '▤ ') + t.title;
  b.onclick = e => {
    if (e.target.classList.contains('x')) closeTab(t.key);
    else activate(t.key);
  };
  b.onauxclick = e => { if (e.button === 1) closeTab(t.key); };
  // Open Design reorders live during dragover, not on drop — it reads as the
  // tab making room for you. Home is pinned structurally: it lives outside
  // this strip, so nothing can be dragged before it.
  b.draggable = true;
  b.addEventListener('dragstart', e => {
    b.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
  });
  b.addEventListener('dragend', () => {
    b.classList.remove('dragging');
    syncTabOrder();
  });
  tabsBox.appendChild(b);
  return b;
}

tabsBox.addEventListener('dragover', e => {
  const dragged = tabsBox.querySelector('.tab.dragging');
  if (!dragged) return;
  e.preventDefault();
  const over = e.target.closest('.tab');
  if (!over || over === dragged) return;
  const r = over.getBoundingClientRect();
  tabsBox.insertBefore(dragged,
    e.clientX > r.left + r.width / 2 ? over.nextSibling : over);
});

function syncTabOrder() {
  tabs = new Map([...tabsBox.children]
    .map(b => [b.dataset.key, tabs.get(b.dataset.key)])
    .filter(([, v]) => v));
  persist();
  if (active === 'home') renderSide();
}

function openTab(kind, id, title, url, focus) {
  const key = kind + ':' + id;
  if (!tabs.has(key)) {
    const t = { key, kind, id, title, url, frame: null, pages: null,
                current: null };
    t.btn = makeTabBtn(t);
    tabs.set(key, t);
  }
  if (focus !== false) activate(key);
  persist();
  return tabs.get(key);
}

function activate(key) {
  const t = key === 'home' ? null : tabs.get(key);
  if (key !== 'home' && !t) return;
  active = key;
  if (t && !t.frame) {           // lazy — a restored tab boots on first focus
    t.frame = document.createElement('iframe');
    t.frame.className = 'view';
    t.frame.src = t.url;
    content.appendChild(t.frame);
  }
  document.querySelectorAll('#top .tab').forEach(b =>
    b.classList.toggle('active', b.dataset.key === key));
  document.querySelectorAll('#content .view').forEach(v =>
    v.classList.remove('on'));
  (t ? t.frame : $('#view-home')).classList.add('on');
  renderSide();
  if ('#/' + key !== location.hash) {
    // A change that came FROM the history (back/forward) must not push a new
    // entry — that would erase the forward stack it just navigated.
    if (fromHash) history.replaceState(null, '', '#/' + key);
    else location.hash = '#/' + key;
  }
  persist();
}

function closeTab(key) {
  const t = tabs.get(key);
  if (!t) return;
  // Open Design's rule: closing the active tab activates the neighbour that
  // slides into its slot, falling back to Home only when none is left.
  const keys = [...tabs.keys()];
  const idx = keys.indexOf(key);
  t.btn.remove();
  if (t.frame) t.frame.remove();
  tabs.delete(key);
  if (active === key) {
    const rest = [...tabs.keys()];
    activate(rest.length ? rest[Math.min(idx, rest.length - 1)] : 'home');
  } else renderSide();             // the home sidebar lists open tabs
  persist();
}

function persist() {
  localStorage.setItem('awmTabs', JSON.stringify(
    [...tabs.values()].map(t => ({ kind: t.kind, id: t.id, title: t.title,
                                   url: t.url }))));
  localStorage.setItem('awmActive', active);
}

/* ── contextual sidebar ── */
function item(label, small, cls) {
  const b = document.createElement('button');
  b.className = 'sitem' + (cls ? ' ' + cls : '');
  b.innerHTML = '<span></span>' + (small ? '<small></small>' : '');
  b.firstChild.textContent = label;
  if (small) b.querySelector('small').textContent = small;
  return b;
}

function renderSide() {
  side.innerHTML = '';
  if (active === 'home') {
    side.insertAdjacentHTML('beforeend', '<h5>Workspace</h5>');
    const a = item('Projects'), b = item('Design systems');
    a.onclick = () => $('#sec-projects').scrollIntoView({ behavior: 'smooth' });
    b.onclick = () => $('#sec-ds').scrollIntoView({ behavior: 'smooth' });
    side.append(a, b);
    side.insertAdjacentHTML('beforeend', '<h5>Open tabs</h5>');
    if (!tabs.size)
      side.insertAdjacentHTML('beforeend',
        '<p class="hint">Open a project or a design system — it stays in ' +
        'the tab bar, and ⌂ always brings you back here.</p>');
    tabs.forEach(t => {
      const row = item(t.title, t.kind);
      row.onclick = () => activate(t.key);
      side.appendChild(row);
    });
    return;
  }
  const t = tabs.get(active);
  if (!t) return;
  if (t.kind === 'project') renderProjectSide(t);
  else renderDsSide(t);
}

function renderProjectSide(t) {
  side.insertAdjacentHTML('beforeend', '<h5>' + t.title + '</h5>');
  const nw = item('↗ Open in new window');
  nw.onclick = () => window.open(t.url, '_blank');
  side.appendChild(nw);
  side.insertAdjacentHTML('beforeend', '<h5>Pages</h5>');
  const box = document.createElement('div');
  side.appendChild(box);
  const paint = () => {
    box.innerHTML = '';
    const f = (filter.value || '').toLowerCase();
    (t.pages || []).forEach(pg => {
      if (f && !(pg.slug + ' ' + pg.title).toLowerCase().includes(f)) return;
      const row = item(pg.slug, pg.template, 'mono');
      row.title = pg.title;
      if (pg.slug === t.current) row.classList.add('on');
      row.onclick = () => {
        t.frame.src = 'http://127.0.0.1:' + t.port + '/' + pg.file;
        t.current = pg.slug;
        paint();
      };
      box.appendChild(row);
    });
  };
  const filter = document.createElement('input');
  filter.placeholder = 'Filter ' + ((t.pages || []).length || '') + ' pages…';
  filter.oninput = paint;
  side.insertBefore(filter, box);
  if (t.pages) { paint(); return; }
  fetch('/api/pages/' + t.id).then(r => r.json()).then(res => {
    t.pages = res.pages || [];
    t.port = res.port;
    filter.placeholder = 'Filter ' + t.pages.length + ' pages…';
    if (active === t.key) paint();
  });
}

function renderDsSide(t) {
  const meta = DS[t.id] || { name: t.id, base: '/ds/' + t.id + '/',
                             files: [], scope: 'official' };
  side.insertAdjacentHTML('beforeend', '<h5>' + t.title + '</h5>');
  meta.files.forEach(([label, file]) => {
    const row = item(label);
    if (t.current === file) row.classList.add('on');
    row.onclick = () => {
      t.frame.src = meta.base + file;
      t.current = file;
      renderSide();
    };
    side.appendChild(row);
  });
  if (meta.scope === 'official') {
    // Open Design's picker flow: choose a system, point it at a project.
    side.insertAdjacentHTML('beforeend', '<h5>Apply to project</h5>');
    document.querySelectorAll('.proj').forEach(c => {
      const row = item(c.dataset.title, 'brandkit');
      row.onclick = () => applyDs(t.id, c.dataset.id, c.dataset.title, row);
      side.appendChild(row);
    });
  } else {
    side.insertAdjacentHTML('beforeend',
      '<p class="hint">This system is owned by its site — edit it live in ' +
      'the project’s editor (Tokens panel), and these swatches follow.</p>');
  }
  side.insertAdjacentHTML('beforeend', '<h5>All systems</h5>');
  const q = document.createElement('input');
  q.placeholder = 'Switch system…';
  side.appendChild(q);
  const list = document.createElement('div');
  side.appendChild(list);
  const paint = () => {
    list.innerHTML = '';
    const f = q.value.trim().toLowerCase();
    Object.keys(DS).forEach(id => {
      if (f && !(id + ' ' + DS[id].name).toLowerCase().includes(f)) return;
      if (list.children.length >= 14) return;
      const row = item(DS[id].name);
      if (id === t.id) row.classList.add('on');
      row.onclick = () => openDs(id);
      list.appendChild(row);
    });
  };
  q.oninput = paint;
  paint();
}

/* ── openers ── */
function openProject(id) {
  const m = projectMeta(id);
  const title = m ? m.title : id;
  const card = document.querySelector('.proj[data-id="' + id + '"]');
  const running = card && card.querySelector('.dot').classList.contains('on');
  if (running && m) {
    return Promise.resolve(
      openTab('project', id, title, 'http://127.0.0.1:' + m.port + '/'));
  }
  return api('/api/open', { id }).then(res => {
    if (!res.url) { alert(res.error || 'failed'); return null; }
    if (card) {
      card.querySelector('.dot').classList.add('on');
      const btn = card.querySelector('[data-open]');
      if (btn) btn.textContent = 'Open';
    }
    return openTab('project', id, title, res.url);
  });
}

function openDs(id) {
  const meta = DS[id] || { name: id, base: '/ds/' + id + '/', files: [] };
  const entry = meta.files.length ? meta.files[0][1] : 'components.html';
  const t = openTab('ds', id, meta.name, meta.base + entry);
  t.current = entry;
  renderSide();
  return t;
}

function applyDs(ds, projectId, projectTitle, row) {
  const name = (DS[ds] || {}).name || ds;
  if (!confirm('Restyle "' + projectTitle + '" with ' + name + '?\n\n' +
      'brandkit derives the palette in OKLab, walks text colours to WCAG ' +
      'AA, and refuses a brand that cannot pass. The site rebuilds and any ' +
      'open editor reloads itself.')) return;
  const span = row.firstChild, was = span.textContent;
  span.textContent = 'applying…';
  row.disabled = true;
  api('/api/apply-ds', { id: projectId, ds }).then(res => {
    row.disabled = false;
    span.textContent = was;
    alert(res.ok ? 'Applied.\n\n' + (res.output || '')
                 : (res.error || 'failed'));
  });
}

/* ── home grid wiring ── */
async function api(route, body) {
  const r = await fetch(route, { method: 'POST',
    body: JSON.stringify(body || {}) });
  return r.json();
}
$('#top .tab[data-key="home"]').onclick = () => activate('home');
document.querySelectorAll('.proj').forEach(card => {
  const id = card.dataset.id;
  const open = card.querySelector('[data-open]');
  if (open) open.onclick = () => openProject(id);
  const stop = card.querySelector('[data-stop]');
  if (stop) stop.onclick = async () => {
    const res = await api('/api/stop', { id });
    if (res.error) { alert(res.error); return; }
    card.querySelector('.dot').classList.remove('on');
    stop.remove();
  };
});
document.querySelectorAll('.ds').forEach(card => {
  card.onclick = () => openDs(card.dataset.id);
});

// relative "updated …" stamps, computed client-side from manifest mtimes
document.querySelectorAll('[data-mtime]').forEach(el => {
  const s = (Date.now() / 1000) - (+el.dataset.mtime);
  el.textContent = 'updated ' + (
    s < 90 ? 'just now' :
    s < 5400 ? Math.round(s / 60) + 'm ago' :
    s < 129600 ? Math.round(s / 3600) + 'h ago' :
    Math.round(s / 86400) + 'd ago');
});

const q = $('#q'), cat = $('#cat');
function filt() {
  const terms = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const c = cat.value;
  document.querySelectorAll('.ds').forEach(el => {
    el.style.display =
      terms.every(x => el.dataset.name.includes(x)) &&
      (!c || el.dataset.cat === c) ? '' : 'none';
  });
}
q.oninput = filt; cat.onchange = filt;

/* ── editor → shell page announcements (cross-origin postMessage) ── */
window.addEventListener('message', e => {
  if (!e.data || e.data.od !== 'page') return;
  tabs.forEach(t => {
    if (t.frame && t.frame.contentWindow === e.source) {
      t.current = e.data.slug;
      if (active === t.key) renderSide();
    }
  });
});

/* ── modal + creation flows ── */
const modal = $('#modal'), modalBox = $('#modal-box');
const closeModal = () => { modal.hidden = true; modalBox.innerHTML = ''; };
modal.addEventListener('mousedown', e => { if (e.target === modal) closeModal(); });

// Open Design's design-system picker: search + YOUR SYSTEMS / OFFICIAL
// PRESETS groups + a swatch detail pane. Returns a getter for the choice.
function dsPicker(host) {
  let chosen = '';
  host.insertAdjacentHTML('beforeend',
    '<div class="pick"><div>' +
      '<input type="text" id="pick-q" placeholder="Search design systems…">' +
      '<div class="pick-list" id="pick-list"></div></div>' +
      '<div class="pick-side" id="pick-side">The scaffold ships neutral ' +
      'tokens; pick a brand to restyle it now, or apply one later.</div>' +
    '</div>');
  const list = host.querySelector('#pick-list');
  const sideEl = host.querySelector('#pick-side');
  const paint = () => {
    const f = host.querySelector('#pick-q').value.trim().toLowerCase();
    list.innerHTML = '';
    const add = (id, label, disabled) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'pick-item' + (chosen === id ? ' on' : '');
      b.textContent = label;
      if (disabled) { b.style.opacity = .45; b.title =
        'site-owned — already lives with its site'; }
      else b.onclick = () => {
        chosen = id;
        paint();
        const m = DS[id];
        sideEl.innerHTML = m ? '<div class="sw">' +
          m.sw.map(c => '<i style="background:' + c + '"></i>').join('') +
          '</div><b>' + m.name + '</b><br>' + (m.blurb || '') : 'No brand — neutral tokens.';
      };
      list.appendChild(b);
    };
    add('', 'No design system (neutral)', false);
    const groups = [['YOUR SYSTEMS', 'mine', true], ['OFFICIAL PRESETS', 'official', false]];
    groups.forEach(([label, scope, disabled]) => {
      const ids = Object.keys(DS).filter(id => DS[id].scope === scope &&
        (!f || (id + ' ' + DS[id].name).toLowerCase().includes(f)));
      if (!ids.length) return;
      list.insertAdjacentHTML('beforeend',
        '<div class="pick-group">' + label + '</div>');
      ids.forEach(id => add(id, DS[id].name, disabled));
    });
  };
  host.querySelector('#pick-q').oninput = paint;
  paint();
  return () => chosen;
}

$('#new-proj').onclick = () => {
  modalBox.innerHTML =
    '<h3>New project</h3>' +
    '<label>Slug <input type="text" id="np-name" placeholder="acme"></label>' +
    '<label>Brand name <input type="text" id="np-title" placeholder="Acme Ltd"></label>' +
    '<label>Design system</label>';
  const getDs = dsPicker(modalBox);
  modalBox.insertAdjacentHTML('beforeend',
    '<div class="modal-acts"><button class="btn" id="np-cancel">Cancel</button>' +
    '<button class="btn primary" id="np-go">Scaffold site</button></div>');
  modalBox.querySelector('#np-cancel').onclick = closeModal;
  modalBox.querySelector('#np-go').onclick = () => {
    const go = modalBox.querySelector('#np-go');
    go.textContent = 'Building…'; go.disabled = true;
    api('/api/new-project', {
      name: modalBox.querySelector('#np-name').value.trim(),
      title: modalBox.querySelector('#np-title').value.trim(),
      ds: getDs(),
    }).then(res => {
      if (!res.ok) {
        go.disabled = false; go.textContent = 'Scaffold site';
        modalBox.insertAdjacentHTML('beforeend',
          '<div class="modal-out">' + (res.error || 'failed') + '</div>');
        return;
      }
      // a new card needs a server render — reload into the new project
      location.hash = '#/project:' + res.id;
      location.reload();
    });
  };
  modal.hidden = false;
  modalBox.querySelector('#np-name').focus();
};

$('#new-ds').onclick = () => {
  modalBox.innerHTML =
    '<h3>Create a design system</h3>' +
    '<p class="hint" style="margin:0 0 10px">Authoring is agent work — ' +
    'measured from a real brand, never improvised. This writes a brief to ' +
    '<code>inputs/briefs/</code>; ask the agent to build it and it appears ' +
    'here when done.</p>' +
    '<label>Name <input type="text" id="nd-name" placeholder="Acme brand"></label>' +
    '<label>Source URL to measure (optional) ' +
      '<input type="text" id="nd-src" placeholder="https://…"></label>' +
    '<label>Notes <textarea id="nd-notes" rows="3" ' +
      'placeholder="mood, must-keep colours, typefaces…"></textarea></label>' +
    '<div class="modal-acts"><button class="btn" id="nd-cancel">Cancel</button>' +
    '<button class="btn primary" id="nd-go">Write brief</button></div>';
  modalBox.querySelector('#nd-cancel').onclick = closeModal;
  modalBox.querySelector('#nd-go').onclick = () => {
    api('/api/ds-brief', {
      name: modalBox.querySelector('#nd-name').value,
      source: modalBox.querySelector('#nd-src').value,
      notes: modalBox.querySelector('#nd-notes').value,
    }).then(res => {
      if (!res.ok) { alert(res.error || 'failed'); return; }
      closeModal();
      alert('Brief written to ' + res.file +
        '\n\nTell the agent: "build the design system from ' + res.file + '"');
    });
  };
  modal.hidden = false;
  modalBox.querySelector('#nd-name').focus();
};

$('#side-toggle').onclick = () => {
  const off = document.body.classList.toggle('no-side');
  localStorage.setItem('awmSide', off ? '0' : '1');
};
if (localStorage.getItem('awmSide') === '0')
  document.body.classList.add('no-side');

/* ── quick switcher (Ctrl+P / Ctrl+K) — Open Design's Cmd+P, widened to
   cover pages, projects and design systems in one list ── */
const qsEl = $('#qs'), qsIn = $('#qs-in'), qsList = $('#qs-list');
let qsEntries = null, qsSel = 0;

function qsBuild() {
  if (qsEntries) return Promise.resolve(qsEntries);
  const base = [];
  document.querySelectorAll('.proj').forEach(c =>
    base.push({ type: 'project', id: c.dataset.id, label: c.dataset.title,
                meta: 'project' }));
  Object.keys(DS).forEach(id =>
    base.push({ type: 'ds', id, label: DS[id].name,
                meta: DS[id].scope === 'mine' ? 'your design system'
                                              : 'design system' }));
  const fetches = [...document.querySelectorAll('.proj')].map(c =>
    fetch('/api/pages/' + c.dataset.id).then(r => r.json()).then(res =>
      (res.pages || []).forEach(pg => base.push({
        type: 'page', id: c.dataset.id + '/' + pg.slug,
        project: c.dataset.id, port: res.port, file: pg.file,
        label: pg.slug, meta: c.dataset.title, title: pg.title,
      }))).catch(() => {}));
  return Promise.all(fetches).then(() => (qsEntries = base));
}

const qsKey = e => e.type + ':' + e.id;
const qsRecents = () =>
  JSON.parse(localStorage.getItem('awmQsRecents') || '[]');

function qsPaint() {
  const f = qsIn.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  let rows;
  if (!f.length) {
    rows = qsRecents().map(k => qsEntries.find(e => qsKey(e) === k))
      .filter(Boolean);
    if (!rows.length) rows = qsEntries.slice(0, 12);
  } else {
    const scored = [];
    qsEntries.forEach(e => {
      const hay = (e.label + ' ' + e.meta + ' ' + (e.title || ''))
        .toLowerCase();
      if (!f.every(t => hay.includes(t))) return;
      scored.push([e.label.toLowerCase().startsWith(f[0]) ? 0 : 1, e]);
    });
    scored.sort((a, b) => a[0] - b[0]);
    rows = scored.slice(0, 18).map(x => x[1]);
  }
  qsSel = Math.min(qsSel, Math.max(0, rows.length - 1));
  qsList.innerHTML = '';
  rows.forEach((e, i) => {
    const b = document.createElement('button');
    b.className = 'qs-row' + (i === qsSel ? ' sel' : '');
    b.innerHTML = '<span></span><small></small>';
    b.firstChild.textContent =
      (e.type === 'ds' ? '◈ ' : e.type === 'project' ? '▤ ' : '· ') + e.label;
    b.lastChild.textContent = e.meta;
    b.onmouseenter = () => {
      qsSel = i;
      [...qsList.children].forEach((c, j) => c.classList.toggle('sel', j === i));
    };
    b.onclick = () => qsGo(e);
    qsList.appendChild(b);
  });
  qsList._rows = rows;
}

function qsGo(e) {
  localStorage.setItem('awmQsRecents', JSON.stringify(
    [qsKey(e), ...qsRecents().filter(k => k !== qsKey(e))].slice(0, 6)));
  qsClose();
  if (e.type === 'project') openProject(e.id);
  else if (e.type === 'ds') openDs(e.id);
  else openProject(e.project).then(t => {
    if (!t) return;
    t.port = t.port || e.port;
    t.frame.src = 'http://127.0.0.1:' + t.port + '/' + e.file;
    t.current = e.label;
    if (active === t.key) renderSide();
  });
}

function qsOpen() {
  qsEl.hidden = false;
  qsIn.value = '';
  qsSel = 0;
  qsBuild().then(qsPaint);
  qsIn.focus();
}
const qsClose = () => { qsEl.hidden = true; };
$('#qs-btn').onclick = qsOpen;
qsIn.oninput = () => { qsSel = 0; qsPaint(); };
qsIn.onkeydown = e => {
  const rows = qsList._rows || [];
  if (e.key === 'ArrowDown') {
    qsSel = Math.min(qsSel + 1, rows.length - 1); qsPaint(); e.preventDefault();
  } else if (e.key === 'ArrowUp') {
    qsSel = Math.max(qsSel - 1, 0); qsPaint(); e.preventDefault();
  } else if (e.key === 'Enter') {
    if (rows[qsSel]) qsGo(rows[qsSel]);
    e.preventDefault();
  } else if (e.key === 'Escape') qsClose();
};
qsEl.addEventListener('mousedown', e => { if (e.target === qsEl) qsClose(); });
// Capture phase beats the browser's print dialog — Open Design's own trick
// for claiming Cmd/Ctrl+P.
window.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey &&
      (e.key === 'p' || e.key === 'k')) {
    e.preventDefault();
    e.stopPropagation();
    if (qsEl.hidden) qsOpen(); else qsClose();
  }
}, true);

/* ── history: hash routing so browser back/forward navigates tabs ── */
let fromHash = false;
function applyHash() {
  fromHash = true;
  try {
    // no hash is the state history held before the first tab opened — Home
    if (!location.hash || location.hash === '#/') {
      if (active !== 'home') activate('home');
      return;
    }
    const m = location.hash.match(/^#\/(home|project:([\w-]+)|ds:([\w-]+))/);
    if (!m) return;
    if (m[1] === 'home') { if (active !== 'home') activate('home'); return; }
    if (m[2]) { openProject(m[2]); return; }
    if (m[3]) openDs(m[3]);
  } finally { fromHash = false; }
}
window.addEventListener('hashchange', applyHash);

/* ── status poll: patch in place — a shell must never reload itself ── */
setInterval(async () => {
  try {
    const st = await (await fetch('/api/status')).json();
    st.projects.forEach(p => {
      const card = document.querySelector('.proj[data-id="' + p.id + '"]');
      if (!card) return;
      card.querySelector('.dot').classList.toggle('on', p.running);
      const btn = card.querySelector('[data-open]');
      if (btn) btn.textContent = p.running ? 'Open' : 'Start & open';
    });
  } catch (e) { /* hub restarting */ }
}, 5000);

/* ── restore ── */
try {
  (JSON.parse(localStorage.getItem('awmTabs') || '[]')).forEach(t =>
    openTab(t.kind, t.id, t.title, t.url, false));
  const last = localStorage.getItem('awmActive');
  if (location.hash && location.hash !== '#/home') applyHash();
  else if (last && last !== 'home' && tabs.has(last)) activate(last);
  else renderSide();
} catch (e) { renderSide(); }
</script>
</body></html>
"""


# ── server ───────────────────────────────────────────────────────────────────

MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8", ".json": "application/json",
        ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
        ".webp": "image/webp", ".woff2": "font/woff2", ".woff": "font/woff",
        ".md": "text/plain; charset=utf-8"}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _bytes(self, body: bytes, kind: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: dict, status: int = 200) -> None:
        self._bytes(json.dumps(payload).encode("utf-8"),
                    "application/json", status)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._bytes(render_home(discover_projects()).encode("utf-8"),
                        MIME[".html"])
            return
        if path == "/api/status":
            self._json({"projects": [
                {"id": p["id"], "port": p["port"],
                 "running": port_alive(p["port"])}
                for p in discover_projects()]})
            return
        if path.startswith("/api/pages/"):
            pid = path[len("/api/pages/"):]
            project = next((p for p in discover_projects()
                            if p["id"] == pid), None)
            if project is None:
                self._json({"error": "no such project"}, 404)
                return
            manifest = Path(project["dir"]) / "dist" / "site-manifest.json"
            try:
                m = json.loads(manifest.read_text(encoding="utf-8"))
                pages = [{"slug": pg.get("slug"), "file": pg.get("file"),
                          "title": pg.get("title", ""),
                          "template": pg.get("template", ""),
                          "module": pg.get("module", "")}
                         for pg in m.get("pages", [])]
            except (OSError, json.JSONDecodeError):
                pages = []
            self._json({"ok": True, "port": project["port"], "pages": pages})
            return
        if path.startswith("/ds/"):
            rel = path[len("/ds/"):]
            target = (CORPUS / rel).resolve()
            if (target.is_file()
                    and CORPUS.resolve() in target.parents):
                self._bytes(target.read_bytes(),
                            MIME.get(target.suffix, "application/octet-stream"))
            else:
                self.send_error(404)
            return
        if path.startswith("/dsu/"):
            # site-owned design systems, served from outputs/<site>/design-system
            site, _, rel = path[len("/dsu/"):].partition("/")
            root = (OUTPUTS / site / "design-system").resolve()
            target = (root / rel).resolve()
            if (re.fullmatch(r"[\w-]+", site) and target.is_file()
                    and root in target.parents and OUTPUTS.resolve() in root.parents):
                self._bytes(target.read_bytes(),
                            MIME.get(target.suffix, "application/octet-stream"))
            else:
                self.send_error(404)
            return
        self.send_error(404)

    def _authorised(self) -> bool:
        host = (self.headers.get("Host") or "").lower()
        if host not in HUB_HOSTS:
            return False
        origin = self.headers.get("Origin")
        return not origin or origin.lower() in {f"http://{h}"
                                                for h in HUB_HOSTS}

    def do_POST(self):
        if not self._authorised():
            self._json({"error": "not authorised"}, 403)
            return
        try:
            req = json.loads(
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                or b"{}")
        except json.JSONDecodeError:
            self._json({"error": "bad json"}, 400)
            return
        route = self.path.split("?", 1)[0]
        if route == "/api/new-project":
            self._json(create_project(req))
            return
        if route == "/api/ds-brief":
            self._json(ds_brief(req))
            return
        project = next((p for p in discover_projects()
                        if p["id"] == req.get("id")), None)
        if project is None:
            self._json({"error": "no such project"}, 404)
        elif route == "/api/open":
            self._json(start_editor(project))
        elif route == "/api/stop":
            self._json(stop_editor(project))
        elif route == "/api/apply-ds":
            self._json(apply_design(project, str(req.get("ds") or "")))
        else:
            self._json({"error": "no such route"}, 404)


def main() -> int:
    url = f"http://127.0.0.1:{PORT}/"
    probe_alive = port_alive(PORT)
    if probe_alive:
        print(f"a hub is already serving {url} — reusing it")
        return 0
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    n = len(discover_projects())
    print(f"workspace hub at {url}  ({n} project(s), "
          f"{len(design_index())} design systems)  (Ctrl+C to stop)")
    if (os.environ.get("TERM_PROGRAM") == "vscode"
            or "vscode" in os.environ.get("CLAUDE_CODE_ENTRYPOINT", "")) \
            and "--open" not in sys.argv:
        print('to view inside VS Code: Terminal > Run Task > '
              '"workspace hub (preview in VS Code)"')
        print('or Ctrl+Shift+P > "Simple Browser: Show" > ' + url)
    elif "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
