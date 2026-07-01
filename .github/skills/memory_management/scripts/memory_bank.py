#!/usr/bin/env python3
"""
Memory Bank — JSON/Markdown Working Memory (Tier 1)

Provides fast, structured working memory for agents using JSON and Markdown files.
Complements memory_db.py (SQLite, Tier 2) which handles long-term search.

Default memory files:
  - context.json       — Current state, active projects, goals, challenges
  - interaction_log.json — Past conversation summaries with topics and follow-ups
  - decision_journal.json — Decisions made with reasoning and outcome tracking
  - insights.md         — Accumulated wisdom and lessons learned (append-only)

Custom memory files can be registered via --register <name> <filename>.

Usage:
    python memory_bank.py --read context              # Read one memory file
    python memory_bank.py --read all                  # Read everything
    python memory_bank.py --status                    # Check what's populated
    python memory_bank.py --update context --key "stage" --value "growth"
    python memory_bank.py --update context --data '{"stage": "growth"}'
    python memory_bank.py --log-interaction --summary "Discussed launch plan"
    python memory_bank.py --log-decision --decision "Go with vendor A" --context "Better SLA"
    python memory_bank.py --update-outcome 1 --outcome "Vendor delivered on time"
    python memory_bank.py --add-insight "Always validate API responses before caching"
    python memory_bank.py --search "funding"
    python memory_bank.py --register birth_chart birth_chart.json
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
MEMORY_DIR = PROJECT_ROOT / "memory"
REGISTRY_FILE = MEMORY_DIR / "_memory_registry.json"

# Default memory files every agent gets
DEFAULT_MEMORY_FILES = {
    "context": "context.json",
    "interaction_log": "interaction_log.json",
    "decision_journal": "decision_journal.json",
    "insights": "insights.md"
}


def load_memory_files():
    """Load memory file registry (defaults + custom)."""
    files = DEFAULT_MEMORY_FILES.copy()
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            custom = json.loads(f.read().strip() or "{}")
            files.update(custom)
    return files


def save_registry(custom_files):
    """Save custom memory file registrations."""
    ensure_memory_dir()
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_files, f, indent=2)


def ensure_memory_dir():
    """Ensure memory directory exists."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def read_memory(memory_type):
    """
    Read a memory file.

    Args:
        memory_type: Key from memory files registry (e.g., 'context', 'interaction_log')

    Returns:
        Contents of the memory file (dict for JSON, string for MD)
    """
    memory_files = load_memory_files()
    if memory_type not in memory_files:
        print(f"Error: Unknown memory type '{memory_type}'. Available: {', '.join(memory_files.keys())}")
        return None

    filepath = MEMORY_DIR / memory_files[memory_type]

    if not filepath.exists():
        print(f"Memory file not found: {filepath}")
        return {} if filepath.suffix == ".json" else ""

    if filepath.suffix == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()


def read_all_memory():
    """Read all memory files and return combined state."""
    memory_files = load_memory_files()
    state = {}
    for memory_type in memory_files:
        state[memory_type] = read_memory(memory_type)
    return state


def write_memory(memory_type, data):
    """
    Write data to a memory file.

    Args:
        memory_type: Memory file key
        data: Dict (for JSON files) or string (for MD files)
    """
    ensure_memory_dir()
    memory_files = load_memory_files()
    filepath = MEMORY_DIR / memory_files[memory_type]

    if filepath.suffix == ".json":
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(data)

    print(f"Updated memory: {memory_type}")


