import json
from pathlib import Path

from c2roo.models.hook import Hook


def parse_hooks(hooks_json_path: Path) -> list[Hook]:
    """Parse hooks/hooks.json into a list of Hook IRs."""
    if not hooks_json_path.exists():
        return []

    data = json.loads(hooks_json_path.read_text(encoding="utf-8"))
    hooks_config = data.get("hooks", {})
    result = []

    for event_name, event_entries in hooks_config.items():
        for entry in event_entries:
            matcher = entry.get("matcher")
            for hook_def in entry.get("hooks", []):
                result.append(
                    Hook(
                        event=event_name,
                        command=hook_def.get("command", ""),
                        matcher=matcher,
                        timeout=hook_def.get("timeout"),
                    )
                )

    return result
