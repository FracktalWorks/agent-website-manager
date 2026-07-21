"""Use browser-use + DeepSeek to configure LSCache."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', '')

from browser_use import Agent, BrowserProfile
from browser_use.llm.litellm import ChatLiteLLM

WP_USER = os.getenv('WORDPRESS_USERNAME', 'vjvarada')
WP_PASS = os.getenv('WORDPRESS_APP_PASSWORD', '')


async def main():
    llm = ChatLiteLLM(model='deepseek/deepseek-chat')

    agent = Agent(
        task=(
            f'1. Go to https://fracktal.in/wp-login.php\n'
            f'2. Log in with username "{WP_USER}" and password '
            f'"{WP_PASS}"\n'
            f'3. After login, go to LiteSpeed Cache dashboard at '
            f'admin.php?page=litespeed\n'
            f'4. Click "Send Optimization Request" to resume '
            f'processing 799 pending images\n'
            f'5. Navigate to Page Optimization settings\n'
            f'6. Turn ON: CSS Minify, CSS Combine, JS Minify, '
            f'JS Combine, HTML Minify\n'
            f'7. Navigate to Image Optimization settings\n'
            f'8. Turn ON WebP Replacement\n'
            f'9. Purge All cache\n'
            f'Report what was changed.'
        ),
        llm=llm,
        browser_profile=BrowserProfile(headless=False),
        use_vision=False,
        max_failures=5,
        step_timeout=60,
    )

    print('Opening Chrome - watch it configure LSCache!')
    result = await agent.run()
    print(f'Done: {result.final_result()}')


if __name__ == '__main__':
    asyncio.run(main())
