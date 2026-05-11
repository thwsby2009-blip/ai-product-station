import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai

def run():

    # ==========================================
    # 初始化 session_state
    # ==========================================
    if 'raw_data' not in st.session_state:
        st.session_state['raw_data'] = []

    if 'google_api_key' not in st.session_state:
        st.session_state['google_api_key'] = ""

    # ==========================================
    # Sidebar
    # ==========================================
    with st.sidebar:
        st.header("🔑 AI 設定 (Google Gemini)")

        st.session_state['google_api_key'] = st.text_input(
            "Google API Key",
            type="password",
            value=st.session_state['google_api_key']
        )

        st.markdown("---")
        st.header("📡 數據來源")

        source_url = st.text_input(
            "數據來源網址：",
            "https://tw.yahoo.com/"
        )

        if st.button("🛰️ 抓取資料"):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0'
                }
                res = requests.get(source_url, headers=headers, timeout=15)
                soup = BeautifulSoup(res.text, "html.parser")

                found = []
                for tag in soup.find_all(['h1', 'h2', 'h3', 'a', 'p']):
                    text = tag.get_text().strip()
                    if 15 < len(text) < 200:
                        found.append(text)

                st.session_state['raw_data'] = list(dict.fromkeys(found))
                st.success(f"成功抓取 {len(found)} 筆資料")

            except Exception as e:
                st.error(f"抓取失敗：{e}")

    # ==========================================
    # 主畫面
    # ==========================================
    st.title("📊 Lesson 1：AI 數據分析（Google Gemini版）")

    if not st.session_state['raw_data']:
        st.info("請先在左側抓取資料")
        return

    keyword = st.text_input("🔍 關鍵字過濾")

    filtered = [
        x for x in st.session_state['raw_data']
        if keyword.lower() in x.lower()
    ]

    st.subheader(f"資料數量：{len(filtered)}")

    df = pd.DataFrame({
        "選擇": [False] * len(filtered),
        "內容": filtered
    })

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        key="lesson1_table"
    )

    selected = edited_df[
        edited_df["選擇"] == True
    ]["內容"].tolist()

    if selected:
        st.success(f"已選擇 {len(selected)} 筆資料")

    # ==========================================
    # AI 分析區（Google Gemini）
    # ==========================================
    st.markdown("---")
    st.header("🤖 AI 分析（Google Gemini）")

    model_name = st.selectbox(
        "選擇模型",
        [
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
    )

    if st.button("🚀 開始分析"):

        if not st.session_state['google_api_key']:
            st.error("請輸入 Google API Key")
            return

        if not selected:
            st.warning("請至少選擇一筆資料")
            return

        try:
            genai.configure(api_key=st.session_state['google_api_key'])

            model = genai.GenerativeModel(model_name)

            prompt = f"""
你是一位專業新聞分析師，請分析以下內容：

{chr(10).join(selected)}

請提供：
1. 重點整理
2. 趨勢分析
3. 一句幽默評論
"""

            response = model.generate_content(prompt)

            st.subheader("📌 AI 分析結果")
            st.markdown(response.text)

            st.balloons()

        except Exception as e:
            st.error(f"AI 分析失敗：{e}")

    st.caption("Lesson 1 - Google Gemini 整合版")
