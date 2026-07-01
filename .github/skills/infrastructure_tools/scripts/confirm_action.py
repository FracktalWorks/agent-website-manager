#!/usr/bin/env python3
"""
Human-in-the-Loop — Approval gates for irreversible agent actions.

Provides a confirmation mechanism that adapts to the deployment mode:
  - Copilot mode: Outputs a clear prompt for the LLM to present to the user
  - Interactive mode: stdin prompt
  - Auto-approve mode: For testing/CI (AGENT_AUTO_APPROVE=true)
  - File-based mode: Write approval request, poll for response

Usage (from other scripts):
    from confirm_action import confirm, check_tool_approval

    if confirm("Send 50 cold emails via Instantly?", details={"count": 50, "campaign": "Q1 outreach"}):
        # proceed with action
    else:
        # action was denied

Usage (CLI — for orchestrator to call):
    python confirm_action.py request "Send 50 emails" --details '{"count": 50}'
    python confirm_action.py check <request_id>
    python confirm_action.py approve <request_id>
    python confirm_action.py deny <request_id>
    python confirm_action.py list-pending
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

# Auto-approve mode for testing/CI
AUTO_APPROVE = os.environ.get("AGENT_AUTO_APPROVE", "").lower() in ("true", "1", "yes")
# Confirmation mode: interactive, file, auto
CONFIRM_MODE = os.environ.get("AGENT_CONFIRM_MODE", "interactive")


def get_db():
    """Get database connection."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_tables(conn):
    """Create approval tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS approval_requests (
            id          TEXT PRIMARY KEY,
            action      TEXT NOT NULL,
            details     TEXT DEFAULT '{}',
            tool_name   TEXT DEFAULT '',
            plan_id     TEXT DEFAULT '',
            step_id     TEXT DEFAULT '',
            status      TEXT DEFAULT 'pending',
            risk_level  TEXT DEFAULT 'medium',
            created_at  TEXT DEFAULT (datetime('now')),
            resolved_at TEXT DEFAULT NULL,
            resolved_by TEXT DEFAULT '',
            reason      TEXT DEFAULT ''
        );
    """)
    conn.commit()


