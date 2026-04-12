import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from c2roo.cli import main

FIXTURES = Path(__file__).parent / "fixtures" / "sample-plugin"


def test_full_conversion_pipeline(tmp_path):
    """End-to-end: convert the sample plugin and verify all outputs."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["convert", str(FIXTURES), "--project", "--force"])
        assert result.exit_code == 0, f"CLI failed: {result.output}"

        roo = Path(".roo")

        # Skills
        skill_md = roo / "skills" / "pdf-processing" / "SKILL.md"
        assert skill_md.exists()
        content = skill_md.read_text()
        assert "name: pdf-processing" in content
        # Claude-specific fields removed from frontmatter
        frontmatter_section = content.split("---")[1]
        assert "disable-model-invocation" not in frontmatter_section
        assert "context" not in frontmatter_section
        assert "PyPDF2" in content  # Body preserved

        # Skill resources copied
        assert (roo / "skills" / "pdf-processing" / "scripts" / "extract.py").exists()

        # Commands
        cmd = roo / "commands" / "commit.md"
        assert cmd.exists()
        cmd_content = cmd.read_text()
        assert "description: Create a git commit" in cmd_content
        assert "allowed-tools" not in cmd_content  # Dropped
        assert "!`git status`" in cmd_content  # Dynamic context preserved

        # Agents -> Custom Modes + Rules
        roomodes = Path(".roomodes")
        assert roomodes.exists()
        modes_data = yaml.safe_load(roomodes.read_text())
        assert len(modes_data["customModes"]) == 1
        mode = modes_data["customModes"][0]
        assert mode["slug"] == "code-reviewer"
        assert mode["name"] == "Code Reviewer"
        assert "read" in mode["groups"]
        assert "command" in mode["groups"]

        rules_file = roo / "rules-code-reviewer" / "converted-agent.md"
        assert rules_file.exists()
        rules_content = rules_file.read_text()
        assert "expert code reviewer" in rules_content
        assert "Originally configured for model: sonnet" in rules_content

        # Hooks -> Guidance
        hooks_guidance = roo / "rules" / "converted-hooks-guidance.md"
        assert hooks_guidance.exists()
        hooks_content = hooks_guidance.read_text()
        assert "PreToolUse" in hooks_content
        assert "Edit|Write|MultiEdit" in hooks_content
        assert "lint.py" in hooks_content
        assert "SessionStart" in hooks_content

        # MCP
        mcp = roo / "mcp.json"
        assert mcp.exists()
        mcp_data = json.loads(mcp.read_text())
        assert "my-server" in mcp_data["mcpServers"]
        assert "remote-server" in mcp_data["mcpServers"]

        # Report output
        assert "Conversion Report" in result.output
        assert "sample-plugin" in result.output
