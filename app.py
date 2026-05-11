import streamlit as st

st.set_page_config(page_title="AI 課程")

# 1️⃣ options 一定要先
options = {
    "0. AI 產品設計全流程工作站": "lesson_0",
    "1. AI 數據分析": "lesson_1",
    "2. 金流數據分析": "lesson_420",
    "3.4/27 AI整合": "lesson_427",
    "4.Google Colab 雲端程式開發": "colab"
}

# 2️⃣ UI
lesson_ui = st.selectbox("課程選擇", list(options.keys()))
lesson_key = options[lesson_ui]

st.write("你選的是：", lesson_key)
if lesson_key == "lesson_0":
    from modules.lesson_0 import run
    run()

elif lesson_key == "lesson_1":
    from modules.lesson_1 import run
    run()

elif lesson_key == "lesson_420":
    from modules.lesson_420 import run
    run()

elif lesson_key == "lesson_427":
    from modules.lesson_427 import run
    run()

elif lesson_key == "colab":
    from modules.colab import run
    run()
