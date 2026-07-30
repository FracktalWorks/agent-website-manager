"""Edit page data by address instead of by matching text.

`resolver.py` finds a literal by its *value*, which is the only option for copy
buried inside a prose list — but it cannot tell 16 identical "Book on Practo"
strings apart. This module addresses the data structurally instead:

    sections.4.h2                 the h2 of the fifth section
    sections.4.items.0.title      a card title inside it
    photo                         a page-level key
    sections.6.items.2.before     a before/after image slot

The renderer emits these addresses into preview HTML as `data-od` attributes, so
the browser can name exactly the value it edited. Nothing is guessed, so nothing
has to be disambiguated — and unlike Open Design's DOM child-index paths, an
address survives markup changes, because it points at the data, not the layout.

Everything here works on the AST for *locating* and on source spans for
*writing*: the file keeps its formatting, comments and hand-wrapped strings, and
a patch touches only the bytes it must. Every write re-parses the result and
rolls back if the file would stop being valid Python.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from resolver import (MAX_LINE, SEARCH_FILES, _format_literal, _quote,
                      char_col)

ROOT = Path(__file__).parent
# only these declare pages; chrome.py holds the template, not page data
CONTENT_FILES = [p for p in SEARCH_FILES if p.parent.name == "content"]


class PatchError(Exception):
    """A patch that cannot be applied safely — reported to the user verbatim."""


@dataclass
class Site:
    """One content module, parsed. Spans are only valid until the file changes."""
    file: Path
    source: str
    tree: ast.Module


def _load(path: Path) -> Site:
    src = path.read_text(encoding="utf-8")
    return Site(file=path, source=src, tree=ast.parse(src))


def _page_dicts(site: Site) -> dict[str, ast.Dict]:
    """slug -> the dict literal that declares it."""
    out: dict[str, ast.Dict] = {}
    for node in ast.walk(site.tree):
        if not isinstance(node, ast.Dict):
            continue
        for k, v in zip(node.keys, node.values):
            if (isinstance(k, ast.Constant) and k.value == "slug"
                    and isinstance(v, ast.Constant) and isinstance(v.value, str)):
                out[v.value] = node
    return out


def find_page(slug: str) -> tuple[Site, ast.Dict]:
    for path in CONTENT_FILES:
        if not path.exists():
            continue
        site = _load(path)
        pages = _page_dicts(site)
        if slug in pages:
            return site, pages[slug]
    raise PatchError(f"No page declares slug '{slug}'.")


def _key_node(d: ast.Dict, key: str) -> tuple[ast.Constant, ast.AST] | None:
    for k, v in zip(d.keys, d.values):
        if isinstance(k, ast.Constant) and k.value == key:
            return k, v
    return None


def walk(page: ast.Dict, path: str) -> ast.AST:
    """Resolve a dotted address to its node, or raise with the failing step."""
    node: ast.AST = page
    for step in [s for s in path.split(".") if s]:
        if step.isdigit():
            if not isinstance(node, (ast.List, ast.Tuple)):
                raise PatchError(f"'{path}': [{step}] used on a non-list.")
            items = node.elts
            i = int(step)
            if i >= len(items):
                raise PatchError(f"'{path}': index {i} is past the end.")
            node = items[i]
        else:
            if not isinstance(node, ast.Dict):
                raise PatchError(f"'{path}': .{step} used on a non-dict.")
            found = _key_node(node, step)
            if found is None:
                raise PatchError(f"'{path}': no key '{step}'.")
            node = found[1]
    return node


def walk_parent(page: ast.Dict, path: str) -> tuple[ast.AST, str]:
    """The container of an address plus the final step — lets us create keys."""
    steps = [s for s in path.split(".") if s]
    if not steps:
        raise PatchError("Empty address.")
    parent = page if len(steps) == 1 else walk(page, ".".join(steps[:-1]))
    return parent, steps[-1]


# ── reading ──────────────────────────────────────────────────────────────────

def read(slug: str, path: str):
    """The current value at an address, as a plain Python object (or None)."""
    site, page = find_page(slug)
    try:
        node = walk(page, path)
    except PatchError:
        return None
    try:
        return ast.literal_eval(node)
    except ValueError:
        return None       # an f-string or a name reference — not a plain value


# ── writing ──────────────────────────────────────────────────────────────────

def literal(value, col: int) -> str:
    """Render a Python literal the way these files are written by hand."""
    if isinstance(value, str):
        return _format_literal(value, col)
    if isinstance(value, bool) or value is None:
        return repr(value)
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, dict):
        # try one line; otherwise one key per line, each value rendered at the
        # column it will actually occupy so long strings wrap correctly
        flat = ", ".join(f"{_quote(str(k))}: {literal(v, col + 1)}"
                         for k, v in value.items())
        if col + len(flat) + 2 <= MAX_LINE and "\n" not in flat:
            return "{" + flat + "}"
        pad = " " * (col + 1)
        rows = []
        for k, v in value.items():
            key = _quote(str(k))
            rows.append(f"{key}: {literal(v, col + 1 + len(key) + 2)}")
        return "{" + (",\n" + pad).join(rows) + "}"
    if isinstance(value, (list, tuple)):
        open_, close = ("[", "]") if isinstance(value, list) else ("(", ")")
        inner = ", ".join(literal(v, col + 1) for v in value)
        return open_ + inner + close
    raise PatchError(f"Cannot write a {type(value).__name__} into the source.")


def _splice(site: Site, start: tuple[int, int], end: tuple[int, int],
            text: str) -> str:
    """Replace an AST span (1-based line, byte column) with text."""
    lines = site.source.splitlines(keepends=True)
    i, j = start[0] - 1, end[0] - 1
    head = lines[i][:char_col(lines[i], start[1])]
    tail = lines[j][char_col(lines[j], end[1]):]
    lines[i:j + 1] = [head + text + tail]
    return "".join(lines)


def _commit(site: Site, new_source: str, expect: tuple[str, str, object] = None,
            ) -> None:
    """Write the patched source, then prove the patch did what it claimed.

    A syntax check alone is not enough: a span that swallows one character too
    many can turn `{...},\n(...)` into `{...}(...)`, which is a perfectly valid
    call expression and parses cleanly while having destroyed the next item. So
    after writing we re-read the file and confirm the address now holds exactly
    the value we asked for, restoring the original bytes if it does not.
    """
    try:
        ast.parse(new_source)
    except SyntaxError as exc:
        raise PatchError(f"Patch would break {site.file.name}: {exc}") from exc

    before = site.source
    site.file.write_text(new_source, encoding="utf-8")
    if expect is None:
        return
    slug, path, value = expect
    try:
        got = read(slug, path)
        ok = got == value
    except Exception:                                  # noqa: BLE001 — see below
        ok = False
    if not ok:
        site.file.write_text(before, encoding="utf-8")
        raise PatchError(
            f"Patch to {site.file.name} did not land cleanly and was rolled "
            f"back ({path} reads back wrong). This is a bug in the editor, not "
            "in your edit — the source is untouched.")


def set_value(slug: str, path: str, value, *, create: bool = True
              ) -> tuple[Path, int]:
    """Set an address to a value.

    `create=False` refuses to invent a key that does not already exist. Copy
    edits pass False: an address the browser sends should always name a value
    that is already there, so a typo or a hostile address must fail loudly
    rather than quietly appending `"__class__": "x"` to the page. Only the
    image endpoints create keys, and only from a known set of names.
    """
    site, page = find_page(slug)
    parent, last = walk_parent(page, path)

    if last.isdigit():                       # replacing a list element
        node = walk(page, path)
        text = literal(value, node.col_offset)
        src = _splice(site, (node.lineno, node.col_offset),
                      (node.end_lineno, node.end_col_offset), text)
        _commit(site, src, (slug, path, value))
        return site.file, node.lineno

    if not isinstance(parent, ast.Dict):
        raise PatchError(f"'{path}': cannot set a key on a non-dict.")

    existing = _key_node(parent, last)
    if existing is not None:
        _, vnode = existing
        text = literal(value, vnode.col_offset)
        src = _splice(site, (vnode.lineno, vnode.col_offset),
                      (vnode.end_lineno, vnode.end_col_offset), text)
        _commit(site, src, (slug, path, value))
        return site.file, vnode.lineno

    if not create:
        raise PatchError(
            f"'{path}' does not exist on page '{slug}', so there is nothing to "
            "edit there. (If this came from the editor, the page was probably "
            "rebuilt underneath it — reload and try again.)")

    # The key does not exist yet. Insert it after the last *short* entry rather
    # than at the very end: a page dict ends with `sections`, `faqs` and
    # `related`, which run for hundreds of lines, and burying a new "photo" key
    # below all of them puts it nowhere near the fields it belongs with.
    if parent.keys:
        col = parent.keys[0].col_offset
        pad = " " * col
        # walk the header block — the run of short values before the first
        # sprawling one — and append at its end
        tail = parent.values[-1]
        for v in parent.values:
            if v.end_lineno - v.lineno > 2:
                break
            tail = v
        head = f"{_quote(last)}: "
        text = f",\n{pad}{head}{literal(value, col + len(head))}"
        src = _splice(site, (tail.end_lineno, tail.end_col_offset),
                      (tail.end_lineno, tail.end_col_offset), text)
        line = tail.end_lineno + 1
    else:                                     # empty dict: {}
        col = parent.col_offset + 1
        head = f"{_quote(last)}: "
        text = head + literal(value, col + len(head))
        src = _splice(site, (parent.lineno, col), (parent.lineno, col), text)
        line = parent.lineno
    _commit(site, src, (slug, path, value))
    return site.file, line


def delete_key(slug: str, path: str) -> tuple[Path, int]:
    """Remove a dict key entirely (used to clear an image back to placeholder)."""
    site, page = find_page(slug)
    parent, last = walk_parent(page, path)
    if not isinstance(parent, ast.Dict):
        raise PatchError(f"'{path}': not a dict key.")
    found = _key_node(parent, last)
    if found is None:
        return site.file, parent.lineno            # already absent
    knode, vnode = found
    src_lines = site.source.splitlines(keepends=True)
    # swallow the trailing comma and any whitespace up to the next token so the
    # dict does not end up with a stray ", ,"
    tail_line, tail_col = vnode.end_lineno - 1, vnode.end_col_offset
    rest = src_lines[tail_line][tail_col:]
    eaten = 0
    for ch in rest:
        if ch == ",":
            eaten += 1
            break
        if ch in " \t":
            eaten += 1
        else:
            break
    end = (tail_line + 1, tail_col + eaten)
    # and any now-blank remainder of the line
    if src_lines[tail_line][tail_col + eaten:].strip() == "":
        end = (tail_line + 1, len(src_lines[tail_line].rstrip("\r\n")))
        start = (knode.lineno, 0)
        if src_lines[knode.lineno - 1][:knode.col_offset].strip() == "":
            src = _splice(site, start, end, "")
            src = src.replace("\n\n\n", "\n\n")
            _commit(site, src)
            return site.file, knode.lineno
    src = _splice(site, (knode.lineno, knode.col_offset), end, "")
    _commit(site, src)
    return site.file, knode.lineno


def read_constants(path: Path, names: list[str]) -> dict[str, object]:
    """Module-level `NAME = "value"` assignments, for the site-details form.

    A name bound to another name (`PRACTO_WM = PRACTO`) reads back as None:
    it has no string of its own to edit, and rewriting it would silently
    detach it from the constant it deliberately mirrors.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        t = node.targets[0]
        if isinstance(t, ast.Name) and t.id in names:
            try:
                out[t.id] = ast.literal_eval(node.value)
            except ValueError:
                out[t.id] = None
    return out


