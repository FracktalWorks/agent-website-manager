"""UserPromptSubmit hook: ride open live-editor feedback along with every prompt.

The live editor's Note tool pins "change this to that" to a page element and
writes it to `outputs/<site>/site/.feedback/notes.jsonl`. This hook checks
those folders on every prompt and, when open items exist, prints a compact
context block to stdout — Claude Code appends stdout (exit 0) to the prompt's
context. Silent (no output) when there is nothing open, so the common case
costs zero tokens.

Each item carries the source file and line the address resolved to when it was
pinned, so the work list arrives ready to act on rather than ready to search.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MAX_ITEMS = 15

sys.stdout.reconfigure(encoding="utf-8")
repo = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()

items: list[str] = []
extra = 0
for build in sorted(repo.glob("outputs/*/site/build.py")):
    site = build.parent.parent.name
    f = build.parent / ".feedback" / "notes.jsonl"
    if not f.exists():
        continue
    for line in f.read_text(encoding="utf-8").splitlines():
        try:
            n = json.loads(line)
        except json.JSONDecodeError:
            continue
        if n.get("status") != "open":
            continue
        if len(items) >= MAX_ITEMS:
            extra += 1
            continue
        where = n.get("addr") or n.get("sel") or "?"
        src = (f' → outputs/{site}/site/{n["file"]}:{n.get("line")}'
               if n.get("file") else "")
        was = n.get("value") or n.get("context")
        ctx = f' on "{was}"' if was else ""
        items.append(
            f'- [{site} · {n.get("slug")}] {where}{src}{ctx} — '
            f'"{n.get("text")}" (id {n.get("id")})')

if not items:
    sys.exit(0)

n = len(items) + extra
print(f"""<site-feedback>
The user pinned {n} unresolved change(s) to page elements in the live editor.
If the current request concerns those sites, act on the relevant items as part
of it — the user expects them to be seen without re-explaining. Each line is
`page  address → source:line  on "current value" — what to change`. Patch the
data-od address in content/*.py rather than matching on text; the source line
is where it resolved when it was pinned, so confirm it before editing.
{chr(10).join(items)}{f'{chr(10)}…and {extra} more — read the site’s .feedback/notes.jsonl for the rest.' if extra else ''}
After acting on an item, mark it done: set status="done" and add a "resolved"
timestamp on that line in the site's .feedback/notes.jsonl. Ignore this block
if the request is unrelated.
</site-feedback>""")
