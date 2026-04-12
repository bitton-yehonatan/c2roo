from dataclasses import dataclass, field

from c2roo.models.command import Command


@dataclass
class ConvertedCommand:
    frontmatter: dict[str, object]
    body: str
    name: str
    dropped_fields: list[str] = field(default_factory=list)


def convert_command(cmd: Command) -> ConvertedCommand:
    """Convert a Command IR to Roo slash command format."""
    frontmatter: dict[str, object] = {}

    if cmd.description:
        frontmatter["description"] = cmd.description
    if cmd.argument_hint:
        frontmatter["argument-hint"] = cmd.argument_hint

    dropped = []
    if cmd.allowed_tools:
        dropped.append("allowed-tools")

    return ConvertedCommand(
        frontmatter=frontmatter,
        body=cmd.body,
        name=cmd.name,
        dropped_fields=sorted(dropped),
    )
