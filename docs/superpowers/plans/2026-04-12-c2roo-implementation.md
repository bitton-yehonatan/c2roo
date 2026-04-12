# c2roo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI tool that converts Claude Code plugins to Roo Code format, supporting marketplace browsing, git repos, and local sources.

**Architecture:** Single-pass converter with light IR. Parse Claude Code plugin entities into dataclasses, convert to Roo format, write to disk. Click CLI with subcommand groups. UV-managed Python project.

**Tech Stack:** Python 3.12+, UV, click, pyyaml, rich, pytest

---

## File Map

| File | Responsibility |
|---|---|
| `pyproject.toml` | UV project config, dependencies, `c2roo` entry point |
| `src/c2roo/__init__.py` | Package version |
| `src/c2roo/cli.py` | Click CLI: marketplace, convert, install command groups |
| `src/c2roo/models/__init__.py` | Re-exports all IR dataclasses |
| `src/c2roo/models/plugin.py` | `Plugin`, `PluginMetadata` dataclasses |
| `src/c2roo/models/skill.py` | `Skill` dataclass |
| `src/c2roo/models/command.py` | `Command` dataclass |
| `src/c2roo/models/agent.py` | `Agent` dataclass |
| `src/c2roo/models/hook.py` | `Hook` dataclass |
| `src/c2roo/models/mcp.py` | `McpServer` dataclass |
| `src/c2roo/parser/__init__.py` | Re-exports `parse_plugin` |
| `src/c2roo/parser/frontmatter.py` | YAML frontmatter extraction from markdown |
| `src/c2roo/parser/plugin_parser.py` | Orchestrates parsing: discovers entities, delegates |
| `src/c2roo/parser/skill_parser.py` | Parse `skills/<name>/SKILL.md` → `Skill` |
| `src/c2roo/parser/command_parser.py` | Parse `commands/<name>.md` → `Command` |
| `src/c2roo/parser/agent_parser.py` | Parse `agents/<name>.md` → `Agent` |
| `src/c2roo/parser/hook_parser.py` | Parse `hooks/hooks.json` → `list[Hook]` |
| `src/c2roo/parser/mcp_parser.py` | Parse `.mcp.json` → `dict[str, McpServer]` |
| `src/c2roo/converter/__init__.py` | Re-exports `convert_plugin` |
| `src/c2roo/converter/skill_converter.py` | `Skill` → Roo skill dir + cleaned SKILL.md |
| `src/c2roo/converter/command_converter.py` | `Command` → Roo slash command .md |
| `src/c2roo/converter/agent_converter.py` | `Agent` → custom mode dict + rules .md |
| `src/c2roo/converter/hook_converter.py` | `list[Hook]` → guidance rules .md |
| `src/c2roo/converter/mcp_converter.py` | `dict[str, McpServer]` → Roo mcp.json dict |
| `src/c2roo/writer/__init__.py` | Re-exports `RooWriter` |
| `src/c2roo/writer/roo_writer.py` | Writes all converted output to global/project paths |
| `src/c2roo/sources/__init__.py` | Re-exports source functions |
| `src/c2roo/sources/local_source.py` | Validate and return local plugin path |
| `src/c2roo/sources/git_source.py` | Clone git URL/subdir to temp dir |
| `src/c2roo/sources/marketplace.py` | Registry config, fetch marketplace.json, resolve plugins |
| `src/c2roo/report.py` | `ConversionReport` — tracks what converted, what dropped |

---

### Task 1: Project Scaffolding & UV Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/c2roo/__init__.py`
- Create: `src/c2roo/cli.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "c2roo"
version = "0.1.0"
description = "Convert Claude Code plugins to Roo Code format"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1",
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.scripts]
c2roo = "c2roo.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/c2roo"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

- [ ] **Step 2: Create src/c2roo/__init__.py**

```python
__version__ = "0.1.0"
```

- [ ] **Step 3: Create src/c2roo/cli.py with skeleton command groups**

```python
import click


@click.group()
@click.version_option()
def main():
    """Convert Claude Code plugins to Roo Code format."""


@main.group()
def marketplace():
    """Browse and manage plugin marketplace sources."""


@marketplace.command("browse")
@click.option("--source", default=None, help="Filter to a specific marketplace source.")
def marketplace_browse(source):
    """List plugins from registered marketplaces."""
    click.echo("Not yet implemented.")


@marketplace.command("add")
@click.argument("url")
def marketplace_add(url):
    """Register a new marketplace source."""
    click.echo("Not yet implemented.")


@marketplace.command("list")
def marketplace_list():
    """Show registered marketplace sources."""
    click.echo("Not yet implemented.")


@marketplace.command("remove")
@click.argument("name")
def marketplace_remove(name):
    """Remove a marketplace source."""
    click.echo("Not yet implemented.")


@main.command()
@click.argument("source")
@click.option("--global", "target_global", is_flag=True, default=False, help="Install to ~/.roo/ (global).")
@click.option("--project", "target_project", is_flag=True, default=False, help="Install to .roo/ (project).")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be converted.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files.")
def convert(source, target_global, target_project, dry_run, force):
    """Convert a Claude Code plugin from a local path or git URL."""
    if not target_global and not target_project:
        raise click.UsageError("Must specify --global or --project.")
    if target_global and target_project:
        raise click.UsageError("Cannot specify both --global and --project.")
    click.echo("Not yet implemented.")


@main.command()
@click.argument("plugin_name")
@click.option("--global", "target_global", is_flag=True, default=False, help="Install to ~/.roo/ (global).")
@click.option("--project", "target_project", is_flag=True, default=False, help="Install to .roo/ (project).")
@click.option("--source", default=None, help="Which marketplace to search.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be converted.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files.")
def install(plugin_name, target_global, target_project, source, dry_run, force):
    """Install a plugin from a marketplace, converting to Roo format."""
    if not target_global and not target_project:
        raise click.UsageError("Must specify --global or --project.")
    if target_global and target_project:
        raise click.UsageError("Cannot specify both --global and --project.")
    click.echo("Not yet implemented.")
```

- [ ] **Step 4: Install dependencies and verify CLI works**

Run: `uv sync && uv run c2roo --version`
Expected: `c2roo, version 0.1.0`

Run: `uv run c2roo convert foo`
Expected: `Error: Must specify --global or --project.`

Run: `uv run c2roo marketplace list`
Expected: `Not yet implemented.`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/c2roo/__init__.py src/c2roo/cli.py
git commit -m "feat: scaffold UV project with click CLI skeleton"
```

---

### Task 2: IR Dataclasses (Models)

**Files:**
- Create: `src/c2roo/models/__init__.py`
- Create: `src/c2roo/models/plugin.py`
- Create: `src/c2roo/models/skill.py`
- Create: `src/c2roo/models/command.py`
- Create: `src/c2roo/models/agent.py`
- Create: `src/c2roo/models/hook.py`
- Create: `src/c2roo/models/mcp.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write tests for IR dataclasses**

```python
# tests/test_models.py
from pathlib import Path

from c2roo.models import (
    Agent,
    Command,
    Hook,
    McpServer,
    Plugin,
    PluginMetadata,
    Skill,
)


def test_plugin_metadata_required_fields():
    meta = PluginMetadata(name="test", version=None, description="A test", author=None, homepage=None, license=None)
    assert meta.name == "test"
    assert meta.version is None


def test_skill_with_all_fields():
    skill = Skill(
        name="pdf-processing",
        description="Process PDFs",
        body="# Instructions\nDo stuff.",
        license="MIT",
        compatibility=None,
        metadata={"author": "test"},
        allowed_tools="Read Bash",
        resources=[Path("scripts/extract.py")],
        disable_model_invocation=True,
        user_invocable=None,
        context="fork",
        agent="Explore",
    )
    assert skill.name == "pdf-processing"
    assert skill.disable_model_invocation is True
    assert len(skill.resources) == 1


def test_command_minimal():
    cmd = Command(name="commit", description="Create a commit", argument_hint=None, allowed_tools=None, body="Do a commit.")
    assert cmd.name == "commit"
    assert cmd.allowed_tools is None


def test_agent_tools_list():
    agent = Agent(
        name="code-reviewer",
        description="Reviews code",
        model="sonnet",
        tools=["Read", "Grep", "Glob", "Bash"],
        color="yellow",
        body="You are a code reviewer.",
    )
    assert "Bash" in agent.tools
    assert agent.model == "sonnet"


def test_hook_fields():
    hook = Hook(event="PreToolUse", matcher="Edit|Write", command="python3 lint.py", timeout=10)
    assert hook.event == "PreToolUse"
    assert hook.matcher == "Edit|Write"


def test_mcp_server_stdio():
    server = McpServer(
        name="my-server",
        command="npx",
        args=["-y", "@org/server"],
        env={"KEY": "val"},
        url=None,
        headers={},
        disabled=False,
        always_allow=["tool1"],
        timeout=60,
    )
    assert server.command == "npx"
    assert server.url is None


def test_mcp_server_sse():
    server = McpServer(
        name="remote",
        command=None,
        args=[],
        env={},
        url="http://localhost:3000/sse",
        headers={"Authorization": "Bearer tok"},
        disabled=False,
        always_allow=[],
        timeout=None,
    )
    assert server.url == "http://localhost:3000/sse"
    assert server.command is None


def test_plugin_assembles_all_entities():
    plugin = Plugin(
        metadata=PluginMetadata(name="test-plugin", version="1.0.0", description="Test", author=None, homepage=None, license=None),
        skills=[],
        commands=[],
        agents=[],
        hooks=[],
        mcp_servers={},
        source_path=Path("/tmp/test"),
    )
    assert plugin.metadata.name == "test-plugin"
    assert plugin.skills == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'c2roo.models'`

- [ ] **Step 3: Create all model files**

```python
# src/c2roo/models/skill.py
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
```

```python
# src/c2roo/models/command.py
from dataclasses import dataclass


@dataclass
class Command:
    name: str
    description: str | None = None
    argument_hint: str | None = None
    allowed_tools: str | None = None
    body: str = ""
```

```python
# src/c2roo/models/agent.py
from dataclasses import dataclass, field


@dataclass
class Agent:
    name: str
    description: str
    body: str
    model: str | None = None
    tools: list[str] = field(default_factory=list)
    color: str | None = None
```

```python
# src/c2roo/models/hook.py
from dataclasses import dataclass


@dataclass
class Hook:
    event: str
    command: str
    matcher: str | None = None
    timeout: int | None = None
