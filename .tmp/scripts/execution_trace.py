#!/usr/bin/env python3
"""
Execution Trace — Structured observability for every tool call.

Records what happened, when, inputs/outputs, duration, and errors.
Enables debugging failed workflows and understanding agent behavior.

Usage:
    python execution_trace.py start "lead_gen_pipeline"           # Start a new trace
    python execution_trace.py log <trace_id> --tool scrape_google_maps \\
        --input '{"search": "plumbers"}' --output '{"rows": 50}' --duration 12.3
    python execution_trace.py end <trace_id> --status success
    python execution_trace.py show <trace_id>                      # Replay a trace
    python execution_trace.py list                                 # Recent traces
    python execution_trace.py list --status failed                 # Failed traces
    python execution_trace.py stats --days 7                       # Aggregate stats

Programmatic usage (from other scripts):
    from execution_trace import Tracer
    
    tracer = Tracer("my_pipeline")
    tracer.log_step("scrape", tool="scrape_google_maps", input_data={...})
    tracer.log_step("scrape", output_data={...}, duration_s=12.3, status="success")
    tracer.end(status="success")
"""

import os
import sys
import json
import sqlite3
import argparse
import uuid
import time
from datetime import datetime, timedelta
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
    return conn


def init_tables(conn):
    """Create trace tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS traces (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            status      TEXT DEFAULT 'running',
            plan_id     TEXT DEFAULT '',
            started_at  TEXT DEFAULT (datetime('now')),
            ended_at    TEXT DEFAULT NULL,
            duration_s  REAL DEFAULT 0.0,
            total_cost  REAL DEFAULT 0.0,
            total_tokens INTEGER DEFAULT 0,
            step_count  INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            metadata    TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS trace_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id    TEXT NOT NULL,
            step        INTEGER DEFAULT 0,
            event_type  TEXT DEFAULT 'tool_call',
            tool        TEXT DEFAULT '',
            input_data  TEXT DEFAULT '{}',
            output_data TEXT DEFAULT '{}',
            status      TEXT DEFAULT 'success',
            duration_s  REAL DEFAULT 0.0,
            cost_usd    REAL DEFAULT 0.0,
            tokens      INTEGER DEFAULT 0,
            error       TEXT DEFAULT '',
            timestamp   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (trace_id) REFERENCES traces(id)
        );

        CREATE INDEX IF NOT EXISTS idx_trace_events_trace ON trace_events(trace_id);
        CREATE INDEX IF NOT EXISTS idx_traces_status ON traces(status);
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# TRACER CLASS (for programmatic use from other scripts)
# ---------------------------------------------------------------------------

class Tracer:
    """Context manager for tracing a pipeline execution."""
    
    def __init__(self, name, plan_id="", metadata=None):
        self.conn = get_db()
        init_tables(self.conn)
        self.trace_id = start_trace(self.conn, name, plan_id, metadata)
        self.step_counter = 0
        self._start_time = time.time()
    
    def log_step(self, step_name, tool="", input_data=None, output_data=None,
                 status="success", duration_s=0.0, cost_usd=0.0, tokens=0,
                 error="", event_type="tool_call"):
        """Log a step in the trace."""
        self.step_counter += 1
        log_event(
            self.conn, self.trace_id, self.step_counter, event_type,
            tool, input_data, output_data, status, duration_s,
            cost_usd, tokens, error
        )
        return self.step_counter
    
    def end(self, status="success"):
        """End the trace."""
        duration = time.time() - self._start_time
        end_trace(self.conn, self.trace_id, status, duration)
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        status = "failed" if exc_type else "success"
        error = str(exc_val) if exc_val else ""
        if error:
            self.log_step("error", status="failed", error=error, event_type="error")
        self.end(status=status)
        return False


# ---------------------------------------------------------------------------
# CORE FUNCTIONS
# ---------------------------------------------------------------------------

def start_trace(conn, name, plan_id="", metadata=None):
    """Start a new execution trace. Returns trace_id."""
    trace_id = "trc-" + datetime.now().strftime("%H%M%S") + "-" + uuid.uuid4().hex[:6]
    conn.execute(
        "INSERT INTO traces (id, name, plan_id, metadata) VALUES (?, ?, ?, ?)",
        (trace_id, name, plan_id, json.dumps(metadata or {}))
    )
    conn.commit()
    return trace_id


def log_event(conn, trace_id, step, event_type, tool="", input_data=None,
              output_data=None, status="success", duration_s=0.0,
              cost_usd=0.0, tokens=0, error=""):
    """Log a trace event."""
    # Truncate large data to prevent DB bloat
    input_str = json.dumps(input_data or {})
    if len(input_str) > 10000:
        input_str = input_str[:10000] + "...(truncated)"
    
    output_str = json.dumps(output_data or {})
    if len(output_str) > 10000:
        output_str = output_str[:10000] + "...(truncated)"
    
    conn.execute("""
        INSERT INTO trace_events (trace_id, step, event_type, tool, input_data, output_data,
                                  status, duration_s, cost_usd, tokens, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (trace_id, step, event_type, tool, input_str, output_str,
          status, duration_s, cost_usd, tokens, error))
    
    # Update trace counters
    conn.execute("""
        UPDATE traces SET 
            step_count = step_count + 1,
            total_cost = total_cost + ?,
            total_tokens = total_tokens + ?,
            error_count = error_count + ?
        WHERE id = ?
    """, (cost_usd, tokens, 1 if status == "failed" else 0, trace_id))
    conn.commit()


