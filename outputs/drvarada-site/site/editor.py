#!/usr/bin/env python
"""Live editor for drvarada.com — edit the rendered page, persist to source.

    python editor.py             # build, serve http://127.0.0.1:8789, open browser
    python editor.py --no-open   # build + serve only

The page in the browser is the editing surface. Everything a visitor can see can
be changed there, and every change is written back into the Python that produced
it — `content/*.py` for copy and images, `chrome.py` for shared constants,
`assets/site.css` and the design system for tokens. There is no separate draft
state and no database: the repo is the document.

Two ways of locating what to edit, in order of preference:

1. **By data address.** The preview build stamps `data-od="sections.4.h2"` onto
   the markup it renders (see `chrome.at`), so the browser can name the exact
   value behind an element. Unambiguous by construction — no guessing, no
   "this text appears in 16 places".
2. **By value.** Copy nested inside a prose paragraph or a table cell carries no
   address, so it is matched on its text through `resolver.py`, which is where
   the ambiguity prompt comes from.

Everything is validated before it sticks: an edit that breaks the build — a
superlative, a missing consent record, an unresolvable link — is reverted and
the build's own objection is shown in the browser. The linter reviews every
edit at the moment it is made.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import threading
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import datapatch
import media
import linkscan
import resolver
import versions

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
PORT = 8789

# Files whose change should rebuild and reload the browser. The design system
# is included: editing a token there must re-skin the open page immediately.
DS = ROOT.parent / "design-system"
WATCH_DIRS = [(ROOT / "content", "*.py"), (ROOT / "assets", "*.css"),
              (DS / "kit", "*.css"), (DS / "system", "*.css")]
WATCH_FILES = [ROOT / "chrome.py", ROOT / "build.py"]

# A per-run secret, handed to the overlay when the page is served and required on
# every mutating call. Binding to loopback is not protection on its own: any web
# page the user has open can POST here cross-origin without a preflight, and DNS
# rebinding would let it read the replies too. So we also pin Origin and Host.
SECRET = __import__("secrets").token_urlsafe(24)
ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}

_lock = threading.Lock()          # one edit/build at a time
_version = 0                      # bumped on every successful build
_cond = threading.Condition()
_last_error = ""                  # last build failure text, "" when green


# ── build + notify ───────────────────────────────────────────────────────────

def build() -> tuple[bool, str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}  # console CP mangles dashes
    r = subprocess.run([sys.executable, str(ROOT / "build.py")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()


def bump(error: str = "") -> None:
    global _version, _last_error
    with _cond:
        _version += 1
        _last_error = error
        _cond.notify_all()


def watched() -> dict[Path, float]:
    out = {}
    for f in WATCH_FILES:
        if f.exists():
            out[f] = f.stat().st_mtime
    for d, pat in WATCH_DIRS:
        if d.is_dir():
            for f in d.glob(pat):
                out[f] = f.stat().st_mtime
    return out


_seen_lock = threading.Lock()
_seen: dict = {}


def adopt_mtimes() -> None:
    """Tell the watcher that the current file state is already accounted for."""
    with _seen_lock:
        _seen.clear()
        _seen.update(watched())


def watch_sources() -> None:
    """Rebuild + reload whenever a source file changes outside the editor.

    Its own transactions must not count: without adopting the post-build mtimes
    every edit rebuilt twice and the browser reloaded twice, the second time
    landing after the user had started typing again.
    """
    adopt_mtimes()
    while True:
        time.sleep(0.7)
        now = watched()
        with _seen_lock:
            changed = now != _seen
            if changed:
                _seen.clear()
                _seen.update(now)
        if changed:
            with _lock:
                ok, out = build()
            bump("" if ok else out)


# ── the edit transaction ─────────────────────────────────────────────────────

def tracked() -> list[Path]:
    """Every file an edit may touch — computed per transaction, not once.

    This must include the design-system stylesheet: it holds most of the tokens,
    and when it sat outside the snapshot a rejected token edit stayed on disk
    while the response claimed the change had been reverted.
    """
    return [ROOT / "chrome.py", ROOT / "assets" / "site.css", token_file(),
            DS / "system" / "variables.css",
            *(ROOT / "content").glob("*.py")]


def snapshot() -> dict[Path, str]:
    return {f: f.read_text(encoding="utf-8") for f in tracked() if f.exists()}


def restore(snap: dict[Path, str]) -> None:
    for f, text in snap.items():
        if f.read_text(encoding="utf-8") != text:
            f.write_text(text, encoding="utf-8")


# ── history ──────────────────────────────────────────────────────────────────
# Ported from Open Design's project file versions — see versions.py for what was
# taken and why. The short version: the timeline is append-only, restoring an
# old version writes it forward as a new one, and nothing is ever discarded.

VERSION_STORE = ROOT / ".versions"
# Rooted at the project, not at site/: an edit can touch the design system's
# stylesheet, which sits beside site/ rather than inside it, and a version that
# cannot record the tokens is not a version of the site.
PROJECT = ROOT.parent
_history = versions.Versions(PROJECT, VERSION_STORE)


def _restore_files(files: dict[str, str]) -> None:
    """Write a version's content back to disk.

    Only files that actually differ are written. Every write bumps an mtime,
    and the source watcher would otherwise see the whole tracked set change and
    trigger a second rebuild behind the one this step already does.
    """
    for rel, text in files.items():
        f = PROJECT / rel
        if not f.exists() or f.read_text(encoding="utf-8") != text:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8")


def chrome_path() -> Path:
    return ROOT / "chrome.py"


def transaction(label: str, apply, *, undoable: bool = True) -> dict:
    """Apply a change, keep it only if the site still builds.

    This is the single gate every edit passes through. `apply(created)` mutates
    the source and returns the response payload, appending any files it wrote to
    `created`; if it raises, or if the build then fails, every tracked file goes
    back to how it was and those new files are deleted. A rejected upload must
    not leave an orphan in assets/img — otherwise refusing an unconsented
    patient photograph would still leave the photograph on disk.
    """
    created: list[Path] = []
    with _lock:
        snap = snapshot()

        def rollback():
            restore(snap)
            for f in created:
                f.unlink(missing_ok=True)

        try:
            payload = apply(created)
        except (datapatch.PatchError, media.MediaError, ValueError, KeyError) as exc:
            rollback()
            return {"error": str(exc)}
        ok, out = build()
        if not ok:
            rollback()
            build()                              # put dist/ back to last good
            return {"error": "Reverted — the build rejected this change:\n" + out}
        if undoable:
            _history.create(snapshot(), prompt=label)
        adopt_mtimes()
    bump()
    return {"ok": True, **payload, "history": _history.state()}


def _travel(move, *, append_restore: bool = False) -> dict:
    """Move to another point in the timeline, then rebuild — reverting if it breaks.

    Time travel can only fail if the files on disk moved out from under the
    stored version (an external edit, a git checkout). Rebuilding and checking
    is the same gate every forward edit passes, so a broken jump is put back
    rather than left for the user to find on the next save.
    """
    with _lock:
        before = snapshot()
        try:
            res = move()
        except versions.VersionError as exc:
            return {"error": str(exc)}
        if "error" in res:
            return res
        _restore_files(res.pop("files"))
        ok, out = build()
        if not ok:
            restore(before)
            build()
            return {"error": "That version does not build any more, so it was "
                             "put back:\n" + out}
        if append_restore:
            # Restoring writes the old content FORWARD as a new version, so the
            # version you came from is still reachable. This is the property
            # that makes the timeline safe to jump around in, and it is the one
            # thing Open Design's model gets right that a rewind cannot.
            entry = _history.note_restored(snapshot(), res["entry"])
            res["label"] = entry["label"]
        adopt_mtimes()
    bump()
    res.pop("entry", None)
    return {**res, "history": _history.state()}


def handle_undo(_req: dict) -> dict:
    return _travel(lambda: _history.step(-1))


def handle_redo(_req: dict) -> dict:
    return _travel(lambda: _history.step(+1))


def handle_restore(req: dict) -> dict:
    """Jump to any version in the timeline, not only the neighbouring one."""
    vid = str(req.get("id") or "")
    return _travel(lambda: _history.restore(vid), append_restore=True)


def handle_history(_req: dict) -> dict:
    """The version timeline, newest first."""
    return {"ok": True, **_history.state(), "entries": _history.timeline()}


# ── text ─────────────────────────────────────────────────────────────────────

def handle_edit(req: dict) -> dict:
    """Copy edit. Uses the data address when the markup carried one."""
    addr, slug = req.get("addr"), req.get("slug") or "index"
    new_html, new_text = req.get("newHTML", ""), req.get("newText", "")

    if addr:
        def apply(created):
            current = datapatch.read(slug, addr)
            # write back in the form the source is authored in: a literal that
            # already contains markup keeps markup, an escaped one stays plain
            value = new_html if (isinstance(current, str) and "<" in current) \
                else new_text
            f, line = datapatch.set_value(slug, addr, value, create=False)
            return {"file": str(f.relative_to(ROOT)), "line": line, "applied": 1}
        return transaction(new_text[:60] or addr, apply)

    old_html, old_text = req.get("oldHTML", ""), req.get("oldText", "")
    matches = resolver.find(old_html, old_text)
    if not matches:
        return {"error": "Couldn't find this text in the source. It may be built "
                         "by a template (an f-string) — edit chrome.py directly."}
    if len(matches) > 1 and not req.get("all"):
        return {"ambiguous": len(matches),
                "locations": [f"{m.file.name}:{m.lineno}" for m in matches]}

    def apply(created):
        for m in sorted(matches, key=lambda m: (str(m.file), -m.lineno, -m.col)):
            value = resolver.resolve_new_value(m, new_html, new_text)
            if m.value != m.value.strip():          # loose match: keep padding
                pad_l = m.value[:len(m.value) - len(m.value.lstrip())]
                pad_r = m.value[len(m.value.rstrip()):]
                value = pad_l + value.strip() + pad_r
            resolver.apply(m, value)
        first = matches[0]
        return {"file": str(first.file.relative_to(ROOT)),
                "line": first.lineno, "applied": len(matches)}
    return transaction(new_text[:60], apply)


# ── images ───────────────────────────────────────────────────────────────────

def promote_before_after(slug: str, addr: str) -> None:
    """Turn a `(title, caption)` before/after item into a dict so it can hold
    images.

    An item nobody has photographed yet is authored as a two-item tuple, which
    is the right shape for it — there is nothing else to say. The moment a photo
    arrives the item needs somewhere to put it, so supplying the first image
    rewrites the tuple as `{"title": …, "cap": …}` and the renderer picks up the
    richer form automatically.
    """
    m = re.match(r"^(.*\.items\.\d+)\.(before|after)$", addr or "")
    if not m:
        return
    parent = m.group(1)
    current = datapatch.read(slug, parent)
    if isinstance(current, (list, tuple)) and len(current) == 2:
        datapatch.set_value(slug, parent,
                            {"title": current[0], "cap": current[1]})


def handle_image(req: dict) -> dict:
    """Upload or replace an image at a data address.

    The address may point at a key that does not exist yet — that is the normal
    case, since an unshot slot has no image dict at all. `datapatch` creates it.
    """
    slug, addr = req.get("slug") or "index", req.get("addr")
    if not addr:
        return {"error": "That image has no data address, so it is part of the "
                         "template rather than page content — edit chrome.py."}
    # An image may only be attached where the renderer looks for one. This is
    # what keeps "create the key if missing" safe: the endpoint that creates
    # keys can only create these four, at a path that already resolves.
    if not re.fullmatch(r"(photo|sections\.\d+\.image"
                        r"|sections\.\d+\.items\.\d+\.(before|after))", addr):
        return {"error": f"'{addr}' is not an image slot."}
    data_url = req.get("dataUrl") or ""
    m = re.match(r"data:([\w/+.-]+);base64,(.*)$", data_url, re.S)
    if not m:
        return {"error": "Upload was not readable."}
    try:
        mime, raw = m.group(1), base64.b64decode(m.group(2), validate=True)
    except (ValueError, TypeError):
        return {"error": "Upload was not valid base64."}

    def apply(created):
        stored = media.save(raw, mime, req.get("filename") or slug)
        created.append(media.IMG_DIR / Path(stored["src"]).name)
        promote_before_after(slug, addr)
        current = datapatch.read(slug, addr) or {}
        image = {**(current if isinstance(current, dict) else {}), **stored}
        alt = (req.get("alt") or image.get("alt") or "").strip()
        if alt:
            image["alt"] = alt
        if req.get("focus"):
            image["focus"] = req["focus"]
        if req.get("consent"):
            image["consent"] = req["consent"]
        # keys in a stable, readable order
        order = ("src", "alt", "w", "h", "focus", "consent")
        image = {k: image[k] for k in order if k in image}
        f, line = datapatch.set_value(slug, addr, image)
        return {"file": str(f.relative_to(ROOT)), "line": line,
                "src": image["src"]}
    return transaction(f"image → {addr}", apply)


def handle_image_meta(req: dict) -> dict:
    """Change alt text, focal point or consent on an existing image."""
    slug, addr = req.get("slug") or "index", req.get("addr")

    def apply(created):
        image = datapatch.read(slug, addr)
        if not isinstance(image, dict):
            raise datapatch.PatchError("There is no image here yet.")
        for key in ("alt", "focus", "consent"):
            if key in req:
                value = (req[key] or "").strip()
                if value:
                    image[key] = value
                else:
                    image.pop(key, None)
        order = ("src", "alt", "w", "h", "focus", "consent")
        image = {k: image[k] for k in order if k in image}
        f, line = datapatch.set_value(slug, addr, image)
        return {"file": str(f.relative_to(ROOT)), "line": line}
    return transaction(f"image details → {addr}", apply)


def handle_image_clear(req: dict) -> dict:
    """Remove an image, returning the slot to its labelled placeholder."""
    slug, addr = req.get("slug") or "index", req.get("addr")

    def apply(created):
        f, line = datapatch.delete_key(slug, addr)
        return {"file": str(f.relative_to(ROOT)), "line": line}
    return transaction(f"remove image at {addr}", apply)


# ── links ────────────────────────────────────────────────────────────────────

def handle_link_where(req: dict) -> dict:
    """Everywhere a destination is used, so the inspector can offer the choice.

    Open Design's link inspector edits the one anchor you clicked, because an
    artifact is one file. A 45-page site needs the other question answered
    first: the Practo URL is on 60 buttons, and "change this one" is almost
    never what someone means.
    """
    target = (req.get("href") or "").strip()
    try:
        hits = linkscan.occurrences(target)
    except Exception as exc:                     # noqa: BLE001 — advisory only
        return {"ok": True, "count": 0, "note": str(exc)[:120]}
    return {"ok": True, "count": len(hits),
            "constant": next((h.const for h in hits if h.const and not h.sub), ""),
            "where": [h.where for h in hits[:12]]}


def handle_link(req: dict) -> dict:
    """Retarget a link — this one, or every use of the same destination.

    An internal link is a slug; an external one is a URL. When the current
    target is one of `chrome.py`'s shared constants (`PRACTO`, `PHONE`,
    `WHATSAPP`), the address points at a tuple element holding a *name*, not a
    string — so we edit the constant instead, which correctly updates every CTA
    on the site at once rather than detaching this one from the others.
    """
    slug, addr = req.get("slug") or "index", req.get("addr")
    target = (req.get("href") or "").strip()
    if not target:
        return {"error": "A link needs a destination."}
    label = req.get("label")
    old = (req.get("oldHref") or "").strip()

    if req.get("scope") == "all" and old and old != target:
        def apply_all(created):
            here = next((ln for ln in linkscan.occurrences(old)
                         if ln.slug == slug and ln.addr == (addr or "")), None)
            changed = linkscan.retarget(old, target)
            if not changed:
                raise datapatch.PatchError(
                    f"Nothing on the site points at {old} any more.")
            if label is not None and here is not None and here.addr:
                # The label belongs to this one button even when the
                # destination is shared — retargeting everywhere must not
                # rename every button on the site.
                current = datapatch.read(slug, here.addr)
                if isinstance(current, (list, tuple)) and len(current) >= 2:
                    datapatch.set_value(slug, f"{here.addr}.0", label,
                                        create=False)
            return {"applied": len(changed), "file": changed[0].split(":")[0],
                    "line": 0, "everywhere": changed[:8]}
        return transaction(f"{old} → {target} (everywhere)", apply_all)

    if (addr or "").startswith("chrome:"):
        # A nav or footer entry: the address resolves against a constant in
        # chrome.py rather than against a page, because that is where those
        # links actually live. Everything else about the edit is the same.
        name, _, subpath = addr[len("chrome:"):].partition(".")

        def apply_chrome(created):
            current = datapatch.read_in_constant(chrome_path(), name, subpath)
            if not isinstance(current, str):
                raise datapatch.PatchError(
                    f"{addr} does not point at a destination any more — the "
                    "page was probably rebuilt underneath the editor.")
            line = datapatch.set_in_constant(chrome_path(), name, subpath, target)
            if label is not None:
                parent = subpath.rsplit(".", 1)[0]
                current_label = datapatch.read_in_constant(
                    chrome_path(), name, f"{parent}.0")
                if isinstance(current_label, str) and label != current_label:
                    datapatch.set_in_constant(chrome_path(), name,
                                              f"{parent}.0", label)
            return {"file": "chrome.py", "line": line, "applied": 1}
        return transaction(f"{name}.{subpath} → {target}", apply_chrome)

    def apply(created):
        node_value = datapatch.read(slug, addr) if addr else None
        # >= 2 rather than == 2: a chip is (label, slug, accent) and a pillar
        # row is (label, slug) or (label, slug, flag). Only the first two
        # elements are the link; anything after them is carried through
        # untouched, so retargeting a chip does not drop its category colour.
        if addr and isinstance(node_value, (list, tuple)) and len(node_value) >= 2:
            new = [label if label is not None else node_value[0], target,
                   *node_value[2:]]
            # keep the container type — these files write links as tuples, and
            # turning one into a list on every edit is churn in the diff
            f, line = datapatch.set_value(
                slug, addr, tuple(new) if isinstance(node_value, tuple) else new)
            return {"file": str(f.relative_to(ROOT)), "line": line}
        # the tuple holds a constant reference: retarget the constant itself
        matches = [m for m in resolver.find(req.get("oldHref", ""),
                                           req.get("oldHref", ""))
                   if m.file.name == "chrome.py"]
        if not matches:
            raise datapatch.PatchError(
                "This link's destination is built from a template or a shared "
                "constant that isn't a plain string — edit chrome.py directly.")
        for m in matches:
            resolver.apply(m, target)
        note = None
        if label:
            # the label lives in the page's own tuple even when the destination
            # is a shared constant; write it too rather than silently dropping it
            current = datapatch.read(slug, addr) if addr else None
            if isinstance(current, (list, tuple)) and len(current) == 2:
                datapatch.set_value(slug, f"{addr}.0", label, create=False)
            else:
                note = ("The destination was updated everywhere it is used, but "
                        "this button's label is set by the template — edit "
                        "chrome.py to change it.")
        return {"file": "chrome.py", "line": matches[0].lineno,
                "applied": len(matches), **({"note": note} if note else {})}
    return transaction(f"link → {target}", apply)


def handle_constants(req: dict) -> dict:
    """Read or write the site-wide constants (Practo links, phone, WhatsApp).

    These are the outstanding TODOs; a form is a far better way to close them
    than asking someone to find nine places in the source.
    """
    names = ["PRACTO", "PRACTO_JH", "PRACTO_WM", "PRACTO_ONLINE", "PHONE",
             "WHATSAPP", "REVIEWER", "REVIEWED"]
    chrome_py = ROOT / "chrome.py"
    current = datapatch.read_constants(chrome_py, names)

    if not req.get("set"):
        return {"ok": True,
                "values": {n: current.get(n) for n in names},
                # a None value mirrors another constant and has nothing of its
                # own to edit; the panel shows it as read-only
                "mirrored": [n for n in names if current.get(n) is None]}

    def apply(created):
        changed = []
        for name, value in req["set"].items():
            if name not in names or not isinstance(value, str) or not value:
                continue
            if name in ("PRACTO", "PRACTO_JH", "PRACTO_WM", "PRACTO_ONLINE",
                        "PHONE", "WHATSAPP"):
                # These land inside href="…" on all 45 pages. Restrict them to
                # the schemes they are allowed to be, and reject anything that
                # could close the attribute.
                if not re.fullmatch(r"(https://|tel:\+?|mailto:)[\w@.\-+/?=&%#:~]*",
                                    value):
                    raise ValueError(
                        f"{name} must be an https:// URL, a tel:+… number or a "
                        "mailto: address, with no quotes or spaces.")
            if re.search(r"""["'<>]""", value):
                raise ValueError(f"{name} may not contain quotes or angle brackets.")
            if current.get(name) == value:
                continue
            datapatch.set_constant(chrome_py, name, value)
            changed.append(name)
        if not changed:
            raise datapatch.PatchError("Nothing to change.")
        return {"file": "chrome.py", "changed": changed}
    return transaction("site details", apply)


