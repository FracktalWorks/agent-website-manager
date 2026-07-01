# Agent Builder Guide — CommandCenter Framework

> **Audience:** AI coding agents and developers building new CommandCenter-compatible agents.
> **Reference implementation:** `sales-prospector` repo — the canonical pattern every new agent must follow.
> **Framework:** DOE v2 — Skills (what to do) / Orchestration (decision making) / Execution (doing the work).
> **Date:** 2026-06-19 · **Version:** 6.0

---

## Overview

A CommandCenter agent is a Python repo with three required files at the root (`agents.py`, `config.json`, `AGENTS.md`) and a structured layout that separates concerns into skills, shared utilities, reference data, and campaign outputs. The same repo serves both **VS Code Copilot Chat** (via `.github/agents/<name>.agent.md`) and **CommandCenter** (via `build_agents()` in `agents.py`) without any code duplication.

**Two modes, one source of truth:**

| Mode                 | Entry point                      | System prompt loaded from                          |
| -------------------- | -------------------------------- | -------------------------------------------------- |
| VS Code Copilot Chat | `.github/agents/<name>.agent.md` | Inline in the `.agent.md` file                     |
| CommandCenter        | `agents.py → build_agents()`     | `.github/prompts/system.md` + all `SKILL.md` files |

Both modes share the same `.github/skills/*/SKILL.md` instructions and `.github/skills/*/scripts/` executables.

### Key files and their roles

| File | Purpose | Who reads it |
| --- | --- | --- |
| `.github/prompts/system.md` | System prompt loaded by `agents.py` for CommandCenter mode | The LLM at runtime |
| `instructions.md` (repo root) | Agent purpose summary — read by the mutation sandbox during auto-repair to understand what the agent does | Mutation sandbox, humans |
| `.github/agents/<name>.agent.md` | VS Code Copilot Chat agent definition with inline system prompt | VS Code Copilot Chat |
| `.github/copilot-instructions.md` | Brief repo overview auto-loaded by GitHub Copilot in ALL contexts | GitHub Copilot (VS Code + chat) |
| `AGENTS.md` | Human + AI orientation document — persona, skills table, quick start | Humans and AI coding agents |

> **Note:** `instructions.md` and `system.md` serve different purposes. `system.md` is the runtime prompt the LLM sees. `instructions.md` is a higher-level summary the mutation sandbox reads during auto-repair to understand what the agent was built to do. Keep both files, but keep `instructions.md` brief (~1 paragraph of purpose).

---

## 1. Canonical Folder Structure

Every agent repo MUST use this exact layout:

```
agent-<name>/
├── agents.py                    # MAF build_agents() entry point — REQUIRED
├── config.json                  # CommandCenter contract — REQUIRED
├── AGENTS.md                    # Human + AI orientation document — REQUIRED
├── pyproject.toml               # Package definition and pytest config
├── requirements.txt             # pip-installable dependency list
├── README.md                    # Human-readable project overview
├── <name>.code-workspace        # VS Code workspace file (recommended)
│
├── .github/
│   ├── copilot-instructions.md  # Auto-loaded by GitHub Copilot in all contexts
│   ├── agents/
│   │   └── <name>.agent.md      # VS Code Copilot Chat custom agent definition
│   ├── prompts/
│   │   ├── system.md            # Primary system prompt loaded by agents.py
│   │   └── *.prompt.md          # Task-specific slash-command prompts for Copilot Chat
│   ├── instructions/
│   │   └── *.instructions.md    # Path-scoped coding rules (applyTo: "pattern/**")
│   └── skills/
│       └── <skill-name>/
│           ├── SKILL.md         # Skill instructions + YAML frontmatter
│           └── scripts/         # Python scripts that execute the skill
│
├── .tmp/                        # Non-durable working space — TRACKED in git
│   ├── scripts/                 # Shared utilities on PYTHONPATH — TRACKED
│   ├── search_cache/            # API response cache (contents gitignored)
│   ├── web_cache/               # Web scraping cache (contents gitignored)
│   └── *.py                     # One-off fix-up scripts (ephemeral)
│
├── agent-data/                  # Permanent reference data: catalogs, templates, PDFs, images
│   └── INDEX.md                 # Required — describes every asset in this folder
│
├── inputs/                      # User-provided files: RFPs, specs, uploaded docs
│   └── <project-slug>/          # One subfolder per project or intake
│
├── outputs/                     # Per-campaign results — tracked for team collaboration
│   └── <campaign-slug>/         # One subfolder per campaign run
│       ├── campaign_config.json
│       ├── step_1_*.json        # Step outputs (one JSON per pipeline step)
│       └── ...
│
├── tests/                       # pytest suite — stays at repo root always
│   ├── test_agents.py           # CI gate: build_agents() must pass
│   └── test_*.py                # Additional contract/path/data tests
│
├── .env                         # Local only — NEVER commit
├── .env.example                 # Committed template with placeholder values
└── .gitignore                   # See §14 for required entries
```

### Folder purpose rules

| Folder            | Durable?        | Committed?        | Purpose                               |
| ----------------- | --------------- | ----------------- | ------------------------------------- |
| `.github/skills/` | ✅ Permanent    | ✅ Always         | Skill instructions + feature scripts  |
| `.tmp/scripts/`   | ✅ Durable      | ✅ Always         | Shared Python utilities on PYTHONPATH |
| `.tmp/` (rest)    | ❌ Ephemeral    | ⚠️ Structure only | Caches, scratch, intermediate files   |
| `agent-data/`     | ✅ Permanent    | ✅ Always         | Read-only reference assets            |
| `inputs/`         | ✅ Per-project  | ✅ Optionally     | User-uploaded files                   |
| `outputs/`        | ✅ Per-campaign | ✅ Yes            | Campaign results, memory              |
| `tests/`          | ✅ Permanent    | ✅ Always         | CI gate, contract validation          |

