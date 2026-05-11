import streamlit as st

st.set_page_config(page_title="AI 課程")

# 1️⃣ options 一定要先
options = {
    "0. 帳號註冊": "lesson_0",
    "1. ChatGPT": "lesson_1",
    "4/20 Pandas課程": "lesson_420",
    "4/27 AI整合": "lesson_427",
    "Colab": "colab"
}

# 2️⃣ UI
lesson_ui = st.selectbox("課程選擇", list(options.keys()))
lesson_key = options[lesson_ui]

st.write("你選的是：", lesson_key)
