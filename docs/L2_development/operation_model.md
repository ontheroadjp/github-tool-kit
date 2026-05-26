# Operation Model

## セットアップ（グローバルフック）

```bash
# 1. このリポジトリをクローン
git clone https://github.com/ontheroadjp/github-tool-kit.git

# 2. グローバルフックパスを設定
git config --global core.hooksPath /path/to/github-tool-kit/hooks

# 3. 設定確認
git config --global core.hooksPath
```

根拠: `README.md:19-37`

## 要件

- Git 2.9+（`core.hooksPath` サポートのため）
- Python 3.10+（`check-sensitive.py` の実行に必要）

根拠: `README.md:43-44`

## 手動スキャン

```bash
# カレントディレクトリをスキャン（非再帰）
python3 scripts/check-sensitive/check-sensitive.py

# 特定ディレクトリを再帰スキャン
python3 scripts/check-sensitive/check-sensitive.py -r path/to/dir

# 明示的なファイルリストをスキャン
python3 scripts/check-sensitive/check-sensitive.py --files file1.py file2.yaml
```

根拠: `scripts/check-sensitive/README.md:28-43`, `check-sensitive.py:217-235`

終了コード: 問題なし=0、問題あり=1

## グローバルフック解除

```bash
git config --global --unset core.hooksPath
```

根拠: `README.md:35-37`

## ビルド・テスト

現時点では未定義。スクリプトはインタプリタ言語（Bash/Python）のため、ビルドステップは存在しない。テストスイートも未設定。