> **Files Viewer visibility:** Only `inputs/`, `outputs/`, and `agent-data/`
> are visible in the Control Plane Files Viewer sidebar.  All other files
> (agent source, configs, skills, .github/, .tmp/, etc.) are hidden from the
> frontend user but remain fully accessible to the agent itself.  Agents MUST
> write any user-facing artefacts to one of these three directories.

### Hard layout rules

- Skills live in `.github/skills/<name>/` — NOT a top-level `skills/` folder.
  - *(Internal CommandCenter agents use `skills/` at the repo root — this doc covers external agents only.)*
- System prompt lives in `.github/prompts/system.md` — NOT `instructions.md` at root.
- `instructions.md` at repo root is optional but recommended: a 1-paragraph agent purpose summary the mutation sandbox reads during auto-repair.
- Shared utilities live in `.tmp/scripts/` — NOT `scripts/` at root.
- Reference data lives in `agent-data/` — NOT `data/`.
- User-provided files go in `inputs/` — NOT anywhere else.
- Campaign outputs go in `outputs/{slug}/` — NOT scattered at root.
- `tests/` stays at the repo root — NOT in `.tmp/` or `agent-data/`.
- `agents.py` and `config.json` MUST be at the repo root.
- `graph.py` is NOT supported. CommandCenter only calls `build_agents()`.
- No credentials anywhere in the repo. Local mode reads `.env`; CommandCenter injects from Integration Registry.

---

## 2. `config.json` — CommandCenter Contract

This file is the machine-readable contract between the repo and CommandCenter. Every field matters.

```json
{
  "name": "my-agent",
  "description": "One-line description with trigger keywords. CommandCenter routes requests using this.",
  "version": "0.1.0",
  "skill_repos": [],
  "integrations": ["anthropic", "zoho-crm", "serpapi"],
  "optional_integrations": [],
  "tags": ["sales", "outbound"],
  "tool_scope": null,
  "max_mutation_attempts": 1,
  "mcp_servers": {},
  "icon": "Bot",
  "category": "external",
  "webhook_routes": []
}
```

| Field | Required | Notes |
| --- | --- | --- |
| `name` | ✅ | Lowercase slug, 2–50 chars: letters, digits, hyphens only. Must match ``^[a-z0-9][a-z0-9-]{0,48}[a-z0-9]$``. **Do NOT include an ``agent-`` prefix** — the system strips it automatically. Shown in Control Plane. |
| `description` | ✅ | **Primary routing signal.** Include trigger keywords and domain. Be specific. Used by the orchestrator to decide which agent to route to. |
| `version` | — | Semver. Bump on breaking changes. Informational only — not validated by the runtime. |
| `integrations` | ✅ | Integration Registry keys — credentials injected as env vars at runtime (see §13). |
| `optional_integrations` | — | Credentials the agent can use if available but doesn't require. |
| `tags` | ✅ | Used for filtering in Control Plane. |
| `tool_scope` | — | Limits which **platform-injected tools** are attached to this agent. If omitted or ``null``, ALL 15+ platform tools are injected (which may hurt accuracy — see §2b). Use a list of tool function names, e.g. ``["call_agent", "web_search", "write_artifact"]``. |
| `max_mutation_attempts` | ✅ | **MUST be ``1``.** Hard constraint — never change this. |
| `mcp_servers` | — | MCP server config overrides (merged with MCP registry at runtime). Rarely needed — prefer registering MCP servers via the Control Plane UI. |
| `icon` | — | Lucide icon name for the Control Plane agent picker (e.g. ``"Mail"``, ``"Bot"``, ``"ShoppingCart"``). Default: ``"Bot"``. |
| `category` | — | Grouping key for the Control Plane UI (e.g. ``"sales"``, ``"ops"``, ``"external"``). |
| `webhook_routes` | — | List of ``{"source": "...", "event_type": "..."}`` objects. When populated, CommandCenter routes matching webhooks to this agent (Phase 2 — currently hardcoded in the gateway). |

### Fields NOT consumed by the runtime (reserved for future use)

The following fields appear in older versions of this guide but are **not currently read** by the CommandCenter runtime. Include them if you want forward-compatibility, but they will not affect agent behaviour today:

| Field | Status |
| --- | --- |
| `model_tier` | Not consumed — model selection is handled by the Control Plane UI per-chat. |
| `execution_budget` | Not consumed — timeout/budget limits are set via environment variables (``COPILOT_TOOL_TIMEOUT_SECONDS``, etc.). |
| `authority` | Not consumed — all agents run with the same authority model. |

### How `agent_runtime` is determined

You do NOT set `agent_runtime` in `config.json` — CommandCenter auto-determines it at registration time:

| Registration method | `agent_runtime` | What it means |
| --- | --- | --- |
| GitHub repo URL (``owner/repo`` or full HTTPS URL) | ``"github-copilot"`` | Agent runs via the **GitHub Copilot SDK** (``GitHubCopilotAgent``). Gets Copilot-native features: built-in `sql`/todos tool, VS Code Copilot parity toolset. All platform-injected tools are also attached. |
| Local path (dev mode) | ``"maf"`` | Agent runs as a plain **MAF Agent**. Lighter runtime — fewer built-in tools, but platform-injected tools are still attached. |

