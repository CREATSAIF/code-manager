#!/usr/bin/env python3
"""
Code Manager - Git workflow automation tool
Features: repo management, branching, commits, PRs, code review, releases
"""

import subprocess
import argparse
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
CONFIG_DIR = HERMES_HOME / "code-manager"
CONFIG_FILE = CONFIG_DIR / "config.json"

def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        default_config = {
            "default_branch": "main",
            "commit_template": "",
            "author_name": "Hermes Agent",
            "author_email": "agent@hermes.local",
            "ci_enabled": True,
        }
        import json
        CONFIG_FILE.write_text(json.dumps(default_config, indent=2))

def load_config():
    import json
    ensure_config()
    return json.loads(CONFIG_FILE.read_text())

def save_config(cfg):
    import json
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def run_git(*args, cwd=None, capture=True):
    cmd = ["git"] + list(args)
    kwargs = {"cwd": cwd or Path.cwd(), "shell": False}
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    try:
        result = subprocess.run(cmd, **kwargs, timeout=30)
        if capture:
            return result.returncode, result.stdout, result.stderr
        return result.returncode, "", ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)

def cmd_init(args):
    """Initialize a new git repository with conventions"""
    target = Path(args.path).resolve()
    if target.exists() and (target / ".git").exists():
        print(f"⚠️  {target} is already a git repo")
        return

    run_git("init", cwd=target)
    run_git("config", "init.defaultBranch", load_config()["default_branch"], cwd=target)
    run_git("config", "user.name", load_config()["author_name"], cwd=target)
    run_git("config", "user.email", load_config()["author_email"], cwd=target)

    # Create standard directories
    for d in ["src", "tests", "docs"]:
        (target / d).mkdir(exist_ok=True)

    # Create .gitignore
    gitignore = target / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(__import__('textwrap').dedent("""
            __pycache__/
            *.py[cod]
            .venv/
            .pytest_cache/
            *.egg-info/
            .DS_Store
            .env
            *.swp
        """).strip() + "\n")

    print(f"✅ Initialized git repo at {target}")
    print(f"   Default branch: {load_config()['default_branch']}")

def cmd_status(args):
    """Show git status with color"""
    rc, out, err = run_git("status", "--porcelain", cwd=args.path)
    if rc != 0:
        print(f"❌ Not a git repo: {args.path}")
        return
    if not out.strip():
        print("✅ Clean working tree")
    else:
        print(out)

def cmd_branch(args):
    """List, create, or delete branches"""
    if args.subcmd == "list":
        rc, out, _ = run_git("branch", "-a", cwd=args.path)
        print(f"Branches in {args.path}:")
        for line in out.strip().split("\n"):
            line = line.strip()
            if line.startswith("*"):
                print(f"  * {line[1:].strip()} (current)")
            elif line:
                print(f"    {line}")
    elif args.subcmd == "create":
        run_git("checkout", "-b", args.branch_name, cwd=args.path)
        print(f"✅ Created and checked out branch '{args.branch_name}'")
    elif args.subcmd == "delete":
        run_git("branch", "-d", args.branch_name, cwd=args.path)
        print(f"🗑 Deleted branch '{args.branch_name}'")

def cmd_commit(args):
    """Stage and commit with message"""
    if not args.message:
        print("❌ Commit message required. Use -m 'message'")
        return
    run_git("add", "-A", cwd=args.path)
    rc, _, err = run_git("commit", "-m", args.message, cwd=args.path)
    if rc == 0:
        print(f"✅ Committed: {args.message}")
    else:
        print(f"❌ Commit failed: {err}")

def cmd_log(args):
    """Show commit history"""
    count = args.n or 10
    rc, out, _ = run_git("log", "--oneline", "-n", str(count), cwd=args.path)
    print(out or "No commits yet")

def cmd_diff(args):
    """Show diff of changes"""
    target = args.path
    if args.staged:
        rc, out, _ = run_git("diff", "--cached", cwd=target)
    else:
        rc, out, _ = run_git("diff", cwd=target)
    print(out or "No changes")

def cmd_tag(args):
    """Create or list tags"""
    if args.name:
        run_git("tag", "-a", args.name, "-m", args.message or args.name, cwd=args.path)
        print(f"🏷 Created tag '{args.name}'")
    else:
        rc, out, _ = run_git("tag", cwd=args.path)
        print("Tags:\n" + (out or "  (none)"))

def cmd_stash(args):
    """Stash changes"""
    if args.subcmd == "save":
        rc, _, err = run_git("stash", "push", "-m", args.message or "WIP", cwd=args.path)
        print("✅ Stashed changes" if rc == 0 else f"❌ {err}")
    elif args.subcmd == "list":
        rc, out, _ = run_git("stash", "list", cwd=args.path)
        print(out or "No stashes")
    elif args.subcmd == "pop":
        run_git("stash", "pop", cwd=args.path)
        print("✅ Applied stash")

