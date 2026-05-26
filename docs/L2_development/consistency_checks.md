# Consistency Checks

## フック動作確認

### pre-commit フック
`check-sensitive.py` のパスが正しく解決されることを確認する:

```bash
# pre-commit が参照するパスを手動確認
SCRIPT_DIR="$(cd "$(dirname "hooks/pre-commit")/../scripts" && pwd)"
ls "$SCRIPT_DIR/check-sensitive/check-sensitive.py"
```

根拠: `hooks/pre-commit:5-6`

### pre-push フック
WIP コミットのブロック条件:
- 最新コミットのサブジェクトが `[WIP]` または `[wip]` で始まること
- かつ `GIT_AUTHOR_DATE` が最新コミットと異なること

根拠: `hooks/pre-push:6-13`

## スキャナ整合性確認

`.check-sensitive-ignore` に記載されたパターンが実際にスキップされるか:

```bash
python3 scripts/check-sensitive/check-sensitive.py --files scripts/check-sensitive/check-sensitive.py
# → [SKIP] と表示されること
```

根拠: `scripts/check-sensitive/.check-sensitive-ignore:6`

## 未確認事項

| 項目 | 理由 | 確認手順 |
|---|---|---|
| テストスイートの有無 | `tests/` ディレクトリが存在しない | `find . -name "*.bats" -o -name "test_*.py"` で確認 |
| CI パイプライン | `.github/` ディレクトリが存在しない | GitHub リポジトリの Actions タブを確認 |
