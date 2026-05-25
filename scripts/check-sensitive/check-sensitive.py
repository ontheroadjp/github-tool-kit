#!/usr/bin/env python3
"""
check-sensitive.py — Detect sensitive information in files.

Usage:
    python3 check-sensitive.py [-r] [directory]
    (When called from pre-commit hook, reads staged file list from stdin or args)
"""

import re
import sys
import os
import argparse
from pathlib import Path
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

SENSITIVE_PATTERNS = [
    ("IPv4 address",          re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b')),
    ("IPv6 address",          re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')),
    ("Private IPv4 address",  re.compile(r'\b(10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)\b')),
    ("Absolute Unix path",    re.compile(r'(?<!["\w])/(?:home|root|Users|var|etc|opt|tmp|srv|usr)/[\w./-]+')),
    ("Absolute Windows path", re.compile(r'[A-Za-z]:\\(?:Users|Windows|Program Files)[\\\w\s.-]+')),
    ("API key (generic)",     re.compile(r'(?i)(?:api[_-]?key|apikey|access[_-]?key)\s*[:=]\s*["\']?[\w\-]{16,}["\']?')),
    ("Secret/token",          re.compile(r'(?i)(?:secret|token|password|passwd|pwd)\s*[:=]\s*["\']?[\w\-]{8,}["\']?')),
    ("AWS access key",        re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ("AWS secret key",        re.compile(r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']?[\w/+]{40}["\']?')),
    ("Private key header",    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ("GitHub token",          re.compile(r'\bghp_[0-9A-Za-z]{36}\b|\bghs_[0-9A-Za-z]{36}\b')),
    ("Domain name",           re.compile(r'\b(?:[a-zA-Z0-9-]+\.){2,}(?:com|net|org|io|co|jp|dev|app|internal|local)\b')),
    ("Email address",         re.compile(r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b')),
]

# Files/dirs that should not be committed
SENSITIVE_FILENAMES = re.compile(
    r'(?:^|\/)('
    r'\.env(?:\.\w+)?'
    r'|\.claude'
    r'|\.aws'
    r'|\.ssh'
    r'|\.gnupg'
    r'|id_rsa(?:\.pub)?'
    r'|id_ed25519(?:\.pub)?'
    r'|credentials(?:\.json)?'
    r'|secrets\.(?:yml|yaml|json|toml)'
    r'|.*\.pem'
    r'|.*\.key'
    r'|.*\.p12'
    r'|.*\.pfx'
    r')$'
)

# Binary-like extensions to skip
SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.svg',
    '.pdf', '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z',
    '.exe', '.dll', '.so', '.dylib', '.bin', '.wasm',
    '.pyc', '.class', '.o', '.a',
    '.mp4', '.mp3', '.mov', '.avi',
    '.ttf', '.woff', '.woff2', '.eot',
    '.db', '.sqlite', '.sqlite3',
}

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    line_no: int
    kind: str
    text: str

@dataclass
class FileResult:
    path: str
    is_sensitive_name: bool = False
    findings: list[Finding] = field(default_factory=list)

    @property
    def has_issues(self):
        return self.is_sensitive_name or bool(self.findings)

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def should_skip(path: Path) -> bool:
    return path.suffix.lower() in SKIP_EXTENSIONS

def check_filename(path: Path) -> bool:
    return bool(SENSITIVE_FILENAMES.search(str(path)))

def check_content(path: Path) -> list[Finding]:
    findings = []
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return findings

    for lineno, line in enumerate(text.splitlines(), 1):
        for kind, pattern in SENSITIVE_PATTERNS:
            if pattern.search(line):
                snippet = line.strip()[:120]
                findings.append(Finding(lineno, kind, snippet))
                break  # one finding per line is enough
    return findings

def scan_files(paths: list[Path]) -> list[FileResult]:
    results = []
    for p in paths:
        if not p.is_file():
            continue
        result = FileResult(path=str(p))
        result.is_sensitive_name = check_filename(p)
        if not should_skip(p):
            result.findings = check_content(p)
        results.append(result)
    return results

def collect_paths(directory: Path, recursive: bool) -> list[Path]:
    if recursive:
        return sorted(p for p in directory.rglob('*') if p.is_file())
    return sorted(p for p in directory.iterdir() if p.is_file())

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_results(results: list[FileResult]) -> int:
    issues_found = 0
    for r in results:
        if not r.has_issues:
            print(f"[OK]     {r.path}")
            continue

        issues_found += 1
        print(f"[WARN]   {r.path}")
        if r.is_sensitive_name:
            print(f"           ! Sensitive filename detected")
        for f in r.findings:
            print(f"           line {f.line_no}: [{f.kind}] {f.text}")

    total = len(results)
    print(f"\n{total} file(s) checked — {issues_found} issue(s) found.")
    return issues_found

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Detect sensitive information in files.")
    parser.add_argument('-r', '--recursive', action='store_true', help='Scan recursively')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan (default: current directory)')
    parser.add_argument('--files', nargs='*', help='Explicit file list (used by pre-commit hook)')
    args = parser.parse_args()

    if args.files is not None:
        paths = [Path(f) for f in args.files]
    else:
        directory = Path(args.directory)
        if not directory.is_dir():
            print(f"Error: '{directory}' is not a directory.", file=sys.stderr)
            sys.exit(2)
        paths = collect_paths(directory, args.recursive)

    results = scan_files(paths)
    issues = print_results(results)
    sys.exit(1 if issues else 0)

if __name__ == '__main__':
    main()
