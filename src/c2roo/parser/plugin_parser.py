import json
from pathlib import Path

from c2roo.models.plugin import Plugin, PluginMetadata
from c2roo.parser.agent_parser import parse_agent
from c2roo.parser.command_parser import parse_command
from c2roo.parser.hook_parser import parse_hooks
from c2roo.parser.mcp_parser import parse_mcp
from c2roo.parser.skill_parser import parse_skill


def parse_plugin(plugin_dir: Path) -> Plugin:
    """Parse a Claude Code plugin directory into a Plugin IR."""
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Not a Claude Code plugin: expected {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    author_obj = manifest.get("author", {})
    author_name = author_obj.get("name") if isinstance(author_obj, dict) else None

    metadata = PluginMetadata(
        name=manifest.get("name", plugin_dir.name),
        description=manifest.get("description", ""),
        version=manifest.get("version"),
        author=author_name,
        homepage=manifest.get("homepage"),
        license=manifest.get("license"),
    )

    skills = []
    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for skill_subdir in sorted(skills_dir.iterdir()):
            if skill_subdir.is_dir() and (skill_subdir / "SKILL.md").exists():
                skills.append(parse_skill(skill_subdir))

    commands = []
    commands_dir = plugin_dir / "commands"
    if commands_dir.is_dir():
        for cmd_file in sorted(commands_dir.glob("*.md")):
            commands.append(parse_command(cmd_file))

    agents = []
    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for agent_file in sorted(agents_dir.glob("*.md")):
            agents.append(parse_agent(agent_file))

    hooks = parse_hooks(plugin_dir / "hooks" / "hooks.json")
    mcp_servers = parse_mcp(plugin_dir / ".mcp.json")

    return Plugin(
        metadata=metadata,
        source_path=plugin_dir,
        skills=skills,
        commands=commands,
        agents=agents,
        hooks=hooks,
        mcp_servers=mcp_servers,
    )
