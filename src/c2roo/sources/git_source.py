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
