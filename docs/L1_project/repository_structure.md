# Repository Structure

```
github-tool-kit/
├── hooks/                          # Git フック（core.hooksPath で参照）
│   ├── pre-commit                  # コミット前: check-sensitive.py を実行
│   ├── pre-push                    # push 前: WIP コミットをブロック
│   └── post-merge                  # マージ後: リマインダー表示
│
├── scripts/                        # フックから呼ばれるスクリプト群
│   └── check-sensitive/
│       ├── check-sensitive.py      # 機密情報スキャナ（メイン実装）
│       ├── .check-sensitive-ignore # スキャン除外パターン定義
│       └── README.md               # check-sensitive の仕様・gitleaks 比較
│
├── .claude/
│   └── settings.local.json         # Claude Code 許可設定（gitignore 対象）
│
├── .gitignore                      # .DS_Store, .claude/ を除外
└── README.md                       # グローバルフック設定手順
```

## 各ディレクトリの責務

### `hooks/`
git の `core.hooksPath` に設定するフック本体。フック自体はロジックを持たず、`scripts/` 以下のスクリプトを呼び出す薄いラッパーとなっている。

根拠: `hooks/pre-commit:5-6`（`SCRIPT_DIR` 経由で `scripts/` を参照）

### `scripts/check-sensitive/`
フックから独立したスタンドアロンスクリプト。`--files` オプションで pre-commit フックから呼ばれる他、手動での任意ディレクトリスキャンにも対応する。

根拠: `scripts/check-sensitive/check-sensitive.py:217-235`

### `.check-sensitive-ignore`
`fnmatch` 形式のグロブパターン。スキャナ自身（`check-sensitive.py`）と `*.example` がデフォルトで登録済み。

根拠: `scripts/check-sensitive/.check-sensitive-ignore:6,9`
