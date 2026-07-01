#!/usr/bin/env python3
"""
Tool Registry — Formal schema definitions for every execution script.

Provides the orchestrator with structured knowledge of available tools:
  - What each script does (description)
  - What parameters it accepts (typed, required/optional, defaults)
  - What it returns
  - What env vars / API keys it needs
  - Cost estimates and side effects

Usage:
    python tool_registry.py list                        # List all tools
    python tool_registry.py list --category lead_gen    # Filter by category
    python tool_registry.py show scrape_google_maps     # Show full tool schema
    python tool_registry.py validate                    # Check all tool scripts exist
    python tool_registry.py export --format json        # Export full registry
    python tool_registry.py find "scrape leads"         # Search tools by description
"""

import os
import sys
import json
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REGISTRY_FILE = SCRIPT_DIR / "tool_registry.json"


def load_registry():
    """Load the tool registry from JSON."""
    if not REGISTRY_FILE.exists():
        print(f"ERROR: Registry file not found: {REGISTRY_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def list_tools(registry, category=None, verbose=False):
    """List all registered tools, optionally filtered by category."""
    tools = registry.get("tools", [])
    if category:
        tools = [t for t in tools if t.get("category", "") == category]

    if not tools:
        print("No tools found." + (f" (category={category})" if category else ""))
        return

    # Group by category
    by_cat = {}
    for t in tools:
        cat = t.get("category", "uncategorized")
        by_cat.setdefault(cat, []).append(t)

    for cat in sorted(by_cat):
        print(f"\n[{cat}]")
        for t in sorted(by_cat[cat], key=lambda x: x["name"]):
            safety = ""
            if t.get("side_effects"):
                safety = " [SIDE EFFECTS]"
            if t.get("requires_confirmation"):
                safety += " [NEEDS APPROVAL]"
            print(f"  {t['name']:35s} {t['description'][:60]}{safety}")
            if verbose:
                params = t.get("parameters", {})
                required = [k for k, v in params.items() if v.get("required")]
                if required:
                    print(f"    Required: {', '.join(required)}")
    print()


def show_tool(registry, tool_name):
    """Show the full schema for a specific tool."""
    tools = registry.get("tools", [])
    tool = next((t for t in tools if t["name"] == tool_name), None)
    if not tool:
        # Try partial match
        matches = [t for t in tools if tool_name in t["name"]]
        if matches:
            print(f"Tool '{tool_name}' not found. Did you mean:")
            for m in matches:
                print(f"  - {m['name']}")
            return
        print(f"Tool '{tool_name}' not found.")
        return

    print(f"\n{'='*60}")
    print(f"TOOL: {tool['name']}")
    print(f"{'='*60}")
    print(f"  Script:      {tool['script']}")
    print(f"  Description: {tool['description']}")
    print(f"  Category:    {tool.get('category', 'uncategorized')}")
    print(f"  Returns:     {tool.get('returns', 'unspecified')}")

    if tool.get("cost_estimate"):
        print(f"  Cost Est:    {tool['cost_estimate']}")
    if tool.get("side_effects"):
        print(f"  Side Effects: {', '.join(tool['side_effects'])}")
    if tool.get("requires_confirmation"):
        print(f"  REQUIRES HUMAN APPROVAL before execution")
    if tool.get("env_vars"):
        print(f"  Env Vars:    {', '.join(tool['env_vars'])}")

    params = tool.get("parameters", {})
    if params:
        print(f"\n  Parameters:")
        for name, spec in params.items():
            req = " (REQUIRED)" if spec.get("required") else ""
            default = f" [default: {spec['default']}]" if "default" in spec else ""
            ptype = spec.get("type", "string")
            print(f"    --{name:20s} {ptype:10s}{req}{default}")
            if spec.get("description"):
                print(f"      {spec['description']}")
    print()


def validate_registry(registry):
    """Check that all registered scripts actually exist."""
    tools = registry.get("tools", [])
    errors = []
    warnings = []

    for t in tools:
        script_path = SCRIPT_DIR / t["script"].replace("execution/", "")
        if not script_path.exists():
            errors.append(f"  MISSING: {t['name']} -> {t['script']}")

        # Check required env vars
        for var in t.get("env_vars", []):
            if not os.environ.get(var):
                warnings.append(f"  ENV NOT SET: {t['name']} needs {var}")

    print(f"\nValidation: {len(tools)} tools registered")
    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    {e}")
    else:
        print(f"  All scripts exist.")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"    {w}")
        if len(warnings) > 10:
            print(f"    ... and {len(warnings)-10} more")

    return len(errors) == 0


