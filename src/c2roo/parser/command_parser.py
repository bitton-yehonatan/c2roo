from pathlib import Path

from c2roo.models.command import Command
from c2roo.parser.frontmatter import parse_frontmatter


def _as_opt_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def parse_command(cmd_path: Path) -> Command:
    """Parse a command markdown file into a Command IR."""
    content = cmd_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    return Command(
        name=cmd_path.stem,
        description=_as_opt_str(meta.get("description")),
        argument_hint=_as_opt_str(meta.get("argument-hint")),
        allowed_tools=_as_opt_str(meta.get("allowed-tools")),
        body=body,
    )
