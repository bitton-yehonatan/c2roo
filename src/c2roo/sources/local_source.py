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
