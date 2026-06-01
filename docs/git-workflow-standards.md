# Git Repository Management Standards

Standards for effective team collaboration using Git.

---

## 1. Branch Strategy

### Branch Types

| Branch | Purpose | Naming Convention |
|--------|---------|-------------------|
| `main` | Production-ready code | `main` (protected) |
| `master` | Legacy main branch | `master` (protected) |
| `develop` | Integration branch | `develop` (protected) |
| `feature/*` | New features | `feature/user-auth`, `feature/payment-v2` |
| `fix/*` | Bug fixes | `fix/login-crash`, `fix/memory-leak` |
| `hotfix/*` | Urgent production fixes | `hotfix/critical-security` |
| `release/*` | Release preparation | `release/v1.2.0` |
| `refactor/*` | Code refactoring | `refactor/api-client` |
| `docs/*` | Documentation only | `docs/api-reference` |
| `test/*` | Test additions | `test/integration-coverage` |

### Branch Creation

```bash
# Create from a clean main
git checkout main
git pull origin main
git checkout -b feature/user-auth

# Feature branches should be short-lived (1-3 days max)
# If longer, break into smaller sub-features
```

### Branch Protection Rules

```
main/master: 
  - Require PR reviews (1-2 reviewers)
  - Require status checks to pass
  - No force push
  - No direct commits

develop:
  - Require PR reviews
  - Require tests passing
  - Merge via squash only
```

---

## 2. Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type Prefixes

| Type | Use Case |
|------|----------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Maintenance, dependencies |
| `ci` | CI/CD changes |
| `revert` | Revert previous commit |

### Examples

```bash
# Good commits
git commit -m "feat(auth): add OAuth2 login flow"
git commit -m "fix(api): handle null response in user endpoint"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(payment): add integration tests for stripe webhook"

# Bad commits (avoid)
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "asdfasdf"
git commit -m "updates"
```

### Commit Best Practices

1. **Atomic commits** - One logical change per commit
2. **Executable tests** - Include tests with new features
3. **Meaningful messages** - Describe WHAT and WHY, not HOW
4. **Reference issues** - Include issue numbers in footer
   ```
   fix(login): handle expired session tokens
   
   Closes #123
   Related to #115, #118
   ```

---

## 3. Pull Request Workflow

### PR Creation

```bash
# Before creating PR
git checkout main
git pull origin main
git checkout -b feature/my-feature
# ... make changes ...
git push -u origin feature/my-feature
# Then create PR via GitHub UI or gh CLI
```

### PR Description Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No warnings/errors
```

### PR Review Process

1. **Self-review first** - Check your own diff before requesting review
2. **Small PRs preferred** - Under 400 lines changed is ideal
3. **Description matters** - Explain WHY, not just WHAT
4. **Respond to feedback** - Don't ignore review comments
5. **Squash before merge** - Keep history clean

### PR Merging

```bash
# Squash and merge (preferred for feature branches)
gh pr merge --squash

# Merge commit (preserves feature branch history)  
gh pr merge --merge

# Rebase and fast-forward (clean linear history)
gh pr merge --rebase
```

---

## 4. Code Review Standards

### As an Author

1. **Limit PR size** - Large PRs get shallow reviews
2. **Write good descriptions** - Help reviewers understand context
3. **Annotate complex code** - Comments explaining non-obvious logic
4. **Be responsive** - Address comments within 24 hours
5. **Don't take feedback personally** - Code review is about the code

### As a Reviewer

1. **Be constructive** - Suggest improvements, don't just criticize
2. **Be specific** - "Consider using X because Y"
3. **Approve when safe** - Don't block on stylistic preferences
4. **Ask questions** - "What happens if input is empty?" not "This is wrong"
5. **Use prefixes**:
   - `nit:` - Minor, non-blocking suggestion
   - `suggestion:` - Consider this, but not required
   - `question:` - Need clarification
   - `blocking:` - Must be addressed before merge

### Review Checklist

```
[ ] Does the code do what the description says?
[ ] Is the code well-tested?
[ ] Are there edge cases handled?
[ ] Is there documentation for complex logic?
[ ] Does it follow project style conventions?
[ ] Any security concerns?
[ ] Any performance concerns?
[ ] No debug code or TODOs left behind?
```

---

## 5. Release Management

### Version Numbering (Semantic Versioning)

```
MAJOR.MINOR.PATCH
1.2.3
│ │ │
│ │ └── Patch: Bug fixes, no API changes
│ └──── Minor: New features, backwards compatible
└────── Major: Breaking changes
```

### Release Branch Workflow

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 2. Update version files, run tests
# ... 

# 3. Merge to main
git checkout main
git merge release/v1.2.0 --no-ff
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# 4. Merge back to develop
git checkout develop
git merge release/v1.2.0 --no-ff
git push origin develop

# 5. Delete release branch
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

### Hotfix Workflow

```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-auth-bug

