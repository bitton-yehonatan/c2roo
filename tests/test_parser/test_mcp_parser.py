from pathlib import Path

from c2roo.parser.mcp_parser import parse_mcp

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_mcp():
    mcp_json = FIXTURES / ".mcp.json"
    servers = parse_mcp(mcp_json)

    assert "my-server" in servers
    assert servers["my-server"].command == "npx"
    assert servers["my-server"].args == ["-y", "@org/mcp-server"]
    assert servers["my-server"].env == {"API_KEY": "test-key"}

    assert "remote-server" in servers
    assert servers["remote-server"].url == "http://localhost:3000/sse"
    assert servers["remote-server"].command is None


def test_parse_mcp_missing_file():
    missing = Path("/nonexistent/.mcp.json")
    servers = parse_mcp(missing)
    assert servers == {}
