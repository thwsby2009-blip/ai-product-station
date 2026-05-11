import streamlit as st

# 1. 頁面基礎設定
st.set_page_config(
    page_title="AI 產品設計全流程工作站",
    page_icon="🤖",
    layout="wide"
)

# --- 側邊欄設計 ---
st.sidebar.title("🎓 課程工作站")
st.sidebar.info("講師：嚴 稑 臻 | 網管開發助手：Gemini")

# --- 側邊欄：分組選單 ---
st.sidebar.subheader("📅 今日課程專區 (115.04.20)")
# 將今天的課程獨立出來
today_mode = st.sidebar.radio(
    "今日實作項目：",
    ["🐍 Google Colab 雲端開發實作"]
)

st.sidebar.divider() # 加入分隔線

st.sidebar.subheader("⏪ 上次課程回顧")
past_mode = st.sidebar.selectbox(
    "回顧往期單元：",
    [
        "--- 請選擇 ---",
        "0. 帳號註冊與環境檢查 (必做)",
        "1. ChatGPT 文字構思",
        "2. DALL-E 圖像生成 (Gemini 指令補強)",
        "3. Luma AI 影片生成 (生長演練)",
        "4. 2D 轉 3D 終極實作",
        "5. 專屬作業：Gemini 3D 公仔生成"
    ]
)

# --- 主頁面邏輯判斷 ---

# 優先處理今日課程
if today_mode == "🐍 Google Colab 雲端開發實作" and past_mode == "--- 請選擇 ---":
    st.header("🐍 今日重點：Google Colab 雲端程式開發")
    st.markdown("""
    ### 🚀 歡迎來到今日實作單元！
    本單元將引導您進入 Google Colab 進行高效能的 Python 開發與 AI 模型測試。
    
    * **無需安裝**：完全在瀏覽器執行。
    * **GPU 加速**：適合跑複雜的 AI 運算。
    * **存檔便利**：自動儲存於您的 Google Drive。
    """)
    
    # 醒目的跳轉按鈕
    st.link_button("🔥 立即開啟 Google Colab 工作站", "https://colab.research.google.com/", use_container_width=True)
    
    st.info("💡 提示：進到 Colab 後，請確認右上角是否已登入您的 Google 帳號。")

# 處理舊有課程回顧
elif past_mode != "--- 請選擇 ---":
    if past_mode == "0. 帳號註冊與環境檢查 (必做)":
        st.header("🔑 實作前置準備")
        st.link_button("ChatGPT 登入", "https://chat.openai.com/")
        st.link_button("Microsoft Designer", "https://designer.microsoft.com/")

    elif past_mode == "1. ChatGPT 文字構思":
        st.header("🧠 ChatGPT 產品創意發想")
        st.link_button("🚀 前往 ChatGPT", "https://chat.openai.com/")

    elif past_mode == "2. DALL-E 圖像生成 (Gemini 指令補強)":
        st.header("🎨 DALL-E 3 圖像核心")
        st.link_button("🚀 前往 Microsoft Designer", "https://designer.microsoft.com/")

    elif past_mode == "3. Luma AI 影片生成 (生長演練)":
        st.header("🎬 Luma AI 影片生成")
        st.link_button("🚀 前往 Luma AI", "https://lumalabs.ai/dream-machine")

    elif past_mode == "4. 2D 轉 3D 終極實作":
        st.header("🔮 2D 轉 3D 核心實作站")
        st.link_button("💎 開啟 Meshy AI", "https://app.meshy.ai/")
        st.link_button("⚡ 開啟 Tripo AI", "https://www.tripo3d.ai/app")

    elif past_mode == "5. 專屬作業：Gemini 3D 公仔生成":
        st.header("🧸 實作專案：生成你的專屬 3D 公仔")
        st.link_button("👉 前往 Google Gemini", "https://gemini.google.com/")
