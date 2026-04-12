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
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["convert", str(FIXTURES), "--project", "--force"])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert "Conversion Report" in result.output

        assert (Path(".roo") / "skills" / "pdf-processing" / "SKILL.md").exists()
        assert (Path(".roo") / "commands" / "commit.md").exists()


def test_convert_dry_run(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["convert", str(FIXTURES), "--project", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert not (Path(".roo") / "skills").exists()