def _constant_node(site, name: str):
    for node in site.tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name):
            return node.value
    raise PatchError(f"{site.file.name} has no constant called {name}.")


def read_in_constant(path: Path, name: str, subpath: str):
    """A value inside a structured module constant, e.g. NAV.0.2.1.

    The nav and footer are lists of tuples in chrome.py, not page data, so
    nothing in `content/` can address them — yet they hold more links than any
    single page does. Addressing into a constant is what makes those editable
    at all.
    """
    site = _load(path)
    try:
        return ast.literal_eval(walk(_constant_node(site, name), subpath))
    except (PatchError, ValueError):
        return None


def set_in_constant(path: Path, name: str, subpath: str, value) -> int:
    site = _load(path)
    node = walk(_constant_node(site, name), subpath)
    text = literal(value, node.col_offset)
    src = _splice(site, (node.lineno, node.col_offset),
                  (node.end_lineno, node.end_col_offset), text)
    _commit(site, src)
    # `_commit`'s address-based read-back only understands page addresses, so
    # verify this one the same way by hand — the byte-offset trap that check
    # exists to catch applies equally here.
    if read_in_constant(path, name, subpath) != value:
        site.file.write_text(site.source, encoding="utf-8")
        raise PatchError(
            f"{name}.{subpath} did not write back cleanly; rolled back.")
    return node.lineno