```

```python
# src/c2roo/models/mcp.py
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
```

```python
# src/c2roo/models/plugin.py
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
```

```python
# src/c2roo/models/__init__.py
from c2roo.models.agent import Agent
from c2roo.models.command import Command
from c2roo.models.hook import Hook
from c2roo.models.mcp import McpServer
from c2roo.models.plugin import Plugin, PluginMetadata
from c2roo.models.skill import Skill

__all__ = [
    "Agent",
    "Command",
    "Hook",
    "McpServer",
    "Plugin",
    "PluginMetadata",
    "Skill",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_models.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/c2roo/models/ tests/test_models.py
git commit -m "feat: add IR dataclasses for all plugin entity types"
```

---

### Task 3: Frontmatter Parser

**Files:**
- Create: `src/c2roo/parser/__init__.py`
- Create: `src/c2roo/parser/frontmatter.py`
- Create: `tests/test_parser/__init__.py`
- Create: `tests/test_parser/test_frontmatter.py`

- [ ] **Step 1: Write tests for frontmatter extraction**

```python
# tests/test_parser/test_frontmatter.py
import pytest

from c2roo.parser.frontmatter import parse_frontmatter


def test_basic_frontmatter():
    content = """---
name: test-skill
description: A test skill
---

# Body content

Some instructions here.
"""
    meta, body = parse_frontmatter(content)
    assert meta["name"] == "test-skill"
    assert meta["description"] == "A test skill"
    assert "# Body content" in body
    assert "Some instructions here." in body


def test_no_frontmatter():
    content = "# Just a markdown file\n\nNo frontmatter here."
    meta, body = parse_frontmatter(content)
    assert meta == {}
    assert "# Just a markdown file" in body


def test_empty_frontmatter():
    content = "---\n---\n\nBody only."
    meta, body = parse_frontmatter(content)
    assert meta == {}
    assert "Body only." in body


def test_frontmatter_with_list_values():
    content = """---
name: agent
tools:
  - Read
  - Grep
  - Bash
---

Body."""
    meta, body = parse_frontmatter(content)
    assert meta["tools"] == ["Read", "Grep", "Bash"]
    assert "Body." in body


def test_frontmatter_with_boolean():
    content = """---
name: skill
disable-model-invocation: true
user-invocable: false
---

Content."""
    meta, body = parse_frontmatter(content)
    assert meta["disable-model-invocation"] is True
    assert meta["user-invocable"] is False


def test_body_stripped_of_leading_whitespace():
    content = """---
name: test
---


  
Body starts here."""
    meta, body = parse_frontmatter(content)
    assert body == "Body starts here."
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_parser/test_frontmatter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'c2roo.parser'`

- [ ] **Step 3: Implement frontmatter parser**

```python
# src/c2roo/parser/__init__.py
```

```python
# src/c2roo/parser/frontmatter.py
import yaml


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a markdown string.

    Returns (metadata_dict, body_string). If no frontmatter is found,
    returns ({}, full_content).
    """
    if not content.startswith("---"):
        return {}, content.strip()

    # Find the closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content.strip()

    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3 :].strip()

    if not yaml_str:
        return {}, body

    meta = yaml.safe_load(yaml_str)
    if not isinstance(meta, dict):
        return {}, body

    return meta, body
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_parser/test_frontmatter.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/c2roo/parser/ tests/test_parser/
git commit -m "feat: add YAML frontmatter parser for markdown files"
```

---

### Task 4: Entity Parsers (Skill, Command, Agent)

**Files:**
- Create: `src/c2roo/parser/skill_parser.py`
- Create: `src/c2roo/parser/command_parser.py`
- Create: `src/c2roo/parser/agent_parser.py`
- Create: `tests/fixtures/sample-plugin/.claude-plugin/plugin.json`
- Create: `tests/fixtures/sample-plugin/skills/pdf-processing/SKILL.md`
- Create: `tests/fixtures/sample-plugin/skills/pdf-processing/scripts/extract.py`
- Create: `tests/fixtures/sample-plugin/commands/commit.md`
- Create: `tests/fixtures/sample-plugin/agents/code-reviewer.md`
- Create: `tests/test_parser/test_skill_parser.py`
- Create: `tests/test_parser/test_command_parser.py`
- Create: `tests/test_parser/test_agent_parser.py`

- [ ] **Step 1: Create test fixtures**

```json
// tests/fixtures/sample-plugin/.claude-plugin/plugin.json
{
  "name": "sample-plugin",
  "version": "1.0.0",
  "description": "A sample plugin for testing",
  "author": {
    "name": "Test Author",
    "email": "test@example.com"
  }
}
```

```markdown
<!-- tests/fixtures/sample-plugin/skills/pdf-processing/SKILL.md -->
---
name: pdf-processing
description: Extract text and tables from PDF files using Python libraries
license: MIT
allowed-tools: Read Bash
disable-model-invocation: true
context: fork
---

# PDF Processing

Use PyPDF2 to extract text from PDFs.

## Steps

1. Read the PDF file
2. Extract text from each page
3. Return structured output
```

```python
# tests/fixtures/sample-plugin/skills/pdf-processing/scripts/extract.py
print("placeholder extraction script")
```

```markdown
<!-- tests/fixtures/sample-plugin/commands/commit.md -->
---
description: Create a git commit
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: <optional message>
---

## Context
- Current git status: !`git status`

## Your task
Based on the above changes, create a single git commit.
```

```markdown
<!-- tests/fixtures/sample-plugin/agents/code-reviewer.md -->
---
name: code-reviewer
description: Reviews code for bugs and quality issues
model: sonnet
tools:
  - Read
  - Grep
  - Glob
  - Bash
color: yellow
---

You are an expert code reviewer. Analyze code for bugs, security issues, and quality problems.

Focus on:
- Logic errors
- Security vulnerabilities
- Performance issues
```

- [ ] **Step 2: Write tests for all three parsers**

```python
# tests/test_parser/test_skill_parser.py
from pathlib import Path

from c2roo.parser.skill_parser import parse_skill

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_skill():
    skill_dir = FIXTURES / "skills" / "pdf-processing"
    skill = parse_skill(skill_dir)

    assert skill.name == "pdf-processing"
    assert skill.description == "Extract text and tables from PDF files using Python libraries"
    assert skill.license == "MIT"
    assert skill.allowed_tools == "Read Bash"
    assert skill.disable_model_invocation is True
    assert skill.context == "fork"
    assert skill.user_invocable is None
    assert skill.agent is None
    assert "# PDF Processing" in skill.body
    assert "PyPDF2" in skill.body
    assert any(p.name == "extract.py" for p in skill.resources)


def test_parse_skill_missing_skill_md():
    empty_dir = FIXTURES / "skills"
    # skills/ dir itself has no SKILL.md
    try:
        parse_skill(empty_dir)
        assert False, "Should have raised"
    except FileNotFoundError:
        pass
```

```python
# tests/test_parser/test_command_parser.py
from pathlib import Path

from c2roo.parser.command_parser import parse_command

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_command():
    cmd_path = FIXTURES / "commands" / "commit.md"
    cmd = parse_command(cmd_path)

    assert cmd.name == "commit"
    assert cmd.description == "Create a git commit"
    assert cmd.allowed_tools == "Bash(git add:*), Bash(git status:*), Bash(git commit:*)"
    assert cmd.argument_hint == "<optional message>"
    assert "!`git status`" in cmd.body
```

```python
# tests/test_parser/test_agent_parser.py
from pathlib import Path

from c2roo.parser.agent_parser import parse_agent

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_agent():
    agent_path = FIXTURES / "agents" / "code-reviewer.md"
    agent = parse_agent(agent_path)

    assert agent.name == "code-reviewer"
    assert agent.description == "Reviews code for bugs and quality issues"
    assert agent.model == "sonnet"
    assert agent.tools == ["Read", "Grep", "Glob", "Bash"]
    assert agent.color == "yellow"
    assert "expert code reviewer" in agent.body
    assert "Security vulnerabilities" in agent.body
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_parser/test_skill_parser.py tests/test_parser/test_command_parser.py tests/test_parser/test_agent_parser.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement all three parsers**

```python
# src/c2roo/parser/skill_parser.py
from pathlib import Path

from c2roo.models.skill import Skill
from c2roo.parser.frontmatter import parse_frontmatter


def parse_skill(skill_dir: Path) -> Skill:
    """Parse a skill directory containing SKILL.md into a Skill IR."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"No SKILL.md found in {skill_dir}")

    content = skill_md.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    # Collect all resource files (everything except SKILL.md)
    resources = [p for p in skill_dir.rglob("*") if p.is_file() and p.name != "SKILL.md"]

    return Skill(
        name=meta.get("name", skill_dir.name),
        description=meta.get("description", ""),
        body=body,
        license=meta.get("license"),
        compatibility=meta.get("compatibility"),
        metadata=meta.get("metadata", {}),
        allowed_tools=meta.get("allowed-tools"),
        resources=resources,
        disable_model_invocation=meta.get("disable-model-invocation"),
        user_invocable=meta.get("user-invocable"),
        context=meta.get("context"),
        agent=meta.get("agent"),
    )
```

```python
# src/c2roo/parser/command_parser.py
from pathlib import Path

from c2roo.models.command import Command
from c2roo.parser.frontmatter import parse_frontmatter


def parse_command(cmd_path: Path) -> Command:
    """Parse a command markdown file into a Command IR."""
    content = cmd_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    return Command(
        name=cmd_path.stem,
        description=meta.get("description"),
        argument_hint=meta.get("argument-hint"),
        allowed_tools=meta.get("allowed-tools"),
        body=body,
    )
```

```python
# src/c2roo/parser/agent_parser.py
from pathlib import Path

from c2roo.models.agent import Agent
from c2roo.parser.frontmatter import parse_frontmatter


def parse_agent(agent_path: Path) -> Agent:
    """Parse an agent markdown file into an Agent IR."""
    content = agent_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)

    tools = meta.get("tools", [])
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.split(",")]

    return Agent(
        name=meta.get("name", agent_path.stem),
        description=meta.get("description", ""),
        body=body,
        model=meta.get("model"),
        tools=tools,
        color=meta.get("color"),
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_parser/ -v`
Expected: All tests PASS (frontmatter + skill + command + agent)

- [ ] **Step 6: Commit**

```bash
git add src/c2roo/parser/ tests/test_parser/ tests/fixtures/
git commit -m "feat: add skill, command, and agent parsers with fixtures"
```

---

### Task 5: Hook & MCP Parsers + Plugin Orchestrator

**Files:**
- Create: `src/c2roo/parser/hook_parser.py`
- Create: `src/c2roo/parser/mcp_parser.py`
- Create: `src/c2roo/parser/plugin_parser.py`
- Create: `tests/fixtures/sample-plugin/hooks/hooks.json`
- Create: `tests/fixtures/sample-plugin/.mcp.json`
- Create: `tests/test_parser/test_hook_parser.py`
- Create: `tests/test_parser/test_mcp_parser.py`
- Create: `tests/test_parser/test_plugin_parser.py`

- [ ] **Step 1: Create test fixtures for hooks and MCP**

```json
// tests/fixtures/sample-plugin/hooks/hooks.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lint.py",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo starting"
          }
        ]
      }
    ]
  }
}
```

```json
// tests/fixtures/sample-plugin/.mcp.json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@org/mcp-server"],
      "env": {
        "API_KEY": "test-key"
      }
    },
    "remote-server": {
      "url": "http://localhost:3000/sse",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  }
}
```

- [ ] **Step 2: Write tests**

```python
# tests/test_parser/test_hook_parser.py
from pathlib import Path

