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
        "2. DALL-E 圖像生成",
        "3. Luma AI 影片生成",
        "4. 2D 轉 3D 終極實作",
        "5. 專屬作業：Gemini 3D 公仔生成"
    ]
)

# --- 主頁面邏輯判斷 ---

# 優先處理：4/27 Pandas 數據分析
if today_mode == "📊 Pandas 數據分析 (P77-P90)" and past_mode == "--- 請選擇 ---":
    st.header("📊 P77-P90：Pandas 數據分析全流程")
    
    # 檢查資料夾是否存在
    if not os.path.exists("data"):
        st.warning("⚠️ 找不到 data 資料夾，正在建立範例數據...")
        os.makedirs("data", exist_ok=True)
        # 這裡可以寫入一段 code 產生練習用的 CSV，防止 GitHub 上沒抓到檔案時噴錯

    try:
        # --- 以下放入你之前寫的 P77-P90 核心邏輯 ---
        # 範例：數據讀取與計算
        df_inc = pd.read_csv("data/practice_income.csv")
        df_exp = pd.read_csv("data/practice_expense.csv")
        
        # (中間計算過程略過，請貼入你之前的 df_final 計算邏輯)
        
        # 展示成果：P80 樞紐分析
        st.subheader("🎛️ 樞紐分析 (P80)")
        # 注意：這裡就是會用到 matplotlib 的地方
        # st.dataframe(df_final.style.background_gradient(cmap="YlGn"))
        
        # 展示成果：P90 儀表板
        st.subheader("📈 綜合銷售儀表板 (P90)")
        # [貼入你的 plt.figure 與 st.pyplot 代碼]
        
    except Exception as e:
        st.error(f"分析模組載入錯誤: {e}")
        st.info("請確認 GitHub 倉庫中包含 data/practice_income.csv 等檔案。")

# 處理：Google Colab
elif today_mode == "🐍 Google Colab 雲端開發實作" and past_mode == "--- 請選擇 ---":
    st.header("🐍 今日重點：Google Colab 雲端程式開發")
    st.link_button("🔥 立即開啟 Google Colab 工作站", "https://colab.research.google.com/")

# 處理：舊有課程
elif past_mode != "--- 請選擇 ---":
    st.header(f"⏪ 課程回顧：{past_mode}")
    # 根據選單顯示對應按鈕...
