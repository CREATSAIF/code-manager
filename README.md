# Code Manager

Git workflow automation tool with convenience commands for branching, commits, staging, and repository management.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Initialize a repo with conventions
cm init /path/to/project

# Branch management
cm branch list /path/to/project
cm branch create new-feature /path/to/project

# Stage and commit
cm commit -m "Add new feature" /path/to/project

# View history
cm log -n 20 /path/to/project

# Tags and releases
cm tag v1.0.0 -m "Release 1.0.0" /path/to/project

# Stash
cm stash save "WIP" /path/to/project
cm stash list /path/to/project
cm stash pop /path/to/project
```

## Commands

- `init` - Initialize git repo with standard config
- `status` - Show working tree status
- `branch` - List/create/delete branches
- `commit` - Stage all and commit with message
- `log` - Show commit history
- `diff` - Show changes (--staged for staged)
- `tag` - Create/list tags
- `stash` - Stash management (save/list/pop)
- `cherry-pick` - Cherry-pick a commit
- `worktree` - Manage git worktrees
- `remote` - Manage remotes
- `fetch` - Fetch from all remotes