"""Use browser-use + Gemini Flash to configure LSCache."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', '')

from browser_use import Agent, BrowserProfile
from browser_use.llm.litellm import ChatLiteLLM

WP_USER = os.getenv('WORDPRESS_USERNAME', 'vjvarada')
WP_PASS = os.getenv('WORDPRESS_APP_PASSWORD', '')


async def main():
    llm = ChatLiteLLM(model='gemini/gemini-2.5-flash')

    agent = Agent(
        task=(
            f'Navigate to https://fracktal.in/wp-login.php. '
            f'Log in with username "{WP_USER}" and password '
            f'"{WP_PASS}". After login, go to the LiteSpeed Cache '
            f'dashboard. '
            f'Click "Send Optimization Request" for images. '
            f'Then go to Page Optimization settings. '
            f'Turn ON: CSS Minify, CSS Combine, JS Minify, '
            f'JS Combine, HTML Minify. Save. '
            f'Then find Image Optimization settings and enable '
            f'WebP Replacement. Save. '
            f'Finally purge all cache. '
            f'Tell me what was changed.'
        ),
        llm=llm,
        browser_profile=BrowserProfile(headless=False),
        use_vision=False,
        max_failures=5,
        step_timeout=90,
    )

    print('🤖 Opening Chrome...')
    result = await agent.run()
    print(f'\n✅ {result.final_result()}')


if __name__ == '__main__':
    asyncio.run(main())
