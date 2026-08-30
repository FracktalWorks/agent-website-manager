"""Gates for drvarada's patient-review corpus and the proof band it feeds.

WHAT CAN GO WRONG HERE THAT NOTHING ELSE CATCHES
  The reviews are reproductions of text on someone else's platform. `build.py`
  will happily ship a quote that has been "tidied up", a tag nobody matches, or
  a page whose band silently fell back to a review about a different condition.
  None of that is a render error and none of it fails the advertising linter —
  it just makes the site's most load-bearing evidence quietly untrue.

  So these check the things a human reading a diff would not notice: that every
  page named in `PROOF_TAGS` still exists, that every tag still selects
  something, and that the band actually reached the page.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1] / "outputs" / "drvarada-site" / "site"
pytestmark = pytest.mark.skipif(not SITE.is_dir(), reason="drvarada site absent")


@pytest.fixture(scope="module")
def site():
    """Import the site's own modules with its directory on the path.

    Restored afterwards so a later test file that imports a different site's
    `chrome` does not get this one out of `sys.modules`.
    """
    before = dict(sys.modules)
    sys.path.insert(0, str(SITE))
    try:
        import siteconf
        proof = importlib.import_module("content.proof")
        pages = {}
        for name in siteconf.MODULES:
            for page in importlib.import_module(f"content.{name}").PAGES:
                pages[page["slug"]] = page
        yield proof, pages
    finally:
        sys.path.remove(str(SITE))
        for k in set(sys.modules) - set(before):
            del sys.modules[k]
        sys.modules.update(before)


def test_every_review_is_complete(site):
    proof, _ = site
    for r in proof.REVIEWS_CORPUS:
        assert r["id"] and r["text"].strip() and r["who"].strip(), r
        assert r["src"] in proof.SOURCE_LABEL, r["id"]
        assert r["tags"], f"{r['id']} carries no tag, so no page can find it"


def test_no_review_reproduces_a_claim_the_site_may_not_make(site):
    """The advertising linter reads rendered pages; this reads the corpus.

    Both figures below sat in real, otherwise-excellent reviews and were
    trimmed out: an unverifiable purity grade, and a quantified outcome about
    a patient the reviewer had never met. A future editor restoring "the full
    quote" would be restoring exactly those.
    """
    import re
    banned = [(re.compile(r"\d{2,3}(\.\d+)?\s*%?\s*(pure|purity)", re.I),
               "purity grade"),
              (re.compile(r"\d{1,3}\s*%\s*\w*\s*(repigmentation|clearance|cure|"
                          r"success|results?)", re.I), "quantified outcome"),
              (re.compile(r"\b99\.9\b"), "invented metric")]
    for r in site[0].REVIEWS_CORPUS:
        for pattern, why in banned:
            assert not pattern.search(r["text"]), f"{r['id']}: {why} restored"


def test_every_mapped_page_exists(site):
    """A slug renamed in `urls.py` and not here loses its band with no error."""
    proof, pages = site
    unknown = sorted(set(proof.PROOF_TAGS) - set(pages))
    assert not unknown, f"PROOF_TAGS names pages that do not exist: {unknown}"


def test_every_tag_selects_at_least_one_review(site):
    """A typo'd tag would raise at import; a tag whose only review is later
    deleted would not, so it is checked here as well as there."""
    proof, _ = site
    for slug, spec in proof.PROOF_TAGS.items():
        tags = tuple(t for t in spec if not t.startswith("first:"))
        assert proof.stories(*tags), f"{slug}: no review matches {tags}"


def test_pinned_lead_reviews_still_exist(site):
    proof, _ = site
    ids = {r["id"] for r in proof.REVIEWS_CORPUS}
    for slug, spec in proof.PROOF_TAGS.items():
        for entry in spec:
            if entry.startswith("first:"):
                assert entry.split(":", 1)[1] in ids, f"{slug} pins a dead id"


def test_the_band_actually_reached_the_page(site):
    """`attach()` runs at import. If a module loses its call, its pages simply
    lose their social proof — the build stays green and the site gets quietly
    worse, which is the failure this whole change existed to end.
    """
    proof, pages = site
    missing = [s for s in proof.PROOF_TAGS
               if not any(x["kind"] == "proof" for x in pages[s]["sections"])]
    assert not missing, f"proof band never attached to: {missing}"


def test_the_band_is_never_the_first_thing_on_a_page(site):
    """A leading callout is a red flag — "go to hospital today" on the
    skin-allergy page — and `chrome.render_body` folds furniture into the band
    BELOW it. A proof band inserted at index 0 would swallow that warning into
    a box of testimonials.
    """
    _, pages = site
    for slug, page in pages.items():
        for i, section in enumerate(page["sections"]):
            if section["kind"] == "proof":
                assert i > 0, f"{slug}: proof band is the first section"


def test_pages_that_must_not_carry_a_band_do_not(site):
    """The four language pages are the live ones: the corpus is English, and a
    Telugu page that switches language mid-scroll breaks its only promise."""
    proof, pages = site
    for slug in ("te-vitiligo", "te-psoriasis", "hi-vitiligo", "hi-psoriasis",
                 "index", "patient-stories", "about-dr-khagendra-varada", "blog"):
        assert slug not in proof.PROOF_TAGS
        assert not any(x["kind"] == "proof" for x in pages[slug]["sections"]), slug


def test_scores_are_shown_for_both_platforms(site):
    """Publishing only the higher of two public scores is the thing this site
    says, on the page, that it does not do."""
    sys.path.insert(0, str(SITE))
    try:
        chrome = importlib.import_module("chrome")
        strip = chrome.score_strip()
    finally:
        sys.path.remove(str(SITE))
    for value in (chrome.RATING, chrome.REVIEWS,
                  chrome.GOOGLE_RATING, chrome.GOOGLE_COUNT):
        assert value in strip
    assert chrome.PRACTO_REVIEWS in strip and chrome.GOOGLE_REVIEWS in strip
