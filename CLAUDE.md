# CLAUDE.md

このファイルは AI 運用の起点となる情報をまとめる。Claude Code がこのリポジトリで作業する際はここを先に読む。

## このリポジトリについて

作業開始時に `README.md` の以下のセクションを読み、リポジトリ固有のコンテキストを把握すること:

- **Scripts / Hooks**: アクティブな機能一覧（スクリプトとフックの対応）
- **Design Principles**: 守るべき設計制約（外部依存ゼロ、単一リポジトリ管理等）
- **Deployment**: インストール手順

## リポジトリ構成の要点

- `hooks/`: git の `core.hooksPath` に設定するフック。ロジックは持たず `scripts/` を呼び出す
- `scripts/check-sensitive/`: 機密情報スキャナ本体（Python 3.10+）
- ビルドステップなし。テストスイートなし。CI 未設定

詳細: `docs/L1_project/repository_structure.md`

## Custom Command の使い分け（AI 向けルール）

**重要: ユーザーから作業指示を受けたら、独自調査を行わずに直ちに `/work` を呼ぶこと。調査は `/work` 内で行う。**

- **work.md**: ユーザーは常にこれを呼ぶ。ゲート確認・ワークスペース管理・現状調査・ルーティング判定を行い、task.md または patch.md へ委譲する。
  - docs 変更不要 → patch.md を Read して patch フロー（issue/PR なし、branch + commit → ユーザーが ff-merge）
  - docs 変更あり → task.md を Read して task フロー（issue 自動生成 → 実装 → ドラフト PR 作成 → /docs-sync へ引き継ぎ）
- **task.md**: docs 変更を伴う実装専用。work.md から Read 経由で呼ばれる。
- **patch.md**: ドキュメント変更を伴わない軽微な修正専用。work.md から Read 経由で呼ばれる。
- **docs-sync.md**: git diff を事実として docs を最小更新し、ドラフト PR を公開する。
- **init-docs.md**: リポジトリ実態の全体把握と設計ドキュメント再構築。docs-sync が説明不能になった時点で呼ぶ。

## ルーティング判定の基準

「この変更で `docs/*` への追加・変更・削除が必要か？」— Yes なら task フロー、No なら patch フロー。

## 重要な制約

- 外部依存を導入してはならない（Python 標準ライブラリのみ使用）
- `check-sensitive.py` への変更はパターンの追加・変更を意味するため、コミットメッセージに変更内容を明記すること
- `.check-sensitive-ignore` のパターンは必要最小限にとどめること
