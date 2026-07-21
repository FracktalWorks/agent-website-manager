"""Use browser-use + DeepSeek V4 Pro — with JSON instruction fix."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', '')

# This ensures response_format works with DeepSeek
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
            f'1. Go to https://fracktal.in/wp-login.php\n'
            f'2. Log in: username="{WP_USER}" password="{WP_PASS}"\n'
            f'3. Go to LiteSpeed Cache dashboard\n'
            f'4. Click "Send Optimization Request" for images\n'
            f'5. Go to Page Optimization settings\n'
            f'6. Turn ON: CSS Minify, CSS Combine, JS Minify, '
            f'JS Combine, HTML Minify. Save.\n'
            f'7. Go to Image Optimization settings\n'
            f'8. Turn ON: WebP Replacement. Save.\n'
            f'9. Purge All cache.\n'
            f'Output your report as JSON.'
            f'{{"steps_completed": [...], "changes_made": [...]}}'
        ),
        llm=llm,
        browser_profile=BrowserProfile(headless=False),
        use_vision=False,
        max_failures=5,
        step_timeout=90,
        # The JSON in the task ensures response_format works
    )

    print('🤖 Chrome opening — DeepSeek V4 Pro will configure LSCache...')
    result = await agent.run()
    print(f'\n✅ {result.final_result()}')


if __name__ == '__main__':
    asyncio.run(main())
