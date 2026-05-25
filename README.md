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

## Requirements

- Git 2.9+ (for `core.hooksPath` support)
- Python 3.10+
