"""Copy that reads as machine-written, held down by CI.

Every other gate on this site checks that the pages *work*. None of them can
tell whether the prose sounds like a person wrote it, and the corpus proved
that gap is real: 5,018 prose strings carrying 1,036 em-dashes — one every 66
words, against nearer one in 500 for edited prose — and 155 findings across 73
of the 96 pages.

The tell was never a banned word. It was RHYTHM: five printer blurbs built to
one skeleton, `<noun phrase> — <spec list>`, repeated across eight pages each;
seventy-two material property cards all reading `<fact> — <implication>`;
eighteen product-card bodies in a row ending in ` — <benefit fragment>`. Each
sentence is defensible alone. The uniformity is what gives it away, and only a
check that compares SIBLINGS can see it.

`slop.py` is that check. These tests keep three things true:

  1. the audit reports nothing, so a regression fails CI rather than shipping;
  2. the audit can still FAIL — a gate that cannot fire is not a gate, so the
     detector is fed known-bad copy and must find it;
  3. the suppression lists stay honest. `NOT_OURS` and `JUDGED_FINE` are the
     only way to silence a finding, they are matched on distinctive fragments,
     and a fragment that no longer appears anywhere on the site is dead weight
     that would silence some future string nobody has read.

Point 3 is the one that rots quietly. A suppression list is how a linter turns
into a rubber stamp, one convenient entry at a time.
"""
from __future__ import annotations

import glob
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "outputs" / "fracktal-site" / "site"

pytestmark = pytest.mark.skipif(
    not (SITE / "slop.py").exists(),
    reason="fracktal site not in this checkout")


def _slop():
    spec = importlib.util.spec_from_file_location("fracktal_slop",
                                                  SITE / "slop.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _pages() -> dict[str, dict]:
    return {Path(f).name.replace("-copy.json", ""):
            json.loads(Path(f).read_text(encoding="utf-8"))
            for f in sorted(glob.glob(str(SITE / "content" / "*-copy.json")))}


def test_no_findings():
    """The whole corpus is clean."""
    slop = _slop()
    bad = {slug: audit for slug, doc in _pages().items()
           if (audit := slop.audit(slug, doc))}
    assert not bad, "\n".join(
        f"{slug}: {kind} — {items[0][:100]}"
        for slug, audit in bad.items() for kind, items in audit.items())


def test_rhythm_still_fires():
    """Feed it the shape it exists to catch. If this passes, it is broken."""
    slop = _slop()
    templated = {"cards": [
        {"body": "The reliable desktop printer — quality parts up to 280 "
                 "degrees."},
        {"body": "Professional desktop printing for labs — sixty micron "
                 "layer resolution."},
        {"body": "Independent dual extrusion for production — two colour "
                 "and dual material."},
    ]}
    found = slop.audit("fixture", templated)
    assert found.get("RHYTHM"), "three siblings on one skeleton went unnoticed"


def test_density_still_fires():
    """A page over the dash budget is reported, not rounded away."""
    slop = _slop()
    line = ("The machine is fast — and accurate — which matters when the "
            "part is large — and the material is expensive. ")
    found = slop.audit("fixture", {"body": [line * 12]})
    assert found.get("DENSITY"), "an em-dash every eleven words passed"


def test_phrase_still_fires():
    slop = _slop()
    found = slop.audit("fixture", {"lede":
                                   "A state-of-the-art solution, world-class "
                                   "in every respect, built to last."})
    assert len(found.get("PHRASE", [])) >= 2


@pytest.mark.parametrize("name", ["NOT_OURS", "JUDGED_FINE"])
def test_every_suppression_is_still_load_bearing(name):
    """A suppression for text that no longer exists silences the next string.

    These lists are matched on a fragment, not on a whole page. Leave a stale
    entry in and it goes on matching — against copy written months later that
    nobody looked at, which is exactly the string a gate exists to catch.
    """
    slop = _slop()
    corpus = "\n".join(
        s for doc in _pages().values() for _, s in slop.texts(doc))
    dead = [x for x in getattr(slop, name)
            if x.lower() not in corpus.lower()]
    assert not dead, (
        f"{name} suppresses text that is no longer on the site: {dead}. "
        f"Delete the entry rather than leaving it to match something else.")


def test_suppressions_are_specific():
    """A short fragment is a wildcard wearing a suppression's clothes."""
    slop = _slop()
    vague = [x for x in slop.NOT_OURS + slop.JUDGED_FINE if len(x) < 15]
    assert not vague, f"too broad to be a suppression: {vague}"
