"""The PrintStick landing page — the claims a buyer acts on.

This page asks for money. Everything below is a fact a visitor uses to decide
whether to spend it, and every one of them was wrong, missing or contradictory
on the page as found on 2026-08-25:

  · both "Buy" buttons went to `/contact-us/` while the two products sat in
    WooCommerce, in stock and purchasable, at exactly the prices the page
    printed. The most motivated visitor on the page — the one reaching for the
    buy button — was the one sent furthest from the checkout;
  · one card said "No solvents", another two cards later said "Solvent-Based
    Polymer Formula". A page that contradicts itself about what is in the
    bottle is not a page anyone buys from;
  · the formula recommendation covered six of the twelve materials Fracktal
    stocks, in a sentence. The other six were a guess.

None of that is visible to `verify.py`, `imgfit.py` or `mobile.py`: the page
rendered clean at five widths throughout. These are the assertions that keep it
true, not the assertions that keep it rendering.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "fracktal-site" / "site"
COPY = SITE / "content" / "printstick-copy.json"

pytestmark = pytest.mark.skipif(
    not (SITE / "printstick_table.py").exists(),
    reason="fracktal site not in this checkout")


def _load(name: str):
    """Import one of this site's modules under a name of its own.

    Every generated site has a `chrome.py`; importing this one as plain
    `chrome` hands it to whichever test imports `chrome` next.
    """
    spec = importlib.util.spec_from_file_location(f"fracktal_{name}",
                                                  SITE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def page() -> dict:
    return json.loads(COPY.read_text(encoding="utf-8"))


def _section(page: dict, **match) -> dict:
    for s in page["sections"]:
        if all(s.get(k) == v for k, v in match.items()):
            return s
    raise AssertionError(f"no section matching {match}")


def _text(cell: str) -> str:
    return re.sub(r"<[^>]+>", "", cell).strip()


# --------------------------------------------------------------- the table

def test_the_formula_table_still_agrees_with_the_material_database(page):
    """The rows are DERIVED, so a database edit must not leave them behind.

    `material-database.json` is this site's declared single source of truth and
    the twelve material pages read their figures from it. A bed temperature
    typed into this page by hand is a figure that drifts the first time one of
    those ranges is revised — and it would drift silently, because a table of
    plausible numbers looks exactly like a table of correct ones.
    """
    derived = _load("printstick_table").rows()
    section = _section(page, id="formula-picker")
    assert section["rows"] == derived, (
        "the formula table and the material database disagree — "
        "run `python printstick_table.py --write`")


def test_the_column_order_the_phone_stylesheet_relies_on_has_not_moved(page):
    """`landing.css` hides the THIRD column of this table below 600px.

    It does that by `nth-child(3)`, because `blk_spectable` emits bare
    `th`/`td` with nothing to target. Fine while column 3 is Enclosure —
    context a phone can lose — and silently destructive the day someone
    reorders the columns and the phone starts hiding the formula instead. The
    last column has to stay the answer for the same reason.
    """
    section = _section(page, id="formula-picker")
    assert section["columns"][2] == "Enclosure", (
        "landing.css hides column 3 on phones expecting it to be Enclosure")
    assert section["columns"][-1] == "PrintStick formula"


def test_the_threshold_reproduces_the_assignments_the_page_states_in_prose(
        page):
    """The 80 °C rule is only legitimate because it was checked, not chosen.

    The pricing lede promises Standard for "PLA, PET-G and TPU" and Plus for
    "ABS, PC and Nylon". Those six came from Fracktal, not from a threshold, so
    they are the fixture the threshold has to satisfy. If someone later tunes
    `PLUS_AT` to make a tidier split, this is what stops the table quietly
    contradicting the sentence three sections above it.
    """
    table = _load("printstick_table")
    want = {"PLA": "Standard", "PETG": "Standard", "TPU 95A": "Standard",
            "ABS": "Plus", "PC": "Plus", "Nylon PA12": "Plus"}
    got = {_text(r[0]): _text(r[3]) for r in table.rows()}
    for material, formula in want.items():
        assert got[material] == formula, (
            f"{material} derives as {got[material]} but the page's own copy "
            f"says {formula}")


# ---------------------------------------------------------- the buy path

def test_every_buy_button_reaches_the_shop_and_not_the_contact_form(page):
    pricing = _section(page, kind="pricing")
    for tier in pricing["tiers"]:
        href = tier["button"]["href"]
        assert "/product/" in href, (
            f"{tier['name']} sends a ready buyer to {href}")


def test_the_struck_through_price_is_higher_than_the_price_charged(page):
    """A `was` under the price is not a discount, just a markup drawn so."""
    def rupees(s: str) -> int:
        return int(re.sub(r"[^\d]", "", s))

    for tier in _section(page, kind="pricing")["tiers"]:
        if not tier.get("was"):
            continue
        assert rupees(tier["was"]) > rupees(tier["price"]), (
            f"{tier['name']}: was {tier['was']} vs price {tier['price']}")


def test_both_tiers_show_the_product_they_charge_for(page):
    for tier in _section(page, kind="pricing")["tiers"]:
        image = tier.get("image") or {}
        assert image.get("src"), f"{tier['name']} has no product image"
        assert (SITE / "assets" / "img" / image["src"]).exists(), image["src"]
        assert image.get("cutout"), (
            f"{tier['name']}'s bottle is a transparent cutout and must be "
            f"declared one, or imgfit.py cannot check how it meets its frame")


def test_the_two_tiers_draw_their_bottles_at_the_same_size(page):
    """Both are 50 ml. A bigger picture for the dearer one is a false claim.

    They are built to a common frame by the prep script, so this asserts the
    frames match rather than trusting that they were built together.
    """
    from PIL import Image
    sizes = set()
    for tier in _section(page, kind="pricing")["tiers"]:
        with Image.open(SITE / "assets" / "img" / tier["image"]["src"]) as im:
            sizes.add(im.size)
    assert len(sizes) == 1, f"tier images are on different frames: {sizes}"


# ------------------------------------------------------ the drawn bottles

SVG = SITE / "assets" / ".imgsrc"


def _svg(tier: str) -> str:
    return (SVG / f"printstick-tier-{tier}.svg").read_text(encoding="utf-8")


def _label(tier: str) -> list[str]:
    return re.findall(r"<text[^>]*>([^<]+)</text>", _svg(tier))


def test_the_two_bottles_are_one_drawing_wearing_two_labels():
    """They are the same 50 ml object, so they must be the same drawing.

    The pricing cards sit side by side and the eye compares them before it
    reads either. Any difference in the artwork — a longer bottle, a fatter
    cap, a different tilt — is read as a difference in the product, and the
    only real difference is what is printed on the label. Sharing `bottle()`
    is what makes that true today; this is what keeps it true after someone
    tunes one tier's drawing and not the other's.
    """
    def skeleton(tier: str) -> str:
        body = re.sub(r'<g transform="translate\(0,[\d.]+\) rotate\(-90\)"'
                      r'.*?</g>', "", _svg(tier), flags=re.S)
        return body.replace(tier, "TIER")

    assert skeleton("standard") == skeleton("plus"), (
        "the Standard and Plus bottles are drawn differently below the label")


def test_the_label_only_says_what_the_page_already_says():
    """A drawing is a claim. This one may only repeat the page's own.

    The bottle it replaced was nearly `printstick/hero-render.webp`, whose
    label reads "100 ML" against a page that sells 50 ml — a wrong fact, small
    enough to miss and large enough to be a lie. Now that the label is drawn
    here rather than photographed, that class of mistake is one careless
    edit away in either direction, so both directions are pinned: the volume
    against the price line, the materials against the tier's own copy.
    """
    page = json.loads(COPY.read_text(encoding="utf-8"))
    for tier in _section(page, kind="pricing")["tiers"]:
        which = "plus" if "Plus" in tier["name"] else "standard"
        printed, name, mats, volume = _label(which)
        assert printed == "PRINTSTICK"
        assert name.title() in tier["name"], (
            f"the {which} bottle is labelled {name}")
        assert volume.lower() in tier["unit"].lower(), (
            f"the {which} bottle is drawn as {volume} but priced "
            f"{tier['unit']}")
        said = " ".join([tier["desc"], *tier["features"]]).lower()
        for material in mats.split(" · "):
            assert material.lower() in said, (
                f"the {which} bottle is labelled for {material}, which its "
                f"own card never claims")


def test_the_drawn_proportions_still_match_the_photograph():
    """The drawing is measured off the product, not remembered.

    `printstick_tiers.py` carries the bottle as a handful of percentages, and a
    handful of percentages is exactly the kind of thing that gets nudged to
    make a composition sit better. Re-measured here from the alpha silhouette
    of the real photograph, so a nudge has to be a deliberate one.
    """
    from PIL import Image
    art = _load("printstick_tiers")
    photo = SITE / "assets" / ".imgsrc" / "printstick-standard-cut.png"
    with Image.open(photo) as im:
        im = im.convert("RGBA").crop(im.getchannel("A").getbbox())
        w, h = im.size
        alpha, rgb = im.getchannel("A").load(), im.convert("RGB").load()

    def rows(hit, floor):
        out = []
        for y in range(h):
            xs = [x for x in range(w) if alpha[x, y] > 128]
            if xs and sum(1 for x in xs
                          if hit(*rgb[x, y])) / len(xs) > floor:
                out.append(y)
        return out

    def longest_run(ys):
        """The printed body, not the stray dark rows at either end."""
        runs, run = [], [ys[0]]
        for y in ys[1:]:
            if y == run[-1] + 1:
                run.append(y)
            else:
                runs.append(run)
                run = [y]
        runs.append(run)
        return max(runs, key=len)

    band = rows(lambda r, g, b: r > 150 and r - g > 60 and r - b > 60, .55)
    body = longest_run(rows(lambda r, g, b: (r + g + b) / 3 < 110, .5))
    for name, measured in (("Y_BAND", band[0]),        # red band starts
                           ("Y_BODY", band[-1] + 1),   # dark body starts
                           ("Y_FOOT", body[-1] + 1)):  # translucent foot
        drawn = getattr(art, name) / art.LENGTH * 100
        assert abs(drawn - measured / h * 100) < 1.5, (
            f"{name} is drawn at {drawn:.1f}% of the bottle, but the "
            f"photograph puts it at {measured / h * 100:.1f}%")


# ------------------------------------------------------- what is in the bottle

def test_the_page_does_not_contradict_itself_about_the_formula(page):
    """Owner-confirmed 2026-08-25: solvent-CARRIED, water-cleanable.

    Both halves are true and the page has to tell them as one fact. The failure
    this pins is the old "No solvents" card sitting six inches from a
    "Solvent-Based Polymer Formula" card.
    """
    blob = json.dumps(page, ensure_ascii=False).lower()
    assert "no solvents" not in blob, (
        "the page claims 'no solvents' somewhere and also sells a "
        "solvent-carried formula")
    assert "solvent-carried" in blob, (
        "the solvent-carrier claim has gone missing — the water-cleanup copy "
        "then reads as the whole story, which it is not")
