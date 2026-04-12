from pathlib import Path

import pytest

from c2roo.sources.local_source import resolve_local

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_resolve_local_valid():
    path = resolve_local(str(FIXTURES))
    assert path == FIXTURES.resolve()


def test_resolve_local_invalid():
    with pytest.raises(FileNotFoundError, match="Not a Claude Code plugin"):
        resolve_local("/nonexistent/path")


def test_resolve_local_missing_manifest():
    with pytest.raises(FileNotFoundError, match="plugin.json"):
        resolve_local(str(FIXTURES.parent))