> **For agent authors:** Your `agents.py` should use ``GitHubCopilotAgent`` as shown in §3. CommandCenter will import and run it correctly in both modes. The runtime mode is transparent to the agent code.

---

## 2a. Platform-Injected Tools (available to every agent)

CommandCenter automatically attaches **15+ tools** to every agent at runtime via the executor's ``_inject_agent_tools()``. These tools are available to the LLM **without the agent author writing any code**. You do NOT wire them in `agents.py` — they are injected transparently.

Knowing these tools exist is critical:
- **Don't re-implement them.** If you need web search, use the injected `web_search` — don't build your own.
- **Reference them in your system prompt.** Your `.github/prompts/system.md` should tell the LLM when to use each one.
- **Use `tool_scope` to limit them.** If your agent doesn't need all 15+, set `tool_scope` in `config.json` to improve accuracy (see §2b).

### Complete injected tool catalog

| Tool | When the LLM should use it |
| --- | --- |
| `call_agent(agent_name, message)` | Delegate a sub-task to another registered agent. Blocks until the sub-agent responds. |
| `call_agents_parallel(tasks)` | Run multiple agents concurrently. Pass a JSON array of `{"agent", "message"}` objects. |
| `call_agent_background(agent_name, message)` | Fire-and-forget delegation. Use when the result is not needed immediately. |
| `web_search(query, max_results=5)` | Search the web via DuckDuckGo. Use for current info, news, company research. No API key needed. |
| `fetch_page(url, max_chars=8000)` | Fetch a public URL as clean Markdown text via Jina Reader. |
| `write_artifact(path, content, encoding?)` | Write a file to the agent workspace. Files land in `outputs/` by default and appear in the Control Plane Files Viewer sidebar. Returns a `download_url` — embed it as a clickable link in your reply. |
| `remember(query)` | Search episodic memory (Mem0) for past facts about the user. Call BEFORE making claims about history or preferences. |
| `recall_timeline(entity, query)` | Query the bi-temporal knowledge graph (Graphiti): "when did X happen?" or entity relationship history. |
| `save_memory(fact)` | Persist a high-signal user fact to Mem0. Routine turns are handled automatically — use this sparingly for important discoveries. |
| `save_episode(name, content, source?)` | Record a time-stamped episode in Graphiti. Entities and relationships are extracted automatically. |
| `manage_todo_list(todoList)` | Update the live "Todos (n/m)" panel in the Control Plane chat UI. Takes a JSON object with `"todoList"` (complete array) and optional `"operation"` (`"write"` or `"read"`). Each item: `id` (number), `title` (string), `status` (`"not-started"`, `"in-progress"`, `"completed"`). Use VERY frequently — the user sees real-time progress. |
| `ask_user(question, choices?, allowFreeform?)` | **Native HITL — blocks the agent turn.** Pause and ask the user ONE clarifying question via an interactive card. Execution truly pauses; resumes automatically when the user answers. Use when you need to disambiguate, a parameter is missing, or a decision has important implications. |
| `ask_questions(questions)` | Multi-question HITL card. Takes a JSON object with a `"questions"` array. Prefer `ask_user` for single blocking questions. |
| `get_errors(filePaths?)` | Check Python files for syntax, type, and lint errors. Call after editing or creating files. Pass a JSON array of file paths or `[]` to auto-discover recently changed files. |
| `save_note(path, fact)` | Append a dated bullet to a Markdown notes file under `agent-data/`. Use `agent-data/NOTES.md` as your canonical cross-session working memory. |
| `recall_notes(path, query?)` | Read back a notes file, optionally filtered by a search query. Use at session start to restore context from previous sessions. |
| `query_history(sql)` | Run a SELECT-only SQL query against the chat history database (tables: `chat_session`, `chat_message`). Use to recall past conversations, find decisions, or resume work. |
| `github_search(query, scope?, maxResults?)` | Lexical search across public GitHub repositories. Supports `language:python`, `repo:owner/name`, `path:src/` filters. |
| `github_repo_search(repo, query?)` | Search within a specific GitHub repository for code snippets and implementation patterns. |

### How your system prompt should reference injected tools

Your `.github/prompts/system.md` should include a section like this so the LLM knows these tools exist:

```markdown
## Platform Tools (injected by CommandCenter)

You have access to these tools automatically — do NOT re-implement them:
- `call_agent` / `call_agents_parallel` — delegate to other agents
- `web_search` / `fetch_page` — web access (no API key needed)
- `write_artifact` — write files visible in the UI sidebar
- `manage_todo_list` — update the live task panel
- `ask_user` — pause and ask the user a clarifying question
- `remember` / `save_memory` / `save_episode` — memory and knowledge graph
- `get_errors` — check code for syntax/lint errors
- `save_note` / `recall_notes` — repo-scoped working memory
- `query_history` — search past conversations
```

The executor also appends a comprehensive tool guidance block to the system message at runtime, so the LLM will always have full documentation even if your system prompt is minimal.

---

## 2b. `tool_scope` — Limiting Injected Tools

**Why this matters:** The Berkeley Function-Calling Leaderboard has shown that **every model degrades in accuracy as the number of available tools increases.** If your agent doesn't need all 15+ platform tools, use `tool_scope` to limit what gets injected.

