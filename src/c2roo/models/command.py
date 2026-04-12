from dataclasses import dataclass


@dataclass
class Command:
    name: str
    description: str | None = None
    argument_hint: str | None = None
    allowed_tools: str | None = None
    body: str = ""
