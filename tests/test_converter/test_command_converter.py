from c2roo.converter.command_converter import convert_command
from c2roo.models.command import Command


def test_convert_command_drops_allowed_tools():
    cmd = Command(
        name="commit",
        description="Create a git commit",
        argument_hint="<optional message>",
        allowed_tools="Bash(git add:*), Bash(git commit:*)",
        body="## Context\n!`git status`\n\nCreate a commit.",
    )
    result = convert_command(cmd)
    assert result.frontmatter["description"] == "Create a git commit"
    assert result.frontmatter["argument-hint"] == "<optional message>"
    assert "allowed-tools" not in result.frontmatter
    assert "!`git status`" in result.body
    assert result.dropped_fields == ["allowed-tools"]


def test_convert_command_no_optional_fields():
    cmd = Command(name="simple", body="Just do it.")
    result = convert_command(cmd)
    assert "description" not in result.frontmatter
    assert result.dropped_fields == []
