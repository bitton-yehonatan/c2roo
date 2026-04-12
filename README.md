<p align="center">
  <img src="logo.svg" alt="c2roo logo" width="600"/>
</p>

<p align="center">
  <strong>Convert Claude Code plugins to Roo Code format</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"/>
  <img src="https://img.shields.io/badge/tests-70%20passing-brightgreen" alt="Tests"/>
</p>

---

## Overview

**c2roo** is a CLI tool that converts [Claude Code](https://claude.ai/code) plugins into [Roo Code](https://roocode.com) format. It handles all plugin entity types — skills, commands, agents, hooks, and MCP servers — and can source plugins from marketplaces, git repos, or local directories.

Both tools follow the [Agent Skills](https://agentskills.io/) open standard, so skill conversion is near-lossless. Other entities require varying degrees of transformation.

## Entity Mapping

| Claude Code | Roo Code | Fidelity | Notes |
|---|---|---|---|
| Skills | Skills | ~100% | Same Agent Skills format. Claude-specific fields stripped. |
| Commands | Slash Commands | ~90% | `allowed-tools` dropped. Body + dynamic context preserved. |
| Agents | Custom Modes + Rules | ~70% | Model pref lost. Tool granularity reduced. |
| Hooks | Guidance Rules | ~30% | Soft guidance only — Roo has no hook enforcement. |
| MCP Servers | MCP config | ~95% | Near-identical. `${CLAUDE_PLUGIN_ROOT}` resolved. |

## Installation

```bash
# With uv (recommended)
uv tool install c2roo

# Or from source
git clone https://github.com/bitton-yehonatan/c2roo.git
cd c2roo
uv sync
```

## Quick Start

```bash
# Convert a local Claude Code plugin to your project
c2roo convert ./path/to/plugin --project

# Install a plugin from the marketplace
c2roo install superpowers --global

# Browse available plugins
c2roo marketplace browse

# Dry run — see what would be converted without writing files
c2roo convert ./path/to/plugin --project --dry-run
```

## CLI Reference

### `c2roo convert`

Convert a plugin from a local path or git URL.

```
Usage: c2roo convert [OPTIONS] SOURCE

Options:
  --global   Install to ~/.roo/ (global)
  --project  Install to .roo/ (project)
  --dry-run  Show what would be converted
  --force    Overwrite existing files
```

You **must** specify `--global` or `--project`. Omitting both is an error.

```bash
# From a local directory
c2roo convert ~/plugins/my-plugin --project --force

# From a git URL
c2roo convert https://github.com/org/plugin.git --global
```

### `c2roo install`

Install a plugin from a registered marketplace.

```
Usage: c2roo install [OPTIONS] PLUGIN_NAME

Options:
  --global       Install to ~/.roo/ (global)
  --project      Install to .roo/ (project)
  --source TEXT  Which marketplace to search
  --dry-run      Show what would be converted
  --force        Overwrite existing files
```

```bash
# Install from any marketplace
c2roo install frontend-design --project

# Install from a specific marketplace
c2roo install react-native-best-practices --global --source callstack
```

### `c2roo marketplace`

Manage plugin marketplace sources.

```bash
# List registered marketplaces
c2roo marketplace list

# Browse plugins from all marketplaces
c2roo marketplace browse

# Browse a specific marketplace
c2roo marketplace browse --source official

# Add a new marketplace (GitHub owner/repo format)
c2roo marketplace add expo/expo-plugins --name expo --description "Expo plugins"

# Remove a marketplace
c2roo marketplace remove expo
```

**Default marketplaces** (pre-registered):
- `official` — `anthropics/claude-plugins-official`
- `community` — `anthropics/claude-plugins-community`

## How Conversion Works

### Skills (near 1:1)

Both tools follow the [Agent Skills](https://agentskills.io/) spec. c2roo copies the entire skill directory (SKILL.md + scripts/references/assets) and strips Claude-specific frontmatter fields (`disable-model-invocation`, `user-invocable`, `context`, `agent`).

### Commands -> Slash Commands

Markdown files with YAML frontmatter transfer cleanly. The `allowed-tools` field is dropped (Roo doesn't support it). Dynamic context injection (`!`backtick``) works in both.

### Agents -> Custom Modes + Rules

Each Claude Code agent produces two Roo outputs:

1. **Custom Mode** in `.roomodes` — with slug, humanized name, role definition (first paragraph), and tool groups mapped from the agent's tool list
2. **Rules file** in `.roo/rules-{slug}/` — full agent system prompt, plus a footer noting the original model preference and tool list

Tool mapping: `Read/Grep/Glob` -> `read`, `Write/Edit` -> `edit`, `Bash` -> `command`, `WebFetch/WebSearch` -> `mcp`.

### Hooks -> Guidance Rules

Roo has no hook system. c2roo converts hooks into a descriptive markdown file (`.roo/rules/converted-hooks-guidance.md`) that explains the original behavior and suggests manual equivalents.

### MCP Servers

Near-identical JSON format. `${CLAUDE_PLUGIN_ROOT}` references are resolved to the actual install path. Existing `.roo/mcp.json` is merged, not overwritten.

## Output Locations

| Flag | Skills | Commands | Modes | Rules | MCP |
|---|---|---|---|---|---|
| `--project` | `.roo/skills/` | `.roo/commands/` | `.roomodes` | `.roo/rules*/` | `.roo/mcp.json` |
| `--global` | `~/.roo/skills/` | `~/.roo/commands/` | `~/.roomodes` | `~/.roo/rules*/` | `~/.roo/mcp.json` |

## Development

```bash
git clone https://github.com/bitton-yehonatan/c2roo.git
cd c2roo
uv sync

# Run tests
uv run pytest tests/ -v

# Run the CLI
uv run c2roo --help
```

## Contributing

1. Fork the repo
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all 70+ tests pass
5. Submit a PR

## License

MIT
