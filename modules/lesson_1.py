
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def run():

    # ❗不能再 set_page_config（這是關鍵修正）

    # 初始化 session_state
    if 'raw_data' not in st.session_state:
        st.session_state['raw_data'] = []

    if 'openrouter_key' not in st.session_state:
        st.session_state['openrouter_key'] = ""

    # =========================
    # sidebar
    # =========================
    with st.sidebar:
        st.header("🔑 AI 設定")

        st.session_state['openrouter_key'] = st.text_input(
            "OpenRouter API Key",
            type="password",
            value=st.session_state['openrouter_key']
        )

        st.header("📡 數據來源")

        url = st.text_input("網址", "https://tw.yahoo.com/")

        if st.button("抓取資料"):
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")

                data = []
                for t in soup.find_all(["h1", "h2", "h3", "a", "p"]):
                    text = t.get_text().strip()
                    if 15 < len(text) < 200:
                        data.append(text)

                st.session_state['raw_data'] = list(dict.fromkeys(data))
                st.success(f"抓到 {len(data)} 筆")

            except Exception as e:
                st.error(e)

    # =========================
    # main UI
    # =========================
    st.title("📊 Lesson 1：AI 數據分析")

    if not st.session_state['raw_data']:
        st.info("請先抓資料")
        return

    keyword = st.text_input("關鍵字")

    filtered = [
        x for x in st.session_state['raw_data']
        if keyword.lower() in x.lower()
    ]

    df = pd.DataFrame({
        "選擇": [False] * len(filtered),
        "內容": filtered
    })

    edited = st.data_editor(df, use_container_width=True)

    selected = edited[edited["選擇"] == True]["內容"].tolist()

    if selected:
        st.success(f"已選 {len(selected)} 筆")

    st.markdown("---")

    st.header("🤖 AI 分析")

    model = st.selectbox("模型", [
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemini-flash-1.5-exp:free"
    ])

    if st.button("分析"):

        if not st.session_state['openrouter_key']:
            st.error("沒 key")
            return

        if not selected:
            st.warning("沒選資料")
            return

        prompt = "\n".join(selected)

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.session_state['openrouter_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        try:
            result = res.json()["choices"][0]["message"]["content"]
            st.markdown(result)
        except:
            st.error("API error")