from c2roo.parser.hook_parser import parse_hooks

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_hooks():
    hooks_json = FIXTURES / "hooks" / "hooks.json"
    hooks = parse_hooks(hooks_json)

    assert len(hooks) == 2

    pre_tool = [h for h in hooks if h.event == "PreToolUse"][0]
    assert pre_tool.matcher == "Edit|Write|MultiEdit"
    assert "lint.py" in pre_tool.command
    assert pre_tool.timeout == 10

    session = [h for h in hooks if h.event == "SessionStart"][0]
    assert session.matcher is None
    assert session.command == "echo starting"


def test_parse_hooks_missing_file():
    missing = Path("/nonexistent/hooks.json")
    hooks = parse_hooks(missing)
    assert hooks == []
```

```python
# tests/test_parser/test_mcp_parser.py
from pathlib import Path

from c2roo.parser.mcp_parser import parse_mcp

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_mcp():
    mcp_json = FIXTURES / ".mcp.json"
    servers = parse_mcp(mcp_json)

    assert "my-server" in servers
    assert servers["my-server"].command == "npx"
    assert servers["my-server"].args == ["-y", "@org/mcp-server"]
    assert servers["my-server"].env == {"API_KEY": "test-key"}

    assert "remote-server" in servers
    assert servers["remote-server"].url == "http://localhost:3000/sse"
    assert servers["remote-server"].command is None


def test_parse_mcp_missing_file():
    missing = Path("/nonexistent/.mcp.json")
    servers = parse_mcp(missing)
    assert servers == {}
```

```python
# tests/test_parser/test_plugin_parser.py
from pathlib import Path

from c2roo.parser.plugin_parser import parse_plugin

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_full_plugin():
    plugin = parse_plugin(FIXTURES)

    assert plugin.metadata.name == "sample-plugin"
    assert plugin.metadata.version == "1.0.0"
    assert plugin.metadata.author == "Test Author"

    assert len(plugin.skills) == 1
    assert plugin.skills[0].name == "pdf-processing"

    assert len(plugin.commands) == 1
    assert plugin.commands[0].name == "commit"

    assert len(plugin.agents) == 1
    assert plugin.agents[0].name == "code-reviewer"

    assert len(plugin.hooks) == 2

    assert len(plugin.mcp_servers) == 2


def test_parse_plugin_missing_manifest():
    try:
        parse_plugin(Path("/nonexistent"))
        assert False, "Should have raised"
    except FileNotFoundError as e:
        assert "plugin.json" in str(e)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_parser/test_hook_parser.py tests/test_parser/test_mcp_parser.py tests/test_parser/test_plugin_parser.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement hook parser, MCP parser, and plugin orchestrator**

```python
# src/c2roo/parser/hook_parser.py
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
```

```python
# src/c2roo/parser/mcp_parser.py
import json
from pathlib import Path

from c2roo.models.mcp import McpServer


def parse_mcp(mcp_json_path: Path) -> dict[str, McpServer]:
    """Parse .mcp.json into a dict of McpServer IRs."""
    if not mcp_json_path.exists():
        return {}

    data = json.loads(mcp_json_path.read_text(encoding="utf-8"))
    servers = {}

    for name, config in data.get("mcpServers", {}).items():
        servers[name] = McpServer(
            name=name,
            command=config.get("command"),
            args=config.get("args", []),
            env=config.get("env", {}),
            url=config.get("url"),
            headers=config.get("headers", {}),
            disabled=config.get("disabled", False),
            always_allow=config.get("alwaysAllow", []),
            timeout=config.get("timeout"),
        )

    return servers
```

```python
# src/c2roo/parser/plugin_parser.py
import json
from pathlib import Path

from c2roo.models.plugin import Plugin, PluginMetadata
from c2roo.parser.agent_parser import parse_agent
from c2roo.parser.command_parser import parse_command
from c2roo.parser.hook_parser import parse_hooks
from c2roo.parser.mcp_parser import parse_mcp
from c2roo.parser.skill_parser import parse_skill


def parse_plugin(plugin_dir: Path) -> Plugin:
    """Parse a Claude Code plugin directory into a Plugin IR."""
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Not a Claude Code plugin: expected {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    author_obj = manifest.get("author", {})
    author_name = author_obj.get("name") if isinstance(author_obj, dict) else None

    metadata = PluginMetadata(
        name=manifest.get("name", plugin_dir.name),
        description=manifest.get("description", ""),
        version=manifest.get("version"),
        author=author_name,
        homepage=manifest.get("homepage"),
        license=manifest.get("license"),
    )

    # Parse skills
    skills = []
    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for skill_subdir in sorted(skills_dir.iterdir()):
            if skill_subdir.is_dir() and (skill_subdir / "SKILL.md").exists():
                skills.append(parse_skill(skill_subdir))

    # Parse commands
    commands = []
    commands_dir = plugin_dir / "commands"
    if commands_dir.is_dir():
        for cmd_file in sorted(commands_dir.glob("*.md")):
            commands.append(parse_command(cmd_file))

    # Parse agents
    agents = []
    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for agent_file in sorted(agents_dir.glob("*.md")):
            agents.append(parse_agent(agent_file))

    # Parse hooks
    hooks = parse_hooks(plugin_dir / "hooks" / "hooks.json")

    # Parse MCP servers
    mcp_servers = parse_mcp(plugin_dir / ".mcp.json")

    return Plugin(
        metadata=metadata,
        source_path=plugin_dir,
        skills=skills,
        commands=commands,
        agents=agents,
        hooks=hooks,
        mcp_servers=mcp_servers,
    )
```

Update the parser `__init__.py`:

```python
# src/c2roo/parser/__init__.py
from c2roo.parser.plugin_parser import parse_plugin

__all__ = ["parse_plugin"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_parser/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/c2roo/parser/ tests/test_parser/ tests/fixtures/
git commit -m "feat: add hook, MCP, and plugin orchestrator parsers"
```

---

### Task 6: Skill & Command Converters

**Files:**
- Create: `src/c2roo/converter/__init__.py`
- Create: `src/c2roo/converter/skill_converter.py`
- Create: `src/c2roo/converter/command_converter.py`
- Create: `tests/test_converter/__init__.py`
- Create: `tests/test_converter/test_skill_converter.py`
- Create: `tests/test_converter/test_command_converter.py`

- [ ] **Step 1: Write tests for skill converter**

```python
# tests/test_converter/test_skill_converter.py
from pathlib import Path

from c2roo.models.skill import Skill
from c2roo.converter.skill_converter import convert_skill


def test_convert_skill_cleans_frontmatter():
    skill = Skill(
        name="pdf-processing",
        description="Extract PDFs",
        body="# Instructions\n\nDo stuff.",
        license="MIT",
        allowed_tools="Read Bash",
        disable_model_invocation=True,
        user_invocable=False,
        context="fork",
        agent="Explore",
        resources=[],
    )
    result = convert_skill(skill)

    assert result.frontmatter["name"] == "pdf-processing"
    assert result.frontmatter["description"] == "Extract PDFs"
    assert result.frontmatter["license"] == "MIT"
    assert result.frontmatter["allowed-tools"] == "Read Bash"
    # Claude-specific fields must be absent
    assert "disable-model-invocation" not in result.frontmatter
    assert "user-invocable" not in result.frontmatter
    assert "context" not in result.frontmatter
    assert "agent" not in result.frontmatter
    assert result.body == "# Instructions\n\nDo stuff."
    assert result.dropped_fields == ["agent", "context", "disable-model-invocation", "user-invocable"]


def test_convert_skill_no_optional_fields():
    skill = Skill(
        name="simple",
        description="Simple skill",
        body="Do things.",
        resources=[],
    )
    result = convert_skill(skill)

    assert result.frontmatter["name"] == "simple"
    assert "license" not in result.frontmatter
    assert "allowed-tools" not in result.frontmatter
    assert result.dropped_fields == []
```

- [ ] **Step 2: Write tests for command converter**

```python
# tests/test_converter/test_command_converter.py
from c2roo.models.command import Command
from c2roo.converter.command_converter import convert_command


def test_convert_command_drops_allowed_tools():
    cmd = Command(
        name="commit",
        description="Create a git commit",
        argument_hint="<optional message>",
        allowed_tools="Bash(git add:*), Bash(git commit:*)",
        body="## Context\n!`git status`\n\nCreate a commit.",
    )
    result = convert_command(cmd)

    assert result.frontmatter["description"] == "Create a git commit"
    assert result.frontmatter["argument-hint"] == "<optional message>"
    assert "allowed-tools" not in result.frontmatter
    assert "!`git status`" in result.body
    assert result.dropped_fields == ["allowed-tools"]


def test_convert_command_no_optional_fields():
    cmd = Command(name="simple", body="Just do it.")
    result = convert_command(cmd)

    assert "description" not in result.frontmatter
    assert "argument-hint" not in result.frontmatter
    assert result.body == "Just do it."
    assert result.dropped_fields == []
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_converter/ -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement skill and command converters**

```python
# src/c2roo/converter/__init__.py
```

```python
# src/c2roo/converter/skill_converter.py
from dataclasses import dataclass, field

from c2roo.models.skill import Skill

CLAUDE_SPECIFIC_FIELDS = ["disable-model-invocation", "user-invocable", "context", "agent"]


