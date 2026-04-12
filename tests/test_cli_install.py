from unittest.mock import MagicMock, patch

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
