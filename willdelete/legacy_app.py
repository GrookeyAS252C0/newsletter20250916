#!/usr/bin/env python3
"""
Legacy ui.py を使用したStreamlitアプリ
"""

import os
import sys

# USER_AGENT環境変数を設定
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = "Newsletter-Generator/1.0 (Educational-Purpose)"

try:
    from ui import NewsletterUI

    def main():
        """メイン関数"""
        ui = NewsletterUI()
        ui.run()

    if __name__ == "__main__":
        main()

except Exception as e:
    import streamlit as st
    st.error(f"❌ アプリケーションの起動に失敗しました: {e}")
    import traceback
    st.text(traceback.format_exc())