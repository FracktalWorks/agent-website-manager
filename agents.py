"""agent-website-manager — MAF Agent definitions.

Agent Website Manager — WordPress website development & management agent.
Connects via Hostinger MCP and WordPress REST API.

Exports:
    build_agents() -> list[GitHubCopilotAgent]

Architecture (DOE v2):
  Layer 1 (Skills) — .github/skills/*/SKILL.md + scripts/
  Layer 2 (Orchestration) — THIS FILE
  Layer 3 (Execution) — .tmp/scripts/ shared utilities + skill scripts
"""
from __future__ import annotations

import asyncio, os, subprocess, sys
from pathlib import Path
from typing import Any

AGENT_DIR   = Path(__file__).parent.resolve()
PROMPTS_DIR = AGENT_DIR / ".github" / "prompts"
SKILLS_DIR  = AGENT_DIR / ".github" / "skills"
SCRIPTS_DIR = AGENT_DIR / ".tmp" / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _run_env():
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    scripts = str(SCRIPTS_DIR)
    if existing:
        env["PYTHONPATH"] = scripts + os.pathsep + existing
    else:
        env["PYTHONPATH"] = scripts
    return env


async def _run(args):
    result = await asyncio.to_thread(
        subprocess.run, args, capture_output=True, text=True,
        cwd=str(AGENT_DIR), env=_run_env(),
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr or f"Script exited {result.returncode}")
    return result.stdout or "(no output)"


def _build_system_prompt():
    parts = []
    system_md = PROMPTS_DIR / "system.md"
    if system_md.exists():
        parts.append(
            system_md.read_text(encoding="utf-8", errors="replace"))
        if SKILLS_DIR.exists():
            skill_sections = []
            for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
                text = skill_md.read_text(
                    encoding="utf-8", errors="replace")
                skill_sections.append(
                    "\n### Tool: " + skill_md.parent.name
                    + "\n\n" + text)
            if skill_sections:
                parts.append(
                    "\n\n---\n\n"
                    "## Registered Skill Tool Descriptions\n")
                parts.extend(skill_sections)
    else:
        agents_md = AGENT_DIR / "AGENTS.md"
        if agents_md.exists():
            parts.append(
                agents_md.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


SYSTEM_PROMPT = _build_system_prompt()


# ── Tool functions ──────────────────────────────────────────────────────


async def wordpress_management(action: str) -> str:
    """Run the wordpress_management skill. Use when user asks about
    WordPress content, pages, posts, media, plugins, themes, SEO.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "wordpress_management" / "scripts" / "wp_rest_api.py"),
        action])


async def hostinger_management(action: str) -> str:
    """Run the hostinger_management skill. Use when user asks about
    Hostinger hosting, domains, email, SSL, files, databases.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "hostinger_management" / "scripts" / "hostinger_mcp.py"),
        action])


async def elementor_builder(action: str) -> str:
    """Run the elementor_builder skill. Use when user asks about
    Elementor page builder, templates, kits, widgets.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "elementor_builder" / "scripts" / "wp_elementor.py"),
        action])


async def woocommerce_management(action: str) -> str:
    """Run the woocommerce_management skill. Use when user asks about
    WooCommerce store, products, orders, customers, coupons, reports.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "woocommerce_management" / "scripts" / "wc_rest_api.py"),
        action])


async def media_cleanup(action: str) -> str:
    """Run the media_cleanup skill. Use when user asks about
    cleaning up unused images, optimizing media, WebP conversion.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "media_cleanup" / "scripts" / "wp_media_cleanup.py"),
        action])


async def performance_optimization(action: str) -> str:
    """Run the performance_optimization skill. Use when user asks about
    page speed, caching, LSCache, minification, CDN, DB optimization.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "performance_optimization" / "scripts" / "wp_cache_setup.py"),
        action])


async def site_health_monitor(action: str) -> str:
    """Run the site_health_monitor skill. Use when user asks about
    site health, uptime, PHP errors, debug logs, cron, disk, SSL.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "site_health_monitor" / "scripts" / "wp_health_check.py"),
        action])


async def security_hardening(action: str) -> str:
    """Run the security_hardening skill. Use when user asks about
    vulnerability scan, security headers, SSL audit, XML-RPC, permissions.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "security_hardening" / "scripts" / "wp_security_scan.py"),
        action])


async def deployment_manager(action: str) -> str:
    """Run the deployment_manager skill. Use when user asks about
    staging, deployment, smoke tests, rollback, git deploy.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "deployment_manager" / "scripts" / "wp_deploy.py"),
        action])


async def content_auditor(action: str) -> str:
    """Run the content_auditor skill. Use when user asks about
    broken links, orphan pages, thin content, duplicate meta, link structure.
    action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "content_auditor" / "scripts" / "wp_content_audit.py"),
        action])


async def memory_management(action: str) -> str:
    """Run the memory_management skill. Use when user asks about
    memory management. action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "memory_management" / "scripts" / "main.py"),
        action])


async def infrastructure_tools(action: str) -> str:
    """Run the infrastructure_tools skill. Use when user asks about
    infrastructure tools. action: one of list|run|status."""
    return await _run([sys.executable,
        str(SKILLS_DIR / "infrastructure_tools" / "scripts" / "main.py"),
        action])



# ── LiteLLM provider (CommandCenter mode) ────────────────────────────────

def _llm_provider():
    base_url = os.environ.get("LITELLM_BASE_URL", "http://127.0.0.1:8080")
    api_key  = os.environ.get("LITELLM_MASTER_KEY", "sk-local")
    return {
        "type": "openai",
        "base_url": base_url + "/v1",
        "api_key": api_key,
    }


# ── Agent factory ────────────────────────────────────────────────────────

def build_agent():
    from agent_framework_github_copilot import GitHubCopilotAgent
    from copilot.types import PermissionHandler

    return GitHubCopilotAgent(
        name="agent-website-manager",
        description="WordPress website development & management agent — "
                    "Hostinger MCP + WordPress REST API + Elementor",
        instructions=SYSTEM_PROMPT,
        tools=[
            wordpress_management,
            hostinger_management,
            elementor_builder,
            woocommerce_management,
            media_cleanup,
            performance_optimization,
            site_health_monitor,
            security_hardening,
            deployment_manager,
            content_auditor,
            memory_management,
            infrastructure_tools,
        ],
        default_options={
            "model": "tier-balanced",
            "provider": _llm_provider(),
            "mcp_servers": {
                "hostinger": {
                    "command": "npx",
                    "args": ["-y", "@hostinger/mcp-server"],
                    "env": {
                        "HOSTINGER_API_TOKEN": os.environ.get(
                            "HOSTINGER_API_TOKEN", "")
                    }
                }
            },
            "on_permission_request": PermissionHandler.approve_all,
        },
    )


def build_agents():
    """Dynamic Agent Loader entry point.
    Synchronous, zero-argument, pure."""
    return [build_agent()]


__all__ = ["build_agents", "build_agent", "SYSTEM_PROMPT"]
