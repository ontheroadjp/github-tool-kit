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
    ("IPv4 address",          re.compile(r'\b(?!(?:10|127)\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b')),
    ("IPv6 address",          re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')),
    ("Absolute Unix path",    re.compile(r'(?<!["\w])/(?:home|root|Users|var|etc|opt|tmp|srv|usr)/[\w./-]+')),
    ("Absolute Windows path", re.compile(r'[A-Za-z]:\\(?:Users|Windows|Program Files)[\\\w\s.-]+')),
    ("API key (generic)",     re.compile(r'(?i)(?:api[_-]?key|apikey|access[_-]?key)\s*[:=]\s*["\']?[\w\-]{16,}["\']?')),
    ("Secret/token",          re.compile(r'(?i)(?:secret|token|password|passwd|pwd)\s*[:=]\s*["\']?[\w\-]{16,}["\']?')),
    ("AWS access key",        re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ("AWS secret key",        re.compile(r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']?[\w/+]{40}["\']?')),
    ("Private key header",    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ("GitHub token",          re.compile(r'\bghp_[0-9A-Za-z]{36}\b|\bghs_[0-9A-Za-z]{36}\b')),
    ("JWT",                   re.compile(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b')),
    ("Bearer token",          re.compile(r'(?i)\bBearer\s+[\w\-._~+/]{20,}=*')),
    # SaaS / cloud API keys
    ("Google API key",        re.compile(r'\bAIza[0-9A-Za-z\-_]{35}\b')),
    ("Slack token",           re.compile(r'\bxox[bpas]-[0-9A-Za-z\-]+')),
    ("Stripe key",            re.compile(r'\b(?:sk|pk)_live_[0-9a-zA-Z]{24,}\b')),
    ("SendGrid API key",      re.compile(r'\bSG\.[a-zA-Z0-9._\-]{66}\b')),
    ("OpenAI API key",        re.compile(r'\bsk-[a-zA-Z0-9]{48}\b')),
    ("Anthropic API key",     re.compile(r'\bsk-ant-[a-zA-Z0-9\-_]{90,}\b')),
    ("npm token",             re.compile(r'\bnpm_[A-Za-z0-9]{36}\b')),
    ("PyPI token",            re.compile(r'\bpypi-[A-Za-z0-9\-_]{50,}\b')),
    ("DigitalOcean token",    re.compile(r'\bdop_v1_[a-f0-9]{64}\b')),
    ("Twilio Account SID",    re.compile(r'\bAC[a-f0-9]{32}\b')),
    ("Telegram Bot token",    re.compile(r'\b\d{8,10}:[A-Za-z0-9_\-]{35}\b')),
    ("Discord Bot token",     re.compile(r'\b[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}\b')),
    # Connection strings / URLs with embedded credentials
    ("DB connection string",  re.compile(r'(?i)(?:postgres|mysql|mongodb(?:\+srv)?|redis|amqp)://[^:/@\s]+:[^@\s]+@')),
    ("Basic auth URL",        re.compile(r'https?://[^/:@\s]+:[^/@\s]+@[^/\s]')),
    ("Azure connection str",  re.compile(r'(?i)DefaultEndpointsProtocol=https;AccountName=\w+;AccountKey=')),
    # Keys and certificates
    ("GCP service account",   re.compile(r'"private_key"\s*:\s*"-----BEGIN PRIVATE KEY')),
    ("Certificate",           re.compile(r'-----BEGIN CERTIFICATE-----')),
    # PII
    ("JP phone number",       re.compile(r'\b0\d{1,4}[-\s]\d{1,4}[-\s]\d{4}\b')),
    ("My Number (JP)",        re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')),
    ("Credit card number",    re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b')),
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

def load_ignore_patterns() -> list[str]:
    ignore_file = Path(__file__).parent / '.check-sensitive-ignore'
    if not ignore_file.is_file():
        return []
    lines = ignore_file.read_text(encoding='utf-8').splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith('#')]

def load_whitelist_patterns() -> list[str]:
    whitelist_file = Path(__file__).parent / '.check-sensitive-whitelist'
    if not whitelist_file.is_file():
        return []
    lines = whitelist_file.read_text(encoding='utf-8').splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith('#')]

def is_ignored(path: Path, ignore_patterns: list[str]) -> bool:
    import fnmatch
    s = str(path)
    return any(fnmatch.fnmatch(s, pat) or fnmatch.fnmatch(path.name, pat) for pat in ignore_patterns)

def is_whitelisted(matched_text: str, whitelist: list[str]) -> bool:
    return any(entry in matched_text for entry in whitelist)

def should_skip(path: Path) -> bool:
    return path.suffix.lower() in SKIP_EXTENSIONS

def check_filename(path: Path) -> bool:
    return bool(SENSITIVE_FILENAMES.search(str(path)))

def check_content(path: Path, whitelist: list[str]) -> list[Finding]:
    findings = []
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return findings

    for lineno, line in enumerate(text.splitlines(), 1):
        if lineno == 1 and line.startswith('#!'):
            continue
        snippet = line.strip()[:120]
        for kind, pattern in SENSITIVE_PATTERNS:
            matches = [m.group() for m in pattern.finditer(line)
                       if not is_whitelisted(m.group(), whitelist)]
            if matches:
                findings.append(Finding(lineno, kind, snippet))
                break
    return findings

def scan_files(paths: list[Path], ignore_patterns: list[str], whitelist: list[str]) -> list[FileResult]:
    results = []
    for p in paths:
        if not p.is_file():
            continue
        if is_ignored(p, ignore_patterns):
            print(f"{cyan('[SKIP]')}   {p} (ignored)")
            continue
        result = FileResult(path=str(p))
        result.is_sensitive_name = check_filename(p)
        if not should_skip(p):
            result.findings = check_content(p, whitelist)
        results.append(result)
    return results

def collect_paths(directory: Path, recursive: bool) -> list[Path]:
    if recursive:
        return sorted(p for p in directory.rglob('*') if p.is_file())
    return sorted(p for p in directory.iterdir() if p.is_file())

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

_USE_COLOR = sys.stdout.isatty()

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text

def green(t):  return _c("32", t)
def yellow(t): return _c("33", t)
def red(t):    return _c("31", t)
def cyan(t):   return _c("36", t)
def bold(t):   return _c("1",  t)

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_results(results: list[FileResult]) -> int:
    issues_found = 0
    for r in results:
        if not r.has_issues:
            print(f"{green('[OK]')}     {r.path}")
            continue

        issues_found += 1
        print(f"{yellow('[WARN]')}   {r.path}")
        if r.is_sensitive_name:
            print(f"           {red('! Sensitive filename detected')}")
        for f in r.findings:
            print(f"           line {f.line_no}: {yellow(f'[{f.kind}]')} {f.text}")

    total = len(results)
    summary_issues = red(str(issues_found)) if issues_found else green(str(issues_found))
    print(f"\n{total} file(s) checked — {summary_issues} issue(s) found.")
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

    ignore_patterns = load_ignore_patterns()
    whitelist = load_whitelist_patterns()
    results = scan_files(paths, ignore_patterns, whitelist)
    issues = print_results(results)
    sys.exit(1 if issues else 0)

if __name__ == '__main__':
    main()
