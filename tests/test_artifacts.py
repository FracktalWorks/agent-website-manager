"""What a project contains, and how it is grouped for the workspace.

`artifacts.py` decides three things the hub then just renders: which files
count as artefacts at all, how 61 pages nest, and which artefacts belong
together. Each test below is a way one of those has been got wrong.

Runs from a cold checkout in well under a second — no server, no network, and
no dependency on `outputs/` holding any particular site.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import artifacts                                    # noqa: E402


# ── the sitemap ──────────────────────────────────────────────────────────────
def page(url: str, module: str = "content/a.py", **kw) -> dict:
    slug = url.strip("/").replace("/", "-") or "index"
    return {"slug": slug, "url": url, "title": slug, "file": slug + ".html",
            "template": "T2", "module": module, **kw}


def test_tree_nests_by_url_not_by_slug():
    """`/vitiligo/cost/` is a child of `/vitiligo/` even though its slug,
    `vitiligo-cost`, sorts next to it in a flat list and says nothing."""
    roots = artifacts.tree([page("/vitiligo/"), page("/vitiligo/cost/"),
                            page("/psoriasis/")])
    assert [r["url"] for r in roots] == ["/psoriasis/", "/vitiligo/"]
    kids = {r["url"]: [k["url"] for k in r["kids"]] for r in roots}
    assert kids["/vitiligo/"] == ["/vitiligo/cost/"]


def test_missing_level_becomes_a_visible_stub():
    """There is no `/about/` page, and flattening `/about/x/` up to the root
    would hide that. The level stays, marked as having no page of its own."""
    roots = artifacts.tree([page("/about/dr-varada/")])
    assert len(roots) == 1
    assert roots[0]["url"] == "/about/" and roots[0]["stub"] is True
    assert roots[0]["kids"][0]["url"] == "/about/dr-varada/"


def test_home_parents_the_site():
    roots = artifacts.tree([page("/"), page("/contact/")])
    assert [r["url"] for r in roots] == ["/"]
    assert [k["url"] for k in roots[0]["kids"]] == ["/contact/"]


# ── the authoring sections ───────────────────────────────────────────────────
def test_sections_group_by_module():
    secs = artifacts.sections([page("/a/", "content/one.py"),
                               page("/b/", "content/one.py"),
                               page("/c/", "content/two.py")])
    assert [(s["label"], s["count"]) for s in secs] == [("One", 2), ("Two", 1)]


def test_a_child_follows_its_parent_into_the_parent_section():
    """A cluster page authored in another module must not be torn out of its
    own sitemap — a section that shows `/vitiligo/` without `/vitiligo/cost/`
    is a section that lies about the site."""
    secs = artifacts.sections([page("/vitiligo/", "content/vitiligo.py"),
                               page("/vitiligo/cost/", "content/money.py")])
    assert len(secs) == 1
    assert secs[0]["label"] == "Vitiligo"
    assert [k["url"] for k in secs[0]["tree"][0]["kids"]] == ["/vitiligo/cost/"]


def test_home_does_not_swallow_every_other_section():
    """`/` parents everything. Rooting its section's tree at `/` would pull
    all 61 pages under one row and leave the other sections empty."""
    secs = {s["label"]: s for s in artifacts.sections(
        [page("/", "content/brand.py"), page("/contact/", "content/brand.py"),
         page("/vitiligo/", "content/vitiligo.py")])}
    assert [n["url"] for n in secs["Brand"]["tree"]] == ["/", "/contact/"]
    assert secs["Vitiligo"]["count"] == 1


# ── what is not an artefact ──────────────────────────────────────────────────
@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A brand with a print run, a logo set and a directory of scratch."""
    for rel in ("print/out/card.pdf", "print/out/card-proof.png",
                "print/out/flier-acne-en-proof.png",
                "print/out/flier-acne-te-proof.png",
                "print/out/_flier-acne-en-proof.html",
                "brand/logo-mark-light.svg", "brand/icons/favicon-32.png",
                "brand/tools/_work/png/favicon-32.png",
                "brand/__pycache__/x.png"):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"x")
    return tmp_path


