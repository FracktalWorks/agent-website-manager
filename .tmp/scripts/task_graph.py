#!/usr/bin/env python3
"""
Task Graph — DAG-based execution plans with checkpointing and resume.

Manages multi-step workflows as directed acyclic graphs (DAGs).
Each step has dependencies, status tracking, and can be resumed on failure.

Usage:
    python task_graph.py create "Lead Gen Pipeline" --steps steps.json
    python task_graph.py create "Quick task" --step "scrape:Scrape leads" --step "enrich:Enrich data:scrape"
    python task_graph.py run <plan_id>
    python task_graph.py run <plan_id> --from-step enrich       # Resume from step
    python task_graph.py status <plan_id>
    python task_graph.py list
    python task_graph.py mark <plan_id> <step_id> <status>      # Manual status update
    python task_graph.py show <plan_id>                          # Show full plan details
"""

import os
import sys
import json
import sqlite3
import argparse
import uuid
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
MEMORY_DIR = PROJECT_ROOT / "memory"
DB_PATH = MEMORY_DIR / "agent_memory.db"


def get_db():
    """Get database connection."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_tables(conn):
    """Create task graph tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS task_plans (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT DEFAULT '',
            status      TEXT DEFAULT 'pending',
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now')),
            started_at  TEXT DEFAULT NULL,
            completed_at TEXT DEFAULT NULL,
            metadata    TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS task_steps (
            id          TEXT NOT NULL,
            plan_id     TEXT NOT NULL,
            name        TEXT NOT NULL,
            description TEXT DEFAULT '',
            tool        TEXT DEFAULT '',
            tool_args   TEXT DEFAULT '{}',
            status      TEXT DEFAULT 'pending',
            depends_on  TEXT DEFAULT '[]',
            created_at  TEXT DEFAULT (datetime('now')),
            started_at  TEXT DEFAULT NULL,
            completed_at TEXT DEFAULT NULL,
            duration_s  REAL DEFAULT 0.0,
            output      TEXT DEFAULT '',
            error       TEXT DEFAULT '',
            retry_count INTEGER DEFAULT 0,
            requires_confirmation INTEGER DEFAULT 0,
            PRIMARY KEY (id, plan_id),
            FOREIGN KEY (plan_id) REFERENCES task_plans(id)
        );
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# PLAN MANAGEMENT
# ---------------------------------------------------------------------------

def create_plan(conn, name, description="", steps=None, metadata=None):
    """Create a new task plan with steps.
    
    Args:
        name: Plan name
        description: Plan description
        steps: List of step dicts with keys: id, name, description, tool, tool_args, depends_on, requires_confirmation
        metadata: Optional dict of plan metadata
    
    Returns:
        Plan ID
    """
    plan_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    
    conn.execute(
        "INSERT INTO task_plans (id, name, description, metadata) VALUES (?, ?, ?, ?)",
        (plan_id, name, description, json.dumps(metadata or {}))
    )
    
    if steps:
        for step in steps:
            depends_on = step.get("depends_on", [])
            if isinstance(depends_on, str):
                depends_on = [d.strip() for d in depends_on.split(",") if d.strip()]
            
            conn.execute("""
                INSERT INTO task_steps (id, plan_id, name, description, tool, tool_args, depends_on, requires_confirmation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                step["id"],
                plan_id,
                step.get("name", step["id"]),
                step.get("description", ""),
                step.get("tool", ""),
                json.dumps(step.get("tool_args", {})),
                json.dumps(depends_on),
                1 if step.get("requires_confirmation") else 0
            ))
    
    conn.commit()
    print(f"Created plan: {plan_id} ({name}) with {len(steps or [])} steps")
    return plan_id


def get_plan(conn, plan_id):
    """Get plan with all steps."""
    plan = conn.execute("SELECT * FROM task_plans WHERE id = ?", (plan_id,)).fetchone()
    if not plan:
        return None
    
    steps = conn.execute(
        "SELECT * FROM task_steps WHERE plan_id = ? ORDER BY rowid",
        (plan_id,)
    ).fetchall()
    
    return {
        "plan": dict(plan),
        "steps": [dict(s) for s in steps]
    }


def list_plans(conn, status=None, limit=20):
    """List all plans."""
    if status:
        rows = conn.execute(
            "SELECT * FROM task_plans WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM task_plans ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_ready_steps(conn, plan_id):
    """Get steps that are ready to execute (all dependencies completed)."""
    steps = conn.execute(
        "SELECT * FROM task_steps WHERE plan_id = ? AND status = 'pending'",
        (plan_id,)
    ).fetchall()
    
    completed = set()
    for s in conn.execute(
        "SELECT id FROM task_steps WHERE plan_id = ? AND status = 'completed'",
        (plan_id,)
    ).fetchall():
        completed.add(s["id"])
    
    ready = []
    for step in steps:
        deps = json.loads(step["depends_on"])
        if all(d in completed for d in deps):
            ready.append(dict(step))
    
    return ready


def mark_step(conn, plan_id, step_id, status, output="", error="", duration_s=0.0):
    """Update step status."""
    now = datetime.now().isoformat()
    
    updates = {"status": status, "output": output, "error": error}
    
    if status == "running":
        conn.execute(
            "UPDATE task_steps SET status=?, started_at=? WHERE id=? AND plan_id=?",
            (status, now, step_id, plan_id)
        )
    elif status in ("completed", "failed", "skipped"):
        conn.execute("""
            UPDATE task_steps SET status=?, completed_at=?, duration_s=?, output=?, error=?
            WHERE id=? AND plan_id=?
        """, (status, now, duration_s, output, error, step_id, plan_id))
    else:
        conn.execute(
            "UPDATE task_steps SET status=? WHERE id=? AND plan_id=?",
            (status, step_id, plan_id)
        )
    
    # Update plan status
    _update_plan_status(conn, plan_id)
    conn.commit()


def _update_plan_status(conn, plan_id):
    """Recalculate plan status based on step statuses."""
    steps = conn.execute(
        "SELECT status FROM task_steps WHERE plan_id = ?", (plan_id,)
    ).fetchall()
    
    if not steps:
        return
    
    statuses = [s["status"] for s in steps]
    now = datetime.now().isoformat()
    
    if all(s == "completed" for s in statuses):
        conn.execute(
            "UPDATE task_plans SET status='completed', completed_at=?, updated_at=? WHERE id=?",
            (now, now, plan_id)
        )
    elif any(s == "failed" for s in statuses):
        conn.execute(
            "UPDATE task_plans SET status='failed', updated_at=? WHERE id=?",
            (now, plan_id)
        )
    elif any(s == "running" for s in statuses):
        conn.execute(
            "UPDATE task_plans SET status='running', updated_at=? WHERE id=?",
            (now, plan_id)
        )
    elif any(s == "blocked" for s in statuses):
        conn.execute(
            "UPDATE task_plans SET status='blocked', updated_at=? WHERE id=?",
            (now, plan_id)
        )


def reset_from_step(conn, plan_id, step_id):
    """Reset a step and all downstream steps to 'pending' for re-execution."""
    # Find all steps that depend on this one (transitively)
    all_steps = conn.execute(
        "SELECT id, depends_on FROM task_steps WHERE plan_id = ?", (plan_id,)
    ).fetchall()
    
    to_reset = {step_id}
    changed = True
    while changed:
        changed = False
        for s in all_steps:
            if s["id"] not in to_reset:
                deps = json.loads(s["depends_on"])
                if any(d in to_reset for d in deps):
                    to_reset.add(s["id"])
                    changed = True
    
    for sid in to_reset:
        conn.execute("""
            UPDATE task_steps SET status='pending', started_at=NULL, completed_at=NULL,
                duration_s=0.0, output='', error=''
            WHERE id=? AND plan_id=?
        """, (sid, plan_id))
    
    conn.execute(
        "UPDATE task_plans SET status='pending', updated_at=? WHERE id=?",
        (datetime.now().isoformat(), plan_id)
    )
    conn.commit()
    print(f"Reset {len(to_reset)} step(s): {', '.join(sorted(to_reset))}")


def show_plan(conn, plan_id, as_json=False):
    """Display plan status with visual DAG."""
    data = get_plan(conn, plan_id)
    if not data:
        print(f"Plan not found: {plan_id}")
        return
    
    plan = data["plan"]
    steps = data["steps"]
    
    if as_json:
        # Parse JSON strings for clean output
        for s in steps:
            s["depends_on"] = json.loads(s["depends_on"]) if isinstance(s["depends_on"], str) else s["depends_on"]
            s["tool_args"] = json.loads(s["tool_args"]) if isinstance(s["tool_args"], str) else s["tool_args"]
        plan["metadata"] = json.loads(plan["metadata"]) if isinstance(plan["metadata"], str) else plan["metadata"]
        print(json.dumps(data, indent=2, default=str))
        return
    
    icons = {
        "pending": "[ ]", "running": "[~]", "completed": "[+]",
        "failed": "[X]", "skipped": "[-]", "blocked": "[!]"
    }
    
    print(f"\n{'='*60}")
    print(f"PLAN: {plan['name']}")
    print(f"{'='*60}")
    print(f"  ID:      {plan['id']}")
    print(f"  Status:  {plan['status'].upper()}")
    print(f"  Created: {plan['created_at']}")
    if plan.get("started_at"):
        print(f"  Started: {plan['started_at']}")
    if plan.get("completed_at"):
        print(f"  Done:    {plan['completed_at']}")
    
    print(f"\n  Steps ({len(steps)}):")
    for s in steps:
        icon = icons.get(s["status"], "[?]")
        deps = json.loads(s["depends_on"]) if isinstance(s["depends_on"], str) else s["depends_on"]
        dep_str = f" (after: {', '.join(deps)})" if deps else ""
        conf_str = " [NEEDS APPROVAL]" if s["requires_confirmation"] else ""
        tool_str = f" [{s['tool']}]" if s["tool"] else ""
        
        print(f"    {icon} {s['id']:20s} {s['name']}{tool_str}{dep_str}{conf_str}")
        
        if s["status"] == "completed" and s.get("duration_s"):
            print(f"        Done in {s['duration_s']:.1f}s")
        if s["status"] == "failed" and s.get("error"):
            print(f"        ERROR: {s['error'][:100]}")
        if s.get("output") and s["status"] == "completed":
            output_preview = s["output"][:100]
            print(f"        Output: {output_preview}")
    
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Task Graph — DAG-based task plans with checkpointing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # create
    p_create = subparsers.add_parser("create", help="Create a new task plan")
    p_create.add_argument("name", help="Plan name")
    p_create.add_argument("--description", "-d", default="", help="Plan description")
    p_create.add_argument("--steps", help="JSON file with step definitions")
    p_create.add_argument("--step", action="append", default=[],
        help="Inline step: 'id:name[:dep1,dep2]' (repeatable)")

    # show
    p_show = subparsers.add_parser("show", help="Show plan details")
    p_show.add_argument("plan_id", help="Plan ID")
    p_show.add_argument("--json", action="store_true")

    # list
    p_list = subparsers.add_parser("list", help="List all plans")
    p_list.add_argument("--status", default=None, help="Filter by status")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--json", action="store_true")

    # ready
    p_ready = subparsers.add_parser("ready", help="Show steps ready to execute")
    p_ready.add_argument("plan_id", help="Plan ID")
    p_ready.add_argument("--json", action="store_true")

    # mark
    p_mark = subparsers.add_parser("mark", help="Update step status")
    p_mark.add_argument("plan_id", help="Plan ID")
    p_mark.add_argument("step_id", help="Step ID")
    p_mark.add_argument("status", choices=["pending", "running", "completed", "failed", "skipped", "blocked"])
    p_mark.add_argument("--output", default="")
    p_mark.add_argument("--error", default="")
    p_mark.add_argument("--duration", type=float, default=0.0)

    # reset
    p_reset = subparsers.add_parser("reset", help="Reset step and downstream for re-execution")
    p_reset.add_argument("plan_id", help="Plan ID")
    p_reset.add_argument("step_id", help="Step ID to reset from")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()
    init_tables(conn)

    try:
        if args.command == "create":
            steps = []
            
            # From JSON file
            if args.steps:
                with open(args.steps, "r", encoding="utf-8") as f:
                    steps = json.load(f)
            
            # From inline --step flags
            for step_str in args.step:
                parts = step_str.split(":")
                step_def = {"id": parts[0], "name": parts[1] if len(parts) > 1 else parts[0]}
                if len(parts) > 2 and parts[2]:
                    step_def["depends_on"] = parts[2].split(",")
                steps.append(step_def)
            
            if not steps:
                print("ERROR: Provide steps via --steps file or --step flags")
                sys.exit(1)
            
            plan_id = create_plan(conn, args.name, args.description, steps)
            show_plan(conn, plan_id)

        elif args.command == "show":
            show_plan(conn, args.plan_id, as_json=getattr(args, 'json', False))

        elif args.command == "list":
            plans = list_plans(conn, status=args.status, limit=args.limit)
            if getattr(args, 'json', False):
                print(json.dumps(plans, indent=2, default=str))
            else:
                if not plans:
                    print("No plans found.")
                else:
                    print(f"\n{'ID':25s} {'Status':12s} {'Name':30s} Created")
                    print("-" * 85)
                    for p in plans:
                        print(f"{p['id']:25s} {p['status']:12s} {p['name']:30s} {p['created_at']}")

        elif args.command == "ready":
            ready = get_ready_steps(conn, args.plan_id)
            if getattr(args, 'json', False):
                for s in ready:
                    s["depends_on"] = json.loads(s["depends_on"]) if isinstance(s["depends_on"], str) else s["depends_on"]
                    s["tool_args"] = json.loads(s["tool_args"]) if isinstance(s["tool_args"], str) else s["tool_args"]
                print(json.dumps(ready, indent=2, default=str))
            else:
                if not ready:
                    print("No steps ready (all completed or waiting on dependencies).")
                else:
                    print(f"\nReady to execute ({len(ready)} steps):")
                    for s in ready:
                        conf = " [NEEDS APPROVAL]" if s["requires_confirmation"] else ""
                        print(f"  {s['id']:20s} {s['name']}{conf}")

        elif args.command == "mark":
            mark_step(conn, args.plan_id, args.step_id, args.status,
                      output=args.output, error=args.error, duration_s=args.duration)
            print(f"Step '{args.step_id}' -> {args.status}")

        elif args.command == "reset":
            reset_from_step(conn, args.plan_id, args.step_id)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
