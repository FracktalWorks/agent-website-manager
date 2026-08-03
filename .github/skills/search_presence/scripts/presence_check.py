#!/usr/bin/env python
"""Check everything a search or answer engine needs from a live site.

    python presence_check.py https://example.com
    python presence_check.py https://example.com --local --indexnow-key KEY

This is the deterministic half of the search_presence skill. It answers "is
the site correctly *presented*" -- the part that is a file, a tag or a
redirect. It cannot answer "is the site correctly *registered*" (Search
Console, Bing, Business Profile), because those live in accounts, not on the
domain. The skill carries that half as a human checklist.

WHY EACH CHECK EXISTS. Every one of these has been a real silent failure:

  favicon        Google needs /favicon.ico at the ROOT and a square icon whose
                 side is a multiple of 48. An SVG-only <link rel=icon> renders
                 perfectly in every browser and gives a grey globe in search
                 results, for months, with nothing broken to find.
  canonical host The four spellings of a domain must converge on one. Two that
                 both answer 200 split every signal the site earns.
  sitemap        A sitemap that 404s is invisible; one that is not named in
                 robots.txt is found only if someone submitted it by hand.
  schema geo     A LocalBusiness without coordinates is placed by string-
                 matching its address, which is how a pin lands on the wrong
                 side of the road. `geo` is the field most often left out.
  og:image       Social and chat previews fetch it cold. A relative or 404
                 image is invisible in the editor and blank in the share card.

Output is a report, not a gate: exit 1 if anything FAILs, 0 otherwise.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from urllib.parse import urljoin, urlparse

import requests

UA = ("Mozilla/5.0 (compatible; presence-check/1.0; "
      "+https://github.com/agent-website-manager)")
TIMEOUT = 20

OK, WARN, FAIL, INFO = "OK", "WARN", "FAIL", "--"
ROWS: list[tuple[str, str, str]] = []


def row(status: str, label: str, detail: str = "") -> None:
    ROWS.append((status, label, detail))


def get(url: str, **kw):
    try:
        return requests.get(url, headers={"User-Agent": UA},
                            timeout=TIMEOUT, **kw)
    except requests.RequestException as e:
        return e


# --------------------------------------------------------------- root files

def check_host(base: str) -> None:
    """All four spellings of the domain must land on one canonical URL."""
    host = urlparse(base).netloc
    bare = host[4:] if host.startswith("www.") else host
    want = None
    for candidate in (f"http://{bare}/", f"http://www.{bare}/",
                      f"https://www.{bare}/", f"https://{bare}/"):
        r = get(candidate, allow_redirects=True)
        if isinstance(r, Exception):
            row(WARN, f"host {candidate}", str(r)[:70])
            continue
        final = r.url.rstrip("/") + "/"
        want = want or final
        if final != want:
            row(FAIL, f"host {candidate}", f"lands on {final}, not {want}")
        else:
            row(OK, f"host {candidate}", f"-> {final} ({r.status_code})")


def check_favicon(base: str, html: str) -> None:
    """Root .ico presence and a size Google will actually use."""
    from PIL import Image
    # Reported BEFORE the fetch, because when the root .ico is missing this
    # line is the diagnosis: "4 declarations, all svg" is the shape of a site
    # that looks fine in every browser and shows a globe in Google.
    declared = re.findall(r'<link[^>]+rel="[^"]*icon[^"]*"[^>]*>', html, re.I)
    kinds = {("svg" if ".svg" in d else "ico" if ".ico" in d else "png")
             for d in declared}
    row(INFO, "declared icons",
        f"{len(declared)} <link rel=icon> ({', '.join(sorted(kinds)) or '-'})")

    r = get(urljoin(base, "/favicon.ico"))
    if isinstance(r, Exception) or r.status_code != 200:
        code = "error" if isinstance(r, Exception) else r.status_code
        row(FAIL, "/favicon.ico",
            f"{code} - Google falls back to this path; an SVG-only "
            "declaration is not enough")
        return
    try:
        im = Image.open(io.BytesIO(r.content))
        sizes = (sorted(im.ico.sizes()) if hasattr(im, "ico")
                 else [im.size])
    except Exception as e:                                    # noqa: BLE001
        row(FAIL, "/favicon.ico", f"unreadable: {e}")
        return
    good = [s for s in sizes if s[0] == s[1] and s[0] % 48 == 0]
    txt = ", ".join(f"{w}x{h}" for w, h in sizes)
    if good:
        row(OK, "/favicon.ico", f"{len(r.content)}b - {txt}")
    else:
        row(FAIL, "/favicon.ico",
            f"{txt} - none is a square multiple of 48; Google will not use it")


def check_robots_sitemap(base: str) -> None:
    r = get(urljoin(base, "/robots.txt"))
    sitemaps: list[str] = []
    if isinstance(r, Exception) or r.status_code != 200:
        row(FAIL, "/robots.txt", "missing")
    else:
        body = r.text
        sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", body)
        blanket = re.search(
            r"(?im)^\s*user-agent:\s*\*\s*$\s*disallow:\s*/\s*$", body)
        row(FAIL if blanket else OK, "/robots.txt",
            "Disallow: / for all agents" if blanket
            else f"{len(body)}b, {len(sitemaps)} sitemap directive(s)")
        if not sitemaps:
            row(WARN, "robots sitemap",
                "no Sitemap: line - engines must be told by hand")
    for sm in (sitemaps or [urljoin(base, "/sitemap.xml")]):
        r = get(sm)
        if isinstance(r, Exception) or r.status_code != 200:
            row(FAIL, f"sitemap {sm}", "unreachable")
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)", r.text)
        off = [u for u in locs
               if urlparse(u).netloc not in (urlparse(base).netloc, "")][:3]
        row(FAIL if off else OK, f"sitemap {urlparse(sm).path}",
            f"off-domain URLs: {off}" if off else f"{len(locs)} URL(s)")


def check_indexnow(base: str, key: str) -> None:
    r = get(urljoin(base, f"/{key}.txt"))
    ok = (not isinstance(r, Exception) and r.status_code == 200
          and r.text.strip() == key)
    row(OK if ok else FAIL, "IndexNow key",
        f"/{key}.txt serves the key" if ok else
        f"/{key}.txt must return exactly the key - that IS the "
        "ownership proof")


# -------------------------------------------------------------- page markup

def check_head(base: str, html: str) -> None:
    def meta(name: str) -> str | None:
        m = re.search(
            rf'<meta[^>]+(?:name|property)="{name}"[^>]+content="([^"]*)"',
            html, re.I)
        return m.group(1) if m else None

    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    t = (title.group(1).strip() if title else "")
    row(OK if 15 <= len(t) <= 65 else WARN, "<title>",
        f"{len(t)} chars - {t[:56]}")

    d = meta("description") or ""
    row(OK if 70 <= len(d) <= 165 else WARN, "meta description",
        f"{len(d)} chars" + ("" if d else " - missing"))

    canon = re.search(
        r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', html, re.I)
    row(OK if canon else FAIL, "canonical",
        canon.group(1) if canon else "no canonical link")

    for tag, label in (("google-site-verification", "Google verify meta"),
                       ("msvalidate.01", "Bing verify meta")):
        row(INFO, label,
            "present" if meta(tag) else "absent (fine if verified by "
                                        "DNS, file or GSC import)")

    og = meta("og:image")
    if not og:
        row(WARN, "og:image", "absent - share cards render blank")
        return
    u = urljoin(base, og)
    r = get(u, stream=True)
    bad = isinstance(r, Exception) or r.status_code != 200
    rel = "" if og.startswith("http") else "  (relative - prefer absolute)"
    row(FAIL if bad else OK, "og:image",
        f"unreachable {u}" if bad else
        f"{r.headers.get('content-type', '?')} "
        f"{r.headers.get('content-length', '?')}b{rel}")


LOCAL_TYPES = ("LocalBusiness", "MedicalBusiness", "MedicalClinic", "Dentist",
               "Physician", "Store", "Restaurant", "ProfessionalService")

# Each entry is a set of ALTERNATES. schema.org accepts more than one spelling
# of the same fact, and a checker that demands one spelling reports a correct
# site as incomplete -- a false alarm nobody trusts twice.
LOCAL_FIELDS = (("name",), ("address",), ("telephone",), ("url",),
                ("image", "logo", "photo"), ("geo",),
                ("openingHours", "openingHoursSpecification"),
                ("hasMap",), ("sameAs",), ("priceRange",))


def walk(node, out: list[dict]) -> None:
    if isinstance(node, dict):
        if "@type" in node:
            out.append(node)
        for v in node.values():
            walk(v, out)
    elif isinstance(node, list):
        for v in node:
            walk(v, out)


# A node that only points at an entity defined elsewhere in the same graph.
#
# Correct JSON-LD says an entity once and refers to it by `@id` everywhere else,
# so `"worksFor": {"@type": "MedicalClinic", "@id": ".../#clinic", "name": ...}`
# is the RIGHT way to attach a doctor to a clinic — the clinic's address, pin and
# hours live on the node that shares that `@id`. Grading the pointer as though it
# were the entity reported this site as missing eight fields it actually had, and
# raised a red `geo` gate against coordinates that were present twice on the same
# page. A gate that cries wolf is worse than no gate: it teaches you to ship past
# red. So a stub is skipped, but ONLY when the graph really does define it
# elsewhere — an `@id` pointing at nothing is a genuine fault and still counts.
REF_KEYS = {"@type", "@id", "name", "url"}


def is_reference(node: dict, nodes: list[dict]) -> bool:
    ref_id = node.get("@id")
    if not ref_id or not set(node).issubset(REF_KEYS):
        return False
    return any(o is not node and o.get("@id") == ref_id
               and not set(o).issubset(REF_KEYS) for o in nodes)


def check_schema(html: str, local: bool) -> None:
    blocks = re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        html, re.I | re.S)
    if not blocks:
        row(FAIL, "JSON-LD", "no structured data on the homepage")
        return
    nodes: list[dict] = []
    for b in blocks:
        try:
            walk(json.loads(b), nodes)
        except json.JSONDecodeError as e:
            row(FAIL, "JSON-LD", f"invalid JSON: {e}")
    types = sorted({str(n.get("@type")) for n in nodes})
    row(OK, "JSON-LD", f"{len(blocks)} block(s), {len(types)} types")
    if not local:
        return
    biz = [n for n in nodes
           if any(t in str(n.get("@type")) for t in LOCAL_TYPES)]
    biz = [n for n in biz if not is_reference(n, nodes)]
    if not biz:
        row(FAIL, "LocalBusiness", "no local business type on the homepage")
        return
    geo_missing = False
    for n in biz[:4]:
        missing = [alt[0] for alt in LOCAL_FIELDS
                   if not any(n.get(f) for f in alt)]
        label = f"{n.get('@type')} {str(n.get('name'))[:24]}"
        row(WARN if missing else OK, label,
            ("missing: " + ", ".join(missing)) if missing
            else "all fields present")
        geo_missing = geo_missing or "geo" in missing
    if geo_missing:
        row(FAIL, "geo coordinates",
            "absent - the pin is guessed from the address string. "
            "Right-click it in Google Maps to copy lat/long.")


# --------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url")
    ap.add_argument("--indexnow-key", default="")
    ap.add_argument("--local", action="store_true",
                    help="also audit LocalBusiness schema completeness")
    a = ap.parse_args()
    base = a.url if "://" in a.url else "https://" + a.url

    r = get(base)
    if isinstance(r, Exception) or r.status_code != 200:
        print(f"homepage unreachable: {r}")
        return 2
    html, base = r.text, r.url

    check_host(base)
    check_robots_sitemap(base)
    check_favicon(base, html)
    if a.indexnow_key:
        check_indexnow(base, a.indexnow_key)
    check_head(base, html)
    check_schema(html, a.local)

    w = max(len(x[1]) for x in ROWS)
    print(f"\n  {base}\n")
    for status, label, detail in ROWS:
        print(f"  {status:<4} {label:<{w}}  {detail}")
    bad = sum(1 for s, _, _ in ROWS if s == FAIL)
    warn = sum(1 for s, _, _ in ROWS if s == WARN)
    ok = sum(1 for s, _, _ in ROWS if s == OK)
    print(f"\n  {bad} fail, {warn} warn, {ok} ok\n")
    print("  Not checked here (these live in accounts, not on the domain):\n"
          "  Search Console property + sitemap, Bing import, Business\n"
          "  Profile name/hours/photos, IndexNow submissions. Those are the\n"
          "  checklist half of the search_presence skill.\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