def test_working_files_are_not_artefacts(project: Path):
    """`brand/tools/_work/` is what a script wrote on its way to the icons.
    Showing it does not make the gallery more complete, only less true."""
    brand = next(k for k in artifacts.kinds(project) if k["id"] == "brand")
    rels = [i["rel"] for i in brand["items"]]
    assert rels == ["brand/icons/favicon-32.png", "brand/logo-mark-light.svg"]


def test_gallery_groups_by_folder_and_ids_survive_as_anchors(project: Path):
    brand = next(k for k in artifacts.kinds(project) if k["id"] == "brand")
    groups = {g["id"]: g for g in brand["groups"]}
    # Loose files group under "" on disk but must have an id an href can use.
    assert set(groups) == {"root", "icons"}
    assert groups["root"]["label"] == "Marks"
    assert groups["icons"]["label"] == "Icons & favicons"


# ── the press run ────────────────────────────────────────────────────────────
def test_proof_and_pdf_are_one_artefact(project: Path):
    """Two tiles for `card.pdf` and `card-proof.png` is how a proof reaches a
    printer. `ready` is False for a family with no PDF — an open sign-off."""
    press = next(k for k in artifacts.kinds(project) if k["id"] == "print")
    by_name = {i["name"]: i for i in press["items"]}
    assert set(by_name) == {"card", "flier-acne-en", "flier-acne-te"}
    assert by_name["card"]["ready"] and by_name["card"]["pdf"]
    assert not by_name["flier-acne-en"]["ready"]
    assert press["note"] == "1/3 press-ready"


def test_press_families_carry_the_language_apart():
    """Twelve fliers are four subjects in three languages. The English one
    being signed off says nothing about the Telugu one."""
    fam, subject, lang = artifacts._split_press("flier-hair-loss-te")
    assert (fam, subject, lang) == ("flier", "hair loss", "te")
    assert artifacts._split_press("card") == ("card", "", "")


def test_families_lead_with_what_is_not_signed_off(project: Path):
    press = next(k for k in artifacts.kinds(project) if k["id"] == "print")
    assert [g["label"] for g in press["groups"]] == ["Fliers", "Business card"]


def test_png_size_reads_the_header(tmp_path: Path):
    """Proof shape drives the card shape; a wrong read letterboxes every
    artefact into the same stamp."""
    png = tmp_path / "p.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 8
                    + (1400).to_bytes(4, "big") + (3981).to_bytes(4, "big"))
    assert artifacts.png_size(png) == (1400, 3981)
    (tmp_path / "q.png").write_bytes(b"not a png")
    assert artifacts.png_size(tmp_path / "q.png") == (0, 0)
    assert artifacts.png_size(tmp_path / "gone.png") == (0, 0)


def test_a_page_always_names_a_file_to_open(tmp_path: Path):
    """`file` is what the hub points its preview iframe at.

    A manifest that omits it — fracktal's did — used to yield "", and the hub
    navigated to the server root instead: a directory listing on load, a 404
    once the editor resolved `/` to a missing index.html. Neither of those
    reads as "that field is absent", which is why it survived a look at the
    screen. Derive it instead; every site engine writes flat `<slug>.html`.
    """
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "site-manifest.json").write_text(json.dumps({
        "pages": [{"slug": "index", "url": "/", "title": "Home"},
                  {"slug": "cf-nylon", "url": "/cf-nylon/", "title": "CF-PA"},
                  {"slug": "pla", "url": "/pla-polylactic-acid/",
                   "title": "PLA", "file": "pla.html"}],
    }), encoding="utf-8")
    got = {p["slug"]: p["file"] for p in artifacts.pages_of(tmp_path)}
    assert got == {"index": "index.html", "cf-nylon": "cf-nylon.html",
                   "pla": "pla.html"}
    # And the URL is left alone: `/pla-polylactic-acid/` is where the page
    # lives on the live site, which is not the file the build wrote.
    assert [p["url"] for p in artifacts.pages_of(tmp_path)][2] \
        == "/pla-polylactic-acid/"


