import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

def init_cloud_font():
    # 1. 嘗試執行 Linux 命令刷新字型快取 (這一步在雲端很有效)
    os.system("fc-cache -fv")
    
    # 2. 強制 Matplotlib 重新掃描系統字型
    fm._load_fontmanager(try_read_cache=False)
    
    # 3. 設定優先順序 (Linux 端的名稱通常包含 'JP' 或 'TC')
    target_fonts = ['Noto Sans CJK JP', 'Noto Sans CJK TC', 'Noto Sans CJK SC']
    
    # 偵測目前系統有的字型
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for f in target_fonts:
        if f in available_fonts:
            plt.rcParams['font.sans-serif'] = [f]
            break
            
    plt.rcParams['axes.unicode_minus'] = False

# 執行初始化
init_cloud_font()
# ==========================================
# 0. 全域設定與 Session State
# ==========================================
st.set_page_config(layout="wide", page_title="AI 產品設計與數據分析工作站")

if 'raw_data' not in st.session_state: st.session_state['raw_data'] = []
if 'google_api_key' not in st.session_state: st.session_state['google_api_key'] = ""

# ==========================================
# 1. 側邊欄導航
# ==========================================
st.sidebar.title("🎓 嚴老師教學工作站")
today_mode = st.sidebar.radio(
    "📅 今日課程項目：",
    ["📊 Pandas 數據分析 (P77-P90)", "🤖 AI 數據整合實作 (115.04.20)", "🐍 Google Colab"]
)

st.sidebar.divider()
past_mode = st.sidebar.selectbox(
    "⏪ 往期課程回顧：",
    ["--- 請選擇 ---", "0. 帳號註冊", "1. ChatGPT", "3. Luma AI", "4. 2D 轉 3D", "5. 植物地圖專案"]
)

# ==========================================
# 2. 核心邏輯判斷
# ==========================================

