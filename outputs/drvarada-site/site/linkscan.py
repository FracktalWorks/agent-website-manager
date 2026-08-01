"""Every link on the site, and the ability to retarget them all at once.

WHY THIS EXISTS
  Open Design's manual-edit mode gives you a link inspector on any anchor and
  writes `href` back into that one element (`set-link` in
  `apps/web/src/edit-mode/source-patches.ts`). That is the right model for a
  single standalone artifact, and it is exactly the wrong one for a 45-page
  site: the WhatsApp button appears on every page, and retargeting it one anchor at a
  time is both unbearable and impossible to get right.

  Because our pages are data rather than markup, the same click can answer a
  question OD cannot even ask — "where else does this destination appear?" —
  and act on all of them. So the inspector gains a scope: this one, or all of them.

  The scan walks the page data through the *same positions the renderer reads*
  rather than grepping the source for a matching string. That distinction is
  load-bearing: the slug `"vitiligo"` appears in the source as a link target,
  as a page's own `slug` key, and inside a dozen sentences of prose. A textual
  search would rewrite all three. Walking the structure only ever finds the
  ones that are genuinely links.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import datapatch                                   # noqa: E402
import siteconf                                    # noqa: E402

CHROME = ROOT / "chrome.py"

# Module constants that hold a destination. Editing one of these is already the
# "everywhere" case by construction, which is why the site details form exists.
CONSTANTS = siteconf.LINK_CONSTANTS


@dataclass(frozen=True)
class Link:
    target: str          # slug or URL
    label: str
    where: str           # human-readable location
    slug: str            # page slug, or "" for chrome
    addr: str            # data address, or "" when it lives in a constant
    const: str = ""      # constant name when the destination is one
    sub: str = ""        # address INSIDE the constant ("0.2.1"), never prefixed
                         # with its name — datapatch.set_in_constant takes the
                         # name separately, and passing "NAV.0.2.1" makes it
                         # walk a step called "NAV" and fail on a non-dict


def _fresh(name: str):
    """Import a source module, reloading it if it is already in memory.

    The scan runs inside the long-lived editor process, which has usually
    imported these modules already — and Python caches them. Without the reload
    a scan taken after an edit reports the state before it, so "12 links point
    here" would be answered from a snapshot of the file as it was at startup.
    Every write the editor makes goes to disk, so re-reading is always correct.
    """
    import importlib                                # noqa: PLC0415
    mod = importlib.import_module(name)
    return importlib.reload(mod)


CONTENT_MODULES = siteconf.MODULES


def _pages() -> list[dict]:
    return [page for name in CONTENT_MODULES
            for page in _fresh(f"content.{name}").PAGES]


def _pair(entry, idx: int):
    """The (label, target) of a link tuple, or None if it is not one."""
    if not isinstance(entry, (list, tuple)) or len(entry) <= idx:
        return None
    target = entry[idx]
    if not isinstance(target, str) or not target:
        return None
    label = entry[0] if isinstance(entry[0], str) else ""
    return label, target


def page_links(page: dict) -> list[Link]:
    """Every link a page's data declares, in the positions chrome.py reads."""
    slug = page["slug"]
    out: list[Link] = []

    def add(entry, idx, addr, where):
        got = _pair(entry, idx)
        if got:
            out.append(Link(got[1], got[0], f"{slug}: {where}", slug, addr))

    for n, act in enumerate(page.get("acts") or []):
        add(act, 1, f"acts.{n}", "hero button")
    for n, rel in enumerate(page.get("related") or []):
        add(rel, 0, f"related.{n}", "related card")

    for i, sec in enumerate(page.get("sections") or []):
        kind = sec.get("kind")
        if sec.get("cta"):
            add(sec["cta"], 1, f"sections.{i}.cta", f"section {i} button")
        if kind == "chips":
            for n, item in enumerate(sec.get("items") or []):
                add(item, 1, f"sections.{i}.items.{n}", f"section {i} chip")
        if kind == "pillars":
            for n, item in enumerate(sec.get("items") or []):
                for j, row in enumerate(item.get("list") or []):
                    add(row, 1, f"sections.{i}.items.{n}.list.{j}",
                        f"section {i} pillar row")
                if item.get("go"):
                    add(item["go"], 1, f"sections.{i}.items.{n}.go",
                        f"section {i} pillar link")
    return out