# ── structure ────────────────────────────────────────────────────────────────

def handle_structure(req: dict) -> dict:
    """Move, duplicate or delete a section — or an item inside one.

    Open Design left this out of its editor because its target is an HTML file,
    where moving a section means re-serializing the DOM. Here a section is an
    element of a Python list, so the operation is exact and the diff is
    reviewable.
    """
    slug = req.get("slug") or "index"
    op, path, index = req.get("op"), req.get("list"), int(req.get("index", 0))
    if not path:
        return {"error": "Nothing addressable selected."}

    def apply(created):
        if op == "up":
            f, line = datapatch.reorder(slug, path, index, -1)
        elif op == "down":
            f, line = datapatch.reorder(slug, path, index, +1)
        elif op == "duplicate":
            f, line = datapatch.duplicate(slug, path, index)
        elif op == "delete":
            f, line = datapatch.remove(slug, path, index)
        else:
            raise ValueError(f"Unknown operation '{op}'.")
        return {"file": str(f.relative_to(ROOT)), "line": line}
    return transaction(f"{op} {path}.{index}", apply)


# ── design tokens ────────────────────────────────────────────────────────────

TOKEN_FILES = [ROOT / "assets" / "site.css",
               DS / "kit" / "colors_and_type.css",
               DS / "system" / "variables.css",
               ROOT.parent / "pages" / "landing" / "assets" / "design-system.css"]
