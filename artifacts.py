"""What a project contains, beyond its website.

A project in `outputs/` started as one thing — a site — and the hub's model
said so: `discover_projects()` looks for `*/site/build.py` and calls what it
finds a project. That was true until the same brand grew a logo system, a
signboard, WhatsApp tiles, a business card and twelve fliers, none of which
have a URL and none of which the workspace could see.

So a project is a brand, and a brand holds ARTEFACT KINDS. Each kind is a
directory with a known shape:

    <project>/site/        the website          → pages, arranged as a sitemap
    <project>/print/out/   press collateral     → PDFs and proofs
    <project>/brand/       identity assets      → lockups, icons, platform art
    <project>/signage/out/ fabrication          → the board

Kinds are discovered, never declared. A project that has no `print/` simply
does not show that kind, and a project that grows one shows it the next time
the page is loaded — because the alternative is a manifest that has to be
edited by hand every time a file is added, which is a manifest that is wrong.

THE SITEMAP IS THE POINT
    A flat list of 61 pages says nothing about a site. The same 61 arranged by
    URL depth show that vitiligo has eight children and psoriasis seven, that
    the Telugu and Hindi pages are a two-page stub each, and that a page like
    `travelling-for-treatment` is sitting at the root with no parent. That is
    the view a site is actually edited from, so `tree()` builds it from the
    URLs themselves rather than from anybody's idea of the hierarchy.

    URL depth is not the only true axis, though. `/vitiligo-treatment-
    hyderabad/` and `/acne-treatment-hyderabad/` are both root-level and so
    both sit flat in the sitemap, but they were authored side by side in
    `content/hyderabad_medical.py` and they are edited side by side too.
    `sections()` groups by that authoring module, so the sidebar can offer
    both readings of the same 61 pages instead of picking one.

AND SO IS WHAT IS *NOT* AN ARTEFACT
    `brand/tools/_work/` holds sixteen PNGs that a script wrote on its way to
    the real icons — the same favicons again, plus a floor plate for a lockup
    render. Showing them next to the finished marks does not make the gallery
    more complete, it makes it 17 tiles less trustworthy. The repo already
    marks working files with a leading underscore (`_card.html`, `_wrap.html`),
    so that convention is the filter: an underscore anywhere in the path means
    the file is scaffolding, not something the brand owns.
"""

from __future__ import annotations

import csv
import json
import pathlib
import re

IMAGE = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico"}
DOC = {".pdf"}
SKIP_DIRS = {"__pycache__", "node_modules", ".git"}


# --------------------------------------------------------------- the sitemap

def tree(pages: list[dict]) -> list[dict]:
    """Nest pages by URL path. Returns roots, each with `kids`.

    A page whose parent URL is not itself a page still nests correctly: the
    missing level becomes a labelled stub rather than being flattened away,
    because "there is no /locations/ page" is information about the site, not
    a reason to lie about the shape.
    """
    by_url: dict[str, dict] = {}
    for p in pages:
        url = (p.get("url") or "/" + (p.get("slug") or "")).rstrip("/") + "/"
        by_url[url] = {**p, "url": url, "kids": [], "stub": False,
                       "depth": url.strip("/").count("/") + (url != "/")}
    # Insert stubs for any missing intermediate level, deepest first so that
    # a two-level gap resolves in one pass.
    for url in sorted(by_url, key=lambda u: -u.count("/")):
        parts = url.strip("/").split("/")
        for i in range(1, len(parts)):
            parent = "/" + "/".join(parts[:i]) + "/"
            if parent not in by_url:
                by_url[parent] = {"url": parent, "slug": "", "kids": [],
                                  "title": parts[i - 1].replace("-", " "),
                                  "stub": True, "depth": i}
    roots: list[dict] = []
    for url, node in sorted(by_url.items()):
        parts = url.strip("/").split("/")
        parent = "/" + "/".join(parts[:-1]) + "/" if len(parts) > 1 else "/"
        if url == "/":
            roots.insert(0, node)
        elif parent in by_url and parent != url:
            by_url[parent]["kids"].append(node)
        else:
            roots.append(node)
    return roots


