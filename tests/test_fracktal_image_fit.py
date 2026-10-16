"""How a picture meets its frame — the defect the build gate cannot see.

Two kinds of picture live on the Fracktal site and they want opposite handling.
A picture that must be read *whole* — a product render, a partner's logo — is
contained, never cropped and never blown up past its own pixels. A photograph
must *fill* its frame, because a contained photograph paints its own backdrop
as a rectangle floating inside the card: a white-ground shot reads as
letterboxing, a black-ground shot as a hole punched in the card.

Both were shipped. `cardstyle: "light"` was written for the transparent printer
renders and then applied to sections full of photographs, so 397 photographs
rendered contained on a dotted panel meant for cutouts. The correction then
overshot: five partner logos are opaque PNGs on a white plate, so keying the
decision off alpha alone cropped three company names in half.

Nothing in `build.py` or `verify.py` can catch either. The data is valid, every
link resolves, the page does not overflow, and every image loads. The evidence
is in the alpha channel of the file and in the class the renderer puts on the
tag — which is what these check.

`imgfit.py` is the full tool (it also stamps the flag and repairs declared
sizes); this is the part CI can run in a second, plus the wiring that decides
fit, which is where the two defects above actually lived.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "fracktal-site" / "site"

pytestmark = pytest.mark.skipif(
    not (SITE / "chrome.py").exists() or not (SITE / "imgfit.py").exists(),
    reason="fracktal site not in this checkout")


def _load(name: str):
    """Import one of this site's modules under a name of its own.

    Every generated site carries its own `chrome.py`, so importing this one as
    plain `chrome` would put it in `sys.modules` and hand it to whichever test
    imports `chrome` next — which is exactly what happened, and it failed three
    tests in `test_site_engine.py` that had nothing to do with this file.

    These are standalone scripts sitting beside each other, and a couple of
    them import a sibling by bare name — `menutiles` imports `imghalo` so the
    two cannot end up disagreeing about what a pale wash is. That resolves when
    the script is run, because its own directory is on the path, and does not
    when it is loaded by file location; the fixture then skipped instead of
    failing, which is worse than red. So the directory goes on the path for the
    exec and comes straight back off: leaving it there put this site's
    `resolver` in front of the drvarada one and broke three URL tests in
    `test_site_engine.py` — the same collision the paragraph above describes,
    by the other route.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"fracktal_{name}",
                                                  SITE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    sys.path.insert(0, str(SITE))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(SITE))
    return mod


@pytest.fixture(scope="module")
def imgfit():
    try:
        return _load("imgfit")
    except ImportError as exc:                      # Pillow missing
        pytest.skip(f"imgfit unavailable: {exc}")


@pytest.fixture(scope="module")
def chrome():
    return _load("chrome")


def images():
    """Every placed picture in the page data, with where it came from."""
    for f in sorted(SITE.glob("content/*-copy.json")) + \
            [SITE / "content" / "nav.json"]:
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        stack = [data]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                if isinstance(n.get("src"), str):
                    yield f.name, n
                stack.extend(n.values())
            elif isinstance(n, list):
                stack.extend(n)


# ── the flag against the file ────────────────────────────────────────────────
def test_every_src_has_a_file():
    missing = [(f, d["src"]) for f, d in images()
               if not d["src"].startswith("http")
               and not (SITE / "assets" / "img" / d["src"]).exists()]
    assert not missing, f"{len(missing)} image(s) with no file: {missing[:6]}"


def test_cutout_flag_matches_the_alpha_channel(imgfit):
    """The flag is a claim about the file. Swap the file, the claim must fail."""
    wrong = []
    seen = {}
    for f, d in images():
        src = d["src"]
        if src.startswith("http"):
            continue
        fp = SITE / "assets" / "img" / src
        if src not in seen:
            seen[src] = imgfit.is_cutout(fp)
        if bool(d.get("cutout")) != seen[src]:
            wrong.append((f, src, "flagged" if d.get("cutout") else "not flagged",
                          "transparent" if seen[src] else "opaque"))
    assert not wrong, (f"{len(wrong)} image(s) disagree with their file "
                       f"(run `python imgfit.py --fix`): {wrong[:6]}")


