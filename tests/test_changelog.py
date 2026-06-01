#!/usr/bin/env python3
"""Tests for the changelog generator in code_manager."""
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import code_manager


def _run(*args, cwd):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


@pytest.fixture
def temp_repo():
    """A temp git repo with conventional commits and one tag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init", "-q", "-b", "master"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, check=True)
        # initial
        (Path(tmpdir) / "README.md").write_text("# Test")
        _run("add", "-A", cwd=tmpdir)
        _run("commit", "-q", "-m", "chore: initial", cwd=tmpdir)
        # feature commit
        (Path(tmpdir) / "feat.py").write_text("x = 1\n")
        _run("add", "-A", cwd=tmpdir)
        _run("commit", "-q", "-m", "feat: add new feature", cwd=tmpdir)
        # fix commit
        (Path(tmpdir) / "fix.py").write_text("x = 2\n")
        _run("add", "-A", cwd=tmpdir)
        _run("commit", "-q", "-m", "fix: correct bug", cwd=tmpdir)
        # docs commit
        (Path(tmpdir) / "DOCS.md").write_text("docs")
        _run("add", "-A", cwd=tmpdir)
        _run("commit", "-q", "-m", "docs: update readme", cwd=tmpdir)
        # tag a release
        _run("tag", "-a", "v0.1.0", "-m", "first release", cwd=tmpdir)
        # one more commit after the tag
        (Path(tmpdir) / "feat2.py").write_text("y = 1\n")
        _run("add", "-A", cwd=tmpdir)
        _run("commit", "-q", "-m", "feat: another feature", cwd=tmpdir)
        # And a non-conventional commit
        (Path(tmpdir) / "misc.py").write_text("z = 1\n")
        _run("add", "-A", cwd=tmpdir)
        _run("commit", "-q", "-m", "WIP stuff", cwd=tmpdir)
        yield tmpdir


def test_changelog_renders_sections(temp_repo):
    args = type("A", (), {"path": temp_repo, "write": False})()
    rc, _, _ = _run("status", cwd=temp_repo)
    assert rc == 0
    # Capture stdout
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code_manager.cmd_changelog(args)
    out = buf.getvalue()
    assert "# Changelog" in out
    assert "## v0.1.0" in out
    assert "## Unreleased" in out
    assert "### Features" in out
    assert "### Bug Fixes" in out
    assert "### Documentation" in out
    # The conventional-commit type prefix is stripped from rendered subjects
    assert "add new feature" in out
    assert "correct bug" in out
    # Non-conventional commits fall through to "Other"
    assert "WIP stuff" in out


def test_changelog_writes_file(temp_repo):
    args = type("A", (), {"path": temp_repo, "write": True})()
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code_manager.cmd_changelog(args)
    msg = buf.getvalue()
    assert "Wrote" in msg
    changelog = Path(temp_repo) / "CHANGELOG.md"
    assert changelog.exists()
    text = changelog.read_text()
    assert "# Changelog" in text
    assert "v0.1.0" in text


def test_classify_commit_conventional():
    key, subj = code_manager._classify_commit("feat: add login")
    assert key == "feat"
    assert subj == "add login"

    key, subj = code_manager._classify_commit("Fix: correct bug")
    assert key == "fix"
    assert subj == "correct bug"


def test_classify_commit_breaking():
    key, subj = code_manager._classify_commit("feat!: rewrite auth")
    assert key == "feat"
    assert "BREAKING" in subj


def test_classify_commit_other():
    key, subj = code_manager._classify_commit("WIP stuff")
    assert key == "other"
    assert subj == "WIP stuff"