Set `tool_scope` in `config.json` to a list of tool function names:

```json
{
  "tool_scope": ["web_search", "fetch_page", "write_artifact", "manage_todo_list", "ask_user"]
}
```

Only the named tools will be injected. If `tool_scope` is omitted or `null`, ALL tools are injected (default).

**Valid tool names** (the function `__name__` of each injected tool):
`call_agent`, `call_agents_parallel`, `call_agent_background`, `web_search`, `fetch_page`, `write_artifact`, `remember`, `recall_timeline`, `save_memory`, `save_episode`, `manage_todo_list`, `ask_questions`, `get_errors`, `save_note`, `recall_notes`, `query_history`, `github_search`, `github_repo_search`

> **Note:** If none of the names in your `tool_scope` list match any known tool, the executor falls back to injecting ALL tools and logs a warning.

---

## 3. `agents.py` — Canonical Template

`build_agents()` is the **only entry point** CommandCenter calls. It must be synchronous, zero-argument, and return a non-empty `list[GitHubCopilotAgent]`. No I/O, no side effects at import time.

```python
"""agent-<name> — MAF Agent definitions.

Your repo should be named ``agent-<name>`` on GitHub, but the bare agent name
in config.json (and this file) is ``<name>`` without the prefix.

Exports:
    build_agents() -> list[GitHubCopilotAgent]   (Dynamic Agent Loader entry point)

Architecture (DOE v2):
  Layer 1 (Skills)        — .github/skills/*/SKILL.md + .github/skills/*/scripts/
  Layer 2 (Orchestration) — THIS FILE (GitHubCopilotAgent via MAF)
  Layer 3 (Execution)     — .tmp/scripts/ shared utilities + skill scripts
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────────
AGENT_DIR   = Path(__file__).parent.resolve()
PROMPTS_DIR = AGENT_DIR / ".github" / "prompts"
SKILLS_DIR  = AGENT_DIR / ".github" / "skills"
SCRIPTS_DIR = AGENT_DIR / ".tmp" / "scripts"

# Make .tmp/scripts/ importable by skill scripts at runtime
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ── Subprocess helpers ────────────────────────────────────────────────────────

def _run_env() -> dict[str, str]:
    """Add .tmp/scripts/ to PYTHONPATH so skill scripts can import shared utilities."""
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    scripts = str(SCRIPTS_DIR)
    env["PYTHONPATH"] = f"{scripts}{os.pathsep}{existing}" if existing else scripts
    return env


async def _run(args: list[str]) -> str:
    """Run a script as a subprocess. Raises RuntimeError on non-zero exit."""
    result = await asyncio.to_thread(
        subprocess.run, args,
        capture_output=True, text=True,
        cwd=str(AGENT_DIR), env=_run_env(),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or f"Script exited {result.returncode}")
    return result.stdout or "(no output)"


# ── System prompt ─────────────────────────────────────────────────────────────

def _build_system_prompt() -> str:
    """Load .github/prompts/system.md + append each .github/skills/*/SKILL.md as a tool block."""
    parts: list[str] = []
    system_md = PROMPTS_DIR / "system.md"
    if system_md.exists():
        parts.append(system_md.read_text(encoding="utf-8", errors="replace"))
        if SKILLS_DIR.exists():
            skill_sections: list[str] = []
            for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
                content = skill_md.read_text(encoding="utf-8", errors="replace")
                skill_sections.append(f"\n### Tool: {skill_md.parent.name}\n\n{content}")
            if skill_sections:
                parts.append("\n\n---\n\n## Registered Skill Tool Descriptions\n")
                parts.extend(skill_sections)
    else:
        # Fallback: load AGENTS.md if system.md is absent
        agents_md = AGENT_DIR / "AGENTS.md"
        if agents_md.exists():
            parts.append(agents_md.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


SYSTEM_PROMPT = _build_system_prompt()


# ── Tool functions ────────────────────────────────────────────────────────────
#
# Every async def below is a callable tool exposed to the LLM.
# The docstring IS the routing signal — write "Use this when the user asks about X."
# Return str. Raise on failure — never swallow exceptions or return {"error": ...}.
#
# Pattern A — skill script in .github/skills/<name>/scripts/:
#
#   async def do_something(arg: str) -> str:
#       "Run the X skill. Use when the user asks about Y. arg: one of a|b|c."
#       return await _run([sys.executable,
#           str(SKILLS_DIR / "my-skill" / "scripts" / "main.py"), arg])
#
# Pattern B — shared utility in .tmp/scripts/:
#
#   async def sync_sheet(sheet_id: str) -> str:
#       "Sync results to Google Sheets. Use after any data collection step."
#       return await _run([sys.executable,
#           str(SCRIPTS_DIR / "append_to_sheet.py"), "--sheet-id", sheet_id])

async def example_tool(action: str) -> str:
    """Run the example skill. Use when the user asks about [domain]. action: one of list|run|summary."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "example-skill" / "scripts" / "main.py"), action])


# ── LiteLLM provider (CommandCenter mode) ────────────────────────────────────

def _llm_provider() -> dict[str, Any]:
    base_url = os.environ.get("LITELLM_BASE_URL", "http://127.0.0.1:8080")
    api_key  = os.environ.get("LITELLM_MASTER_KEY", "sk-local")
    return {"type": "openai", "base_url": f"{base_url}/v1", "api_key": api_key}


# ── Agent factory ─────────────────────────────────────────────────────────────

def build_agent() -> "GitHubCopilotAgent":
    from agent_framework_github_copilot import GitHubCopilotAgent  # type: ignore[import]
    from copilot.types import PermissionHandler                     # type: ignore[import]

    return GitHubCopilotAgent(
        name="my-agent",
        description="One-line description matching config.json.",
        instructions=SYSTEM_PROMPT,
        tools=[
            example_tool,
            # Add more async def tool functions here — one per skill capability
        ],
        default_options={
            "model": "tier-balanced",
            "provider": _llm_provider(),
            "mcp_servers": {},
            "on_permission_request": PermissionHandler.approve_all,
        },
    )


def build_agents() -> list:
    """Dynamic Agent Loader entry point. Synchronous, zero-argument, pure."""
    return [build_agent()]


__all__ = ["build_agents", "build_agent", "SYSTEM_PROMPT"]
```