def test_declared_size_matches_the_file(imgfit):
    """`width`/`height` are the intrinsic size; a wrong ratio squashes the
    picture wherever the stylesheet does not pin both axes."""
    from PIL import Image
    wrong, size = [], {}
    for f, d in images():
        src, dw, dh = d["src"], d.get("width"), d.get("height")
        if src.startswith("http") or not (dw and dh):
            continue
        if src not in size:
            with Image.open(SITE / "assets" / "img" / src) as im:
                size[src] = im.size
        rw, rh = size[src]
        if abs(dw / dh - rw / rh) / (rw / rh) > 0.02:
            wrong.append((f, src, f"declared {dw}x{dh}", f"real {rw}x{rh}"))
    assert not wrong, f"{len(wrong)} squashed: {wrong[:6]}"


# ── the rule that turns the flag into a fit ──────────────────────────────────
def test_contained_prefers_the_explicit_fit_over_the_alpha(chrome):
    """A logo delivered opaque on a white plate is still a mark, not a
    photograph — which is the case that cropped three company names in half."""
    assert chrome.contained({"src": "x.png", "cutout": True})
    assert not chrome.contained({"src": "x.jpg"})
    # `fit` wins in both directions.
    assert chrome.contained({"src": "x.png", "fit": "contain"})
    assert not chrome.contained({"src": "x.png", "cutout": True, "fit": "cover"})


def test_img_marks_a_contained_picture_and_leaves_a_photograph_alone(chrome):
    mark = chrome.img({"src": "a.png", "alt": "a", "cutout": True}, "preview")
    photo = chrome.img({"src": "b.jpg", "alt": "b"}, "preview")
    assert "is-contained" in mark
    assert "is-contained" not in photo


def test_img_keeps_the_caller_class_when_adding_its_own(chrome):
    """`.mat-img` and friends carry the layout; dropping one on a cutout would
    silently unstyle the card."""
    out = chrome.img({"src": "a.png", "alt": "a", "cutout": True}, "preview",
                     "mat-img")
    assert 'class="mat-img is-contained"' in out


def test_a_row_of_photographs_is_not_framed_as_a_row_of_renders(chrome):
    """`products-photo` swaps the cutout square for the aspect the photographs
    are actually shot at — but only when no card needs the square."""
    photos = {"kind": "products", "cardstyle": "light",
              "cards": [{"tag": "t", "title": "T", "body": "b",
                         "image": {"src": "a.jpg", "alt": "a"}}]}
    mixed = {"kind": "products", "cardstyle": "light",
             "cards": [{"tag": "t", "title": "T", "body": "b",
                        "image": {"src": "a.jpg", "alt": "a"}},
                       {"tag": "t", "title": "U", "body": "b",
                        "image": {"src": "b.png", "alt": "b", "cutout": True}}]}
    assert "products-photo" in chrome.blk_products(photos, "preview")
    assert "products-photo" not in chrome.blk_products(mixed, "preview")


# ── the stylesheet has to agree with the class ───────────────────────────────
def test_the_stylesheet_still_distinguishes_the_two_fits():
    """The class is only worth emitting if something styles it."""
    css = (SITE / "assets" / "landing.css").read_text(encoding="utf-8")
    assert ".products-light .thumb img{object-fit:cover" in css, \
        "photographs must fill the light product thumb"
    assert ".products-light .thumb img.is-contained{object-fit:scale-down" in css, \
        "a mark must be shown whole and never blown up past its own pixels"
    assert ".products-photo .product-card .thumb" in css


def test_outline_buttons_borrow_the_band_colour_instead_of_hardcoding_white():
    """`.btn-outline` was `color:#fff`: right on a dark band, white-on-white on
    every light one — 107 buttons across the site rendered as empty rectangles.
    Taking `inherit`/`currentColor` makes that impossible, because the band's
    own text colour is by definition readable on that band."""
    for name in ("landing.css", "home.css"):
        css = (SITE / "assets" / name).read_text(encoding="utf-8")
        rule = css[css.index(".btn-outline{"):]
        rule = rule[:rule.index("}") + 1]
        assert "color:inherit" in rule, f"{name}: .btn-outline must inherit"
        assert "currentColor" in rule, f"{name}: border must be currentColor"
        assert "#fff" not in rule, f"{name}: .btn-outline still hard-codes white"


