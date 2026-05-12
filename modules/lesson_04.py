import streamlit as st
import os
import pandas as pd
import re
import requests
import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai
import platform

def run():
    # ═══ 1. API Key 與環境設定 ═══
    # 建立一個與 Lesson 03 同名的 Session State 鍵值，達到 Key 共用效果
    if "google_api_key" not in st.session_state:
        st.session_state["google_api_key"] = ""

    st.sidebar.header("🔑 AI 設定中心")
    st.session_state["google_api_key"] = st.sidebar.text_input(
        "輸入 Google API Key",
        type="password",
        value=st.session_state["google_api_key"],
        help="此 Key 將用於對話與占卜功能"
    )

    # 只要有 Key 就進行配置
    if st.session_state["google_api_key"]:
        genai.configure(api_key=st.session_state["google_api_key"])

    # ═══ 2. 共享空間初始化 ═══
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "shared_board" not in st.session_state:
        st.session_state.shared_board = []
    if "news_list" not in st.session_state:
        st.session_state.news_list = []

    # ═══ 3. 側邊欄：小龍蝦功能選單 ═══
    st.sidebar.divider()
    st.sidebar.subheader("🦞 系統模式")
    mode = st.sidebar.radio(
        "功能切換", 
        ["💬 智能對話", "📰 今日新聞", "📮 郵遞查詢", "💹 今日匯率", "📋 協作白板", "🌟 星座運勢", "🎨 畫圖展示"]
    )

    # ═══ 4. 各功能畫面實作 ═══

    # --- 模式：智能對話 (使用 Google Gemini) ---
    if mode == "💬 智能對話":
        st.title("💬 小龍蝦 AI 智慧對話")
        st.caption("基於 Gemini-2.5-flash 模型")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("請輸入您的問題..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                if not st.session_state["google_api_key"]:
                    st.warning("⚠️ 請先在左側欄位輸入 Google API Key")
                else:
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        # 轉換歷史紀錄格式以符合 Gemini SDK 要求
                        history = [
                            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                            for m in st.session_state.messages[:-1]
                        ]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(prompt)
                        
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"AI 回應失敗: {e}")

    # --- 模式：今日新聞 (RSS 爬蟲) ---
    elif mode == "📰 今日新聞":
        st.title("📰 全球新聞即時觀測站")
        col_l, col_r = st.columns([1, 1.2])
        
        with col_l:
            ch_name = st.selectbox("情報頻道", ["🔥 為你推薦", "🇹🇼 台灣", "🌍 國際", "💻 科技"])
            search_q = st.text_input("🔍 關鍵字搜尋")
            
            if st.button("🛰️ 獲取最新情報", use_container_width=True):
                news_map = {
                    "🔥 為你推薦": "",
                    "🇹🇼 台灣": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd3U0FtdHdaV1JlU0Vsb0x3b0FQAQ",
                    "🌍 國際": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtdHdaV1JlU0Vsb0x3b0FQAQ",
                    "💻 科技": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVd4b1NBTXpXalJmZEdvU0Vsb0x3b0FQAQ"
                }
                try:
                    base_url = "https://news.google.com/rss"
                    if search_q:
                        url = f"{base_url}/search?q={requests.utils.quote(search_q)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
                    elif news_map[ch_name]:
                        url = f"{base_url}/topics/{news_map[ch_name]}?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
                    else:
                        url = f"{base_url}?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
                    
                    res = requests.get(url, timeout=10)
                    soup = BeautifulSoup(res.text, 'xml')
                    st.session_state.news_list = [{
                        "title": item.title.text,
                        "desc": BeautifulSoup(item.description.text if item.description else "", "html.parser").get_text(),
                        "link": item.link.text,
                        "date": item.pubDate.text[:16] if item.pubDate else ""
                    } for item in soup.find_all('item')]
                except Exception as e:
                    st.error(f"新聞載入失敗: {e}")

            if st.session_state.news_list:
                titles = [f"📌 {n['title']}" for n in st.session_state.news_list]
                sel = st.radio("🎯 選取標題閱覽", titles, index=None)
                if sel:
                    st.session_state['current_news'] = next(n for n in st.session_state.news_list if f"📌 {n['title']}" == sel)

        with col_r:
            if st.session_state.get('current_news'):
                n = st.session_state['current_news']
                with st.container(border=True):
                    st.markdown(f"### {n['title']}")
                    st.caption(f"📅 發布時間：{n['date']}")
                    st.divider()
                    st.markdown(f"<div style='font-size:18px; line-height:1.7;'>{n['desc']}</div>", unsafe_allow_html=True)
                    st.link_button("🚀 閱讀完整原文", n['link'], use_container_width=True)
            else:
                st.info("👈 請點擊獲取情報並選擇新聞")

    # --- 模式：郵遞查詢 ---
    elif mode == "📮 郵遞查詢":
        st.title("📮 郵遞區號快速查詢")
        
        # 1. 確認檔案路徑
        file_path = "data/County_h_10906.xml"
        
        if os.path.exists(file_path):
            try:
                # 2. 讀取 XML 內容
                with open(file_path, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                
                # 3. 使用 re.findall 抓取所有縣市名稱 (假設標籤為 <COUNTYNAME>)
                import re
                counties = re.findall(r'<COUNTYNAME>(.*?)</COUNTYNAME>', xml_content)
                
                # 去除重複項並排序
                unique_counties = sorted(list(set(counties)))
                
                if unique_counties:
                    st.success(f"✅ 成功從地圖資料中解析出 {len(unique_counties)} 個縣市")
                    
                    # 4. 讓使用者選擇縣市
                    selected_county = st.selectbox("請選擇縣市：", unique_counties)
                    
                    # 5. 這裡可以串接你的郵遞區號邏輯
                    # 範例：簡單顯示選擇結果
                    st.write(f"你選擇了：**{selected_county}**")
                    st.info(f"💡 接下來可以根據 {selected_county} 進行區域定位或郵遞區號細分。")
                else:
                    st.warning("⚠️ 檔案讀取成功，但找不到縣市名稱標籤，請確認 XML 結構。")
                    
            except Exception as e:
                st.error(f"❌ 檔案解析失敗：{e}")
        else:
            st.error(f"❌ 找不到檔案：{file_path}")
            st.info("請確認你已經將 County_h_10906.xml 放入 data 資料夾中。")

    # --- 模式：今日匯率 ---
    elif mode == "💹 今日匯率":
        st.title("💹 即時外幣匯率 (TWD)")
        try:
            res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
            twd = res["rates"]["TWD"]
            rates = {
                "美金 (USD/TWD)": round(twd, 2),
                "日幣 (JPY/TWD)": round(twd / res["rates"]["JPY"], 4),
                "歐元 (EUR/TWD)": round(twd / res["rates"]["EUR"], 2),
                "人民幣 (CNY/TWD)": round(twd / res["rates"]["CNY"], 2)
            }
            cols = st.columns(4)
            for i, (k, v) in enumerate(rates.items()):
                cols[i].metric(k, v)
            st.caption(f"數據最後更新時間: {res['time_last_update_utc'][:16]}")
        except:
            st.error("無法取得即時匯率數據")

    # --- 模式：協作白板 ---
    elif mode == "📋 協作白板":
        st.title("📋 團隊即時白板")
        with st.container(border=True):
            if not st.session_state.shared_board:
                st.write("目前尚無訊息...")
            for msg in st.session_state.shared_board:
                st.text(msg)
        
        c1, c2 = st.columns([4, 1])
        uname = c2.text_input("暱稱", value="小龍蝦", key="wb_name")
        m_in = c1.text_input("輸入訊息...", key="wb_msg")
        if st.button("發送訊息", use_container_width=True):
            t = datetime.datetime.now().strftime("%H:%M")
            st.session_state.shared_board.append(f"[{t}] {uname}: {m_in}")
            st.rerun()

    # --- 模式：星座運勢 ---
    elif mode == "🌟 星座運勢":
        st.title("🌟 今日星座占卜")
        z = st.selectbox("選擇你的星座", ["白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"])
        if st.button("🔮 獲取今日啟示"):
            if not st.session_state["google_api_key"]:
                st.warning("⚠️ 請先輸入 API Key")
            else:
                with st.spinner("正在觀測星象中..."):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        prompt = f"請以專業占星師的口吻，為{z}寫一段今日運勢，包含整體指數、工作、財運、感情，建議用繁體中文，約 200 字。"
                        response = model.generate_content(prompt)
                        st.success(response.text)
                        st.balloons()
                    except Exception as e:
                        st.error(f"占卜失敗: {e}")

    # --- 模式：畫圖展示 ---
    elif mode == "🎨 畫圖展示":
        st.title("🎨 AI 畫廊展示")
        st.write("這是一個模擬生成畫面的區塊，展示如何結合圖片顯示。")
        st.image("https://images.unsplash.com/photo-1551244072-5d12893278ab?w=1000", caption="AI 生成藝術模擬")
