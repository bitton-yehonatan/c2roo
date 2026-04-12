import json

import yaml

from c2roo.converter.agent_converter import ConvertedAgent
from c2roo.converter.command_converter import ConvertedCommand
from c2roo.converter.skill_converter import ConvertedSkill
from c2roo.writer.roo_writer import RooWriter


def test_write_skill(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    skill = ConvertedSkill(
        name="pdf-processing",
        frontmatter={"name": "pdf-processing", "description": "Process PDFs"},
        body="# Instructions\nDo stuff.",
        dropped_fields=[],
    )
    source_skill_dir = tmp_path / "source" / "skills" / "pdf-processing"
    source_skill_dir.mkdir(parents=True)
    (source_skill_dir / "SKILL.md").write_text("original")
    (source_skill_dir / "scripts").mkdir()
    (source_skill_dir / "scripts" / "extract.py").write_text("print('hi')")

    writer.write_skill(skill, source_skill_dir)

    output_skill = tmp_path / "skills" / "pdf-processing" / "SKILL.md"
    assert output_skill.exists()
    content = output_skill.read_text()
    assert "name: pdf-processing" in content
    assert "# Instructions" in content

    script = tmp_path / "skills" / "pdf-processing" / "scripts" / "extract.py"
    assert script.exists()


def test_write_command(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    cmd = ConvertedCommand(
        name="commit",
        frontmatter={"description": "Create a commit"},
        body="Do a commit.",
        dropped_fields=[],
    )
    writer.write_command(cmd)

    output = tmp_path / "commands" / "commit.md"
    assert output.exists()
    content = output.read_text()
    assert "description: Create a commit" in content
    assert "Do a commit." in content


def test_write_agent_mode_and_rules(tmp_path):
    # output_root simulates .roo/ inside a project
    output_root = tmp_path / ".roo"
    writer = RooWriter(output_root=output_root, force=False, dry_run=False)
    agent = ConvertedAgent(
        slug="code-reviewer",
        mode={
            "slug": "code-reviewer",
            "name": "Code Reviewer",
            "roleDefinition": "Expert reviewer.",
            "groups": ["read"],
        },
        rules_content="# Rules\nReview code.",
    )
    writer.write_agent(agent)

    # Check .roomodes (lives next to .roo/, not inside it)
    roomodes = tmp_path / ".roomodes"
    assert roomodes.exists()
    data = yaml.safe_load(roomodes.read_text())
    assert len(data["customModes"]) == 1
    assert data["customModes"][0]["slug"] == "code-reviewer"

    # Check rules file (inside .roo/)
    rules = output_root / "rules-code-reviewer" / "converted-agent.md"
    assert rules.exists()
    assert "Review code." in rules.read_text()


def test_write_agent_merges_roomodes(tmp_path):
    # Pre-existing .roomodes (lives at project root, next to .roo/)
    roomodes = tmp_path / ".roomodes"
    roomodes.write_text(yaml.dump({"customModes": [{"slug": "existing", "name": "Existing"}]}))

    output_root = tmp_path / ".roo"
    writer = RooWriter(output_root=output_root, force=False, dry_run=False)
    agent = ConvertedAgent(
        slug="new-mode",
        mode={"slug": "new-mode", "name": "New Mode", "roleDefinition": "New.", "groups": ["read"]},
        rules_content="# Rules",
    )
    writer.write_agent(agent)

    data = yaml.safe_load(roomodes.read_text())
    assert len(data["customModes"]) == 2
    slugs = [m["slug"] for m in data["customModes"]]
    assert "existing" in slugs
    assert "new-mode" in slugs


def test_write_agent_skips_duplicate_slug(tmp_path):
    roomodes = tmp_path / ".roomodes"
    roomodes.write_text(yaml.dump({"customModes": [{"slug": "dupe", "name": "Dupe"}]}))

    output_root = tmp_path / ".roo"
    writer = RooWriter(output_root=output_root, force=False, dry_run=False)
    agent = ConvertedAgent(
        slug="dupe",
        mode={"slug": "dupe", "name": "Dupe v2", "roleDefinition": "New.", "groups": ["read"]},
        rules_content="# Rules",
    )
    writer.write_agent(agent)

    data = yaml.safe_load(roomodes.read_text())
    assert len(data["customModes"]) == 1
    assert data["customModes"][0]["name"] == "Dupe"  # Original preserved


def test_write_hooks(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    writer.write_hooks("# Hook guidance content\n")

    output = tmp_path / "rules" / "converted-hooks-guidance.md"
    assert output.exists()
    assert "Hook guidance" in output.read_text()


def test_write_mcp(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    mcp_data = {"my-server": {"command": "npx", "args": ["-y", "@org/server"]}}
    writer.write_mcp(mcp_data)

    output = tmp_path / "mcp.json"
    assert output.exists()
    data = json.loads(output.read_text())
    assert "my-server" in data["mcpServers"]


def test_write_mcp_merges_existing(tmp_path):
    mcp_file = tmp_path / "mcp.json"
    mcp_file.write_text(json.dumps({"mcpServers": {"existing": {"url": "http://old"}}}))

    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    writer.write_mcp({"new-server": {"command": "npx", "args": []}})

    data = json.loads(mcp_file.read_text())
    assert "existing" in data["mcpServers"]
    assert "new-server" in data["mcpServers"]


def test_dry_run_writes_nothing(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=True)
    cmd = ConvertedCommand(
        name="test",
        frontmatter={"description": "Test"},
        body="Body.",
        dropped_fields=[],
    )
    writer.write_command(cmd)

    assert not (tmp_path / "commands" / "test.md").exists()


def test_conflict_without_force_raises(tmp_path):
    # Pre-create the file
    (tmp_path / "commands").mkdir(parents=True)
    (tmp_path / "commands" / "conflict.md").write_text("existing")

    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    cmd = ConvertedCommand(
        name="conflict",
        frontmatter={"description": "New"},
        body="New body.",
        dropped_fields=[],
    )
    try:
        writer.write_command(cmd)
        assert False, "Should have raised"
    except FileExistsError:
        pass
