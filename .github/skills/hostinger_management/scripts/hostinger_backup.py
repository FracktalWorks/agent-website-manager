#!/usr/bin/env python3
"""
Hostinger Backup Manager

Create, list, restore, and delete backups for Hostinger-hosted sites.
Always trigger a backup before making destructive changes.

Usage:
    python hostinger_backup.py --action create --domain example.com
    python hostinger_backup.py --action list --domain example.com
    python hostinger_backup.py --action restore --domain example.com --id backup_123
    python hostinger_backup.py --action delete --domain example.com --id backup_123
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

HOSTINGER_TOKEN = os.getenv("HOSTINGER_API_TOKEN", "")


def _check_config():
    if not HOSTINGER_TOKEN:
        print(json.dumps({
            "error": True,
            "message": "HOSTINGER_API_TOKEN not set.",
            "fix": "Add HOSTINGER_API_TOKEN= to your .env file"
        }, indent=2))
        sys.exit(1)


def _mcp_call(action: str, params: dict = None) -> dict:
    """MCP communication placeholder. Implemented by CommandCenter runtime."""
    return {
        "status": "ready",
        "action": f"backup_{action}",
        "params": params or {},
        "timestamp": datetime.now().isoformat(),
        "note": "This script is invoked via CommandCenter MCP runtime.",
    }


def action_create(args):
    """Create a new backup for a domain."""
    desc = args.description or f"Agent-triggered backup {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    return _mcp_call("create", {
        "domain": args.domain,
        "description": desc,
        "type": args.type or "full",  # full, files, database
    })


def action_list(args):
    """List available backups for a domain."""
    return _mcp_call("list", {
        "domain": args.domain,
        "limit": args.limit or 20,
    })


def action_restore(args):
    """Restore a backup."""
    return _mcp_call("restore", {
        "domain": args.domain,
        "backup_id": args.id,
        "confirm": True,
    })


def action_delete(args):
    """Delete a backup."""
    return _mcp_call("delete", {
        "domain": args.domain,
        "backup_id": args.id,
        "confirm": args.force or False,
    })


def action_schedule(args):
    """Set up automatic backup schedule."""
    return _mcp_call("schedule", {
        "domain": args.domain,
        "frequency": args.frequency or "daily",  # daily, weekly, monthly
        "retention": args.retention or 7,  # number of backups to keep
        "type": args.type or "full",
    })


def main():
    parser = argparse.ArgumentParser(
        description="Hostinger Backup Manager"
    )
    parser.add_argument("--action", required=True, choices=[
        "create", "list", "restore", "delete", "schedule",
    ])
    parser.add_argument("--domain", required=True)
    parser.add_argument("--id", help="Backup ID (for restore/delete)")
    parser.add_argument("--type", choices=["full", "files", "database"])
    parser.add_argument("--description")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--frequency", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--retention", type=int)
    parser.add_argument("--force", action="store_true")

    args = parser.parse_args()
    _check_config()

    action_map = {
        "create": lambda: action_create(args),
        "list": lambda: action_list(args),
        "restore": lambda: action_restore(args),
        "delete": lambda: action_delete(args),
        "schedule": lambda: action_schedule(args),
    }

    try:
        result = action_map[args.action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