def test_a_dark_surface_declares_its_text_colour():
    """An outline button inside a dark card takes the colour it inherits. If
    the card only sets a dark `background` and no `color`, that is the
    *section's* ink — which on a light band is dark text on a dark card, and is
    exactly what the first fix caused on 463 card buttons."""
    import re
    for name, selectors in (
            ("landing.css", (".pillar-card", ".product-card", ".feature-card",
                             ".cta-band", ".software-strip")),
            ("home.css", (".ocard",))):
        css = (SITE / "assets" / name).read_text(encoding="utf-8")
        for sel in selectors:
            m = re.search(re.escape(sel) + r"\{([^{}]*)\}", css)
            assert m, f"{name}: {sel} not found"
            body = m.group(1)
            assert "color:" in body.replace("background-color", ""), \
                f"{name}: {sel} paints a dark background and sets no text colour"


def test_the_class_is_defined_on_every_page_not_just_the_landing_one():
    """Each page loads only its own stylesheet (rule 1), so a class defined in
    `landing.css` alone means nothing on the home template — which is how the
    home page ended up emitting `is-contained` with no rule behind it."""
    chrome_css = (SITE / "assets" / "chrome.css").read_text(encoding="utf-8")
    assert ".is-contained" in chrome_css, (
        "chrome.css is the only sheet every page loads; the fit class has to "
        "be defined there or it is unstyled outside the landing template")


# ── the hero: the same two kinds of picture, one band apart ──────────────────
def _hero(src: str, **flags) -> dict:
    return {"kind": "hero2", "eyebrow": "E", "h1": "H", "body": "B",
            "image": {"src": src, "alt": "a", **flags}}


def test_the_headline_comes_before_the_picture_in_the_hero(chrome):
    """Source order is reading order — for a screen reader, for a crawler, and
    for a phone, where the picture used to occupy the whole first screen and
    the h1 only appeared once you scrolled past it."""
    out = chrome.blk_hero2(_hero("julia/julia-hero.webp", cutout=True), "preview")
    assert out.index("<h1") < out.index("hero-image"), \
        "the picture is back in front of the headline"


def test_a_wide_cutout_hero_keeps_the_full_width(chrome):
    """The seven-machine range shot is 2.57:1. In a 45% column each printer
    renders about 60px wide, so a wide cutout stays a banner. Nothing else
    does: a 16:9 photograph is happy in the column, and so is a square render."""
    wide = chrome.blk_hero2(_hero("printers/family.webp", cutout=True), "preview")
    square = chrome.blk_hero2(_hero("julia/julia-hero.webp", cutout=True), "preview")
    photo = chrome.blk_hero2(_hero("services/fdm.jpg"), "preview")
    assert "hero-inner--banner" in wide
    assert "hero-inner--banner" not in square
    assert "hero-inner--banner" not in photo, \
        "a photograph fills its frame; it never needs the banner escape hatch"


def test_a_cutout_hero_carries_the_ink_box_its_file_actually_has(chrome):
    """The contact shadow is placed off these three numbers. Measured, not
    declared — `julia-hero.webp` is a square whose printer stopped 20% short of
    the bottom edge, and a shadow pinned to the box landed on nothing."""
    box = chrome.ink_box({"src": "printers/apollo-front.webp"})
    assert box is not None
    left, right, bottom = box
    assert 0 <= left < right <= 1 and 0 < bottom <= 1
    out = chrome.blk_hero2(_hero("printers/apollo-front.webp", cutout=True),
                           "preview")
    assert "is-cutout" in out and f"--ink-b:{bottom}" in out
    # A photograph has no ink box: it fills its frame, so its own edge is the
    # frame's edge and there is nothing to cast a shadow.
    photo = chrome.blk_hero2(_hero("services/fdm.jpg"), "preview")
    assert "is-cutout" not in photo and "--ink-b" not in photo


def test_the_shadow_is_positioned_off_the_measured_ink_box():
    """Emitting the numbers is only half of it — the stylesheet has to read
    them, or the shadow silently falls back to the file's edge again."""
    css = (SITE / "assets" / "landing.css").read_text(encoding="utf-8")
    rule = css[css.index(".hero-image.is-cutout::after{"):]
    rule = rule[:rule.index("}") + 1]
    for var in ("--ink-l", "--ink-r", "--ink-b"):
        assert var in rule, f"the contact shadow ignores {var}"


