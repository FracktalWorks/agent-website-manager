#!/usr/bin/env python
"""Check the built pages in a real browser, at real viewport widths.

    python verify.py            # representative pages, 4 viewports
    python verify.py --all      # every page
    python verify.py vitiligo acne-treatment-hyderabad

`build.py` proves the *data* is right. It cannot tell you the page renders: a
table that overflows at 390px, an image that never loads, a heading clipped by a
sticky header — all pass every static check and are obvious in a browser.

Open Design learned this the expensive way. A five-phase static audit of theirs
reported "42/45 requirements met, 0 defects"; driving the same build in a real
browser found three runtime-only bugs, one of which rendered a blank page. Static
confidence is not evidence.

The measurement that matters most is horizontal overflow. It is the most common
responsive defect, it is invisible in a desktop screenshot, and it is exactly
mechanical: if `documentElement.scrollWidth` exceeds the viewport width, some
element is too wide, and we can name it.

No dependencies: Chrome's `--dump-dom` runs the page's JavaScript and prints the
resulting DOM, so a measuring script that writes its findings into `<title>` gets
them back out.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"

# Widths that correspond to real decisions in the stylesheet, not round numbers:
# 390 is the common phone, 768 is where the nav collapses, 1040 and 1240 sit
# either side of the 1200px dropdown breakpoint, 1440 is the design width.
VIEWPORTS = [("phone", 390, 844), ("tablet", 768, 1024),
             ("laptop", 1040, 800), ("wide", 1240, 800),
             ("desktop", 1440, 900)]

# One page per template, plus the layouts most likely to break: the widest table
# and the page with the most cards.
SAMPLE = ["index", "vitiligo", "vitiligo-cost", "about-dr-khagendra-varada",
          "contact", "te-vitiligo"]

# Chrome on Windows refuses to open a window narrower than ~500px, so
# `--window-size=390,844` silently gives a 500px viewport and the most important
# width never gets tested. Measuring inside an iframe of the exact width sidesteps
# that entirely — the iframe's own `innerWidth` really is 390 — and it needs
# `--allow-file-access-from-files` so the harness can read into the frame.
HARNESS = """<!doctype html><meta charset="utf-8">
<body style="margin:0;background:#fff">
<iframe id="f" src="PAGE" style="width:WIDTHpx;height:HEIGHTpx;border:0"></iframe>
<script>
function report(data) { document.title = 'ODV' + JSON.stringify(data); }
document.getElementById('f').addEventListener('load', function () {
  var f = document.getElementById('f');
  setTimeout(function () {
    var d, w;
    try { d = f.contentDocument; w = f.contentWindow; } catch (e) {
      report({ error: 'cannot read into the frame: ' + e }); return;
    }
    if (!d || !d.body) { report({ error: 'page did not load in the frame' }); return; }
    var iw = w.innerWidth, over = [], all = d.querySelectorAll('body *');
    for (var i = 0; i < all.length; i++) {
      var el = all[i], r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      if (r.right <= iw + 1 && r.left >= -1) continue;
      // An element wider than the viewport is only a defect if nothing above it
      // clips or scrolls it. Wide tables live in .tablewrap (overflow-x:auto)
      // and the marquee lives in .ticker (overflow:hidden) — both intentional.
      var contained = false;
      for (var p = el.parentElement; p && p !== d.body; p = p.parentElement) {
        var ov = w.getComputedStyle(p).overflowX;
        if (ov === 'hidden' || ov === 'auto' || ov === 'scroll' || ov === 'clip') {
          contained = true; break;
        }
      }
      if (contained) continue;
      var id = el.tagName.toLowerCase() +
        (el.className && typeof el.className === 'string'
          ? '.' + el.className.trim().split(/\\s+/)[0] : '');
      if (over.indexOf(id) === -1) over.push(id);
    }
    var imgs = [], pics = d.images;
    for (var j = 0; j < pics.length; j++) {
      if (!pics[j].complete || pics[j].naturalWidth === 0)
        imgs.push(pics[j].getAttribute('src'));
    }
    report({ scrollWidth: d.documentElement.scrollWidth, innerWidth: iw,
             overflow: over.slice(0, 6), brokenImages: imgs.slice(0, 6) });
  }, 320);
});
</script>
"""


def chrome() -> str:
    for candidate in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "google-chrome", "chromium",
    ):
        if Path(candidate).exists() or shutil.which(candidate):
            return candidate
    raise SystemExit("Chrome not found — install it or set the path in verify.py.")


def probe(exe: str, slug: str, name: str, w: int, h: int) -> dict:
    """Render one page at one width and read back what the browser measured."""
    page = DIST / ("index.html" if slug == "index" else f"{slug}.html")
    if not page.exists():
        return {"error": f"{page.name} not built"}
    # The harness lives beside the real page so the iframe's relative asset
    # paths still resolve; it is removed afterwards.
    tmp = DIST / f"__verify-{slug}-{name}.html"
    tmp.write_text(HARNESS.replace("PAGE", page.name)
                   .replace("WIDTH", str(w)).replace("HEIGHT", str(h)),
                   encoding="utf-8")
    try:
        out = subprocess.run(
            [exe, "--headless", "--disable-gpu", "--no-sandbox",
             "--hide-scrollbars", "--allow-file-access-from-files",
             f"--window-size={max(w, 520)},{h + 40}",
             "--virtual-time-budget=2500", "--dump-dom", tmp.as_uri()],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60).stdout
    except subprocess.TimeoutExpired:
        return {"error": "browser timed out"}
    finally:
        tmp.unlink(missing_ok=True)

    m = re.search(r"<title>ODV(\{.*?\})</title>", out, re.S)
    if not m:
        return {"error": "probe did not report — the page may not have loaded"}
    try:
        return json.loads(m.group(1).replace("&quot;", '"'))
    except json.JSONDecodeError as exc:
        return {"error": f"unreadable probe result ({exc})"}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        slugs = sorted(p.stem if p.stem != "index" else "index"
                       for p in DIST.glob("*.html")
                       if not p.name.startswith("__"))
    else:
        slugs = args or SAMPLE

    exe = chrome()
    jobs = [(s, n, w, h) for s in slugs for n, w, h in VIEWPORTS]
    print(f"checking {len(slugs)} page(s) at {len(VIEWPORTS)} widths "
          f"({len(jobs)} renders)…\n")

    problems: list[str] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda j: (j, probe(exe, *j)), jobs))

    for (slug, name, w, _h), res in results:
        where = f"{slug} @ {name} ({w}px)"
        if res.get("error"):
            problems.append(f"{where}: {res['error']}")
            continue
        sw, iw = res["scrollWidth"], res["innerWidth"]
        if sw > iw + 1:
            culprits = ", ".join(res["overflow"]) or "unknown element"
            problems.append(f"{where}: scrolls sideways — content is {sw}px wide "
                            f"in a {iw}px viewport (widest: {culprits})")
        if res.get("brokenImages"):
            problems.append(f"{where}: images did not load — "
                            f"{', '.join(res['brokenImages'])}")

    if problems:
        print(f"{len(problems)} problem(s):\n")
        for p in problems:
            print("  ·", p)
        return 1
    print(f"all {len(jobs)} renders clean — no horizontal overflow, "
          "no broken images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
