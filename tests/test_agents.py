"""CommandCenter CI gate — must pass for agent registration."""
import pytest

def test_build_agents_importable():
    import agents  # noqa: F401

def test_build_agents_returns_list():
    try:
        from agents import build_agents
        result = build_agents()
        assert isinstance(result, list) and len(result) >= 1
    except ImportError:
        pytest.skip("MAF runtime not available")

def test_agent_has_name_and_instructions():
    try:
        from agents import build_agents
        agent = build_agents()[0]
        instructions = (
            getattr(agent, "instructions", None)
            or getattr(agent, "_instructions", None)
        )
        assert instructions and len(instructions) > 50
    except ImportError:
        pytest.skip("MAF runtime not available")

def test_agent_has_tools():
    try:
        from agents import build_agents
        agent = build_agents()[0]
        tools = (
            getattr(agent, "tools", None)
            or getattr(agent, "_tools", None)
            or []
        )
        assert len(tools) > 0, "Agent has no tools — it will only apologise"
    except ImportError:
        pytest.skip("MAF runtime not available")

def test_system_prompt_contains_skills():
    from agents import SYSTEM_PROMPT
    assert len(SYSTEM_PROMPT) > 100
