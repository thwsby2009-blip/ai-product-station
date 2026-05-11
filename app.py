import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 0. 全域設定與 Session State 初始化
# ==========================================
st.set_page_config(page_title="AI 課程工作站", page_icon="🤖", layout="wide")

# 初始化變數，防止 KeyError
if 'raw_data' not in st.session_state: st.session_state['raw_data'] = []
if 'google_api_key' not in st.session_state: st.session_state['google_api_key'] = ""

# ==========================================
# 1. 側邊欄選單設計
# ==========================================
st.sidebar.title("🎓 AI 課程工作站")
st.sidebar.info("講師：嚴 稑 臻 | 助手：Gemini")

st.sidebar.subheader("📅 今日課程專區")
today_mode = st.sidebar.radio(
    "請選擇實作單元：",
    ["📊 Pandas 數據分析 (115.04.27)", "🤖 AI 數據整合實作 (115.04.20)", "🐍 Google Colab"]
)

st.sidebar.divider()
st.sidebar.subheader("⏪ 往期課程回顧")
past_mode = st.sidebar.selectbox(
    "回顧單元：",
    ["--- 請選擇 ---", "0. 帳號註冊", "1. ChatGPT", "2. DALL-E", "3. Luma AI", "4. 2D 轉 3D", "5. Gemini 3D 公仔"]
)

# ==========================================
# 2. 邏輯判斷
# ==========================================

# --- [優先處理：往期回顧] ---
if past_mode != "--- 請選擇 ---":
    st.header(f"⏪ 往期回顧：{past_mode}")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🔑 申請 Google AI Key", "https://aistudio.google.com/app/apikey", use_container_width=True)
        st.link_button("🎨 Microsoft Designer", "https://designer.microsoft.com/", use_container_width=True)
    with col2:
        st.link_button("🎬 Luma AI 影片生成", "https://lumalabs.ai/dream-machine", use_container_width=True)
        st.link_button("🧊 Meshy 2D 轉 3D", "https://www.meshy.ai/", use_container_width=True)
    st.info("💡 如需執行今日實作，請將上方下拉選單改回『--- 請選擇 ---』。")

# --- [今日模式：4月27日 Pandas 數據分析] ---
elif today_mode == "📊 Pandas 數據分析 (115.04.27)":
    st.title("📊 Pandas 數據全流程分析 (P77-P90)")
    
    # 模擬數據：收入與支出
    df_inc = pd.DataFrame({
        "年齡組": ["20-30", "30-40", "40-50", "50+"],
        "月薪": [38000, 55000, 72000, 85000],
        "獎金": [4000, 10000, 15000, 25000]
    })
    df_exp = pd.DataFrame({
        "年齡組": ["20-30", "30-40", "40-50", "50+"],
        "日常開銷": [22000, 30000, 35000, 38000],
        "房貸車貸": [5000, 15000, 20000, 10000]
    })

    st.subheader("1️⃣ 數據合併與特徵工程 (Merge & Calculation)")
    df_merged = pd.merge(df_inc, df_exp, on="年齡組")
    df_merged["總收入"] = df_merged["月薪"] + df_merged["獎金"]
    df_merged["總支出"] = df_merged["日常開銷"] + df_merged["房貸車貸"]
    df_merged["可支配所得"] = df_merged["總收入"] - df_merged["總支出"]
    st.dataframe(df_merged, use_container_width=True)

    st.divider()
    st.subheader("2️⃣ 視覺化分析報告 (Plotly)")
    tab1, tab2 = st.tabs(["📊 儲蓄趨勢", "🍰 收入佔比"])
    with tab1:
        st.plotly_chart(px.line(df_merged, x="年齡組", y="可支配所得", title="各年齡層平均儲蓄能力", markers=True))
    with tab2:
        st.plotly_chart(px.pie(df_merged, values="總收入", names="年齡組", title="整體收入結構比"))

# --- [今日模式：4月20日 AI 數據整合] ---
elif today_mode == "🤖 AI 數據整合實作 (115.04.20)":
    st.title("🤖 Gemini AI 數據自動化實作")
    
    with st.sidebar:
        st.header("🔑 API 設定")
        st.markdown("[👉 獲取免費 Google API Key](https://aistudio.google.com/app/apikey)")
        api_input = st.text_input("Google API Key:", type="password", value=st.session_state['google_api_key'])
        if api_input: st.session_state['google_api_key'] = api_input
        
        st.divider()
        st.header("📡 數據爬取")
        target_url = st.text_input("爬取網址:", "https://tw.news.yahoo.com/")
        if st.button("🛰️ 執行即時抓取"):
            try:
                res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                # 抓取具有代表性的標題
                titles = [t.get_text().strip() for t in soup.find_all(['h2', 'h3', 'a']) if 15 < len(t.get_text().strip()) < 80]
                st.session_state['raw_data'] = list(dict.fromkeys(titles))[:25]
                st.success("✅ 資料抓取成功！")
            except Exception as e:
                st.error(f"抓取失敗: {e}")

    # 主畫面邏輯
    if st.session_state['raw_data']:
        st.subheader("🔍 第一步：篩選感興趣的新聞")
        df_select = pd.DataFrame({"勾選": [False] * len(st.session_state['raw_data']), "標題內容": st.session_state['raw_data']})
        edited_df = st.data_editor(df_select, hide_index=True, use_container_width=True, key="news_editor_420")
        selected_list = edited_df[edited_df["勾選"] == True]["標題內容"].tolist()

        st.divider()
        st.subheader("🧠 第二步：Gemini 2.0 Flash 深度分析")
        
        if st.button("🚀 啟動 AI 智慧總結", type="primary"):
            if not st.session_state['google_api_key']:
                st.error("❌ 請先在左側輸入 Google API Key！")
            elif not selected_list:
                st.warning("⚠️ 請至少勾選一項內容。")
            else:
                try:
                    with st.spinner("Gemini 正在分析大數據中..."):
                        # 配置 Google Gemini
                        genai.configure(api_key=st.session_state['google_api_key'])
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        
                        prompt = f"""
                        你是一位專業的新聞分析師。以下是從網路抓取的最新資訊：
                        {chr(10).join(selected_list)}
                        
                        請針對上述內容進行：
                        1. 綜合趨勢總結。
                        2. 針對每項重點給予幽默且精闢的短評。
                        3. 給予讀者一條行動建議。
                        請使用繁體中文(台灣)回答。
                        """
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.balloons()
                except Exception as e:
                    st.error(f"AI 分析出錯: {e}")
    else:
        st.info("👋 尚未有數據。請先在左側邊欄設定 API Key 並點擊『執行即時抓取』。")

# --- [今日模式：Google Colab] ---
elif today_mode == "🐍 Google Colab":
    st.title("🐍 Google Colab 雲端開發環境")
    st.write("本單元練習如何將 Streamlit 代碼移植到 Colab 運行。")
    st.link_button("🚀 開啟我的 Google Colab", "https://colab.research.google.com/", use_container_width=True)
