#!/usr/bin/env python3
"""
メルマガ「一日一知」生成システム - 統一エントリーポイント
両方のバージョンに対応したStreamlitアプリ
"""

import os
import sys
import streamlit as st

# USER_AGENT環境変数を最初に設定
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = "Newsletter-Generator/1.0 (Educational-Purpose)"

def main():
    """メイン関数"""
    st.set_page_config(
        page_title="メルマガ「一日一知」生成",
        page_icon="📧",
        layout="wide"
    )

    st.title("📧 メルマガ「一日一知」生成システム")

    # バージョン選択
    st.sidebar.header("🔧 バージョン選択")
    version = st.sidebar.radio(
        "使用するバージョンを選択してください",
        ["新バージョン (推奨)", "レガシー版"],
        help="新バージョンは改善されたUI構造、レガシー版は従来のシンプルな構造です"
    )

    try:
        if version == "新バージョン (推奨)":
            st.info("🚀 新バージョンを起動中...")

            # プロジェクトルートをパスに追加
            project_root = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, project_root)
            sys.path.insert(0, os.path.join(project_root, 'src'))

            from src.ui.main_controller import MainUIController
            from src.utils.logging_config import logger

            logger.info("=== 新バージョン起動 ===")
            controller = MainUIController()
            controller.run()

        else:
            st.info("📁 レガシー版を起動中...")

            from ui import NewsletterUI

            ui = NewsletterUI()
            ui.run()

    except ImportError as e:
        st.error(f"❌ インポートエラー: {e}")
        st.markdown("""
        **解決方法:**
        1. 必要なパッケージがインストールされていることを確認
        2. ファイル構造が正しいことを確認
        3. 環境変数（.env）が設定されていることを確認
        """)

    except Exception as e:
        st.error(f"❌ アプリケーションエラー: {e}")

        with st.expander("🔍 詳細エラー情報", expanded=False):
            import traceback
            st.code(traceback.format_exc())

            st.markdown("**デバッグ情報:**")
            st.write(f"- Python バージョン: {sys.version}")
            st.write(f"- 現在のディレクトリ: {os.getcwd()}")
            st.write(f"- 選択バージョン: {version}")

if __name__ == "__main__":
    main()