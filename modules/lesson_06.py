import streamlit as st

def run():

    st.title("📊 AI 簡報工具入口")

    st.sidebar.subheader("🧠 AI 簡報工具導覽")

    mode = st.selectbox(
        "請選擇工具：",
        [
            "0. AI Agent 型簡報",
            "1. Gamma",
            "2. Canva AI",
            "3. Manus AI",
            "4. Genspark AI Slides",
            "5. Tome",
            "6. Beautiful.ai",
            "7. Pitch",
            "8. Plus AI (Google Slides)",
            "9. SlidesAI",
            "10. Prezi AI",
            "11. Microsoft Copilot (PowerPoint)",
            "12. Google Gemini Slides"
        ]
    )

    st.divider()

    # ===== 0 =====
    if mode.startswith("0"):
        st.header("🧠 AI Agent 型簡報工具（最進階）")
        st.link_button("Manus AI", "https://manus.im/")
        st.link_button("Genspark AI Slides", "https://www.genspark.ai/")
        st.write("👉 特色：會自己研究＋生成完整簡報")

    # ===== 1 =====
    elif mode.startswith("1"):
        st.header("Gamma AI 簡報")
        st.link_button("開啟 Gamma", "https://gamma.app/")
        st.write("👉 快速生成商業簡報、提案、Pitch Deck")

    # ===== 2 =====
    elif mode.startswith("2"):
        st.header("Canva AI 簡報")
        st.link_button("開啟 Canva", "https://www.canva.com/")
        st.write("👉 視覺設計強、行銷簡報最佳")

    # ===== 3 =====
    elif mode.startswith("3"):
        st.header("Manus AI")
        st.link_button("開啟 Manus", "https://manus.im/")
        st.write("👉 AI 自動研究 + 自動生成完整簡報")

    # ===== 4 =====
    elif mode.startswith("4"):
        st.header("Genspark AI Slides")
        st.link_button("開啟 Genspark", "https://www.genspark.ai/")
        st.write("👉 AI 搜尋 + 自動簡報生成")

    # ===== 5 =====
    elif mode.startswith("5"):
        st.header("Tome AI 簡報")
        st.link_button("開啟 Tome", "https://tome.app/")
        st.write("👉 故事型、視覺敘事簡報")

    # ===== 6 =====
    elif mode.startswith("6"):
        st.header("Beautiful.ai")
        st.link_button("開啟 Beautiful.ai", "https://www.beautiful.ai/")
        st.write("👉 自動排版、企業簡報風格")

    # ===== 7 =====
    elif mode.startswith("7"):
        st.header("Pitch 簡報協作工具")
        st.link_button("開啟 Pitch", "https://pitch.com/")
        st.write("👉 團隊協作、Startup 簡報")

    # ===== 8 =====
    elif mode.startswith("8"):
        st.header("Plus AI (Google Slides)")
        st.link_button("開啟 Plus AI", "https://www.plusdocs.com/")
        st.write("👉 Google Slides AI 生成工具")

    # ===== 9 =====
    elif mode.startswith("9"):
        st.header("SlidesAI")
        st.link_button("開啟 SlidesAI", "https://www.slidesai.io/")
        st.write("👉 文字轉簡報（Google 外掛）")

    # ===== 10 =====
    elif mode.startswith("10"):
        st.header("Prezi AI")
        st.link_button("開啟 Prezi", "https://prezi.com/")
        st.write("👉 動態縮放式簡報風格")

    # ===== 11 =====
    elif mode.startswith("11"):
        st.header("Microsoft Copilot for PowerPoint")
        st.link_button(
            "開啟 Microsoft Copilot",
            "https://www.microsoft.com/microsoft-365/copilot"
        )
        st.write("👉 PowerPoint AI 助理，企業級整合")

    # ===== 12 =====
    elif mode.startswith("12"):
        st.header("Google Gemini for Slides")
        st.link_button(
            "開啟 Google Gemini",
            "https://workspace.google.com/gemini/"
        )
        st.write("👉 Google 生態 AI 簡報工具")
