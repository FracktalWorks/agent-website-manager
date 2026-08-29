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

import artifacts

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
            # Prefer a brand the build STATED. Everything below is a fallback
            # for manifests written before `brand` existed.
            title = (m.get("brand") or "").strip() or title
            first = (m.get("pages") or [{}])[0].get("title", "")
            # "Dermatologist in Hyderabad … | Dr. Varada's" → the brand half.
            # Em and en dashes count too: Fracktal's material pages separate
            # with "—", and knowing only "|" made a whole project display as
            # the title-cased folder name ("Fracktal Site").
            #
            # This heuristic is only ever right by luck: it recovers the brand
            # from a tag written for Google. Shortening Atlas Wild
            # Experiences' title suffix to fit 60 characters renamed the whole
            # project here. Sites should set `brand` in their manifest.
            if not m.get("brand"):
                for sep in ("|", "—", "–"):
                    if sep in first:
                        title = first.rsplit(sep, 1)[1].strip() or title
                        break
            site_url = m.get("site", "")
            # Which file to open. A site whose pages are all deployed onto an
            # existing WordPress install has no index.html, and opening `/`
            # then serves the directory listing instead of the site.
            entry = m.get("entry") or "index.html"
            if not (site / "dist" / entry).exists():
                entry = ""
        except (OSError, json.JSONDecodeError):
            site_url = ""
            entry = ""
        # Which artefact kinds this brand owns, beyond the website. Cheap —
        # a directory existence check per kind, not a walk.
        kinds = [k for k, _, rel in artifacts.KINDS
                 if (site.parent / rel).is_dir()]
        out.append({"id": pid, "dir": str(site), "title": title,
                    "kinds": kinds, "entry": entry,
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
    # `entry` is "" for a site whose dist/ has an index.html, so the URL is
    # unchanged for those; it names a real file for one that has none.
    base = f"http://127.0.0.1:{project['port']}/{project.get('entry', '')}"
    if port_alive(project["port"]):
        return {"ok": True, "url": base, "already": True}
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
            return {"ok": True, "url": base}
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
        # `entry` is "" for a site whose dist/ has an index.html, so this is
        # unchanged for those. For one that has none — Fracktal's pages are
        # bodies deployed onto an existing WordPress site — `/` is a directory
        # listing, and that is what the card thumbnail showed.
        url = f"http://127.0.0.1:{p['port']}/{p.get('entry', '')}"
        thumb = (
            f'<div class="thumb"><iframe src="{url}" loading="lazy" '
            'tabindex="-1"></iframe></div>' if running else
            '<div class="thumb empty"><span>editor not running</span></div>')
        cards.append(
            f'<article class="proj" data-id="{escape(p["id"])}" '
            f'data-port="{p["port"]}" data-title="{escape(p["title"])}" '
            f'data-entry="{escape(p.get("entry", ""))}">'
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
            # A project is a brand, not only a site — this is the way in to
            # everything it owns that has no URL. Counted live, so a project
            # with nothing but a website still says so honestly.
            + (f'<a class="btn" href="/collateral/{escape(p["id"])}"'
               f' target="_blank">Collateral</a>'
               if p.get("kinds") else "")
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
        .replace("{{DSDATA}}", json.dumps(ds_data).replace("</", "<\\/")) \
        .replace("{{ICONS}}", json.dumps({"paths": LUCIDE, "kind": KIND_ICON})
                 .replace("</", "<\\/"))


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
/* ── the page tree ── */
.segs { display:flex; gap:2px; margin:4px 0 6px; padding:2px;
  background:#0e1116; border:1px solid var(--line); border-radius:8px }
.segs button { flex:1; border:0; border-radius:6px; background:none;
  color:var(--mut); font:600 11.5px system-ui; padding:5px 0; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:5px }
.segs button.on { background:#242a36; color:var(--fg) }
.sitem.page { padding-top:3px; padding-bottom:3px }
/* The twisty is the accordion's whole affordance — give it a real hit area
   and an icon big enough to aim at, not a 9px character. */
.sitem .tw, .sitem .ico { flex:0 0 18px; height:18px; display:grid;
  place-items:center; color:var(--mut); border-radius:5px }
.sitem .tw { cursor:pointer }
.sitem .tw:hover { color:var(--fg); background:#2b3240 }
.sitem .tw.leaf { color:#5a6474; cursor:inherit }
.sitem.on .tw, .sitem.on .ico { color:#dfe8ff }
.sitem .ic { display:block }
.sitem.kind { padding-top:6px; padding-bottom:6px }
.sitem span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap }
.sitem.stub { color:#f2b544 }
.sitem.stub small { color:#f2b544; opacity:.7 }
.sitem.sec { margin-top:6px; font-size:11px; text-transform:uppercase;
  letter-spacing:.06em; color:var(--mut) }
.treeacts { display:flex; gap:10px; margin:0 6px 5px }
.treeacts button { border:0; background:none; padding:2px 0; cursor:pointer;
  color:var(--mut); font:500 10.5px system-ui; display:flex;
  align-items:center; gap:4px }
.treeacts button:hover { color:var(--fg) }
/* hover preview — one iframe at 1280x800, scaled, reused for every row */
#pv { position:fixed; z-index:40; width:340px; height:239px; border-radius:10px;
  border:1px solid var(--line); background:#fff; overflow:hidden;
  box-shadow:0 18px 44px rgba(0,0,0,.55); pointer-events:none }
#pv[hidden] { display:none }
#pv iframe { width:1280px; height:800px; border:0; display:block;
  transform:scale(.265625); transform-origin:0 0 }
#pv b { position:absolute; left:0; right:0; bottom:0; padding:5px 9px;
  background:var(--panel); color:var(--mut); font:400 11px/1.4
  ui-monospace,monospace; border-top:1px solid var(--line);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis }

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
<div id="pv" hidden><iframe title="page preview"></iframe><b></b></div>
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
<script id="icondata" type="application/json">{{ICONS}}</script>
<script>
"use strict";
const DS = JSON.parse(document.getElementById('dsdata').textContent);
const IC = JSON.parse(document.getElementById('icondata').textContent);

/* Lucide, drawn from the table the server shipped — same paths the Python
   side uses, so the two never drift. */
function icon(name, size) {
  return '<svg class="ic" width="' + (size || 16) + '" height="' +
    (size || 16) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor"' +
    ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"' +
    ' aria-hidden="true">' + (IC.paths[name] || '') + '</svg>';
}
const $ = s => document.querySelector(s);
const content = $('#content'), side = $('#side'), tabsBox = $('#tabs');

/* ── tab model — Open Design's prefix-encoded tab ids ("project:x", "ds:y"),
   one kept-alive iframe per tab so switching never reloads an editor ── */
let tabs = new Map();            // key -> {key,kind,id,title,url,btn,frame,pages,current}
let active = 'home';

function projectMeta(id) {
  const card = document.querySelector('.proj[data-id="' + id + '"]');
  // `entry` has to be read here. `openProject` composes its URL from
  // `m.entry`, and this returning only {title, port} made that `undefined`
  // every time — so the fallback fired always and the tab opened the server
  // root. It looked like the entry logic was wrong; the entry never arrived.
  return card ? { title: card.dataset.title, port: +card.dataset.port,
                  entry: card.dataset.entry || '' } : null;
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
    // Let embedded media (YouTube heroes, product demo videos) autoplay in
    // the preview — a nested iframe otherwise cannot without this delegation.
    t.frame.allow = 'autoplay; fullscreen; encrypted-media; picture-in-picture';
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

/* ── hover preview ──────────────────────────────────────────────────────────
   A page name tells you a page exists; it does not tell you what is on it.
   One iframe, reused, loaded only once the pointer has settled — sixty-one
   live previews at once would be sixty-one editors' worth of work for one
   glance. */
const pvEl = $('#pv'), pvFrame = pvEl.querySelector('iframe');
let pvTimer = null;

function previewOn(row, url, label) {
  row.onmouseenter = () => {
    clearTimeout(pvTimer);
    pvTimer = setTimeout(() => {
      if (pvFrame.dataset.at !== url) {
        pvFrame.src = url;
        pvFrame.dataset.at = url;
      }
      pvEl.querySelector('b').textContent = label;
      const r = row.getBoundingClientRect();
      pvEl.style.left = (side.getBoundingClientRect().right + 10) + 'px';
      pvEl.style.top = Math.max(46, Math.min(r.top - 8,
                                             innerHeight - 249)) + 'px';
      pvEl.hidden = false;
    }, 280);
  };
  row.onmouseleave = () => { clearTimeout(pvTimer); pvEl.hidden = true; };
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

/* A project is a brand, not only a site. The sidebar is therefore a KIND
   switcher first — website, print, brand, signage — and only then a page
   list, because a business card filed under sixty-one page rows is a business
   card nobody scrolls to.

   Pages themselves read two ways: the URL hierarchy (Sitemap) and the module
   that authored them (Sections). Sixty-one rows in one flat alphabetical
   column is a list, not a structure — and neither reading is the only true
   one. `/vitiligo/cost/` belongs under `/vitiligo/`; `/acne-treatment-
   hyderabad/` has no parent at all and is still edited beside the seven
   siblings it was written with in `hyderabad_medical.py`. */
function renderProjectSide(t) {
  side.insertAdjacentHTML('beforeend', '<h5>' + t.title + '</h5>');
  const nw = item('Open in new window');
  nw.insertAdjacentHTML('afterbegin',
    '<b class="ico">' + icon('external-link', 14) + '</b>');
  nw.onclick = () => window.open(t.url, '_blank');
  side.appendChild(nw);
  if (!t.closed) t.closed = new Set();
  if (!t.mode) t.mode = 'tree';
  if (!t.view) t.view = 'website';

  side.insertAdjacentHTML('beforeend', '<h5>Artefacts</h5>');
  const kindsBox = document.createElement('div');
  const body = document.createElement('div');
  side.append(kindsBox, body);

  /* ── the website kind: pages ── */
  const openPage = pg => {
    t.frame.src = 'http://127.0.0.1:' + t.port + '/' + pg.file;
    t.current = pg.url || pg.slug;
    t.view = 'website';
    paint();
  };
  const toggle = key => {
    t.closed.has(key) ? t.closed.delete(key) : t.closed.add(key);
    paint();
  };
  /* One page row. `depth` indents it under its parent; a node with children
     carries the twisty, and a URL level with no page of its own stays visible
     as a stub — "there is no /about/ page" is a fact about the site. */
  const pageRow = (n, depth) => {
    const kids = (n.kids || []).length;
    const seg = n.url === '/' ? 'index'
      : n.url.replace(/\/$/, '').split('/').pop();
    const note = [n.stub ? 'no page' : n.template, kids || '']
      .filter(Boolean).join(' ');
    const row = item(seg, note || ' ', 'mono page');
    row.style.paddingLeft = (8 + depth * 11) + 'px';
    row.title = (n.title || '') + '  ' + n.url;
    if (n.stub) {
      row.classList.add('stub');
      row.onclick = () => toggle(n.url);
    } else {
      if (t.view === 'website' && n.url === t.current) row.classList.add('on');
      row.onclick = () => openPage(n);
      previewOn(row, 'http://127.0.0.1:' + t.port + '/' + n.file, n.url);
    }
    if (kids) {
      const tw = document.createElement('b');
      tw.className = 'tw';
      tw.innerHTML = icon(t.closed.has(n.url) ? 'chevron-right'
                                              : 'chevron-down', 15);
      tw.title = t.closed.has(n.url) ? 'Expand' : 'Collapse';
      tw.onclick = e => { e.stopPropagation(); toggle(n.url); };
      row.insertBefore(tw, row.firstChild);
    } else {
      // A leaf still needs the twisty's width, and a page icon says more in
      // that space than an empty gutter does.
      row.insertAdjacentHTML('afterbegin',
        '<b class="tw leaf">' + icon('file-text', 13) + '</b>');
    }
    return row;
  };
  const walk = (nodes, depth, into) => nodes.forEach(n => {
    into.appendChild(pageRow(n, depth));
    if (!t.closed.has(n.url)) walk(n.kids || [], depth + 1, into);
  });
  /* Every key that can be rolled up: a URL with children, plus — in Sections
     mode — the section headers themselves. Collapse all in Sitemap mode must
     not silently also shut sections the user cannot see. */
  const collapsible = () => {
    const keys = [];
    const scan = ns => ns.forEach(n => {
      if ((n.kids || []).length) { keys.push(n.url); scan(n.kids); }
    });
    if (t.mode === 'sections') {
      (t.sections || []).forEach(s => { keys.push('§' + s.id); scan(s.tree); });
    } else scan(t.tree || []);
    return keys;
  };

  const paintPages = () => {
    const modes = document.createElement('div');
    modes.className = 'segs';
    [['tree', 'Sitemap', 'network'],
     ['sections', 'Sections', 'layers']].forEach(([m, label, ico]) => {
      const b = document.createElement('button');
      b.innerHTML = icon(ico, 14) + '<span></span>';
      b.querySelector('span').textContent = label;
      b.className = t.mode === m ? 'on' : '';
      b.onclick = () => { t.mode = m; paint(); };
      modes.appendChild(b);
    });
    const filter = document.createElement('input');
    filter.placeholder = 'Filter ' + ((t.pages || []).length || '') + ' pages…';
    filter.value = t.q || '';
    // Repainting replaces this input, so put the caret back where it was —
    // otherwise the second keystroke of a filter lands nowhere.
    filter.oninput = () => {
      const at = filter.selectionStart;
      t.q = filter.value;
      paint();
      const now = body.querySelector('input');
      if (now) { now.focus(); now.setSelectionRange(at, at); }
    };
    const box = document.createElement('div');
    const acts = document.createElement('div');
    acts.className = 'treeacts';
    [['Expand all', false, 'chevrons-up-down'],
     ['Collapse all', true, 'chevrons-down-up']].forEach(([label, shut, i]) => {
      const b = document.createElement('button');
      b.innerHTML = icon(i, 13) + '<span></span>';
      b.querySelector('span').textContent = label;
      b.onclick = () => {
        t.closed = new Set();
        if (shut) collapsible().forEach(k => t.closed.add(k));
        paint();
      };
      acts.appendChild(b);
    });
    body.append(modes, filter, acts, box);

    const f = (t.q || '').trim().toLowerCase();
    if (f) {
      // A filtered list is a search result, not a hierarchy — show the whole
      // URL so two pages both called `cost` stay tellable apart.
      const hits = (t.pages || []).filter(pg =>
        (pg.slug + ' ' + pg.title + ' ' + (pg.url || '')).toLowerCase()
          .includes(f));
      hits.forEach(pg => {
        const row = item(pg.url || pg.slug, pg.template, 'mono page');
        row.title = pg.title;
        if (t.view === 'website' && pg.url === t.current)
          row.classList.add('on');
        row.onclick = () => openPage(pg);
        previewOn(row, 'http://127.0.0.1:' + t.port + '/' + pg.file, pg.url);
        box.appendChild(row);
      });
      if (!hits.length)
        box.insertAdjacentHTML('beforeend',
          '<p class="hint">No page matches “' + f + '”.</p>');
    } else if (t.mode === 'sections') {
      (t.sections || []).forEach(s => {
        const key = '§' + s.id;
        const head = item(s.label, s.count + '', 'sec');
        head.insertAdjacentHTML('afterbegin', '<b class="tw">' +
          icon(t.closed.has(key) ? 'chevron-right' : 'chevron-down', 15) +
          '</b>');
        head.onclick = () => toggle(key);
        box.appendChild(head);
        if (!t.closed.has(key)) walk(s.tree, 1, box);
      });
    } else {
      // The home page parents every other page, so drawing it as a branch
      // would indent the whole site one level to say nothing. It gets a row
      // of its own and its children start at the left margin.
      const roots = t.tree || [];
      const home = roots.length === 1 && roots[0].url === '/' ? roots[0] : null;
      if (home) {
        box.appendChild(pageRow({ ...home, kids: [] }, 0));
        walk(home.kids || [], 0, box);
      } else walk(roots, 0, box);
    }
  };

  /* ── every other kind: its groups, as jump links into the collateral view ── */
  const paintKind = k => {
    const url = '/collateral/' + t.id + '/' + k.id;
    body.insertAdjacentHTML('beforeend',
      '<p class="hint">' + (k.note || '') + '</p>');
    (t.groups[k.id] || []).forEach(g => {
      const row = item(g.label, g.count + '');
      row.onclick = () => { t.frame.src = url + '?embed=1#g-' + g.id; };
      body.appendChild(row);
    });
    const open = item('Open on its own');
    open.insertAdjacentHTML('afterbegin',
      '<b class="ico">' + icon('external-link', 14) + '</b>');
    open.onclick = () => window.open(url, '_blank');
    body.appendChild(open);
  };

  const paint = () => {
    kindsBox.innerHTML = '';
    body.innerHTML = '';
    (t.kinds || []).forEach(k => {
      const row = item(k.label, k.count + '', 'kind');
      row.insertAdjacentHTML('afterbegin',
        '<b class="ico">' + icon(IC.kind[k.id] || 'file-text', 15) + '</b>');
      row.title = k.note || '';
      if (t.view === k.id) row.classList.add('on');
      row.onclick = () => {
        t.view = k.id;
        t.frame.src = k.id === 'website'
          ? 'http://127.0.0.1:' + t.port + '/'
          : '/collateral/' + t.id + '/' + k.id + '?embed=1';
        if (k.id === 'website') t.current = '/';
        paint();
      };
      kindsBox.appendChild(row);
    });
    if (!t.kinds) return;
    const kind = t.kinds.find(k => k.id === t.view);
    if (!kind || kind.id === 'website') paintPages();
    else paintKind(kind);
  };

  if (t.pages) { paint(); return; }
  fetch('/api/pages/' + t.id).then(r => r.json()).then(res => {
    t.pages = res.pages || [];
    t.tree = res.tree || [];
    t.sections = res.sections || [];
    t.kinds = res.kinds || [];
    t.groups = res.groups || {};
    t.port = res.port;
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
      openTab('project', id, title,
              'http://127.0.0.1:' + m.port + '/' + (m.entry || '')));
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
  /* Drop tabs whose project no longer exists. Renaming a project directory
     leaves its tab in localStorage pointing at a dead id, and it restores
     looking perfectly normal until it is clicked and 404s. The server just
     rendered one `.proj` card per live project, so the DOM is the authority
     on what exists. */
  const live = new Set(
    [...document.querySelectorAll('.proj')].map(c => c.dataset.id));
  (JSON.parse(localStorage.getItem('awmTabs') || '[]'))
    .filter(t => t.kind !== 'project' || live.has(t.id))
    .forEach(t => openTab(t.kind, t.id, t.title, t.url, false));
  const last = localStorage.getItem('awmActive');
  if (location.hash && location.hash !== '#/home') applyHash();
  else if (last && last !== 'home' && tabs.has(last)) activate(last);
  else renderSide();
} catch (e) { renderSide(); }
</script>
</body></html>
"""


# ── server ───────────────────────────────────────────────────────────────────

# ── icons ────────────────────────────────────────────────────────────────────
# Lucide v1.28.0 (ISC), vendored as raw path data rather than pulled from a
# CDN: the hub is a loopback tool that has to draw its own chrome with no
# network, and a 12-icon <script src> is a dependency for nothing. Both the
# Python-rendered pages and the shell's JS draw from this one table, so a
# chevron in the sidebar is the same chevron in the sitemap.
LUCIDE = {
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "chevrons-up-down": '<path d="m7 15 5 5 5-5"/><path d="m7 9 5-5 5 5"/>',
    "chevrons-down-up": '<path d="m7 20 5-5 5 5"/><path d="m7 4 5 5 5-5"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0'
             ' 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "printer": '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2'
               ' 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0'
               ' 0 1 1 1v6"/><rect x="6" y="14" width="12" height="8" rx="1"/>',
    "palette": '<path d="M12 22a1 1 0 0 1 0-20 10 9 0 0 1 10 9 5 5 0 0 1-5'
               ' 5h-2.25a1.75 1.75 0 0 0-1.4 2.8l.3.4a1.75 1.75 0 0 1-1.4'
               ' 2.8z"/><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/>'
               '<circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/>'
               '<circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>'
               '<circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/>',
    "signpost": '<path d="M12 13v8"/><path d="M12 3v3"/><path d="M2.354'
                ' 10.354a1.207 1.207 0 0 1 0-1.708l2.06-2.06A2 2 0 0 1 5.828'
                ' 6h12.344a2 2 0 0 1 1.414.586l2.06 2.06a1.207 1.207 0 0 1 0'
                ' 1.708l-2.06 2.06a2 2 0 0 1-1.414.586H5.828a2 2 0 0'
                ' 1-1.414-.586z"/>',
    "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18'
                     ' 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1'
                     ' 2-2h6"/>',
    "file-text": '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1'
                 ' 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2'
                 ' 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M10 9H8"/>'
                 '<path d="M16 13H8"/><path d="M16 17H8"/>',
    "network": '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2"'
               ' y="16" width="6" height="6" rx="1"/><rect x="9" y="2"'
               ' width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1'
               ' 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
             '<circle cx="9" cy="9" r="2"/>'
             '<path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "megaphone": '<path d="m3 11 18-5v12L3 14v-3z"/>'
                 '<path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    "layers": '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0'
              ' 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"/>'
              '<path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58'
              '-3.9A1 1 0 0 0 22 12"/><path d="M2 17a1 1 0 0 0 .58.91l8.6'
              ' 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17"/>',
}
# Which icon stands for which artefact kind, keyed by `artifacts.KINDS` id.
KIND_ICON = {"website": "globe", "concepts": "layers", "media": "image",
             "print": "printer", "social": "megaphone", "brand": "palette",
             "signage": "signpost"}


def icon(name: str, size: int = 16, cls: str = "") -> str:
    return (f'<svg class="ic{" " + cls if cls else ""}" width="{size}" '
            f'height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{LUCIDE[name]}</svg>')


MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8", ".json": "application/json",
        ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
        ".webp": "image/webp", ".woff2": "font/woff2", ".woff": "font/woff",
        ".md": "text/plain; charset=utf-8", ".jpeg": "image/jpeg",
        ".ico": "image/x-icon",
        # Without this a press PDF is served as octet-stream and downloads
        # instead of opening, which is the wrong default for a proof.
        ".pdf": "application/pdf"}


COLLATERAL_CSS = """
:root { --bg:#0f1218; --panel:#14171e; --line:#2a2f3a; --fg:#e8ebf2;
  --mut:#8b93a4; --blue:#2f6df6; --ok:#3ddc97; --wait:#f2b544; }
* { box-sizing:border-box }
body { margin:0; background:var(--bg); color:var(--fg);
  font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif }
header { padding:22px 28px 0; }
header a.back { color:var(--mut); text-decoration:none; font-size:13px }
header h1 { margin:10px 0 2px; font-size:24px; font-weight:700 }
header p { margin:0; color:var(--mut); font-size:13px }
nav { display:flex; gap:4px; padding:18px 28px 0; border-bottom:1px solid var(--line) }
nav a { padding:9px 14px; border:1px solid transparent; border-bottom:0;
  border-radius:8px 8px 0 0; color:var(--mut); text-decoration:none; font-size:13px }
nav a.on { background:var(--panel); border-color:var(--line); color:var(--fg) }
nav a b { color:var(--mut); font-weight:400; margin-left:6px; font-size:12px }
main { padding:22px 28px 60px }
main.embed { padding-top:14px }
iframe.concepts { width:100%; border:1px solid var(--line); border-radius:10px;
  height:calc(100vh - 210px); background:var(--panel) }
main.embed iframe.concepts { height:calc(100vh - 50px) }
main h3 { display:flex; align-items:baseline; gap:10px; margin:26px 0 11px;
  font-size:12px; text-transform:uppercase; letter-spacing:.07em;
  color:var(--fg); font-weight:700 }
main h3:first-child { margin-top:4px }
main h3 em { font-style:normal; font-size:11.5px; letter-spacing:0;
  text-transform:none; color:var(--mut); font-weight:400 }
main h3::after { content:''; flex:1; height:1px; background:var(--line) }
.pill.lang { background:#242a36; color:var(--mut) }
.grid { display:grid; gap:14px;
  grid-template-columns:repeat(auto-fill,minmax(230px,1fr)) }
.card { background:var(--panel); border:1px solid var(--line); border-radius:10px;
  overflow:hidden; text-decoration:none; color:inherit; display:block }
.card .shot { display:block; width:100%; height:auto; max-height:420px;
  object-fit:contain; background:#fff; border-bottom:1px solid var(--line) }
.card .shot.none { height:120px; display:grid; place-items:center;
  background:#0e1116; color:var(--mut); font-size:11.5px }
.card .m { padding:9px 11px; display:flex; justify-content:space-between;
  align-items:center; gap:8px }
.card .m span { font-size:12.5px; overflow:hidden; text-overflow:ellipsis;
  white-space:nowrap }
.pill { font-size:10.5px; padding:2px 7px; border-radius:99px; white-space:nowrap }
.pill.ok { background:rgba(61,220,151,.14); color:var(--ok) }
.pill.wait { background:rgba(242,181,68,.14); color:var(--wait) }
.tree { font:13px/1.7 ui-monospace,SFMono-Regular,Consolas,monospace }
.tree .row { display:flex; gap:10px; align-items:baseline; padding:2px 0;
  border-bottom:1px solid rgba(42,47,58,.5) }
.tree .row:hover { background:#161a22 }
.tree a { color:var(--fg); text-decoration:none }
.tree a:hover { color:var(--blue) }
.tree .t { color:var(--mut); font-family:system-ui,sans-serif; font-size:12.5px;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap }
.tree .stub { color:var(--wait) }
.tree .kidcount { color:var(--mut); font-size:11.5px }
/* the accordion: one level of nesting per URL level */
.tree .kids { margin-left:11px; padding-left:11px;
  border-left:1px solid var(--line) }
.tree .node.shut > .kids { display:none }
.tree .tw { flex:0 0 22px; height:22px; display:grid; place-items:center;
  color:var(--mut); cursor:pointer; border-radius:6px; align-self:center }
.tree .tw:hover { color:var(--fg); background:#232936 }
.tree .tw.leaf { color:#4d5666; cursor:default }
.tree .tw.leaf:hover { background:none; color:#4d5666 }
/* one <b> holds both chevrons; `shut` decides which of them is drawn */
.tree .tw .shutico, .tree .node.shut > .row > .tw .ic { display:none }
.tree .node.shut > .row > .tw .shutico { display:block }
.tree .ic { display:block }
.treebar { display:flex; gap:8px; align-items:center; margin-bottom:10px }
.treebar button { font:600 11.5px system-ui; padding:6px 10px; cursor:pointer;
  border:1px solid var(--line); border-radius:7px; background:#1d222c;
  color:var(--fg); display:flex; align-items:center; gap:6px }
.treebar button:hover { filter:brightness(1.2) }
.treebar span { color:var(--mut); font-size:11.5px }
/* hover preview: one iframe laid out at 1280x800 and scaled down */
#pv { position:fixed; right:22px; width:340px; z-index:9; border-radius:10px;
  border:1px solid var(--line); background:#fff; overflow:hidden;
  box-shadow:0 18px 44px rgba(0,0,0,.55) }
#pv[hidden] { display:none }
#pv iframe { width:1280px; height:800px; border:0; display:block;
  transform:scale(.265625); transform-origin:0 0; pointer-events:none }
#pv { height:calc(800px * .265625 + 26px) }
#pv b { position:absolute; left:0; right:0; bottom:0; padding:5px 9px;
  background:var(--panel); color:var(--mut); font:400 11px/1.4
  ui-monospace,monospace; border-top:1px solid var(--line) }
.gal { display:grid; gap:10px;
  grid-template-columns:repeat(auto-fill,minmax(130px,1fr)) }
.gal a { background:var(--panel); border:1px solid var(--line); border-radius:8px;
  padding:8px; text-align:center; text-decoration:none; color:var(--mut);
  font-size:11px; overflow:hidden }
.gal img { width:100%; height:96px; object-fit:contain; background:#fff;
  border-radius:4px; margin-bottom:6px }
body.dk .gal img { background:#10141b }
.bg { float:right; font-size:11.5px; color:var(--mut); margin-top:-2px;
  display:flex; align-items:center; gap:6px; cursor:pointer }
.empty { color:var(--mut) }
"""


def render_collateral(project: dict, kind_id: str = "",
                      embed: bool = False) -> str:
    """Every artefact a project owns, grouped by kind.

    The hub's home page answers "which projects are there"; this answers "what
    has this brand actually got" — which stopped being the same question when
    the first thing without a URL was made.
    """
    root = Path(project["dir"]).parent
    ks = artifacts.kinds(root)
    if not ks:
        body = '<p class="empty">Nothing built yet.</p>'
        kind_id = ""
    else:
        kind_id = kind_id if any(k["id"] == kind_id for k in ks) else ks[0]["id"]
        kind = next(k for k in ks if k["id"] == kind_id)
        body = _collateral_body(project, kind)
        if kind["kind"] == "gallery" and kind["id"] != "capture":
            # A white mark on a white tile is indistinguishable from a broken
            # file, and half a brand's assets are drawn for dark backgrounds.
            # (The capture gallery carries its own dark-tiles toggle + search.)
            body = ('<label class="bg"><input type="checkbox" '
                    'onchange="document.body.classList.toggle(\'dk\')"> '
                    'Dark tiles</label>' + body)
    q = "?embed=1" if embed else ""
    tabs = "".join(
        f'<a class="{"on" if k["id"] == kind_id else ""}" '
        f'href="/collateral/{project["id"]}/{k["id"]}{q}">{escape(k["label"])}'
        f'<b>{k["count"]}</b></a>' for k in ks)
    # Framed inside the workspace shell the tab already carries the project
    # name and the sidebar already carries the kinds — repeating both is two
    # navigations for one page.
    head = "" if embed else f"""<header>
  <a class="back" href="/">&larr; workspace</a>
  <h1>{escape(project["title"])}</h1>
  <p>{escape(str(root))}</p>
</header>
<nav>{tabs}</nav>"""
    return f"""<!doctype html><html><meta charset="utf-8">
<title>{escape(project["title"])} — collateral</title>
<style>{COLLATERAL_CSS}</style>
{head}
<main{' class="embed"' if embed else ''}>{body}</main>
</html>"""


def _collateral_body(project: dict, kind: dict) -> str:
    """One kind, in the groups that kind actually has.

    Sixteen press tiles in one grid is a pile; the same sixteen under Fliers /
    Standees / Leaflets / Business card is a production status, and the empty
    `press-ready` count on a family is the thing worth seeing first.
    """
    pid = project["id"]
    if kind["kind"] == "pages":
        return _sitemap_html(project, kind)
    if kind["kind"] == "concepts":
        return _concepts_html(pid, kind)
    if kind["id"] == "capture":
        return _capture_gallery_html(pid, kind)
    out = []
    for g in kind["groups"]:
        if kind["kind"] == "press":
            note = f'{g["ready"]}/{g["count"]} press-ready'
            body = f'<div class="grid">{_press_cards(pid, g["items"])}</div>'
        else:
            note = f'{g["count"]} file{"s" * (g["count"] != 1)}'
            body = f'<div class="gal">{_gallery_tiles(pid, g["items"])}</div>'
        out.append(f'<h3 id="g-{escape(g["id"])}">{escape(g["label"])}'
                   f'<em>{escape(note)}</em></h3>{body}')
    return "".join(out)


def _concepts_html(pid: str, kind: dict) -> str:
    """The concept round, framed whole.

    `concepts/compare.html` is the review surface (live iframes of every
    direction, phone→desktop width toggle, chosen badge). The hub frames it
    rather than re-implementing it, so the page a user opens from disk and
    the page the hub shows can never drift apart.
    """
    if kind.get("compare"):
        return (f'<iframe class="concepts" title="Design concepts" '
                f'src="/art/{pid}/{escape(kind["compare"])}"></iframe>')
    rows = "".join(
        f'<li><a href="/art/{pid}/{escape(i["rel"])}" target="_blank">'
        f'{escape(i["title"])}</a>'
        f'{" — chosen" if i.get("chosen") else ""}</li>'
        for i in kind["items"])
    return ('<p class="empty">No compare page yet — run <code>python '
            '.github/skills/design_concepting/scripts/concepts.py compare '
            f'{escape(pid)}</code></p><ul>{rows}</ul>')


def _press_cards(pid: str, items: list[dict]) -> str:
    cards = []
    for i in items:
        # An <img> rather than a background, so the proof keeps its own
        # proportions — a standee reads as a standee and a card as a card,
        # instead of every artefact becoming a stamp in a fixed-height box.
        dims = (f' width="{i["w"]}" height="{i["h"]}"'
                if i.get("w") and i.get("h") else "")
        shot = (f'<img class="shot" src="/art/{pid}/{i["proof"]}"{dims} '
                f'loading="lazy" alt="">' if i.get("proof")
                else '<div class="shot none">no proof</div>')
        badge = ('<i class="pill ok">press-ready</i>' if i["ready"]
                 else '<i class="pill wait">proof only</i>')
        lang = (f'<i class="pill lang">{escape(i["lang"].upper())}</i>'
                if i.get("lang") else "")
        href = f'/art/{pid}/{i["pdf"] or i["proof"]}'
        size = f' · {i["w"]}×{i["h"]}' if i.get("w") else ""
        cards.append(
            f'<a class="card" href="{href}" target="_blank" '
            f'title="{escape(i["name"])}{size}">{shot}'
            f'<div class="m"><span>{escape(i.get("subject") or i["name"])}'
            f'</span>{lang}{badge}</div></a>')
    return "".join(cards)


def _capture_gallery_html(pid: str, kind: dict) -> str:
    """The captured-media kind, as a searchable, chunked gallery.

    A flat 1,300-tile grid renders every tile up front and locks the browser.
    This embeds the item metadata and paints tiles in batches as you scroll
    (IntersectionObserver), and adds a search box + category filter — so you
    find "the extruder cutaway" by caption instead of scrolling past a thousand
    thumbnails. Thumbs load lazily from /art/; a click opens the full original.
    """
    slim = [{"n": i["name"], "r": i["rel"], "o": i.get("orig", i["rel"]),
             "c": i.get("cat", ""), "k": i.get("kb", 0),
             "p": i.get("cap", "")} for i in kind["items"]]
    cats = "".join(f'<option value="{escape(g["label"])}">{escape(g["label"])}'
                   f' ({g["count"]})</option>' for g in kind["groups"])
    data = json.dumps(slim, ensure_ascii=False)
    return f"""<div class="capg">
<div class="capg-bar">
  <input id="capq" placeholder="Search filename or caption…" autocomplete="off">
  <select id="capcat"><option value="">All categories</option>{cats}</select>
  <select id="capsort"><option value="cat">Sort: category</option>
    <option value="name">name</option><option value="big">largest</option></select>
  <label class="capchk"><input type="checkbox" id="capdk"> Dark tiles</label>
  <span id="capcnt"></span>
</div>
<div id="capgrid" class="capgrid"></div><div id="capmore"></div></div>
<style>
.capg-bar{{position:sticky;top:0;z-index:3;display:flex;gap:8px;flex-wrap:wrap;
  align-items:center;padding:10px 2px;background:var(--bg,#fff);
  border-bottom:1px solid #e4e4e7;margin-bottom:12px}}
.capg-bar input#capq{{flex:1;min-width:200px;padding:7px 10px;border:1px solid #d4d4d8;
  border-radius:8px;font:inherit}}
.capg-bar select,.capg-bar .capchk{{padding:6px 8px;border:1px solid #d4d4d8;
  border-radius:8px;font:inherit;background:#fff}}
.capg-bar .capchk{{display:inline-flex;gap:5px;align-items:center;color:#52525b}}
#capcnt{{color:#71717a;font-size:12px}}
.capgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}
.capgrid a{{display:flex;flex-direction:column;text-decoration:none;color:inherit;
  border:1px solid #e4e4e7;border-radius:10px;overflow:hidden;background:#fff}}
.capgrid .th{{aspect-ratio:1;display:flex;align-items:center;justify-content:center;
  padding:8px;background-color:#f2f4f8;
  background-image:linear-gradient(45deg,#dce0e8 25%,transparent 25%),linear-gradient(-45deg,#dce0e8 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#dce0e8 75%),linear-gradient(-45deg,transparent 75%,#dce0e8 75%);
  background-size:16px 16px;background-position:0 0,0 8px,8px -8px,-8px 0}}
body.capdark .capgrid .th{{background-color:#1b1d24;
  background-image:linear-gradient(45deg,#2a2d3a 25%,transparent 25%),linear-gradient(-45deg,#2a2d3a 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#2a2d3a 75%),linear-gradient(-45deg,transparent 75%,#2a2d3a 75%)}}
.capgrid .th img{{max-width:100%;max-height:100%;object-fit:contain}}
.capgrid .m{{padding:6px 8px;border-top:1px solid #eee}}
.capgrid .m .ct{{color:#e11d2a;font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}}
.capgrid .m .nm{{font-size:11px;font-weight:600;word-break:break-word;line-height:1.3}}
.capgrid .m .cp{{color:#71717a;font-size:10.5px;margin-top:2px}}
</style>
<script>
(function(){{
const D={data}, PID={json.dumps(pid)}, B=90;
const $=s=>document.querySelector(s), grid=$('#capgrid');
function esc(s){{return (s||'').replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));}}
function tile(x){{return '<a href="/art/'+PID+'/'+encodeURI(x.o)+'" target="_blank" title="'+esc(x.p||x.n)+' · '+x.k+' KB">'
  +'<span class="th"><img loading="lazy" src="/art/'+PID+'/'+encodeURI(x.r)+'" alt=""></span>'
  +'<span class="m"><span class="ct">'+esc(x.c)+'</span><span class="nm">'+esc(x.n)+'</span>'
  +(x.p?'<span class="cp">'+esc(x.p)+'</span>':'')+'</span></a>';}}
let cur=[], shown=0;
const sent=$('#capmore');
function more(){{const s=cur.slice(shown,shown+B);grid.insertAdjacentHTML('beforeend',s.map(tile).join(''));shown+=s.length;}}
new IntersectionObserver(e=>{{if(e[0].isIntersecting&&shown<cur.length)more();}},{{rootMargin:'700px'}}).observe(sent);
function render(){{
  const q=$('#capq').value.toLowerCase().trim(), c=$('#capcat').value, so=$('#capsort').value;
  cur=D.filter(x=>(!c||x.c===c)&&(!q||(x.n+' '+x.p).toLowerCase().includes(q)));
  if(so==='name')cur.sort((a,b)=>a.n.localeCompare(b.n));
  else if(so==='big')cur.sort((a,b)=>b.k-a.k);
  else cur.sort((a,b)=>(a.c+a.n).localeCompare(b.c+b.n));
  grid.innerHTML='';shown=0;more();
  $('#capcnt').textContent=cur.length+' / '+D.length;
}}
['capq','capcat','capsort'].forEach(id=>$('#'+id).addEventListener('input',render));
$('#capdk').addEventListener('change',e=>document.body.classList.toggle('capdark',e.target.checked));
render();
}})();
</script>"""


def _gallery_tiles(pid: str, items: list[dict]) -> str:
    # The tile shows the thumbnail (i["rel"]) but links to the full original
    # (i["orig"], for the captured-media kind) so a click opens the real file,
    # not the shrunk preview. Older kinds carry no "orig"/"cap" and fall back
    # to the thumbnail path and filename — unchanged.
    return "".join(
        f'<a href="/art/{pid}/{i.get("orig", i["rel"])}" target="_blank" '
        f'title="{escape(i.get("cap") or i["rel"])} · {i["kb"]} KB">'
        f'<img src="/art/{pid}/{i["rel"]}" loading="lazy" alt="">'
        f'{escape(i["name"])}</a>' for i in items)


def _sitemap_html(project: dict, kind: dict) -> str:
    """The site as its own URL hierarchy — nested, collapsible, previewable.

    The links point at `<slug>.html`, NOT at the page's public URL. The editor
    serves the built files flat, so `/vitiligo/cost/` is a 404 there while
    `/vitiligo-cost.html` is the page — the pretty URL only exists once the
    site is deployed. A sitemap whose every link 404s is worse than no sitemap.
    """
    port = project["port"]

    def node(n: dict) -> str:
        kids = "".join(node(k) for k in n["kids"])
        label = escape(n["url"])
        twisty = (f'<b class="tw" title="Collapse">{icon("chevron-down", 17)}'
                  f'{icon("chevron-right", 17, "shutico")}</b>'
                  if n["kids"] else
                  f'<b class="tw leaf">{icon("file-text", 14)}</b>')
        count = (f'<span class="kidcount">{len(n["kids"])}</span>'
                 if n["kids"] else "")
        if n["stub"]:
            link = (f'<span class="stub">{label}</span>'
                    f'<span class="kidcount">no page</span>')
        else:
            href = f'http://127.0.0.1:{port}/{n.get("file", "")}'
            link = (f'<a href="{href}" target="_blank" data-pv="{href}">'
                    f'{label}</a>')
        return (f'<div class="node">'
                f'<div class="row">{twisty}{link}{count}'
                f'<span class="t">{escape(n.get("title", ""))}</span></div>'
                f'<div class="kids">{kids}</div></div>')

    body = "".join(node(n) for n in kind["tree"])
    return f"""<div class="treebar">
  <button data-all="open">{icon("chevrons-up-down", 14)}Expand all</button>
  <button data-all="shut">{icon("chevrons-down-up", 14)}Collapse all</button>
  <span>Hover a page to preview it · click to open it in the editor
  (port {port})</span>
</div>
<div class="tree">{body}</div>
<div id="pv" hidden><iframe title="preview"></iframe><b></b></div>
<script>
document.querySelectorAll('.tw').forEach(t => t.onclick = () =>
  t.closest('.node').classList.toggle('shut'));
document.querySelectorAll('.treebar button').forEach(b => b.onclick = () =>
  document.querySelectorAll('.node').forEach(n =>
    n.classList.toggle('shut', b.dataset.all === 'shut' && !!n.querySelector('.kids > .node'))));
/* One reused iframe, loaded only after the pointer settles — 61 live
   previews at once would be 61 editors' worth of work for one glance. */
const pv = document.getElementById('pv'), fr = pv.querySelector('iframe');
let timer = null;
document.querySelectorAll('a[data-pv]').forEach(a => {{
  a.onmouseenter = () => {{
    clearTimeout(timer);
    timer = setTimeout(() => {{
      if (fr.dataset.at !== a.dataset.pv)
        {{ fr.src = a.dataset.pv; fr.dataset.at = a.dataset.pv; }}
      pv.querySelector('b').textContent = a.textContent;
      const r = a.getBoundingClientRect();
      pv.style.top = Math.min(r.top, innerHeight - 250) + 'px';
      pv.hidden = false;
    }}, 260);
  }};
  a.onmouseleave = () => clearTimeout(timer);
}});
document.querySelector('.tree').onmouseleave = () =>
  {{ clearTimeout(timer); pv.hidden = true; }};
</script>"""


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
            # Both readings of the same pages: the URL hierarchy and the
            # authoring sections. The sidebar switches between them without a
            # second round trip, and the flat list still feeds the switcher.
            pages = artifacts.pages_of(Path(project["dir"]))
            detail = artifacts.kinds(Path(project["dir"]).parent)
            self._json({"ok": True, "port": project["port"], "pages": pages,
                        "tree": artifacts.tree(pages),
                        "sections": artifacts.sections(pages),
                        "kinds": [{k: v for k, v in kind.items()
                                   if k in artifacts.LIGHT}
                                  for kind in detail],
                        # group headings only — the items themselves are the
                        # collateral page's job, not the sidebar's.
                        "groups": {kind["id"]: [
                            {"id": g["id"], "label": g["label"],
                             "count": g["count"]}
                            for g in kind.get("groups", [])]
                            for kind in detail}})
            return
        if path.startswith("/collateral/"):
            pid, _, kind = path[len("/collateral/"):].partition("/")
            project = next((p for p in discover_projects()
                            if p["id"] == pid), None)
            if project is None:
                self.send_error(404)
                return
            embed = "embed=1" in self.path.split("?", 1)[-1]
            self._bytes(render_collateral(project, kind, embed)
                        .encode("utf-8"), MIME[".html"])
            return
        if path.startswith("/api/artifacts/"):
            pid = path[len("/api/artifacts/"):]
            project = next((p for p in discover_projects()
                            if p["id"] == pid), None)
            if project is None:
                self._json({"error": "no such project"}, 404)
                return
            self._json({"ok": True,
                        **artifacts.summary(Path(project["dir"]).parent)})
            return
        if path.startswith("/art/"):
            # Files inside one project directory. Same containment check as
            # /dsu/ — resolve first, then prove the resolved path is still
            # under the project, so `..` cannot walk out of it.
            pid, _, rel = path[len("/art/"):].partition("/")
            project = next((p for p in discover_projects()
                            if p["id"] == pid), None)
            root = (Path(project["dir"]).parent.resolve() if project
                    else None)
            target = (root / rel).resolve() if root else None
            if (target and target.is_file() and root in target.parents
                    and OUTPUTS.resolve() in root.parents):
                self._bytes(target.read_bytes(),
                            MIME.get(target.suffix,
                                     "application/octet-stream"))
            else:
                self.send_error(404)
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
