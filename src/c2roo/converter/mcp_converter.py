from pathlib import Path

from c2roo.models.mcp import McpServer


def _resolve_plugin_root(value: str, install_path: Path) -> str:
    """Replace ${CLAUDE_PLUGIN_ROOT} with the actual install path."""
    return value.replace("${CLAUDE_PLUGIN_ROOT}", str(install_path))


def convert_mcp(servers: dict[str, McpServer], install_path: Path) -> dict[str, dict[str, object]]:
    """Convert McpServer IRs to a Roo mcp.json-compatible dict."""
    if not servers:
        return {}

    result: dict[str, dict[str, object]] = {}
    for name, server in servers.items():
        entry: dict[str, object] = {}

        if server.command:
            entry["command"] = _resolve_plugin_root(server.command, install_path)
        if server.args:
            entry["args"] = [_resolve_plugin_root(a, install_path) for a in server.args]
        if server.env:
            entry["env"] = {k: _resolve_plugin_root(v, install_path) for k, v in server.env.items()}
        if server.url:
            entry["url"] = server.url
        if server.headers:
            entry["headers"] = server.headers
        if server.disabled:
            entry["disabled"] = True
        if server.always_allow:
            entry["alwaysAllow"] = server.always_allow
        if server.timeout:
            entry["timeout"] = server.timeout

        result[name] = entry

    return result
