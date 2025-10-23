# 削除予定ファイル

このフォルダには、プロジェクトから削除予定の不要なファイルが格納されています。

## 移動したファイル一覧

### 旧アプリケーションファイル
- **app.py** - 旧統一エントリーポイント（現在は`streamlit_app.py`を使用）
- **legacy_app.py** - Legacy版アプリ（ui.pyを使用）
- **simple_app.py** - テスト用シンプルアプリ
- **ui.py** - 旧UIファイル（現在は`streamlit_app.py`内のコントローラーシステムを使用）

### 削除された名言機能関連
名言機能は手動入力に変更されたため、以下のファイルは不要になりました：

- **teacher_quotes_service.py** - 先生の名言サービス
- **llm_quote_formatter.py** - LLM名言フォーマッター
- **meigen_converter.py** - 名言コンバーター
- **meigen_db_20250916.txt** - 名言データベース（62KB）
- **meigen_meta.json** - 名言メタデータ
- **transcript_quotes_balanced_detailed.txt** - トランスクリプト（38KB）

## 移動日時
2025年10月23日

## 削除前の確認事項
- ✅ 上記ファイルは現在のプロジェクトで参照されていないことを確認済み
- ✅ `newsletter_generator.py`で名言機能はコメントアウト済み
- ✅ メインアプリは`streamlit_app.py`に統一済み

## 今後の対応
問題がなければ、このフォルダごと削除してください。
