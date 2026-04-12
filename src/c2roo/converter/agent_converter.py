from dataclasses import dataclass

from c2roo.models.agent import Agent

# Mapping from Claude Code tool names to Roo tool groups
TOOL_TO_GROUP = {
    "Read": "read",
    "Grep": "read",
    "Glob": "read",
    "LS": "read",
    "NotebookRead": "read",
    "Write": "edit",
    "Edit": "edit",
    "MultiEdit": "edit",
    "NotebookEdit": "edit",
    "Bash": "command",
    "BashOutput": "command",
    "KillShell": "command",
}

MCP_TOOLS = {"WebFetch", "WebSearch", "TodoWrite"}


def _humanize_name(slug: str) -> str:
    """Convert kebab-case slug to Title Case name."""
    return " ".join(word.capitalize() for word in slug.split("-"))


def _extract_role_definition(body: str, max_length: int = 500) -> str:
    """Extract the first paragraph of the body as a role definition."""
    paragraphs = body.split("\n\n")
    first = paragraphs[0].strip() if paragraphs else body.strip()
    if len(first) > max_length:
        first = first[:max_length].rsplit(" ", 1)[0] + "..."
    return first


def _map_tools_to_groups(tools: list[str]) -> list[str]:
    """Map Claude Code tool names to Roo tool groups."""
    groups = set()
    for tool in tools:
        if tool in TOOL_TO_GROUP:
            groups.add(TOOL_TO_GROUP[tool])
        elif tool in MCP_TOOLS:
            groups.add("mcp")
    return sorted(groups)


@dataclass
class ConvertedAgent:
    mode: dict[str, object]
    rules_content: str
    slug: str


def convert_agent(agent: Agent) -> ConvertedAgent:
    """Convert an Agent IR to a Roo custom mode + rules file."""
    slug = agent.name
    groups = _map_tools_to_groups(agent.tools)

    mode: dict[str, object] = {
        "slug": slug,
        "name": _humanize_name(slug),
        "description": agent.description,
        "roleDefinition": _extract_role_definition(agent.body),
        "groups": groups,
    }

    lines = [
        f"# {_humanize_name(slug)}",
        "",
        f"> Converted from Claude Code agent: `{agent.name}`",
        "",
        agent.body,
    ]

    footer_parts = []
    if agent.model:
        footer_parts.append(f"Originally configured for model: {agent.model}")
    if agent.tools:
        footer_parts.append(f"Original tool list: {', '.join(agent.tools)}")

    if footer_parts:
        lines.append("")
        lines.append("---")
        lines.append("")
        for part in footer_parts:
            lines.append(f"*{part}*")

    return ConvertedAgent(
        mode=mode,
        rules_content="\n".join(lines),
        slug=slug,
    )
