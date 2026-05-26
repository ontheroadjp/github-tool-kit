# Policy

## 技術選定ポリシー

- **言語**: Bash（フック）+ Python 3.10+（スクリプト）。インストール不要で広く利用可能なランタイムのみ使用する
- **外部ツール非採用の根拠**: gitleaks 等の OSS と比較検討した結果、外部バイナリへの依存を避け、ルールをこのリポジトリで一元管理するため `check-sensitive.py` 単体運用を選択（`scripts/check-sensitive/README.md:62-96` に判断経緯を記録）
- **gitleaks への移行基準**: 外部バイナリ依存が許容される状況になった場合、または組み込みルール数が重要になった場合（同 README に具体的な移行パターンあり）

## セキュリティ方針

- **誤検知対策**: `.check-sensitive-ignore` ファイルでファイル単位のスキップパターンを管理（`scripts/check-sensitive/.check-sensitive-ignore`）
- **行単位抑制**: `# nosec` コメントで特定行をスキャン対象外にできる（`scripts/check-sensitive/check-sensitive.py:116`）
- **例外ファイル排除**: `*.example` ファイルはデフォルトで除外（プレースホルダ値を含む意図的なファイルのため）
- **プライベート IP 除外**: `10.x`, `172.16-31.x`, `192.168.x` は検出対象外（`check-sensitive.py:22`）

## 禁止事項

- スキャン対象の拡張子を binary/media ファイルに広げてはならない（`SKIP_EXTENSIONS` で定義済み、`check-sensitive.py:82-90`）
- `.check-sensitive-ignore` に `check-sensitive.py` 自体を含めること（パターン文字列がリテラルとして存在するため、デフォルトで除外済み）
- `--no-verify` の常用。緊急回避手段として案内するが、日常的に使うことは意図していない
