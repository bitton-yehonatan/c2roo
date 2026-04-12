from c2roo.models.hook import Hook


def convert_hooks(hooks: list[Hook]) -> str:
    """Convert Hook IRs to a Roo guidance rules markdown document."""
    if not hooks:
        return ""

    lines = [
        "# Converted from Claude Code hooks",
        "",
        "> These hooks were originally enforced automatically by Claude Code.",
        "> Roo Code does not support hooks. The guidance below describes the",
        "> original behavior — consider running these manually or setting up",
        "> an equivalent workflow.",
        "",
    ]

    # Group by event type
    by_event: dict[str, list[Hook]] = {}
    for hook in hooks:
        by_event.setdefault(hook.event, []).append(hook)

    for event, event_hooks in by_event.items():
        lines.append(f"## {event}")
        lines.append("")

        for hook in event_hooks:
            if hook.matcher:
                lines.append(f"**Trigger:** when tools matching `{hook.matcher}` are used")
                lines.append("")

            lines.append("**Original command:**")
            lines.append("```")
            lines.append(hook.command)
            lines.append("```")

            if hook.timeout:
                lines.append(f"*Timeout: {hook.timeout}s*")

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