def set_constant(path: Path, name: str, value: str) -> int:
    """Rewrite one module-level string constant. Re-parses, so it is safe to
    call in a loop even though every write shifts the lines below it."""
    site = _load(path)
    for node in site.tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        t = node.targets[0]
        if not (isinstance(t, ast.Name) and t.id == name):
            continue
        try:
            ast.literal_eval(node.value)
        except ValueError:
            raise PatchError(
                f"{name} mirrors another constant rather than holding its own "
                f"value. Edit the constant it points at, or set it in "
                f"{path.name} directly.") from None
        col = char_col(site.source.splitlines()[node.value.lineno - 1],
                       node.value.col_offset)
        text = _format_literal(value, col)
        src = _splice(site, (node.value.lineno, node.value.col_offset),
                      (node.value.end_lineno, node.value.end_col_offset), text)
        _commit(site, src)
        if read_constants(path, [name]).get(name) != value:
            site.file.write_text(site.source, encoding="utf-8")
            raise PatchError(f"{name} did not write back cleanly; rolled back.")
        return node.value.lineno
    raise PatchError(f"{path.name} has no constant called {name}.")


# ── list surgery: reorder and remove sections ────────────────────────────────
# Open Design left move/duplicate out of its editor because its target is an
# HTML file, where "move a section" means re-serializing the DOM. Here a section
# is an element of a Python list, so the operation is exact and reviewable.