def flatten(nodes: list[dict], out: list[dict] | None = None) -> list[dict]:
    """Depth-first, for rendering an indented list."""
    out = [] if out is None else out
    for n in nodes:
        out.append(n)
        flatten(n["kids"], out)
    return out


def sections(pages: list[dict]) -> list[dict]:
    """Group pages by the module that authored them, each nested as a sitemap.

    A page belongs to exactly one section, and a child follows its parent into
    the parent's section even when the two were authored apart — a sitemap
    that splits `/vitiligo/cost/` away from `/vitiligo/` is not a sitemap.
    """
    home = {p.get("url"): p for p in pages}.get("/")
    owner: dict[str, str] = {}
    for p in sorted(pages, key=lambda p: len(p.get("url") or "")):
        url = (p.get("url") or "").rstrip("/") + "/"
        parent = "/" + "/".join(url.strip("/").split("/")[:-1]) + "/"
        owner[url] = (owner.get(parent) if parent != url and parent in owner
                      else p.get("module") or "")
    groups: dict[str, list[dict]] = {}
    for p in pages:
        url = (p.get("url") or "").rstrip("/") + "/"
        groups.setdefault(owner.get(url, ""), []).append(p)
    out = []
    for module, group in groups.items():
        # The home page anchors the whole site; a section tree rooted at "/"
        # would swallow every other section's pages into one row.
        roots = tree([p for p in group if p is not home])
        if any(p is home for p in group):
            roots = [{**home, "kids": [], "stub": False, "depth": 0,
                      "url": "/"}] + roots
        out.append({"id": module, "label": _module_label(module),
                    "count": len(group), "tree": roots})
    out.sort(key=lambda s: (-s["count"], s["label"]))
    return out


def _module_label(module: str) -> str:
    """`content/hyderabad_skin.py` → `Hyderabad skin`."""
    stem = module.rsplit("/", 1)[-1].removesuffix(".py")
    return stem.replace("_", " ").replace("-", " ").strip().capitalize() \
        or "Ungrouped"


def _page_file(slug: str) -> str:
    """The file a build writes for a slug. `index` is the one special case."""
    return "index.html" if slug == "index" else f"{slug}.html" if slug else ""


