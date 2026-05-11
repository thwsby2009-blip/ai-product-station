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
import matplotlib.font_manager as fm

# ==========================================
# 0. 字型初始化
# ==========================================
def init_cloud_font():
    os.system("fc-cache -fv")
    fm._load_fontmanager(try_read_cache=False)

    target_fonts = [
        'Noto Sans CJK JP',
        'Noto Sans CJK TC',
        'Noto Sans CJK SC',
        'DejaVu Sans'
    ]

    available_fonts = [f.name for f in fm.fontManager.ttflist]

    selected_font = None
    for f in target_fonts:
        if f in available_fonts:
            plt.rcParams['font.sans-serif'] = [f]
            selected_font = f
            break

    plt.rcParams['axes.unicode_minus'] = False
    return selected_font

active_font = init_cloud_font()

# ==========================================
# 1. 基本設定
# ==========================================
st.set_page_config(layout="wide", page_title="AI 產品設計與數據分析工作站")

if 'raw_data' not in st.session_state:
    st.session_state['raw_data'] = []

if 'google_api_key' not in st.session_state:
    st.session_state['google_api_key'] = ""

if 'selected_data' not in st.session_state:
    st.session_state['selected_data'] = []

# ==========================================
# 2. 側邊欄
# ==========================================
st.sidebar.title("🎓 嚴老師教學工作站")

today_mode = st.sidebar.radio(
    "📅 今日課程項目：",
    ["📊 Pandas 數據分析 (P77-P90)", "🤖 AI 數據整合實作 (115.04.20)"]
)

# ==========================================
# 3. Pandas 主課程
# ==========================================
if today_mode == "📊 Pandas 數據分析 (P77-P90)":
    st.title("📊 Pandas 進階數據全流程實作")

    try:
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists("data/practice_income.csv"):
            pd.DataFrame({
                "年齡組": ["20-30", "30-40", "40-50"],
                "月薪": [35000, 52000, 68000],
                "獎金": [5000, 12000, 20000]
            }).to_csv("data/practice_income.csv", index=False, encoding="utf-8-sig")

        if not os.path.exists("data/practice_expense.csv"):
            pd.DataFrame({
                "年齡組": ["20-30", "30-40", "40-50"],
                "食衣住行支出": [15000, 20000, 25000],
                "娛樂教育支出": [5000, 8000, 12000]
            }).to_csv("data/practice_expense.csv", index=False, encoding="utf-8-sig")

        df_inc = pd.read_csv("data/practice_income.csv")
        df_exp = pd.read_csv("data/practice_expense.csv")

    except Exception as e:
        st.error(f"載入失敗: {e}")
        st.stop()

    df_inc_avg = df_inc.groupby("年齡組")[["月薪", "獎金"]].mean().reset_index()
    df_final = pd.merge(df_inc_avg, df_exp, on="年齡組", how="inner")

    df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
    df_final["總支出"] = df_final["食衣住行支出"] + df_final["娛樂教育支出"]
    df_final["儲蓄額"] = df_final["總收入"] - df_final["總支出"]

    st.header("🎛️ 樞紐分析")
    st.dataframe(df_final)

    st.header("📈 Plotly 圖表")
    st.plotly_chart(px.pie(df_final, values='總收入', names='年齡組'))

    st.divider()
    st.header("📦 P82 資料分箱")
    bins = [-float('inf'), 10000, 20000, float('inf')]
    labels = ["🔴 緊繃", "🟡 穩健", "🟢 優渥"]
    df_final["財務狀態"] = pd.cut(df_final["儲蓄額"], bins=bins, labels=labels)
    st.dataframe(df_final[["年齡組", "儲蓄額", "財務狀態"]])

    st.divider()
    st.header("📅 P85 時間序列")

    df_time = pd.DataFrame({
        "日期": ["2024-01-01", "2024-02-14", "2024-03-08"],
        "營業額": [50000, 85000, 62000]
    })

    df_time["日期"] = pd.to_datetime(df_time["日期"])
    st.line_chart(df_time, x="日期", y="營業額")

    st.divider()
    st.header("📊 P87 統計圖")

    np.random.seed(42)
    df_sim = pd.DataFrame({
        "年齡": np.random.randint(22, 60, 100),
        "月薪": np.random.randint(30, 150, 100) * 1000
    })

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df_sim, x="年齡", y="月薪", ax=ax)
    st.pyplot(fig)

    st.divider()
    st.header("📊 P90 儀表板")

    fig_dash = plt.figure(figsize=(10, 5))
    ax1 = fig_dash.add_subplot(121)
    ax2 = fig_dash.add_subplot(122)

    ax1.plot(range(1, 13), np.random.randint(80, 150, 12))
    ax1.set_title("銷售趨勢")

    ax2.pie([35, 25, 20, 20], labels=["A", "B", "C", "D"])
    ax2.set_title("產品占比")

    st.pyplot(fig_dash)

    st.divider()
    st.header("💾 匯出")

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="下載 CSV",
        data=convert_df(df_final),
        file_name="analysis.csv",
        mime="text/csv"
    )

# ==========================================
# 4. AI 整合區
# ==========================================
elif today_mode == "🤖 AI 數據整合實作 (115.04.20)":
    st.title("🤖 Gemini 數據整合")

    with st.sidebar:
        key = st.text_input("Google API Key", type="password", value=st.session_state['google_api_key'])
        if key:
            st.session_state['google_api_key'] = key

        url = st.text_input("網址", "https://tw.news.yahoo.com/")

        if st.button("抓取資料"):
            try:
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                titles = [
                    t.get_text().strip()
                    for t in soup.find_all(['h2', 'h3', 'a'])
                    if 15 < len(t.get_text().strip()) < 80
                ]

                new_titles = list(dict.fromkeys(titles))[:20]
                old_titles = st.session_state.get('raw_data', [])
                st.session_state['raw_data'] = list(dict.fromkeys(old_titles + new_titles))

            except Exception as e:
                st.error(f"抓取失敗: {e}")

    if st.session_state['raw_data']:
        df_sel = pd.DataFrame({
            "勾選": [item in st.session_state['selected_data'] for item in st.session_state['raw_data']],
            "內容": st.session_state['raw_data']
        })

        edited = st.data_editor(df_sel, hide_index=True, use_container_width=True)

        st.session_state['selected_data'] = edited[
            edited["勾選"] == True
        ]["內容"].tolist()

        if st.button("Gemini 分析"):
            try:
                genai.configure(api_key=st.session_state['google_api_key'])
                model = genai.GenerativeModel('gemini-2.0-flash')
                prompt = "請用繁體中文整理並簡短評論：\n" + "\n".join(st.session_state['selected_data'])
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"分析失敗: {e}")