def deep_merge(base, override):
    """Deep merge two dicts. Override wins on conflicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def set_nested(d, key_path, value):
    """Set a value using dot notation path. E.g., 'goals.q2' -> d['goals']['q2']"""
    keys = key_path.split(".")
    current = d
    for k in keys[:-1]:
        if k not in current or not isinstance(current[k], dict):
            current[k] = {}
        current = current[k]

    # Try to parse value as JSON for complex values
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
        current[keys[-1]] = parsed
    except (json.JSONDecodeError, TypeError):
        current[keys[-1]] = value


def update_memory(memory_type, key=None, value=None, data=None):
    """
    Update a specific field or merge data into a memory file.

    Args:
        memory_type: Memory file key
        key: Specific key to update (dot notation supported: "goals.q2")
        value: Value for the key
        data: Full dict to merge (alternative to key/value)
    """
    current = read_memory(memory_type)
    if current is None:
        current = {}

    if isinstance(current, str):
        # For markdown files, append data
        if data:
            current += f"\n{data}"
        write_memory(memory_type, current)
        return

    if data:
        if isinstance(data, str):
            data = json.loads(data)
        current = deep_merge(current, data)
    elif key and value is not None:
        set_nested(current, key, value)

    # Add last_updated timestamp
    current["_last_updated"] = datetime.now().isoformat()

    write_memory(memory_type, current)


def log_interaction(summary, topics=None, advice_given=None, follow_ups=None):
    """
    Log an interaction to the interaction log.

    Args:
        summary: Brief summary of the conversation
        topics: List of topics discussed
        advice_given: List of advice/recommendations given
        follow_ups: List of follow-up items
    """
    log = read_memory("interaction_log")
    if not isinstance(log, dict):
        log = {}
    if "interactions" not in log:
        log["interactions"] = []

    entry = {
        "date": datetime.now().isoformat(),
        "summary": summary,
        "topics": topics or [],
        "advice_given": advice_given or [],
        "follow_ups": follow_ups or [],
        "interaction_number": len(log["interactions"]) + 1
    }

    log["interactions"].append(entry)
    log["total_interactions"] = len(log["interactions"])
    log["_last_updated"] = datetime.now().isoformat()

    write_memory("interaction_log", log)
    return entry


def log_decision(decision, context=None, reasoning=None, expected_outcome=None):
    """
    Log a decision to the decision journal.

    Args:
        decision: What was decided
        context: Business/technical context
        reasoning: Why this decision was made
        expected_outcome: What we expect to happen
    """
    journal = read_memory("decision_journal")
    if not isinstance(journal, dict):
        journal = {}
    if "decisions" not in journal:
        journal["decisions"] = []

    entry = {
        "id": len(journal["decisions"]) + 1,
        "date": datetime.now().isoformat(),
        "decision": decision,
        "context": context or "",
        "reasoning": reasoning or "",
        "expected_outcome": expected_outcome or "",
        "actual_outcome": None,
        "status": "pending",
        "outcome_recorded": False
    }

    journal["decisions"].append(entry)
    journal["total_decisions"] = len(journal["decisions"])
    journal["_last_updated"] = datetime.now().isoformat()

    write_memory("decision_journal", journal)
    return entry


def update_decision_outcome(decision_id, actual_outcome, status="completed"):
    """Update the outcome of a previously logged decision."""
    journal = read_memory("decision_journal")
    if not isinstance(journal, dict) or "decisions" not in journal:
        print("Error: No decision journal found")
        return

    for entry in journal["decisions"]:
        if entry["id"] == decision_id:
            entry["actual_outcome"] = actual_outcome
            entry["status"] = status
            entry["outcome_recorded"] = True
            entry["outcome_date"] = datetime.now().isoformat()
            write_memory("decision_journal", journal)
            print(f"Updated decision #{decision_id} outcome")
            return

    print(f"Decision #{decision_id} not found")


def add_insight(insight_text, category=None):
    """
    Add an insight to the insights file (append-only).

    Args:
        insight_text: The insight to record
        category: Optional category tag
    """
    filepath = MEMORY_DIR / "insights.md"

    content = ""
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

    if not content.strip():
        content = "# Accumulated Insights\n\n_Lessons learned, patterns observed, and wisdom collected over time._\n\n"

    date_str = datetime.now().strftime("%Y-%m-%d")
    category_tag = f" [{category}]" if category else ""
    content += f"\n### {date_str}{category_tag}\n- {insight_text}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Insight added to {filepath}")


def search_memory(query):
    """
    Search across all memory files for relevant information.

    Args:
        query: Search term

    Returns:
        Dict of matches by memory type
    """
    query_lower = query.lower()
    memory_files = load_memory_files()
    results = {}

    for memory_type in memory_files:
        data = read_memory(memory_type)
        matches = []

        if isinstance(data, dict):
            matches = _search_dict(data, query_lower)
        elif isinstance(data, str):
            for i, line in enumerate(data.split("\n")):
                if query_lower in line.lower():
                    matches.append({"line": i + 1, "text": line.strip()})

        if matches:
            results[memory_type] = matches

    return results


def _search_dict(d, query, path=""):
    """Recursively search a dict for query matches."""
    matches = []
    for key, value in d.items():
        current_path = f"{path}.{key}" if path else key
        if isinstance(value, dict):
            matches.extend(_search_dict(value, query, current_path))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    matches.extend(_search_dict(item, query, f"{current_path}[{i}]"))
                elif isinstance(item, str) and query in item.lower():
                    matches.append({"path": f"{current_path}[{i}]", "value": item})
        elif isinstance(value, str) and query in value.lower():
            matches.append({"path": current_path, "value": value})
    return matches


def get_memory_summary():
    """Get a brief summary of what's stored in memory."""
    memory_files = load_memory_files()
    summary = {}
    for memory_type, filename in memory_files.items():
        filepath = MEMORY_DIR / filename
        if filepath.exists():
            if filepath.suffix == ".json":
                data = read_memory(memory_type)
                if isinstance(data, dict):
                    summary[memory_type] = {
                        "file": filename,
                        "status": "populated" if len(data) > 1 else "empty",
                        "keys": list(data.keys())[:10],
                        "last_updated": data.get("_last_updated", "unknown")
                    }
                else:
                    summary[memory_type] = {"file": filename, "status": "empty"}
            else:
                content = read_memory(memory_type)
                summary[memory_type] = {
                    "file": filename,
                    "status": "populated" if content.strip() else "empty",
                    "lines": len(content.split("\n")) if content else 0
                }
        else:
            summary[memory_type] = {"file": filename, "status": "not_created"}

    return summary


