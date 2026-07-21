"""DeepSeek V4 Pro compatibility for browser-use.

Usage:
    from deepseek_browser import configure
    configure()
    # Now browser-use works with DeepSeek V4 Pro

Strips response_format from all DeepSeek LLM calls (sync + async).
"""

import litellm

_original_completion = litellm.completion
_original_acompletion = litellm.acompletion
_patched = False


def _strip_rf(kwargs):
    """Strip response_format for DeepSeek models."""
    model = str(kwargs.get('model', ''))
    if 'deepseek' in model.lower():
        kwargs.pop('response_format', None)
        kwargs.pop('response_schema', None)


def configure():
    """Patch litellm to strip response_format for DeepSeek models."""
    global _patched
    if _patched:
        return

    def patched_completion(*args, **kwargs):
        _strip_rf(kwargs)
        return _original_completion(*args, **kwargs)

    async def patched_acompletion(*args, **kwargs):
        _strip_rf(kwargs)
        return await _original_acompletion(*args, **kwargs)

    litellm.completion = patched_completion
    litellm.acompletion = patched_acompletion
    _patched = True
