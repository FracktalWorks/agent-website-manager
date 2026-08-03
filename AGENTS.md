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
| HTML → WordPress | `.github/skills/html_deploy/SKILL.md` | Publish finished HTML to WP — canvas (default) or Elementor widgets. Was `open_design_integration` |
| Website Analysis & Reporting | `.github/skills/website_analysis/SKILL.md` | Decision-oriented site reports: health, SEO, linking/orphans, architecture, page opportunities |
| Site Generator & Live Editor | `.github/skills/site_generator/SKILL.md` | In-repo site generation: pages as data, validating builder, live browser editor writing back to source |
| Design System Management | `.github/skills/design_system_management/SKILL.md` | Choose/load/use/validate/create design systems from the 152-package corpus: token tiers, paste-the-`:root` rule, quality rubric, craft rules |
| Search Presence | `.github/skills/search_presence/SKILL.md` | Be findable: root favicon, canonical host, sitemap, Search Console, Bing→ChatGPT, IndexNow, LocalBusiness `geo`, Business Profile, keyless map embed. `presence_check.py` measures the on-domain half |
| Brand Assets | `.github/skills/brand_assets/SKILL.md` | Platform artwork from the brand's SVGs — favicon, GBP logo/cover, WhatsApp profile + catalogue tiles, social cards. Judged at consumption size by `asset_check.py` |

**Launching a brand?** The skills above are the parts; `agent-data/BRAND_LAUNCH_RUNBOOK.md`
is the order they go in — scaffold → design system → content → verify → deploy
→ search presence → platform assets → profiles, with the gate for each step and
the failure modes that repeat across brands.

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
- `agent-data/` — Reference data: WordPress templates, Elementor kits, SEO checklists, design systems
- `inputs/` — User-provided files: design briefs, content drafts, media assets
- `outputs/` — Campaign results, generated website content, design page drafts
- `tests/` — pytest suite — CI gate
- `hub.py` — workspace shell at http://127.0.0.1:8780 (projects, pages, design systems)
- `artifacts.py` — what a project owns *beyond* its website: artefact kinds
  (website / print / brand / signage), discovered from the directory layout,
  plus the sitemap tree the hub's Collateral view renders

## Directory contracts (read the local AGENTS.md before editing there)

Deeper contracts load on demand so this file stays small. Before editing in a
directory that has one, read it — it says what the directory owns, where new
work belongs, and which gate to run:

| Directory | Contract covers |
|---|---|
| `outputs/drvarada-site/site/` | the site engine: placement table (content vs chrome vs engine), silent-failure invariants, test gates |
| `outputs/drvarada-site/print/` | print collateral: the millimetre engine, bleed/trim/safe, sign-off gates, why nothing is retyped |
| `agent-data/design-systems/` | `INDEX.md` — the 152-system corpus and its CLI |

**Place before building:** name the kind of thing you are adding, find the
directory that owns that kind in the table above, and put it there — never in
whatever file is already open. If nothing owns it, add a new scope with its own
contract rather than an orphan file.

## Quick Start

**Opening the folder in VS Code does steps 1 and 2 for you** — `setup.ps1` /
`setup.sh` run on `folderOpen`, and the workspace hub opens in a Simple Browser
pane at the same time. Setup is fingerprinted against `requirements.txt`, so
only the first open after a change actually installs anything (~0.7s otherwise).

1. Copy `.env.example` → `.env` and fill in your Hostinger & WordPress credentials
2. `pip install -r requirements.txt` (optional heavy ML extras:
   `pip install -r requirements-ml.txt` — only needed for media auto-tagging)
3. Tell the agent what you want to do:
   - "Set up a new WordPress site on Hostinger for my business"
   - "Create a landing page with Elementor for my product launch"
   - "Update all my WordPress plugins and run a security scan"
   - "Redesign the homepage using the fracktal-works design system"
   - "Scaffold a new site for Acme and build the homepage"
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
