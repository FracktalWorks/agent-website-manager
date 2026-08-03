#!/usr/bin/env python
"""Check what each diagram label is actually pointing AT, in the artwork itself.

    python diagram_anchors.py              # report every anchor, worst first
    python diagram_anchors.py --class-map E1-examination   # see the segmentation

WHY THIS EXISTS, AND WHY IT IS NOT diagram_audit.py
  `diagram_audit.py` proves a ring RENDERS at the (x, y) it was authored with —
  that no transform, border or container displaced it. It is a rendering check,
  and it passes every label on the site today.

  It cannot see the defect that matters: whether that authored (x, y) is on the
  structure the label names. "The dermatoscope" at (33, 41) rendered pixel-exact
  and pointed at empty background, because the device is at y≈51. Both tools are
  needed; this is the one that looks at the picture.

HOW IT WORKS, AND WHY THERE IS NO MODEL IN IT
  The illustrations are drawn to a controlled palette (see DIAGRAMS.md), so the
  structures are separable by colour alone:

      stage   the #F8F5F3 field the artwork sits on — nothing is ever on it
      ink     outlines and hair, near-black
      glass   the cyan-green lens of an instrument
      metal   achromatic mid-value: instruments, steel
      pale    warm but desaturated — depigmented skin, a vitiligo patch
      skin    warm and saturated — normal pigmented skin
      fabric  the muted rose of a clinician's sleeve

  Classification is a fixed set of HSV thresholds. No detector, no model, no
  asking a language model where the dermatoscope is — that guess is exactly what
  put the ring in the background in the first place.

  The one judgement a human still makes is WHICH class a label should sit on,
  declared per label as `find`. That is a semantic question about the caption,
  not a coordinate, and it is the part a person should own. Everything after it
  — locating the region, choosing a robust point inside it — is arithmetic.

THE RULE THIS ENFORCES
  An anchor sitting mostly on `stage` is pointing at nothing and is wrong —
  EXCEPT in row mode, where being on the stage is the entire design.

  Row mode (`label_col: 0`, `lead: 2`, every label sharing one `y`) puts its
  chips in a band the artwork deliberately left empty beneath a left-to-right
  sequence; DIAGRAMS.md is explicit that "they cover nothing". Nine diagrams use
  it, and a naive stage test condemns all thirty-odd of their chips. Skipping
  them is not a loosened rule, it is the rule applied to the right mode: a row
  chip is a caption under a stage, not a pointer into the artwork.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ASSETS = Path(__file__).parent / "assets"

# The ring is small, but a label naming a thin structure (a hair, a border)
# needs a little tolerance or it would read as a miss whenever it sat one pixel
# off. 1.2% of the short side is about the ring's own footprint on the page.
PROBE_FRAC = 0.012


def classify(im: Image.Image) -> tuple[np.ndarray, dict[str, int]]:
    """Label every pixel with one of the palette classes.

    Order matters: `stage` and `ink` are tested first because they are defined
    by value alone and would otherwise be swallowed by the chromatic tests.
    """
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2)
    V = mx
    S = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    d = mx - mn + 1e-6
    Hh = np.select([mx == r, mx == g, mx == b],
                   [(60 * ((g - b) / d)) % 360,
                    60 * ((b - r) / d) + 120,
                    60 * ((r - g) / d) + 240], 0.0)

    out = np.full(V.shape, "other", dtype=object)
    warm = ((Hh < 48) | (Hh > 330)) & (S >= 0.08)
    out[warm] = "tissue"
    out[(S < 0.18) & (V >= 0.35) & (V <= 0.93)] = "metal"
    out[(Hh >= 120) & (Hh <= 200) & (S >= 0.12)] = "glass"
    out[(Hh >= 320) & (Hh <= 375) & (S >= 0.18) & (S < 0.45)] = "fabric"
    out[(S < 0.10) & (V > 0.93)] = "stage"
    out[V < 0.32] = "ink"

    # PALE vs PIGMENTED IS RELATIVE, NOT ABSOLUTE.
    #   A first version split them on a fixed saturation threshold and found
    #   almost no `pale` anywhere: a vitiligo patch is still warm and still
    #   fairly saturated (S≈0.40 here) — it is only pale *next to the arm it
    #   sits on* (S≈0.59). Any constant that separates them in one illustration
    #   is wrong in the next, because the two artworks are not lit alike.
    #
    #   So the threshold is derived per image, by Otsu over the saturation of
    #   the tissue pixels alone. That is the standard way to split a bimodal
    #   population and it needs no tuning. Where the histogram is NOT bimodal —
    #   an illustration of nothing but normal skin — Otsu would invent a split,
    #   so a weak separation is rejected and the tissue stays one class.
    tissue = out == "tissue"
    if tissue.sum() > 0.01 * V.size:
        thresh, strength = _otsu(S[tissue])
        if strength >= SPLIT_MIN:
            out[tissue & (S < thresh)] = "pale"
            out[tissue & (S >= thresh)] = "skin"
        else:
            out[tissue] = "skin"

    names, counts = np.unique(out.astype(str), return_counts=True)
    return out.astype(str), dict(zip(names, counts.tolist()))


# Between-class variance below which a saturation histogram is treated as one
# mode rather than two. Set from the diagrams that genuinely have no pale
# tissue in them at all; see the `--class-map` output when adjusting it.
SPLIT_MIN = 0.0016


def _otsu(vals: np.ndarray, bins: int = 64) -> tuple[float, float]:
    """Otsu's threshold, and how strongly the data actually supports it.

    The second return value is the maximised between-class variance. It is the
    part that matters here: it says whether there were two modes to separate,
    or whether the threshold is an artefact of forcing a split on one.
    """
    hist, _ = np.histogram(vals, bins=bins, range=(0.0, 1.0))
    p = hist / max(hist.sum(), 1)
    centres = (np.arange(bins) + 0.5) / bins
    w = p.cumsum()
    mu = (p * centres).cumsum()
    denom = w * (1 - w)
    sb = np.where(denom > 1e-9, (mu[-1] * w - mu) ** 2 / np.maximum(denom, 1e-9), 0)
    k = int(sb.argmax())
    return float(centres[k]), float(sb.max())


def probe(cls: np.ndarray, xp: float, yp: float) -> list[tuple[str, float]]:
    """The class mix under one anchor, as fractions, commonest first."""
    H, W = cls.shape
    x, y = int(round(xp / 100 * W)), int(round(yp / 100 * H))
    r = max(4, int(round(min(W, H) * PROBE_FRAC)))
    ys, xs = np.ogrid[-r:r + 1, -r:r + 1]
    disc = xs * xs + ys * ys <= r * r
    y0, y1 = max(0, y - r), min(H, y + r + 1)
    x0, x1 = max(0, x - r), min(W, x + r + 1)
    win = cls[y0:y1, x0:x1]
    m = disc[(y0 - (y - r)):(y0 - (y - r)) + win.shape[0],
             (x0 - (x - r)):(x0 - (x - r)) + win.shape[1]]
    vals = win[m]
    if vals.size == 0:
        return [("outside", 1.0)]
    names, counts = np.unique(vals, return_counts=True)
    mix = sorted(zip(names.tolist(), (counts / vals.size).tolist()),
                 key=lambda t: -t[1])
    return mix


def boxfrac(mask: np.ndarray, r: int) -> np.ndarray:
    """Fraction of `mask` that is True in a (2r+1) square around every pixel.

    An integral image, so this is O(pixels) rather than O(pixels x window) —
    which matters because the solver evaluates it over the whole 1820x1024
    frame for every candidate class.
    """
    ii = np.pad(mask.astype(np.float32), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    H, W = mask.shape
    ys, xs = np.arange(H), np.arange(W)
    y0, y1 = np.clip(ys - r, 0, H), np.clip(ys + r + 1, 0, H)
    x0, x1 = np.clip(xs - r, 0, W), np.clip(xs + r + 1, 0, W)
    tot = (ii[np.ix_(y1, x1)] - ii[np.ix_(y0, x1)]
           - ii[np.ix_(y1, x0)] + ii[np.ix_(y0, x0)])
    return tot / np.maximum((y1 - y0)[:, None] * (x1 - x0)[None, :], 1)


def qualify(cls: np.ndarray, spec: str, r: int) -> np.ndarray:
    """Every pixel where an anchor would be sitting on what `spec` names.

    Three forms, which between them cover what these illustrations label:

        "pale"            solidly inside one class
        "edge:pale|skin"  on the boundary where two classes meet — this is what
                          "where pigment stops" or "a border you can draw"
                          actually mean, and neither class alone expresses it
        "spot:skin@pale"  a small island of one class surrounded by another —
                          a pigment island in a patch, a graft in a bed

    The thresholds are deliberately blunt. A ring only has to be ON the thing;
    finding its optical centre would be false precision.
    """
    if spec == "artwork":
        # The weakest useful claim: on the drawing rather than on the stage.
        # For a label whose exact target needs a person to look at the picture,
        # this still converts "pointing at nothing" into "pointing at the
        # nearest thing", which is strictly better and never wrong in the way
        # a guessed class would be. Narrow it to a real class once someone has
        # looked; `--audit-find` lists everything still on this.
        return boxfrac(cls != "stage", r * 2) >= 0.90
    if spec.startswith("edge:"):
        a, b = spec[5:].split("|")
        return (boxfrac(cls == a, r) >= 0.25) & (boxfrac(cls == b, r) >= 0.25)
    if spec.startswith("spot:"):
        a, b = spec[5:].split("@")
        return (boxfrac(cls == a, r) >= 0.45) & (boxfrac(cls == b, r * 3) >= 0.25)
    # A WIDER window than the probe, on purpose. `snap` takes the NEAREST
    # qualifying pixel, and for a solid object the nearest pixel of it is
    # always a rim pixel — the first attempt put "the dermatoscope" on the top
    # edge of its own housing. Demanding a solid neighbourhood twice the probe
    # radius admits only points well inside the shape, so the nearest of those
    # is in the body of the object rather than on its outline.
    return boxfrac(cls == spec, r * 2) >= 0.80


def snap(cls: np.ndarray, xp: float, yp: float, spec: str,
         r: int) -> tuple[float, float, float] | None:
    """Nearest qualifying point to where the label was authored.

    NEAREST, not best. The author's coordinate carries a judgement the picture
    cannot: which of six pigment islands, which of two panels. Moving to the
    closest valid point keeps that and corrects only the error, where snapping
    to the largest or most central region would quietly re-target the label.
    """
    q = qualify(cls, spec, r)
    if not q.any():
        return None
    H, W = cls.shape
    y, x = int(round(yp / 100 * H)), int(round(xp / 100 * W))
    ys, xs = np.nonzero(q)
    d2 = (ys - y) ** 2 + (xs - x) ** 2
    i = int(d2.argmin())
    return (round(xs[i] / W * 100, 1), round(ys[i] / H * 100, 1),
            float(np.sqrt(d2[i])))


def apply_moves(todo: list[tuple]) -> int:
    """Rewrite the x/y of the named labels in the content modules.

    Matched on the label's text AND its current coordinates, so a rerun is a
    no-op rather than a second displacement, and so a label whose words appear
    twice cannot be moved by a fix meant for the other one.

    Editing every file that mentions the text is deliberate: B4 carries the same
    labels in `brand.py` and `vitiligo.py`, and the Telugu and Hindi pages carry
    translated words over the same coordinates. One picture-space correction
    should land everywhere the picture is used.
    """
    import re as _re
    content = Path(__file__).parent / "content"
    done = 0
    for text, ox, oy, nx, ny in todo:
        # x/y are ints in the source; the solver returns one decimal place, and
        # a tenth of a percent is a third of a pixel here. Round to keep the
        # data in the form the rest of the pipeline already expects.
        nxi, nyi = int(round(nx)), int(round(ny))
        pat = _re.compile(
            r'(\{"text":\s*"' + _re.escape(text) + r'",\s*)'
            r'"x":\s*' + str(ox) + r',\s*"y":\s*' + str(oy))
        for path in sorted(content.glob("*.py")):
            src = path.read_text(encoding="utf-8")
            new, n = pat.subn(rf'\g<1>"x": {nxi}, "y": {nyi}', src)
            if n:
                path.write_text(new, encoding="utf-8")
                _drop_pyc(path)
                done += n
    return done


def _drop_pyc(path: Path) -> None:
    """Delete the module's cached bytecode after rewriting its source.

    Not paranoia. CPython invalidates a `.pyc` on (mtime, size), and these edits
    routinely change neither: rewriting `"y": 12` to `"y": 16` is the same byte
    count, and it lands in the same second as the import that just read it. The
    next process then loads the stale bytecode and the tool reports the label it
    has just fixed as still broken — which is exactly what happened, and cost
    more time to understand than the fix it was hiding.
    """
    # The WHOLE package cache, not just this module's. Dropping only the edited
    # file's `.pyc` still let a stale read through — these edits change neither
    # mtime-second nor byte count, which is exactly the blind spot in CPython's
    # (mtime, size) check, and one survivor is enough to make the tool report a
    # label it has just corrected as still broken.
    for pyc in (path.parent / "__pycache__").glob("*.pyc"):
        pyc.unlink(missing_ok=True)


def diagrams() -> list[dict]:
    """Every labelled diagram on the site, with the page it appears on.

    Read from `build.PAGES` rather than by parsing the content modules, so this
    sees exactly what the site is built from — including the Telugu and Hindi
    pages, which carry their own labels over the same artwork.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    import build                                        # noqa: E402
    found = []
    for page in build.PAGES:
        for sec in page.get("sections", []):
            if sec.get("kind") != "diagram" or not sec.get("labels"):
                continue
            img = sec.get("image") or {}
            if not img.get("src"):
                continue
            found.append({"slug": page["slug"], "src": img["src"],
                          "labels": sec["labels"], "mode": mode(sec)})
    return found