@dataclass
class ConvertedSkill:
    frontmatter: dict
    body: str
    name: str
    dropped_fields: list[str] = field(default_factory=list)


def convert_skill(skill: Skill) -> ConvertedSkill:
    """Convert a Skill IR to Roo skill format (cleaned frontmatter)."""
    frontmatter: dict = {
        "name": skill.name,
        "description": skill.description,
    }

    if skill.license:
        frontmatter["license"] = skill.license
    if skill.compatibility:
        frontmatter["compatibility"] = skill.compatibility
    if skill.metadata:
        frontmatter["metadata"] = skill.metadata
    if skill.allowed_tools:
        frontmatter["allowed-tools"] = skill.allowed_tools

    # Track which Claude-specific fields were present and dropped
    dropped = []
    if skill.agent is not None:
        dropped.append("agent")
    if skill.context is not None:
        dropped.append("context")
    if skill.disable_model_invocation is not None:
        dropped.append("disable-model-invocation")
    if skill.user_invocable is not None:
        dropped.append("user-invocable")

    return ConvertedSkill(
        frontmatter=frontmatter,
        body=skill.body,
        name=skill.name,
        dropped_fields=sorted(dropped),
    )
```

```python
# src/c2roo/converter/command_converter.py
from dataclasses import dataclass, field

from c2roo.models.command import Command


@dataclass
class ConvertedCommand:
    frontmatter: dict
    body: str
    name: str
    dropped_fields: list[str] = field(default_factory=list)


