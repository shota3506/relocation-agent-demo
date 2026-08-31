import pytest
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from app.agent import (
    after_agent_callback,
    app,
    before_agent_callback,
    root_agent,
)


def test_app_events_compaction_configuration():
    """Verify that EventsCompactionConfig is configured with token threshold and retention size."""
    config = app.events_compaction_config
    assert isinstance(config, EventsCompactionConfig)
    assert config.token_threshold == 32000
    assert config.event_retention_size == 5
    assert isinstance(config.summarizer, LlmEventSummarizer)


def test_app_context_cache_configuration():
    """Verify that ContextCacheConfig is configured for prompt caching."""
    cache_config = app.context_cache_config
    assert isinstance(cache_config, ContextCacheConfig)
    assert cache_config.min_tokens == 2048
    assert cache_config.ttl_seconds == 1800


def test_root_agent_preload_memory_tool():
    """Verify that PreloadMemoryTool is attached to root_agent."""
    assert any(isinstance(t, PreloadMemoryTool) for t in root_agent.tools)


@pytest.mark.asyncio
async def test_before_agent_callback_state_initialization():
    """Verify that before_agent_callback initializes required user:* keys."""

    class DummyContext:
        def __init__(self):
            self.state = {}

    ctx = DummyContext()
    await before_agent_callback(ctx)

    assert "user:family_structure" in ctx.state
    assert "user:workplace" in ctx.state
    assert "user:lifestyle_priorities" in ctx.state
    assert ctx.state["user:lifestyle_priorities"] == []
    assert "user:dislikes" in ctx.state
    assert ctx.state["user:dislikes"] == []
    assert "user:viewing_history" in ctx.state
    assert ctx.state["user:viewing_history"] == []


@pytest.mark.asyncio
async def test_after_agent_callback_asynchronous_memory():
    """Verify that after_agent_callback triggers add_session_to_memory."""
    called = False

    class DummyContext:
        def __init__(self):
            self.state = {}

        async def add_session_to_memory(self):
            nonlocal called
            called = True

    ctx = DummyContext()
    res = await after_agent_callback(ctx)
    assert res is None
    assert called is True
