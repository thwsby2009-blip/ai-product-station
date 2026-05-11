import streamlit as st

st.set_page_config(page_title="AI 教學平台", layout="wide")

st.sidebar.title("🎓 AI 教學平台")

lesson = st.sidebar.selectbox(
    "選擇課程",
    [
        "0. 帳號註冊",
        "1. ChatGPT",
        "2. DALL-E",
        "3. Luma AI",
        "4. 2D轉3D",
        "5. 公仔生成",
        "4/20 Pandas課程",
        "4/27 AI整合",
        "Colab"
    ]
)

# ======================
# 模組導入
# ======================

if lesson == "0. 帳號註冊":
    from modules.lesson_0 import run
    run()

elif lesson == "1. ChatGPT":
    from modules.lesson_1 import run
    run()

elif lesson == "4/20 Pandas課程":
    from modules.lesson_420 import run
    run()

elif lesson == "4/27 AI整合":
    from modules.lesson_427 import run
    run()

elif lesson == "Colab":
    from modules.colab import run
    run()