def convert_command(cmd: Command) -> ConvertedCommand:
    """Convert a Command IR to Roo slash command format."""
    frontmatter: dict = {}

    if cmd.description:
        frontmatter["description"] = cmd.description
    if cmd.argument_hint:
        frontmatter["argument-hint"] = cmd.argument_hint

    dropped = []
    if cmd.allowed_tools:
        dropped.append("allowed-tools")

    return ConvertedCommand(
        frontmatter=frontmatter,
        body=cmd.body,
        name=cmd.name,
        dropped_fields=sorted(dropped),
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_converter/ -v`
Expected: All 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/c2roo/converter/ tests/test_converter/
git commit -m "feat: add skill and command converters"
```

---

### Task 7: Agent Converter (Agent → Custom Mode + Rules)

**Files:**
- Create: `src/c2roo/converter/agent_converter.py`
- Create: `tests/test_converter/test_agent_converter.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_converter/test_agent_converter.py
from c2roo.models.agent import Agent
from c2roo.converter.agent_converter import convert_agent


def test_convert_agent_to_mode_and_rules():
    agent = Agent(
        name="code-reviewer",
        description="Reviews code for bugs and quality issues",
        body="You are an expert code reviewer. Analyze code for bugs, security issues, and quality problems.\n\nFocus on:\n- Logic errors\n- Security vulnerabilities\n- Performance issues",
        model="sonnet",
        tools=["Read", "Grep", "Glob", "Bash"],
        color="yellow",
    )
    result = convert_agent(agent)

    # Custom mode
    mode = result.mode
    assert mode["slug"] == "code-reviewer"
    assert mode["name"] == "Code Reviewer"
    assert "expert code reviewer" in mode["roleDefinition"]
    assert "read" in mode["groups"]
    assert "command" in mode["groups"]
    # edit should NOT be in groups (no Write/Edit tools)
    assert "edit" not in mode["groups"]

    # Rules file
    assert "expert code reviewer" in result.rules_content
    assert "Originally configured for model: sonnet" in result.rules_content
    assert "Converted from Claude Code agent" in result.rules_content

    assert result.slug == "code-reviewer"


def test_convert_agent_tool_mapping():
    agent = Agent(
        name="full-agent",
        description="Has all tools",
        body="Instructions.",
        tools=["Read", "Grep", "Glob", "LS", "Write", "Edit", "MultiEdit", "Bash", "BashOutput", "KillShell", "WebFetch"],
    )
    result = convert_agent(agent)

    groups = result.mode["groups"]
    assert "read" in groups
    assert "edit" in groups
    assert "command" in groups


def test_convert_agent_humanizes_name():
    agent = Agent(
        name="my-cool-agent",
        description="Does cool stuff",
        body="You are cool.",
    )
    result = convert_agent(agent)
    assert result.mode["name"] == "My Cool Agent"


def test_convert_agent_no_model():
    agent = Agent(
        name="basic",
        description="Basic agent",
        body="Do things.",
    )
    result = convert_agent(agent)
    assert "Originally configured for model" not in result.rules_content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_converter/test_agent_converter.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement agent converter**

```python
# src/c2roo/converter/agent_converter.py
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

# Tools that don't map to a standard group (treated as MCP or ignored)
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
    mode: dict
    rules_content: str
    slug: str


def convert_agent(agent: Agent) -> ConvertedAgent:
    """Convert an Agent IR to a Roo custom mode + rules file."""
    slug = agent.name
    groups = _map_tools_to_groups(agent.tools)

    mode = {
        "slug": slug,
        "name": _humanize_name(slug),
        "description": agent.description,
        "roleDefinition": _extract_role_definition(agent.body),
        "groups": groups,
    }

    # Build rules file content
    lines = [
        f"# {_humanize_name(slug)}",
        "",
        f"> Converted from Claude Code agent: `{agent.name}`",
        "",
        agent.body,
    ]

    # Append metadata footer
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_converter/test_agent_converter.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/c2roo/converter/agent_converter.py tests/test_converter/test_agent_converter.py
git commit -m "feat: add agent-to-custom-mode converter"
```

---

### Task 8: Hook & MCP Converters

**Files:**
- Create: `src/c2roo/converter/hook_converter.py`
- Create: `src/c2roo/converter/mcp_converter.py`
- Create: `tests/test_converter/test_hook_converter.py`
- Create: `tests/test_converter/test_mcp_converter.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_converter/test_hook_converter.py
from c2roo.models.hook import Hook
from c2roo.converter.hook_converter import convert_hooks


def test_convert_hooks_to_guidance():
    hooks = [
        Hook(event="PreToolUse", matcher="Edit|Write", command="python3 hooks/lint.py", timeout=10),
        Hook(event="SessionStart", matcher=None, command="echo starting", timeout=None),
    ]
    result = convert_hooks(hooks)

    assert "## PreToolUse" in result
    assert "Edit|Write" in result
    assert "python3 hooks/lint.py" in result
    assert "## SessionStart" in result
    assert "echo starting" in result
    assert "Converted from Claude Code hooks" in result


def test_convert_empty_hooks():
    result = convert_hooks([])
    assert result == ""
```

```python
# tests/test_converter/test_mcp_converter.py
from pathlib import Path

from c2roo.models.mcp import McpServer
from c2roo.converter.mcp_converter import convert_mcp


def test_convert_mcp_servers():
    servers = {
        "my-server": McpServer(
            name="my-server",
            command="npx",
            args=["-y", "@org/server"],
            env={"KEY": "val"},
        ),
        "remote": McpServer(
            name="remote",
            url="http://localhost:3000/sse",
            headers={"Authorization": "Bearer tok"},
        ),
    }
    install_path = Path("/home/user/.roo")
    result = convert_mcp(servers, install_path)

    assert "my-server" in result
    assert result["my-server"]["command"] == "npx"
    assert result["my-server"]["args"] == ["-y", "@org/server"]
    assert result["my-server"]["env"] == {"KEY": "val"}

    assert "remote" in result
    assert result["remote"]["url"] == "http://localhost:3000/sse"


def test_convert_mcp_resolves_plugin_root():
    servers = {
        "lint": McpServer(
            name="lint",
            command="python3",
            args=["${CLAUDE_PLUGIN_ROOT}/scripts/lint.py"],
            env={"CONFIG": "${CLAUDE_PLUGIN_ROOT}/config.json"},
        ),
    }
    install_path = Path("/home/user/.roo")
    result = convert_mcp(servers, install_path)

    assert "${CLAUDE_PLUGIN_ROOT}" not in str(result["lint"]["args"])
    assert "${CLAUDE_PLUGIN_ROOT}" not in str(result["lint"]["env"])


def test_convert_empty_mcp():
    result = convert_mcp({}, Path("/tmp"))
    assert result == {}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_converter/test_hook_converter.py tests/test_converter/test_mcp_converter.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement hook and MCP converters**

```python
# src/c2roo/converter/hook_converter.py
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

            lines.append(f"**Original command:**")
            lines.append(f"```")
            lines.append(hook.command)
            lines.append(f"```")

            if hook.timeout:
                lines.append(f"*Timeout: {hook.timeout}s*")

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
```

```python
# src/c2roo/converter/mcp_converter.py
from pathlib import Path

from c2roo.models.mcp import McpServer


def _resolve_plugin_root(value: str, install_path: Path) -> str:
    """Replace ${CLAUDE_PLUGIN_ROOT} with the actual install path."""
    return value.replace("${CLAUDE_PLUGIN_ROOT}", str(install_path))


def convert_mcp(servers: dict[str, McpServer], install_path: Path) -> dict:
    """Convert McpServer IRs to a Roo mcp.json-compatible dict."""
    if not servers:
        return {}

    result = {}
    for name, server in servers.items():
        entry: dict = {}

        if server.command:
            entry["command"] = _resolve_plugin_root(server.command, install_path)
        if server.args:
            entry["args"] = [_resolve_plugin_root(a, install_path) for a in server.args]
        if server.env:
            entry["env"] = {k: _resolve_plugin_root(v, install_path) for k, v in server.env.items()}
        if server.url:
            entry["url"] = server.url
        if server.headers:
            entry["headers"] = server.headers
        if server.disabled:
            entry["disabled"] = True
        if server.always_allow:
            entry["alwaysAllow"] = server.always_allow
        if server.timeout:
            entry["timeout"] = server.timeout

        result[name] = entry

    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_converter/ -v`
Expected: All converter tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/c2roo/converter/ tests/test_converter/
git commit -m "feat: add hook and MCP converters"
```

---

### Task 9: Conversion Report

**Files:**
- Create: `src/c2roo/report.py`
- Create: `tests/test_report.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_report.py
from c2roo.report import ConversionReport


def test_report_tracks_entities():
    report = ConversionReport(plugin_name="superpowers")
    report.add_skill("pdf-processing", dropped=["context", "agent"])
    report.add_skill("frontend-design", dropped=[])
    report.add_command("commit", dropped=["allowed-tools"])
    report.add_agent("code-reviewer")
    report.add_hooks(count=2)

    assert report.skill_count == 2
    assert report.command_count == 1
    assert report.agent_count == 1
    assert report.hook_count == 2
    assert report.mcp_count == 0

    assert ("pdf-processing", ["context", "agent"]) in report.skill_drops
    assert ("commit", ["allowed-tools"]) in report.command_drops


def test_report_render_returns_string():
    report = ConversionReport(plugin_name="test")
    report.add_skill("s1", dropped=[])
    output_path = "/home/user/.roo"
    text = report.render(output_path)

    assert "test" in text
    assert "Skills" in text
    assert output_path in text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_report.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement ConversionReport**

```python
# src/c2roo/report.py
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


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
        lines.append(_status(self.agent_count, "Agents" if not self.agent_count else "Agents → custom modes", agent_extra))

        hook_extra = "not enforced" if self.hook_count > 0 else ""
        lines.append(_status(self.hook_count, "Hooks" if not self.hook_count else "Hooks → guidance rules", hook_extra))

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_report.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/c2roo/report.py tests/test_report.py
git commit -m "feat: add conversion report with Rich output"
```

---

### Task 10: Roo Writer (Output to Disk)

**Files:**
- Create: `src/c2roo/writer/__init__.py`
- Create: `src/c2roo/writer/roo_writer.py`
- Create: `tests/test_writer.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_writer.py
import json
from pathlib import Path

import yaml

from c2roo.converter.agent_converter import ConvertedAgent
from c2roo.converter.command_converter import ConvertedCommand
from c2roo.converter.skill_converter import ConvertedSkill
from c2roo.writer.roo_writer import RooWriter


def test_write_skill(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    skill = ConvertedSkill(
        name="pdf-processing",
        frontmatter={"name": "pdf-processing", "description": "Process PDFs"},
        body="# Instructions\nDo stuff.",
        dropped_fields=[],
    )
    source_skill_dir = tmp_path / "source" / "skills" / "pdf-processing"
    source_skill_dir.mkdir(parents=True)
    (source_skill_dir / "SKILL.md").write_text("original")
    (source_skill_dir / "scripts").mkdir()
    (source_skill_dir / "scripts" / "extract.py").write_text("print('hi')")

    writer.write_skill(skill, source_skill_dir)

    output_skill = tmp_path / "skills" / "pdf-processing" / "SKILL.md"
    assert output_skill.exists()
    content = output_skill.read_text()
    assert "name: pdf-processing" in content
    assert "# Instructions" in content

    script = tmp_path / "skills" / "pdf-processing" / "scripts" / "extract.py"
    assert script.exists()


def test_write_command(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    cmd = ConvertedCommand(
        name="commit",
        frontmatter={"description": "Create a commit"},
        body="Do a commit.",
        dropped_fields=[],
    )
    writer.write_command(cmd)

    output = tmp_path / "commands" / "commit.md"
    assert output.exists()
    content = output.read_text()
    assert "description: Create a commit" in content
    assert "Do a commit." in content


def test_write_agent_mode_and_rules(tmp_path):
    # output_root simulates .roo/ inside a project
    output_root = tmp_path / ".roo"
    writer = RooWriter(output_root=output_root, force=False, dry_run=False)
    agent = ConvertedAgent(
        slug="code-reviewer",
        mode={"slug": "code-reviewer", "name": "Code Reviewer", "roleDefinition": "Expert reviewer.", "groups": ["read"]},
        rules_content="# Rules\nReview code.",
    )
    writer.write_agent(agent)

    # Check .roomodes (lives next to .roo/, not inside it)
    roomodes = tmp_path / ".roomodes"
    assert roomodes.exists()
    data = yaml.safe_load(roomodes.read_text())
    assert len(data["customModes"]) == 1
    assert data["customModes"][0]["slug"] == "code-reviewer"

    # Check rules file (inside .roo/)
    rules = output_root / "rules-code-reviewer" / "converted-agent.md"
    assert rules.exists()
    assert "Review code." in rules.read_text()


def test_write_agent_merges_roomodes(tmp_path):
    # Pre-existing .roomodes (lives at project root, next to .roo/)
    roomodes = tmp_path / ".roomodes"
    roomodes.write_text(yaml.dump({"customModes": [{"slug": "existing", "name": "Existing"}]}))

    output_root = tmp_path / ".roo"
    writer = RooWriter(output_root=output_root, force=False, dry_run=False)
    agent = ConvertedAgent(
        slug="new-mode",
        mode={"slug": "new-mode", "name": "New Mode", "roleDefinition": "New.", "groups": ["read"]},
        rules_content="# Rules",
    )
    writer.write_agent(agent)

    data = yaml.safe_load(roomodes.read_text())
    assert len(data["customModes"]) == 2
    slugs = [m["slug"] for m in data["customModes"]]
    assert "existing" in slugs
    assert "new-mode" in slugs


def test_write_agent_skips_duplicate_slug(tmp_path):
    roomodes = tmp_path / ".roomodes"
    roomodes.write_text(yaml.dump({"customModes": [{"slug": "dupe", "name": "Dupe"}]}))

    output_root = tmp_path / ".roo"
    writer = RooWriter(output_root=output_root, force=False, dry_run=False)
    agent = ConvertedAgent(
        slug="dupe",
        mode={"slug": "dupe", "name": "Dupe v2", "roleDefinition": "New.", "groups": ["read"]},
        rules_content="# Rules",
    )
    writer.write_agent(agent)

    data = yaml.safe_load(roomodes.read_text())
    assert len(data["customModes"]) == 1
    assert data["customModes"][0]["name"] == "Dupe"  # Original preserved


def test_write_hooks(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    writer.write_hooks("# Hook guidance content\n")

    output = tmp_path / "rules" / "converted-hooks-guidance.md"
    assert output.exists()
    assert "Hook guidance" in output.read_text()


def test_write_mcp(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    mcp_data = {"my-server": {"command": "npx", "args": ["-y", "@org/server"]}}
    writer.write_mcp(mcp_data)

    output = tmp_path / "mcp.json"
    assert output.exists()
    data = json.loads(output.read_text())
    assert "my-server" in data["mcpServers"]


def test_write_mcp_merges_existing(tmp_path):
    mcp_file = tmp_path / "mcp.json"
    mcp_file.write_text(json.dumps({"mcpServers": {"existing": {"url": "http://old"}}}))

    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    writer.write_mcp({"new-server": {"command": "npx", "args": []}})

    data = json.loads(mcp_file.read_text())
    assert "existing" in data["mcpServers"]
    assert "new-server" in data["mcpServers"]


def test_dry_run_writes_nothing(tmp_path):
    writer = RooWriter(output_root=tmp_path, force=False, dry_run=True)
    cmd = ConvertedCommand(
        name="test",
        frontmatter={"description": "Test"},
        body="Body.",
        dropped_fields=[],
    )
    writer.write_command(cmd)

    assert not (tmp_path / "commands" / "test.md").exists()


def test_conflict_without_force_raises(tmp_path):
    # Pre-create the file
    (tmp_path / "commands").mkdir(parents=True)
    (tmp_path / "commands" / "conflict.md").write_text("existing")

    writer = RooWriter(output_root=tmp_path, force=False, dry_run=False)
    cmd = ConvertedCommand(
        name="conflict",
        frontmatter={"description": "New"},
        body="New body.",
        dropped_fields=[],
    )
    try:
        writer.write_command(cmd)
        assert False, "Should have raised"
    except FileExistsError:
        pass
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_writer.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement RooWriter**

```python
# src/c2roo/writer/__init__.py
from c2roo.writer.roo_writer import RooWriter

__all__ = ["RooWriter"]
```

```python
# src/c2roo/writer/roo_writer.py
import json
import shutil
from pathlib import Path

import yaml

from c2roo.converter.agent_converter import ConvertedAgent
from c2roo.converter.command_converter import ConvertedCommand
from c2roo.converter.skill_converter import ConvertedSkill


def _render_markdown(frontmatter: dict, body: str) -> str:
    """Render YAML frontmatter + markdown body into a complete file."""
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{yaml_str}\n---\n\n{body}\n"


class RooWriter:
    def __init__(self, output_root: Path, force: bool, dry_run: bool) -> None:
        self.output_root = output_root
        self.force = force
        self.dry_run = dry_run
        self.written_files: list[Path] = []
        self.skipped_files: list[tuple[Path, str]] = []

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to a file, respecting force/dry_run flags."""
        if self.dry_run:
            self.written_files.append(path)
            return

        if path.exists() and not self.force:
            raise FileExistsError(f"File already exists (use --force to overwrite): {path}")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.written_files.append(path)

    def write_skill(self, skill: ConvertedSkill, source_dir: Path) -> None:
        """Write a converted skill directory."""
        dest_dir = self.output_root / "skills" / skill.name

        # Write SKILL.md
        content = _render_markdown(skill.frontmatter, skill.body)
        self._write_file(dest_dir / "SKILL.md", content)

        # Copy resource files
        if not self.dry_run:
            for item in source_dir.iterdir():
                if item.name == "SKILL.md":
                    continue
                dest = dest_dir / item.name
                if item.is_dir():
                    if dest.exists() and self.force:
                        shutil.rmtree(dest)
                    elif dest.exists():
                        self.skipped_files.append((dest, "directory exists"))
                        continue
                    shutil.copytree(item, dest)
                else:
                    self._write_file(dest, item.read_text(encoding="utf-8"))

    def write_command(self, cmd: ConvertedCommand) -> None:
        """Write a converted slash command."""
        path = self.output_root / "commands" / f"{cmd.name}.md"
        content = _render_markdown(cmd.frontmatter, cmd.body)
        self._write_file(path, content)

    def write_agent(self, agent: ConvertedAgent) -> None:
        """Write a converted agent as custom mode entry + rules file."""
        # Write/merge .roomodes (lives next to .roo/, not inside it)
        roomodes_path = self.output_root.parent / ".roomodes"

        if not self.dry_run:
            existing_modes = []
            if roomodes_path.exists():
                data = yaml.safe_load(roomodes_path.read_text(encoding="utf-8")) or {}
                existing_modes = data.get("customModes", [])

            # Skip if slug already exists
            existing_slugs = {m["slug"] for m in existing_modes}
            if agent.slug not in existing_slugs:
                existing_modes.append(agent.mode)
                roomodes_path.parent.mkdir(parents=True, exist_ok=True)
                roomodes_path.write_text(
                    yaml.dump({"customModes": existing_modes}, default_flow_style=False, sort_keys=False),
                    encoding="utf-8",
                )
            else:
                self.skipped_files.append((roomodes_path, f"mode slug '{agent.slug}' already exists"))

        self.written_files.append(roomodes_path)

        # Write rules file
        rules_path = self.output_root / f"rules-{agent.slug}" / "converted-agent.md"
        self._write_file(rules_path, agent.rules_content + "\n")

    def write_hooks(self, content: str) -> None:
        """Write converted hooks guidance."""
        if not content:
            return
        path = self.output_root / "rules" / "converted-hooks-guidance.md"
        self._write_file(path, content)

    def write_mcp(self, mcp_data: dict) -> None:
        """Write/merge MCP server configuration."""
        if not mcp_data:
            return

        path = self.output_root / "mcp.json"

        if not self.dry_run:
            existing = {}
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                existing = data.get("mcpServers", {})

            existing.update(mcp_data)

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"mcpServers": existing}, indent=2) + "\n",
                encoding="utf-8",
            )

        self.written_files.append(path)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_writer.py -v`
Expected: All 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/c2roo/writer/ tests/test_writer.py
git commit -m "feat: add RooWriter with merge, conflict, and dry-run support"
```

---

### Task 11: Local Source & Convert Command

**Files:**
- Create: `src/c2roo/sources/__init__.py`
- Create: `src/c2roo/sources/local_source.py`
- Modify: `src/c2roo/cli.py`
- Create: `tests/test_sources/__init__.py`
- Create: `tests/test_sources/test_local_source.py`
- Create: `tests/test_cli_convert.py`

- [ ] **Step 1: Write tests for local source and convert CLI**

```python
# tests/test_sources/test_local_source.py
from pathlib import Path

import pytest

from c2roo.sources.local_source import resolve_local

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_resolve_local_valid():
    path = resolve_local(str(FIXTURES))
    assert path == FIXTURES


def test_resolve_local_invalid():
    with pytest.raises(FileNotFoundError, match="Not a Claude Code plugin"):
        resolve_local("/nonexistent/path")


def test_resolve_local_missing_manifest():
    with pytest.raises(FileNotFoundError, match="plugin.json"):
        resolve_local(str(FIXTURES.parent))  # fixtures/ dir has no .claude-plugin/
```

```python
# tests/test_cli_convert.py
from pathlib import Path

from click.testing import CliRunner

from c2roo.cli import main

FIXTURES = Path(__file__).parent / "fixtures" / "sample-plugin"


def test_convert_requires_target_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["convert", str(FIXTURES)])
    assert result.exit_code != 0
    assert "Must specify --global or --project" in result.output


def test_convert_local_plugin(tmp_path):
    runner = CliRunner()
    # Use --project with a custom working directory
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["convert", str(FIXTURES), "--project", "--force"])
        assert result.exit_code == 0
        assert "Conversion Report" in result.output
        assert "Skills" in result.output

        # Verify files were written
        assert (Path(".roo") / "skills" / "pdf-processing" / "SKILL.md").exists()
        assert (Path(".roo") / "commands" / "commit.md").exists()


def test_convert_dry_run(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["convert", str(FIXTURES), "--project", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        # Nothing should be written
        assert not (Path(".roo") / "skills").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_sources/test_local_source.py tests/test_cli_convert.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement local source**

```python
# src/c2roo/sources/__init__.py
```

```python
# src/c2roo/sources/local_source.py
from pathlib import Path


def resolve_local(source: str) -> Path:
    """Validate a local path as a Claude Code plugin directory."""
    path = Path(source).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Not a Claude Code plugin: path does not exist: {path}")

    manifest = path / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        raise FileNotFoundError(f"Not a Claude Code plugin: expected {manifest}")

    return path
```

- [ ] **Step 4: Wire up the convert command in cli.py**

Replace the `convert` function in `src/c2roo/cli.py`:

```python
@main.command()
@click.argument("source")
@click.option("--global", "target_global", is_flag=True, default=False, help="Install to ~/.roo/ (global).")
@click.option("--project", "target_project", is_flag=True, default=False, help="Install to .roo/ (project).")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be converted.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files.")
def convert(source, target_global, target_project, dry_run, force):
    """Convert a Claude Code plugin from a local path or git URL."""
    if not target_global and not target_project:
        raise click.UsageError("Must specify --global or --project.")
    if target_global and target_project:
        raise click.UsageError("Cannot specify both --global and --project.")

    from pathlib import Path

    from c2roo.converter.agent_converter import convert_agent
    from c2roo.converter.command_converter import convert_command
    from c2roo.converter.hook_converter import convert_hooks
    from c2roo.converter.mcp_converter import convert_mcp
    from c2roo.converter.skill_converter import convert_skill
    from c2roo.parser.plugin_parser import parse_plugin
    from c2roo.report import ConversionReport
    from c2roo.sources.local_source import resolve_local
    from c2roo.writer.roo_writer import RooWriter

    # Resolve source
    # TODO: add git source support in Task 12
    plugin_path = resolve_local(source)

    # Determine output root
    if target_global:
        output_root = Path.home() / ".roo"
    else:
        output_root = Path.cwd() / ".roo"

    if dry_run:
        click.echo("[DRY RUN] No files will be written.\n")

    # Parse
    plugin = parse_plugin(plugin_path)

    # Convert & write
    writer = RooWriter(output_root=output_root, force=force, dry_run=dry_run)
    report = ConversionReport(plugin_name=plugin.metadata.name)

    # Skills
    for skill_ir in plugin.skills:
        converted = convert_skill(skill_ir)
        source_dir = plugin_path / "skills" / skill_ir.name
        writer.write_skill(converted, source_dir)
        report.add_skill(converted.name, dropped=converted.dropped_fields)

    # Commands
    for cmd_ir in plugin.commands:
        converted = convert_command(cmd_ir)
        writer.write_command(converted)
        report.add_command(converted.name, dropped=converted.dropped_fields)

    # Agents
    for agent_ir in plugin.agents:
        converted = convert_agent(agent_ir)
        writer.write_agent(converted)
        report.add_agent(agent_ir.name)

    # Hooks
    if plugin.hooks:
        hooks_content = convert_hooks(plugin.hooks)
        writer.write_hooks(hooks_content)
        report.add_hooks(count=len(plugin.hooks))

    # MCP
    if plugin.mcp_servers:
        mcp_data = convert_mcp(plugin.mcp_servers, output_root)
        writer.write_mcp(mcp_data)
        report.add_mcp(count=len(plugin.mcp_servers))

    # Print report
    report.print(str(output_root))
```

Also add the required import at the top of `cli.py`:

```python
import click
```

(Already present from Task 1.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_sources/ tests/test_cli_convert.py -v`
Expected: All tests PASS

- [ ] **Step 6: Run the full convert manually as a smoke test**

Run: `cd /tmp && uv run --project /c/Users/bitto/projects/c2roo c2roo convert /c/Users/bitto/projects/c2roo/tests/fixtures/sample-plugin --project --force`
Expected: Conversion report printed, files created in `/tmp/.roo/`

- [ ] **Step 7: Commit**

```bash
git add src/c2roo/sources/ src/c2roo/cli.py tests/test_sources/ tests/test_cli_convert.py
git commit -m "feat: wire up convert command with local source support"
```

---

### Task 12: Git Source

**Files:**
- Create: `src/c2roo/sources/git_source.py`
- Create: `tests/test_sources/test_git_source.py`
- Modify: `src/c2roo/cli.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_sources/test_git_source.py
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from c2roo.sources.git_source import clone_repo, is_git_url


def test_is_git_url_https():
    assert is_git_url("https://github.com/org/repo.git") is True


def test_is_git_url_ssh():
    assert is_git_url("git@github.com:org/repo.git") is True


def test_is_git_url_local_path():
    assert is_git_url("/home/user/code") is False
    assert is_git_url("C:\\Users\\code") is False
    assert is_git_url("./relative/path") is False


def test_clone_repo_calls_git(tmp_path):
    """Test that clone_repo invokes git clone with correct arguments."""
    with patch("c2roo.sources.git_source.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        result = clone_repo("https://github.com/org/repo.git", dest=tmp_path / "cloned", sha="abc123")

        calls = mock_run.call_args_list
        # Should have clone call then checkout call
        assert len(calls) == 2
        clone_args = calls[0][0][0]
        assert "git" in clone_args
        assert "clone" in clone_args
        assert "https://github.com/org/repo.git" in clone_args

        checkout_args = calls[1][0][0]
        assert "checkout" in checkout_args
        assert "abc123" in checkout_args


def test_clone_repo_no_sha(tmp_path):
    with patch("c2roo.sources.git_source.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        clone_repo("https://github.com/org/repo.git", dest=tmp_path / "cloned")

        calls = mock_run.call_args_list
        assert len(calls) == 1  # Only clone, no checkout
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_sources/test_git_source.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement git source**

```python
# src/c2roo/sources/git_source.py
import subprocess
from pathlib import Path


def is_git_url(source: str) -> bool:
    """Check if a source string looks like a git URL."""
    return (
        source.startswith("https://")
        or source.startswith("http://")
        or source.startswith("git@")
        or source.startswith("git://")
    )


def check_git_available() -> None:
    """Raise RuntimeError if git is not on PATH."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        raise RuntimeError("git is not installed or not on PATH. Install git to use git sources.")


def clone_repo(url: str, dest: Path, sha: str | None = None, subdir: str | None = None) -> Path:
    """Clone a git repository and optionally checkout a specific SHA.

    Returns the path to the plugin directory (may be a subdirectory).
    """
    subprocess.run(
        ["git", "clone", "--depth", "1", url, str(dest)],
        check=True,
        capture_output=True,
    )

    if sha:
        # Fetch the specific commit (depth=1 clone may not have it)
        subprocess.run(
            ["git", "-C", str(dest), "fetch", "origin", sha, "--depth", "1"],
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(dest), "checkout", sha],
            check=True,
            capture_output=True,
        )

    if subdir:
        return dest / subdir
    return dest
```

- [ ] **Step 4: Update cli.py convert command to support git URLs**

In `src/c2roo/cli.py`, update the source resolution in the `convert` function. Replace the line:

```python
    # TODO: add git source support in Task 12
    plugin_path = resolve_local(source)
```

With:

```python
    import tempfile

    from c2roo.sources.git_source import is_git_url

    temp_dir = None
    if is_git_url(source):
        from c2roo.sources.git_source import check_git_available, clone_repo

        check_git_available()
        temp_dir = tempfile.mkdtemp(prefix="c2roo-")
        plugin_path = clone_repo(source, dest=Path(temp_dir) / "plugin")
    else:
        plugin_path = resolve_local(source)
```

And at the end of the function, after the report, add cleanup:

```python
    # Cleanup temp directory
    if temp_dir:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_sources/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/c2roo/sources/git_source.py src/c2roo/cli.py tests/test_sources/test_git_source.py
git commit -m "feat: add git source cloning for convert command"
```

---

### Task 13: Marketplace Registry & Browse/List/Add/Remove

**Files:**
- Create: `src/c2roo/sources/marketplace.py`
- Create: `tests/test_sources/test_marketplace.py`
- Modify: `src/c2roo/cli.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_sources/test_marketplace.py
from pathlib import Path

import yaml

from c2roo.sources.marketplace import (
    MarketplaceRegistry,
    DEFAULT_MARKETPLACES,
)


def test_default_marketplaces():
    assert len(DEFAULT_MARKETPLACES) >= 2
    names = [m["name"] for m in DEFAULT_MARKETPLACES]
    assert "official" in names
    assert "community" in names


def test_registry_init_creates_config(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    assert config_path.exists()
    data = yaml.safe_load(config_path.read_text())
    assert len(data["marketplaces"]) >= 2


def test_registry_list(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    sources = registry.list_sources()
    assert len(sources) >= 2
    assert sources[0]["name"] == "official"


def test_registry_add(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    registry.add_source("custom", "my-org/my-marketplace", "Custom plugins")

    sources = registry.list_sources()
    names = [s["name"] for s in sources]
    assert "custom" in names


def test_registry_add_duplicate_raises(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    try:
        registry.add_source("official", "other/repo", "Duplicate")
        assert False, "Should have raised"
    except ValueError as e:
        assert "already exists" in str(e)


def test_registry_remove(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()
    registry.add_source("custom", "my-org/repo", "Temp")

    registry.remove_source("custom")

    names = [s["name"] for s in registry.list_sources()]
    assert "custom" not in names


def test_registry_remove_nonexistent_raises(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    try:
        registry.remove_source("nonexistent")
        assert False, "Should have raised"
    except ValueError as e:
        assert "not found" in str(e)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_sources/test_marketplace.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement marketplace registry**

```python
# src/c2roo/sources/marketplace.py
import json
import subprocess
import tempfile
import time
from pathlib import Path

import yaml

DEFAULT_MARKETPLACES = [
    {
        "name": "official",
        "repo": "anthropics/claude-plugins-official",
        "description": "Official Anthropic plugins",
    },
    {
        "name": "community",
        "repo": "anthropics/claude-plugins-community",
        "description": "Community-submitted plugins",
    },
]

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "c2roo" / "marketplaces.yaml"
CACHE_DIR = Path.home() / ".cache" / "c2roo"
CACHE_TTL_SECONDS = 3600  # 1 hour


class MarketplaceRegistry:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self.config_path = config_path

    def ensure_config(self) -> None:
        """Create default config if it doesn't exist."""
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(
                yaml.dump({"marketplaces": DEFAULT_MARKETPLACES}, default_flow_style=False, sort_keys=False),
                encoding="utf-8",
            )

    def _load(self) -> dict:
        self.ensure_config()
        return yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {"marketplaces": []}

    def _save(self, data: dict) -> None:
        self.config_path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

    def list_sources(self) -> list[dict]:
        return self._load().get("marketplaces", [])

    def add_source(self, name: str, repo: str, description: str) -> None:
        data = self._load()
        existing_names = {m["name"] for m in data.get("marketplaces", [])}
        if name in existing_names:
            raise ValueError(f"Marketplace '{name}' already exists.")
        data["marketplaces"].append({"name": name, "repo": repo, "description": description})
        self._save(data)

    def remove_source(self, name: str) -> None:
        data = self._load()
        original_len = len(data.get("marketplaces", []))
        data["marketplaces"] = [m for m in data.get("marketplaces", []) if m["name"] != name]
        if len(data["marketplaces"]) == original_len:
            raise ValueError(f"Marketplace '{name}' not found.")
        self._save(data)

    def fetch_marketplace_json(self, source: dict) -> list[dict]:
        """Fetch and parse marketplace.json from a marketplace source.

        Uses a local cache with 1-hour TTL.
        """
        repo = source["repo"]
        name = source["name"]

        # Check cache
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{name}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < CACHE_TTL_SECONDS:
                return json.loads(cache_file.read_text(encoding="utf-8"))

        # Clone marketplace repo (shallow) to temp dir
        temp_dir = tempfile.mkdtemp(prefix="c2roo-mkt-")
        try:
            url = f"https://github.com/{repo}.git"
            subprocess.run(
                ["git", "clone", "--depth", "1", url, temp_dir],
                check=True,
                capture_output=True,
            )

            manifest_path = Path(temp_dir) / ".claude-plugin" / "marketplace.json"
            if not manifest_path.exists():
                return []

            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            plugins = data.get("plugins", [])

            # Cache
            cache_file.write_text(json.dumps(plugins), encoding="utf-8")

            return plugins
        except subprocess.CalledProcessError:
            return []
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def search_plugin(self, plugin_name: str, source_filter: str | None = None) -> tuple[dict, dict] | None:
        """Search marketplaces for a plugin by name.

        Returns (plugin_entry, marketplace_source) or None.
        """
        sources = self.list_sources()
        if source_filter:
            sources = [s for s in sources if s["name"] == source_filter]

        for source in sources:
            plugins = self.fetch_marketplace_json(source)
            for plugin in plugins:
                if plugin.get("name") == plugin_name:
                    return plugin, source

        return None
```

- [ ] **Step 4: Wire up marketplace CLI commands in cli.py**

Replace the four marketplace command stubs in `src/c2roo/cli.py`:

```python
@marketplace.command("browse")
@click.option("--source", default=None, help="Filter to a specific marketplace source.")
def marketplace_browse(source):
    """List plugins from registered marketplaces."""
    from rich.console import Console
    from rich.table import Table

    from c2roo.sources.marketplace import MarketplaceRegistry

    registry = MarketplaceRegistry()
    sources = registry.list_sources()
    if source:
        sources = [s for s in sources if s["name"] == source]

    console = Console()
    table = Table(title="Available Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Source", style="green")

    for src in sources:
        try:
            plugins = registry.fetch_marketplace_json(src)
            for plugin in plugins:
                table.add_row(plugin.get("name", "?"), plugin.get("description", ""), src["name"])
        except Exception as e:
            console.print(f"[yellow]Warning: could not fetch {src['name']}: {e}[/yellow]")

    console.print(table)


@marketplace.command("add")
@click.argument("repo")
@click.option("--name", required=True, help="Short name for this marketplace.")
@click.option("--description", default="", help="Description of this marketplace.")
def marketplace_add(repo, name, description):
    """Register a new marketplace source (owner/repo format)."""
    from c2roo.sources.marketplace import MarketplaceRegistry

    registry = MarketplaceRegistry()
    registry.add_source(name, repo, description)
    click.echo(f"Added marketplace '{name}' ({repo})")


@marketplace.command("list")
def marketplace_list():
    """Show registered marketplace sources."""
    from rich.console import Console
    from rich.table import Table

    from c2roo.sources.marketplace import MarketplaceRegistry

    registry = MarketplaceRegistry()
    sources = registry.list_sources()

    console = Console()
    table = Table(title="Registered Marketplaces")
    table.add_column("Name", style="cyan")
    table.add_column("Repo", style="green")
    table.add_column("Description")

    for src in sources:
        table.add_row(src["name"], src.get("repo", ""), src.get("description", ""))

    console.print(table)


@marketplace.command("remove")
@click.argument("name")
def marketplace_remove(name):
    """Remove a marketplace source."""
    from c2roo.sources.marketplace import MarketplaceRegistry

    registry = MarketplaceRegistry()
    registry.remove_source(name)
    click.echo(f"Removed marketplace '{name}'")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_sources/test_marketplace.py -v`
Expected: All 7 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/c2roo/sources/marketplace.py src/c2roo/cli.py tests/test_sources/test_marketplace.py
git commit -m "feat: add marketplace registry with browse, add, list, remove"
```

---

### Task 14: Install Command (Marketplace → Convert Pipeline)

**Files:**
- Modify: `src/c2roo/cli.py`
- Create: `tests/test_cli_install.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_cli_install.py
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from c2roo.cli import main


def test_install_requires_target_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["install", "some-plugin"])
    assert result.exit_code != 0
    assert "Must specify --global or --project" in result.output


@patch("c2roo.cli.MarketplaceRegistry")
def test_install_plugin_not_found(mock_registry_cls):
    mock_registry = MagicMock()
    mock_registry.search_plugin.return_value = None
    mock_registry_cls.return_value = mock_registry

    runner = CliRunner()
    result = runner.invoke(main, ["install", "nonexistent", "--project"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli_install.py -v`
Expected: FAIL (the `install` command still prints "Not yet implemented")

- [ ] **Step 3: Implement the install command**

Replace the `install` function in `src/c2roo/cli.py`:

```python
@main.command()
@click.argument("plugin_name")
@click.option("--global", "target_global", is_flag=True, default=False, help="Install to ~/.roo/ (global).")
@click.option("--project", "target_project", is_flag=True, default=False, help="Install to .roo/ (project).")
@click.option("--source", default=None, help="Which marketplace to search.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be converted.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files.")
def install(plugin_name, target_global, target_project, source, dry_run, force):
    """Install a plugin from a marketplace, converting to Roo format."""
    if not target_global and not target_project:
        raise click.UsageError("Must specify --global or --project.")
    if target_global and target_project:
        raise click.UsageError("Cannot specify both --global and --project.")

    import shutil
    import tempfile
    from pathlib import Path

    from c2roo.converter.agent_converter import convert_agent
    from c2roo.converter.command_converter import convert_command
    from c2roo.converter.hook_converter import convert_hooks
    from c2roo.converter.mcp_converter import convert_mcp
    from c2roo.converter.skill_converter import convert_skill
    from c2roo.parser.plugin_parser import parse_plugin
    from c2roo.report import ConversionReport
    from c2roo.sources.git_source import check_git_available, clone_repo
    from c2roo.sources.marketplace import MarketplaceRegistry
    from c2roo.writer.roo_writer import RooWriter

    check_git_available()

    registry = MarketplaceRegistry()
    result = registry.search_plugin(plugin_name, source_filter=source)

    if result is None:
        raise click.ClickException(f"Plugin '{plugin_name}' not found in any registered marketplace.")

    plugin_entry, mkt_source = result
    click.echo(f"Found '{plugin_name}' in marketplace '{mkt_source['name']}'")

    # Resolve source
    temp_dir = tempfile.mkdtemp(prefix="c2roo-")
    try:
        plugin_source = plugin_entry.get("source")

        if isinstance(plugin_source, str):
            # Relative path — need to clone the marketplace repo first
            mkt_repo_url = f"https://github.com/{mkt_source['repo']}.git"
            mkt_dir = Path(temp_dir) / "marketplace"
            clone_repo(mkt_repo_url, dest=mkt_dir)
            plugin_path = mkt_dir / plugin_source
        elif isinstance(plugin_source, dict):
            source_type = plugin_source.get("source")
            if source_type == "url":
                url = plugin_source["url"]
                sha = plugin_source.get("sha")
                plugin_path = clone_repo(url, dest=Path(temp_dir) / "plugin", sha=sha)
            elif source_type == "git-subdir":
                repo_url = plugin_source["url"]
                if not repo_url.startswith("http"):
                    repo_url = f"https://github.com/{repo_url}.git"
                sha = plugin_source.get("sha")
                subdir = plugin_source.get("path")
                plugin_path = clone_repo(repo_url, dest=Path(temp_dir) / "plugin", sha=sha, subdir=subdir)
            else:
                raise click.ClickException(f"Unknown source type: {source_type}")
        else:
            raise click.ClickException(f"Invalid source format for plugin '{plugin_name}'")

        if not (plugin_path / ".claude-plugin" / "plugin.json").exists():
            raise click.ClickException(f"Downloaded plugin has no .claude-plugin/plugin.json")

        # Determine output root
        if target_global:
            output_root = Path.home() / ".roo"
        else:
            output_root = Path.cwd() / ".roo"

        if dry_run:
            click.echo("[DRY RUN] No files will be written.\n")

        # Parse → Convert → Write (same pipeline as convert command)
        plugin = parse_plugin(plugin_path)
        writer = RooWriter(output_root=output_root, force=force, dry_run=dry_run)
        report = ConversionReport(plugin_name=plugin.metadata.name)

        for skill_ir in plugin.skills:
            converted = convert_skill(skill_ir)
            source_dir = plugin_path / "skills" / skill_ir.name
            writer.write_skill(converted, source_dir)
            report.add_skill(converted.name, dropped=converted.dropped_fields)

        for cmd_ir in plugin.commands:
            converted = convert_command(cmd_ir)
            writer.write_command(converted)
            report.add_command(converted.name, dropped=converted.dropped_fields)

        for agent_ir in plugin.agents:
            converted = convert_agent(agent_ir)
            writer.write_agent(converted)
            report.add_agent(agent_ir.name)

        if plugin.hooks:
            hooks_content = convert_hooks(plugin.hooks)
            writer.write_hooks(hooks_content)
            report.add_hooks(count=len(plugin.hooks))

        if plugin.mcp_servers:
            mcp_data = convert_mcp(plugin.mcp_servers, output_root)
            writer.write_mcp(mcp_data)
            report.add_mcp(count=len(plugin.mcp_servers))

        report.print(str(output_root))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli_install.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/c2roo/cli.py tests/test_cli_install.py
git commit -m "feat: implement install command with marketplace lookup and conversion"
```

---

### Task 15: Refactor Convert Pipeline into Shared Function

The `convert` and `install` commands share the same parse→convert→write pipeline. Extract it to avoid duplication.

**Files:**
- Modify: `src/c2roo/cli.py`

- [ ] **Step 1: Extract shared pipeline function**

Add this function to `src/c2roo/cli.py` (above the command definitions):

```python
def _run_conversion(plugin_path: Path, output_root: Path, force: bool, dry_run: bool) -> None:
    """Shared parse → convert → write pipeline."""
    from c2roo.converter.agent_converter import convert_agent
    from c2roo.converter.command_converter import convert_command
    from c2roo.converter.hook_converter import convert_hooks
    from c2roo.converter.mcp_converter import convert_mcp
    from c2roo.converter.skill_converter import convert_skill
    from c2roo.parser.plugin_parser import parse_plugin
    from c2roo.report import ConversionReport
    from c2roo.writer.roo_writer import RooWriter

    plugin = parse_plugin(plugin_path)
    writer = RooWriter(output_root=output_root, force=force, dry_run=dry_run)
    report = ConversionReport(plugin_name=plugin.metadata.name)

    for skill_ir in plugin.skills:
        converted = convert_skill(skill_ir)
        source_dir = plugin_path / "skills" / skill_ir.name
        writer.write_skill(converted, source_dir)
        report.add_skill(converted.name, dropped=converted.dropped_fields)

    for cmd_ir in plugin.commands:
        converted = convert_command(cmd_ir)
        writer.write_command(converted)
        report.add_command(converted.name, dropped=converted.dropped_fields)

    for agent_ir in plugin.agents:
        converted = convert_agent(agent_ir)
        writer.write_agent(converted)
        report.add_agent(agent_ir.name)

    if plugin.hooks:
        hooks_content = convert_hooks(plugin.hooks)
        writer.write_hooks(hooks_content)
        report.add_hooks(count=len(plugin.hooks))

    if plugin.mcp_servers:
        mcp_data = convert_mcp(plugin.mcp_servers, output_root)
        writer.write_mcp(mcp_data)
        report.add_mcp(count=len(plugin.mcp_servers))

    report.print(str(output_root))
```

- [ ] **Step 2: Simplify convert and install commands to use it**

Replace the body of `convert` (after flag validation and source resolution) with:

```python
    if dry_run:
        click.echo("[DRY RUN] No files will be written.\n")
    _run_conversion(plugin_path, output_root, force, dry_run)
    if temp_dir:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
```

Replace the pipeline section of `install` (after plugin_path is resolved, before the finally block) with:

```python
        if dry_run:
            click.echo("[DRY RUN] No files will be written.\n")
        _run_conversion(plugin_path, output_root, force, dry_run)
```

- [ ] **Step 3: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests PASS (no behavior change, just deduplication)

- [ ] **Step 4: Commit**

```bash
git add src/c2roo/cli.py
git commit -m "refactor: extract shared conversion pipeline from convert and install"
```

---

### Task 16: End-to-End Integration Test

**Files:**
- Create: `tests/test_e2e.py`

- [ ] **Step 1: Write end-to-end test**

```python
# tests/test_e2e.py
import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from c2roo.cli import main

FIXTURES = Path(__file__).parent / "fixtures" / "sample-plugin"


def test_full_conversion_pipeline(tmp_path):
    """End-to-end: convert the sample plugin and verify all outputs."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["convert", str(FIXTURES), "--project", "--force"])
        assert result.exit_code == 0, f"CLI failed: {result.output}"

        roo = Path(".roo")

        # Skills
        skill_md = roo / "skills" / "pdf-processing" / "SKILL.md"
        assert skill_md.exists()
        content = skill_md.read_text()
        assert "name: pdf-processing" in content
        assert "disable-model-invocation" not in content  # Claude-specific removed
        assert "context" not in content.split("---")[1]  # Not in frontmatter
        assert "PyPDF2" in content  # Body preserved

        # Skill resources copied
        assert (roo / "skills" / "pdf-processing" / "scripts" / "extract.py").exists()

        # Commands
        cmd = roo / "commands" / "commit.md"
        assert cmd.exists()
        cmd_content = cmd.read_text()
        assert "description: Create a git commit" in cmd_content
        assert "allowed-tools" not in cmd_content  # Dropped
        assert "!`git status`" in cmd_content  # Dynamic context preserved

        # Agents → Custom Modes + Rules (.roomodes lives at project root, next to .roo/)
        roomodes = Path(".roomodes")
        assert roomodes.exists()
        modes_data = yaml.safe_load(roomodes.read_text())
        assert len(modes_data["customModes"]) == 1
        mode = modes_data["customModes"][0]
        assert mode["slug"] == "code-reviewer"
        assert mode["name"] == "Code Reviewer"
        assert "read" in mode["groups"]
        assert "command" in mode["groups"]

        rules_file = roo / "rules-code-reviewer" / "converted-agent.md"
        assert rules_file.exists()
        rules_content = rules_file.read_text()
        assert "expert code reviewer" in rules_content
        assert "Originally configured for model: sonnet" in rules_content

        # Hooks → Guidance
        hooks_guidance = roo / "rules" / "converted-hooks-guidance.md"
        assert hooks_guidance.exists()
        hooks_content = hooks_guidance.read_text()
        assert "PreToolUse" in hooks_content
        assert "Edit|Write|MultiEdit" in hooks_content
        assert "lint.py" in hooks_content
        assert "SessionStart" in hooks_content

        # MCP
        mcp = roo / "mcp.json"
        assert mcp.exists()
        mcp_data = json.loads(mcp.read_text())
        assert "my-server" in mcp_data["mcpServers"]
        assert "remote-server" in mcp_data["mcpServers"]

        # Report output
        assert "Conversion Report" in result.output
        assert "sample-plugin" in result.output
```

- [ ] **Step 2: Run the test**

Run: `uv run pytest tests/test_e2e.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_e2e.py
git commit -m "test: add end-to-end integration test for full conversion pipeline"
```

---

### Task 17: Final Polish — README and Entry Point Verification

**Files:**
- Verify: `pyproject.toml` entry point works
- Run: full test suite

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -v --tb=short`
Expected: All tests PASS

- [ ] **Step 2: Verify CLI entry point**

Run: `uv run c2roo --help`
Expected: Shows usage with `marketplace`, `convert`, `install` commands

Run: `uv run c2roo marketplace --help`
Expected: Shows `browse`, `add`, `list`, `remove` subcommands

Run: `uv run c2roo convert --help`
Expected: Shows `SOURCE`, `--global`, `--project`, `--dry-run`, `--force`

Run: `uv run c2roo install --help`
Expected: Shows `PLUGIN_NAME`, `--global`, `--project`, `--source`, `--dry-run`, `--force`

- [ ] **Step 3: Smoke test with a real local plugin**

Run: `cd /tmp && uv run --project /c/Users/bitto/projects/c2roo c2roo convert "/c/Users/bitto/.claude/plugins/cache/claude-plugins-official/code-simplifier/1.0.0" --project --force`
Expected: Conversion report showing at least 1 agent converted

- [ ] **Step 4: Commit any final fixes**

```bash
git add -A
git commit -m "chore: final polish and verification"
```
