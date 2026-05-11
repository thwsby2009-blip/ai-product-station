import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 0. 全域設定與 Session State
# ==========================================
st.set_page_config(page_title="AI 產品設計工作站", layout="wide")

if 'raw_data' not in st.session_state: st.session_state['raw_data'] = []
if 'google_api_key' not in st.session_state: st.session_state['google_api_key'] = ""

# ==========================================
# 1. 側邊欄與導航
# ==========================================
st.sidebar.title("🎓 嚴老師教學工作站")
today_mode = st.sidebar.radio(
    "📅 今日課程：",
    ["📊 Pandas 數據分析 (115.04.27)", "🤖 AI 數據整合實作 (115.04.20)", "🐍 Google Colab"]
)

st.sidebar.divider()
past_mode = st.sidebar.selectbox(
    "⏪ 往期回顧：",
    ["--- 請選擇 ---", "0. 帳號註冊", "3. Luma AI", "4. 2D 轉 3D", "5. 植物地圖專案"]
)

# ==========================================
# 2. 核心邏輯判斷
# ==========================================

# --- [4月27日：Pandas 深度實作 P77-P90] ---
if today_mode == "📊 Pandas 數據分析 (115.04.27)" and past_mode == "--- 請選擇 ---":
    st.title("📊 Pandas 進階數據全流程 (P77-P90)")
    
    # --- 擴展數據集 ---
    st.subheader("1️⃣ 多來源數據整合 (Merge)")
    col_a, col_b = st.columns(2)
    
    # 模擬植物調查數據 (對標植物地圖概念)
    df_plants = pd.DataFrame({
        "區域名稱": ["泰山區", "泰山區", "淡水區", "淡水區", "林口區", "林口區"],
        "植物種類": ["櫻花", "多肉-乙女心", "天元宮櫻花", "黃金葛", "杜鵑", "松柏"],
        "觀測數量": [120, 45, 300, 80, 150, 60]
    })
    
    df_climate = pd.DataFrame({
        "區域名稱": ["泰山區", "淡水區", "林口區"],
        "平均氣溫": [24.5, 22.8, 21.5],
        "降雨等級": ["中", "高", "中"]
    })
    
    with col_a:
        st.write("原始觀測表 (Table A)")
        st.dataframe(df_plants)
    with col_b:
        st.write("區域氣候表 (Table B)")
        st.dataframe(df_climate)
        
    # Merge 實作
    df_merged = pd.merge(df_plants, df_climate, on="區域名稱", how="left")
    st.write("✅ 合併後的寬表 (Merged Dataframe)")
    st.dataframe(df_merged, use_container_width=True)

    st.divider()
    
    # --- 數據透視 P80 ---
    st.subheader("2️⃣ 樞紐分析與統計 (Pivot & Groupby)")
    pivot_res = df_merged.pivot_table(
        index="區域名稱", 
        values="觀測數量", 
        aggfunc=["sum", "mean", "count"]
    )
    st.write("各區域植物分佈統計摘要：")
    st.dataframe(pivot_res, use_container_width=True)

    st.divider()
    
    # --- 進階視覺化 P81-P90 ---
    st.subheader("3️⃣ 進階圖表展示 (Plotly Express)")
    tab1, tab2, tab3 = st.tabs(["分佈長條圖", "區域佔比圓餅圖", "氣溫與數量散佈圖"])
    
    with tab1:
        st.plotly_chart(px.bar(df_merged, x="植物種類", y="觀測數量", color="區域名稱", barmode="group", text_auto=True))
    with tab2:
        st.plotly_chart(px.pie(df_merged, values="觀測數量", names="區域名稱", hole=0.4, title="全區植物數量佔比"))
    with tab3:
        # 散佈圖練習
        st.plotly_chart(px.scatter(df_merged, x="平均氣溫", y="觀測數量", size="觀測數量", color="植物種類", hover_name="區域名稱"))

# --- [4月20日：AI 整合 - 預設使用 gemini-2.5-flash] ---
elif today_mode == "🤖 AI 數據整合實作 (115.04.20)" and past_mode == "--- 請選擇 ---":
    st.title("🤖 Gemini 數據自動化 (2.5 Flash)")
    
    with st.sidebar:
        st.header("🔑 API 設定")
        # 預留你的 Key
        key = st.text_input("Google API Key:", type="password", value=st.session_state['google_api_key'])
        if key: st.session_state['google_api_key'] = key
        
        st.divider()
        st.header("🔍 模型指定")
        # 直接鎖定你目前的開發版本
        target_model = st.text_input("模型 ID:", value="gemini-2.5-flash")
        
        url = st.text_input("爬取網址:", "https://tw.news.yahoo.com/")
        if st.button("🚀 執行即時抓取"):
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            titles = [t.get_text().strip() for t in soup.find_all(['h2', 'h3', 'a']) if 15 < len(t.get_text().strip()) < 80]
            st.session_state['raw_data'] = list(dict.fromkeys(titles))[:20]
            st.success("抓取完成")

    if st.session_state['raw_data']:
        df_sel = pd.DataFrame({"選擇": [False] * len(st.session_state['raw_data']), "內容": st.session_state['raw_data']})
        edited = st.data_editor(df_sel, hide_index=True, use_container_width=True)
        selected = edited[edited["選擇"] == True]["內容"].tolist()

        if st.button("🪄 使用 2.5 Flash 分析", type="primary"):
            try:
                genai.configure(api_key=st.session_state['google_api_key'])
                model = genai.GenerativeModel(target_model)
                prompt = "請用繁體中文總結以下趨勢，並給出專業建議：\n" + "\n".join(selected)
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.balloons()
            except Exception as e:
                st.error(f"分析失敗: {e}")
    else:
        st.info("請先執行左側抓取。")

# --- 其他模式 (略) ---
else:
    st.write("請選擇課程單元或回顧項目。")
