from pathlib import Path

from c2roo.parser.plugin_parser import parse_plugin

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_full_plugin():
    plugin = parse_plugin(FIXTURES)

    assert plugin.metadata.name == "sample-plugin"
    assert plugin.metadata.version == "1.0.0"
    assert plugin.metadata.author == "Test Author"

    assert len(plugin.skills) == 1
    assert plugin.skills[0].name == "pdf-processing"

    assert len(plugin.commands) == 1
    assert plugin.commands[0].name == "commit"

    assert len(plugin.agents) == 1
    assert plugin.agents[0].name == "code-reviewer"

    assert len(plugin.hooks) == 2

    assert len(plugin.mcp_servers) == 2


def test_parse_plugin_missing_manifest():
    try:
        parse_plugin(Path("/nonexistent"))
        assert False, "Should have raised"
    except FileNotFoundError as e:
        assert "plugin.json" in str(e)
