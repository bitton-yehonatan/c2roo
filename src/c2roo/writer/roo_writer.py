import json
import shutil
from pathlib import Path

import yaml

from c2roo.converter.agent_converter import ConvertedAgent
from c2roo.converter.command_converter import ConvertedCommand
from c2roo.converter.skill_converter import ConvertedSkill


def _render_markdown(frontmatter: dict[str, object], body: str) -> str:
    """Render YAML frontmatter + markdown body into a complete file."""
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{yaml_str}\n---\n\n{body}\n"


class RooWriter:
    def __init__(self, output_root: Path, force: bool, dry_run: bool) -> None:
        self.output_root = output_root
        self.force = force
        self.dry_run = dry_run
        self.written_files: list[Path] = []
        self.skipped_files: list[tuple[Path, str]] = []

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to a file, respecting force/dry_run flags."""
        if self.dry_run:
            self.written_files.append(path)
            return

        if path.exists() and not self.force:
            raise FileExistsError(f"File already exists (use --force to overwrite): {path}")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.written_files.append(path)

    def write_skill(self, skill: ConvertedSkill, source_dir: Path) -> None:
        """Write a converted skill directory."""
        dest_dir = self.output_root / "skills" / skill.name

        # Write SKILL.md
        content = _render_markdown(skill.frontmatter, skill.body)
        self._write_file(dest_dir / "SKILL.md", content)

        # Copy resource files
        if not self.dry_run:
            for item in source_dir.iterdir():
                if item.name == "SKILL.md":
                    continue
                dest = dest_dir / item.name
                if item.is_dir():
                    if dest.exists() and self.force:
                        shutil.rmtree(dest)
                    elif dest.exists():
                        self.skipped_files.append((dest, "directory exists"))
                        continue
                    shutil.copytree(item, dest)
                else:
                    self._write_file(dest, item.read_text(encoding="utf-8"))

    def write_command(self, cmd: ConvertedCommand) -> None:
        """Write a converted slash command."""
        path = self.output_root / "commands" / f"{cmd.name}.md"
        content = _render_markdown(cmd.frontmatter, cmd.body)
        self._write_file(path, content)

    def write_agent(self, agent: ConvertedAgent) -> None:
        """Write a converted agent as custom mode entry + rules file."""
        # .roomodes lives next to .roo/, not inside it
        roomodes_path = self.output_root.parent / ".roomodes"

        if not self.dry_run:
            existing_modes = []
            if roomodes_path.exists():
                data = yaml.safe_load(roomodes_path.read_text(encoding="utf-8")) or {}
                existing_modes = data.get("customModes", [])

            # Skip if slug already exists
            existing_slugs = {m["slug"] for m in existing_modes}
            if agent.slug not in existing_slugs:
                existing_modes.append(agent.mode)
                roomodes_path.parent.mkdir(parents=True, exist_ok=True)
                roomodes_path.write_text(
                    yaml.dump(
                        {"customModes": existing_modes}, default_flow_style=False, sort_keys=False
                    ),
                    encoding="utf-8",
                )
            else:
                self.skipped_files.append(
                    (roomodes_path, f"mode slug '{agent.slug}' already exists")
                )

        self.written_files.append(roomodes_path)

        # Write rules file
        rules_path = self.output_root / f"rules-{agent.slug}" / "converted-agent.md"
        self._write_file(rules_path, agent.rules_content + "\n")

    def write_hooks(self, content: str) -> None:
        """Write converted hooks guidance."""
        if not content:
            return
        path = self.output_root / "rules" / "converted-hooks-guidance.md"
        self._write_file(path, content)

    def write_mcp(self, mcp_data: dict[str, dict[str, object]]) -> None:
        """Write/merge MCP server configuration."""
        if not mcp_data:
            return

        path = self.output_root / "mcp.json"

        if not self.dry_run:
            existing = {}
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                existing = data.get("mcpServers", {})

            existing.update(mcp_data)

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"mcpServers": existing}, indent=2) + "\n",
                encoding="utf-8",
            )

        self.written_files.append(path)
