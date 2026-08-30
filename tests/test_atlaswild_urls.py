"""The migration map: does every old URL still land somewhere?

`outputs/atlaswild-site/site/content/urls.py` holds the map from the live old
site's paths to the new slugs. It is the only thing standing between a
relaunch and throwing away everything those URLs have earned, and it is the
kind of file that rots silently — a new page is added, an old one is
forgotten, and nobody finds out until the 404s show up in Search Console
months later.

It had already rotted once. It covered 9 of the 72 old paths and contained
three that never existed (`/experiences/`, `/contact-us/`,
`/cancellation-policy/`) because it had been written from a general sense of
what a site like this has rather than from the crawl. These tests make both
failures loud: the map must cover the inventory exactly, and every target must
be a real page.

The inventory is `library/content/pages.json` + `products.json`, which is what
`audit_coverage.py` crawled — 33 pages and 39 products.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "atlaswild-site" / "site"
LIB = ROOT / "outputs" / "atlaswild-site" / "library" / "content"

pytestmark = pytest.mark.skipif(
    not (SITE / "content" / "urls.py").exists() or not LIB.is_dir(),
    reason="atlaswild site not in this checkout")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                     # type: ignore
    return mod


@pytest.fixture(scope="module")
def urls():
    return _load("awe_urls", SITE / "content" / "urls.py")


@pytest.fixture(scope="module")
def chrome():
    import sys
    sys.path.insert(0, str(SITE))
    try:
        return _load("awe_chrome", SITE / "chrome.py")
    finally:
        sys.path.remove(str(SITE))


@pytest.fixture(scope="module")
def old_paths() -> set[str]:
    pages = json.loads((LIB / "pages.json").read_text(encoding="utf-8"))
    prods = json.loads((LIB / "products.json").read_text(encoding="utf-8"))
    out = {re.sub(r"https://atlaswildexperiences\.com", "", p["link"])
           for p in pages}
    out |= {f'/product/{p["slug"]}/' for p in prods}
    return out


def test_every_old_url_still_lands_somewhere(urls, old_paths, chrome):
    """The failure this exists for: 63 of 72 paths were missing.

    There are two honest ways for an old URL to survive the relaunch, and this
    asserts every one of the 72 uses one of them. Most are MOVED — a 301 in
    REDIRECTS to the page that replaced them. The shop's URLs are instead
    KEPT: since 2026-08-27 WooCommerce still serves /shop/, /cart/, /checkout/,
    /my-account/ and all 39 /product/ pages from the same webroot, and
    redirecting those would be the bug, not the fix — a 301 on /checkout/ is a
    shop that cannot take money. What is not allowed is a path that does
    neither, because that one 404s.
    """
    missing = sorted(p for p in old_paths - set(urls.REDIRECTS)
                     if not chrome.served_by_wordpress(p))
    assert not missing, (
        f"{len(missing)} live old URLs are neither redirected nor served by "
        f"WordPress, so they will 404 at relaunch: {missing[:8]}")


def test_commerce_urls_are_never_redirected(urls, chrome):
    """A 301 on /checkout/ is a shop that cannot take money.

    The map used to fold all of them into /prints/, which was right while the
    store was being retired and became wrong the moment it was kept. This is
    the assertion that nobody quietly puts them back.
    """
    hijacked = sorted(p for p in urls.REDIRECTS if chrome.served_by_wordpress(p))
    assert not hijacked, (
        f"these are live WooCommerce URLs and must not be redirected: "
        f"{hijacked[:8]}")


def test_no_redirect_from_a_path_that_never_existed(urls, old_paths):
    """A redirect nobody can trigger is not harmful, but it is evidence the
    map was written from memory — and a map written from memory is also
    missing things. Fail on it so the source stays the crawl."""
    invented = sorted(set(urls.REDIRECTS) - old_paths)
    assert not invented, (
        f"these paths are not in the crawled inventory: {invented}")


def test_every_redirect_target_is_a_real_page(urls):
    """A 301 to a slug that does not exist is a 301 to a 404, which is worse
    than the original 404 because it looks handled."""
    bad = {old: slug for old, slug in urls.REDIRECTS.items()
           if slug not in urls.URLS}
    assert not bad, f"redirect targets that are not pages: {bad}"


def test_no_redirect_loops(urls):
    """A path that maps to its own new URL would send the server round in a
    circle. `build.py` filters these out of .htaccess; this is the assertion
    that the filter is still needed and still correct."""
    loops = {old for old, slug in urls.REDIRECTS.items()
             if urls.URLS[slug] == old}
    # These are legitimate: the URL did not move. They must be in the map (so
    # the inventory check passes) and out of the .htaccess. `/shipping-policy/`
    # joined them when the Shipping & returns page took that exact old path as
    # its own URL — the old link still resolves, and no 301 is emitted.
    assert loops == {"/", "/contact/", "/prints/", "/shipping-policy/"}, \
        f"unexpected self-redirects: {loops}"


def test_the_emitted_htaccess_matches_the_map(urls):
    """The map used to be a dict no code imported. Now it is emitted — so the
    emitted file is what actually has to be right."""
    ht = SITE / "dist" / ".htaccess"
    if not ht.exists():
        pytest.skip("site not built")
    rules = re.findall(r"RewriteRule \^(\S+)\$ (\S+) \[R=301,L\]",
                       ht.read_text(encoding="utf-8"))
    emitted = {"/" + old: new for old, new in rules}
    expected = {old: urls.URLS[slug] for old, slug in urls.REDIRECTS.items()
                if urls.URLS[slug] != old}
    assert emitted == expected


def test_slugs_and_urls_do_not_collide(urls):
    """Two slugs pointing at one URL means one of them is unreachable."""
    seen: dict[str, str] = {}
    for slug, url in urls.URLS.items():
        assert url not in seen, f"{slug} and {seen[url]} both claim {url}"
        seen[url] = slug
