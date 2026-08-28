from pathlib import Path

from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.skill_toolset import SkillToolset

from app.agent import root_agent
from app.area_researcher import area_researcher


def test_agent_subagent_delegation_structure():
    """Verify that root_agent delegates geospatial tasks to area_researcher sub-agent."""
    assert root_agent.name == "root_agent"
    assert len(root_agent.sub_agents) == 1
    assert root_agent.sub_agents[0].name == "area_researcher"


def test_area_researcher_subagent_configuration():
    """Verify area_researcher sub-agent configuration, McpToolset, and SkillToolset."""
    assert area_researcher.name == "area_researcher"
    assert area_researcher.mode == "task"

    # Verify McpToolset and SkillToolset are attached
    assert any(isinstance(t, McpToolset) for t in area_researcher.tools)
    assert any(isinstance(t, SkillToolset) for t in area_researcher.tools)


def test_area_researcher_adk_skill_loading():
    """Verify that area_researcher loads skill via ADK load_skill_from_dir from app/skills/."""
    skill_dir = (
        Path(__file__).parent.parent.parent / "app" / "skills" / "area-due-diligence"
    )
    skill = load_skill_from_dir(str(skill_dir))

    assert skill.frontmatter.name == "area-due-diligence"
    assert len(skill.instructions) > 50
    assert "compute_routes" in skill.instructions
    assert "search_places" in skill.instructions
