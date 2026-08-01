"""Exercise the live editor's version model and site-wide link retargeting.

Run it against a running editor:

    cd outputs/drvarada-site/site && python editor.py &
    python tests/live_editor_parity.py

WHY THE SAFETY HARNESS BELOW EXISTS
  The first version of this file took its "clean tree" baseline to be the OLDEST
  entry in the version store, on the assumption that the store was fresh. On
  2026-07-30 it was not — it held a seed from a previous session — and restoring
  it reverted an hour of source edits to that morning's state. Nothing was lost,
  because append-only meant the newer seed was still in the timeline, but the
  recovery was a hand-written script run under pressure.

  Two rules came out of that, and they are the reason this file is shaped the
  way it is:

    1. A test that mutates the working tree keeps its OWN copy of every file it
       could touch, and restores from that copy — never from the system under
       test. You cannot use the thing you are testing as your safety net.
    2. The test never restores a version it did not create. `BASELINE_ID` is
       read at start-up and is the version that was current then; every restore
       target is either that or something this run made.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8789"
SITE = (pathlib.Path(__file__).resolve().parents[1]
        / "outputs" / "drvarada-site" / "site")

# Every file an edit in this test could reach. Kept explicit rather than globbed
# so a new content module does not silently fall outside the safety net.
WATCH = sorted(SITE.glob("content/*.py")) + [SITE / "chrome.py"]
ORIGINAL = {f: f.read_bytes() for f in WATCH}


def fingerprint() -> dict[str, str]:
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in WATCH}


BASELINE = fingerprint()


def drifted() -> str:
    now = fingerprint()
    return ", ".join(sorted(k for k in BASELINE if BASELINE[k] != now.get(k)))


def put_it_back() -> list[str]:
    """Restore from our own copy. The last line of defence, and deliberately
    the dumbest code in the file: bytes in, bytes out, no dependency on the
    editor being alive or the store being sane."""
    healed = []
    for f, blob in ORIGINAL.items():
        if f.read_bytes() != blob:
            f.write_bytes(blob)
            healed.append(f.name)
    return healed


def get(path: str) -> str:
    with urllib.request.urlopen(BASE + path, timeout=90) as r:
        return r.read().decode("utf-8")


def post(path: str, body: dict | None = None):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body or {}).encode(),
        headers={"Content-Type": "text/plain", "X-OD-Token": TOKEN, "Origin": BASE})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()[:160]


TOKEN = re.search(r'__odToken\s*=\s*"([^"]+)"', get("/index.html")).group(1)
fails: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(("  ok   " if cond else "  FAIL ") + name + (f"   {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def main() -> int:
    print("\n-- 1. the version timeline ------------------------------------")
    _, h = post("/api/history")
    check("history endpoint answers", h.get("ok") is True, str(h)[:80])
    start_depth = h["depth"]
    # The version that is current NOW. Every "go back to where we started" in
    # this file means this one, and never entries[-1].
    baseline_id = next((e["id"] for e in h["entries"] if e.get("current")),
                       h["entries"][0]["id"])
    check("there is a version to come back to", bool(baseline_id))

    print("\n-- 2. an edit appends a version -------------------------------")
    cells = re.findall(r'<td data-od="(sections\.\d+\.rows\.\d+\.\d+)"',
                       get("/vitiligo-cost.html"))
    _, r = post("/api/edit", {"slug": "vitiligo-cost", "addr": cells[2],
                              "newText": "VERSION TEST", "newHTML": "VERSION TEST"})
    check("edit applied", r.get("ok") is True, str(r)[:90])
    _, h2 = post("/api/history")
    check("timeline grew by one", h2["depth"] == start_depth + 1,
          f"{start_depth} -> {h2['depth']}")
    check("the new version records the edit text",
          "VERSION TEST" in (h2["entries"][0]["prompt"] or ""), h2["entries"][0]["prompt"])
    v_edit = h2["entries"][0]["id"]

    print("\n-- 3. restore is a write, not a rewind (Open Design's rule) ---")
    _, r = post("/api/restore", {"id": baseline_id})
    check("restore succeeds", r.get("ok") is True, str(r)[:90])
    check("restore produced the pre-edit content",
          "VERSION TEST" not in get("/vitiligo-cost.html"))
    _, h3 = post("/api/history")
    check("restoring APPENDED rather than truncating", h3["depth"] == h2["depth"] + 1,
          f"{h2['depth']} -> {h3['depth']}")
    check("the new version carries its provenance in the label",
          "restored from v" in h3["entries"][0]["label"], h3["entries"][0]["label"])
    check("the version we came from is still in the timeline",
          any(e["id"] == v_edit for e in h3["entries"]))

    print("\n-- 4. and we can still jump forward to it ---------------------")
    _, r = post("/api/restore", {"id": v_edit})
    check("restoring the newer version works", r.get("ok") is True, str(r)[:90])
    check("its content came back", "VERSION TEST" in get("/vitiligo-cost.html"))

    print("\n-- 5. undo/redo move without appending ------------------------")
    _, before = post("/api/history")
    _, r = post("/api/undo")
    check("undo works", r.get("ok") is True, str(r)[:80])
    _, after = post("/api/history")
    check("undo did NOT append", after["depth"] == before["depth"],
          f"{before['depth']} -> {after['depth']}")
    check("redo works", post("/api/redo")[1].get("ok") is True)

    print("\n-- 6. back to where we started --------------------------------")
    _, r = post("/api/restore", {"id": baseline_id})
    check("restored the baseline", r.get("ok") is True)
    check("sources are exactly as they started", drifted() == "", drifted()[:90])

    print("\n-- 7. link scope: where is this used? -------------------------")
    _, w = post("/api/link-where", {"href": "vitiligo.html"})
    check("a rendered href is normalised back to its slug", w["count"] > 10,
          f"{w['count']} uses of 'vitiligo'")
    _, w2 = post("/api/link-where", {"href": "https://wa.me/919989955330"})
    check("a shared constant is reported as such", w2.get("constant") == "WHATSAPP",
          str(w2.get("constant")))

    print("\n-- 8. retarget everywhere -------------------------------------")
    _, w3 = post("/api/link-where", {"href": "dandruff-treatment.html"})
    n_before = w3["count"]
    check("target has several uses", n_before >= 4, f"{n_before} uses")
    _, r = post("/api/link", {"slug": "index", "addr": "", "scope": "all",
                              "oldHref": "dandruff-treatment.html",
                              "href": "premature-greying-treatment"})
    check("retarget-all succeeded", r.get("ok") is True, str(r)[:110])
    check("it changed every use", r.get("applied") == n_before,
          f"applied {r.get('applied')} of {n_before}")
    check("nothing points at the old target any more",
          post("/api/link-where", {"href": "dandruff-treatment"})[1]["count"] == 0)

    print("\n-- 9. one click puts all of it back ---------------------------")
    check("undo reverses the whole site-wide change",
          post("/api/undo")[1].get("ok") is True)
    _, w5 = post("/api/link-where", {"href": "dandruff-treatment"})
    check("every link is back", w5["count"] == n_before, f"{w5['count']} of {n_before}")
    check("sources are back to how they started", drifted() == "", drifted()[:90])

    print("\n-- 10. nav and footer links are addressable -------------------")
    home = get("/index.html")
    nav = re.findall(r'data-od-link="(chrome:NAV[^"]*)"', home)
    foot = re.findall(r'data-od-link="(chrome:FOOTER[^"]*)"', home)
    check("nav links carry chrome addresses", len(nav) > 20, f"{len(nav)} found")
    check("footer links carry chrome addresses", len(foot) > 15, f"{len(foot)} found")
    _, r = post("/api/link", {"slug": "index", "addr": foot[0],
                              "oldHref": "vitiligo.html", "href": "vitiligo-cost"})
    check("a footer link can be retargeted", r.get("ok") is True, str(r)[:110])
    check("it wrote to chrome.py", r.get("file") == "chrome.py", str(r.get("file")))
    check("and undone", post("/api/undo")[1].get("ok") is True)
    check("sources unchanged overall", drifted() == "", drifted()[:90])
    return 0


if __name__ == "__main__":
    try:
        main()
    finally:
        # Runs on a passing run, a failing one, and a crash halfway through an
        # edit. Silence here is the good outcome.
        healed = put_it_back()
        if healed:
            print(f"\nSAFETY NET: rewrote {len(healed)} file(s) the test left "
                  f"changed — {', '.join(healed)}")
            fails.append("test left the tree dirty")
    print(f"\n{len(fails)} failure(s)" + (": " + "; ".join(fails) if fails else ""))
    sys.exit(1 if fails else 0)