def chrome_links() -> list[Link]:
    """Nav and footer links. These live in chrome.py constants, not page data,
    and they carry more destinations than any single page does."""
    chrome = _fresh("chrome")
    out: list[Link] = []
    for i, entry in enumerate(chrome.NAV):
        got = _pair(entry, 1)
        if got:
            out.append(Link(got[1], got[0], f"nav: {got[0]}", "",
                            "", sub=f"{i}.1", const="NAV"))
        for j, child in enumerate(entry[2] or []):
            got = _pair(child, 1)
            if got:
                out.append(Link(got[1], got[0], f"nav › {got[0]}", "",
                                "", sub=f"{i}.2.{j}.1", const="NAV"))
    for i, (group, rows) in enumerate(chrome.FOOTER):
        for j, row in enumerate(rows):
            got = _pair(row, 1)
            if got:
                out.append(Link(got[1], got[0], f"footer › {group}: {got[0]}",
                                "", "", sub=f"{i}.1.{j}.1", const="FOOTER"))
    # The language alternates moved out of FOOTER into their own constant. They
    # are still footer links on every page, so they still have to be scannable —
    # a list the scanner does not know about is a link nobody can retarget.
    for i, row in enumerate(chrome.LANGUAGES):
        got = _pair(row, 1)
        if got:
            out.append(Link(got[1], got[0], f"footer › language: {got[0]}",
                            "", "", sub=f"{i}.1", const="LANGUAGES"))
    return out


def constant_links() -> list[Link]:
    values = datapatch.read_constants(CHROME, list(CONSTANTS))
    return [Link(v, name, f"chrome.py constant {name}", "", "", const=name)
            for name, v in values.items() if isinstance(v, str) and v]


def all_links() -> list[Link]:
    return [ln for p in _pages() for ln in page_links(p)] + \
        chrome_links() + constant_links()


def normalize(href: str) -> str:
    """A rendered href back to the target the source actually stores.

    The browser hands us what it sees, and in a preview build that is
    `vitiligo.html` — a flat filename produced by `chrome.href()`. The source
    stores the slug `vitiligo`. Without undoing that the scan finds nothing and
    "used on 21 pages" silently reads as "used once", which is the worst
    possible failure for a control that offers to change everything at once.
    """
    href = (href or "").strip()
    if not href or "://" in href or href.startswith(("tel:", "mailto:", "#")):
        return href
    tail = href.rstrip("/").rsplit("/", 1)[-1]
    if tail.endswith(".html"):
        return tail[:-5]
    # A production build emits nested paths (`/locations/secunderabad/`), and
    # the last segment is NOT the slug — `locations-secunderabad` is. So the URL
    # map is consulted rather than the path guessed. Without this a scan run
    # against a production render answers "used once" for a link used on 21
    # pages, which is the failure mode that makes retarget-everywhere unsafe.
    if href.startswith("/"):
        from content.urls import URLS               # noqa: PLC0415
        want = href if href.endswith("/") else href + "/"
        for slug, path in URLS.items():
            if path == want:
                return slug
    return href


def occurrences(target: str) -> list[Link]:
    """Everywhere this exact destination is used."""
    target = normalize(target)
    if not target:
        return []
    return [ln for ln in all_links() if ln.target == target]


def retarget(old: str, new: str, *, skip: Link | None = None) -> list[str]:
    """Point every use of `old` at `new`. Returns a description of each change.

    A constant is rewritten once and covers all its uses at a stroke — which is
    the whole reason the Practo URL is a constant. Rewriting the constant AND
    the pages that reference it would be double work with no effect, so a
    destination that lives in a constant short-circuits the page pass.
    """
    old, new = normalize(old), normalize(new)
    hits = occurrences(old)
    if skip is not None:
        hits = [h for h in hits
                if not (h.slug == skip.slug and h.addr == skip.addr
                        and h.sub == skip.sub and h.const == skip.const)]
    done: list[str] = []
    for ln in hits:
        if ln.const and not ln.sub:
            datapatch.set_constant(CHROME, ln.const, new)
            done.append(f"chrome.py {ln.const}")
        elif ln.sub:
            datapatch.set_in_constant(CHROME, ln.const, ln.sub, new)
            done.append(f"chrome.py {ln.const}.{ln.sub}")
        else:
            current = datapatch.read(ln.slug, ln.addr)
            if not isinstance(current, (list, tuple)):
                continue
            idx = 0 if ln.addr.startswith("related.") else 1
            updated = list(current)
            updated[idx] = new
            datapatch.set_value(ln.slug, ln.addr,
                                tuple(updated) if isinstance(current, tuple)
                                else updated, create=False)
            done.append(f"{ln.slug}: {ln.addr}")
    return done


def _cli() -> int:
    import argparse                                 # noqa: PLC0415
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("where", help="everywhere a destination is used")
    p.add_argument("target")
    sub.add_parser("audit", help="every destination on the site, by frequency")
    args = ap.parse_args()

    if args.cmd == "where":
        hits = occurrences(args.target)
        print(f"{len(hits)} use(s) of {args.target!r}\n")
        for ln in hits:
            inside = f"{ln.const}.{ln.sub}" if ln.sub else ""
            print(f"  {ln.where:52s} {ln.addr or inside or ln.const}")
        return 0

    from collections import Counter                 # noqa: PLC0415
    counts = Counter(ln.target for ln in all_links())
    print(f"{sum(counts.values())} links to {len(counts)} distinct destinations\n")
    for target, n in counts.most_common():
        print(f"  {n:4d}  {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
