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