### Hard rules for `agents.py`

- `build_agents()` is synchronous, zero-argument. No I/O at module import time.
- `tools=[...]` must not be empty — an agent with no tools only apologises.
- Every tool must be `async def` and return `str`. Raise `RuntimeError` on failure.
- Use `sys.executable`, not `"python"`, in all subprocess calls.
- Import `GitHubCopilotAgent` and `PermissionHandler` **inside** `build_agent()` — they are injected at runtime by CommandCenter and not available during local import/testing.
- `on_permission_request` must be `PermissionHandler.approve_all`.
- Never instantiate `GitHubCopilotAgent` outside of `build_agents()`.

---

## 4. `AGENTS.md` — Agent Orientation

This file is read by both humans and AI coding agents to understand what the agent does and how to work with it. Keep it under 300 lines.

```markdown
# Agent Name — Agent Instructions

> One-sentence persona statement. e.g. "You are a world-class B2B sales agent..."

## Architecture (DOE v2)

**Layer 1 — Skills:** `.github/skills/*/SKILL.md` define goals, inputs, scripts, outputs.
**Layer 2 — Orchestration:** You (the LLM) read SKILL.md, call scripts, apply judgment.
**Layer 3 — Execution:** `.github/skills/*/scripts/` and `.tmp/scripts/` do the actual work.

## Available Skills

| Skill      | SKILL.md                             | What it does         |
| ---------- | ------------------------------------ | -------------------- |
| skill-name | `.github/skills/skill-name/SKILL.md` | One-line description |

## File Organization

- `.github/skills/` — Skill instructions + feature scripts
- `.tmp/scripts/` — Shared utilities (on PYTHONPATH)
- `agent-data/` — Reference data: catalogs, templates, PDFs, images
- `inputs/` — User-provided files (subfolders per project)
- `outputs/` — Campaign results (subfolders per campaign slug)

## Quick Start

1. Copy `.env.example` → `.env` and fill in API keys
2. `pip install -r requirements.txt`
3. Tell the agent what you want to do
```

---

## 5. `.github/prompts/system.md` — System Prompt

The primary prompt loaded by `agents.py` for CommandCenter mode. Keep under ~300 lines.

```markdown
# Agent Name — System Prompt

## Purpose

[One paragraph — what the agent does, who it serves, what integrations it uses.]

## Available Tools

| Tool           | When to call it                    |
| -------------- | ---------------------------------- |
| `example_tool` | User asks about X or wants to do Y |

## Rules

1. Always call the relevant tool — never answer from memory alone.
2. Raise errors explicitly — never silently return partial results.
3. Do NOT fabricate data. If a tool fails, say so.

## Output Format

- Lead with one sentence of context
- Results as bullet points or a markdown table
- End with the next suggested action
```

---

## 6. `.github/agents/<name>.agent.md` — VS Code Copilot Chat

This file activates the agent in VS Code Copilot Chat. It is independent of CommandCenter.

```markdown
---
name: My Agent
description: >
  One-line description with trigger keywords. Max ~300 chars.
  Used by Copilot Chat to decide when to activate this agent.
model: claude-sonnet-4-5
tools:
  - runCommands
  - codebase
  - editFiles
  - fetch
  - search
  - terminal
---

# My Agent

[Paste the contents of .github/prompts/system.md here]

## Skills

- **skill-name** (`.github/skills/skill-name/SKILL.md`) — brief description

## How to Use

- Read the relevant `SKILL.md` before running any script
- Run scripts via the terminal tool: `python .github/skills/<name>/scripts/main.py [args]`
- Credentials in `.env` — never commit
```

**Available `tools` values for VS Code Copilot Chat:**
`runCommands`, `codebase`, `editFiles`, `changes`, `extensions`, `fetch`, `findTestFiles`, `githubRepo`, `new`, `openSimpleBrowser`, `problems`, `runNotebooks`, `runTasks`, `search`, `searchResults`, `terminalLastCommand`, `terminalSelection`, `terminal`, `testFailure`, `usages`, `vscodeAPI`

---

## 7. `.github/skills/<name>/SKILL.md` — Skill Definition

Every skill needs a `SKILL.md` with YAML frontmatter and a standard body.

```yaml
---
name: skill-name
description: >
  What this skill does and WHEN to use it. Include trigger keywords.
  This text is appended to the system prompt — be specific. Max 1024 chars.
when_to_use: "Plain English trigger conditions."
authority: read
cost_tier: 1
version: 0.1.0
---
```