# --- [今日模式：4月27日 Pandas 深度實作 P77-P90] ---
if today_mode == "📊 Pandas 數據分析 (P77-P90)" and past_mode == "--- 請選擇 ---":
    st.title("📊 Pandas 進階數據全流程實作")

    # ═══ P77: 數據載入 ═══
    try:
        # 自動檢查並建立資料夾與練習檔，確保學生執行不報錯
        if not os.path.exists("data"): os.makedirs("data")
        if not os.path.exists("data/practice_income.csv"):
            pd.DataFrame({"年齡組": ["20-30", "30-40", "40-50"], "月薪": [35000, 52000, 68000], "獎金": [5000, 12000, 20000]}).to_csv("data/practice_income.csv", index=False)
        if not os.path.exists("data/practice_expense.csv"):
            pd.DataFrame({"年齡組": ["20-30", "30-40", "40-50"], "食衣住行支出": [15000, 20000, 25000], "娛樂教育支出": [5000, 8000, 12000]}).to_csv("data/practice_expense.csv", index=False)
        
        df_inc = pd.read_csv("data/practice_income.csv")
        df_exp = pd.read_csv("data/practice_expense.csv")
        st.sidebar.success("✅ 原始資料載入成功")
    except Exception as e:
        st.error(f"❌ 載入失敗: {e}")
        st.stop()

    # ═══ P78-P79: Groupby & Merge ═══
    df_inc_avg = df_inc.groupby("年齡組")[["月薪", "獎金"]].mean().reset_index()
    df_final = pd.merge(df_inc_avg, df_exp, on="年齡組", how="inner")
    df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
    df_final["總支出"] = df_final["食衣住行支出"] + df_final["娛樂教育支出"]
    df_final["儲蓄額"] = df_final["總收入"] - df_final["總支出"]

    # ═══ P80: Pivot Table ═══
    st.header("🎛️ 樞紐分析預覽 (P80)")
    st.dataframe(df_final.pivot_table(index="年齡組", values=["總收入", "總支出", "儲蓄額"]).style.background_gradient(cmap="YlGn"))

    # ═══ P81: 進階視覺化 ═══
    st.divider()
    st.header("📈 進階圖表實作 (P81)")
    tab1, tab2, tab3 = st.tabs(["圓餅圖 (組成)", "散佈圖 (關聯)", "折線圖 (趨勢)"])
    with tab1:
        st.plotly_chart(px.pie(df_final, values='總收入', names='年齡組', hole=0.4), use_container_width=True)
    with tab2:
        st.scatter_chart(data=df_final, x="月薪", y="總支出", color="年齡組")
    with tab3:
        st.line_chart(data=df_final, x="年齡組", y=["月薪", "獎金"])

    # ═══ P82: 資料分箱 ═══
    st.divider()
    st.header("📦 P82: 資料分箱 (pd.cut)")
    bins = [-float('inf'), 10000, 20000, float('inf')]
    labels = ["🔴 消費緊繃", "🟡 財務穩健", "🟢 儲蓄優渥"]
    df_final["財務狀態"] = pd.cut(df_final["儲蓄額"], bins=bins, labels=labels)
    st.dataframe(df_final[["年齡組", "儲蓄額", "財務狀態"]].sort_values("儲蓄額", ascending=False))

    # ═══ P86-P88: Matplotlib & Seaborn ═══
    st.divider()
    st.header("🎨 P86-P88: 專業統計繪圖")
    plt.rcParams["font.family"] = ["Microsoft JhengHei"] # 解決中文亂碼
    fig_mix, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # P86: 帶平均線的長條圖
    cities = ["台北", "新北", "桃園", "台中", "高雄"]
    salaries = [65000, 58000, 52000, 55000, 53000]
    axes[0].bar(cities, salaries, color="#81C784")
    axes[0].axhline(y=np.mean(salaries), color="red", linestyle="--", label="全均線")
    axes[0].set_title("各縣市薪資比較")
    axes[0].legend()

    # P88: Seaborn Boxplot
    try:
        tips = sns.load_dataset("tips")
        sns.boxplot(data=tips, x="day", y="total_bill", ax=axes[1], palette="Set3")
        axes[1].set_title("各星期消費分布 (箱型圖)")
    except:
        axes[1].text(0.5, 0.5, "需聯網載入 tips 資料集")
    
    st.pyplot(fig_mix)

    # ═══ P90: 銷售儀表板 (GridSpec) ═══
    st.divider()
    st.header("📊 P90: 專業銷售儀表板 (GridSpec)")
    fig_dash = plt.figure(figsize=(12, 6))
    grid = gs.GridSpec(1, 2, figure=fig_dash)
    ax_main = fig_dash.add_subplot(grid[0, 0])
    ax_main.plot(range(1, 13), np.random.randint(80, 150, 12), "b-o")
    ax_main.set_title("月度銷售趨勢")
    ax_side = fig_dash.add_subplot(grid[0, 1])
    ax_side.pie([35, 25, 20, 20], labels=["A", "B", "C", "D"], autopct="%1.0f%%")
    ax_side.set_title("產品占比")
    st.pyplot(fig_dash)

# --- [今日模式：4月20日 AI 數據整合 - 鎖定 gemini-2.0-flash] ---
elif today_mode == "🤖 AI 數據整合實作 (115.04.20)":
    st.title("🤖 Gemini 2.0 Flash 數據實作")
    
    with st.sidebar:
        st.header("🔑 API 設定")
        key = st.text_input("Google API Key:", type="password", value=st.session_state['google_api_key'])
        if key: st.session_state['google_api_key'] = key
        
        st.divider()
        url = st.text_input("爬取網址:", "https://tw.news.yahoo.com/")
        if st.button("🚀 執行抓取"):
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            titles = [t.get_text().strip() for t in soup.find_all(['h2', 'h3', 'a']) if 15 < len(t.get_text().strip()) < 80]
            st.session_state['raw_data'] = list(dict.fromkeys(titles))[:20]

    if st.session_state['raw_data']:
        df_sel = pd.DataFrame({"勾選": [False] * len(st.session_state['raw_data']), "內容": st.session_state['raw_data']})
        edited = st.data_editor(df_sel, hide_index=True, use_container_width=True)
        selected = edited[edited["勾選"] == True]["內容"].tolist()

        if st.button("🪄 使用 Gemini 2.0 Flash 分析", type="primary"):
            try:
                genai.configure(api_key=st.session_state['google_api_key'])
                model = genai.GenerativeModel('gemini-2.0-flash')
                prompt = "請用繁體中文(台灣)總結以下資訊並給出幽默評論：\n" + "\n".join(selected)
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.balloons()
            except Exception as e:
                st.error(f"分析失敗: {e}")
    else:
        st.info("請先從左側抓取數據。")

# --- 其他模式 (如 Google Colab, 往期回顧) ---
else:
    st.info("請從左側選單切換至今日課程或回顧單元。")
