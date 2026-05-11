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

# --- 主頁面邏輯判斷 ---

# ==========================================
# ═══ 核心邏輯 A：4月27日 Pandas 課程 ═══
# ==========================================
if today_mode == "📊 Pandas 數據分析 (P77-P90)" and past_mode == "--- 請選擇 ---":
    st.header("🎓 Pandas 全流程實作 (P77-P90)")

    # 🛠️ 數據自動補全邏輯 (防止 GitHub 讀檔報錯)
    if not os.path.exists("data"): os.makedirs("data")
    path_inc, path_exp = "data/practice_income.csv", "data/practice_expense.csv"
    
    if not os.path.exists(path_inc) or not os.path.exists(path_exp):
        st.warning("⚠️ 檢測到缺少練習檔，正在為您生成模擬數據...")
        pd.DataFrame({
            "姓名": ["張三", "李四", "王五", "趙六", "孫七"],
            "年齡組": ["20-30", "30-40", "20-30", "40-50", "30-40"],
            "月薪": [35000, 48000, 38000, 55000, 42000],
            "獎金": [5000, 8000, 4000, 12000, 7000]
        }).to_csv(path_inc, index=False, encoding="utf-8-sig")
        pd.DataFrame({
            "年齡組": ["20-30", "30-40", "40-50"],
            "食衣住行支出": [15000, 20000, 25000],
            "娛樂教育支出": [5000, 8000, 10000]
        }).to_csv(path_exp, index=False, encoding="utf-8-sig")

    # --- 開始原本的分析程式內容 ---
    try:
        df_inc = pd.read_csv(path_inc)
        df_exp = pd.read_csv(path_exp)
        
        # P78-P79: 計算
        df_inc_avg = df_inc.groupby("年齡組")[["月薪", "獎金"]].mean().reset_index()
        df_final = pd.merge(df_inc_avg, df_exp, on="年齡組", how="inner")
        df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
        df_final["總支出"] = df_final["食衣住行支出"] + df_final["娛樂教育支出"]
        df_final["儲蓄額"] = df_final["總收入"] - df_final["總支出"]

        # P80: 樞紐分析
        st.header("🎛️ 樞紐分析預覽 (P80)")
        df_pivot = df_final.pivot_table(index="年齡組", values=["總收入", "總支出", "儲蓄額"])
        st.dataframe(df_pivot.style.background_gradient(cmap="YlGn"))

        # P81: 視覺化 Tabs
        st.divider()
        st.header("📈 進階圖表實作 (P81)")
        t1, t2, t3 = st.tabs(["圓餅圖", "散佈圖", "折線圖"])
        with t1: st.plotly_chart(px.pie(df_final, values='總收入', names='年齡組', hole=0.4))
        with t2: st.scatter_chart(data=df_final, x="月薪", y="總支出", color="年齡組")
        with t3: st.line_chart(data=df_final, x="年齡組", y=["月薪", "獎金"])

        # P82: 分箱
        st.divider()
        st.header("📦 P82: 資料分箱 (pd.cut)")
        df_final["財務狀態"] = pd.cut(df_final["儲蓄額"], bins=[-float('inf'), 10000, 20000, float('inf')], labels=["🔴 緊繃", "🟡 穩健", "🟢 優渥"])
        st.dataframe(df_final[["年齡組", "儲蓄額", "財務狀態"]])

        # P86: Matplotlib 專業圖表
        st.divider()
        st.header("📊 P86: 進階長條圖 (Matplotlib)")
        plt.rcParams["font.family"] = ["Microsoft JhengHei"]
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].bar(["台北", "新北", "桃園", "台中", "高雄"], [65, 58, 52, 55, 53], color="green")
        axes[0].set_title("各地區薪資")
        axes[1].barh(["台北", "新北", "桃園", "台中", "高雄"], [65, 58, 52, 55, 53], color="darkgreen")
        st.pyplot(fig)

        # P90: 綜合銷售儀表板 (簡化核心邏輯)
        st.divider()
        st.header("📊 P90: 專業銷售儀表板")
        fig_dash = plt.figure(figsize=(16, 8))
        grid = gs.GridSpec(2, 2, figure=fig_dash)
        ax1 = fig_dash.add_subplot(grid[0, :])
        ax1.plot(range(1, 13), np.random.randint(80, 150, 12), "b-o")
        ax1.set_title("月度銷售趨勢")
        st.pyplot(fig_dash)

        # P92: 導出
        st.divider()
        st.header("💾 數據導出")
        st.download_button("📥 下載分析結果", df_final.to_csv(index=False).encode('utf-8-sig'), "report.csv", "text/csv")

    except Exception as e:
        st.error(f"分析失敗: {e}")

# ==========================================
# ═══ 核心邏輯 B：Google Colab 雲端開發 ═══
# ==========================================
elif today_mode == "🐍 Google Colab 雲端開發實作" and past_mode == "--- 請選擇 ---":
    st.header("🐍 今日重點：Google Colab 雲端程式開發")
    st.markdown("### 🚀 歡迎來到今日實作單元！\n此處為 Colab 指引區...")
    st.link_button("🔥 立即開啟 Google Colab 工作站", "https://colab.research.google.com/", use_container_width=True)

# ==========================================
# ═══ 核心邏輯 C：舊有課程回顧 ═══
# ==========================================
elif past_mode != "--- 請選擇 ---":
    # 這裡保留你原本 0. 到 5. 的 elif 邏輯
    if past_mode == "0. 帳號註冊與環境檢查 (必做)":
        st.header("🔑 實作前置準備")
        st.link_button("ChatGPT 登入", "https://chat.openai.com/")
        st.link_button("Microsoft Designer", "https://designer.microsoft.com/")
    # ... 其餘 1~5 內容同你原本的代碼 ...
