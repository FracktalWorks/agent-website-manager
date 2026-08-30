"""Every price on the Atlas Wild site is one the rate card actually contains.

A wrong price on a travel site is not a typo — it is a number somebody holds
you to. The 2027 rates were supplied once, as a spreadsheet, and then written
by hand onto eleven pages: two journey hubs, the Tryst trip page, six
destination pages and the cost page's rate card. Hand-copying is how the figure
on the destination page and the figure on the cost page stop agreeing.

`content/_prices.py` holds the supplied numbers. These tests assert that no
page shows a dollar figure that table does not contain, that the schema.org
Offers carry the same numbers a reader sees, and that every published figure
is rounded UP to the hundred — never below what the trip actually costs.

The pages keep LITERAL price strings rather than calling into `_prices`,
because `datapatch.py` finds an editable value by walking the AST for a
literal — a computed price would vanish from the live editor. Literals in the
pages plus this test is what keeps both properties.
"""
from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "atlaswild-site" / "site"
CONTENT = SITE / "content"

pytestmark = pytest.mark.skipif(
    not (CONTENT / "_prices.py").exists(),
    reason="atlaswild site not in this checkout")

# The Pantanal is priced from its own itinerary PDF, in a different country and
# a different business line, so it is not on the India rate card. It is allowed
# by name rather than by silence, so that adding a second exception is a
# deliberate act.
OFF_CARD = {"USD 5,800"}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                     # type: ignore
    return mod


@pytest.fixture(scope="module")
def prices():
    return _load("awe_prices", CONTENT / "_prices.py")


@pytest.fixture(scope="module")
def sources() -> dict[str, str]:
    return {f.name: f.read_text(encoding="utf-8")
            for f in CONTENT.glob("*.py") if not f.name.startswith("_")}


def test_rounding_is_always_upward(prices):
    """Published prices round UP to the hundred, never down.

    Changed from nearest-hundred on 2026-08-27. Nearest put six of the twelve
    rates BELOW what the trip actually costs, and a published price under cost
    is a number the business is held to. So the assertion is directional: the
    published figure is a round hundred, is never less than the real cost, and
    is within one hundred of it — the last part catching a price that has been
    rounded up twice, which is the failure mode of editing these by hand.
    """
    for key, row in prices.PRICES.items():
        assert row["usd"] % 100 == 0, f"{key}: {row['usd']} is not a round hundred"
        assert row["usd"] >= row["usd_exact"], (
            f"{key}: {row['usd']} is BELOW the real cost {row['usd_exact']}")
        assert row["usd"] - row["usd_exact"] < 100, (
            f"{key}: {row['usd']} is more than a hundred above "
            f"{row['usd_exact']} — rounded up twice?")


def test_the_exchange_rate_is_consistent(prices):
    """One rate struck across the whole card, or the card is two cards.

    Caught nothing when written — all twelve rows agree to the paisa. It exists
    so that a row edited in isolation, at a different rate, is loud.
    """
    off = {k: round(r["inr_pp"] / r["usd_exact"], 2)
           for k, r in prices.PRICES.items()
           if abs(r["inr_pp"] / r["usd_exact"] - prices.INR_PER_USD) > 0.01}
    assert not off, f"rows struck at a different rate than INR_PER_USD: {off}"


def test_group_size_divides_exactly(prices):
    """Per-group ÷ per-person must be a whole number of people."""
    bad = {k: r["inr_group"] / r["inr_pp"] for k, r in prices.PRICES.items()
           if abs(r["inr_group"] / r["inr_pp"] - r["group"]) > 0.01}
    assert not bad, f"group size does not divide exactly: {bad}"


def test_no_page_shows_a_price_the_card_does_not_contain(prices, sources):
    """The one that matters: no invented, stale or mistyped figure."""
    allowed = {f"USD {r['usd']:,}" for r in prices.PRICES.values()} | OFF_CARD
    found: dict[str, set[str]] = {}
    for name, src in sources.items():
        for m in re.findall(r"USD [\d,]+", src):
            if m not in allowed:
                found.setdefault(name, set()).add(m)
    assert not found, f"prices not on the rate card: {found}"


def test_schema_offers_match_the_rate_card(prices, sources):
    """A reader sees one number and Google is told another — invisible, and bad.

    `chrome.page_schema` publishes `trip["price"]` as a schema.org Offer. If it
    drifts from the facts block, the rich result quotes a price the page does
    not.
    """
    allowed = {r["usd"] for r in prices.PRICES.values()} | {5800}
    bad = {}
    for name, src in sources.items():
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.Dict):
                continue
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "slug" not in keys or "trip" not in keys:
                continue
            slug = node.values[keys.index("slug")].value
            trip = node.values[keys.index("trip")]
            tk = [k.value for k in trip.keys if isinstance(k, ast.Constant)]
            if "price" not in tk:
                continue
            val = trip.values[tk.index("price")]
            price = val.value if isinstance(val, ast.Constant) else "?"
            if price is None:              # honestly unpriced — allowed
                continue
            if price not in allowed:
                bad[slug] = price
    assert not bad, f"schema Offers not on the rate card: {bad}"


def test_the_placeholder_price_is_gone(sources):
    """₹9,99,999 was WooCommerce's way of saying nobody had set a price.

    It may still be DESCRIBED — the cost page explains where it came from —
    but it must never appear as a price a page is quoting.
    """
    for name, src in sources.items():
        for m in re.findall(r'\("Price[^"]*", "[^"]*9,99,999[^"]*"\)', src):
            pytest.fail(f"{name} still quotes the placeholder: {m}")


def test_a_price_always_says_what_it_is_per(sources):
    """"USD 9,000" alone is not a price, it is half of one.

    These are per-person figures struck on a group of seven or eight. A page
    that states the number without the basis is quoting something it cannot
    honour, so every price row must carry "per person".
    """
    thin = []
    for name, src in sources.items():
        for m in re.findall(r'\("(?:Price|Price from)", "(USD [^"]*)"\)', src):
            if "per person" not in m:
                thin.append(f"{name}: {m}")
    assert not thin, f"price rows with no basis stated: {thin}"
