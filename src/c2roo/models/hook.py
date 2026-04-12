from dataclasses import dataclass


@dataclass
class Hook:
    event: str
    command: str
    matcher: str | None = None
    timeout: int | None = None
