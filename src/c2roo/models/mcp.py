from dataclasses import dataclass, field


@dataclass
class McpServer:
    name: str
    command: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    disabled: bool = False
    always_allow: list[str] = field(default_factory=list)
    timeout: int | None = None
