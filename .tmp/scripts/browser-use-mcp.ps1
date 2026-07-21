# ⚠️ DEPRECATED (2026-07-04): browser-use MCP removed in favor of Playwright MCP with Chrome.
# This script is kept for reference only. Use Playwright MCP tools instead.
# Wrapper for browser-use MCP server with DeepSeek
$env:OPENAI_API_KEY = "sk-a40a5330c1494ffe9ca9b31b4294d593"
$env:OPENAI_API_BASE = "https://api.deepseek.com/v1"
$env:BROWSER_USE_HEADLESS = "false"
uvx --from "browser-use[cli]" browser-use --mcp