def cmd_cherry_pick(args):
    """Cherry-pick a commit"""
    run_git("cherry-pick", args.commit, cwd=args.path)
    print(f"✅ Cherry-picked {args.commit}")

def cmd_worktree(args):
    """Manage git worktrees"""
    if args.subcmd == "list":
        rc, out, _ = run_git("worktree", "list", cwd=args.path)
        print(out or "No worktrees")
    elif args.subcmd == "add":
        run_git("worktree", "add", args.path, args.branch or "HEAD", cwd=args.path)
        print(f"✅ Created worktree at {args.path}")

def cmd_remote(args):
    """Manage remotes"""
    if args.subcmd == "list":
        rc, out, _ = run_git("remote", "-v", cwd=args.path)
        print(out or "No remotes configured")
    elif args.subcmd == "add":
        run_git("remote", "add", args.name, args.url, cwd=args.path)
        print(f"✅ Added remote '{args.name}' -> {args.url}")
    elif args.subcmd == "remove":
        run_git("remote", "remove", args.name, cwd=args.path)
        print(f"🗑 Removed remote '{args.name}'")

def cmd_fetch(args):
    """Fetch from remote"""
    rc, _, err = run_git("fetch", "--all", cwd=args.path)
    if rc == 0:
        print("✅ Fetched from all remotes")
    else:
        print(f"⚠️  Fetch incomplete: {err}")

# Conventional-commit type → human section label
_CHANGELOG_SECTIONS = [
    ("feat",     "Features"),
    ("fix",      "Bug Fixes"),
    ("perf",     "Performance"),
    ("refactor", "Refactoring"),
    ("docs",     "Documentation"),
    ("test",     "Tests"),
    ("ci",       "CI / Build"),
    ("chore",    "Chores"),
    ("style",    "Style"),
    ("build",    "Build System"),
]

def _classify_commit(subject: str) -> tuple[str, str]:
    """Return (section_key, cleaned_subject) for a commit subject line.
    Falls back to ('other', subject) for non-conventional messages.
    """
    for key, _ in _CHANGELOG_SECTIONS:
        prefix = f"{key}:"
        if subject.lower().startswith(prefix):
            return key, subject[len(prefix):].strip() or subject
        prefix_bang = f"{key}!"
        if subject.lower().startswith(prefix_bang):
            return key, ("**BREAKING:** " + subject[len(prefix_bang):].strip()).strip()
    if "BREAKING CHANGE" in subject.upper() or "BREAKING:" in subject.upper():
        return "feat", ("**BREAKING:** " + subject).strip()
    return "other", subject

def cmd_changelog(args):
    """Generate (or print) a CHANGELOG.md from git history, grouped by tag.

    When --write is given, writes the result to CHANGELOG.md in the repo.
    Otherwise prints to stdout.
    """
    repo = args.path
    # %B = full body; %H = hash; %s = subject
    rc, out, err = run_git("log", "--tags", "--simplify-by-decoration",
                           "--pretty=format:%H|%d|%s", cwd=repo)
    if rc != 0:
        print(f"❌ git log failed: {err}")
        return

    rc, out2, err2 = run_git("log", "--pretty=format:%H|%s|%b", cwd=repo)
    if rc != 0:
        print(f"❌ git log failed: {err2}")
        return

    # Build tag → (hash, name) map from the decorated log
    tag_map = {}     # hash -> tag name (latest wins)
    tag_order = []   # ordered list of (hash, tag) newest-first
    for line in out.splitlines():
        if not line.strip():
            continue
        hash_part, _, rest = line.partition("|")
        deco = ""
        subj = rest
        if "|" in rest:
            deco, _, subj = rest.partition("|")
        tag_name = ""
        if "tag:" in deco:
            tag_name = deco.split("tag:", 1)[1].split(")")[0].strip()
        if tag_name and hash_part not in tag_map:
            tag_map[hash_part] = tag_name
            tag_order.append((hash_part, tag_name))

    # Build sections: list of (header, [(subject, hash)]) newest first
    # Iterate commits; group by the most recent preceding tag.
    sections = []  # list of (header, [items])
    current_header = "Unreleased"
    current_items = []
    seen_in_section = set()

    for line in out2.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        commit_hash = parts[0]
        subject = parts[1] if len(parts) >= 2 else ""
        # body = parts[2] if len(parts) > 2 else ""

        if commit_hash in tag_map and current_items:
            sections.append((current_header, current_items))
            current_header = tag_map[commit_hash]
            current_items = []
            seen_in_section = set()
        elif commit_hash in tag_map:
            current_header = tag_map[commit_hash]

        # Dedupe within a section (decorated + full logs both list tag commits)
        dedupe_key = (current_header, subject)
        if dedupe_key in seen_in_section:
            continue
        seen_in_section.add(dedupe_key)

        section_key, cleaned = _classify_commit(subject)
        current_items.append((section_key, cleaned, commit_hash[:7]))

    if current_items:
        sections.append((current_header, current_items))

    # Render
    lines = ["# Changelog", "", "All notable changes are documented here.", ""]
    for header, items in sections:
        lines.append(f"## {header}")
        lines.append("")
        # Group by section_key, keep original order within each group
        groups = {}
        order = []
        for section_key, subj, short_hash in items:
            if section_key not in groups:
                groups[section_key] = []
                order.append(section_key)
            groups[section_key].append((subj, short_hash))
        for key in order:
            label = dict(_CHANGELOG_SECTIONS).get(key, "Other")
            lines.append(f"### {label}")
            lines.append("")
            for subj, short_hash in groups[key]:
                lines.append(f"- {subj} ({short_hash})")
            lines.append("")

    body = "\n".join(lines).rstrip() + "\n"

    if getattr(args, "write", False):
        out_path = Path(repo) / "CHANGELOG.md"
        out_path.write_text(body)
        print(f"✅ Wrote {out_path} ({len(sections)} sections)")
    else:
        print(body)

