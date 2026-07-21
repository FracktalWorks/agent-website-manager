"""browser-use + DeepSeek V4 Pro — patched for response_format."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', '')

# ── DeepSeek V4 Pro compatibility ──
import sys
sys.path.insert(0, '.tmp/scripts')
from deepseek_browser import configure
configure()
# ───────────────────────────────────

from browser_use import Agent, BrowserProfile
from browser_use.llm.litellm import ChatLiteLLM

WP_USER = os.getenv('WORDPRESS_USERNAME', 'vjvarada')
WP_PASS = os.getenv('WORDPRESS_APP_PASSWORD', '')


async def main():
    llm = ChatLiteLLM(
        model='openai/deepseek-v4-pro',
        api_base='https://api.deepseek.com/v1',
        api_key=os.getenv('DEEPSEEK_API_KEY'),
    )

    agent = Agent(
        task=(
            f'Go to https://fracktal.in/wp-login.php. '
            f'Log in with user="{WP_USER}" pass="{WP_PASS}". '
            f'Go to LiteSpeed dashboard. '
            f'Click "Send Optimization Request" for images. '
            f'Go to Page Optimization. Turn ON: '
            f'CSS Minify, CSS Combine, JS Minify, JS Combine, '
            f'HTML Minify. Save. '
            f'Go to Image Optimization, enable WebP Replacement. Save. '
            f'Purge All cache. '
            f'Report what was changed in JSON format.'
        ),
        llm=llm,
        browser_profile=BrowserProfile(headless=False),
        use_vision=False,
        max_failures=5,
        step_timeout=90,
    )

    print('🤖 DeepSeek V4 Pro configuring LSCache...')
    result = await agent.run()
    print(f'\n✅ {result.final_result()}')


if __name__ == '__main__':
    asyncio.run(main())
