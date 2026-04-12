from dataclasses import dataclass, field
from pathlib import Path

from c2roo.models.agent import Agent
from c2roo.models.command import Command
from c2roo.models.hook import Hook
from c2roo.models.mcp import McpServer
from c2roo.models.skill import Skill


@dataclass
class PluginMetadata:
    name: str
    description: str
    version: str | None = None
    author: str | None = None
    homepage: str | None = None
    license: str | None = None


@dataclass
class Plugin:
    metadata: PluginMetadata
    source_path: Path
    skills: list[Skill] = field(default_factory=list)
    commands: list[Command] = field(default_factory=list)
    agents: list[Agent] = field(default_factory=list)
    hooks: list[Hook] = field(default_factory=list)
    mcp_servers: dict[str, McpServer] = field(default_factory=dict)
