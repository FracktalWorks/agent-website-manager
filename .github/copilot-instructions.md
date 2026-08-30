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
- `.github/skills/design_taste/SKILL.md` — anti-slop design judgment (vendored tasteskill.dev + 74 brand DESIGN.md corpora); load before designing any page
- `.github/skills/design_concepting/SKILL.md` — mockup-first flow: compare 2-4 design directions in the hub before building anything
- `.github/skills/link_authority/SKILL.md` — earn links, mentions and AI citations: `authority_audit.py` + `post_gate.py`, claim-what's-ours inventory, Discover-eligible newsroom, LinkedIn canonical-first; prospect libraries per vertical
- `.github/skills/*/scripts/` — Deterministic execution scripts
- `.tmp/scripts/` — Shared utilities on PYTHONPATH

**Architecture:** Skills (what to do) → Orchestration (decision making) → Execution (doing the work)

**User feedback on generated sites:** the live editor's **Note** tool queues
requested changes in `outputs/<site>/site/.feedback/notes.jsonl`, each line
carrying the element's `data-od` address, the source `file:line` it resolved
to, and its current value. Before improving any generated site, read that file
and act on every `status: "open"` item, then set its `status` to `"done"` with
a `resolved` timestamp. Patch the address, not the text. The user expects
pinned feedback to be seen without re-explaining it in chat.