def register_memory_type(name, filename):
    """Register a custom memory file type."""
    ensure_memory_dir()
    custom = {}
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                custom = json.loads(content)
    custom[name] = filename
    save_registry(custom)
    print(f"Registered memory type: {name} -> {filename}")


def init_memory():
    """Initialize memory directory with empty default files."""
    ensure_memory_dir()
    memory_files = load_memory_files()
    created = 0
    for memory_type, filename in memory_files.items():
        filepath = MEMORY_DIR / filename
        if not filepath.exists():
            if filepath.suffix == ".json":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=2)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("# Accumulated Insights\n\n_Lessons learned, patterns observed, and wisdom collected over time._\n\n")
            created += 1
    print(f"Memory initialized: {created} file(s) created in {MEMORY_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Memory Bank — JSON/Markdown Working Memory (Tier 1)")
    parser.add_argument("--read", type=str, help="Read a memory type (or 'all')")
    parser.add_argument("--update", type=str, help="Memory type to update")
    parser.add_argument("--key", type=str, help="Key to update (dot notation)")
    parser.add_argument("--value", type=str, help="Value to set")
    parser.add_argument("--data", type=str, help="JSON data to merge")
    parser.add_argument("--log-interaction", action="store_true", help="Log an interaction")
    parser.add_argument("--summary", type=str, help="Interaction summary")
    parser.add_argument("--topics", type=str, help="Comma-separated topics")
    parser.add_argument("--log-decision", action="store_true", help="Log a decision")
    parser.add_argument("--decision", type=str, help="Decision text")
    parser.add_argument("--context", type=str, help="Decision context")
    parser.add_argument("--reasoning", type=str, help="Decision reasoning")
    parser.add_argument("--add-insight", type=str, help="Add an insight")
    parser.add_argument("--category", type=str, help="Insight category")
    parser.add_argument("--search", type=str, help="Search all memory for a term")
    parser.add_argument("--status", action="store_true", help="Show memory bank status")
    parser.add_argument("--update-outcome", type=int, help="Decision ID to update outcome")
    parser.add_argument("--outcome", type=str, help="Actual outcome text")
    parser.add_argument("--register", nargs=2, metavar=("NAME", "FILENAME"),
                        help="Register a custom memory type")
    parser.add_argument("--init", action="store_true", help="Initialize memory directory with default files")

    args = parser.parse_args()

    if args.init:
        init_memory()

    elif args.read:
        if args.read == "all":
            data = read_all_memory()
        else:
            data = read_memory(args.read)
        print(json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, dict) else data)

    elif args.update:
        update_memory(args.update, key=args.key, value=args.value, data=args.data)

    elif args.log_interaction:
        if not args.summary:
            print("Error: --summary required for logging interaction")
            sys.exit(1)
        topics = args.topics.split(",") if args.topics else []
        entry = log_interaction(args.summary, topics=topics)
        print(json.dumps(entry, indent=2))

    elif args.log_decision:
        if not args.decision:
            print("Error: --decision required")
            sys.exit(1)
        entry = log_decision(args.decision, context=args.context, reasoning=args.reasoning)
        print(json.dumps(entry, indent=2))

    elif args.update_outcome is not None and args.outcome:
        update_decision_outcome(args.update_outcome, args.outcome)

    elif args.add_insight:
        add_insight(args.add_insight, category=args.category)

    elif args.search:
        results = search_memory(args.search)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.status:
        summary = get_memory_summary()
        print(json.dumps(summary, indent=2))

    elif args.register:
        register_memory_type(args.register[0], args.register[1])

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
