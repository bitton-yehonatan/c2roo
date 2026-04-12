from pathlib import Path

from c2roo.models.skill import Skill
from c2roo.parser.frontmatter import parse_frontmatter


def _as_str(value: object, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _as_opt_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _as_opt_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _as_str_dict(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(k): str(v) for k, v in value.items()}


def parse_skill(skill_dir: Path) -> Skill:
    """Parse a skill directory containing SKILL.md into a Skill IR."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"No SKILL.md found in {skill_dir}")

    content = skill_md.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    resources = [p for p in skill_dir.rglob("*") if p.is_file() and p.name != "SKILL.md"]

    return Skill(
        name=_as_str(meta.get("name"), skill_dir.name),
        description=_as_str(meta.get("description"), ""),
        body=body,
        license=_as_opt_str(meta.get("license")),
        compatibility=_as_opt_str(meta.get("compatibility")),
        metadata=_as_str_dict(meta.get("metadata")),
        allowed_tools=_as_opt_str(meta.get("allowed-tools")),
        resources=resources,
        disable_model_invocation=_as_opt_bool(meta.get("disable-model-invocation")),
        user_invocable=_as_opt_bool(meta.get("user-invocable")),
        context=_as_opt_str(meta.get("context")),
        agent=_as_opt_str(meta.get("agent")),
    )