def test_the_websites_own_images_are_artefacts(tmp_path: Path):
    """The art a site is built from is the largest artefact set it owns.

    It used to be the one you could not see: `KINDS` listed the website's
    PAGES and the brand directory, so a project reported 61 pages and 108
    brand assets while 75 illustrations, case photos and emblems — the things
    those pages are actually made of — appeared nowhere.

    The root is the SOURCE tree. `dist/` and `dist-prod/` hold a copy of every
    one of them, and counting a build output would treble the number.
    """
    for rel in ("site/assets/img/hero.webp",
                "site/assets/img/diagrams/vitiligo.png",
                "site/assets/img/cases/before-1.jpg",
                "site/dist/assets/img/hero.webp",
                "site/dist-prod/assets/img/diagrams/vitiligo.png",
                # Working state, by both markers.
                "site/.diagram-queue/take-3.png",
                "site/assets/img/_scratch/reject.png"):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"x")
    media = next(k for k in artifacts.kinds(tmp_path) if k["id"] == "media")
    assert media["count"] == 3
    assert [i["rel"] for i in media["items"]] == [
        "site/assets/img/cases/before-1.jpg",
        "site/assets/img/diagrams/vitiligo.png",
        "site/assets/img/hero.webp"]
    # Grouped by the folders already on disk, with the headings this kind
    # uses — NOT the brand directory's, whose root group is "Marks".
    assert {g["label"]: g["count"] for g in media["groups"]} == {
        "Loose art": 1, "Medical illustrations": 1, "Before & after": 1}


def test_a_gallery_kind_with_no_labels_still_reads(tmp_path: Path):
    """`{}` is a real answer: title-case the folder and carry on."""
    got = artifacts._gallery(
        [{"rel": "x/product-renders/a.png"}, {"rel": "x/b.png"}], "x", {})
    assert [(g["id"], g["label"]) for g in got] == [
        ("root", "Loose files"), ("product-renders", "Product renders")]


# ── design concepts ──────────────────────────────────────────────────────────
def concept_round(tmp_path: Path) -> Path:
    """Two directions: one with a NOTES.md title, one bare."""
    croot = tmp_path / "concepts"
    for rel, text in (("calm/index.html", "<h1>calm</h1>"),
                      ("calm/NOTES.md", "# Calm Editorial\n\n**Dials:** 5/3/3"),
                      ("bold-dark/index.html", "<h1>bold</h1>")):
        f = croot / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    return croot


def test_concepts_read_their_titles_and_wait_for_a_decision(tmp_path: Path):
    """A direction is named by its NOTES.md heading, not its folder slug, and
    an undecided round says so instead of pretending to be done."""
    concept_round(tmp_path)
    kind = next(k for k in artifacts.kinds(tmp_path) if k["id"] == "concepts")
    assert kind["kind"] == "concepts" and kind["count"] == 2
    assert kind["note"] == "2 directions, no decision yet"
    by_slug = {i["slug"]: i for i in kind["items"]}
    assert by_slug["calm"]["title"] == "Calm Editorial"
    assert by_slug["bold-dark"]["title"] == "Bold Dark"
    assert not any(i["chosen"] for i in kind["items"])
    assert kind["compare"] is None


def test_a_decision_marks_the_chosen_direction(tmp_path: Path):
    """DECISION.md names the winner; the note and the item both carry it, and
    a generated compare page is surfaced for the hub to frame."""
    croot = concept_round(tmp_path)
    (croot / "DECISION.md").write_text(
        "# Decision\n\n**Chosen:** `bold-dark`\n", encoding="utf-8")
    (croot / "compare.html").write_text("<html>", encoding="utf-8")
    kind = next(k for k in artifacts.kinds(tmp_path) if k["id"] == "concepts")
    assert kind["note"] == "direction chosen: bold-dark"
    assert {i["slug"]: i["chosen"] for i in kind["items"]} == {
        "calm": False, "bold-dark": True}
    assert kind["compare"] == "concepts/compare.html"


def test_scaffolding_and_empty_rounds_are_not_concepts(tmp_path: Path):
    """A `_wip` draft is working state, a folder without an index.html is not
    a direction, and a concepts dir with neither yields no kind at all."""
    croot = tmp_path / "concepts"
    (croot / "_wip").mkdir(parents=True)
    (croot / "_wip" / "index.html").write_text("x", encoding="utf-8")
    (croot / "no-mockup-yet").mkdir()
    assert not any(k["id"] == "concepts" for k in artifacts.kinds(tmp_path))
