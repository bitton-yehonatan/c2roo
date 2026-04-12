from dataclasses import dataclass, field


@dataclass
class Agent:
    name: str
    description: str
    body: str
    model: str | None = None
    tools: list[str] = field(default_factory=list)
    color: str | None = None
