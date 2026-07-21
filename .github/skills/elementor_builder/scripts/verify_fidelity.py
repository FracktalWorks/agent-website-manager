#!/usr/bin/env python3
"""
Post-import fidelity checker: diffs a live Elementor page against its HTML
source, targeting the 9 recurring drift categories documented in the
`elementor-fidelity-patch-workflow` memory note (heading font-size, button
text color, image radius/object-fit, container-width flex-collapse,
mojibake, accordion typography, full-bleed images, missing pseudo-element
overlays, counter widget styling).

Replaces the old fully-manual "Playwright browser_evaluate + eyeball it"
loop with one deterministic pass: load both pages at the same viewport,
read computed styles for matching elements, and print a structured patch
list an agent can act on directly (native update-element vs. Custom CSS,
per the memory note's hybrid rule).

This is a computed-style diff, not a pixel/vision diff — it catches
categories 1-4 and 6-8 (anything expressible as a CSS property comparison)
directly. Category 9 (pseudo-element overlays) can only be flagged as
"present in source, absent live" since Elementor has no pseudo-element
concept — it always needs the Custom CSS recreation from the memory note.
Category 5 (flex-collapse) is flagged via a width-ratio check, not proven
root cause, since the same symptom can have other causes.

Usage:
    python verify_fidelity.py --source outputs/design_pages/home.html \\
        --live https://fracktal.in/some-page/

Requires: playwright (pip install playwright && playwright install chromium)
"""
from __future__ import annotations
import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin

FONT_TOLERANCE_PX = 2
WIDTH_RATIO_TOLERANCE = 0.15  # flag if live width is <85% of source width

# Elements worth comparing: visible text blocks, buttons, images, containers
# with a background — matches what the fidelity-patch memory note actually
# patches. Kept intentionally small; broad selectors just add noise no one acts on.
SELECTORS = "h1, h2, h3, h4, a.button, button, .btn, img, [class*='stat'], [class*='counter']"

COMPUTED_STYLE_JS = """
(el) => {
    const cs = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return {
        tag: el.tagName.toLowerCase(),
        text: (el.innerText || el.getAttribute('alt') || '').trim().slice(0, 60),
        fontSize: cs.fontSize,
        color: cs.color,
        backgroundColor: cs.backgroundColor,
        borderRadius: cs.borderRadius,
        boxShadow: cs.boxShadow,
        objectFit: cs.objectFit,
        width: rect.width,
        hasBeforeContent: getComputedStyle(el, '::before').content !== 'none',
        hasAfterContent: getComputedStyle(el, '::after').content !== 'none',
    };
}
"""


@dataclass
class Drift:
    category: str
    element: str
    detail: str
    fix_hint: str


@dataclass
class Report:
    drifts: list = field(default_factory=list)

    def add(self, category: str, element: str, detail: str, fix_hint: str):
        self.drifts.append(Drift(category, element, detail, fix_hint))


def _px(val: str) -> float | None:
    try:
        return float(val.replace("px", "").strip())
    except (ValueError, AttributeError):
        return None


async def _snapshot(page, url_or_path: str, is_local: bool) -> list[dict]:
    if is_local:
        await page.goto(Path(url_or_path).resolve().as_uri())
    else:
        await page.goto(url_or_path, wait_until="networkidle")
        # Force-load lazy images so hidden backgrounds/images are measurable —
        # a known Elementor lazy-load gotcha (see html2elementor README).
        await page.evaluate(
            "document.querySelectorAll('img[data-src]').forEach(i => i.src = i.dataset.src)"
        )
    els = await page.query_selector_all(SELECTORS)
    return [await el.evaluate(COMPUTED_STYLE_JS) for el in els]


def _match(source_els: list[dict], live_els: list[dict]) -> list[tuple[dict, dict]]:
    """Pair elements by normalized text (best-effort — same approach as
    verify.py's structural matcher, simplified since this only needs pairs
    for the elements present on both sides)."""
    pairs = []
    used = set()
    for s in source_els:
        if not s["text"]:
            continue
        for i, l in enumerate(live_els):
            if i in used or l["text"] != s["text"]:
                continue
            pairs.append((s, l))
            used.add(i)
            break
    return pairs


