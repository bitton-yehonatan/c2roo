from pathlib import Path

from c2roo.models.skill import Skill
from c2roo.parser.frontmatter import parse_frontmatter


def parse_skill(skill_dir: Path) -> Skill:
    """Parse a skill directory containing SKILL.md into a Skill IR."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"No SKILL.md found in {skill_dir}")

    content = skill_md.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    resources = [p for p in skill_dir.rglob("*") if p.is_file() and p.name != "SKILL.md"]

    return Skill(
        name=meta.get("name", skill_dir.name),
        description=meta.get("description", ""),
        body=body,
        license=meta.get("license"),
        compatibility=meta.get("compatibility"),
        metadata=meta.get("metadata", {}),
        allowed_tools=meta.get("allowed-tools"),
        resources=resources,
        disable_model_invocation=meta.get("disable-model-invocation"),
        user_invocable=meta.get("user-invocable"),
        context=meta.get("context"),
        agent=meta.get("agent"),
    )
