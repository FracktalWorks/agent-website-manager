"""The site may only sell what the shop can actually sell.

The Atlas Wild site is static pages with WooCommerce running behind them, and
the prints galleries link each frame to the product that sells it. That is the
join, and it can fail in two directions: a link to a product that no longer
exists (a 404 where a checkout should be), and a link to a product WooCommerce
has not priced.

The second is the live one. Eleven of the shop's 39 products carry ₹9,99,999 —
WooCommerce's way of saying nobody set a price — or ₹1, and they are buyable on
the shop today. They are marked `sellable: false` when `store.py pull` writes
`content/_store.json`, and the site must never point anyone at them. Sending a
customer to a page that offers a safari at ₹9,99,999 is worse than not linking
to it at all.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "atlaswild-site" / "site"
MANIFEST = SITE / "content" / "_store.json"
CONTENT = SITE / "content"

pytestmark = pytest.mark.skipif(
    not MANIFEST.exists(), reason="atlaswild store manifest not in this checkout")


@pytest.fixture(scope="module")
def catalogue() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["products"]


@pytest.fixture(scope="module")
def linked() -> set[str]:
    """Every /product/ URL any content module points at."""
    found: set[str] = set()
    for f in CONTENT.glob("*.py"):
        found |= set(re.findall(r'"(/product/[a-z0-9-]+/)"',
                                f.read_text(encoding="utf-8")))
    return found


def test_no_page_links_to_an_unpriced_product(catalogue, linked):
    """The one that matters. A link to a ₹9,99,999 product is a link to a lie."""
    bad = {p["url"]: p["name"] for p in catalogue
           if not p["sellable"] and p["url"] in linked}
    assert not bad, (
        f"these products are linked from the site but WooCommerce has not "
        f"priced them: {bad}")


def test_every_product_link_is_a_real_product(catalogue, linked):
    """A link to a product that does not exist is a 404 where money should be."""
    known = {p["url"] for p in catalogue}
    missing = sorted(linked - known)
    assert not missing, f"linked but not in the catalogue: {missing}"


def test_linked_products_are_in_stock(catalogue, linked):
    """Selling an out-of-stock print is a support email, not a sale."""
    out = {p["url"]: p["name"] for p in catalogue
           if p["url"] in linked and not p.get("in_stock", True)}
    assert not out, f"linked but out of stock: {out}"


def test_the_manifest_still_knows_the_shop_is_broken(catalogue):
    """A canary, not a pass/fail on the shop.

    This asserts the manifest is still MARKING unpriced products rather than
    quietly deciding everything is fine — if `sellable` ever became True for
    all 39 because the pull logic broke, the guard above would stop guarding
    and nobody would notice. If the owner genuinely prices them all in
    wp-admin, this test is the one to delete, deliberately.
    """
    unsellable = [p for p in catalogue if not p["sellable"]]
    assert unsellable, (
        "every product is now sellable — if the shop was really fixed, delete "
        "this test; if the pull broke, fix store.py")
    for p in unsellable:
        assert p["price_minor"] in ("999999", "1") or not p["price_minor"], (
            f"{p['name']} is marked unsellable for an unexpected reason: "
            f"{p['price_minor']}")
