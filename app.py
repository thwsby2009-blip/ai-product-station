import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gs
import os
import requests
from bs4 import BeautifulSoup

# ==========================================
# 0. 全域設定與 Session State 初始化
# ==========================================
st.set_page_config(
    page_title="AI 產品設計全流程工作站",
    page_icon="🤖",
    layout="wide"
)

# 必須放在所有邏輯之前，確保任何時候讀取都不會 KeyError
if 'raw_data' not in st.session_state:
    st.session_state['raw_data'] = []
if 'openrouter_key' not in st.session_state:
    st.session_state['openrouter_key'] = ""

# ==========================================
# 1. 側邊欄選單設計
# ==========================================
st.sidebar.title("🎓 課程工作站")
st.sidebar.info("講師：嚴 稑 臻 | 助手：Gemini")

st.sidebar.subheader("📅 今日課程專區")
today_mode = st.sidebar.radio(
    "請選擇實作單元：",
    [
        "📊 Pandas 數據分析 (115.04.27)", 
        "🤖 AI 數據整合實作 (115.04.20)", 
        "🐍 Google Colab 雲端開發"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("⏪ 往期課程回顧")
past_mode = st.sidebar.selectbox(
    "回顧單元：",
    [
        "--- 請選擇 ---",
        "0. 帳號註冊與環境檢查",
        "1. ChatGPT 文字構思",
        "2. DALL-E 圖像生成",
        "3. Luma AI 影片生成",
        "4. 2D 轉 3D 實作",
        "5. 專屬作業：Gemini 3D 公仔"
    ]
)

# ==========================================
# 2. 主頁面邏輯判斷
# ==========================================

# --- 2A. 4月27日：Pandas 數據分析 ---
if today_mode == "📊 Pandas 數據分析 (115.04.27)" and past_mode == "--- 請選擇 ---":
    st.title("🎓 Pandas 全流程實作 (P77-P90)")
    
    # 數據補全邏輯
    if not os.path.exists("data"): os.makedirs("data")
    path_inc, path_exp = "data/practice_income.csv", "data/practice_expense.csv"
    if not os.path.exists(path_inc):
        pd.DataFrame({"年齡組": ["20-30", "30-40"], "月薪": [35000, 48000], "獎金": [5000, 8000]}).to_csv(path_inc, index=False)
    if not os.path.exists(path_exp):
        pd.DataFrame({"年齡組": ["20-30", "30-40"], "食衣住行支出": [15000, 20000], "娛樂教育支出": [5000, 8000]}).to_csv(path_exp, index=False)

    try:
        df_inc = pd.read_csv(path_inc)
        df_exp = pd.read_csv(path_exp)
        df_inc_avg = df_inc.groupby("年齡組")[["月薪", "獎金"]].mean().reset_index()
        df_final = pd.merge(df_inc_avg, df_exp, on="年齡組", how="inner")
        df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
        df_final["總支出"] = df_final["食衣住行支出"] + df_final["娛樂教育支出"]
        df_final["儲蓄額"] = df_final["總收入"] - df_final["總支出"]

        st.header("🎛️ 樞紐分析預覽 (P80)")
        st.dataframe(df_final.pivot_table(index="年齡組", values=["總收入", "總支出", "儲蓄額"]))

        st.divider()
        st.header("📈 進階圖表實作 (P81)")
        t1, t2 = st.tabs(["收入佔比", "薪資趨勢"])
        with t1: st.plotly_chart(px.pie(df_final, values='總收入', names='年齡組'))
        with t2: st.line_chart(data=df_final, x="年齡組", y=["月薪", "獎金"])
    except Exception as e:
        st.error(f"數據加載錯誤: {e}")

# --- 2B. 4月20日：AI 數據整合 (OpenRouter) ---
elif today_mode == "🤖 AI 數據整合實作 (115.04.20)" and past_mode == "--- 請選擇 ---":
    st.title("🤖 跨模型 AI 數據實作 (OpenRouter)")
    st.info("流程：左側輸入 Key -> 抓取資料 -> 勾選 -> AI 分析")

    with st.sidebar:
        st.header("🔑 AI 設定")
        st.markdown("[👉 申請 OpenRouter Key](https://openrouter.ai/keys)")
        or_key = st.text_input("OpenRouter Key：", type="password", value=st.session_state['openrouter_key'])
        if or_key: st.session_state['openrouter_key'] = or_key

        st.markdown("---")
        st.header("📡 數據來源")
        url = st.text_input("抓取網址：", "https://tw.yahoo.com/")
        if st.button("🛰️ 執行即時抓取"):
            try:
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                titles = [t.get_text().strip() for t in soup.find_all(['h2', 'h3', 'a']) if 15 < len(t.get_text().strip()) < 100]
                st.session_state['raw_data'] = list(dict.fromkeys(titles))
                st.success(f"✅ 獲取 {len(st.session_state['raw_data'])} 筆！")
            except Exception as e:
                st.error(f"抓取失敗: {e}")

    st.header("🔍 資訊過濾與精選")
    if st.session_state['raw_data']:
        search = st.text_input("🎯 關鍵字過濾：")
        filtered = [t for t in st.session_state['raw_data'] if search.lower() in t.lower()]
        
        df_sel = pd.DataFrame({"選擇": [False] * len(filtered), "新聞標題內容": filtered})
        edited_df = st.data_editor(df_sel, hide_index=True, use_container_width=True, key="editor_420")
        selected = edited_df[edited_df["選擇"] == True]["新聞標題內容"].tolist()

        st.divider()
        st.header("🤖 AI 多模型分析")
        model = st.selectbox("選擇模型：", ["google/gemini-flash-1.5-exp:free", "meta-llama/llama-3.1-8b-instruct:free"])
        
        if st.button("🚀 啟動 AI 分析", type="primary"):
            if not st.session_state['openrouter_key']:
                st.error("❌ 請填寫 API Key")
            elif not selected:
                st.warning("⚠️ 請勾選內容")
            else:
                try:
                    with st.spinner("AI 分析中..."):
                        prompt = f"請總結以下趨勢並給予幽默短評：\n\n" + "\n".join(selected)
                        resp = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {st.session_state['openrouter_key']}"},
                            json={"model": model, "messages": [{"role": "user", "content": prompt}]}
                        )
                        st.markdown(resp.json()['choices'][0]['message']['content'])
                        st.balloons()
                except Exception as e:
                    st.error(f"分析失敗: {e}")
    else:
        st.info("👋 請先在左側邊欄執行抓取數據。")

# --- 2C. 雲端開發 ---
elif today_mode == "🐍 Google Colab 雲端開發" and past_mode == "--- 請選擇 ---":
    st.header("🐍 Google Colab 實作指引")
    st.link_button("🔥 開啟 Colab 工作站", "https://colab.research.google.com/")

# --- 2D. 往期回顧 ---
elif past_mode != "--- 請選擇 ---":
    st.header(f"⏪ 回顧單元：{past_mode}")
    st.write("此部分可根據需求放入舊有的教學投影片連結或重點。")