# ... fix and test ...

# Merge to main
git checkout main
git merge hotfix/critical-auth-bug --no-ff
git tag -a v1.2.1 -m "Hotfix: critical auth bug"
git push origin main --tags

# Merge to develop
git checkout develop
git merge hotfix/critical-auth-bug --no-ff
git push origin develop

# Clean up
git branch -d hotfix/critical-auth-bug
```

---

## 6. Tagging Conventions

### Tag Types

| Tag | Format | Use |
|-----|--------|-----|
| Release | `v1.2.3` | Stable releases |
| Pre-release | `v1.2.3-beta.1` | Beta testing |
| RC | `v1.2.3-rc.1` | Release candidate |
| Dev | `v1.2.3-dev` | Development snapshot |

### Tag Commands

```bash
# Annotated tag (recommended)
git tag -a v1.0.0 -m "Version 1.0.0 - Initial stable release"
git push origin v1.0.0

# List tags
git tag -l
git tag -l "v1.*"

# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0

# Update tag to new commit
git tag -a v1.0.0 -f -m "Updated v1.0.0"
git push origin v1.0.0 --force
```

---

## 7. Gitignore Standards

### Common Patterns

```
# Dependencies
node_modules/
venv/
.venv/
__pycache__/

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Logs
*.log
logs/

# Test coverage
coverage/
.coverage

# Secrets
*.pem
*.key
credentials.json
```

### Tools for Managing .gitignore

```bash
# Use github/gitignore for project-specific templates
curl -s https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore

# Or use the tools:
# https://gitignore.io
```

---

## 8. Useful Aliases

```bash
# ~/.gitconfig or .git/config

[alias]
    # Short status
    s = status -sb
    
    # Log with graph
    l = log --oneline --graph --decorate -20
    
    # Amend without editing message
    amend = commit --amend --no-edit
    
    # Uncommit last commit (keep changes)
    undo = reset --soft HEAD~1
    
    # Stash with message
    ss = stash push -m
    
    # Show changes from commit
    show-stat = show --stat
    
    # Clean merged branches
    cleanup = !git branch --merged | grep -v \"\\*\\|main\\|master\\|develop\" | xargs -r git branch -d
    
    # Pull with rebase
    pl = pull --rebase
    
    # Fetch all remotes
    fa = fetch --all
```

---

## 9. Conflict Resolution

### Before Starting Work

```bash
# Always start from clean main
git checkout main
git pull origin main
git checkout -b feature/my-work
```

### When Conflicts Occur

```bash
# Fetch latest
git fetch --all

# Start rebase (or merge)
git rebase origin/main

# Resolve conflicts, then:
git add .
git rebase --continue

# If things go wrong:
git rebase --abort
```

### Merge vs Rebase

| Scenario | Recommended |
|----------|-------------|
| Local feature branch | Rebase onto main (clean history) |
| Public branch (shared) | Merge (don't rebase shared branches) |
| Release branches | Merge (preserve context) |
| Hotfixes | Merge to main, then rebase develop |

---

## 10. Repository Hygiene

### Regular Maintenance

```bash
# Weekly: Clean up merged branches
git checkout main && git pull
git remote prune origin

# Monthly: Verify repository health
git fsck --full
git reflog expire --expire=30days --all

# After major changes: Verify tags are correct
git log --oneline --tags | head -20
```

### Large File Management

```bash
# Check for large files in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sort -k3 -n -r | head -20

# Use Git LFS for large files
git lfs install
git lfs track "*.zip"
git add .gitattributes
```

---

## Quick Reference

```bash
# Daily workflow
git checkout main && git pull          # Start fresh
git checkout -b feature/your-feature   # Create branch
# ... work ...
git add -A && git commit -m "feat(scope): description"
git push -u origin feature/your-feature
# Create PR, get review, merge

# Sync with upstream
git fetch upstream
git rebase upstream/main

# Stash work
git stash save "WIP: working on X"
git stash list
git stash pop # Apply and remove
git stash apply # Apply but keep
```
