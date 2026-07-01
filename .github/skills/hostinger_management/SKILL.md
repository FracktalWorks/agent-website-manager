---
name: hostinger_management
description: >
  Manage Hostinger hosting account via MCP — domains, hosting plans, email
  accounts, SSL certificates, file manager, databases, WordPress installer,
  staging sites, backups, and cron jobs. Full hPanel control.
when_to_use: "User asks to manage Hostinger hosting, domains, email, SSL, files, databases, backups, or WordPress installation"
authority: write
cost_tier: 2
version: 0.1.0
---

# Hostinger Management Skill

Complete Hostinger hPanel management via MCP (Model Context Protocol).
Control every aspect of your Hostinger account — domains, hosting, email,
SSL, files, databases, and WordPress installations.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/hostinger_mcp.py` | Hostinger MCP client — all hPanel operations |
| `scripts/hostinger_backup.py` | Backup management — create, list, restore backups |

## Usage

```bash
# Account info
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action account-info

# Domain management
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action list-domains
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action dns-records --domain example.com

# Hosting management
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action hosting-info
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action php-version --set 8.2

# Email management
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action list-emails
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action create-email --address hello@example.com --password "..."

# SSL management
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action ssl-status --domain example.com
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action install-ssl --domain example.com

# File Manager
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action list-files --path /public_html
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action upload-file --local ./style.css --remote /public_html/wp-content/themes/

# Database management
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action list-databases
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action create-database --name mydb

# WordPress management
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action install-wordpress --domain example.com
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action create-staging --domain example.com
python .github/skills/hostinger_management/scripts/hostinger_mcp.py --action push-staging --domain example.com

# Backups
python .github/skills/hostinger_management/scripts/hostinger_backup.py --action create --domain example.com
python .github/skills/hostinger_management/scripts/hostinger_backup.py --action list --domain example.com
python .github/skills/hostinger_management/scripts/hostinger_backup.py --action restore --id backup123
```

## Required Environment Variables

- `HOSTINGER_API_TOKEN` — Hostinger hPanel API token

## Outputs

Writes operation results to `outputs/<project-slug>/hostinger_*.json`.