def create_request(conn, action, details=None, tool_name="", plan_id="",
                   step_id="", risk_level="medium"):
    """Create an approval request.
    
    Returns:
        (request_id, auto_approved) tuple
    """
    request_id = "apr-" + uuid.uuid4().hex[:8]
    
    conn.execute("""
        INSERT INTO approval_requests (id, action, details, tool_name, plan_id, step_id, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (request_id, action, json.dumps(details or {}), tool_name, plan_id, step_id, risk_level))
    conn.commit()
    
    # Auto-approve if configured
    if AUTO_APPROVE:
        resolve_request(conn, request_id, "approved", resolved_by="auto")
        return request_id, True
    
    return request_id, False


def resolve_request(conn, request_id, status, resolved_by="user", reason=""):
    """Resolve an approval request (approve or deny)."""
    conn.execute("""
        UPDATE approval_requests 
        SET status=?, resolved_at=?, resolved_by=?, reason=?
        WHERE id=?
    """, (status, datetime.now().isoformat(), resolved_by, reason, request_id))
    conn.commit()


def get_request(conn, request_id):
    """Get a specific approval request."""
    row = conn.execute(
        "SELECT * FROM approval_requests WHERE id = ?", (request_id,)
    ).fetchone()
    return dict(row) if row else None


def list_pending(conn):
    """List all pending approval requests."""
    rows = conn.execute(
        "SELECT * FROM approval_requests WHERE status = 'pending' ORDER BY created_at"
    ).fetchall()
    return [dict(r) for r in rows]


def confirm(action, details=None, tool_name="", plan_id="", step_id="",
            risk_level="medium"):
    """High-level confirmation function.
    
    In interactive mode: prompts user via stdin.
    In auto mode: returns True immediately.
    In file mode: creates request and returns False (async).
    
    Returns:
        True if approved, False if denied.
    """
    if AUTO_APPROVE:
        print(f"[AUTO-APPROVED] {action}")
        conn = get_db()
        init_tables(conn)
        create_request(conn, action, details, tool_name, plan_id, step_id, risk_level)
        conn.close()
        return True
    
    if CONFIRM_MODE == "interactive":
        return _interactive_confirm(action, details, risk_level)
    
    # File/async mode — create request and return False
    conn = get_db()
    init_tables(conn)
    req_id, _ = create_request(conn, action, details, tool_name, plan_id, step_id, risk_level)
    conn.close()
    print(f"[APPROVAL NEEDED] {action}")
    print(f"  Request ID: {req_id}")
    print(f"  Risk Level: {risk_level}")
    if details:
        print(f"  Details: {json.dumps(details, indent=2)}")
    print(f"  To approve: python confirm_action.py approve {req_id}")
    print(f"  To deny:    python confirm_action.py deny {req_id}")
    return False


def _interactive_confirm(action, details, risk_level):
    """Interactive stdin confirmation."""
    print(f"\n{'='*60}")
    print(f"APPROVAL REQUIRED")
    print(f"{'='*60}")
    print(f"  Action: {action}")
    print(f"  Risk:   {risk_level}")
    if details:
        for k, v in details.items():
            print(f"  {k}: {v}")
    print(f"{'='*60}")
    
    try:
        response = input("  Approve? [y/N]: ").strip().lower()
        approved = response in ("y", "yes")
        
        conn = get_db()
        init_tables(conn)
        req_id, _ = create_request(conn, action, details, risk_level=risk_level)
        status = "approved" if approved else "denied"
        resolve_request(conn, req_id, status, resolved_by="user_interactive")
        conn.close()
        
        if approved:
            print("  -> APPROVED")
        else:
            print("  -> DENIED")
        return approved
    except (EOFError, KeyboardInterrupt):
        print("\n  -> DENIED (no input)")
        return False


def check_tool_approval(tool_name, registry_path=None):
    """Check if a tool requires approval based on the tool registry.
    
    Returns:
        (requires_confirmation, side_effects) tuple
    """
    if registry_path is None:
        registry_path = SCRIPT_DIR / "tool_registry.json"
    
    if not registry_path.exists():
        return False, []
    
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    for tool in registry.get("tools", []):
        if tool["name"] == tool_name:
            return tool.get("requires_confirmation", False), tool.get("side_effects", [])
    
    return False, []


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Human-in-the-Loop — Approval gates for agent actions",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # request
    p_req = subparsers.add_parser("request", help="Create an approval request")
    p_req.add_argument("action", help="Description of the action")
    p_req.add_argument("--details", default="{}", help="JSON details")
    p_req.add_argument("--tool", default="", help="Tool name")
    p_req.add_argument("--plan-id", default="", help="Associated plan ID")
    p_req.add_argument("--step-id", default="", help="Associated step ID")
    p_req.add_argument("--risk", default="medium", choices=["low", "medium", "high", "critical"])

    # check
    p_check = subparsers.add_parser("check", help="Check approval request status")
    p_check.add_argument("request_id", help="Request ID")

    # approve
    p_approve = subparsers.add_parser("approve", help="Approve a request")
    p_approve.add_argument("request_id", help="Request ID")
    p_approve.add_argument("--reason", default="")

    # deny
    p_deny = subparsers.add_parser("deny", help="Deny a request")
    p_deny.add_argument("request_id", help="Request ID")
    p_deny.add_argument("--reason", default="")

    # list
    p_pending = subparsers.add_parser("list-pending", help="List pending approvals")
    p_pending.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()
    init_tables(conn)

    try:
        if args.command == "request":
            details = json.loads(args.details) if args.details != "{}" else {}
            req_id, auto = create_request(
                conn, args.action, details, args.tool, args.plan_id,
                args.step_id, args.risk
            )
            status = "auto-approved" if auto else "pending"
            print(json.dumps({"request_id": req_id, "status": status}, indent=2))

        elif args.command == "check":
            req = get_request(conn, args.request_id)
            if req:
                print(json.dumps(req, indent=2, default=str))
            else:
                print(f"Request not found: {args.request_id}")

        elif args.command == "approve":
            resolve_request(conn, args.request_id, "approved", reason=args.reason)
            print(f"Approved: {args.request_id}")

        elif args.command == "deny":
            resolve_request(conn, args.request_id, "denied", reason=args.reason)
            print(f"Denied: {args.request_id}")

        elif args.command == "list-pending":
            pending = list_pending(conn)
            if getattr(args, 'json', False):
                print(json.dumps(pending, indent=2, default=str))
            else:
                if not pending:
                    print("No pending approvals.")
                else:
                    print(f"\nPending Approvals ({len(pending)}):")
                    for r in pending:
                        print(f"  {r['id']}  [{r['risk_level']}]  {r['action']}")
                        print(f"    Created: {r['created_at']}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