# Several tokens share a line in the design system. Anchoring to ^ hid six of
# them; anchoring to `;` still missed every second one, because each match
# consumes the semicolon the next one would need. No anchor is needed at all:
# a token *declaration* requires a colon, and `var(--x)` has none.
TOKEN_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+);")


def token_file() -> Path:
    """The design system stylesheet the build actually consumes."""
    for f in TOKEN_FILES[1:]:
        if f.exists():
            return f
    return TOKEN_FILES[0]


def handle_tokens(_req: dict) -> dict:
    """Every design token, so the panel can offer them for editing.

    Editing a token is the *right* way to restyle a generated site: it changes
    every surface that uses it, consistently, and it cannot drift from the
    design system the way a one-off inline style would. This is deliberately
    offered instead of Open Design's per-element inline style controls — those
    make sense for a standalone artifact and would be pure entropy here.
    """
    out = []
    for f in (token_file(), ROOT / "assets" / "site.css"):
        if not f.exists():
            continue
        css = f.read_text(encoding="utf-8")
        root = re.search(r":root\s*\{(.*?)\}", css, re.S)
        if not root:
            continue
        for m in TOKEN_RE.finditer(root.group(1)):
            value = m.group(2).strip()
            out.append({"name": m.group(1), "value": value, "file": f.name,
                        "kind": "color" if re.match(
                            r"^(#|rgb|hsl|oklch|color-mix)", value) else "text"})
    return {"ok": True, "tokens": out}


