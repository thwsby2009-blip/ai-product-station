import streamlit as st
import numpy as np
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
# 0. 基礎設定
# ==========================================
st.set_page_config(
    page_title="AI 產品設計全流程工作站",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.title("🎓 課程工作站")
st.sidebar.info("講師：嚴 稑 臻 | AI 教學系統")

# ==========================================
# 側邊欄
# ==========================================
st.sidebar.subheader("📅 今日課程 (4/20)")

today_mode = st.sidebar.radio(
    "今日課程：",
    ["📊 Pandas + AI 數據分析", "🐍 Google Colab"]
)

st.sidebar.divider()

st.sidebar.subheader("⏪ 往期課程回顧")

past_mode = st.sidebar.selectbox(
    "選擇課程：",
    [
        "--- 請選擇 ---",
        "0. 帳號註冊",
        "1. ChatGPT",
        "2. DALL-E",
        "3. Luma AI",
        "4. 2D 轉 3D",
        "5. Gemini 3D 公仔",
        "6. AI 數據整合實作 (4/27)"
    ]
)

# ==========================================
# 4/20：Pandas + AI
# ==========================================
if today_mode == "📊 Pandas + AI 數據分析" and past_mode == "--- 請選擇 ---":

    st.title("📊 Pandas + AI 數據分析課程")

    # 建立資料
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

    df_inc_avg = df_inc.groupby("年齡組")[["月薪", "獎金"]].mean().reset_index()
    df_final = pd.merge(df_inc_avg, df_exp, on="年齡組", how="inner")

    df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
    df_final["總支出"] = df_final["食衣住行支出"] + df_final["娛樂教育支出"]
    df_final["儲蓄額"] = df_final["總收入"] - df_final["總支出"]

    st.subheader("📊 數據結果")
    st.dataframe(df_final)

    st.plotly_chart(
        px.pie(df_final, values="總收入", names="年齡組"),
        use_container_width=True
    )

# ==========================================
# 4/27：Google Gemini AI 數據整合
# ==========================================
elif past_mode == "6. AI 數據整合實作 (4/27)":

    st.title("🤖 4/27 AI 數據整合（Google Gemini）")

    if "raw_data" not in st.session_state:
        st.session_state["raw_data"] = []
    if "google_api_key" not in st.session_state:
        st.session_state["google_api_key"] = ""

    with st.sidebar:
        st.subheader("🔑 Google API Key")
        key = st.text_input(
            "輸入 Gemini API Key",
            type="password",
            value=st.session_state["google_api_key"]
        )
        if key:
            st.session_state["google_api_key"] = key

        st.subheader("📡 網頁抓取")
        url = st.text_input("網址", "https://tw.yahoo.com/")

        if st.button("抓取資料"):
            try:
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(res.text, "html.parser")

                data = []
                for t in soup.find_all(["h1", "h2", "h3", "a", "p"]):
                    text = t.get_text().strip()
                    if 15 < len(text) < 200:
                        data.append(text)

                st.session_state["raw_data"] = list(dict.fromkeys(data))
                st.success(f"抓取完成：{len(data)} 筆")

            except Exception as e:
                st.error(e)

    st.subheader("📊 選擇資料")

    if st.session_state["raw_data"]:

        df = pd.DataFrame({
            "選擇": [False] * len(st.session_state["raw_data"]),
            "內容": st.session_state["raw_data"]
        })

        edited = st.data_editor(df)
        selected = edited[edited["選擇"] == True]["內容"].tolist()

        if st.button("開始 AI 分析"):

            if not st.session_state["google_api_key"]:
                st.error("請輸入 API Key")

            elif not selected:
                st.warning("請先選資料")

            else:
                try:
                    genai.configure(api_key=st.session_state["google_api_key"])
                    model = genai.GenerativeModel("gemini-1.5-flash")

                    prompt = "請用繁體中文整理並評論：\n" + "\n".join(selected)

                    res = model.generate_content(prompt)

                    st.markdown("### AI 分析結果")
                    st.markdown(res.text)
                    st.balloons()

                except Exception as e:
                    st.error(e)

    else:
        st.info("請先抓取資料")

# ==========================================
# Colab
elif today_mode == "🐍 Google Colab":

    st.title("🐍 Google Colab 雲端開發工作站")

    st.markdown("""
    ## 🚀 今日實作目標
    進入 Google Colab 進行 AI / Python 雲端開發
    """)

    # ======================
    # 功能說明區（補回來的核心）
    # ======================
    st.subheader("📌 Colab 功能說明")

    st.info("""
    ✔ 無需安裝 Python  
    ✔ 支援 GPU / TPU  
    ✔ 可直接跑 AI 模型  
    ✔ 自動存到 Google Drive  
    """)

    # ======================
    # 快速入口
    # ======================
    st.subheader("🔗 快速進入")

    st.link_button(
        "🔥 開啟 Google Colab",
        "https://colab.research.google.com/",
        use_container_width=True
    )

    st.link_button(
        "📘 官方 Python 教學 Notebook",
        "https://colab.research.google.com/notebooks/intro.ipynb",
        use_container_width=True
    )

    # ======================
    # 教學流程（你原本缺掉的核心）
    # ======================
    st.subheader("🧭 建議學習流程")

    st.markdown("""
    1. 開啟 Colab  
    2. 登入 Google 帳號  
    3. 新增 Notebook  
    4. 測試 Python 基本語法  
    5. 嘗試 import numpy / pandas  
    """)

    # ======================
    # 範例 code（這是最重要補回）
    # ======================
    st.subheader("💡 第一個測試程式")

    st.code("""
import numpy as np
import pandas as pd

print("Hello Colab!")

data = np.random.randint(1, 100, 10)
print(data)
""", language="python")

    # ======================
    # 提醒
    # ======================
    st.warning("💡 提醒：請確認右上角已登入 Google 帳號")
# ==========================================
# fallback
# ==========================================
else:
    st.info("請選擇課程")
