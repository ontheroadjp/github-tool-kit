# Specification Summary

## check-sensitive.py

エントリポイント: `scripts/check-sensitive/check-sensitive.py`

### CLI インターフェース

```
python3 check-sensitive.py [-r] [directory]
python3 check-sensitive.py --files file1 [file2 ...]
```

| 引数 | 説明 |
|---|---|
| `-r`, `--recursive` | ディレクトリを再帰スキャン |
| `directory` | スキャン対象ディレクトリ（デフォルト: `.`） |
| `--files` | 明示的なファイルリスト（pre-commit フックはこちらを使用） |

根拠: `check-sensitive.py:218-222`

### 検出カテゴリ（`SENSITIVE_PATTERNS`）

| カテゴリ | 代表的な検出対象 |
|---|---|
| IP アドレス | IPv4（プライベート除外）, IPv6 |
| クレデンシャル | API キー, トークン, パスワード, AWS キー |
| 秘密鍵 | RSA/EC/OpenSSH PEM ヘッダ, 証明書 |
| 認証トークン | JWT, Bearer トークン, GitHub token |
| SaaS/クラウドキー | Google, Slack, Stripe, SendGrid, OpenAI, Anthropic, npm, PyPI, DigitalOcean, Twilio, Telegram, Discord |
| 接続文字列 | DB URL（postgres/mysql/mongodb/redis/amqp）, Basic auth URL, Azure |
| GCP | サービスアカウント秘密鍵 |
| センシティブパス | `/home/`, `/etc/`, Windows 絶対パス 等 |
| PII | メールアドレス, ドメイン名, JP 電話番号, マイナンバー, クレジットカード番号 |

根拠: `check-sensitive.py:21-60`

### センシティブファイル名検出（`SENSITIVE_FILENAMES`）

`.env`, `.claude`, `.aws`, `.ssh`, `.gnupg`, `id_rsa`, `id_ed25519`, `credentials.json`, `secrets.*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`

根拠: `check-sensitive.py:63-79`

### スキップ条件

1. `.check-sensitive-ignore` パターンにマッチするファイル（`check-sensitive.py:125-128`）
2. `SKIP_EXTENSIONS` に含まれるバイナリ系拡張子（`check-sensitive.py:82-90`）
3. シェバング行（`#!` で始まる 1 行目, `check-sensitive.py:144-145`）
4. `.check-sensitive-whitelist` に記載された文字列を含むマッチ（マッチを含む行全体に対して部分一致で照合して抑制、エントリが長いほど絞り込み精度が上がる。例: `hoge.com` はそのドメインを含む全行を抑制、`hoge.com/foo/bar` はそのパスを含む行のみ抑制、`check-sensitive.py:135-136`）
5. SVG パスコマンド（`M`/`L`/`C` 等）直後の IPv4 マッチ（座標の誤検知を防止、`check-sensitive.py:140`）

### 出力形式

```
[OK]     src/main.py
[WARN]   config/settings.py
           line 4: [Secret/token] api_token = "..."
[WARN]   .env
           ! Sensitive filename detected

3 file(s) checked — 2 issue(s) found.
```

色出力は TTY 接続時のみ有効（`check-sensitive.py:179`）

### 終了コード

- `0`: 問題なし
- `1`: 問題あり（コミットをブロックする）
- `2`: 引数エラー

根拠: `check-sensitive.py:233-236`

---

## hooks/pre-commit

`git diff --cached --name-only --diff-filter=ACM` でステージ済みファイル（追加・変更・コピー）を取得し、`check-sensitive.py --files` に渡す。削除ファイルは対象外。

根拠: `hooks/pre-commit:13-17`, `hooks/pre-commit:26`

---

## hooks/pre-push

最新コミットのサブジェクトが `[WIP]`/`[wip]` で始まる場合、`GIT_AUTHOR_DATE` との比較で WIP コミットへの push を検出してブロックする。

根拠: `hooks/pre-push:6-13`

---

## hooks/post-merge

マージ後にバージョン番号変更とコードクリーニングのリマインダーをシアン色で表示する。ブロック動作なし。

根拠: `hooks/post-merge:3-17`
