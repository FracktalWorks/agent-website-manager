"""site-feedback — an MCP stdio server over every site's `.feedback/` folder.

UNREGISTERED 2026-07-31. Kept on disk, wired to nothing. It was removed from
`.mcp.json` and `.vscode/mcp.json` because its two tools cost a process and
two tool schemas in every session to wrap a JSONL file any agent can already
read and edit — and with the editor's ⚑ Agent button now handing the user the
whole queue as one pasteable prompt, there was nothing left for it to do that
`Read` did not. To bring it back, re-add:

    "site-feedback": {"type": "stdio", "command": "python",
                      "args": [".tmp/scripts/feedback_mcp.py"]}

The live editor's Note tool pins "change this to that" to a page element and
writes it to `outputs/<site>/site/.feedback/notes.jsonl`. This server gives
GitHub Copilot (agent mode, via .vscode/mcp.json) and Claude Code (via
.mcp.json) direct tools over that folder, so the user can annotate a page in
the browser and the sidebar agent can list and resolve the feedback without
being told where the files live.

Each note carries the element's data address *and* the source file and line it
resolved to when it was pinned, so acting on one is an edit, not a search.

A `get_screenshot` tool used to live here, serving PNGs captured by the
editor's Shot button. Both were removed 2026-07-31 — the user screenshots
their own screen and pastes it into the chat, which no tool needs to mediate.

Pure stdlib: MCP's stdio transport is newline-delimited JSON-RPC 2.0, one
message per line on stdin/stdout, logs to stderr. No pip install needed.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SERVER_INFO = {"name": "site-feedback", "version": "1.0.0"}
KNOWN_PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18"}


# ── the feedback store ───────────────────────────────────────────────────────

def sites() -> dict[str, Path]:
    """site name → its .feedback dir (existing or not) for every generated site."""
    out = {}
    for build in sorted(REPO.glob("outputs/*/site/build.py")):
        out[build.parent.parent.name] = build.parent / ".feedback"
    return out


def notes_for(fb: Path) -> list[dict]:
    f = fb / "notes.jsonl"
    items = []
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def save_notes(fb: Path, items: list[dict]) -> None:
    fb.mkdir(exist_ok=True)
    (fb / "notes.jsonl").write_text(
        "".join(json.dumps(n, ensure_ascii=False) + "\n" for n in items),
        encoding="utf-8")


def describe(site: str, n: dict) -> dict:
    """A note as the agent should see it: repo-relative paths, no noise."""
    out = {"site": site, "id": n.get("id"), "page": n.get("slug"),
           "change": n.get("text"), "when": n.get("ts")}
    if n.get("addr"):
        out["data_od_address"] = n["addr"]
    # Resolved when the note was pinned, against the file as it was then. It is
    # a starting point, not a promise — an edit since could have moved the line.
    if n.get("file"):
        out["source"] = f"outputs/{site}/site/{n['file']}:{n.get('line')}"
    if n.get("value"):
        out["current_value"] = n["value"]
    elif n.get("context"):
        out["element_text"] = n["context"]
    if not n.get("addr") and n.get("sel"):
        out["css_path"] = n["sel"]
    return out


# ── tools ────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_feedback",
        "description": (
            "List the changes the user pinned to page elements in the live "
            "editor. Each item names the page, the data-od address to patch, "
            "the source file and line it lives on, and the current value — so "
            "acting on one is an edit, not a search. ALWAYS call this before "
            "improving a generated site; act on items that relate to the "
            "request, then mark them done with resolve_note."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "site": {"type": "string",
                         "description": "Limit to one site (e.g. 'drvarada-site'). Omit for all sites."},
                "include_done": {"type": "boolean",
                                 "description": "Also list resolved items (default false)."},
            },
        },
    },
    {
        "name": "resolve_note",
        "description": (
            "Mark a feedback item done after acting on it (the live editor "
            "shows open items as red pins on the page, so stale entries "
            "mislead the user). Pass the site and note id from list_feedback."),
        "inputSchema": {
            "type": "object",
            "properties": {"site": {"type": "string"}, "id": {"type": "string"}},
            "required": ["site", "id"],
        },
    },
]


def tool_list_feedback(args: dict) -> list[dict]:
    only, include_done = args.get("site"), bool(args.get("include_done"))
    store = sites()
    if only and only not in store:
        return text_block(f"No site named {only!r}. Sites: {', '.join(store) or '(none)'}.")
    picked = {only: store[only]} if only else store
    items, done = [], 0
    for site, fb in picked.items():
        for n in notes_for(fb):
            if n.get("status") == "open":
                items.append(describe(site, n))
            else:
                done += 1
                if include_done:
                    items.append({**describe(site, n), "status": "done"})
    if not items:
        return text_block("No open feedback. "
                          + (f"({done} resolved items exist — pass include_done to see them.)"
                             if done else "The user has not pinned anything in the live editor."))
    head = (f"{len(items)} pinned change(s). Each carries the element's data-od "
            "address — patch that address in the site's content/*.py, don't "
            "guess from text. `source` is where it resolved when it was pinned; "
            "verify before editing, the file may have moved on. Rebuild with "
            "build.py afterwards, and call resolve_note per item handled.")
    return text_block(head + "\n" + json.dumps(items, ensure_ascii=False, indent=1))


def tool_resolve_note(args: dict) -> list[dict]:
    site, store = args.get("site"), sites()
    if site not in store:
        return text_block(f"No site named {site!r}. Sites: {', '.join(store)}.", error=True)
    fb, items, hit = store[site], notes_for(store[site]), False
    for n in items:
        if n.get("id") == args.get("id") and n.get("status") == "open":
            n["status"], n["resolved"] = "done", time.strftime("%Y-%m-%d %H:%M")
            hit = True
    if not hit:
        return text_block("That note is not open (wrong id, or already resolved).", error=True)
    save_notes(fb, items)
    left = sum(1 for n in items if n.get("status") == "open")
    return text_block(f"Resolved. {left} item(s) still open on {site}.")


def text_block(text: str, error: bool = False) -> list[dict]:
    blocks = [{"type": "text", "text": text}]
    if error:
        blocks[0]["_isError"] = True
    return blocks


# ── JSON-RPC over stdio ──────────────────────────────────────────────────────

def reply(msg_id, result=None, error=None) -> None:
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(msg: dict) -> None:
    method, msg_id, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
    if method == "initialize":
        proto = params.get("protocolVersion")
        reply(msg_id, {"protocolVersion": proto if proto in KNOWN_PROTOCOLS else "2024-11-05",
                       "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO})
    elif method == "ping":
        reply(msg_id, {})
    elif method == "tools/list":
        reply(msg_id, {"tools": TOOLS})
    elif method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        fn = {"list_feedback": tool_list_feedback,
              "resolve_note": tool_resolve_note}.get(name)
        if fn is None:
            reply(msg_id, error={"code": -32602, "message": f"unknown tool {name!r}"})
            return
        try:
            blocks = fn(args)
        except Exception as e:  # a tool error is a result, not a protocol error
            reply(msg_id, {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}],
                           "isError": True})
            return
        is_error = any(b.pop("_isError", False) for b in blocks)
        reply(msg_id, {"content": blocks, "isError": is_error})
    elif msg_id is not None:  # unknown *request* — notifications are ignored
        reply(msg_id, error={"code": -32601, "message": f"method {method!r} not found"})


def main() -> None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            handle(msg)
        except Exception as e:
            print(f"site-feedback: {type(e).__name__}: {e}", file=sys.stderr)
            if msg.get("id") is not None:
                reply(msg["id"], error={"code": -32603, "message": str(e)})


if __name__ == "__main__":
    main()
