from pathlib import Path

from c2roo.parser.command_parser import parse_command

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_command():
    cmd_path = FIXTURES / "commands" / "commit.md"
    cmd = parse_command(cmd_path)

    assert cmd.name == "commit"
    assert cmd.description == "Create a git commit"
    assert cmd.allowed_tools == "Bash(git add:*), Bash(git status:*), Bash(git commit:*)"
    assert cmd.argument_hint == "<optional message>"
    assert "!`git status`" in cmd.body