def find_tools(registry, query):
    """Search tools by name or description."""
    query_lower = query.lower()
    tools = registry.get("tools", [])
    matches = []
    for t in tools:
        searchable = f"{t['name']} {t['description']} {t.get('category', '')} {' '.join(t.get('tags', []))}".lower()
        if query_lower in searchable:
            matches.append(t)

    if not matches:
        print(f"No tools matching '{query}'.")
        return

    print(f"\nFound {len(matches)} tool(s) matching '{query}':")
    for t in matches:
        safety = " [NEEDS APPROVAL]" if t.get("requires_confirmation") else ""
        print(f"  {t['name']:35s} {t['description'][:60]}{safety}")


def get_tool_schema(registry, tool_name):
    """Get machine-readable schema for a tool (for LLM function calling)."""
    tools = registry.get("tools", [])
    tool = next((t for t in tools if t["name"] == tool_name), None)
    if not tool:
        return None
    return {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": {
            "type": "object",
            "properties": {
                name: {
                    "type": spec.get("type", "string"),
                    "description": spec.get("description", ""),
                    **({"default": spec["default"]} if "default" in spec else {}),
                    **({"enum": spec["enum"]} if "enum" in spec else {})
                }
                for name, spec in tool.get("parameters", {}).items()
            },
            "required": [
                name for name, spec in tool.get("parameters", {}).items()
                if spec.get("required")
            ]
        }
    }


def export_registry(registry, fmt="json"):
    """Export the full registry."""
    if fmt == "json":
        print(json.dumps(registry, indent=2))
    elif fmt == "schemas":
        # Export as OpenAI/Anthropic function-calling schemas
        schemas = []
        for t in registry.get("tools", []):
            schema = get_tool_schema(registry, t["name"])
            if schema:
                schemas.append(schema)
        print(json.dumps(schemas, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Tool Registry — Manage and inspect execution tool schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list
    p_list = subparsers.add_parser("list", help="List all tools")
    p_list.add_argument("--category", default=None, help="Filter by category")
    p_list.add_argument("--verbose", "-v", action="store_true")

    # show
    p_show = subparsers.add_parser("show", help="Show full tool schema")
    p_show.add_argument("tool_name", help="Tool name")

    # validate
    subparsers.add_parser("validate", help="Validate all tools exist")

    # find
    p_find = subparsers.add_parser("find", help="Search tools by description")
    p_find.add_argument("query", help="Search query")

    # export
    p_export = subparsers.add_parser("export", help="Export full registry")
    p_export.add_argument("--format", default="json", choices=["json", "schemas"])

    # schema (single tool as function-calling schema)
    p_schema = subparsers.add_parser("schema", help="Get function-calling schema for a tool")
    p_schema.add_argument("tool_name", help="Tool name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    registry = load_registry()

    if args.command == "list":
        list_tools(registry, category=args.category, verbose=args.verbose)
    elif args.command == "show":
        show_tool(registry, args.tool_name)
    elif args.command == "validate":
        valid = validate_registry(registry)
        sys.exit(0 if valid else 1)
    elif args.command == "find":
        find_tools(registry, args.query)
    elif args.command == "export":
        export_registry(registry, fmt=args.format)
    elif args.command == "schema":
        schema = get_tool_schema(registry, args.tool_name)
        if schema:
            print(json.dumps(schema, indent=2))
        else:
            print(f"Tool '{args.tool_name}' not found.")
            sys.exit(1)


if __name__ == "__main__":
    main()
