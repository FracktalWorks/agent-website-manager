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
"""

from __future__ import annotations

import json
import pathlib

IMAGE = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
DOC = {".pdf"}


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


def pages_of(site: pathlib.Path) -> list[dict]:
    """Read the build manifest. Empty if the site has never been built."""
    for name in ("dist/site-manifest.json", "dist-prod/site-manifest.json"):
        try:
            m = json.loads((site / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        return [{"slug": p.get("slug", ""), "title": p.get("title", ""),
                 "url": p.get("url", ""), "file": p.get("file", ""),
                 "template": p.get("template", ""),
                 "module": p.get("module", "")}
                for p in m.get("pages", [])]
    return []


# ----------------------------------------------------------------- the kinds

def _items(root: pathlib.Path, base: pathlib.Path, exts: set[str],
           limit: int = 400) -> list[dict]:
    if not root.is_dir():
        return []
    out = []
    for f in sorted(root.rglob("*")):
        if f.is_file() and f.suffix.lower() in exts:
            out.append({"name": f.name, "rel": f.relative_to(base).as_posix(),
                        "kb": f.stat().st_size // 1024,
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
        out.append({"name": stem, "proof": (proofs.get(stem) or {}).get("rel"),
                    "pdf": (pdf or {}).get("rel"), "ready": bool(pdf),
                    "kb": (pdf or proofs.get(stem) or {}).get("kb", 0)})
    return out


KINDS = [
    ("website", "Website", "site"),
    ("print", "Print collateral", "print/out"),
    ("brand", "Brand assets", "brand"),
    ("signage", "Signage", "signage/out"),
]


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
                        "tree": tree(pages)})
        elif kid in ("print", "signage"):
            items = _pair(_items(root, project_dir, IMAGE | DOC))
            if not items:
                continue
            ready = sum(i["ready"] for i in items)
            out.append({"id": kid, "label": label, "count": len(items),
                        "kind": "press", "items": items,
                        "note": f"{ready}/{len(items)} press-ready"})
        else:
            items = _items(root, project_dir, IMAGE)
            if not items:
                continue
            groups: dict[str, list[dict]] = {}
            for i in items:
                groups.setdefault(i["rel"].split("/")[1]
                                  if "/" in i["rel"][len("brand/"):]
                                  else "root", []).append(i)
            out.append({"id": kid, "label": label, "count": len(items),
                        "kind": "gallery", "items": items,
                        "groups": sorted(groups)})
    return out


def summary(project_dir: pathlib.Path) -> dict:
    ks = kinds(project_dir)
    return {"kinds": [{k: v for k, v in kind.items()
                       if k not in ("pages", "tree", "items")}
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
        else:
            for i in k["items"][:6]:
                print(f"      {i['name']}")
