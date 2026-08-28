from app.maps_tools import EXPOSED_MAPS_TOOLS, get_maps_mcp_toolset


def test_get_maps_mcp_toolset_official_grounding_lite_configuration():
    """Verify that Google Maps MCP Toolset connects to official Google Maps Grounding Lite endpoint."""
    toolset = get_maps_mcp_toolset()
    assert hasattr(toolset, "connection_params")

    # Verify StreamableHTTP connection parameters
    conn_params = toolset.connection_params
    assert conn_params.url == "https://mapstools.googleapis.com/mcp"

    # Verify explicitly exposed official Grounding Lite tools (weather excluded)
    assert toolset.tool_filter == EXPOSED_MAPS_TOOLS
    assert "search_places" in EXPOSED_MAPS_TOOLS
    assert "compute_routes" in EXPOSED_MAPS_TOOLS
    assert "resolve_names" in EXPOSED_MAPS_TOOLS
    assert "lookup_weather" not in EXPOSED_MAPS_TOOLS