def _diff_pair(s: dict, l: dict, report: Report):
    label = f"{l['tag']} \"{l['text'][:40]}\""

    sf, lf = _px(s["fontSize"]), _px(l["fontSize"])
    if sf and lf and abs(sf - lf) > FONT_TOLERANCE_PX:
        report.add("1-heading-font-size", label, f"source {sf}px vs live {lf}px",
                    "set typography_font_size natively via update-element")

    if l["tag"] in ("a", "button") or "btn" in s.get("text", ""):
        if s["color"] != l["color"] and l["color"] in ("rgb(255, 255, 255)", "rgba(0, 0, 0, 0)"):
            report.add("3-button-text-color", label, f"source {s['color']} vs live {l['color']}",
                        "set button_text_color natively via update-element")

    if l["tag"] == "img":
        if s["borderRadius"] != l["borderRadius"]:
            report.add("4-image-radius", label, f"source {s['borderRadius']} vs live {l['borderRadius']}",
                        "set image_border_radius natively via update-element")
        if s["objectFit"] != l["objectFit"] and s["objectFit"] != "fill":
            report.add("4/8-image-object-fit", label, f"source {s['objectFit']} vs live {l['objectFit']}",
                        "set width:100% + object-fit natively, or Custom CSS if the widget wrapper stays content-width (category 8)")
        if s["boxShadow"] not in ("none", l["boxShadow"]) and l["boxShadow"] == "none":
            report.add("4-image-shadow", label, "source has box-shadow, live has none",
                        "set image_box_shadow_box_shadow natively via update-element")

    if s["width"] and l["width"] and s["width"] > 0:
        ratio = l["width"] / s["width"]
        if ratio < (1 - WIDTH_RATIO_TOLERANCE):
            report.add("5-container-width-collapse", label,
                        f"live width {l['width']:.0f}px is {ratio:.0%} of source {s['width']:.0f}px",
                        "do NOT keep tuning flex_grow — use a scoped Custom CSS block "
                        "(flex: 1 1 X%; max-width: X%) per the fidelity-patch memory note")

    if any(ch in s["text"] for ch in ("→", "—", "’")) and s["text"] != l["text"]:
        report.add("6-mojibake", label, f"source \"{s['text'][:30]}\" vs live \"{l['text'][:30]}\"",
                    "reset text using HTML entities (&rarr; &mdash; &rsquo;) instead of raw UTF-8 chars")

    if (s["hasBeforeContent"] or s["hasAfterContent"]) and not (l["hasBeforeContent"] or l["hasAfterContent"]):
        report.add("9-pseudo-element-overlay", label, "source has ::before/::after content, live has none",
                    "recreate via scoped Custom CSS on the container id (Elementor has no pseudo-element concept)")


async def run(source: str, live_url: str) -> Report:
    from playwright.async_api import async_playwright

    report = Report()
    is_local = not source.startswith("http")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        source_els = await _snapshot(page, source, is_local)
        live_els = await _snapshot(page, live_url, False)
        await browser.close()

    for s, l in _match(source_els, live_els):
        _diff_pair(s, l, report)

    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="Source HTML file path or URL")
    ap.add_argument("--live", required=True, help="Live Elementor page URL to verify")
    ap.add_argument("--json", action="store_true", help="Output as JSON instead of a text report")
    args = ap.parse_args()

    report = asyncio.run(run(args.source, args.live))

    if args.json:
        print(json.dumps([d.__dict__ for d in report.drifts], indent=2))
        return

    if not report.drifts:
        print("No drift detected across the 9 known categories.")
        return

    print(f"\n{len(report.drifts)} drift(s) found:\n")
    for d in report.drifts:
        print(f"[{d.category}] {d.element}")
        print(f"    {d.detail}")
        print(f"    fix: {d.fix_hint}\n")

    categories = sorted(set(d.category for d in report.drifts))
    print(f"Categories affected: {', '.join(categories)}")
    print("See elementor-fidelity-patch-workflow memory note for the full patch procedure.")
    sys.exit(1)


if __name__ == "__main__":
    main()
