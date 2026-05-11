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

# ==========================================
# ═══ 核心邏輯 A：4月27日 Pandas 課程 ═══
# ==========================================
if today_mode == "📊 Pandas 數據分析 (P77-P90)" and past_mode == "--- 請選擇 ---":
    st.title("🎓 Pandas 全流程實作 (P77-P90)")

    # --- 自動檢查並生成數據檔案 (防止 Errno 2) ---
    if not os.path.exists("data"):
        os.makedirs("data")
    
    file_inc = "data/practice_income.csv"
    file_exp = "data/practice_expense.csv"

    if not os.path.exists(file_inc) or not os.path.exists(file_exp):
        st.warning("⚠️ 找不到練習檔案，系統正在自動生成範例數據...")
        
        # 生成收入範例檔
        df_inc_sample = pd.DataFrame({
            "姓名": ["張三", "李四", "王五", "趙六", "孫七"],
            "年齡組": ["20-30", "30-40", "20-30", "40-50", "30-40"],
            "月薪": [35000, 48000, 38000, 55000, 42000],
            "獎金": [5000, 8000, 4000, 12000, 7000]
        })
        # 生成支出範例檔
        df_exp_sample = pd.DataFrame({
            "年齡組": ["20-30", "30-40", "40-50"],
            "食衣住行支出": [15000, 20000, 25000],
            "娛樂教育支出": [5000, 8000, 10000]
        })
        df_inc_sample.to_csv(file_inc, index=False, encoding="utf-8-sig")
        df_exp_sample.to_csv(file_exp, index=False, encoding="utf-8-sig")
        st.success("✅ 範例數據已補齊！")

    # --- 進入正式分析邏輯 ---
    try:
        df_inc = pd.read_csv(file_inc)
        df_exp = pd.read_csv(file_exp)
        
        # P78-P79：計算過程
        df_inc_avg = df_inc.groupby("年齡組")[["月薪", "獎金"]].mean().reset_index()
        df_final = pd.merge(df_inc_avg, df_exp, on="年齡組", how="inner")
        df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
        df_final["總支出"] = df_final["食衣住行支出"] + df_final["娛樂教育支出"]
        df_final["儲蓄額"] = df_final["總收入"] - df_final["總支出"]

        # 展示：P80 樞紐分析
        st.header("🎛️ 樞紐分析預覽 (P80)")
        st.dataframe(df_final.style.background_gradient(cmap="YlGn"))
        
        # ... 後續繪圖代碼 (P81-P90) ...
        
    except Exception as e:
        st.error(f"❌ 讀取資料失敗：{e}")
