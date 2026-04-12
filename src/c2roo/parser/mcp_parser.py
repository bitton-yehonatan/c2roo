import json
from pathlib import Path

from c2roo.models.mcp import McpServer


def parse_mcp(mcp_json_path: Path) -> dict[str, McpServer]:
    """Parse .mcp.json into a dict of McpServer IRs."""
    if not mcp_json_path.exists():
        return {}

    data = json.loads(mcp_json_path.read_text(encoding="utf-8"))
    servers = {}

    for name, config in data.get("mcpServers", {}).items():
        servers[name] = McpServer(
            name=name,
            command=config.get("command"),
            args=config.get("args", []),
            env=config.get("env", {}),
            url=config.get("url"),
            headers=config.get("headers", {}),
            disabled=config.get("disabled", False),
            always_allow=config.get("alwaysAllow", []),
            timeout=config.get("timeout"),
        )

    return servers
