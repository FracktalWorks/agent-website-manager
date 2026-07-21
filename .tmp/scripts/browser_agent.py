"""Browser-use agent with DeepSeek — natural language browser automation.

Usage:
    python .tmp/scripts/browser_agent.py "Purge LiteSpeed cache on fracktal.in"
    python .tmp/scripts/browser_agent.py "Log into GSC and check indexing status"

Requirements:
    DEEPSEEK_API_KEY in .env
    pip install browser-use
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
load_dotenv(Path(__file__).parent.parent.parent / '.env')

DEEPSEEK_KEY = os.getenv('DEEPSEEK_API_KEY', '')

if not DEEPSEEK_KEY:
    print("❌ DEEPSEEK_API_KEY not set in .env")
    print("   Get a key at: https://platform.deepseek.com/api_keys")
    sys.exit(1)


async def run_task(task: str, headless: bool = False):
    """Run a browser task using DeepSeek via browser-use."""
    from browser_use import Agent, BrowserProfile
    from langchain_openai import ChatOpenAI

    # DeepSeek via OpenAI-compatible endpoint
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_KEY,
        base_url="https://api.deepseek.com/v1",
        temperature=0,
    )

    agent = Agent(
        task=task,
        llm=llm,
        browser_profile=BrowserProfile(
            headless=headless,
        ),
    )

    print(f"🤖 Running: {task[:100]}...")
    history = await agent.run()
    result = history.final_result()
    print(f"✅ Done: {result}")
    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python browser_agent.py '<task description>'")
        print("Example: python browser_agent.py 'Purge all LiteSpeed caches'")
        sys.exit(1)

    task = sys.argv[1]
    headless = '--headless' in sys.argv
    asyncio.run(run_task(task, headless=headless))
