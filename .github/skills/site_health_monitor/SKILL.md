---
name: site_health_monitor
description: >
  Comprehensive WordPress site health checks — uptime monitoring, PHP error
  logs, WordPress Site Health API scores, debug log analysis, cron job health,
  disk usage, database size, PHP version/limits, and Hostinger server status.
when_to_use: "User asks to check site health, monitor uptime, review errors, audit server status, or run health diagnostics"
authority: read
cost_tier: 1
version: 0.1.0
---

# Site Health Monitor Skill

Full health check for WordPress sites on Hostinger. Monitors uptime, PHP
errors, WordPress Site Health API, cron jobs, disk/database usage, and server
resource limits. Identifies issues before they become outages.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_health_check.py` | Full site health audit — all checks in one command |

## Usage

```bash
# Full health audit
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action full

# Quick status check (uptime + response code + PHP)
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action quick

# WordPress Site Health scores (from Site Health API)
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action wp-health

# PHP error log analysis (last N lines)
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action php-errors --lines 200

# Debug log analysis (wp-content/debug.log)
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action debug-log --lines 100

# Cron job health — list overdue/abandoned cron jobs
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action cron-health

# Disk usage check (via Hostinger MCP)
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action disk-usage

# Database stats (size, table count, overhead)
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action db-stats

# Check PHP version, memory limit, max execution time, upload size
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action php-info

# SSL certificate expiry check
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action ssl-check--domain example.com

# Uptime check (single or repeated)
python .github/skills/site_health_monitor/scripts/wp_health_check.py --action uptime --repeat 5 --interval 10
```

## What Gets Checked

| Category | Checks |
|----------|--------|
| **Availability** | HTTP status, response time, SSL cert expiry, DNS resolution |
| **WordPress Health** | Site Health API scores, auto-update status, inactive plugins/themes, REST API availability |
| **PHP** | Version, memory limit, max execution time, upload max filesize, error log |
| **Database** | Total size, table count, overhead, last optimized, wp_options autoload size |
| **Cron** | Total jobs, overdue jobs, abandoned jobs, next scheduled |
| **Disk** | Total usage, uploads folder size, inode count |
| **Security surface** | XML-RPC enabled, debug mode, wp-config.php location, directory listing |

## Required Environment Variables

- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
- `HOSTINGER_API_TOKEN` — for disk usage and server-level checks

## Outputs

Writes health reports to `outputs/<project-slug>/health_*.json`.
