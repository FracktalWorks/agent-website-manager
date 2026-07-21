"""Use browser-use + DeepSeek to configure LSCache for optimal performance."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', '')

from browser_use import Agent, BrowserProfile
from browser_use.llm.litellm import ChatLiteLLM


async def main():
    llm = ChatLiteLLM(model='deepseek/deepseek-chat')

    agent = Agent(
        task=(
            'You are logged into WordPress admin at fracktal.in. '
            'Do the following to optimize site performance:\n'
            '1. Go to https://fracktal.in/wp-admin/admin.php?page=litespeed\n'
            '2. Look for "Send Optimization Request" under Image Optimization '
            'Summary and click it to process pending images\n'
            '3. Then navigate to Page Optimization settings (look in the '
            'LiteSpeed Cache sidebar menu for "Page Optimization")\n'
            '4. Under CSS Settings, enable: CSS Minify, CSS Combine\n'
            '5. Under JS Settings, enable: JS Minify, JS Combine\n'
            '6. Under HTML Settings, enable: HTML Minify\n'
            '7. Under Image Optimization settings, find and enable '
            'WebP Replacement or "Image WebP Replacement"\n'
            '8. Finally, click "Purge All" cache\n'
            'Report back what settings you changed.'
        ),
        llm=llm,
        browser_profile=BrowserProfile(headless=False),
        use_vision=True,
        max_failures=3,
        step_timeout=60,
    )

    print('🤖 Starting LSCache optimization...')
    print('   A Chrome window will open — watch it work!')
    result = await agent.run()
    print('\n✅ Done!')
    print(f'Result: {result.final_result()}')


if __name__ == '__main__':
    asyncio.run(main())