def handle_token_set(req: dict) -> dict:
    name, value = req.get("name", ""), (req.get("value") or "").strip()
    if not re.fullmatch(r"--[\w-]+", name):
        return {"error": "Not a token name."}
    if not value or len(value) > 200:
        return {"error": "That value isn't a legal CSS value."}
    # A blocklist of punctuation is not enough: `url(javascript:…)` contains no
    # forbidden character, yet a token used in `background-image` would then
    # fetch or execute it. So the grammar is an allowlist of the value shapes a
    # design token actually takes — colours, lengths, keywords, font stacks,
    # easing curves, shadows, gradients — and nothing that can reference a URL.
    if "\n" in value or "\r" in value:
        return {"error": "A token value must be a single line."}
    if re.search(r"url\s*\(|javascript:|expression\s*\(|@import|/\*", value, re.I):
        return {"error": "A design token may not reference a URL or a script."}
    if not re.fullmatch(
            r"[#\w\s.,%()/+*-]+|"                      # values, functions, lists
            r"(['\"][^'\"<>;{}]*['\"][\s,]*)+[\w\s,.-]*",   # quoted font names
            value):
        return {"error": "That value isn't a legal CSS value."}

    def apply(created):
        for f in (token_file(), ROOT / "assets" / "site.css"):
            if not f.exists():
                continue
            css = f.read_text(encoding="utf-8")
            pattern = re.compile(
                rf"((?:^|;)\s*{re.escape(name)}\s*:\s*)([^;]+)(;)", re.M)
            if not pattern.search(css):
                continue
            f.write_text(pattern.sub(lambda m: m.group(1) + value + m.group(3),
                                     css, count=1), encoding="utf-8")
            return {"file": f.name, "name": name, "value": value}
        raise datapatch.PatchError(f"{name} is not declared in a :root block.")
    return transaction(f"{name} = {value}", apply)


