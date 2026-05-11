import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gs
import os

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
st.sidebar.subheader("📅 今日課程專區 (115.04.27)")
today_mode = st.sidebar.radio(
    "今日實作項目：",
    ["📊 Pandas 數據分析 (P77-P90)", "🐍 Google Colab 雲端開發實作"]
)

st.sidebar.divider() 

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
    # --- 主畫面：數據處理區 ---
st.header("🔍 模組二：資訊過濾與精選")
if st.session_state['raw_data']:
        search_query = st.text_input("🎯 關鍵字快速過濾：", placeholder="例如：股市、AI...")
        filtered_list = [t for t in st.session_state['raw_data'] if search_query.lower() in t.lower()]
        
        # 建立勾選表格
        df_to_select = pd.DataFrame({"選擇": [False] * len(filtered_list), "新聞標題內容": filtered_list})
        edited_df = st.data_editor(
            df_to_select,
            hide_index=True,
            column_config={
                "選擇": st.column_config.CheckboxColumn(required=False),
                "新聞標題內容": st.column_config.TextColumn(width="large")
            },
            use_container_width=True,
            key="news_editor"
        )
        selected_titles = edited_df[edited_df["選擇"] == True]["新聞標題內容"].tolist()
        
        if selected_titles:
            st.success(f"已選取 {len(selected_titles)} 條新聞")

        # --- 模組三：AI 分析 ---
        st.divider()
        st.header("🤖 模組三：多模型調度分析")
        
        target_model = st.selectbox(
            "選擇 AI 模型 (免費模型推薦)：",
            [
                "google/gemini-flash-1.5-exp:free",
                "meta-llama/llama-3.1-8b-instruct:free",
                "mistralai/mistral-7b-instruct:free",
                "qwen/qwen-2-7b-instruct:free"
            ]
        )

        if st.button("🚀 啟動 AI 進行深度分析", type="primary"):
            if not st.session_state['openrouter_key']:
                st.error("❌ 請先在左側輸入 OpenRouter API Key！")
            elif not selected_titles:
                st.warning("⚠️ 請勾選新聞。")
            else:
                try:
                    with st.spinner(f"🧠 {target_model} 分析中..."):
                        context = "\n".join(selected_titles)
                        prompt = f"請擔任專業評論員，針對以下新聞內容進行繁體中文的趨勢總結與幽默短評，最後給讀者一個建議：\n\n{context}"
                        
                        response = requests.post(
                            url="https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {st.session_state['openrouter_key']}",
                                "HTTP-Referer": "http://localhost:8501",
                                "X-Title": "Student Demo",
                            },
                            json={
                                "model": target_model,
                                "messages": [{"role": "user", "content": prompt}]
                            },
                            timeout=60
                        )
                        result = response.json()
                        st.markdown(result['choices'][0]['message']['content'])
                        st.balloons()
                except Exception as e:
                    st.error(f"分析失敗：{e}")
        else:
                    st.info("👋 請先在左側邊欄點擊「執行即時抓取」來獲取數據來源。")
# ==========================================
# ═══ 核心邏輯：4月27日 Pandas 數據分析 ═══
# ==========================================
if today_mode == "📊 Pandas 數據分析 (115.04.27)" and past_mode == "--- 請選擇 ---":
    # (此處放你原本 P77-P90 的程式碼，記得維持 4 格縮排)
    st.header("🎓 Pandas 全流程實作 (P77-P90)")
    # ... (省略) ...

# ==========================================
# ═══ 核心邏輯：4月20日 跨模型 AI 數據整合 ═══
# ==========================================
elif today_mode == "🎨 AI 指令與圖像核心 (115.04.20)" and past_mode == "--- 請選擇 ---":
    import requests
    from bs4 import BeautifulSoup

    st.title("🤖 跨模型 AI 數據實作 (去 Google 化版本)")
    
    # 初始化 session_state
    if 'raw_data' not in st.session_state: st.session_state['raw_data'] = []
    if 'openrouter_key' not in st.session_state: st.session_state['openrouter_key'] = ""

    # --- 側邊欄設定 ---
    with st.sidebar:
        st.header("🔑 第一步：AI 設定")
        st.markdown("[👉 點此申請 OpenRouter Key](https://openrouter.ai/keys)")
        or_key_input = st.text_input("API Key：", type="password", value=st.session_state['openrouter_key'])
        if or_key_input: st.session_state['openrouter_key'] = or_key_input

        st.markdown("---")
        st.header("📡 第二步：數據來源")
        source_url = st.text_input("網址：", "https://tw.yahoo.com/")
        if st.button("🛰️ 執行即時抓取"):
            with st.spinner("抓取中..."):
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    res = requests.get(source_url, headers=headers, timeout=10)
                    res.encoding = 'utf-8'
                    soup = BeautifulSoup(res.text, 'html.parser')
                    titles = [t.get_text().strip() for t in soup.find_all(['h1', 'h2', 'h3', 'a']) if 15 < len(t.get_text().strip()) < 100]
                    st.session_state['raw_data'] = list(dict.fromkeys(titles))
                    st.success(f"✅ 成功獲取 {len(st.session_state['raw_data'])} 筆！")
                except Exception as e:
                    st.error(f"抓取失敗：{e}")

    # --- 主畫面：數據處理區 ---
    st.header("🔍 模組二：資訊過濾與精選")

    # 關鍵判斷：是否有抓到資料
    if st.session_state['raw_data']:
        search_query = st.text_input("🎯 關鍵字過濾：")
        filtered_list = [t for t in st.session_state['raw_data'] if search_query.lower() in t.lower()]
        
        df_to_select = pd.DataFrame({"選擇": [False] * len(filtered_list), "新聞標題內容": filtered_list})
        edited_df = st.data_editor(df_to_select, hide_index=True, use_container_width=True)
        selected_titles = edited_df[edited_df["選擇"] == True]["新聞標題內容"].tolist()

        # --- 模組三：AI 分析 ---
        st.divider()
        st.header("🤖 模組三：AI 分析報告")
        target_model = st.selectbox("選擇模型：", ["google/gemini-flash-1.5-exp:free", "meta-llama/llama-3.1-8b-instruct:free"])

        if st.button("🚀 啟動 AI 分析", type="primary"):
            if not st.session_state['openrouter_key']:
                st.error("❌ 沒 Key 啊！請在左側輸入。")
            elif not selected_titles:
                st.warning("⚠️ 請勾選要分析的內容。")
            else:
                try:
                    with st.spinner("AI 思考中..."):
                        prompt = f"請總結以下新聞趨勢並給予幽默短評：\n\n" + "\n".join(selected_titles)
                        response = requests.post(
                            url="https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {st.session_state['openrouter_key']}"},
                            json={"model": target_model, "messages": [{"role": "user", "content": prompt}]}
                        )
                        st.markdown(response.json()['choices'][0]['message']['content'])
                        st.balloons()
                except Exception as e:
                    st.error(f"分析失敗：{e}")
    
    # 這是原本卡住你的 else：它跟「if st.session_state['raw_data']:」垂直對齊
    else:
        st.info("👋 請先在左側邊欄點擊「執行即時抓取」來獲取數據來源。")

# ==========================================
# ═══ 核心邏輯：Google Colab 課程 ═══
# ==========================================
elif today_mode == "🐍 Google Colab 雲端開發實作" and past_mode == "--- 請選擇 ---":
    st.header("🐍 Google Colab 實作指引")
    st.link_button("🔥 開啟 Colab", "https://colab.research.google.com/")
