# c2roo — Claude Code Plugin to Roo Code Converter

> Design Spec — 2026-04-12

## Overview

c2roo is a Python CLI tool (UV-managed) that converts Claude Code plugins into Roo Code format. It supports all Claude Code plugin entity types (skills, commands, agents, hooks, MCP servers) and can source plugins from multiple marketplaces, git repositories, or local directories.

Both Claude Code and Roo Code follow the [Agent Skills](https://agentskills.io/) open standard for skills, making skill conversion near-trivial. Other entity types require varying degrees of transformation.

## Entity Mapping

| Claude Code Entity | Roo Equivalent | Fidelity | Notes |
|---|---|---|---|
| Skills (`skills/<name>/SKILL.md`) | Skills (`.roo/skills/<name>/SKILL.md`) | ~100% | Same Agent Skills format. Drop Claude-specific frontmatter fields. |
| Commands (`commands/<name>.md`) | Slash Commands (`.roo/commands/<name>.md`) | ~90% | `allowed-tools` dropped (Roo doesn't support it). Body + dynamic context preserved. |
| Agents (`agents/<name>.md`) | Custom Modes (`.roomodes`) + Rules (`.roo/rules-<slug>.md`) | ~70% | Model preference lost. Tool granularity reduced (fine-grained → group-based). |
| Hooks (`hooks/hooks.json`) | Guidance Rules (`.roo/rules/converted-hooks-guidance.md`) | ~30% | Soft guidance only — Roo has no hook enforcement. Intent preserved as AI instructions. |
| MCP Servers (`.mcp.json`) | MCP config (`.roo/mcp.json`) | ~95% | Near-identical format. `${CLAUDE_PLUGIN_ROOT}` resolved to installed path. |
| Plugin metadata (`.claude-plugin/plugin.json`) | Conversion report | N/A | No Roo equivalent. Metadata captured in report output. |

## Conversion Details

### Skills (Claude → Roo)

Skills follow the Agent Skills specification on both sides.

**Kept**: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`
**Dropped**: `disable-model-invocation`, `user-invocable`, `context`, `agent` (Claude-specific)
**Copied**: entire skill directory including `scripts/`, `references/`, `assets/`

The conversion is a directory copy with frontmatter cleanup.

### Commands (Claude → Roo Slash Commands)

Both use markdown files with YAML frontmatter.

**Kept**: `description`, `argument-hint`, body content (including `!`backtick`` dynamic context injection)
**Dropped**: `allowed-tools` (Roo slash commands don't support tool restrictions)
**Added**: `mode` field if inferrable from command content

### Agents → Custom Modes + Rules

This is the most complex conversion. A single Claude Code agent produces two outputs:

**Step 1 — Custom Mode entry** (in `.roomodes`):
- `slug`: agent name (kebab-case)
- `name`: humanized agent name
- `roleDefinition`: first paragraph of agent body (~500 chars)
- `groups`: mapped from agent `tools` list:
  - `Read`, `Grep`, `Glob`, `LS` → `"read"`
  - `Write`, `Edit`, `MultiEdit` → `"edit"`
  - `Bash`, `BashOutput`, `KillShell` → `"command"`
  - MCP-related tools → `"mcp"`
- `customInstructions`: null (full content goes to rules file)

**Step 2 — Rules file** (`.roo/rules-<slug>.md`):
- Full agent body as markdown
- Header noting this was converted from a Claude Code agent
- Footer noting original model preference and full tool list for reference

**Step 3 — .roomodes merge**:
- If `.roomodes` exists, parse and append new mode (skip duplicates by slug)
- If not, create new file
- Format: YAML (Roo's preferred format)

### Hooks → Guidance Rules

Hooks have no Roo equivalent. They are converted to descriptive markdown guidance.

**Output**: `.roo/rules/converted-hooks-guidance.md`

For each hook, generate a section describing:
- The event type (PreToolUse, SessionStart, etc.)
- The matcher pattern if present
- The original command that was run
- Suggestion to run manually or set up equivalent workflow

Referenced hook scripts are copied alongside for reference.

### MCP Servers

Near-identical format. Main transformations:
- Merge into existing `.roo/mcp.json` if present
- Resolve `${CLAUDE_PLUGIN_ROOT}` to actual installed path
- Warn on server name collisions

## CLI Architecture

### Command Tree

```
c2roo
├── marketplace
│   ├── browse [--source NAME]       # List plugins from registered marketplaces
│   ├── add <url>                    # Register a new marketplace source
│   ├── list                         # Show registered marketplace sources
│   └── remove <name>               # Remove a marketplace source
├── convert <path-or-url> --global|--project
│   ├── --dry-run                    # Show what would be converted
│   └── --force                      # Overwrite existing files
└── install <plugin-name> --global|--project
    ├── --source NAME                # Which marketplace to search
    ├── --dry-run                    # Show what would be converted
    └── --force                      # Overwrite existing files
```

### Output Location

- `--global`: writes to `~/.roo/` (skills, commands, rules, mcp.json) and `~/custom_modes.yaml` (modes)
- `--project`: writes to `.roo/` and `.roomodes` in current working directory
- **Neither flag**: error — user must specify one

### Install Flow

`c2roo install superpowers --global`:

1. Search registered marketplaces for "superpowers"
2. Resolve source entry (git URL + SHA, relative path, or git-subdir)
3. Clone/download to temp directory
4. Parse plugin → IR (dataclasses)
5. Convert IR → Roo format
6. Write to `~/.roo/`
7. Print conversion report
8. Clean up temp directory

## Project Structure

```
c2roo/
├── pyproject.toml
├── src/
│   └── c2roo/
│       ├── __init__.py
│       ├── cli.py                  # Click CLI groups & commands
│       ├── models/                 # IR dataclasses
│       │   ├── __init__.py
│       │   ├── plugin.py           # Plugin, PluginMetadata
│       │   ├── skill.py            # Skill
│       │   ├── command.py          # Command
│       │   ├── agent.py            # Agent
│       │   ├── hook.py             # Hook
│       │   └── mcp.py              # McpServer
│       ├── parser/                 # Claude Code plugin → IR
│       │   ├── __init__.py
│       │   ├── plugin_parser.py    # Orchestrates entity parsing
│       │   ├── frontmatter.py      # YAML frontmatter extraction
│       │   ├── skill_parser.py
│       │   ├── command_parser.py
│       │   ├── agent_parser.py
│       │   ├── hook_parser.py
│       │   └── mcp_parser.py
│       ├── converter/              # IR → Roo format
│       │   ├── __init__.py
│       │   ├── skill_converter.py
│       │   ├── command_converter.py
│       │   ├── agent_converter.py
│       │   ├── hook_converter.py
│       │   └── mcp_converter.py
│       ├── writer/                 # Output to disk
│       │   ├── __init__.py
│       │   └── roo_writer.py       # Handles --global vs --project paths
│       ├── sources/                # Plugin acquisition
│       │   ├── __init__.py
│       │   ├── marketplace.py      # Fetch & browse marketplace registries
│       │   ├── git_source.py       # Clone from git URL / git-subdir
│       │   └── local_source.py     # Read from local path
│       └── report.py               # Conversion report generation
└── tests/
    ├── test_parser/
    ├── test_converter/
    └── fixtures/                   # Sample plugin dirs for testing
```

## IR Dataclasses

```python
@dataclass
class PluginMetadata:
    name: str
    version: str | None
    description: str
    author: str | None
    homepage: str | None
    license: str | None

@dataclass
class Plugin:
    metadata: PluginMetadata
    skills: list[Skill]
    commands: list[Command]
    agents: list[Agent]
    hooks: list[Hook]
    mcp_servers: dict[str, McpServer]
    source_path: Path

@dataclass
class Skill:
    name: str
    description: str
    body: str
    license: str | None
    compatibility: str | None
    metadata: dict[str, str]
    allowed_tools: str | None
    resources: list[Path]
    # Claude-specific (preserved for report, dropped in conversion)
    disable_model_invocation: bool | None
    user_invocable: bool | None
    context: str | None
    agent: str | None

@dataclass
class Command:
    name: str
    description: str | None
    argument_hint: str | None
    allowed_tools: str | None
    body: str

@dataclass
class Agent:
    name: str
    description: str
    model: str | None
    tools: list[str]
    color: str | None
    body: str

@dataclass
class Hook:
    event: str
    matcher: str | None
    command: str
    timeout: int | None

@dataclass
class McpServer:
    name: str
    command: str | None
    args: list[str]
    env: dict[str, str]
    url: str | None
    headers: dict[str, str]
    disabled: bool
    always_allow: list[str]
    timeout: int | None
```

## Marketplace Management

### Registry Config

Stored at `~/.config/c2roo/marketplaces.yaml`:

```yaml
marketplaces:
  - name: official
    repo: anthropics/claude-plugins-official
    description: Official Anthropic plugins
  - name: community
    repo: anthropics/claude-plugins-community
    description: Community-submitted plugins
```

Marketplace sources are GitHub repos in `owner/repo` format. The tool clones the repo (or fetches just the `marketplace.json`) and reads `.claude-plugin/marketplace.json` from it.

The tool ships with the official and community Anthropic marketplaces pre-registered. Users add others via `c2roo marketplace add`.

### Plugin Source Resolution

Marketplace `plugin` entries use three source formats (from `marketplace.json`):

1. **Relative path**: `"source": "./plugins/foo"` — navigate within the already-cloned marketplace repo
2. **Git URL**: `"source": {"source": "url", "url": "https://github.com/org/repo.git", "sha": "abc123"}` — clone external repo at pinned SHA
3. **Git subdirectory**: `"source": {"source": "git-subdir", "url": "org/repo", "path": "plugins/name", "ref": "main", "sha": "abc123"}` — clone external repo, navigate to subdirectory

For `c2roo convert`, the source is a direct local path or git URL (not a marketplace entry).

### Caching

- Marketplace JSON files: cached at `~/.cache/c2roo/` with 1-hour TTL
- Plugin downloads: temp directory, cleaned up after install

## Error Handling

### File Conflicts
- Default: refuse to overwrite, list conflicting files
- `--force`: overwrite without asking
- `--dry-run`: show what would happen without writing

### Invalid Plugins
- Missing `.claude-plugin/plugin.json`: error with clear message
- Malformed frontmatter: skip entity, warn in report, continue
- Empty plugin (no entities): warn and exit cleanly

### Network Failures
- Marketplace fetch fails: skip that marketplace, warn, continue with others
- Git clone fails: clear error with the URL
- No internet: detect early, suggest local path

### Merge Behavior
- `.roomodes` exists: parse, append new modes, skip duplicates by slug
- `.roo/mcp.json` exists: merge `mcpServers`, warn on name collisions
- `.roo/rules-<slug>.md` exists: refuse unless `--force`

### Path Resolution
- `${CLAUDE_PLUGIN_ROOT}` in hooks/MCP configs: resolve to installed path
- Warn if hook scripts reference plugin-internal paths

### Platform
- Windows paths: `pathlib.Path` throughout
- `~/.roo/`: expand via `Path.home()`
- Git on PATH: check at startup, clear error if missing

## Conversion Report

Every `convert` and `install` command prints a report:

```
╭─ Conversion Report: superpowers ────────────────╮
│                                                  │
│ ✓ Skills:   12 converted                        │
│ ✓ Commands:  3 converted                        │
│ ~ Agents:    2 → custom modes (model pref lost) │
│ ~ Hooks:     1 → guidance rules (not enforced)  │
│ ✓ MCP:       0 servers                          │
│                                                  │
│ Dropped fields:                                  │
│   - skills: context, agent (3 skills)           │
│   - commands: allowed-tools (2 commands)        │
│                                                  │
│ Output: ~/.roo/                                  │
╰──────────────────────────────────────────────────╯
```

## Dependencies

- **click** — CLI framework
- **pyyaml** — YAML/frontmatter parsing
- **rich** — terminal output, tables, progress bars
- **git** (system) — via subprocess, must be on PATH

No other runtime dependencies. UV manages the Python environment and project.

## Future Extensibility

The light IR design allows future expansion:
- Additional emitters (Cursor, Windsurf, Copilot) by adding new converter modules
- Reverse conversion (Roo → Claude Code) by adding new parsers
- The IR dataclasses serve as the stable interchange format
