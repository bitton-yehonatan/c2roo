from pathlib import Path

from c2roo.models.command import Command
from c2roo.parser.frontmatter import parse_frontmatter


def parse_command(cmd_path: Path) -> Command:
    """Parse a command markdown file into a Command IR."""
    content = cmd_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    return Command(
        name=cmd_path.stem,
        description=meta.get("description"),
        argument_hint=meta.get("argument-hint"),
        allowed_tools=meta.get("allowed-tools"),
        body=body,
    )
