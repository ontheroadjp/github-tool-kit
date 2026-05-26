# Project Overview

## 目的

日常的な GitHub ワークフローに組み込む Git フックとスクリプトのコレクション。`core.hooksPath` によるグローバル適用を主ユースケースとし、全リポジトリに一括で適用できる。

根拠: `README.md:1-3`, `README.md:19-27`

## 技術スタック

| 要素 | 内容 | 根拠 |
|---|---|---|
| 言語 | Bash, Python 3.10+ | `README.md:43-44`, `hooks/pre-commit:1`, `scripts/check-sensitive/check-sensitive.py:1` |
| パッケージマネージャ | なし（外部依存ゼロ） | `scripts/check-sensitive/README.md:62-97` |
| CI/CD | 未設定 | `.github/` ディレクトリが存在しない |
| テストフレームワーク | 未設定 | テストファイルが存在しない |

## 実装済み機能

| 機能 | エントリポイント | 説明 |
|---|---|---|
| 機密情報スキャン | `scripts/check-sensitive/check-sensitive.py` | ステージ済みファイルまたは任意ファイルの機密情報検出 |
| pre-commit フック | `hooks/pre-commit` | コミット前に `check-sensitive.py` を自動実行 |
| pre-push フック | `hooks/pre-push` | WIP コミットを含む push をブロック |
| post-merge フック | `hooks/post-merge` | マージ後にリマインダーを表示 |

## デプロイモデル

```bash
git config --global core.hooksPath /path/to/github-tool-kit/hooks
```

このコマンドにより、マシン上のすべての git リポジトリにフックが適用される。
