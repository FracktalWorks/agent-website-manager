# Agent Website Manager — Copilot Instructions

This is the **Agent Website Manager** repo — builds and manages WordPress websites
on Hostinger using the DOE Framework (Directive, Orchestration, Execution).

**Key files:**
- `agents.py` — `build_agents()` entry point for CommandCenter dynamic agent loading
- `config.json` — CommandCenter contract (Hostinger MCP, WordPress REST API integrations)
- `.github/prompts/system.md` — System prompt loaded by agents.py at runtime
- `.github/skills/wordpress_management/SKILL.md` — WordPress content, plugins, themes, SEO
- `.github/skills/hostinger_management/SKILL.md` — Hostinger hosting, domains, email, SSL
- `.github/skills/elementor_builder/SKILL.md` — Elementor page builder, templates, kits
- `.github/skills/*/scripts/` — Deterministic execution scripts
- `.tmp/scripts/` — Shared utilities on PYTHONPATH

**Architecture:** Skills (what to do) → Orchestration (decision making) → Execution (doing the work)