# ── inspection: what the panel needs to know about a target ──────────────────

def handle_inspect(req: dict) -> dict:
    slug, addr = req.get("slug") or "index", req.get("addr")
    out: dict = {"ok": True}
    if addr:
        out["value"] = datapatch.read(slug, addr)
    if req.get("wantSlugs"):
        from content.urls import URLS
        out["slugs"] = sorted(URLS)
    if req.get("wantUnused"):
        out["unused"] = media.unused()
    return out


def handle_locate(req: dict) -> dict:
    slug, addr = req.get("slug") or "index", req.get("addr")
    if addr:
        try:
            site, page = datapatch.find_page(slug)
            node = datapatch.walk(page, addr)
            return {"locations": [{"file": str(site.file.relative_to(ROOT)),
                                   "line": node.lineno}]}
        except datapatch.PatchError as exc:
            return {"error": str(exc)}
    matches = resolver.find(req.get("oldHTML", ""), req.get("oldText", ""))
    if not matches:
        return {"error": "Not found in source — likely template markup (chrome.py)."}
    return {"locations": [{"file": str(m.file.relative_to(ROOT)), "line": m.lineno}
                          for m in matches]}


def handle_open(req: dict) -> dict:
    """Jump to a source location in VS Code (uses `code -g`)."""
    target = (ROOT / req["file"]).resolve()
    if not target.is_file() or ROOT.resolve() not in target.parents:
        return {"error": "bad path"}
    spot = f"{target}:{int(req.get('line', 1))}"
    subprocess.Popen(f'code -g "{spot}"', shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"ok": True}