```markdown
# Skill Name

One-line summary of what this skill does.

## Scripts

| Script              | Purpose             |
| ------------------- | ------------------- |
| `scripts/main.py`   | Primary entry point |
| `scripts/helper.py` | Supporting logic    |

## Usage

\`\`\`bash
python .github/skills/<name>/scripts/main.py --help
python .github/skills/<name>/scripts/main.py --input "..." --output "outputs/slug/"
\`\`\`

## Required Environment Variables

- `MY_API_KEY` — obtained from [provider]. Set in `.env` or Integration Registry.

## Outputs

Writes to `outputs/{campaign-slug}/step_N_*.json`.
```

Updating a `SKILL.md` takes effect on the next CommandCenter run — no changes to `agents.py` needed.

---

## 8. `.tmp/scripts/` — Shared Utilities

Scripts used by 2+ skills live here, not inside any skill folder. `.tmp/scripts/` is **tracked in git**.

`agents.py` adds it to `PYTHONPATH` via `_run_env()`, so any skill script can do:

```python
from retry_utils import retry_with_backoff, safe_api_call
from campaign_data_manager import create_campaign, save_step
```

### Promotion path

```
One-off fix-up script (.tmp/*.py)
        │  used successfully across 2+ campaigns
        ▼
Shared utility (.tmp/scripts/*.py)
        │  grows into multi-step domain workflow
        ▼
Skill (.github/skills/<name>/SKILL.md + scripts/)
```

### What belongs in `.tmp/scripts/` vs a skill

| Criterion                                 | `.tmp/scripts/`   | Skill script                           |
| ----------------------------------------- | ----------------- | -------------------------------------- |
| Used by 2+ skills?                        | ✅ Yes            | ❌ No — put in that skill's `scripts/` |
| Domain-agnostic?                          | ✅ Yes            | ❌ No                                  |
| Needs SKILL.md instructions?              | ❌ No             | ✅ Yes                                 |
| Has external dependencies as sub-scripts? | ❌ Self-contained | ✅ Potentially                         |

---

## 9. `agent-data/` — Reference Data

Permanent assets the agent reads at runtime. Committed and never deleted.

```
agent-data/
├── INDEX.md                  # REQUIRED — describes every asset
├── products_catalog.json     # Machine-readable product/service database
├── templates/                # Document templates (DOCX, etc.)
├── images/                   # Product images and renders
├── specs/                    # Technical specification PDFs
├── brochures/                # Sales collateral PDFs
└── marp-theme/               # Presentation theme CSS
```

**Rules:**

- Every asset must be listed in `agent-data/INDEX.md` with its path, purpose, and usage example.
- Scripts reference assets via `AGENT_DIR / "agent-data" / ...` — never hardcode absolute paths.
- Do not put user-provided files here — those go in `inputs/`.

---

## 10. `inputs/` and `outputs/` — Data Flow

### `inputs/` — User-Provided Files

Files uploaded or provided by the user for a specific project.

```
inputs/
└── <project-slug>/          # One subfolder per project or intake
    ├── rfp.pdf
    ├── spec.docx
    └── reference-data.xlsx
```

Files here are read-only from the agent's perspective. Never write outputs here.

### `outputs/` — Campaign Results

Every campaign run creates a subfolder. The step JSON structure is the contract between pipeline steps.

```
outputs/
├── _memory/                         # Cross-campaign long-term memory (always present)
│   ├── agent_long_term_memory.json
│   └── agent_memory_index.json
└── <campaign-slug>/                 # One subfolder per campaign
    ├── campaign_config.json         # Campaign metadata and configuration
    ├── step_1_product_analysis.json
    ├── step_2_competitive_analysis.json
    ├── step_3_industry_targeting.json
    ├── step_4_company_prospects.json
    ├── step_5_decision_makers.json
    ├── step_6_outreach_sequences.json
    ├── step_7_campaign_tracker.json
    └── research/                    # Supporting research artefacts
```

---

## 11. `pyproject.toml` — Package Definition

```toml
[project]
name = "agent-my-agent"
version = "0.1.0"
description = "Short description matching config.json."
requires-python = ">=3.11"
dependencies = [
    "python-dotenv",
    "requests",
    # Add skill-specific deps here
    # agent-framework-github-copilot is injected by CommandCenter at runtime
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-asyncio>=0.24"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

Note: `agent-framework-github-copilot` and `cb_llm` are **injected by CommandCenter at runtime** — do not add them to `dependencies`. The `build_agent()` function imports them inside the function body specifically to avoid import failures during local testing.

---

## 12. `tests/` — Test Suite

`tests/` lives at the repo root permanently. It is the CommandCenter CI gate.

### Required: `tests/test_agents.py`

```python
"""CommandCenter CI gate — these three tests must pass for the agent to be registered."""
import pytest

def test_build_agents_importable():
    """agents.py must be importable without errors."""
    import agents  # noqa: F401

def test_build_agents_returns_list():
    """build_agents() must return a non-empty list."""
    try:
        from agents import build_agents
        result = build_agents()
        assert isinstance(result, list) and len(result) >= 1
    except ImportError:
        pytest.skip("MAF runtime not available — skipping in local env")

def test_agent_has_name_and_instructions():
    """Agent must have a name and a non-trivial system prompt."""
    try:
        from agents import build_agents
        agent = build_agents()[0]
        instructions = getattr(agent, "instructions", None) or getattr(agent, "_instructions", None)
        assert instructions and len(instructions) > 50
    except ImportError:
        pytest.skip("MAF runtime not available")

