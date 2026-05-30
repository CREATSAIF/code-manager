#!/usr/bin/env python3
"""Tests for code_manager"""
import pytest
import subprocess
import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import code_manager

def run_git(*args, cwd=None):
    result = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        os.makedirs("src")
        os.makedirs("tests")
        (Path(tmpdir) / ".gitignore").write_text("__pycache__/\n*.pyc\n")
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmpdir, capture_output=True)
        yield tmpdir

def test_status_clean(temp_repo):
    rc, out, err = run_git("status", "--porcelain", cwd=temp_repo)
    assert rc == 0
    assert out.strip() == ""

def test_log_shows_commits(temp_repo):
    rc, out, _ = run_git("log", "--oneline", cwd=temp_repo)
    assert "initial" in out
    assert rc == 0

def test_branch_list(temp_repo):
    rc, out, _ = run_git("branch", "-a", cwd=temp_repo)
    assert "master" in out
    assert rc == 0

def test_commit_message_required():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(f"{tmpdir}/src")
        os.makedirs(f"{tmpdir}/tests")
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, capture_output=True)
        Path(f"{tmpdir}/README.md").write_text("# Test")
        subprocess.run(["git", "add", "-A"], cwd=tmpdir, capture_output=True)

        class Args:
            message = None
            path = tmpdir
        args = Args()
        code_manager.cmd_commit(args)
        # Should have printed error message