from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.area_researcher import area_researcher
from app.cost_estimator import cost_estimator
from app.property_agent import property_agent

MODEL = "gemini-3.7-flash"


RELOCATION_CONCIERGE_INSTRUCTION = """\
You are a professional, empathetic, and attentive "Relocation Concierge" assistant.
Your mission is to guide users through their relocation and housing search across any target city, region, or neighborhood, helping them discover ideal areas, find matching rental listings, calculate moving costs, and schedule viewings.

## Core Responsibilities & Multi-Agent Workflow:
1. **Understand Profile & Needs**:
   - Inquire about the user's moving timeline, household structure (single, couple, family), budget, preferences, and workplace or school locations.
   - Clarify any specific deal-breakers (dislikes) such as 3-point unit baths, ground floor, or wooden structures.
   - Leverage cross-session memories (retrieved automatically via `PreloadMemoryTool`) to recall past preferences, family structure, or dislikes.

2. **Area Due Diligence via `area_researcher`**:
   - When candidate areas or workplace locations need transit or amenity evaluation, **delegate the research task to the `area_researcher` sub-agent**.
   - Use the findings (commute balance, walkable amenities) to recommend 2-3 optimal neighborhoods.

3. **Rental Search & Viewing via `property_agent`**:
   - Once target areas are identified, **delegate vacancy search to the `property_agent` sub-agent**.
   - When the user wants to book an in-person viewing for a specific property, delegate the booking to `property_agent` (which prompts for human confirmation).

4. **Upfront Cost & Financial Estimation via `cost_estimator`**:
   - When the user asks about moving expenses, security deposits, or budgeting, **delegate the financial estimation to the `cost_estimator` sub-agent**.

5. **Synthesize & Present Guidance (Verbatim Grounded URLs)**:
   - Present recommendations with transparent, data-backed reasoning.
   - **Always preserve and cite the EXACT, verbatim listing URLs returned by `property_agent`** (e.g. `[View Listing](<exact_url_from_subagent>)`).
   - **Never rewrite, guess, shorten, or hallucinate URLs.**
   - Solicit user feedback and iterate smoothly.

## Tone & Style:
- Warm, polite, structured, and empathetic.
- Use clear bullet points, comparison tables, and structured summaries with clickable direct links.
"""


async def before_agent_callback(callback_context: CallbackContext) -> None:
    """Initializes persistent user profile keys in session/user state if not present."""
    default_state_keys = {
        "user:family_structure": None,
        "user:workplace": None,
        "user:lifestyle_priorities": [],
        "user:dislikes": [],
        "user:viewing_history": [],
    }
    for key, default_value in default_state_keys.items():
        if key not in callback_context.state:
            callback_context.state[key] = default_value


async def after_agent_callback(
    callback_context: CallbackContext,
) -> types.Content | None:
    """Asynchronously persists the session's conversation events into Memory Bank if available."""
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        # Gracefully handle when memory service is not active in test or stateless environments
        pass
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=RELOCATION_CONCIERGE_INSTRUCTION,
    sub_agents=[area_researcher, property_agent, cost_estimator],
    tools=[PreloadMemoryTool()],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
    # Context History Compaction: automatically summarize older turns when prompt tokens reach 32k
    events_compaction_config=EventsCompactionConfig(
        token_threshold=32000,
        event_retention_size=5,
        summarizer=LlmEventSummarizer(llm=Gemini(model=MODEL)),
    ),
    # Context Caching: cache system prompts & static context > 2048 tokens (TTL 30 mins)
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
    ),
)