def _element_spans(site: Site, lst: ast.List) -> list[tuple[int, int]]:
    """Character offsets covering each element, comma and trailing comment."""
    text = site.source
    starts = [_offset(text, el.lineno, el.col_offset) for el in lst.elts]
    ends = [starts[n + 1] if n + 1 < len(starts)
            else _offset(text, lst.end_lineno, lst.end_col_offset) - 1
            for n in range(len(lst.elts))]
    return list(zip(starts, ends))


def _offset(text: str, line: int, col: int) -> int:
    """Absolute character index of an AST (line, byte column) position."""
    lines = text.splitlines(keepends=True)
    return sum(len(x) for x in lines[:line - 1]) + char_col(lines[line - 1], col)


def _verify_len(slug: str, list_path: str, expected: int, site: Site,
                before: str) -> None:
    """Confirm a list op produced the expected element count, else roll back.

    The failure this guards against is a span that eats a separating comma:
    two adjacent items merge into one expression, the file still parses, and a
    whole section disappears from the page without any error.
    """
    site2, page2 = find_page(slug)
    lst = walk(page2, list_path)
    if not isinstance(lst, ast.List) or len(lst.elts) != expected:
        site.file.write_text(before, encoding="utf-8")
        raise PatchError(
            f"That change did not apply cleanly and was rolled back "
            f"({list_path} would have held "
            f"{len(getattr(lst, 'elts', []))} items, expected {expected}).")


def reorder(slug: str, list_path: str, index: int, delta: int) -> tuple[Path, int]:
    """Swap a list element with its neighbour."""
    site, page = find_page(slug)
    lst = walk(page, list_path)
    if not isinstance(lst, ast.List):
        raise PatchError(f"'{list_path}' is not a list.")
    other = index + delta
    if not (0 <= index < len(lst.elts)) or not (0 <= other < len(lst.elts)):
        raise PatchError("That section is already at the end of the page.")

    spans = _element_spans(site, lst)
    text = site.source
    chunks = [text[a:b] for a, b in spans]
    chunks[index], chunks[other] = chunks[other], chunks[index]
    body = "".join(chunks)
    new = text[:spans[0][0]] + body + text[spans[-1][1]:]
    n = len(lst.elts)
    line = lst.elts[min(index, other)].lineno
    _commit(site, new)
    _verify_len(slug, list_path, n, site, text)
    return site.file, line


def remove(slug: str, list_path: str, index: int) -> tuple[Path, int]:
    """Delete a list element (a whole section, or one card inside one)."""
    site, page = find_page(slug)
    lst = walk(page, list_path)
    if not isinstance(lst, ast.List):
        raise PatchError(f"'{list_path}' is not a list.")
    if len(lst.elts) <= 1:
        raise PatchError("That is the last item — deleting it would leave the "
                         "page with an empty section. Remove the section instead.")
    spans = _element_spans(site, lst)
    text = site.source
    chunks = [text[a:b] for i, (a, b) in enumerate(spans) if i != index]
    new = text[:spans[0][0]] + "".join(chunks) + text[spans[-1][1]:]
    n, line = len(lst.elts), lst.elts[index].lineno
    _commit(site, new)
    _verify_len(slug, list_path, n - 1, site, text)
    return site.file, line


def duplicate(slug: str, list_path: str, index: int) -> tuple[Path, int]:
    """Copy a list element in place — the fastest way to add another card."""
    site, page = find_page(slug)
    lst = walk(page, list_path)
    if not isinstance(lst, ast.List):
        raise PatchError(f"'{list_path}' is not a list.")
    spans = _element_spans(site, lst)
    text = site.source
    a, b = spans[index]
    chunk = text[a:b]
    if not chunk.rstrip().endswith(","):
        chunk = chunk.rstrip() + ",\n"
    new = text[:b] + chunk + text[b:]
    n, line = len(lst.elts), lst.elts[index].lineno
    _commit(site, new)
    _verify_len(slug, list_path, n + 1, site, text)
    return site.file, line


if __name__ == "__main__":            # sanity CLI: read an address
    import sys
    if len(sys.argv) >= 3:
        print(repr(read(sys.argv[1], sys.argv[2])))
