from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Skill:
    name: str
    description: str
    body: str
    license: str | None = None
    compatibility: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    allowed_tools: str | None = None
    resources: list[Path] = field(default_factory=list)
    disable_model_invocation: bool | None = None
    user_invocable: bool | None = None
    context: str | None = None
    agent: str | None = None
