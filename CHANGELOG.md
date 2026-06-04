# Changelog

All notable changes are documented here.

## v0.2.0

### CI / Build

- add PyPI Trusted Publishing (OIDC) job to release workflow
- verify artifact sha256 checksums before publishing
- enrich `pyproject.toml` with license, authors, classifiers, project URLs, and long description

## Unreleased

### Chores

- add .gitignore (#2) (81cff8b)

### Features

- add changelog subcommand with conventional-commit grouping (#1) (7e00f3d)
- add code-manager git workflow tool (d62bc26)

### Bug Fixes

- remove unused 'current' var and unnecessary f-string to pass pyflakes lint (980cb2c)
- remove unused imports to pass pyflakes lint (d33b703)

### Documentation

- add CONTRIBUTING.md with contribution guidelines (cea51c8)
- add comprehensive git workflow standards guide (9daa73f)

### Tests

- add pytest test suite for core git operations (d83eae6)

### CI / Build

- add GitHub Actions workflow for test and lint jobs (f91f718)
