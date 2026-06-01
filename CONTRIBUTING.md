# Contributing to Code Manager

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/CREATSAIF/code-manager.git
cd code-manager

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## Project Structure

```
code-manager/
├── code_manager.py      # Main CLI entry point
├── pyproject.toml       # Project configuration
├── README.md           # Main documentation
├── docs/
│   └── git-workflow-standards.md  # Git workflow guide
└── tests/
    └── test_code_manager.py      # Test suite
```

## Coding Standards

- Follow PEP 8 style guidelines
- Add type hints to all function signatures
- Include docstrings for public functions
- Add tests for new features (pytest)

## Commit Message Format

```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
- `feat(cli): add worktree management commands`
- `fix(branch): handle empty branch list gracefully`
- `docs(readme): add installation screenshots`

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_code_manager.py -v

# Run with coverage
pytest tests/ --cov=code_manager --cov-report=html
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest tests/`
5. Commit with a clear message
6. Push to your fork and submit a PR

## Code Review Process

- PRs require at least 1 approval
- All CI checks must pass
- Address review feedback promptly
- Squash commits before merging

## Reporting Issues

- Use GitHub Issues for bugs and feature requests
- Include your Python version, OS, and error details
- For bugs, include a minimal reproduction case
