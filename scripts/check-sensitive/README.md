# check-sensitive

Scans files for sensitive information and blocks commits that contain secrets, credentials, or other data that should not be pushed to a repository.

## What It Detects

| Category | Examples |
|---|---|
| IP addresses | IPv4, IPv6, private ranges (10.x, 172.16–31.x, 192.168.x) |
| Credentials | API keys, tokens, passwords, AWS access/secret keys |
| Private keys | RSA, EC, OpenSSH PEM headers |
| GitHub tokens | `ghp_*`, `ghs_*` |
| Sensitive paths | Absolute Unix (`/home/`, `/etc/`) and Windows paths |
| Sensitive filenames | `.env`, `.ssh`, `*.pem`, `*.key`, `*.p12`, `credentials.json`, etc. |
| PII | Email addresses, domain names |

## Usage

### As a pre-commit hook

When wired up via `core.hooksPath` (see the [top-level README](../../README.md)), the hook runs automatically on every `git commit` and scans all staged files.

### Standalone

```bash
# Scan current directory (non-recursive)
python3 check-sensitive.py

# Scan a specific directory
python3 check-sensitive.py path/to/dir

# Scan recursively
python3 check-sensitive.py -r path/to/dir

# Scan explicit files
python3 check-sensitive.py --files file1.py file2.yaml
```

Exit code is `0` if no issues found, `1` if issues are detected.

### Output

```
[OK]     src/main.py
[WARN]   config/settings.py
           line 4: [Secret/token] api_token = "s3cr3t-value"
[WARN]   .env
           ! Sensitive filename detected

3 file(s) checked — 2 issue(s) found.
```

## Skipped Files

Binary and non-text files are skipped automatically: images, archives, executables, compiled artifacts, fonts, databases, and media files.

## Requirements

- Python 3.10+
