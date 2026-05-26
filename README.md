# github-kit

A growing collection of Git hooks and scripts for everyday GitHub workflows.

Each script lives in its own directory under `scripts/` with a dedicated README.

## Scripts

| Script | Description |
|---|---|
| [check-sensitive](scripts/check-sensitive/) | Detect secrets, credentials, and sensitive data before committing |

## Hooks

| Hook | Script | Description |
|---|---|---|
| pre-commit | check-sensitive | Blocks commits containing sensitive information |

## Deployment (Global Git Hooks)

To apply all hooks globally across every repository on your machine:

```bash
git config --global core.hooksPath /path/to/github-kit/hooks
```

Replace `/path/to/github-kit` with the path where you cloned this repository.

To verify:

```bash
git config --global core.hooksPath
```

To revert to per-repository hooks:

```bash
git config --global --unset core.hooksPath
```

## Design Principles

- **Zero external dependencies**: Requires only Python 3.10+. No package managers, no additional binaries.
- **Single source of truth**: All hooks, scripts, and detection rules live in this repository. Rule changes go through code review.
- **Global-first deployment**: Hooks are applied machine-wide via `core.hooksPath`, not per-repository.
- **Standalone usability**: Scripts run independently of the hook infrastructure for manual scans.
- **Opt-out over opt-in**: Use `.check-sensitive-ignore` to suppress false positives rather than weakening the default ruleset.

## Requirements

- Git 2.9+ (for `core.hooksPath` support)
- Python 3.10+
