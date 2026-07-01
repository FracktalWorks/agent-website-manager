# Agent Website Manager — Agent Instructions

> Expert WordPress website development & management agent. Connects via Hostinger MCP for full hosting control and WordPress REST API for content, design, SEO, and maintenance — all from chat.

## Architecture (DOE v2)

**Layer 1 — Skills:** `.github/skills/*/SKILL.md` define goals, inputs, scripts, outputs.
**Layer 2 — Orchestration:** You (the LLM) read SKILL.md, call scripts, apply judgment.
**Layer 3 — Execution:** `.github/skills/*/scripts/` and `.tmp/scripts/` do the actual work.

## Available Skills

| Skill | SKILL.md | What it does |
|-------|----------|--------------|
| WordPress Management | `.github/skills/wordpress_management/SKILL.md` | Pages, posts, media, plugins, themes, users, comments, SEO |
| Hostinger Management | `.github/skills/hostinger_management/SKILL.md` | Domains, hosting, email, SSL, files, databases, backups |
| Elementor Builder | `.github/skills/elementor_builder/SKILL.md` | Page builder, templates, global widgets, kits, responsive design |
| WooCommerce Management | `.github/skills/woocommerce_management/SKILL.md` | Products, orders, customers, coupons, reports, settings |
| Media Cleanup | `.github/skills/media_cleanup/SKILL.md` | Unused image detection, media optimization, WebP conversion |
| Performance Optimization | `.github/skills/performance_optimization/SKILL.md` | Page speed, LSCache, minification, CDN, DB optimization |
| Memory Management | `.github/skills/memory_management/SKILL.md` | Persistent agent memory, FTS5 search, STM/LTM |
| Infrastructure Tools | `.github/skills/infrastructure_tools/SKILL.md` | Tool registry, task graphs, execution traces, approval gates |

## Platform Tools (injected by CommandCenter)

- `write_artifact` — write files visible in the UI sidebar
- `manage_todo_list` — update the live task panel
- `ask_user` — pause and ask the user a clarifying question
- `get_errors` — check code for syntax/lint errors
- `save_note` / `recall_notes` — repo-scoped working memory
- `web_search` / `fetch_page` — web access (no API key needed)

## File Organization

- `.github/skills/` — Skill instructions + feature scripts
- `.tmp/scripts/` — Shared utilities (on PYTHONPATH)
- `agent-data/` — Reference data: WordPress templates, Elementor kits, SEO checklists
- `inputs/` — User-provided files: design briefs, content drafts, media assets
- `outputs/` — Campaign results and generated website content
- `tests/` — pytest suite — CI gate

## Quick Start

1. Copy `.env.example` → `.env` and fill in your Hostinger & WordPress credentials
2. `pip install -r requirements.txt`
3. Tell the agent what you want to do:
   - "Set up a new WordPress site on Hostinger for my business"
   - "Create a landing page with Elementor for my product launch"
   - "Update all my WordPress plugins and run a security scan"
   - "Build a blog section with 5 SEO-optimized posts"

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. **Store the lesson in memory** (`add-insight`, `add-fact`)
6. System is now stronger

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts).
Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.
