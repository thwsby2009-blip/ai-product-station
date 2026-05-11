import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import requests
from bs4 import BeautifulSoup

# ==========================================
# 0. 全域設定與 Session State 初始化
# ==========================================
st.set_page_config(page_title="AI 課程工作站", page_icon="🤖", layout="wide")

if 'raw_data' not in st.session_state: st.session_state['raw_data'] = []
if 'openrouter_key' not in st.session_state: st.session_state['openrouter_key'] = ""

# ==========================================
# 1. 側邊欄選單
# ==========================================
st.sidebar.title("🎓 課程工作站")
today_mode = st.sidebar.radio(
    "📅 今日課程項目：",
    ["📊 Pandas 數據分析 (115.04.27)", "🤖 AI 數據整合實作 (115.04.20)", "🐍 Google Colab"]
)

st.sidebar.divider()
past_mode = st.sidebar.selectbox(
    "⏪ 往期課程回顧：",
    ["--- 請選擇 ---", "0. 帳號註冊", "1. ChatGPT", "3. Luma AI", "4. 2D 轉 3D", "5. Gemini 3D 公仔"]
)

# ==========================================
# 2. 邏輯判斷 (優先回顧，再判斷今日)
# ==========================================

# --- [回顧模式] ---
if past_mode != "--- 請選擇 ---":
    st.header(f"⏪ 往期回顧：{past_mode}")
    if "0." in past_mode:
        st.link_button("🔑 OpenRouter Key 申請", "https://openrouter.ai/keys")
    elif "4." in past_mode:
        st.link_button("🛠️ Meshy 3D", "https://www.meshy.ai/")
    elif "3." in past_mode:
        st.link_button("🎬 Luma Dream Machine", "https://lumalabs.ai/dream-machine")
    st.info("此區塊為快速連結回顧，如需實作請切換回今日課程。")

# --- [今日模式：4月27日 Pandas 實戰] ---
elif today_mode == "📊 Pandas 數據分析 (115.04.27)":
    st.title("📊 Pandas 數據全流程分析 (P77-P90)")
    
    # 建立範例數據
    data_inc = {"年齡組": ["20-30", "30-40", "40-50"], "月薪": [35000, 52000, 68000], "獎金": [5000, 12000, 20000]}
    data_exp = {"年齡組": ["20-30", "30-40", "40-50"], "生活支出": [20000, 28000, 35000], "娛樂支出": [5000, 8000, 12000]}
    df_inc = pd.DataFrame(data_inc)
    df_exp = pd.DataFrame(data_exp)

    st.subheader("1️⃣ 數據合併與清洗 (Merge)")
    df_final = pd.merge(df_inc, df_exp, on="年齡組")
    df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
    df_final["總支出"] = df_final["生活支出"] + df_final["娛樂支出"]
    df_final["儲蓄"] = df_final["總收入"] - df_final["總支出"]
    st.dataframe(df_final, use_container_width=True)

    st.divider()
    st.subheader("2️⃣ 數據視覺化 (Plotly)")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(df_final, x="年齡組", y="儲蓄", title="各年齡組儲蓄額", color="年齡組"))
    with c2:
        st.plotly_chart(px.pie(df_final, values="總收入", names="年齡組", title="收入佔比分析"))

# --- [今日模式：4月20日 AI 爬蟲整合] ---
elif today_mode == "🤖 AI 數據整合實作 (115.04.20)":
    st.title("🤖 跨模型 AI 數據實作 (爬蟲 + OpenRouter)")
    
    with st.sidebar:
        st.header("🔑 設定區")
        key = st.text_input("OpenRouter Key:", type="password", value=st.session_state['openrouter_key'])
        if key: st.session_state['openrouter_key'] = key
        
        url = st.text_input("爬取網址:", "https://tw.news.yahoo.com/")
        if st.button("🚀 抓取資料"):
            try:
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                titles = [t.get_text().strip() for t in soup.find_all(['h2', 'h3', 'a']) if 15 < len(t.get_text().strip()) < 80]
                st.session_state['raw_data'] = list(dict.fromkeys(titles))[:20] # 取前20筆
                st.success("抓取成功！")
            except Exception as e:
                st.error(f"抓取失敗: {e}")

    st.subheader("🔍 步驟一：選擇分析內容")
    if st.session_state['raw_data']:
        df_sel = pd.DataFrame({"選擇": [False] * len(st.session_state['raw_data']), "內容": st.session_state['raw_data']})
        edited_df = st.data_editor(df_sel, hide_index=True, use_container_width=True)
        selected = edited_df[edited_df["選擇"] == True]["內容"].tolist()

        st.divider()
        st.subheader("🧠 步驟二：AI 多模型分析")
        model = st.selectbox("切換模型:", ["google/gemini-flash-1.5-exp:free", "meta-llama/llama-3.1-8b-instruct:free"])
        
        if st.button("🪄 開始分析", type="primary"):
            if not st.session_state['openrouter_key']:
                st.error("請先輸入 API Key")
            elif not selected:
                st.warning("請勾選資料")
            else:
                try:
                    with st.spinner("AI 運算中..."):
                        prompt = "請幫我總結以下資訊並給出簡短評論：\n" + "\n".join(selected)
                        headers = {"Authorization": f"Bearer {st.session_state['openrouter_key']}"}
                        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
                        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                        st.markdown(r.json()['choices'][0]['message']['content'])
                        st.balloons()
                except Exception as e:
                    st.error(f"AI 回傳錯誤: {e}")
    else:
        st.info("💡 請點擊左側「抓取資料」按鈕。")

# --- [今日模式：Google Colab] ---
elif today_mode == "🐍 Google Colab":
    st.title("🐍 Google Colab 雲端開發")
    st.write("請點擊下方連結開啟雲端筆記本：")
    st.link_button("🚀 開啟 Google Colab", "https://colab.research.google.com/")
