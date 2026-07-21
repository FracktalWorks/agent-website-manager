"""Use browser-use + DeepSeek to configure LSCache."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', '')

# Fix for DeepSeek: drop unsupported params
import litellm
litellm.drop_params = True

from browser_use import Agent, BrowserProfile
from browser_use.llm.litellm import ChatLiteLLM

WP_USER = os.getenv('WORDPRESS_USERNAME', 'vjvarada')
WP_PASS = os.getenv('WORDPRESS_APP_PASSWORD', '')


async def main():
    llm = ChatLiteLLM(
        model='openai/deepseek-chat',
        api_base='https://api.deepseek.com/v1',
        api_key=os.getenv('DEEPSEEK_API_KEY'),
    )

    agent = Agent(
        task=(
            f'Navigate to https://fracktal.in/wp-login.php. '
            f'Log in with username "{WP_USER}" and password '
            f'"{WP_PASS}". After login, go to the LiteSpeed Cache '
            f'dashboard (admin.php?page=litespeed). '
            f'Click "Send Optimization Request" for images. '
            f'Then go to Page Optimization settings via the sidebar. '
            f'Turn ON: CSS Minify, CSS Combine, JS Minify, '
            f'JS Combine, HTML Minify. Save settings. '
            f'Then go to Image Optimization settings and enable '
            f'WebP Replacement. Save. '
            f'Finally purge all cache. '
            f'Report a summary of what was changed.'
        ),
        llm=llm,
        browser_profile=BrowserProfile(headless=False),
        use_vision=False,
        max_failures=5,
        step_timeout=90,
    )

    print('🤖 Opening Chrome — it will log in and configure LSCache...')
    result = await agent.run()
    print(f'\n✅ {result.final_result()}')


if __name__ == '__main__':
    asyncio.run(main())
