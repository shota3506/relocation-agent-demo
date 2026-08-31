from pathlib import Path

from google.adk.skills import load_skill_from_dir
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.skill_toolset import SkillToolset

from app.agent import root_agent
from app.area_researcher import AreaResearchOutput, area_researcher
from app.cost_estimator import CostEstimationOutput, cost_estimator
from app.property_agent import PropertySearchOutput, property_agent
from app.property_tools import (
    book_viewing_tool,
    estimate_upfront_costs,
)


def test_agent_subagent_delegation_structure():
    """Verify that root_agent delegates tasks to 3 specialized sub-agents."""
    assert root_agent.name == "root_agent"
    assert len(root_agent.sub_agents) == 3
    sub_names = [sa.name for sa in root_agent.sub_agents]
    assert "area_researcher" in sub_names
    assert "property_agent" in sub_names
    assert "cost_estimator" in sub_names


def test_strategic_model_routing_across_agents():
    """Verify task-appropriate strategic model routing across the agent hierarchy."""
    # Root coordinator: Flagship 3.7-flash model for multi-agent synthesis & planning
    assert root_agent.model.model == "gemini-3.7-flash"
    # Specialist sub-agents: Flash models tailored for MCP, web scraping, and math
    assert area_researcher.model.model == "gemini-3.7-flash"
    assert property_agent.model.model == "gemini-3.7-flash"
    assert cost_estimator.model.model == "gemini-3.5-flash"


def test_area_researcher_subagent_configuration():
    """Verify area_researcher has strict output_schema, gemini-3.7-flash, and ONLY area-due-diligence skill."""
    assert area_researcher.name == "area_researcher"
    assert area_researcher.mode == "task"
    assert area_researcher.output_schema == AreaResearchOutput
    assert area_researcher.model.model == "gemini-3.7-flash"

    # Verify McpToolset and SkillToolset are attached
    assert any(isinstance(t, McpToolset) for t in area_researcher.tools)
    skill_toolsets = [t for t in area_researcher.tools if isinstance(t, SkillToolset)]
    assert len(skill_toolsets) == 1
    # Check that it only has 1 skill (area-due-diligence)
    assert len(skill_toolsets[0].skills) == 1
    assert skill_toolsets[0].skills[0].name == "area-due-diligence"


def test_property_agent_subagent_configuration():
    """Verify property_agent has strict output_schema, gemini-3.7-flash, search tools, and live-property-search skill."""
    assert property_agent.name == "property_agent"
    assert property_agent.mode == "task"
    assert property_agent.output_schema == PropertySearchOutput
    assert property_agent.model.model == "gemini-3.7-flash"

    # Verify real web search tools and dedicated skill are attached
    assert any(isinstance(t, GoogleSearchTool) for t in property_agent.tools)
    assert load_web_page in property_agent.tools
    assert book_viewing_tool in property_agent.tools

    skill_toolsets = [t for t in property_agent.tools if isinstance(t, SkillToolset)]
    assert len(skill_toolsets) == 1
    assert len(skill_toolsets[0].skills) == 1
    assert skill_toolsets[0].skills[0].name == "live-property-search"


def test_cost_estimator_subagent_configuration():
    """Verify cost_estimator has strict output_schema, lightweight gemini-3.5-flash, and ONLY moving-cost-estimator skill."""
    assert cost_estimator.name == "cost_estimator"
    assert cost_estimator.mode == "task"
    assert cost_estimator.output_schema == CostEstimationOutput
    assert cost_estimator.model.model == "gemini-3.5-flash"

    # Verify estimation tool and dedicated skill
    assert estimate_upfront_costs in cost_estimator.tools
    skill_toolsets = [t for t in cost_estimator.tools if isinstance(t, SkillToolset)]
    assert len(skill_toolsets) == 1
    assert len(skill_toolsets[0].skills) == 1
    assert skill_toolsets[0].skills[0].name == "moving-cost-estimator"


def test_skills_loading_for_all_agents():
    """Verify that all skills in app/skills/ are valid and loadable."""
    skills_base = Path(__file__).parent.parent.parent / "app" / "skills"

    area_skill = load_skill_from_dir(str(skills_base / "area-due-diligence"))
    assert area_skill.frontmatter.name == "area-due-diligence"

    search_skill = load_skill_from_dir(str(skills_base / "live-property-search"))
    assert search_skill.frontmatter.name == "live-property-search"

    cost_skill = load_skill_from_dir(str(skills_base / "moving-cost-estimator"))
    assert cost_skill.frontmatter.name == "moving-cost-estimator"
