#!/usr/bin/env python
"""Measure every diagram label, in a real browser, at every width.

    python diagram_audit.py              # every built page, phone + desktop
    python diagram_audit.py --all-widths # all five verify.py viewports
    python diagram_audit.py vitiligo psoriasis

WHY THIS EXISTS
  `verify.py` proves no page scrolls sideways and no image 404s. Neither of
  those catches the defect that actually matters on a labelled illustration:
  a ring that has drifted off the structure it names, a riser that stops short
  of its own ring, two numbers sitting on top of each other. All of those
  render "fine" — nothing overflows, nothing is broken — and all of them make
  the picture wrong.

  Eyeballing catches them one at a time, at one width, on the page you happened
  to open. There are 66 placements across 47 pages and five widths. That is 330
  page-renders and several hundred labels; it is not an eyeball job.

WHAT IT CHECKS
  drift    the anchor ring's centre, as a fraction of the ARTWORK box, must be
           the (x, y) the label was authored with. This is the load-bearing
           one: it is what "the label lands accurately" means. Anything above
           a pixel or two means a transform, a border or a container is
           displacing the ring from the structure it points at.
  riser    (rail mode) the hairline must actually touch its ring at the top and
           its own number at the foot. A riser computed from one constant and
           drawn from another stops short, and the picture then has a line
           pointing at nothing.
  collide  two numbers, two chips or two rail labels overlapping inside one
           figure. On a phone the words are hidden and the number is the whole
           label, so two numbers on one spot destroys the figure outright.
  cross    (rail mode) a riser passing through a NUMBER that is not its own.
           `diagram_rail.py` proves this cannot happen for the authored data;
           this proves it for what the browser actually painted, which is the
           claim that matters.
  escape   any part of a label outside its own figure. `verify.py` sees this
           only when it reaches the viewport edge; here a label hanging off a
           narrow figure is caught wherever it happens.

Exit code is 1 if anything is out of tolerance, so it can gate a build.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from verify import DIST, chrome

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A ring is a 9px circle over anatomy; a pixel and a half of slop is invisible
# and is also the most sub-pixel rounding can contribute at these sizes.
DRIFT_TOL = 1.5
# A riser is 1px wide and meets a ring that is 9px across, so it can miss by a
# few pixels and still look joined. Beyond that it visibly stops short.
RISER_TOL = 3.0
# Two boxes are only "colliding" when they genuinely intersect, not when they
# share a rounded edge.
OVERLAP_TOL = 1.0

WIDTHS = {"phone": (390, 844), "tablet": (768, 1024), "laptop": (1040, 800),
          "wide": (1240, 800), "desktop": (1440, 900)}
DEFAULT_WIDTHS = ["phone", "desktop"]

# Measured inside an iframe of the exact width for the same reason verify.py
# does it: Chrome on Windows will not open a window narrower than ~500px, so a
# 390px --window-size lays the page out at ~512 and every phone measurement
# taken that way is a measurement of the wrong layout.
HARNESS = r"""<!doctype html><meta charset="utf-8">
<body style="margin:0;background:#fff">
<iframe id="f" src="PAGE" style="width:WIDTHpx;height:HEIGHTpx;border:0"></iframe>
<script>
function report(d) { document.title = 'DGA' + JSON.stringify(d); }
document.getElementById('f').addEventListener('load', function () {
  var f = document.getElementById('f');
  setTimeout(function () {
    var d, w;
    try { d = f.contentDocument; w = f.contentWindow; } catch (e) {
      report({ error: 'cannot read into the frame: ' + e }); return;
    }
    if (!d || !d.body) { report({ error: 'page did not load in the frame' }); return; }
    function box(el) {
      if (!el) return null;
      var r = el.getBoundingClientRect();
      return { l: r.left, t: r.top, r: r.right, b: r.bottom,
               w: r.width, h: r.height, cx: r.left + r.width / 2,
               cy: r.top + r.height / 2 };
    }
    // The authored percentage, read back off the inline custom property. Going
    // through the DOM rather than the source data is deliberate: it proves the
    // browser received the number the renderer emitted.
    function pct(el, name) {
      var v = el.style.getPropertyValue(name).trim();
      return v ? parseFloat(v) : null;
    }
    var out = [];
    var figs = d.querySelectorAll('figure.diagram');
    for (var i = 0; i < figs.length; i++) {
      var fig = figs[i];
      var pic = fig.querySelector('.dg-img');
      var art = box(pic);
      if (!art || !art.w) continue;
      // A broken image still lays out at full width but collapses to the
      // height of its alt text, so `y` measurements come out of a box that is
      // 36px tall instead of 750 and every label looks catastrophically
      // misplaced. That is a lie about the labels, and it is exactly the kind
      // of lie a gate must not tell — a half-copied `dist/` once produced a
      // page of confident nonsense here. Report the real fault instead.
      var rec = { fig: i, art: art, box: box(fig), rail: !!fig.querySelector('.dg-rail'),
                  loaded: !!(pic.complete && pic.naturalWidth > 0),
                  labels: [] };
      var pins = fig.querySelectorAll('li.dg-pin');
      var rails = fig.querySelectorAll('li.dg-rpin');
      for (var n = 0; n < pins.length; n++) {
        var pin = pins[n];
        var lab = {
          n: n + 1,
          x: pct(pin, '--x'), y: pct(pin, '--y'),
          ring: box(pin.querySelector('.dg-anchor')),
          num: box(pin.querySelector('.dg-n')),
          chip: box(pin.querySelector('.dg-t')),
          lead: box(pin.querySelector('.dg-lead'))
        };
        // A rail figure keeps its number in the rail, so the pin's own disc is
        // display:none and must not be measured as if it were on the artwork.
        var rl = rails[n];
        if (rl) {
          lab.riser = box(rl.querySelector('.dg-riser'));
          lab.jog = box(rl.querySelector('.dg-jog'));
          lab.drop = box(rl.querySelector('.dg-drop'));
          lab.rlab = box(rl.querySelector('.dg-rlab'));
          lab.num = box(rl.querySelector('.dg-n'));
          lab.chip = box(rl.querySelector('.dg-t'));
          lab.rl = rl.className.indexOf('dg-rl') !== -1;
        }
        // A hidden element reports a zero box; report it as absent instead so
        // the checks can tell "not shown at this width" from "shown here". A
        // jog of zero width is the normal case — a disc that never moved — so
        // it has to be allowed to vanish the same way.
        ['ring','num','chip','lead','riser','rlab','jog','drop'].forEach(function (k) {
          if (lab[k] && (lab[k].w + lab[k].h === 0)) lab[k] = null;
        });
        rec.labels.push(lab);
      }
      out.push(rec);
    }
    report({ innerWidth: w.innerWidth, figures: out });
  }, 380);
});
</script>
"""


def probe(exe: str, slug: str, name: str) -> dict:
    w, h = WIDTHS[name]
    page = DIST / ("index.html" if slug == "index" else f"{slug}.html")
    if not page.exists():
        return {"error": f"{page.name} not built"}
    tmp = DIST / f"__dga-{slug}-{name}.html"
    tmp.write_text(HARNESS.replace("PAGE", page.name)
                   .replace("WIDTH", str(w)).replace("HEIGHT", str(h)),
                   encoding="utf-8")
    try:
        out = subprocess.run(
            [exe, "--headless", "--disable-gpu", "--no-sandbox",
             "--hide-scrollbars", "--allow-file-access-from-files",
             f"--window-size={max(w, 520)},{h + 40}",
             "--virtual-time-budget=3000", "--dump-dom", tmp.as_uri()],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=90).stdout
    except subprocess.TimeoutExpired:
        return {"error": "browser timed out"}
    finally:
        tmp.unlink(missing_ok=True)
    m = re.search(r"<title>DGA(\{.*?\})</title>", out, re.S)
    if not m:
        return {"error": "probe did not report"}
    try:
        return json.loads(m.group(1).replace("&quot;", '"'))
    except json.JSONDecodeError as exc:
        return {"error": f"unreadable probe result ({exc})"}


def overlap(a: dict, b: dict) -> float:
    """Area-free overlap measure: the smaller of the two axis intersections."""
    ox = min(a["r"], b["r"]) - max(a["l"], b["l"])
    oy = min(a["b"], b["b"]) - max(a["t"], b["t"])
    return min(ox, oy) if ox > 0 and oy > 0 else 0.0


def audit_figure(fig: dict) -> list[str]:
    """Every complaint about one figure at one width, in plain English."""
    bad: list[str] = []
    art, labels = fig["art"], fig["labels"]
    # Measuring against a box whose height came from alt text would report every
    # label as wildly misplaced and send someone hunting a layout bug that is
    # really a missing file.
    if not fig.get("loaded", True):
        return ["artwork did not load — nothing here was measured"]

    for lab in labels:
        n = lab["n"]
        ring = lab.get("ring")
        # DRIFT — the ring must sit at the authored fraction of the ARTWORK.
        if ring and lab["x"] is not None:
            want_x = art["l"] + art["w"] * lab["x"] / 100
            want_y = art["t"] + art["h"] * lab["y"] / 100
            dx, dy = ring["cx"] - want_x, ring["cy"] - want_y
            if abs(dx) > DRIFT_TOL or abs(dy) > DRIFT_TOL:
                bad.append(f"label {n} ring is {dx:+.1f}px, {dy:+.1f}px off its "
                           f"anchor ({lab['x']}%, {lab['y']}%)")
        # LEADER — must start on its ring and end on its own number, whether it
        # is a straight riser or an elbow (riser → jog → drop). Checking only
        # the riser would pass an elbow whose two halves had come apart.
        riser, num = lab.get("riser"), lab.get("num")
        jog, drop = lab.get("jog"), lab.get("drop")
        if riser and ring:
            if abs(riser["t"] - ring["cy"]) > RISER_TOL:
                bad.append(f"label {n} leader starts {riser['t'] - ring['cy']:+.1f}px "
                           f"from its ring")
            if abs(riser["cx"] - ring["cx"]) > RISER_TOL:
                bad.append(f"label {n} leader is {riser['cx'] - ring['cx']:+.1f}px "
                           f"sideways of its ring")
            foot = drop or riser
            if num and abs(foot["b"] - num["cy"]) > RISER_TOL:
                bad.append(f"label {n} leader misses its own number by "
                           f"{foot['b'] - num['cy']:+.1f}px")
            if num and drop and abs(drop["cx"] - num["cx"]) > RISER_TOL:
                bad.append(f"label {n} leader lands {drop['cx'] - num['cx']:+.1f}px "
                           f"sideways of its own number")
            # An elbow's three segments have to touch, or it reads as two
            # unrelated hairlines pointing at nothing.
            if jog:
                for seg, end in (("riser", riser["b"]), ("drop", drop["t"] if drop else None)):
                    if end is not None and abs(end - jog["cy"]) > RISER_TOL:
                        bad.append(f"label {n} elbow is broken: {seg} ends "
                                   f"{end - jog['cy']:+.1f}px from the turn")
                if drop and min(jog["r"] - drop["cx"], drop["cx"] - jog["l"]) < -RISER_TOL:
                    bad.append(f"label {n} elbow turn does not reach its drop")
        # ESCAPE — nothing may hang outside the figure.
        for part in ("num", "chip", "rlab"):
            got = lab.get(part)
            if got and (got["l"] < fig["box"]["l"] - 1
                        or got["r"] > fig["box"]["r"] + 1):
                bad.append(f"label {n} {part} escapes the figure "
                           f"({got['l'] - fig['box']['l']:+.0f}px, "
                           f"{got['r'] - fig['box']['r']:+.0f}px)")

    # COLLIDE — two labels' visible parts intersecting.
    for part, what in (("num", "numbers"), ("chip", "chips"), ("rlab", "rail labels")):
        boxes = [(lab["n"], lab[part]) for lab in labels if lab.get(part)]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ov = overlap(boxes[i][1], boxes[j][1])
                if ov > OVERLAP_TOL:
                    bad.append(f"{what} {boxes[i][0]} and {boxes[j][0]} overlap "
                               f"by {ov:.0f}px")

    # CROSS — any part of one label's leader passing through someone else's
    # number. Each segment is a thin box, so this is a plain intersection test;
    # the jog is included because a turn line drawn at disc height would run
    # straight through whatever discs lay between its ends.
    for lab in labels:
        for part in ("riser", "jog", "drop"):
            seg = lab.get(part)
            if not seg:
                continue
            for other in labels:
                if other is lab or not other.get("num"):
                    continue
                if overlap(seg, other["num"]) > OVERLAP_TOL:
                    bad.append(f"label {lab['n']}'s {part} crosses "
                               f"number {other['n']}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all-widths", action="store_true")
    ap.add_argument("--quiet", action="store_true",
                    help="only print pages that have a problem")
    args = ap.parse_args()

    names = list(WIDTHS) if args.all_widths else DEFAULT_WIDTHS
    slugs = args.slugs or sorted(
        p.stem for p in DIST.glob("*.html") if not p.name.startswith("__"))

    exe = chrome()
    jobs = [(s, n) for s in slugs for n in names]
    print(f"measuring {len(slugs)} page(s) at {len(names)} width(s) "
          f"({len(jobs)} renders)…\n")

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda j: (j, probe(exe, *j)), jobs))

    problems, figures, labels = [], 0, 0
    for (slug, name), res in results:
        where = f"{slug} @ {name} ({WIDTHS[name][0]}px)"
        if res.get("error"):
            problems.append((where, [res["error"]]))
            continue
        for fig in res["figures"]:
            figures += 1
            labels += len(fig["labels"])
            bad = audit_figure(fig)
            if bad:
                mode = "rail" if fig["rail"] else "pin"
                problems.append((f"{where} · figure {fig['fig'] + 1} ({mode})", bad))

    if problems:
        total = sum(len(b) for _, b in problems)
        print(f"{total} problem(s) across {len(problems)} figure-width(s):\n")
        for where, bad in problems:
            print(f"  {where}")
            for b in bad:
                print(f"      · {b}")
        return 1
    print(f"clean — {labels} labels across {figures} figure-renders sit on their "
          f"anchors, joined, unobstructed and inside the frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
