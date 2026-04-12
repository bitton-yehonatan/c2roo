from pathlib import Path

from c2roo.models.agent import Agent
from c2roo.parser.frontmatter import parse_frontmatter


def _as_str(value: object, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _as_opt_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def parse_agent(agent_path: Path) -> Agent:
    """Parse an agent markdown file into an Agent IR."""
    content = agent_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    raw_tools = meta.get("tools", [])
    tools: list[str]
    if isinstance(raw_tools, str):
        tools = [t.strip() for t in raw_tools.split(",")]
    elif isinstance(raw_tools, list):
        tools = [str(t) for t in raw_tools]
    else:
        tools = []

    return Agent(
        name=_as_str(meta.get("name"), agent_path.stem),
        description=_as_str(meta.get("description"), ""),
        body=body,
        model=_as_opt_str(meta.get("model")),
        tools=tools,
        color=_as_opt_str(meta.get("color")),
    )
