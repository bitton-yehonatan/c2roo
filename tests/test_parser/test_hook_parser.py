from pathlib import Path

from c2roo.parser.hook_parser import parse_hooks

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_hooks():
    hooks_json = FIXTURES / "hooks" / "hooks.json"
    hooks = parse_hooks(hooks_json)

    assert len(hooks) == 2

    pre_tool = [h for h in hooks if h.event == "PreToolUse"][0]
    assert pre_tool.matcher == "Edit|Write|MultiEdit"
    assert "lint.py" in pre_tool.command
    assert pre_tool.timeout == 10

    session = [h for h in hooks if h.event == "SessionStart"][0]
    assert session.matcher is None
    assert session.command == "echo starting"


def test_parse_hooks_missing_file():
    missing = Path("/nonexistent/hooks.json")
    hooks = parse_hooks(missing)
    assert hooks == []
