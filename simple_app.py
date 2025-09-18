#!/usr/bin/env python3
"""
シンプルなStreamlitアプリのテスト用
"""

import streamlit as st
from datetime import date

st.title("📧 テスト用アプリ")

# ファイルアップロードのテスト
uploaded_file = st.file_uploader(
    "ファイルをアップロード",
    type=['png', 'jpg', 'jpeg'],
    help="画像ファイルをアップロードしてください"
)

if uploaded_file is not None:
    st.success(f"ファイルがアップロードされました: {uploaded_file.name}")
    st.write(f"ファイルタイプ: {uploaded_file.type}")
    st.write(f"ファイルサイズ: {len(uploaded_file.getvalue())} bytes")
else:
    st.info("ファイルがアップロードされていません")

# シンプルな日付選択
selected_date = st.date_input("日付を選択", value=date.today())
st.write(f"選択された日付: {selected_date}")

if st.button("テストボタン"):
    st.success("ボタンが押されました！")