def end_trace(conn, trace_id, status="success", duration_s=None):
    """End a trace."""
    now = datetime.now().isoformat()
    if duration_s is None:
        trace = conn.execute("SELECT started_at FROM traces WHERE id = ?", (trace_id,)).fetchone()
        if trace:
            started = datetime.fromisoformat(trace["started_at"])
            duration_s = (datetime.now() - started).total_seconds()
        else:
            duration_s = 0.0
    
    conn.execute("""
        UPDATE traces SET status=?, ended_at=?, duration_s=? WHERE id=?
    """, (status, now, duration_s, trace_id))
    conn.commit()


def get_trace(conn, trace_id):
    """Get a trace with all events."""
    trace = conn.execute("SELECT * FROM traces WHERE id = ?", (trace_id,)).fetchone()
    if not trace:
        return None
    
    events = conn.execute(
        "SELECT * FROM trace_events WHERE trace_id = ? ORDER BY step, id",
        (trace_id,)
    ).fetchall()
    
    return {
        "trace": dict(trace),
        "events": [dict(e) for e in events]
    }


def list_traces(conn, status=None, limit=20):
    """List recent traces."""
    if status:
        rows = conn.execute(
            "SELECT * FROM traces WHERE status = ? ORDER BY started_at DESC LIMIT ?",
            (status, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM traces ORDER BY started_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_trace_stats(conn, days=7):
    """Get aggregate trace statistics."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    total = conn.execute(
        "SELECT COUNT(*) as c FROM traces WHERE started_at > ?", (cutoff,)
    ).fetchone()["c"]
    
    by_status = conn.execute(
        "SELECT status, COUNT(*) as c FROM traces WHERE started_at > ? GROUP BY status",
        (cutoff,)
    ).fetchall()
    
    cost = conn.execute(
        "SELECT COALESCE(SUM(total_cost), 0) as c FROM traces WHERE started_at > ?",
        (cutoff,)
    ).fetchone()["c"]
    
    tokens = conn.execute(
        "SELECT COALESCE(SUM(total_tokens), 0) as c FROM traces WHERE started_at > ?",
        (cutoff,)
    ).fetchone()["c"]
    
    avg_duration = conn.execute(
        "SELECT COALESCE(AVG(duration_s), 0) as c FROM traces WHERE started_at > ? AND status='success'",
        (cutoff,)
    ).fetchone()["c"]
    
    # Most used tools
    top_tools = conn.execute("""
        SELECT te.tool, COUNT(*) as cnt, SUM(te.duration_s) as total_time, SUM(te.cost_usd) as total_cost
        FROM trace_events te JOIN traces t ON te.trace_id = t.id
        WHERE t.started_at > ? AND te.tool != ''
        GROUP BY te.tool ORDER BY cnt DESC LIMIT 10
    """, (cutoff,)).fetchall()
    
    # Most common errors
    top_errors = conn.execute("""
        SELECT te.tool, te.error, COUNT(*) as cnt
        FROM trace_events te JOIN traces t ON te.trace_id = t.id
        WHERE t.started_at > ? AND te.status = 'failed' AND te.error != ''
        GROUP BY te.tool, te.error ORDER BY cnt DESC LIMIT 5
    """, (cutoff,)).fetchall()
    
    return {
        "period_days": days,
        "total_traces": total,
        "by_status": {r["status"]: r["c"] for r in by_status},
        "total_cost_usd": round(cost, 4),
        "total_tokens": tokens,
        "avg_duration_s": round(avg_duration, 2),
        "top_tools": [{"tool": r["tool"], "calls": r["cnt"], 
                        "total_time": round(r["total_time"], 2),
                        "total_cost": round(r["total_cost"], 4)} for r in top_tools],
        "top_errors": [{"tool": r["tool"], "error": r["error"][:100], "count": r["cnt"]} for r in top_errors]
    }


def show_trace(conn, trace_id, as_json=False):
    """Display a trace with all events."""
    data = get_trace(conn, trace_id)
    if not data:
        print(f"Trace not found: {trace_id}")
        return
    
    trace = data["trace"]
    events = data["events"]
    
    if as_json:
        print(json.dumps(data, indent=2, default=str))
        return
    
    icons = {"success": "[+]", "failed": "[X]", "running": "[~]"}
    
    print(f"\n{'='*60}")
    print(f"TRACE: {trace['name']}")
    print(f"{'='*60}")
    print(f"  ID:       {trace['id']}")
    print(f"  Status:   {trace['status'].upper()}")
    print(f"  Started:  {trace['started_at']}")
    if trace.get('ended_at'):
        print(f"  Ended:    {trace['ended_at']}")
    print(f"  Duration: {trace['duration_s']:.2f}s")
    print(f"  Steps:    {trace['step_count']}  (errors: {trace['error_count']})")
    print(f"  Cost:     ${trace['total_cost']:.4f}")
    print(f"  Tokens:   {trace['total_tokens']}")
    
    if events:
        print(f"\n  Timeline:")
        for e in events:
            icon = icons.get(e["status"], "[?]")
            tool_str = f" [{e['tool']}]" if e["tool"] else ""
            dur_str = f" ({e['duration_s']:.2f}s)" if e["duration_s"] else ""
            cost_str = f" ${e['cost_usd']:.4f}" if e["cost_usd"] else ""
            
            print(f"    {icon} Step {e['step']:3d}{tool_str}{dur_str}{cost_str}")
            
            if e.get("error"):
                print(f"          ERROR: {e['error'][:100]}")
    
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Execution Trace — Structured observability for tool calls",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # start
    p_start = subparsers.add_parser("start", help="Start a new trace")
    p_start.add_argument("name", help="Trace name")
    p_start.add_argument("--plan-id", default="", help="Associated plan ID")
    p_start.add_argument("--metadata", default="{}", help="JSON metadata")

    # log
    p_log = subparsers.add_parser("log", help="Log a trace event")
    p_log.add_argument("trace_id", help="Trace ID")
    p_log.add_argument("--step", type=int, default=None, help="Step number (auto-increments if omitted)")
    p_log.add_argument("--type", default="tool_call", help="Event type")
    p_log.add_argument("--tool", default="", help="Tool name")
    p_log.add_argument("--input", default="{}", help="Input JSON")
    p_log.add_argument("--output", default="{}", help="Output JSON")
    p_log.add_argument("--status", default="success", choices=["success", "failed", "running"])
    p_log.add_argument("--duration", type=float, default=0.0)
    p_log.add_argument("--cost", type=float, default=0.0)
    p_log.add_argument("--tokens", type=int, default=0)
    p_log.add_argument("--error", default="")

    # end
    p_end = subparsers.add_parser("end", help="End a trace")
    p_end.add_argument("trace_id", help="Trace ID")
    p_end.add_argument("--status", default="success", choices=["success", "failed"])

    # show
    p_show = subparsers.add_parser("show", help="Show trace details")
    p_show.add_argument("trace_id", help="Trace ID")
    p_show.add_argument("--json", action="store_true")

    # list
    p_list = subparsers.add_parser("list", help="List recent traces")
    p_list.add_argument("--status", default=None)
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--json", action="store_true")

    # stats
    p_stats = subparsers.add_parser("stats", help="Aggregate trace statistics")
    p_stats.add_argument("--days", type=int, default=7)
    p_stats.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()
    init_tables(conn)

    try:
        if args.command == "start":
            metadata = json.loads(args.metadata) if args.metadata != "{}" else {}
            trace_id = start_trace(conn, args.name, args.plan_id, metadata)
            print(json.dumps({"trace_id": trace_id, "status": "running"}))

        elif args.command == "log":
            input_data = json.loads(args.input) if args.input != "{}" else {}
            output_data = json.loads(args.output) if args.output != "{}" else {}
            step = args.step
            if step is None:
                # Auto-increment: get max step for this trace + 1
                row = conn.execute(
                    "SELECT COALESCE(MAX(step), -1) as mx FROM trace_events WHERE trace_id = ?",
                    (args.trace_id,)
                ).fetchone()
                step = row["mx"] + 1
            log_event(conn, args.trace_id, step, args.type, args.tool,
                      input_data, output_data, args.status, args.duration,
                      args.cost, args.tokens, args.error)
            print(f"Logged step {step} for trace {args.trace_id}")

        elif args.command == "end":
            end_trace(conn, args.trace_id, args.status)
            print(f"Trace {args.trace_id} -> {args.status}")

        elif args.command == "show":
            show_trace(conn, args.trace_id, as_json=getattr(args, 'json', False))

        elif args.command == "list":
            traces = list_traces(conn, status=args.status, limit=args.limit)
            if getattr(args, 'json', False):
                print(json.dumps(traces, indent=2, default=str))
            else:
                if not traces:
                    print("No traces found.")
                else:
                    print(f"\n{'ID':20s} {'Status':10s} {'Steps':6s} {'Duration':10s} {'Cost':8s} Name")
                    print("-" * 80)
                    for t in traces:
                        print(f"{t['id']:20s} {t['status']:10s} {t['step_count']:>5d}  "
                              f"{t['duration_s']:>8.1f}s ${t['total_cost']:.4f}  {t['name']}")

        elif args.command == "stats":
            stats = get_trace_stats(conn, days=args.days)
            if getattr(args, 'json', False):
                print(json.dumps(stats, indent=2, default=str))
            else:
                print(f"\n{'='*60}")
                print(f"TRACE STATS (last {args.days} days)")
                print(f"{'='*60}")
                print(f"  Total traces:  {stats['total_traces']}")
                for status, count in stats.get('by_status', {}).items():
                    print(f"    {status}: {count}")
                print(f"  Total cost:    ${stats['total_cost_usd']:.4f}")
                print(f"  Total tokens:  {stats['total_tokens']}")
                print(f"  Avg duration:  {stats['avg_duration_s']:.2f}s")
                
                if stats.get('top_tools'):
                    print(f"\n  Top Tools:")
                    for t in stats['top_tools']:
                        print(f"    {t['tool']:30s} {t['calls']:>5d} calls  {t['total_time']:>8.1f}s  ${t['total_cost']:.4f}")
                
                if stats.get('top_errors'):
                    print(f"\n  Common Errors:")
                    for e in stats['top_errors']:
                        print(f"    [{e['tool']}] {e['error']} (x{e['count']})")
                print(f"{'='*60}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
