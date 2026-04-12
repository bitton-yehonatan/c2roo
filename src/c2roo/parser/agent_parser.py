from pathlib import Path

from c2roo.models.agent import Agent
from c2roo.parser.frontmatter import parse_frontmatter


def parse_agent(agent_path: Path) -> Agent:
    """Parse an agent markdown file into an Agent IR."""
    content = agent_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    tools = meta.get("tools", [])
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.split(",")]

    return Agent(
        name=meta.get("name", agent_path.stem),
        description=meta.get("description", ""),
        body=body,
        model=meta.get("model"),
        tools=tools,
        color=meta.get("color"),
    )
