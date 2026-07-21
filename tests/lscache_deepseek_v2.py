"""browser-use + DeepSeek V4 Pro — with response_format stripped via callback."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', '')

import litellm
import litellm.litellm_core_utils.litellm_logging as logging_module

# Strip response_format from all DeepSeek calls
_original_log = logging_module.Logging

def strip_deepseek_rf(kwargs, completion_response, start_time, end_time):
    """Pre-call hook: strip response_format for DeepSeek models."""
    model = kwargs.get('model', '')
    if 'deepseek' in str(model).lower():
        kwargs.pop('response_format', None)
        kwargs.pop('response_schema', None)

# Register as success callback (runs before call)
litellm.success_callback = [strip_deepseek_rf]
litellm.pre_call_rules = []

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
            f'Go to https://fracktal.in/wp-login.php. '
            f'Log in: user="{WP_USER}" pass="{WP_PASS}". '
            f'Go to LiteSpeed dashboard. '
            f'Click Send Optimization Request for images. '
            f'Go to Page Optimization settings. '
            f'Turn ON: CSS Minify, CSS Combine, JS Minify, '
            f'JS Combine, HTML Minify. Save. '
            f'Go to Image Optimization, enable WebP Replacement. Save. '
            f'Purge All cache. '
            f'Report as JSON what was changed.'
        ),
        llm=llm,
        browser_profile=BrowserProfile(headless=False),
        use_vision=False,
        max_failures=5,
        step_timeout=90,
    )

    print('🤖 Chrome opening with DeepSeek V4 Pro...')
    result = await agent.run()
    print(f'\n✅ {result.final_result()}')


if __name__ == '__main__':
    asyncio.run(main())
