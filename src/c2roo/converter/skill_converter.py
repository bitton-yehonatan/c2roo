from dataclasses import dataclass, field

from c2roo.models.skill import Skill

CLAUDE_SPECIFIC_FIELDS = ["disable-model-invocation", "user-invocable", "context", "agent"]


@dataclass
class ConvertedSkill:
    frontmatter: dict[str, object]
    body: str
    name: str
    dropped_fields: list[str] = field(default_factory=list)


def convert_skill(skill: Skill) -> ConvertedSkill:
    """Convert a Skill IR to Roo skill format (cleaned frontmatter)."""
    frontmatter: dict[str, object] = {
        "name": skill.name,
        "description": skill.description,
    }

    if skill.license:
        frontmatter["license"] = skill.license
    if skill.compatibility:
        frontmatter["compatibility"] = skill.compatibility
    if skill.metadata:
        frontmatter["metadata"] = skill.metadata
    if skill.allowed_tools:
        frontmatter["allowed-tools"] = skill.allowed_tools

    # Track which Claude-specific fields were present and dropped
    dropped = []
    if skill.agent is not None:
        dropped.append("agent")
    if skill.context is not None:
        dropped.append("context")
    if skill.disable_model_invocation is not None:
        dropped.append("disable-model-invocation")
    if skill.user_invocable is not None:
        dropped.append("user-invocable")

    return ConvertedSkill(
        frontmatter=frontmatter,
        body=skill.body,
        name=skill.name,
        dropped_fields=sorted(dropped),
    )