def test_a_hero_cutout_is_not_mostly_empty_file(chrome):
    """A transparent margin is part of the file, and `contain`/`max-height`
    size a picture by its file. `julia-hero.webp` was a 900px square holding a
    603px printer: every box reserved the full square and painted the machine
    at 67% of it, and the waste was invisible in the file, the markup and the
    CSS alike. `python imgtrim.py` reports and cuts it."""
    import numpy as np
    from PIL import Image
    fat = []
    for f in sorted(SITE.glob("content/*-copy.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        first = (data.get("sections") or [{}])[0]
        img = first.get("image") or {}
        if first.get("kind") != "hero2" or not img.get("cutout"):
            continue
        with Image.open(SITE / "assets" / "img" / img["src"]) as im:
            a = np.array(im.convert("RGBA"))[:, :, 3]
        ys, xs = np.where(a > 8)
        h, w = a.shape
        idle = 1 - ((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)) / (w * h)
        if idle > 0.20:
            fat.append((img["src"], f"{idle:.0%} idle"))
    assert not fat, f"hero cutouts carrying dead margin: {fat}"


# ── the panel answers to the picture ────────────────────────────────────────
def test_a_pale_cutout_gets_a_panel_it_can_be_seen_against(chrome):
    """A cutout has no background of its own, so the thumb IS its background.
    `#eef1f5` is right behind a black machine and wrong behind a white vase,
    where subject and panel dissolve into each other."""
    dark = {"kind": "products", "cardstyle": "light",
            "cards": [{"tag": "t", "title": "T", "body": "b",
                       "image": {"src": "julia/julia-hero.webp", "alt": "a",
                                 "cutout": True}}]}
    pale = {"kind": "products", "cardstyle": "light",
            "cards": [{"tag": "t", "title": "T", "body": "b",
                       "image": {"src": "snowflake/nozzle-render.webp",
                                 "alt": "a", "cutout": True}}]}
    assert "thumb--pale-subject" not in chrome.blk_products(dark, "preview")
    assert "thumb--pale-subject" in chrome.blk_products(pale, "preview")


def test_a_photograph_is_never_asked_how_light_it_is(chrome):
    """It covers the panel, so the panel behind it is irrelevant — and reading
    the luminance of a photograph would swap the ground for no reason."""
    photo = {"kind": "products", "cardstyle": "light",
             "cards": [{"tag": "t", "title": "T", "body": "b",
                        "image": {"src": "services/fdm.jpg", "alt": "a"}}]}
    assert "thumb--pale-subject" not in chrome.blk_products(photo, "preview")


def test_the_pale_panel_is_actually_styled():
    css = (SITE / "assets" / "landing.css").read_text(encoding="utf-8")
    assert ".products-light .thumb--pale-subject{" in css


def test_ink_luma_reads_only_the_subject(chrome):
    """Alpha-gated: a soft shadow's transparent fringe must not drag the mean
    down and send a white object to the wrong panel."""
    assert chrome.ink_luma({"src": "dryer/dryer-hero.webp"}) < chrome.LIGHT_SUBJECT
    assert chrome.ink_luma({"src": "snowflake/nozzle-render.webp"}) >= chrome.LIGHT_SUBJECT
    assert chrome.ink_luma({"src": "services/fdm.jpg"}) is None   # no alpha


# ── the background a cutout is not entitled to have ─────────────────────────
@pytest.fixture(scope="module")
def imghalo():
    try:
        return _load("imghalo")
    except ImportError as exc:                          # Pillow / numpy missing
        pytest.skip(f"imghalo unavailable: {exc}")


def _placed_cutouts():
    """Every distinct transparent file the page data actually places."""
    out = {}
    for f, d in images():
        src = d["src"]
        if not src.startswith("http") and d.get("cutout"):
            out.setdefault(src, f)
    return out


def test_no_placed_cutout_carries_a_pale_wash(imghalo):
    """A cutout has no background of its own — whatever it is placed on IS its
    background. `snowflake/nozzle-render.webp` kept a near-white cloud at 53%
    opacity from an imperfect background removal. It was invisible on the pale
    product panel, so it survived; then `ink_luma` counted the cloud as part of
    the subject, called the picture too light for that panel and moved the card
    to the DARK one, where the cloud painted a grey smear the size of the card.

    Pale, not dark: an off-subject dark pixel is a contact shadow and is
    wanted. `python imghalo.py` reports both and clears only the pale.
    """
    dirty = []
    for src in sorted(_placed_cutouts()):
        if src in imghalo.KEEP:
            continue
        m = imghalo.measure(SITE / "assets" / "img" / src)
        if m and m["pale"] >= imghalo.SHOWS:
            dirty.append((src, f"{m['pale']:.1%} of the frame"))
    assert not dirty, (f"{len(dirty)} cutout(s) still carry a pale background "
                       f"(run `python imghalo.py --apply`): {dirty[:6]}")


@pytest.mark.parametrize("src", [
    "snowflake/printer-blue.webp",       # floor shadow under a desktop machine
    "snowflake/heated-bed-flame.png",   # shadow under the bed
    "dryer/dryer-hero.webp",            # shadow under the dryer
    "home/svc-vacuum.png",              # the darkest shadow on the site
])
def test_clearing_the_wash_leaves_the_contact_shadows_alone(imghalo, src):
    """The one-directional rule is the whole safety argument: pale goes, dark
    stays. These four are the shadows that stop a render floating, and a
    threshold that started deleting them would look like a tidier picture right
    up until every machine on the site was hovering."""
    m = imghalo.measure(SITE / "assets" / "img" / src)
    assert m is not None
    assert m["wash"] > 0.02, f"{src} has no shadow left to protect"
    assert m["pale"] < imghalo.SHOWS, (
        f"{src}: the pale line has drifted down into a real shadow "
        f"({m['pale']:.1%} of the frame would be cleared)")


# ── the header's picture tiles ───────────────────────────────────────────────
@pytest.fixture(scope="module")
def menutiles():
    try:
        return _load("menutiles")
    except ImportError as exc:                          # Pillow / numpy missing
        pytest.skip(f"menutiles unavailable: {exc}")


def test_every_generated_tile_is_the_frame_size(menutiles):
    """A tile off the frame is a tile the browser has to crop or letterbox,
    which is the whole defect these were made to end."""
    from PIL import Image
    wrong = []
    for name in menutiles.TILES:
        p = SITE / "assets" / "img" / name
        if not p.exists():
            wrong.append((name, "missing — run `python menutiles.py --apply`"))
            continue
        with Image.open(p) as im:
            if im.size != menutiles.FRAME:
                wrong.append((name, f"{im.size} != {menutiles.FRAME}"))
    assert not wrong, wrong


def test_the_swatch_tiles_are_contained_rather_than_cropped():
    """Twelve 240x240 hand-crops in a 4:3 `cover` frame were cropped twice: the
    hand-crop cut the vase and the spool at the edges, and the browser then
    took another 12.5% off the top and the bottom. The reader is being asked
    which material this is; the middle of a spool does not answer that."""
    css = (SITE / "assets" / "chrome.css").read_text(encoding="utf-8")
    assert ".fw-mega__grid--swatches .fw-tile__pic img" in css, \
        "the swatch tiles inherit `object-fit: cover` and get cropped"
    rule = css[css.index(".fw-mega__grid--swatches .fw-tile__pic img"):]
    rule = rule[:rule.index("}") + 1]
    assert "object-fit: contain" in rule


def test_no_picture_is_used_twice_inside_one_menu():
    """Careers and For education sat side by side in the Resources panel with
    the same photograph, under two different alt texts — one of which described
    a picture that is not in the file."""
    import collections
    nav = json.loads((SITE / "content" / "nav.json").read_text(encoding="utf-8"))
    dupes = {}
    for m in nav["menu"]:
        seen = collections.defaultdict(list)
        for g in (m.get("groups") or [{"items": m.get("items", [])}]):
            for it in g["items"]:
                src = (it.get("image") or {}).get("src")
                if src:
                    seen[src].append(it.get("label"))
        for src, where in seen.items():
            if len(where) > 1:
                dupes[f'{m["label"]}: {src}'] = where
    assert not dupes, dupes


def test_the_build_ships_images_and_not_what_they_were_made_from():
    """`assets/.imgsrc/` is input. The build tree is meant to be output.

    It holds the photograph a cutout was traced off, the SVG a WebP was
    rendered from, and the 37 kB font that SVG embeds — each one larger than
    the asset it produced, and none of them fetched by any page. `copytree`
    took the whole of `assets/` and so took these too, for as long as the
    folder has existed.

    Nothing failed, which is the point: `pushassets.py` uploads only what
    `dist-prod/` actually references, so none of it ever reached the server and
    no gate had reason to complain. It was invisible until the folder grew a
    font. A build tree you could not upload as-is is a build tree that has
    stopped being one.
    """
    for tree in ("dist", "dist-prod"):
        out = SITE / tree / "assets"
        if not out.exists():                       # not built in this checkout
            continue
        leaked = [str(p.relative_to(out)) for p in out.rglob("*")
                  if p.is_file() and ".imgsrc" in p.parts]
        assert not leaked, f"{tree}/ ships build sources: {leaked[:5]}"
