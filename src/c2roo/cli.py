import shutil
import tempfile
from pathlib import Path

import click

from c2roo.converter.agent_converter import convert_agent
from c2roo.converter.command_converter import convert_command
from c2roo.converter.hook_converter import convert_hooks
from c2roo.converter.mcp_converter import convert_mcp
from c2roo.converter.skill_converter import convert_skill
from c2roo.parser.plugin_parser import parse_plugin
from c2roo.report import ConversionReport
from c2roo.sources.git_source import check_git_available, clone_repo, is_git_url
from c2roo.sources.local_source import resolve_local
from c2roo.sources.marketplace import MarketplaceRegistry
from c2roo.writer.roo_writer import RooWriter


def _resolve_output_root(target_global: bool) -> Path:
    if target_global:
        return Path.home() / ".roo"
    return Path.cwd() / ".roo"


def _run_conversion(plugin_path: Path, output_root: Path, force: bool, dry_run: bool) -> None:
    """Shared parse -> convert -> write pipeline."""
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


@click.group()
@click.version_option()
def main():
    """Convert Claude Code plugins to Roo Code format."""


# --- marketplace subcommands ---


@main.group()
def marketplace():
    """Browse and manage plugin marketplace sources."""


@marketplace.command("browse")
@click.option("--source", default=None, help="Filter to a specific marketplace source.")
def marketplace_browse(source):
    """List plugins from registered marketplaces."""
    from rich.console import Console
    from rich.table import Table

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
    registry = MarketplaceRegistry()
    registry.add_source(name, repo, description)
    click.echo(f"Added marketplace '{name}' ({repo})")


@marketplace.command("list")
def marketplace_list():
    """Show registered marketplace sources."""
    from rich.console import Console
    from rich.table import Table

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
    registry = MarketplaceRegistry()
    registry.remove_source(name)
    click.echo(f"Removed marketplace '{name}'")


# --- convert command ---


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

    temp_dir = None
    if is_git_url(source):
        check_git_available()
        temp_dir = tempfile.mkdtemp(prefix="c2roo-")
        plugin_path = clone_repo(source, dest=Path(temp_dir) / "plugin")
    else:
        plugin_path = resolve_local(source)

    output_root = _resolve_output_root(target_global)

    if dry_run:
        click.echo("[DRY RUN] No files will be written.\n")

    try:
        _run_conversion(plugin_path, output_root, force, dry_run)
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


# --- install command ---


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

    check_git_available()

    registry = MarketplaceRegistry()
    result = registry.search_plugin(plugin_name, source_filter=source)

    if result is None:
        raise click.ClickException(f"Plugin '{plugin_name}' not found in any registered marketplace.")

    plugin_entry, mkt_source = result
    click.echo(f"Found '{plugin_name}' in marketplace '{mkt_source['name']}'")

    output_root = _resolve_output_root(target_global)

    if dry_run:
        click.echo("[DRY RUN] No files will be written.\n")

    temp_dir = tempfile.mkdtemp(prefix="c2roo-")
    try:
        plugin_source = plugin_entry.get("source")

        if isinstance(plugin_source, str):
            # Relative path — clone the marketplace repo first
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
            raise click.ClickException("Downloaded plugin has no .claude-plugin/plugin.json")

        _run_conversion(plugin_path, output_root, force, dry_run)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
