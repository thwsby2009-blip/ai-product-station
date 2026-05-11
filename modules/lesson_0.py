import streamlit as st

def run():

    st.title("🎓 AI 課程總入口 (課程1)")

    st.sidebar.subheader("📚 課程導覽")

    mode = st.selectbox(
        "請選擇課程：",
        [
            "0. 帳號註冊與環境檢查 (必做)",
            "1. ChatGPT 文字構思",
            "2. DALL-E 圖像生成 (Gemini 指令補強)",
            "3. Luma AI 影片生成 (生長演練)",
            "4. 2D 轉 3D 終極實作",
            "5. 專屬作業：Gemini 3D 公仔生成"
        ]
    )

    st.divider()

    # ===== 0 =====
    if mode.startswith("0"):
        st.header("0️⃣ 帳號註冊與環境檢查")
        st.link_button("ChatGPT", "https://chat.openai.com/")
        st.link_button("Google Colab", "https://colab.research.google.com/")
        st.link_button("Designer", "https://designer.microsoft.com/")

    # ===== 1 =====
    elif mode.startswith("1"):
        st.header("1️⃣ ChatGPT 文字構思")
        st.link_button("開啟 ChatGPT", "https://chat.openai.com/")

    # ===== 2 =====
    elif mode.startswith("2"):
        st.header("2️⃣ DALL·E 圖像生成")
        st.link_button("Microsoft Designer", "https://designer.microsoft.com/")

    # ===== 3 =====
    elif mode.startswith("3"):
        st.header("3️⃣ Luma AI 影片生成")
        st.link_button("Luma AI", "https://lumalabs.ai/dream-machine")

    # ===== 4 =====
    elif mode.startswith("4"):
        st.header("4️⃣ 2D → 3D")
        st.link_button("Meshy AI", "https://app.meshy.ai/")
        st.link_button("Tripo AI", "https://www.tripo3d.ai/app")

    # ===== 5 =====
    elif mode.startswith("5"):
        st.header("5️⃣ Gemini 3D 作業")
        st.link_button("Gemini", "https://gemini.google.com/")
