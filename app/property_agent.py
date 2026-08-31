from pathlib import Path

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types
from pydantic import BaseModel, Field

from app.property_tools import book_viewing_tool

MODEL = "gemini-3.7-flash"

# Load ONLY the live-property-search skill for this specialist agent
_SKILLS_DIR = Path(__file__).parent / "skills" / "live-property-search"
_LIVE_SEARCH_SKILL = load_skill_from_dir(str(_SKILLS_DIR))


class PropertyListingDetail(BaseModel):
    name: str = Field(description="Listing title or apartment complex name")
    url: str = Field(
        description="Exact, verbatim verified permalink URL directly from web search"
    )
    monthly_rent_yen: int = Field(description="Monthly rent amount in JPY")
    layout: str = Field(description="Floor layout, e.g. '1LDK', '2BR'")
    floor: int | None = Field(
        default=None, description="Floor number of the rental unit if known"
    )
    key_features: list[str] = Field(
        description="Verified amenities (e.g. separate bath/toilet, auto-lock, balcony)"
    )


class PropertySearchOutput(BaseModel):
    recommended_properties: list[PropertyListingDetail] = Field(
        description="List of verified vacant listings matching user criteria"
    )
    total_candidates_inspected: int = Field(
        description="Total number of search results inspected"
    )
    dislikes_excluded: list[str] = Field(
        description="Negative criteria strictly filtered out (e.g. ground floor, unit bath)"
    )
    search_summary: str = Field(
        description="Executive summary of the live rental search results"
    )
    recovery_guidance: str | None = Field(
        default=None,
        description="Recovery instructions if no listings satisfied the strict criteria",
    )


PROPERTY_AGENT_INSTRUCTION = """\
You are an expert Real Estate & Rental Property Agent specialist.
Your mission is to perform REAL-TIME LIVE WEB SEARCHES to discover active vacant rental listings matching user criteria and coordinate property viewing appointments using the embedded `live-property-search` skill.

## Step-by-Step Task Workflow & Guided Recovery:

1. **Perform Targeted Web Search (`google_search`)**:
   - Search real estate portals and listing databases for specific vacancies in the target area/neighborhood.
   - Formulate targeted queries (e.g. `'site:suumo.jp/chintai/ "Meguro" "1LDK"'`, `'site:zillow.com "Brooklyn" "1 bedroom" rent'`).

2. **Verify Real Property Page via `load_web_page` (MANDATORY)**:
   - For candidate listing URLs discovered in `google_search`, **you MUST invoke `load_web_page(url=...)` with the exact URL**.
   - Inspect the actual page content to verify:
     - Specific property details: rent, floor, layout, building structure (RC vs Wood), and current vacancy status.
     - **Strictly enforce negative feedback filters (dislikes)**:
       - Discard ground-floor units if `first_floor` is disliked.
       - Discard 3-point unit baths if `unit_bath` is disliked.
       - Discard wooden structures if `wood_structure` is disliked.

3. **Strict Grounding & Verbatim URL Preservation (CRITICAL)**:
   - **DO NOT hallucinate, guess, shorten, or alter URLs under any circumstances.**
   - **Copy-paste the exact, raw URL string retrieved from `google_search` / `load_web_page` verbatim.**
   - Ensure the link directly points to the actual property or search listing you inspected, not a generic fabricated path.

4. **Viewing Appointment Scheduling (`book_viewing_tool`)**:
   - When the user selects a verified property and wants to book an in-person viewing, invoke `book_viewing_tool` with the verified property ID/URL, preferred date/time, and applicant details.
   - **Guided Error Recovery**: If `book_viewing_tool` returns an error (e.g., missing contact info), ask the user for the missing fields before retrying.
"""

property_agent = Agent(
    name="property_agent",
    mode="task",
    output_schema=PropertySearchOutput,
    description=(
        "Performs live web searches on real estate portals, verifies specific listing pages with load_web_page, "
        "and provides grounded, verbatim property listing URLs."
    ),
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=PROPERTY_AGENT_INSTRUCTION,
    tools=[
        GoogleSearchTool(),
        load_web_page,
        book_viewing_tool,
        SkillToolset(skills=[_LIVE_SEARCH_SKILL]),
    ],
)
