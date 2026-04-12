import subprocess
from unittest.mock import patch

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
    with patch("c2roo.sources.git_source.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        clone_repo("https://github.com/org/repo.git", dest=tmp_path / "cloned", sha="abc123")

        calls = mock_run.call_args_list
        assert len(calls) == 3  # clone + fetch + checkout
        clone_args = calls[0][0][0]
        assert "git" in clone_args
        assert "clone" in clone_args
        assert "https://github.com/org/repo.git" in clone_args

        checkout_args = calls[2][0][0]
        assert "checkout" in checkout_args
        assert "abc123" in checkout_args


def test_clone_repo_no_sha(tmp_path):
    with patch("c2roo.sources.git_source.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        clone_repo("https://github.com/org/repo.git", dest=tmp_path / "cloned")

        calls = mock_run.call_args_list
        assert len(calls) == 1  # Only clone, no checkout
