from pathlib import Path
from c2roo.models.mcp import McpServer
from c2roo.converter.mcp_converter import convert_mcp


def test_convert_mcp_servers():
    servers = {
        "my-server": McpServer(name="my-server", command="npx", args=["-y", "@org/server"], env={"KEY": "val"}),
        "remote": McpServer(name="remote", url="http://localhost:3000/sse", headers={"Authorization": "Bearer tok"}),
    }
    result = convert_mcp(servers, Path("/home/user/.roo"))
    assert "my-server" in result
    assert result["my-server"]["command"] == "npx"
    assert "remote" in result
    assert result["remote"]["url"] == "http://localhost:3000/sse"


def test_convert_mcp_resolves_plugin_root():
    servers = {
        "lint": McpServer(name="lint", command="python3",
            args=["${CLAUDE_PLUGIN_ROOT}/scripts/lint.py"],
            env={"CONFIG": "${CLAUDE_PLUGIN_ROOT}/config.json"}),
    }
    result = convert_mcp(servers, Path("/home/user/.roo"))
    assert "${CLAUDE_PLUGIN_ROOT}" not in str(result["lint"]["args"])
    assert "${CLAUDE_PLUGIN_ROOT}" not in str(result["lint"]["env"])


def test_convert_empty_mcp():
    result = convert_mcp({}, Path("/tmp"))
    assert result == {}
