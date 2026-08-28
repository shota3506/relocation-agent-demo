import os

from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

# Official Google Maps Grounding Lite MCP tools
# Ref: https://developers.google.com/maps/ai/grounding-lite/reference/mcp
EXPOSED_MAPS_TOOLS = [
    "search_places",  # Find amenities, businesses, supermarkets, parks, clinics
    "compute_routes",  # Calculate commute routes and travel durations
    "resolve_names",  # Resolve free-form location queries into canonical Google Maps Place IDs
]


def get_maps_mcp_toolset() -> McpToolset:
    """Creates an MCP Toolset connected to the official Google Maps Grounding Lite MCP service."""
    api_key = os.environ.get("GOOGLE_MAPS_GROUNDING_LITE_API_KEY") or os.environ.get(
        "GOOGLE_MAPS_API_KEY", ""
    )
    headers = {"X-Goog-Api-Key": api_key} if api_key else {}

    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://mapstools.googleapis.com/mcp",
            headers=headers,
        ),
        tool_filter=EXPOSED_MAPS_TOOLS,
    )
