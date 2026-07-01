# Agent Website Manager

> Built with DOE Framework — CommandCenter-Compatible

**Type:** WordPress Website Development & Management Agent

WordPress website development & management agent. Connects via Hostinger MCP
for full hosting control (domains, email, SSL, files, databases) and WordPress
REST API for content management, Elementor page building, SEO optimization,
plugin/theme management, backups, and security — all from chat.

## Quick Start

**Double-click:** `agent-website-manager.code-workspace` to open in VS Code.

Or manually:
```bash
# Windows
.\setup.ps1

# macOS/Linux
chmod +x setup.sh && ./setup.sh
```

## Using the Agent

1. Open in VS Code
2. Select **"Agent Website Manager"** from Copilot Chat agent dropdown
3. Tell the agent what you want to do:
   - "Set up a new WordPress site on Hostinger for my business"
   - "Create a landing page with Elementor for my product launch"
   - "Update all my WordPress plugins and run a security scan"
   - "Build a blog section with 5 SEO-optimized posts"
   - "Check my domain DNS records and install SSL"

## Skills

| Skill | Description |
|-------|-------------|
| **WordPress Management** | Pages, posts, media, plugins, themes, users, comments, SEO |
| **Hostinger Management** | Domains, hosting, email, SSL, files, databases, backups |
| **Elementor Builder** | Page builder, templates, global widgets, kits, responsive |
| **Memory Management** | Persistent agent memory with FTS5 search |
| **Infrastructure Tools** | Tool registry, task graphs, execution traces |

## Required API Keys

- `HOSTINGER_API_TOKEN` — Hostinger hPanel API token (get from hPanel → API)
- `WORDPRESS_SITE_URL` — Your WordPress site URL
- `WORDPRESS_USERNAME` — WordPress admin username
- `WORDPRESS_APP_PASSWORD` — WordPress application password

## Optional API Keys

- `ELEMENTOR_API_KEY` — Elementor Cloud features
- `GOOGLE_ANALYTICS_VIEW_ID` — Analytics reporting
- `GOOGLE_SEARCH_CONSOLE_SITE` — Search performance data
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` — Standalone mode only

## Structure

```
├── agents.py                 # build_agents() entry point
├── config.json               # CommandCenter contract
├── .github/
│   ├── prompts/system.md     # System prompt
│   ├── agents/*.agent.md     # VS Code Copilot Chat agent
│   └── skills/
│       ├── wordpress_management/  # WordPress content, plugins, SEO
│       ├── hostinger_management/  # Hostinger hosting, domains, email
│       └── elementor_builder/     # Elementor page builder
├── .tmp/scripts/             # Shared utilities
├── agent-data/               # Reference data
├── inputs/                   # User-provided files
├── outputs/                  # Campaign results
└── tests/                    # CI gate
```
