# check-sensitive

Scans files for sensitive information and blocks commits that contain secrets, credentials, or other data that should not be pushed to a repository.

## What It Detects

| Category | Examples |
|---|---|
| IP addresses | IPv4, IPv6, private ranges (10.x, 172.16–31.x, 192.168.x) |
| Credentials | API keys, tokens, passwords, AWS access/secret keys |
| Private keys | RSA, EC, OpenSSH PEM headers, PEM certificates |
| Auth tokens | JWT, Bearer tokens, GitHub (`ghp_*`, `ghs_*`) |
| SaaS / cloud keys | Google API Key, Slack, Stripe, SendGrid, OpenAI, Anthropic, npm, PyPI, DigitalOcean, Twilio, Telegram Bot, Discord Bot |
| Connection strings | DB URLs with embedded password (postgres/mysql/mongodb/redis/amqp), Basic auth URLs, Azure connection strings |
| GCP credentials | Service account private key (`"private_key": "-----BEGIN`) |
| Sensitive paths | Absolute Unix (`/home/`, `/etc/`) and Windows paths |
| Sensitive filenames | `.env`, `.ssh`, `*.pem`, `*.key`, `*.p12`, `credentials.json`, etc. |
| PII | Email addresses, domain names, JP phone numbers, My Number, credit card numbers |

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

## Comparison with gitleaks

[gitleaks](https://github.com/gitleaks/gitleaks) is a widely-used OSS tool for secret detection. This section summarizes the tradeoffs considered when deciding whether to adopt it.

### gitleaks の強み

- コミュニティが維持する 150 以上の組み込みルール（新サービスのトークン形式が随時追加される）
- `git log` 全体をスキャンしてコミット履歴の漏洩を検出できる
- `.gitleaks.toml` による allowlist で誤検知を管理しやすい
- CI/CD との統合実績が豊富

### check-sensitive.py の強み

- 外部バイナリ不要（Python 3.10+ のみ）
- JP電話番号・マイナンバーなどロケール固有の PII ルールを自由に追加できる
- このリポジトリを single source of truth として管理できる
- ルールの追加・変更がコードレビューの対象になる

### 併用パターン（採用しない場合の参考）

gitleaks をシークレット検出のメインエンジンに据え、check-sensitive.py を PII 専用に絞る構成が考えられる。

```bash
# pre-commit (概念図)
gitleaks protect --staged --redact   # シークレット検出
python3 check-sensitive.py --files … # PII のみ（JP固有ルール）
```

この場合、check-sensitive.py から SaaS/クラウド系・接続文字列・証明書のパターンを削除し、PII カテゴリ（JP電話番号・マイナンバー・クレジットカード）だけ残す。

### 現状の判断

外部バイナリへの依存を避け、ルールをこのリポジトリで一元管理するため、check-sensitive.py 単体で運用する。gitleaks への移行が必要になった場合はこのセクションを起点に検討する。
