"""The project notebook: discovery, the scratchpad round-trip, and the renderer.

The renderer tests are mostly regressions. Two bugs shipped to the screen
before they were caught by LOOKING at the page, and both had the same shape:
the preview said something the document did not.

  * a four-item numbered list whose items wrapped rendered as four separate
    lists, each restarting at 1, with every wrapped line adrift between them
  * `_emphasis_` rendered as literal underscores

Neither raised anything. Both are pinned here.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import notebook                                            # noqa: E402


# ------------------------------------------------------------------ renderer

def test_wrapped_numbered_list_stays_one_list():
    md = ("1. **First.** this one wraps\n"
          "   onto a second line.\n"
          "2. **Second.** and so\n"
          "   does this one.\n"
          "3. **Third.**\n")
    h = notebook.render(md)
    assert h.count("<ol>") == 1, "each wrap started a new list, restarting at 1"
    assert h.count("<li>") == 3
    assert "onto a second line." in h
    # the continuation must be INSIDE the item, not a sibling paragraph
    assert "<p>onto a second line." not in h


def test_blank_line_between_items_keeps_one_list():
    md = "- one\n\n- two\n\n- three\n"
    h = notebook.render(md)
    assert h.count("<ul>") == 1
    assert h.count("<li>") == 3


def test_paragraph_after_a_list_is_not_swallowed():
    md = "- one\n- two\n\nA new paragraph entirely.\n"
    h = notebook.render(md)
    assert "</ul>" in h
    assert "<p>A new paragraph entirely.</p>" in h


def test_underscore_emphasis_renders():
    assert "<em>like this</em>" in notebook.render("_like this_\n")


def test_underscores_inside_words_are_left_alone():
    """`wp_head` and `tax_rate_compound` are not emphasis."""
    h = notebook.render("Set `wp_head` and tax_rate_compound and snake_case.\n")
    assert "<em>" not in h
    assert "tax_rate_compound" in h


def test_code_span_protects_its_contents():
    h = notebook.render("Use `**kwargs` and `_x_` carefully.\n")
    assert "<strong>" not in h
    assert "<em>" not in h
    assert "<code>**kwargs</code>" in h


def test_table_renders_with_header_and_scroll_box():
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    h = notebook.render(md)
    assert "<table>" in h and "<th>A</th>" in h and "<td>2</td>" in h
    assert 'class="tw"' in h, "wide tables must scroll in their own box"


def test_fenced_code_is_verbatim_and_escaped():
    h = notebook.render("```python\nif a < b and c:\n    pass\n```\n")
    assert "&lt; b" in h
    assert "<pre>" in h and 'class="lang-python"' in h
    assert "<em>" not in h


def test_html_in_the_source_is_escaped_not_executed():
    h = notebook.render("A <script>alert(1)</script> line.\n")
    assert "<script>" not in h
    assert "&lt;script&gt;" in h


def test_headings_and_rules():
    h = notebook.render("# One\n\n## Two\n\n---\n\n### Three\n")
    assert "<h1>One</h1>" in h and "<h2>Two</h2>" in h
    assert "<h3>Three</h3>" in h and "<hr>" in h


def test_links_and_bare_urls():
    h = notebook.render("See [the plan](PLAN.md) and https://fracktal.in/shop/\n")
    assert 'href="PLAN.md"' in h
    assert 'href="https://fracktal.in/shop/"' in h


def test_nothing_in_the_source_silently_vanishes():
    """The renderer may not understand a construct; it may not lose it."""
    md = "Some ~~strike~~ and a footnote[^1] and :emoji: text.\n"
    h = notebook.render(md)
    for fragment in ("strike", "footnote", "emoji"):
        assert fragment in h


# ----------------------------------------------------------------- discovery

def test_docs_finds_markdown_and_puts_the_scratchpad_first(tmp_path):
    (tmp_path / "PLAN.md").write_text("# A plan\n\nBody.\n", encoding="utf-8")
    (tmp_path / "NOTES.md").write_text("# Notes\n\nWhere we left off.\n",
                                       encoding="utf-8")
    found = notebook.docs(tmp_path)
    assert [d["name"] for d in found][0] == "NOTES.md"
    assert found[0]["scratch"] is True
    assert {d["name"] for d in found} == {"NOTES.md", "PLAN.md"}
    assert found[1]["title"] == "A plan", "title comes from the document's H1"


def test_docs_skips_scaffolding(tmp_path):
    (tmp_path / "_draft.md").write_text("# Draft\n", encoding="utf-8")
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "_wip.md").write_text("# WIP\n", encoding="utf-8")
    (tmp_path / "notes" / "real.md").write_text("# Real\n", encoding="utf-8")
    assert [d["name"] for d in notebook.docs(tmp_path)] == ["real.md"]


def test_kind_exists_even_with_nothing_written(tmp_path):
    """A notebook that only appears once you have notes is one nobody starts."""
    k = notebook.kind(tmp_path)
    assert k is not None and k["id"] == "notes"
    assert k["count"] == 0
    assert "no notes yet" in k["note"]


def test_scratch_round_trip_and_line_endings(tmp_path):
    notebook.write_scratch(tmp_path, "# Notes\r\n\r\nWindows typed this.\r\n")
    raw = notebook.scratch_path(tmp_path).read_text(encoding="utf-8")
    assert "\r" not in raw, "CRLF would make this file diff badly forever"
    assert notebook.read_scratch(tmp_path).endswith("Windows typed this.\n")


def test_scratch_gets_a_trailing_newline(tmp_path):
    notebook.write_scratch(tmp_path, "no newline at the end")
    assert notebook.read_scratch(tmp_path).endswith("\n")


def test_real_project_docs_render_without_leaking_markdown():
    """The documents this was built for, rendered whole.

    A leak here means somebody reads a plan in the hub and sees `**` and
    `| --- |` instead of a table — the preview misrepresenting the document.
    """
    import re
    root = pathlib.Path(__file__).resolve().parents[1] / "outputs"
    md_files = sorted(root.glob("*/[A-Z]*.md"))[:8]
    if not md_files:
        return
    for f in md_files:
        h = notebook.render(f.read_text(encoding="utf-8", errors="replace"))
        body = re.sub(r"<pre><code.*?</code></pre>", "", h, flags=re.S)
        body = re.sub(r"<code>.*?</code>", "", body, flags=re.S)
        assert not re.search(r"^\s*#{1,6}\s", body, re.M), f"{f.name}: heading"
        assert "```" not in body, f"{f.name}: code fence leaked"
        assert not re.search(r"^\s*\|", body, re.M), f"{f.name}: table row"
