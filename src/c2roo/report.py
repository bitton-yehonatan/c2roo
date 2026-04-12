from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel


@dataclass
class ConversionReport:
    plugin_name: str
    skill_count: int = 0
    command_count: int = 0
    agent_count: int = 0
    hook_count: int = 0
    mcp_count: int = 0
    skill_drops: list[tuple[str, list[str]]] = field(default_factory=list)
    command_drops: list[tuple[str, list[str]]] = field(default_factory=list)

    def add_skill(self, name: str, dropped: list[str]) -> None:
        self.skill_count += 1
        if dropped:
            self.skill_drops.append((name, dropped))

    def add_command(self, name: str, dropped: list[str]) -> None:
        self.command_count += 1
        if dropped:
            self.command_drops.append((name, dropped))

    def add_agent(self, name: str) -> None:
        self.agent_count += 1

    def add_hooks(self, count: int) -> None:
        self.hook_count += count

    def add_mcp(self, count: int) -> None:
        self.mcp_count += count

    def render(self, output_path: str) -> str:
        """Render the report as a string for display."""
        lines = []

        def _status(count: int, label: str, extra: str = "") -> str:
            icon = "✓" if not extra else "~"
            suffix = f" ({extra})" if extra else ""
            return f" {icon} {label + ':':<11} {count} converted{suffix}"

        lines.append(_status(self.skill_count, "Skills"))
        lines.append(_status(self.command_count, "Commands"))

        agent_extra = "model pref lost" if self.agent_count > 0 else ""
        agent_label = "Agents → modes" if self.agent_count > 0 else "Agents"
        lines.append(_status(self.agent_count, agent_label, agent_extra))

        hook_extra = "not enforced" if self.hook_count > 0 else ""
        hook_label = "Hooks → rules" if self.hook_count > 0 else "Hooks"
        lines.append(_status(self.hook_count, hook_label, hook_extra))

        lines.append(_status(self.mcp_count, "MCP"))

        # Dropped fields summary
        all_drops = []
        if self.skill_drops:
            fields = set()
            count = 0
            for _, dropped in self.skill_drops:
                fields.update(dropped)
                count += 1
            all_drops.append(f"  - skills: {', '.join(sorted(fields))} ({count} skills)")
        if self.command_drops:
            fields = set()
            count = 0
            for _, dropped in self.command_drops:
                fields.update(dropped)
                count += 1
            all_drops.append(f"  - commands: {', '.join(sorted(fields))} ({count} commands)")

        if all_drops:
            lines.append("")
            lines.append(" Dropped fields:")
            lines.extend(all_drops)

        lines.append("")
        lines.append(f" Output: {output_path}")

        return "\n".join(lines)

    def print(self, output_path: str) -> None:
        """Print the report to the terminal using Rich."""
        console = Console()
        text = self.render(output_path)
        panel = Panel(text, title=f"Conversion Report: {self.plugin_name}", expand=False)
        console.print(panel)