def test_agent_has_tools():
    """Agent must have at least one tool — an empty tools list means it can only apologise."""
    try:
        from agents import build_agents
        agent = build_agents()[0]
        tools = getattr(agent, "tools", None) or getattr(agent, "_tools", None) or []
        assert len(tools) > 0, "Agent has no tools — it will only apologise"
    except ImportError:
        pytest.skip("MAF runtime not available")

def test_system_prompt_contains_skills():
    """System prompt must include content from at least one SKILL.md."""
    from agents import SYSTEM_PROMPT
    assert len(SYSTEM_PROMPT) > 100
```

### Recommended additional tests

```python
# tests/test_path_resolution.py — verify all script paths are correct after any restructure
def test_all_scripts_help_works():
    import subprocess, sys
    from pathlib import Path
    REPO = Path(__file__).resolve().parent.parent
    scripts = [
        ".tmp/scripts/campaign_data_manager.py",
        ".tmp/scripts/self_anneal_diagnostics.py",
    ]
    for s in scripts:
        r = subprocess.run([sys.executable, str(REPO / s), "--help"],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, f"{s} --help failed: {r.stderr[:200]}"
```

Run the full suite: `python -m pytest tests/ -v`

---

## 13. Integration Credentials

CommandCenter injects credentials from the Integration Registry as environment variables before running the agent. Scripts always use `os.getenv(...)` — this works identically in local (`.env`) and CommandCenter modes.

### `.env.example` (commit this, not `.env`)

```bash
# LiteLLM (local dev only — CommandCenter injects at runtime)
LITELLM_BASE_URL=http://127.0.0.1:8080
LITELLM_MASTER_KEY=sk-local

# AI providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Sales / data
APOLLO_API_KEY=
SERPAPI_API_KEY=
APIFY_API_TOKEN=
INSTANTLY_API_KEY=
ANYMAILFINDER_API_KEY=

# CRM
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_REFRESH_TOKEN=

# Google Workspace
GOOGLE_SHEETS_SA_JSON_PATH=
```

### Integration Registry keys → environment variables

| Integration key | Environment variable(s)                                      |
| --------------- | ------------------------------------------------------------ |
| `anthropic`     | `ANTHROPIC_API_KEY`                                          |
| `openai`        | `OPENAI_API_KEY`                                             |
| `litellm`       | `LITELLM_BASE_URL`, `LITELLM_MASTER_KEY`                     |
| `apollo`        | `APOLLO_API_KEY`                                             |
| `serpapi`       | `SERPAPI_API_KEY`                                            |
| `apify`         | `APIFY_API_TOKEN`                                            |
| `instantly`     | `INSTANTLY_API_KEY`                                          |
| `anymailfinder` | `ANYMAILFINDER_API_KEY`                                      |
| `zoho-crm`      | `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN` |
| `google-sheets` | `GOOGLE_SHEETS_SA_JSON_PATH`                                 |
| `clickup`       | `CLICKUP_API_TOKEN`, `CLICKUP_WORKSPACE_ID`                  |

---

## 14. `.gitignore` — Required Entries

```gitignore
# Secrets
.env
.env.local
credentials.json
token.json
*.token_cache.json

# Python
__pycache__/
*.py[cod]
.venv/
venv/
ENV/

# .tmp/ caches — structure tracked, contents not
.tmp/search_cache/*.json
.tmp/web_cache/*
!.tmp/search_cache/README.md
!.tmp/web_cache/README.md
# .tmp/scripts/ IS tracked — shared utilities
!.tmp/scripts/**

# OS / IDE
.DS_Store
Thumbs.db
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Keep .vscode/ settings
!.vscode/
```

---

## 15. Build Checklist

Use this checklist when creating a new agent from scratch.

```
- [ ] 1.  Scaffold repo as `agent-<name>` on GitHub with the folder structure from §1. The bare agent name in `config.json` is `<name>` (no prefix).
- [ ] 2.  config.json — name (bare slug, no `agent-` prefix), description (trigger keywords!), integrations, tags, `max_mutation_attempts: 1`, optional `tool_scope` (see §2b).
- [ ] 3.  .github/prompts/system.md — agent identity, tool table (include platform-injected tools reference — see §2a), rules (≤ 300 lines).
- [ ] 4.  AGENTS.md — persona, skills table, file organization, quick start
- [ ] 5.  .github/agents/<name>.agent.md — frontmatter with model + tools, inline system prompt
- [ ] 6.  .github/copilot-instructions.md — brief repo overview for Copilot in all contexts
- [ ] 7.  instructions.md (repo root) — 1-paragraph agent purpose summary for mutation sandbox
- [ ] 8.  For each skill: mkdir .github/skills/<name>, write SKILL.md + scripts/*.py
- [ ] 9.  .tmp/scripts/ — add shared utilities (retry_utils.py, campaign_data_manager.py, etc.)
- [ ] 10. agent-data/ — add reference assets + write INDEX.md describing every file
- [ ] 11. inputs/ — create folder with .gitkeep (user files land here per project)
- [ ] 12. agents.py — use canonical template (§3), wire one async def tool per skill capability
- [ ] 13. pyproject.toml — dependencies, dev extras, pytest config (§11)
- [ ] 14. requirements.txt — pip-installable list for setup scripts
- [ ] 15. tests/test_agents.py — minimum CI gate suite from §12
- [ ] 16. .env.example — all required keys with placeholder values (§13)
- [ ] 17. .gitignore — required entries from §14
- [ ] 18. Smoke test: `python -m pytest tests/ -v` (all pass or skip — no failures)
- [ ] 19. Import test: `python -c "from agents import SYSTEM_PROMPT; print(len(SYSTEM_PROMPT), 'chars')"`
- [ ] 20. Tools test: `python -c "from agents import build_agents"` (must not raise)
- [ ] 21. Review §18 (Agent Registration Flow) — verify your repo meets all registration requirements
- [ ] 22. Register in CommandCenter: Control Plane → Agents → Add Agent → paste GitHub repo URL
```

---

## 16. Anti-Patterns

These will cause registration failures, silent bugs, or CommandCenter rejection:

| ❌ Anti-pattern                            | ✅ Correct                          |
| ------------------------------------------ | ----------------------------------- |
| `scripts/` at repo root                    | `.tmp/scripts/`                     |
| `data/` at repo root                       | `agent-data/`                       |
| `skills/` at repo root                     | `.github/skills/`                   |
| `instructions.md` at root                  | `.github/prompts/system.md`         |
| `"python"` in subprocess args              | `sys.executable`                    |
| `tools=[]` empty                           | At least one `async def` tool       |
| `max_mutation_attempts: 2` or higher       | Always `1`                          |
| I/O at module import time in `agents.py`   | All I/O inside function bodies      |
| `GitHubCopilotAgent(...)` at module level  | Only inside `build_agents()`        |
| `import GitHubCopilotAgent` at top of file | Import inside `build_agent()`       |
| `graph.py` present                         | Delete it — LangGraph not supported |
| Credentials hardcoded                      | `os.getenv("KEY_NAME")` always      |
| `except Exception: return {"error": ...}`  | `raise RuntimeError(...)` always    |
| User files in `agent-data/`                | User files in `inputs/<project>/`   |
| Campaign outputs scattered at root         | `outputs/<campaign-slug>/`          |
| ``"name": "agent-my-agent"`` in config.json | ``"name": "my-agent"`` (no prefix) |
| Building your own `web_search` tool        | Use the injected `web_search` (see §2a) |
| Re-implementing any platform-injected tool | Reference it in system prompt; don't code it |

---

## 17. Self-Mutation and Auto-Repair

CommandCenter monitors agent repos and applies auto-repairs under two conditions:

**Proactive skill sync:** After every `git pull`, any script found in `.github/skills/*/scripts/` that is not wired as a tool in `agents.py` is automatically added as a stub `async def` tool function and committed.

**AgentLoadError repair:** If `agents.py` fails to import, `build_agents()` throws, or the return type is wrong, a Copilot SDK mutation sandbox generates a fix, runs `pytest tests/`, and commits the fix directly. Maximum 1 attempt per failure event.

### How the mutation sandbox works

1. A **detached Docker container** (`acb-mutation-runner`) is spawned with the failing agent's local clone mounted at `/workspace/repo`.
2. The sandbox receives the full error traceback, the agent's `instructions.md` (purpose summary), and — for structural incompatibilities — this entire `agent_repo_compatibility.md` guide as context.
3. It generates a fix and runs `pytest tests/` inside the container.
4. **Auto-push gate:** If all tests pass → the commit is pushed directly. If tests fail → the commit is **queued for human approval** in the Control Plane Inbox. A human must review and approve/reject before the commit is pushed.
5. The live agent continues to use its pre-mutation code until the fix commit is pushed and pulled.

**Implication:** Keep `tests/test_agents.py` tight. If the tests are weak, auto-repair may commit a broken fix that passes flawed tests — but the human review gate (step 4) catches this before it reaches production.

To revert any auto-commit: `git revert <hash>` and push.

---

## 18. Agent Registration Flow

When a user registers your agent in CommandCenter (Control Plane → Agents → Add Agent → paste GitHub repo URL), here's what happens:

1. **Name validation:** The agent name is checked against ``^[a-z0-9][a-z0-9-]{0,48}[a-z0-9]$``. Must be unique — no duplicate names allowed.
2. **`config.json` fetch:** CommandCenter fetches your repo's `config.json` from GitHub (tries `main`, `master`, `HEAD` branches in order). Fields `description`, `tags`, `integrations`, and `optional_integrations` are auto-populated from `config.json` if left empty in the registration form.
3. **`agent_runtime` assignment:** If you provided a GitHub URL → `"github-copilot"`. If you provided a local path → `"maf"`.
4. **Persistence:** The agent entry is saved to the `dynamic_agents` Postgres table (survives deploys and reboots).
5. **Background clone:** A background task clones your repo into ``{agents_clone_dir}/repos/{agent_name}/`` so the agent is warm before its first run.
6. **Live:** The agent appears in the Control Plane agent picker immediately. It can be invoked via `/agent/run/stream`.

### Registration checklist for agent authors

- [ ] Repo is public (or the CommandCenter GitHub token has access to your org)
- [ ] `config.json` is at the repo root and is valid JSON
- [ ] `agents.py` is at the repo root and exports `build_agents() -> list`
- [ ] `build_agents()` returns at least one agent with a non-trivial system prompt and at least one tool
- [ ] `max_mutation_attempts` is set to `1`
- [ ] No credentials are hardcoded — all secrets use `os.getenv(...)`
- [ ] Repo name follows the convention (e.g. `agent-my-agent` for discoverability, though the bare agent name in `config.json` should be `my-agent`)