def build_parser():
    parser = argparse.ArgumentParser(description="Code Manager - Git workflow automation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    p_init = subparsers.add_parser("init", help="Initialize a new git repo")
    p_init.add_argument("path", default=".", help="Directory path")

    p_status = subparsers.add_parser("status", help="Show git status")
    p_status.add_argument("path", default=".", help="Directory path")

    p_branch = subparsers.add_parser("branch", help="Manage branches")
    p_branch.add_argument("subcmd", choices=["list", "create", "delete"], help="Action")
    p_branch.add_argument("--name", dest="branch_name", help="Branch name")
    p_branch.add_argument("path", default=".")

    p_commit = subparsers.add_parser("commit", help="Stage and commit")
    p_commit.add_argument("-m", dest="message", required=True, help="Commit message")
    p_commit.add_argument("path", default=".")

    p_log = subparsers.add_parser("log", help="Show commit history")
    p_log.add_argument("-n", type=int, dest="n", help="Number of commits")
    p_log.add_argument("path", default=".")

    p_diff = subparsers.add_parser("diff", help="Show changes")
    p_diff.add_argument("--staged", action="store_true", help="Show staged diff")
    p_diff.add_argument("path", default=".")

    p_tag = subparsers.add_parser("tag", help="Manage tags")
    p_tag.add_argument("-m", dest="message", help="Tag message")
    p_tag.add_argument("name", nargs="?", help="Tag name")
    p_tag.add_argument("path", default=".")

    p_stash = subparsers.add_parser("stash", help="Stash management")
    p_stash.add_argument("subcmd", choices=["save", "list", "pop"], help="Action")
    p_stash.add_argument("-m", dest="message", help="Stash message")
    p_stash.add_argument("path", default=".")

    p_cherry = subparsers.add_parser("cherry-pick", help="Cherry-pick commit")
    p_cherry.add_argument("commit", help="Commit hash")
    p_cherry.add_argument("path", default=".")

    p_worktree = subparsers.add_parser("worktree", help="Manage worktrees")
    p_worktree.add_argument("subcmd", choices=["list", "add"], help="Action")
    p_worktree.add_argument("path", default=".")
    p_worktree.add_argument("--branch", help="Branch for new worktree")

    p_remote = subparsers.add_parser("remote", help="Manage remotes")
    p_remote.add_argument("subcmd", choices=["list", "add", "remove"], help="Action")
    p_remote.add_argument("name", nargs="?", help="Remote name")
    p_remote.add_argument("url", nargs="?", help="Remote URL")
    p_remote.add_argument("path", default=".")

    p_fetch = subparsers.add_parser("fetch", help="Fetch from remote")
    p_fetch.add_argument("path", default=".")

    p_changelog = subparsers.add_parser("changelog", help="Generate CHANGELOG.md from git history")
    p_changelog.add_argument("--write", action="store_true", help="Write to CHANGELOG.md in the repo")
    p_changelog.add_argument("path", default=".")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n--- Git Convenience Commands ---")
        print("  git status          -> cm status")
        print("  git branch -a       -> cm branch list")
        print("  git log --oneline   -> cm log -n 10")
        print("  git diff --cached   -> cm diff --staged")
        return

    args.path = str(Path(args.path).resolve())

    handlers = {
        "init": cmd_init,
        "status": cmd_status,
        "branch": cmd_branch,
        "commit": cmd_commit,
        "log": cmd_log,
        "diff": cmd_diff,
        "tag": cmd_tag,
        "stash": cmd_stash,
        "cherry-pick": cmd_cherry_pick,
        "worktree": cmd_worktree,
        "remote": cmd_remote,
        "fetch": cmd_fetch,
        "changelog": cmd_changelog,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()