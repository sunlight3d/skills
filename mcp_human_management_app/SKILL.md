---
name: mcp_human_management_app
description: MCP server configuration for Human Management Web Application (Stitch API Integration).
---

# MCP Human Management App

This skill provides the MCP server configuration for connecting to the Human Management Web Application via the Stitch MCP endpoint.

## Configuration (`mcp_config.json`)

```json
{
  "mcpServers": {
    "mcp_human_management_app": {
      "serverUrl": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "${STITCH_API_KEY}"
      }
    }
  }
}
```

## Setup Instructions

To enable this MCP server globally in Antigravity:
1. Copy the configuration above to `~/.gemini/config/mcp_config.json`.
2. Replace `${STITCH_API_KEY}` with your actual Stitch API key.