def mode(sec: dict) -> str:
    """Which placement mode a diagram uses — the same test build.py applies.

    Order matters: `rail` is an explicit flag and wins outright. Row mode is
    recognised by `label_col: 0` or by every label carrying `lead: 2`, which is
    how DIAGRAMS.md defines it. Anything else is a column.
    """
    if sec.get("rail"):
        return "rail"
    if sec.get("label_col") == 0 or {l.get("lead") for l in sec["labels"]} == {2}:
        return "row"
    return "column"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--class-map", metavar="STEM",
                    help="print an ASCII segmentation of one diagram")
    ap.add_argument("--quiet-ok", action="store_true",
                    help="only show anchors that are on `stage`")
    ap.add_argument("--snap", action="store_true",
                    help="for labels carrying `find`, print corrected x/y")
    ap.add_argument("--write", action="store_true",
                    help="with --snap, apply the corrections to content/*.py")
    args = ap.parse_args()

    cache: dict[str, tuple[np.ndarray, dict]] = {}

    def load(src: str):
        if src not in cache:
            cache[src] = classify(Image.open(ASSETS / src))
        return cache[src]

    if args.class_map:
        hits = [d for d in diagrams() if args.class_map in d["src"]]
        if not hits:
            return print(f"no diagram matching {args.class_map!r}") or 1
        cls, _ = load(hits[0]["src"])
        H, W = cls.shape
        glyph = {"stage": " ", "ink": "#", "metal": "M", "glass": "G",
                 "pale": ".", "skin": "s", "fabric": "f", "other": "?"}
        rows, cols = 34, 96
        for j in range(rows):
            line = []
            for i in range(cols):
                y0, y1 = j * H // rows, (j + 1) * H // rows
                x0, x1 = i * W // cols, (i + 1) * W // cols
                blk = cls[y0:y1, x0:x1]
                names, counts = np.unique(blk, return_counts=True)
                line.append(glyph.get(names[counts.argmax()], "?"))
            print("".join(line))
        print(f"\n{hits[0]['src']}  {W}x{H}   "
              + "  ".join(f"{k}={v}" for k, v in glyph.items()))
        return 0

    # Deduped on (artwork, x, y) — NOT on the label text. The Telugu and Hindi
    # pages carry their own words over the same picture at the same coordinate,
    # so one geometric fix serves all three languages, and counting them
    # separately would treble the apparent size of the problem.
    if args.snap:
        moves, todo = 0, []
        for d in diagrams():
            cls, _ = load(d["src"])
            H, W = cls.shape
            r = max(4, int(round(min(W, H) * PROBE_FRAC)))
            for lab in d["labels"]:
                spec = lab.get("find")
                if not spec:
                    continue
                stem = Path(d["src"]).stem
                got = snap(cls, lab["x"], lab["y"], spec, r)
                if got is None:
                    print(f"  !!  {stem:26} {lab['text'][:22]:23} "
                          f"nothing in the artwork matches {spec!r}")
                    continue
                nx, ny, dist = got
                # Inside the probe radius the anchor is already on the right
                # structure; anything further and it was pointing elsewhere.
                if dist < r:
                    print(f"  ok  {stem:26} {lab['text'][:22]:23} {spec:16}")
                    continue
                moves += 1
                print(f"  FIX {stem:26} {lab['text'][:22]:23} {spec:16} "
                      f"{lab['x']},{lab['y']} -> {nx},{ny}  ({dist:.0f}px)")
                if args.write:
                    todo.append((lab["text"], lab["x"], lab["y"], nx, ny))
        if args.write and todo:
            print(f"\n{apply_moves(todo)} label(s) rewritten in content/")
        print(f"\n{moves} anchor(s) need moving")
        return 0

    rows, seen, by_design = [], set(), 0
    for d in diagrams():
        cls, _ = load(d["src"])
        for lab in d["labels"]:
            key = (d["src"], lab.get("x"), lab.get("y"))
            if key in seen:
                continue
            seen.add(key)
            if d["mode"] == "row":
                by_design += 1                  # a caption, not a pointer
                continue
            mix = probe(cls, lab["x"], lab["y"])
            top, frac = mix[0]
            stage = dict(mix).get("stage", 0.0)
            rows.append({"src": Path(d["src"]).stem, "slug": d["slug"],
                         "mode": d["mode"], "text": lab.get("text", ""),
                         "x": lab["x"], "y": lab["y"], "top": top,
                         "frac": frac, "stage": stage,
                         "find": lab.get("find")})

    rows.sort(key=lambda r: -r["stage"])
    bad = [r for r in rows if r["stage"] >= 0.5]
    soft = [r for r in rows if 0.15 <= r["stage"] < 0.5]

    show = bad if args.quiet_ok else rows
    print(f"{'diagram':26} {'label':26} {'x,y':>9}  {'on':7} {'stage%':>7}")
    print("-" * 82)
    for r in show:
        print(f"{r['src'][:25]:26} {r['text'][:25]:26} "
              f"{str(r['x']) + ',' + str(r['y']):>9}  {r['top']:7} "
              f"{r['stage'] * 100:6.0f}%")

    print(f"\n{len(seen)} distinct anchors ({len(rows)} pointers, "
          f"{by_design} row-mode captions skipped by design)")
    print(f"  {len(bad)} pointing at background (>=50% stage) — always wrong")
    print(f"  {len(soft)} partly off the artwork (15-50% stage) — check")

    # COVERAGE, stated rather than left to be assumed.
    #   The stage test only catches an anchor pointing at NOTHING. An anchor on
    #   the wrong structure — "a scratch line" sitting on plain skin beside the
    #   streak — is invisible to it and is only caught by a `find` declaration.
    #   So a label with no `find` is unverified, not passing, and the difference
    #   matters: a green run with 10% coverage means almost nothing was checked.
    declared = [r for r in rows if r["find"]]
    print(f"  {len(declared)}/{len(rows)} pointers have a `find` declaration "
          f"({len(declared) * 100 // max(len(rows), 1)}% verified; the rest are "
          f"UNCHECKED, not passing)")
    weak = [r for r in declared if r["find"] == "artwork"]
    if weak:
        print(f"  {len(weak)} declared only as `artwork` — on the drawing, but "
              f"the exact structure still wants a human eye")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
