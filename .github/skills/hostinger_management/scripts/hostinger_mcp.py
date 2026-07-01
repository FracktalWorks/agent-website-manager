#!/usr/bin/env python3
"""
Hostinger MCP Client

Manages Hostinger hPanel operations via MCP (Model Context Protocol).
Controls domains, hosting, email, SSL, files, databases, and WordPress
installations on Hostinger.

The actual MCP communication is handled by the CommandCenter runtime
which injects the Hostinger MCP server. This script provides a CLI
wrapper that documents all available operations and can be invoked
directly for testing.

Usage:
    python hostinger_mcp.py --action account-info
    python hostinger_mcp.py --action list-domains
    python hostinger_mcp.py --action dns-records --domain example.com
    python hostinger_mcp.py --action create-email --address hello@example.com
    python hostinger_mcp.py --action install-wordpress --domain example.com
"""

import os
import sys
import json
import argparse
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

HOSTINGER_TOKEN = os.getenv("HOSTINGER_API_TOKEN", "")


def _check_config():
    """Verify Hostinger API token is set."""
    if not HOSTINGER_TOKEN:
        print(json.dumps({
            "error": True,
            "message": "HOSTINGER_API_TOKEN not set. Get it from hPanel → API.",
            "fix": "Add HOSTINGER_API_TOKEN= to your .env file"
        }, indent=2))
        sys.exit(1)


