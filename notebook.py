"""The project notebook: where we left off, and what is written down.

WHY THIS EXISTS
    The hub could already show what a brand OWNS — pages, print, brand assets,
    concept rounds. It could not show what anyone KNEW about it. So every time
    a project was picked up again, the state of it lived in three places that
    are all worse than a page: a chat transcript that had scrolled away, a
    memory file the user cannot read, and a `.md` sitting in the project folder
    that you had to already know the name of.

    A project's own notes are the first thing you want when you reopen it, and
    the last thing anybody writes down. This makes them a surface.

TWO DIFFERENT THINGS, DELIBERATELY
    THE SCRATCHPAD (`NOTES.md` at the project root) is one file, always
    editable in the hub, always shown first. It answers "where did we leave
    off". It is a scratchpad on purpose: no schema, no front matter, no
    required headings. A notes feature that demands a format is a notes
    feature nobody writes in.

    THE DOCUMENTS are every other `.md` the project already has — plans,
    runbooks, audit write-ups. They are read-only here. They are written by
    whoever is doing the work, in the repo, and the hub's job is to make them
    findable and readable, not to become a second editor for them.

WHERE IT LOOKS
    `<project>/*.md` and `<project>/notes/**/*.md`. Root level because that is
    where this repo already puts project docs (PRINTSTICK-SEO-PLAN.md,
    REDIRECTS.md, TRANSFER.json's neighbours); `notes/` because a project that
    accumulates many wants somewhere to put them that is not the root.

    The repo's underscore convention holds here as everywhere else: a leading
    underscore anywhere in the path means scaffolding, and scaffolding is not
    a document.

THE MARKDOWN RENDERER
    Deliberately small, and deliberately not a dependency. It covers what
    these documents actually use — headings, paragraphs, lists, fenced code,
    tables, block quotes, rules, and inline code/bold/italic/links — and
    nothing else. It is not CommonMark and does not pretend to be. Anything it
    does not understand survives as escaped text rather than vanishing, which
    is the only property that really matters for a preview: you must never
    look at this pane and believe a document says less than it does.
"""

from __future__ import annotations

import html
import pathlib
import re
import time

SKIP_DIRS = {"__pycache__", "node_modules", ".git", ".versions", "dist",
             "dist-prod"}
SCRATCH = "NOTES.md"

# The scratchpad a project gets the first time somebody opens the tab. Prompts
# rather than headings-to-fill-in: the questions are what make somebody type.
TEMPLATE = """# Notes

_Scratchpad for this project. Nothing here is generated — edit freely._

## Where we left off


## What's next


## Open questions / waiting on


## Things worth remembering

"""


def _working(rel: pathlib.PurePath) -> bool:
    """Scaffolding, by the repo's own convention: an underscore anywhere."""
    return any(part.startswith("_") for part in rel.parts)


