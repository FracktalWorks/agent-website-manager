---
name: deployment_manager
description: >
  Manage WordPress deployments — sync Hostinger staging↔production, run
  pre-deployment backups, execute post-deployment smoke tests (homepage,
  API, checkout, forms), validate plugin/theme compatibility, and provide
  rollback procedures when deployments fail.
when_to_use: "User asks to deploy, push staging to production, sync environments, run smoke tests, or rollback a deployment"
authority: write
cost_tier: 2
version: 0.1.0
---

# Deployment Manager Skill

Safe WordPress deployments with Hostinger staging. Automates pre-deployment
backups, environment sync, post-deployment smoke tests, and rollback planning.
Reduces the risk of breaking your live site during updates.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_deploy.py` | Deployment orchestration — backup, sync, test, validate |

## Usage

```bash
# Pre-deployment check (is staging ready? any conflicts?)
python .github/skills/deployment_manager/scripts/wp_deploy.py --action pre-check

# Create pre-deployment backup
python .github/skills/deployment_manager/scripts/wp_deploy.py --action backup --domain example.com

# Push staging to production (via Hostinger MCP)
python .github/skills/deployment_manager/scripts/wp_deploy.py --action push-staging --domain example.com

# Post-deployment smoke tests
python .github/skills/deployment_manager/scripts/wp_deploy.py --action smoke-test --url https://example.com

# Validate specific pages after deploy
python .github/skills/deployment_manager/scripts/wp_deploy.py --action validate-pages --urls "https://example.com/,https://example.com/shop/,https://example.com/checkout/"

# Check WooCommerce checkout flow
python .github/skills/deployment_manager/scripts/wp_deploy.py --action test-checkout

# Rollback to last backup (if smoke tests fail)
python .github/skills/deployment_manager/scripts/wp_deploy.py --action rollback --domain example.com --backup-id latest

# Full deployment pipeline (backup → push → test → report)
python .github/skills/deployment_manager/scripts/wp_deploy.py --action deploy --domain example.com

# Compare staging vs production (plugin versions, post counts, settings)
python .github/skills/deployment_manager/scripts/wp_deploy.py --action diff --staging-url https://staging.example.com

# List recent backups available for rollback
python .github/skills/deployment_manager/scripts/wp_deploy.py --action list-backups --domain example.com

# Deploy with git (push theme/plugin changes from git repo)
python .github/skills/deployment_manager/scripts/wp_deploy.py --action git-deploy --repo ./my-theme --target wp-content/themes/my-theme/
```

## Deployment Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ PRE-CHECK│───▶│  BACKUP  │───▶│   PUSH   │───▶│  SMOKE   │───▶│  REPORT  │
│ staging  │    │  prod    │    │ staging  │    │  TEST    │    │ success/ │
│ status   │    │ snapshot │    │  → prod  │    │ critical │    │  failure │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                              ┌──────────┐
                                              │ ROLLBACK │  (if tests fail)
                                              │ restore  │
                                              └──────────┘
```

## Smoke Tests

After deployment, the agent automatically checks:
1. **Homepage** returns 200 with expected content
2. **REST API** is accessible and responsive
3. **Key pages** (shop, cart, checkout, contact) all return 200
4. **WooCommerce** checkout endpoint functional (if applicable)
5. **Admin login** page accessible
6. **No PHP fatal errors** in debug log
7. **SSL certificate** still valid
8. **LSCache** is still serving cached pages properly

## Required Environment Variables

- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
- `HOSTINGER_API_TOKEN` — For staging push/pull and backups
- `STAGING_SITE_URL` (optional) — For diff comparisons

## Outputs

Writes deployment logs to `outputs/<project-slug>/deploy_*.json`.