def pages_of(site: pathlib.Path) -> list[dict]:
    """Read the build manifest. Empty if the site has never been built."""
    for name in ("dist/site-manifest.json", "dist-prod/site-manifest.json"):
        try:
            m = json.loads((site / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        # `file` is what the hub opens. A manifest that omits it used to yield
        # "", which navigates the preview iframe to the server root — a
        # directory listing, or a 404 once the editor resolves `/` to a missing
        # index.html. Neither reads as "this field is absent". Every site
        # engine writes flat `<slug>.html` files, so derive it rather than
        # handing the caller an empty string it cannot tell from a real answer.
        return [{"slug": p.get("slug", ""), "title": p.get("title", ""),
                 "url": p.get("url", ""),
                 "file": p.get("file") or _page_file(p.get("slug", "")),
                 "template": p.get("template", ""),
                 "module": p.get("module", "")}
                for p in m.get("pages", [])]
    return []


# ----------------------------------------------------------------- the kinds

def png_size(f: pathlib.Path) -> tuple[int, int]:
    """A PNG's pixel size from its IHDR, or (0, 0) for anything else.

    A business card proof is landscape, a flier is A5 portrait and a standee
    is nearly three times as tall as it is wide. Rendered into one fixed-height
    box they all become a stamp floating in white, which is the one thing a
    proof must not look like. 24 bytes of header is enough to give each card
    the shape of the thing it shows.
    """
    try:
        with f.open("rb") as fh:
            head = fh.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            return 0, 0
        return (int.from_bytes(head[16:20], "big"),
                int.from_bytes(head[20:24], "big"))
    except OSError:
        return 0, 0


def _working(rel: pathlib.PurePath) -> bool:
    """Scaffolding, not an artefact — see the module docstring.

    A leading dot counts too. `site/.diagram-queue` holds 69 candidate renders,
    review contact sheets and rejected takes — every one of them a PNG, none of
    them a thing the brand owns. Same argument as the leading underscore: the
    directory name already says it is working state.
    """
    return any(part.startswith(("_", ".")) or part in SKIP_DIRS
               for part in rel.parts)


def _items(root: pathlib.Path, base: pathlib.Path, exts: set[str],
           limit: int = 400) -> list[dict]:
    if not root.is_dir():
        return []
    out = []
    for f in sorted(root.rglob("*")):
        rel = f.relative_to(base)
        if f.is_file() and f.suffix.lower() in exts and not _working(rel):
            w, h = png_size(f)
            out.append({"name": f.name, "rel": rel.as_posix(),
                        "kb": f.stat().st_size // 1024, "w": w, "h": h,
                        "ext": f.suffix.lower().lstrip(".")})
        if len(out) >= limit:
            break
    return out


def _pair(items: list[dict]) -> list[dict]:
    """Pair a press PDF with its proof image, so one artefact is one card.

    `card.pdf` and `card-proof.png` are the same object seen twice — one to
    send, one to look at. Showing them as two tiles is how a proof ends up at
    a printer. `ready` is False when there is no PDF, which is exactly what an
    open sign-off gate leaves behind.
    """
    proofs = {i["name"][:-len("-proof.png")]: i for i in items
              if i["name"].endswith("-proof.png")}
    pdfs = {i["name"][:-4]: i for i in items if i["ext"] == "pdf"}
    # `../signage/` names its pair `fascia-proof.png` / `fascia-signage.pdf`,
    # which predates this convention. Fall back to a prefix match so the older
    # directory reads as one artefact rather than two half-empty ones.
    for stem in list(proofs):
        if stem not in pdfs:
            near = [k for k in pdfs if k.startswith(stem)]
            if len(near) == 1:
                pdfs[stem] = pdfs.pop(near[0])
    stems = sorted(set(proofs) | set(pdfs))
    out = []
    for stem in stems:
        pdf = pdfs.get(stem)
        family, subject, lang = _split_press(stem)
        proof = proofs.get(stem) or {}
        out.append({"name": stem, "proof": proof.get("rel"),
                    "pdf": (pdf or {}).get("rel"), "ready": bool(pdf),
                    "family": family, "subject": subject, "lang": lang,
                    "w": proof.get("w", 0), "h": proof.get("h", 0),
                    "kb": (pdf or proof or {}).get("kb", 0)})
    return out


LANGS = {"en": "English", "hi": "हिन्दी", "te": "తెలుగు"}
FAMILIES = {"card": "Business card", "flier": "Fliers", "leaflet": "Leaflets",
            "standee": "Standees", "fascia": "Fascia board"}


def _split_press(stem: str) -> tuple[str, str, str]:
    """`flier-hair-loss-te` → (`flier`, `hair loss`, `te`).

    Twelve fliers are four subjects in three languages, and a grid that says
    so is a different object from a grid of twelve unrelated names — the
    English one being signed off says nothing about the Telugu one.
    """
    parts = stem.split("-")
    lang = parts[-1] if len(parts) > 1 and parts[-1] in LANGS else ""
    subject = " ".join(parts[1:len(parts) - (1 if lang else 0)])
    return parts[0], subject, lang


def _families(items: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for i in items:
        groups.setdefault(i["family"], []).append(i)
    out = [{"id": fid, "label": FAMILIES.get(fid, fid.replace("-", " ").
                                             capitalize()),
            "count": len(g), "ready": sum(i["ready"] for i in g), "items": g}
           for fid, g in groups.items()]
    # Whatever is furthest from the printer first: a family with nothing signed
    # off is the one that still needs a decision.
    out.sort(key=lambda f: (f["ready"] == f["count"], f["label"]))
    return out


# Folder → heading, per gallery kind. The root group ("" — the loose files at
# the top of the directory) means something different in each: the brand
# directory's loose files are the marks, the website's are the art that is not
# in a set. Sharing one table labelled every gallery's root "Marks".
GALLERY_LABELS = {
    "brand": {"": "Marks", "icons": "Icons & favicons",
              "lockups": "Lockups", "google": "Google Business Profile",
              "whatsapp": "WhatsApp", "social": "Social",
              "badges": "Badges & app icons", "plaques": "Plaques",
              "chips": "Chips", "knockouts": "Knockouts",
              "safe": "Clear-space cuts",
              "watermarks": "Photo watermarks", "patterns": "Patterns",
              "print": "Print", "source": "Source art"},
    "media": {"": "Loose art", "diagrams": "Medical illustrations",
              "cases": "Before & after", "emblems": "Emblems",
              "placeholder": "Placeholders", "img": "Images"},
    "social": {"": "Post cards"},
}


def _gallery(items: list[dict], prefix: str,
             labels: dict[str, str] | None = None) -> list[dict]:
    """Group gallery items by folder — the grouping already on disk.

    `labels` is the folder→heading table for THIS kind; `{}` is a legitimate
    answer, meaning "no headings written down, title-case the folder name".
    A kind nobody has named folders for still reads correctly.
    """
    labels = {} if labels is None else labels
    groups: dict[str, list[dict]] = {}
    for i in items:
        rest = i["rel"][len(prefix):].lstrip("/")
        groups.setdefault(rest.split("/")[0] if "/" in rest else "",
                          []).append(i)
    order = list(labels)
    # `id` has to survive being an HTML anchor, so the loose files at the top
    # of the directory are `root` rather than the empty string they group by.
    rank = {gid: (order.index(gid) if gid in order else len(order))
            for gid in groups}
    # The root group has no folder name to title-case, so an unlabelled kind
    # would head it with the empty string — a set of files under no heading at
    # all. "Loose files" is the honest default.
    out = [{"id": gid or "root",
            "label": labels.get(gid) or (
                gid.replace("-", " ").replace("_", " ").capitalize()
                if gid else "Loose files"),
            "count": len(g), "items": g}
           for gid, g in sorted(groups.items(),
                                key=lambda kv: (rank[kv[0]], kv[0]))]
    return out


# Every kind of thing a brand owns, in the order the switcher shows them.
#
# `media` is the art the website is actually built from. It sat outside this
# table for a long while, which meant a project could show 61 pages and 108
# brand assets and not one of the 75 illustrations, case photos and emblems
# those pages are made of — the largest set of artefacts in the project was
# also the only one you could not see. The root is the SOURCE tree
# (`site/assets/img`), never `dist/`: a build copy is the same artefact again,
# and counting it would treble every number here.
#
# `documents` is the other thing a brand hands people: itineraries, price
# sheets, guides. They pair with a proof exactly like press files do, but they
# are NOT press files — no bleed, no trim, no sign-off — so calling nineteen
# emailed itineraries "3/19 press-ready" would be a category error dressed as a
# status. They get their own row and their own wording.
#
# `concepts` is what exists BEFORE the website does: a round of direction
# mockups from the design_concepting skill, kept so the record of what was
# considered and chosen stays browsable next to what got built.
KINDS = [
    ("website", "Website", "site"),
    ("concepts", "Design concepts", "concepts"),
    ("media", "Website images", "site/assets/img"),
    ("print", "Print collateral", "print/out"),
    ("documents", "Documents", "documents/out"),
    ("social", "Social posts", "posts/out"),
    ("brand", "Brand assets", "brand"),
    ("signage", "Signage", "signage/out"),
]

# Kinds whose artefacts are a file-plus-proof pair, and what "done" means for
# each. Press files are signed off; documents just exist.
PAIRED = {"print": "press-ready", "signage": "press-ready",
          "documents": "with a proof"}


def _concepts(root: pathlib.Path, project_dir: pathlib.Path) -> dict | None:
    """A round of design-direction mockups, compared before anything is built.

    Directions live at `concepts/<slug>/index.html` — single-file HTML mockups
    authored by the design_concepting skill — with an optional NOTES.md whose
    first heading names the direction. `DECISION.md` records the chosen slug
    once the user has looked. The kind exists so choosing a look happens on
    live renders in the hub, not in a folder listing.
    """
    dirs = sorted(p.parent for p in root.glob("*/index.html")
                  if not _working(p.parent.relative_to(project_dir)))
    if not dirs:
        return None
    picked = None
    decision = root / "DECISION.md"
    if decision.is_file():
        m = re.search(r"\*\*Chosen:\*\*\s*`?([\w-]+)`?",
                      decision.read_text(encoding="utf-8", errors="replace"))
        picked = m.group(1) if m else None
    items = []
    for d in dirs:
        title = d.name.replace("-", " ").title()
        notes = d / "NOTES.md"
        if notes.is_file():
            m = re.search(r"^#\s+(.+)$",
                          notes.read_text(encoding="utf-8", errors="replace"),
                          re.MULTILINE)
            if m:
                title = m.group(1).strip()
        items.append({"slug": d.name, "title": title,
                      "rel": (d / "index.html").relative_to(
                          project_dir).as_posix(),
                      "chosen": d.name == picked})
    compare = root / "compare.html"
    note = (f"direction chosen: {picked}" if picked
            else f"{len(items)} direction{'s' * (len(items) != 1)}, "
                 "no decision yet")
    return {"id": "concepts", "label": "Design concepts", "count": len(items),
            "kind": "concepts", "items": items, "note": note,
            "compare": (compare.relative_to(project_dir).as_posix()
                        if compare.is_file() else None)}


def _captured_media(project_dir: pathlib.Path) -> dict | None:
    """The raw media pulled off the live site, surfaced as a browsable kind.

    Captures live under a leading-underscore working directory (`_capture-*`),
    so `_working` rightly hides them from the artefact tree — they are source
    material, not something the brand authored. But you still need to SEE them
    to choose which to rebuild a page from. This reads the capture's
    `media_catalog.csv` (folder, category and AI caption straight from the live
    site) and its pre-built `gallery-thumbs/`, and returns a gallery kind whose
    tiles are the small thumbnails (fast) but link to the full originals.

    Returns None when no capture with a built gallery exists — the kind then
    simply does not appear, exactly like every other absent kind.
    """
    caps = sorted(project_dir.glob("_capture-*"), reverse=True)
    for cap in caps:
        catalog = cap / "media_catalog.csv"
        thumbs = cap / "gallery-thumbs"
        uploads = cap / "media" / "wp-content" / "uploads"
        if not (catalog.is_file() and thumbs.is_dir()):
            continue
        items: list[dict] = []
        groups: dict[str, list[dict]] = {}
        with catalog.open(encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                fn = (row.get("filename") or "").strip()
                if pathlib.PurePath(fn).suffix.lower() not in IMAGE:
                    continue
                folder = (row.get("folder") or "").replace(
                    "wp-content/uploads", "").strip("/ ")
                relup = f"{folder}/{fn}" if folder else fn
                thumb = thumbs / (relup + ".webp")
                if not thumb.is_file():
                    hit = next(thumbs.rglob(fn + ".webp"), None)
                    if hit is None:
                        continue
                    thumb = hit
                    relup = thumb.relative_to(thumbs).as_posix()[:-5]
                orig = uploads / relup
                cat = (row.get("vmfo_folder") or "").strip() or "Uncategorised"
                cap_txt = (row.get("ai_caption") or row.get("caption")
                           or row.get("alt") or "").strip()
                item = {
                    "name": row.get("proposed_filename") or fn,
                    "rel": thumb.relative_to(project_dir).as_posix(),
                    "orig": (orig.relative_to(project_dir).as_posix()
                             if orig.is_file()
                             else thumb.relative_to(project_dir).as_posix()),
                    "kb": int(row["kb"]) if (row.get("kb") or "").isdigit() else 0,
                    "w": int(row["w"]) if (row.get("w") or "").isdigit() else 0,
                    "h": int(row["h"]) if (row.get("h") or "").isdigit() else 0,
                    "ext": "webp", "cap": cap_txt[:160], "cat": cat,
                }
                items.append(item)
                groups.setdefault(cat, []).append(item)
        if not items:
            continue
        grp = [{"id": re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-") or "misc",
                "label": c, "count": len(g), "items": g}
               for c, g in sorted(groups.items(), key=lambda kv: -len(kv[1]))]
        return {"id": "capture", "label": "Captured media", "count": len(items),
                "kind": "gallery", "items": items, "groups": grp,
                "note": f"{len(grp)} sets · from the live site"}
    return None


def kinds(project_dir: pathlib.Path) -> list[dict]:
    """Every artefact kind this project actually has, in a fixed order."""
    out = []
    for kid, label, rel in KINDS:
        root = project_dir / rel
        if not root.is_dir():
            continue
        if kid == "website":
            pages = pages_of(root)
            if not pages:
                continue
            out.append({"id": kid, "label": label, "count": len(pages),
                        "kind": "pages", "pages": pages,
                        "note": f"{len(tree(pages))} root, "
                                f"{len(sections(pages))} sections",
                        "tree": tree(pages), "sections": sections(pages)})
        elif kid == "concepts":
            k = _concepts(root, project_dir)
            if k:
                out.append(k)
        elif kid in PAIRED:
            items = _pair(_items(root, project_dir, IMAGE | DOC))
            if not items:
                continue
            ready = sum(i["ready"] for i in items)
            out.append({"id": kid, "label": label, "count": len(items),
                        "kind": "press", "items": items,
                        "groups": _families(items),
                        "note": f"{ready}/{len(items)} {PAIRED[kid]}"})
        else:
            items = _items(root, project_dir, IMAGE)
            if not items:
                continue
            groups = _gallery(items, rel, GALLERY_LABELS.get(kid))
            out.append({"id": kid, "label": label, "count": len(items),
                        "kind": "gallery", "items": items, "groups": groups,
                        "note": f"{len(groups)} sets"})
    cap = _captured_media(project_dir)
    if cap:
        out.append(cap)
    return out


LIGHT = ("id", "label", "count", "kind", "note")


def summary(project_dir: pathlib.Path) -> dict:
    """`kinds` is the cheap list a sidebar needs, `detail` the items."""
    ks = kinds(project_dir)
    return {"kinds": [{k: v for k, v in kind.items() if k in LIGHT}
                      for kind in ks],
            "detail": ks}


if __name__ == "__main__":                       # quick look from the CLI
    import sys
    d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                     else "outputs/drvarada-site")
    for k in kinds(d):
        print(f"\n  {k['label']:<20} {k['count']:>4}  "
              f"{k.get('note', k['kind'])}")
        if k["kind"] == "pages":
            for n in flatten(k["tree"])[:12]:
                print(f"      {'  ' * n['depth']}{n['url']}"
                      f"{'  (no page)' if n['stub'] else ''}")
            print(f"      … {len(k['pages'])} pages total")
            for s in k["sections"]:
                print(f"      {s['label']:<22} {s['count']:>3} pages")
        else:
            for g in k["groups"]:
                print(f"      {g['label']:<22} {g['count']:>3}  "
                      + ", ".join(i.get("subject") or i["name"]
                                  for i in g["items"][:4]))