def _title_of(text: str, fallback: str) -> str:
    """The document's own H1, which is what it calls itself."""
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def _summary(text: str) -> str:
    """The first real sentence, for the list. Skips the title and any
    metadata line, because "Written 2026-09-15 from Search Console" is not
    what the document is about."""
    for raw in text.splitlines():
        line = raw.strip()
        if (not line or line.startswith(("#", ">", "|", "-", "*", "`", "_"))
                or line.startswith("![")):
            continue
        line = re.sub(r"[*_`]", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        return line[:160]
    return ""


def docs(project_dir: pathlib.Path) -> list[dict]:
    """Every markdown document this project owns, scratchpad first.

    Ordered by recency after that, because the document somebody touched last
    is the one they came back for — the same rule the project shelf uses.
    """
    project_dir = pathlib.Path(project_dir)
    found: list[pathlib.Path] = sorted(project_dir.glob("*.md"))
    notes_dir = project_dir / "notes"
    if notes_dir.is_dir():
        found += sorted(p for p in notes_dir.rglob("*.md")
                        if not (set(p.parts) & SKIP_DIRS))

    out = []
    for f in found:
        rel = f.relative_to(project_dir)
        if _working(rel):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        st = f.stat()
        out.append({
            "id": re.sub(r"[^a-z0-9]+", "-", rel.as_posix().lower()).strip("-"),
            "rel": rel.as_posix(),
            "name": f.name,
            "title": _title_of(
                text, f.stem.replace("-", " ").replace("_", " ")),
            "summary": _summary(text),
            "scratch": rel.as_posix() == SCRATCH,
            "words": len(text.split()),
            "mtime": st.st_mtime,
            "when": time.strftime("%d %b %Y",
                                 time.localtime(st.st_mtime)),
            "text": text,
        })
    out.sort(key=lambda d: (not d["scratch"], -d["mtime"]))
    return out


def scratch_path(project_dir: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(project_dir) / SCRATCH


def read_scratch(project_dir: pathlib.Path) -> str:
    p = scratch_path(project_dir)
    if p.is_file():
        return p.read_text(encoding="utf-8", errors="replace")
    return ""


def write_scratch(project_dir: pathlib.Path, text: str) -> dict:
    """Save the scratchpad. Returns what the UI needs to confirm it landed.

    Normalises line endings, because the textarea posts \\r\\n on Windows and
    a file that grows a carriage return per line every save is a file that
    diffs badly forever.
    """
    p = scratch_path(project_dir)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text and not text.endswith("\n"):
        text += "\n"
    p.write_text(text, encoding="utf-8")
    st = p.stat()
    return {"ok": True, "bytes": st.st_size, "rel": SCRATCH,
            "when": time.strftime("%H:%M", time.localtime(st.st_mtime))}


# ------------------------------------------------------------------ markdown

_CODE_SPAN = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_ITAL = re.compile(r"(?<![*\w])\*(?!\s)([^*]+?)(?<!\s)\*(?!\*)")
# `_like this_`, but never inside a word. `wp_head`, `snake_case` and
# `tax_rate_compound` are all over these documents and none of them are
# emphasis, so both edges need a non-word character outside them.
_ITAL_U = re.compile(r"(?<![\w*_])_(?!\s)([^_]+?)(?<!\s)_(?![\w_])")
_BARE = re.compile(r"(?<![\"'=(>])\bhttps?://[^\s<>)\"']+")


def _inline(text: str) -> str:
    """Inline formatting, with code spans held out of it.

    Code spans are extracted BEFORE anything else and put back last, so
    `**kwargs` inside backticks stays `**kwargs` instead of turning half the
    paragraph bold — which is exactly the failure a naive ordering produces on
    a page full of shell and Python.
    """
    held: list[str] = []

    def hold(m):
        held.append(html.escape(m.group(1)))
        return f"\x00{len(held) - 1}\x00"

    text = _CODE_SPAN.sub(hold, text)
    text = html.escape(text)
    text = _LINK.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" '
                  f'target="_blank" rel="noopener">{m.group(1)}</a>', text)
    text = _BARE.sub(lambda m: f'<a href="{m.group(0)}" target="_blank" '
                               f'rel="noopener">{m.group(0)}</a>', text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITAL.sub(r"<em>\1</em>", text)
    text = _ITAL_U.sub(r"<em>\1</em>", text)
    for i, code in enumerate(held):
        text = text.replace(f"\x00{i}\x00", f"<code>{code}</code>")
    return text


def _row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render(md: str) -> str:
    """Markdown to HTML. Small on purpose — see the module docstring."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    para: list[str] = []
    list_stack: list[str] = []          # 'ul' / 'ol', innermost last

    def close_para():
        if para:
            out.append(f"<p>{_inline(' '.join(para))}</p>")
            para.clear()

    def close_lists():
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    def continue_item(text: str) -> bool:
        """Fold a wrapped line back into the list item it belongs to.

        Markdown calls this lazy continuation, and without it a four-item
        numbered list whose items wrap onto a second line renders as four
        separate lists — each restarting at 1, with every wrapped line adrift
        as its own paragraph between them. That is the document saying
        something other than what it says, which is the one thing this
        renderer must not do.
        """
        for j in range(len(out) - 1, -1, -1):
            if out[j].startswith("<li>"):
                out[j] = out[j][:-len("</li>")] + " " + _inline(text) + "</li>"
                return True
            if not out[j].startswith(("<ul>", "<ol>")):
                return False
        return False

    # A blank line does not end a list on its own: items separated by blank
    # lines are one loose list, and closing on the blank restarted the
    # numbering. So the blank is remembered, and what comes next decides.
    blank = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code — verbatim, and the fence language becomes a class
        if stripped.startswith("```"):
            close_para()
            close_lists()
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang, quote=True)}"' if lang else ""
            out.append(f"<pre><code{cls}>"
                       + html.escape("\n".join(buf)) + "</code></pre>")
            continue

        if not stripped:
            close_para()
            blank = True                 # what follows decides, see above
            i += 1
            continue

        # table: a header row followed by a |---|---| delimiter
        if (stripped.startswith("|") and i + 1 < n
                and re.fullmatch(r"\|[\s:|-]+\|?", lines[i + 1].strip())):
            close_para()
            close_lists()
            head = _row(stripped)
            i += 2
            body = []
            while i < n and lines[i].strip().startswith("|"):
                body.append(_row(lines[i]))
                i += 1
            th = "".join(f"<th>{_inline(c)}</th>" for c in head)
            rows = "".join(
                "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>"
                for r in body)
            out.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead>'
                       f"<tbody>{rows}</tbody></table></div>")
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            close_para()
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"(#{1,6})\s+(.+?)\s*#*$", stripped)
        if m:
            close_para()
            close_lists()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        if stripped.startswith(">"):
            close_para()
            close_lists()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(buf))}</blockquote>")
            continue

        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            close_para()
            blank = False
            indent = len(m.group(1))
            kind = "ol" if m.group(2)[0].isdigit() else "ul"
            depth = indent // 2 + 1
            while len(list_stack) > depth:
                out.append(f"</{list_stack.pop()}>")
            if len(list_stack) < depth:
                out.append(f"<{kind}>")
                list_stack.append(kind)
            elif list_stack and list_stack[-1] != kind:
                out.append(f"</{list_stack.pop()}>")
                out.append(f"<{kind}>")
                list_stack.append(kind)
            out.append(f"<li>{_inline(m.group(3))}</li>")
            i += 1
            continue

        # Plain text. Inside an open list and with no blank line since the
        # last item, this is a wrapped continuation of that item, not a new
        # paragraph — see continue_item().
        if list_stack and not blank and continue_item(stripped):
            i += 1
            continue
        close_lists()
        blank = False
        para.append(stripped)
        i += 1

    close_para()
    close_lists()
    return "\n".join(out)


def kind(project_dir: pathlib.Path) -> dict | None:
    """The artefact kind, in the shape `artifacts.kinds()` hands the hub.

    Returns a kind even when the project has written nothing yet — an empty
    scratchpad with a prompt in it is the whole point, and a notebook that
    only appears once you have already made notes somewhere else is a
    notebook nobody starts using.
    """
    items = docs(project_dir)
    has_scratch = any(d["scratch"] for d in items)
    others = [d for d in items if not d["scratch"]]
    if not has_scratch:
        note = ("no notes yet" if not others
                else f"{len(others)} doc{'s' * (len(others) != 1)}, "
                     "no scratchpad yet")
    else:
        scratch = next(d for d in items if d["scratch"])
        note = f"updated {scratch['when']}"
        if others:
            note += f" · {len(others)} doc{'s' * (len(others) != 1)}"
    return {"id": "notes", "label": "Notes & docs",
            "count": len(items), "kind": "notes", "items": items,
            "note": note}


if __name__ == "__main__":                       # quick look from the CLI
    import sys
    # These documents are full of arrows, dashes and ₹ — cp1252 cannot encode
    # any of them, and the traceback looks like a discovery bug rather than a
    # console one.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                            # noqa: BLE001
        pass
    d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                     else "outputs/fracktal-site")
    k = kind(d)
    print(f"\n  {k['label']}  —  {k['note']}\n")
    for doc in k["items"]:
        flag = "scratchpad" if doc["scratch"] else f"{doc['words']:>6} words"
        print(f"    {doc['rel']:<34} {flag:>12}  {doc['when']}")
        if doc["summary"]:
            print(f"      {doc['summary'][:92]}")
