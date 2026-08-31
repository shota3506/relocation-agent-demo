from pathlib import Path

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types
from pydantic import BaseModel, Field

from app.maps_tools import get_maps_mcp_toolset

MODEL = "gemini-3.7-flash"

# Load Skill instance from app/skills/area-due-diligence
_SKILLS_DIR = Path(__file__).parent / "skills" / "area-due-diligence"
_AREA_SKILL = load_skill_from_dir(str(_SKILLS_DIR))


class CommuteRouteDetail(BaseModel):
    destination: str = Field(
        description="Workplace or target destination (e.g. Shibuya Station)"
    )
    transit_duration_minutes: int = Field(description="Commute duration in minutes")
    route_summary: str = Field(
        description="Transit lines, transfers, or route overview"
    )


class NeighborhoodDueDiligence(BaseModel):
    neighborhood_name: str = Field(
        description="Name of the candidate neighborhood or station (e.g. Meguro)"
    )
    commute_details: list[CommuteRouteDetail] = Field(
        description="Commute durations to each workplace"
    )
    nearby_amenities: list[str] = Field(
        description="Supermarkets, parks, clinics within walking distance"
    )
    suitability_verdict: str = Field(
        description="Assessment of commute equity and neighborhood livability"
    )


class AreaResearchOutput(BaseModel):
    evaluated_neighborhoods: list[NeighborhoodDueDiligence] = Field(
        description="Evaluated candidate neighborhoods"
    )
    summary_recommendation: str = Field(
        description="Overall recommendation for the user/concierge"
    )
    recovery_guidance: str | None = Field(
        default=None,
        description="Actionable recovery advice if routes could not be calculated",
    )


AREA_RESEARCHER_INSTRUCTION = """\
You are an expert Area Researcher specializing in neighborhood research and geospatial due diligence.
Your role is to perform objective geospatial analysis across any target city, region, or neighborhood using Google Maps MCP tools guided by your embedded SkillToolset.

## Responsibilities & Guided Recovery Workflow:

1. **Commute Route Analysis**:
   - Use `compute_routes` to calculate transit/driving travel durations and distances from candidate neighborhoods to the user's workplaces or schools.
   - For multiple household members with different destinations, evaluate commute fairness.
   - **Guided Error Recovery**: If a destination cannot be resolved, use `resolve_names` or try canonical station names (e.g. 'Shibuya Station' instead of a generic company name).

2. **Neighborhood Amenity Discovery**:
   - Use `search_places` to identify supermarkets, grocery stores, parks, childcare centers, and clinics within walking distance of candidate areas.
   - Use `resolve_names` to resolve location/station/neighborhood queries to canonical Place IDs.
"""

area_researcher = Agent(
    name="area_researcher",
    mode="task",
    output_schema=AreaResearchOutput,
    description=(
        "Evaluates neighborhoods across any target city or region, calculates commute routes/durations to workplaces, "
        "and discovers nearby amenities (supermarkets, parks, clinics) using Google Maps MCP tools and domain skills."
    ),
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AREA_RESEARCHER_INSTRUCTION,
    tools=[
        get_maps_mcp_toolset(),
        SkillToolset(skills=[_AREA_SKILL]),
    ],
)