ROUTES = {
    "/api/edit": handle_edit,
    "/api/image": handle_image,
    "/api/image-meta": handle_image_meta,
    "/api/image-clear": handle_image_clear,
    "/api/link": handle_link,
    "/api/link-where": handle_link_where,
    "/api/constants": handle_constants,
    "/api/structure": handle_structure,
    "/api/tokens": handle_tokens,
    "/api/token-set": handle_token_set,
    "/api/inspect": handle_inspect,
    "/api/locate": handle_locate,
    "/api/open": handle_open,
    "/api/undo": handle_undo,
    "/api/redo": handle_redo,
    "/api/history": handle_history,
    "/api/restore": handle_restore,
}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):               # keep the console readable
        pass

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _bytes(self, body: bytes, kind: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path.startswith("/__editor__/"):
            name = path.rsplit("/", 1)[-1]
            asset = ROOT / "editor" / name
            if asset.is_file() and asset.parent == ROOT / "editor":
                kind = "text/javascript" if name.endswith(".js") else "text/css"
                self._bytes(asset.read_bytes(), f"{kind}; charset=utf-8")
            else:
                self.send_error(404)
            return

        if path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            known = _version
            try:
                self.wfile.write(f"data: {json.dumps({'version': known})}\n\n"
                                 .encode())
                self.wfile.flush()
                while True:
                    with _cond:
                        _cond.wait(timeout=15)
                        v, err = _version, _last_error
                    if v != known:
                        known = v
                        msg = {"version": v, "error": err}
                        self.wfile.write(f"data: {json.dumps(msg)}\n\n".encode())
                    else:
                        self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except (ConnectionError, OSError):
                return
            return

        # everything else is a dist/ file, with the overlay injected into pages
        file = (DIST / (path.lstrip("/") or "index.html")).resolve()
        if file.is_dir():
            file = file / "index.html"
        # `..` in the request must not escape dist/. The fall-through to
        # SimpleHTTPRequestHandler sanitises itself; this branch did not.
        if DIST.resolve() not in file.parents:
            self.send_error(404)
            return
        if file.suffix == ".html" and file.is_file():
            html = file.read_text(encoding="utf-8")
            html = html.replace(
                "</body>",
                '<link rel="stylesheet" href="/__editor__/editor.css">'
                f'<script>window.__odToken={json.dumps(SECRET)}</script>'
                '<script defer src="/__editor__/editor.js"></script></body>')
            self._bytes(html.encode("utf-8"), "text/html; charset=utf-8")
            return
        super().do_GET()

    def _authorised(self) -> bool:
        if self.headers.get("X-OD-Token") != SECRET:
            return False
        host = (self.headers.get("Host") or "").lower()
        if host not in ALLOWED_HOSTS:
            return False
        origin = self.headers.get("Origin")
        if origin and origin.lower() not in {f"http://{h}" for h in ALLOWED_HOSTS}:
            return False
        return True

    def do_POST(self):
        if not self._authorised():
            self._json({"error": "Not authorised — reload the editor page."}, 403)
            return
        length = int(self.headers.get("Content-Length", 0))
        if length > 32 * 1024 * 1024:
            self._json({"error": "Request too large."}, 413)
            return
        try:
            req = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json({"error": "bad json"}, 400)
            return
        handler = ROUTES.get(self.path.split("?", 1)[0])
        if not handler:
            self._json({"error": "no such route"}, 404)
            return
        try:
            self._json(handler(req))
        except Exception as exc:                     # surface, don't crash serve
            self._json({"error": f"{type(exc).__name__}: {exc}"}, 500)


def main() -> int:
    ok, out = build()
    print(out.splitlines()[-1] if ok else out)
    if not ok:
        return 1

    # Capture whatever is on disk before the first edit can bury it. This is
    # Open Design's `ensureCurrentProjectFileVersion`, and it earns its keep in
    # a git working tree: check out a branch, start the editor, make one edit,
    # and without this the pre-edit state has no version to go back to.
    seeded = _history.ensure_current(snapshot())
    state = _history.state()
    print(f"history: {state['depth']} version(s), on v{state['version']}"
          + ("  (captured the current files as a new version)" if seeded else ""))

    threading.Thread(target=watch_sources, daemon=True).start()
    handler = partial(Handler, directory=str(DIST))
    server = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"live editor at {url}  (Ctrl+C to stop)")
    print('in VS Code: Ctrl+Shift+P -> "Simple Browser: Show" -> paste the URL')
    if "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
