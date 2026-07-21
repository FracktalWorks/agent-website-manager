"""html2elementor — Convert HTML+CSS to Elementor JSON.

Usage:
    from html2elementor import convert
    result = convert(html_string)
    # result["layout"]  → Elementor _elementor_data JSON array
    # result["kit"]     → Site Settings (colors + typography globals)

CLI:
    python3 -m html2elementor input.html -o layout.json
"""
from __future__ import annotations
import json
from typing import Any

from .parser import parse_html
from .sections import detect_sections, classify_section
from .containers import map_section
from .builder import build_layout
from .globals import build_kit

__version__ = "0.1.0"


def convert(html: str, html_path: str | None = None,
            extra_css: list[str] | None = None) -> dict[str, Any]:
    """Convert an HTML string to Elementor layout + kit globals.

    Returns dict with:
        "layout": list[dict] — _elementor_data sections
        "kit": dict — site settings (system_colors, custom_colors, system_typography)
        "color_map": dict — {hex: global_id}
        "font_map": dict — {font_name: global_id}
    """
    capture = parse_html(html, html_path=html_path, extra_css=extra_css)

    # Build globals kit from all colors/fonts in the HTML
    kit_settings, color_map, font_map, typo_map = build_kit(capture)

    sections = detect_sections(capture)

    mapped: list[tuple[dict, list[dict]]] = []
    for sec in sections:
        role = classify_section(sec)
        container, elements = map_section(sec)
        container["_title"] = role
        mapped.append((container, elements))

    layout = build_layout(mapped)

    # Post-pass: replace literal colors/fonts with __globals__ refs
    _apply_globals(layout, color_map, font_map, typo_map)

    return {
        "layout": layout,
        "kit": kit_settings,
        "color_map": color_map,
        "font_map": font_map,
    }


def convert_to_json(html: str, indent: int = 2) -> str:
    result = convert(html)
    return json.dumps(result["layout"], indent=indent, ensure_ascii=False)


def _apply_globals(layout: list[dict], color_map: dict, font_map: dict, typo_map: dict | None = None) -> None:
    """Recursively walk layout and replace literal color/font values with globals refs."""
    for element in layout:
        _apply_globals_to_element(element, color_map, font_map, typo_map)


def _apply_globals_to_element(el: dict, color_map: dict, font_map: dict, typo_map: dict | None = None) -> None:
    settings = el.get("settings", {})
    globals_dict = settings.setdefault("__globals__", {})

    # NOTE: We deliberately DO NOT convert literal color values into
    # `globals/colors?id=<hash>` references. A custom-color global ref only
    # renders if that exact color exists in the active Elementor kit's
    # custom_colors — a fragile dependency that fails silently on pages written
    # via the REST API (the kit merge doesn't apply, or the generated id doesn't
    # match), leaving backgrounds transparent and colored text unstyled. That is
    # exactly what made the HSN page's dark hero band render as white-on-white.
    # Keeping the direct hex value makes every page self-contained and reliable;
    # Elementor renders literal colors with no kit lookup. (color_map is still
    # used by build_kit to populate the editor's color palette.) System-color
    # globals that widgets.py sets directly (e.g. title_color -> id=text) are
    # left untouched — those resolve reliably because system colors exist in
    # every kit by default.

    # Typography: keep any explicit `custom` typography as DIRECT per-widget
    # values (self-contained, exact fidelity — no kit lookup). Only widgets
    # WITHOUT custom typography get assigned a system typography role global
    # (primary/secondary/accent/text); those are system entries present in every
    # kit by default, so they resolve reliably. We no longer convert custom
    # typography into custom-hash global refs, for the same kit-resolution
    # fragility reason as colors above.
    widget_type = el.get("widgetType", "")
    header_size = settings.get("header_size", "")

    if settings.get("typography_typography") != "custom":
        if widget_type == "heading":
            typo_role = "primary" if header_size in ("h1", "h2") else "secondary"
        elif widget_type == "button":
            typo_role = "accent"
        else:
            typo_role = "text"
        globals_dict["typography_typography"] = f"globals/typography?id={typo_role}"

    # Clean empty __globals__
    if not globals_dict:
        settings.pop("__globals__", None)

    # Recurse into children
    for child in el.get("elements", []):
        _apply_globals_to_element(child, color_map, font_map, typo_map)