def _mcp_call(action: str, params: dict = None) -> dict:
    """
    Placeholder for MCP communication.
    In production, this is intercepted by the CommandCenter MCP runtime.
    For local testing, this attempts a direct API call if possible.
    """
    # This is a documentation/CLI wrapper. The actual MCP communication
    # happens at the CommandCenter runtime level when the agent is deployed.
    # For standalone testing, you can implement direct Hostinger API calls here.
    return {
        "status": "ready",
        "action": action,
        "params": params or {},
        "note": "This script is invoked via CommandCenter MCP runtime. "
                "Direct Hostinger API calls require implementing the "
                "Hostinger REST API client. See docs at: "
                "https://developers.hostinger.com",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def action_account_info(args):
    """Get Hostinger account information."""
    return _mcp_call("account_info", {
        "fields": ["email", "plan", "balance", "status", "created_at"]
    })


def action_list_domains(args):
    """List all domains in the Hostinger account."""
    return _mcp_call("list_domains", {
        "status": args.status or "active"
    })


def action_domain_info(args):
    """Get detailed info about a specific domain."""
    return _mcp_call("domain_info", {"domain": args.domain})


def action_dns_records(args):
    """List DNS records for a domain."""
    return _mcp_call("list_dns_records", {"domain": args.domain})


def action_add_dns_record(args):
    """Add a DNS record to a domain."""
    return _mcp_call("add_dns_record", {
        "domain": args.domain,
        "type": args.record_type,
        "name": args.name,
        "value": args.value,
        "ttl": args.ttl or 3600,
        "priority": args.priority or 0,
    })


def action_hosting_info(args):
    """Get hosting plan and resource usage."""
    return _mcp_call("hosting_info", {})


def action_set_php_version(args):
    """Set PHP version for a hosting account."""
    return _mcp_call("set_php_version", {
        "domain": args.domain,
        "version": args.version or "8.2"
    })


def action_list_emails(args):
    """List email accounts for a domain."""
    return _mcp_call("list_emails", {"domain": args.domain})


def action_create_email(args):
    """Create a new email account."""
    return _mcp_call("create_email", {
        "domain": args.domain,
        "address": args.address,
        "password": args.password,
        "quota": args.quota or 1024,
    })


def action_delete_email(args):
    """Delete an email account."""
    return _mcp_call("delete_email", {
        "email": args.address
    })


def action_ssl_status(args):
    """Check SSL certificate status for a domain."""
    return _mcp_call("ssl_status", {"domain": args.domain})


def action_install_ssl(args):
    """Install/activate SSL certificate for a domain."""
    return _mcp_call("install_ssl", {
        "domain": args.domain,
        "force_https": args.force_https if hasattr(args, 'force_https') else True,
    })


def action_list_files(args):
    """List files in a directory on the hosting account."""
    return _mcp_call("list_files", {
        "domain": args.domain,
        "path": args.path or "/public_html",
    })


def action_upload_file(args):
    """Upload a file to the hosting account."""
    return _mcp_call("upload_file", {
        "domain": args.domain,
        "local_path": args.local,
        "remote_path": args.remote,
    })


def action_list_databases(args):
    """List MySQL databases."""
    return _mcp_call("list_databases", {})


def action_create_database(args):
    """Create a new MySQL database."""
    return _mcp_call("create_database", {
        "name": args.name,
        "username": args.username or args.name,
        "password": args.password or "",
    })


def action_install_wordpress(args):
    """Install WordPress on a domain via Hostinger auto-installer."""
    return _mcp_call("install_wordpress", {
        "domain": args.domain,
        "path": args.path or "/",
        "site_title": args.site_title or args.domain,
        "admin_user": args.admin_user or "admin",
        "admin_password": args.admin_password or "",
        "admin_email": args.admin_email or "",
        "language": args.language or "en_US",
    })


def action_create_staging(args):
    """Create a staging site for a WordPress installation."""
    return _mcp_call("create_staging", {"domain": args.domain})


def action_push_staging(args):
    """Push staging site changes to production."""
    return _mcp_call("push_staging", {
        "domain": args.domain,
        "confirm": args.confirm or False,
    })


def action_list_cron_jobs(args):
    """List cron jobs."""
    return _mcp_call("list_cron_jobs", {"domain": args.domain})


def action_create_cron_job(args):
    """Create a cron job."""
    return _mcp_call("create_cron_job", {
        "domain": args.domain,
        "command": args.command,
        "schedule": args.schedule,  # e.g., "*/5 * * * *"
    })


def action_php_error_logs(args):
    """Retrieve recent PHP error logs."""
    return _mcp_call("php_error_logs", {
        "domain": args.domain,
        "lines": args.lines or 100,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Hostinger MCP Client — hPanel operations"
    )
    parser.add_argument("--action", required=True, choices=[
        "account-info", "list-domains", "domain-info", "dns-records",
        "add-dns-record", "hosting-info", "set-php-version",
        "list-emails", "create-email", "delete-email",
        "ssl-status", "install-ssl",
        "list-files", "upload-file",
        "list-databases", "create-database",
        "install-wordpress", "create-staging", "push-staging",
        "list-cron-jobs", "create-cron-job",
        "php-error-logs",
    ])
    # Domain
    parser.add_argument("--domain")
    # DNS
    parser.add_argument("--record-type", dest="record_type")
    parser.add_argument("--name")
    parser.add_argument("--value")
    parser.add_argument("--ttl", type=int)
    parser.add_argument("--priority", type=int)
    # PHP
    parser.add_argument("--version")
    # Email
    parser.add_argument("--address")
    parser.add_argument("--password")
    parser.add_argument("--quota", type=int)
    # SSL
    parser.add_argument("--force-https", dest="force_https", action="store_true")
    # Files
    parser.add_argument("--path")
    parser.add_argument("--local")
    parser.add_argument("--remote")
    # DB
    parser.add_argument("--username")
    # WordPress
    parser.add_argument("--site-title", dest="site_title")
    parser.add_argument("--admin-user", dest="admin_user")
    parser.add_argument("--admin-password", dest="admin_password")
    parser.add_argument("--admin-email", dest="admin_email")
    parser.add_argument("--language")
    # Staging
    parser.add_argument("--confirm", action="store_true")
    # Cron
    parser.add_argument("--command")
    parser.add_argument("--schedule")
    parser.add_argument("--lines", type=int)
    # General
    parser.add_argument("--status")

    args = parser.parse_args()
    _check_config()

    action_map = {
        "account-info": lambda: action_account_info(args),
        "list-domains": lambda: action_list_domains(args),
        "domain-info": lambda: action_domain_info(args),
        "dns-records": lambda: action_dns_records(args),
        "add-dns-record": lambda: action_add_dns_record(args),
        "hosting-info": lambda: action_hosting_info(args),
        "set-php-version": lambda: action_set_php_version(args),
        "list-emails": lambda: action_list_emails(args),
        "create-email": lambda: action_create_email(args),
        "delete-email": lambda: action_delete_email(args),
        "ssl-status": lambda: action_ssl_status(args),
        "install-ssl": lambda: action_install_ssl(args),
        "list-files": lambda: action_list_files(args),
        "upload-file": lambda: action_upload_file(args),
        "list-databases": lambda: action_list_databases(args),
        "create-database": lambda: action_create_database(args),
        "install-wordpress": lambda: action_install_wordpress(args),
        "create-staging": lambda: action_create_staging(args),
        "push-staging": lambda: action_push_staging(args),
        "list-cron-jobs": lambda: action_list_cron_jobs(args),
        "create-cron-job": lambda: action_create_cron_job(args),
        "php-error-logs": lambda: action_php_error_logs(args),
    }

    try:
        result = action_map[args.action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
