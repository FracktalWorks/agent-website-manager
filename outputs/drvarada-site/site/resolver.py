"""Map text seen in a rendered page back to the Python string literal it came from.

The live editor's whole trick lives here. Pages are generated — content strings sit
in ``content/*.py`` and ``chrome.py`` — so when someone edits a headline in the
browser, we must find the *source literal* that produced it and rewrite that.

Plain substring search fails immediately: the content files wrap long copy as
implicit concatenations across lines ("abc "\n"def"), so the rendered string never
appears verbatim in the file. The AST solves this: Python folds an implicit
concatenation into ONE ``ast.Constant`` whose value is the joined string and whose
span covers every fragment. Matching against node *values* and rewriting node
*spans* handles any wrapping style without caring how the author formatted it.

Matching rules:
- The browser sends both ``innerHTML`` (entities intact: ``&amp;``, ``<em>``) and
  ``textContent`` (decoded). Source literals authored with markup match the first;
  literals escaped at render time by ``chrome.e()`` match the second. Whichever
  variant matches decides which new value gets written back.
- Docstrings, dict keys, and fragments inside f-strings are never candidates — an
  edit that lands in an f-string is template surgery, not a copy change, and is
  refused with a pointer to the file instead.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
# urls.py is deliberately absent: its strings are slugs and URL paths, and a copy
# edit must never rewrite the information architecture by accident.
# Derived from siteconf, not listed again. This was the fourth copy of the same
# module list, and the one that failed most obscurely: a page whose module was
# missing here produced "No page declares slug 'index'" — a message that sounds
# like the page is wrong rather than the search path.
import siteconf                                    # noqa: E402

SEARCH_FILES = [ROOT / "content" / f"{name}.py" for name in siteconf.MODULES]
SEARCH_FILES.append(ROOT / "chrome.py")

MAX_LINE = 96  # wrap rewritten literals so files stay diffable


def char_col(line: str, byte_col: int) -> int:
    """Convert an AST column to a string index.

    `ast` reports `col_offset` as an offset in UTF-8 **bytes**, while Python
    string slicing counts characters. Every line of this site's copy is full of
    em dashes and ·, each three bytes and one character, so using the raw
    column silently slices several characters too far — which corrupts the file
    in a way that can still parse (a dict followed by a tuple reads as a call).
    Every span used for slicing must come through here.
    """
    return len(line.encode("utf-8")[:byte_col].decode("utf-8", "ignore"))


@dataclass
class Match:
    file: Path
    lineno: int          # 1-based, start of the literal
    col: int             # 0-based column of the opening quote
    end_lineno: int
    end_col: int
    value: str           # the matched source string
    variant: str         # "html" or "text" — which browser form matched


def _excluded(tree: ast.Module) -> set[int]:
    """ids of Constant nodes that must never be edit targets."""
    out: set[int] = set()
    for node in ast.walk(tree):
        # docstrings: first statement of a module / def / class
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and \
                    isinstance(body[0].value, ast.Constant):
                out.add(id(body[0].value))
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant):
                    out.add(id(k))
        if isinstance(node, ast.JoinedStr):
            for child in ast.walk(node):
                if isinstance(child, ast.Constant):
                    out.add(id(child))
    return out


def find(old_html: str, old_text: str) -> list[Match]:
    """Every string literal across the site source that equals the edited node.

    Two tiers: exact equality wins; only if nothing matches exactly do we fall
    back to whitespace-trimmed equality (renderers sometimes pad, and authors
    sometimes leave a trailing space on a concatenation fragment).
    """
    variants = [("html", old_html)]
    if old_text != old_html:
        variants.append(("text", old_text))

    exact: list[Match] = []
    loose: list[Match] = []
    for path in SEARCH_FILES:
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        skip = _excluded(tree)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            if id(node) in skip or not node.value.strip():
                continue
            for name, wanted in variants:
                m = Match(file=path, lineno=node.lineno, col=node.col_offset,
                          end_lineno=node.end_lineno, end_col=node.end_col_offset,
                          value=node.value, variant=name)
                if node.value == wanted:
                    exact.append(m)
                    break
                if node.value.strip() == wanted.strip():
                    loose.append(m)
                    break
    return exact or loose


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _format_literal(value: str, col: int) -> str:
    """A double-quoted literal, wrapped as implicit concatenation past MAX_LINE.

    Continuation fragments align under the opening quote, matching how the
    content files are written by hand, and every fragment keeps its trailing
    space so the joined value is byte-identical to ``value``.
    """
    whole = _quote(value)
    if col + len(whole) <= MAX_LINE:
        return whole

    budget = MAX_LINE - col - 2          # room between the quotes on each line
    words = value.split(" ")
    frags: list[str] = []
    cur = ""
    for w in words:
        piece = w if not cur else " " + w
        if cur and len(cur) + len(piece) > budget:
            frags.append(cur + " ")      # trailing space carries the join
            cur = w
        else:
            cur += piece
    if cur:
        frags.append(cur)
    indent = "\n" + " " * col
    return indent.join(_quote(f) for f in frags)


def apply(match: Match, new_value: str) -> None:
    """Rewrite the matched literal's span in place with ``new_value``."""
    lines = match.file.read_text(encoding="utf-8").splitlines(keepends=True)
    i, j = match.lineno - 1, match.end_lineno - 1
    start = char_col(lines[i], match.col)
    end = char_col(lines[j], match.end_col)
    head, tail = lines[i][:start], lines[j][end:]
    lines[i:j + 1] = [head + _format_literal(new_value, start) + tail]
    match.file.write_text("".join(lines), encoding="utf-8")


def resolve_new_value(match: Match, new_html: str, new_text: str) -> str:
    """Pick the write-back form matching how the source literal was authored."""
    return new_html if match.variant == "html" else new_text


if __name__ == "__main__":                       # tiny CLI for sanity checks
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Three practices, one dermatologist."
    for m in find(q, q):
        rel = m.file.relative_to(ROOT)
        print(f"{rel}:{m.lineno}:{m.col}  [{m.variant}]  {m.value[:60]!r}")
