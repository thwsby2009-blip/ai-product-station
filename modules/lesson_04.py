import streamlit as st
import os
import pandas as pd
import requests
import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import google.generativeai as genai

def run():
    # ═══ 1. API Key 與環境設定 ═══
    if "google_api_key" not in st.session_state:
        st.session_state["google_api_key"] = ""

    st.sidebar.header("🔑 AI 設定中心")
    st.session_state["google_api_key"] = st.sidebar.text_input(
        "輸入 Google API Key",
        type="password",
        value=st.session_state["google_api_key"]
    )

    if st.session_state["google_api_key"]:
        genai.configure(api_key=st.session_state["google_api_key"])

    # ═══ 2. 共享空間初始化 ═══
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "shared_board" not in st.session_state:
        st.session_state.shared_board = []
    if "news_list" not in st.session_state:
        st.session_state.news_list = []

    # ═══ 3. 側邊欄：功能選單 ═══
    st.sidebar.divider()
    st.sidebar.subheader("🦞 系統模式")
    mode = st.sidebar.radio(
        "功能切換", 
        ["💬 智能對話", "📰 今日新聞", "📮 郵遞查詢", "💹 今日匯率", "📋 協作白板", "🌟 星座運勢", "🎨 畫圖展示"]
    )

    # ═══ 4. 各功能畫面實作 ═══

    if mode == "💬 智能對話":
        st.title("💬 小龍蝦 AI 智慧對話")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("請輸入您的問題..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                if not st.session_state["google_api_key"]:
                    st.warning("⚠️ 請先在左側輸入 API Key")
                else:
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"AI 回應失敗: {e}")

    elif mode == "📰 今日新聞":
        st.title("📰 全球新聞即時觀測站")
        col_l, col_r = st.columns([1, 1.2])
        with col_l:
            ch_name = st.selectbox("情報頻道", ["🔥 為你推薦", "🇹🇼 台灣", "🌍 國際", "💻 科技"])
            search_q = st.text_input("🔍 關鍵字搜尋")
            if st.button("🛰️ 獲取最新情報", use_container_width=True):
                news_map = {"🔥 為你推薦": "", "🇹🇼 台灣": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd3U0FtdHdaV1JlU0Vsb0x3b0FQAQ", "🌍 國際": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtdHdaV1JlU0Vsb0x3b0FQAQ", "💻 科技": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVd4b1NBTXpXalJmZEdvU0Vsb0x3b0FQAQ"}
                try:
                    base_url = "https://news.google.com/rss"
                    url = f"{base_url}/search?q={requests.utils.quote(search_q)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant" if search_q else (f"{base_url}/topics/{news_map[ch_name]}?hl=zh-TW&gl=TW&ceid=TW:zh-Hant" if news_map[ch_name] else f"{base_url}?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
                    res = requests.get(url, timeout=10)
                    soup = BeautifulSoup(res.text, 'xml')
                    st.session_state.news_list = [{"title": item.title.text, "desc": BeautifulSoup(item.description.text if item.description else "", "html.parser").get_text(), "link": item.link.text, "date": item.pubDate.text[:16] if item.pubDate else ""} for item in soup.find_all('item')]
                except Exception as e: st.error(f"新聞載入失敗: {e}")

            if st.session_state.news_list:
                titles = [f"📌 {n['title']}" for n in st.session_state.news_list]
                sel = st.radio("🎯 選取標題閱覽", titles, index=None)
                if sel: st.session_state['current_news'] = next(n for n in st.session_state.news_list if f"📌 {n['title']}" == sel)
        with col_r:
            if st.session_state.get('current_news'):
                n = st.session_state['current_news']
                with st.container(border=True):
                    st.markdown(f"### {n['title']}"); st.caption(f"📅 發布時間：{n['date']}"); st.divider()
                    st.markdown(f"<div style='font-size:18px; line-height:1.7;'>{n['desc']}</div>", unsafe_allow_html=True)
                    st.link_button("🚀 閱讀完整原文", n['link'], use_container_width=True)

    elif mode == "📮 郵遞查詢":
        st.title("📮 全台郵遞區號查詢系統")
        
        # 這裡放入你準備好的 XML 長字串
        xml_data = """<dataroot>
            <County_h_10906><欄位1>100</欄位1><欄位2>臺北市中正區</欄位2><欄位3>Zhongzheng Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>103</欄位1><欄位2>臺北市大同區</欄位2><欄位3>Datong Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>104</欄位1><欄位2>臺北市中山區</欄位2><欄位3>Zhongshan Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>105</欄位1><欄位2>臺北市松山區</欄位2><欄位3>Songshan Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>106</欄位1><欄位2>臺北市大安區</欄位2><欄位3>Da'an Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>108</欄位1><欄位2>臺北市萬華區</欄位2><欄位3>Wanhua Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>110</欄位1><欄位2>臺北市信義區</欄位2><欄位3>Xinyi Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>111</欄位1><欄位2>臺北市士林區</欄位2><欄位3>Shilin Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>112</欄位1><欄位2>臺北市北投區</欄位2><欄位3>Beitou Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>114</欄位1><欄位2>臺北市內湖區</欄位2><欄位3>Neihu Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>115</欄位1><欄位2>臺北市南港區</欄位2><欄位3>Nangang Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>116</欄位1><欄位2>臺北市文山區</欄位2><欄位3>Wenshan Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>200</欄位1><欄位2>基隆市仁愛區</欄位2><欄位3>Ren'ai Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>201</欄位1><欄位2>基隆市信義區</欄位2><欄位3>Xinyi Dist.</欄位3></County_h_10906>
            <County_h_10906><欄位1>202</欄位1><欄位2>基隆市中正區</欄位2><欄位3>Zhongzheng Dist.</欄位3></County_h_10906>
        </dataroot>""" 
        
        try:
            root = ET.fromstring(xml_data)
            districts = [{"郵遞區號": item.findtext('欄位1'), "行政區": item.findtext('欄位2'), "英文": item.findtext('欄位3')} for item in root.findall('County_h_10906')]
            df = pd.DataFrame(districts)
            
            # --- 實作搜尋功能 ---
            keyword = st.text_input("🔍 請輸入關鍵字（例如：中正、100、Zhongzheng）")
            
            if keyword:
                # 使用 str.contains 同時篩選中英文與郵遞區號，na=False 避免空值報錯
                filtered_df = df[
                    df['行政區'].str.contains(keyword, na=False) | 
                    df['郵遞區號'].str.contains(keyword, na=False) |
                    df['英文'].str.contains(keyword, case=False, na=False)
                ]
                st.write(f"找到 {len(filtered_df)} 筆結果：")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.write("顯示全部列表：")
                st.dataframe(df, use_container_width=True)
                
        except Exception as e:
            st.error(f"XML 解析失敗: {e}")

    elif mode == "💹 今日匯率":
        st.title("💹 即時外幣匯率 (TWD)")
        try:
            res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
            twd = res["rates"]["TWD"]
            rates = {"美金 (USD/TWD)": round(twd, 2), "日幣 (JPY/TWD)": round(twd / res["rates"]["JPY"], 4), "歐元 (EUR/TWD)": round(twd / res["rates"]["EUR"], 2), "人民幣 (CNY/TWD)": round(twd / res["rates"]["CNY"], 2)}
            cols = st.columns(4)
            for i, (k, v) in enumerate(rates.items()): cols[i].metric(k, v)
            st.caption(f"數據最後更新: {res['time_last_update_utc'][:16]}")
        except: st.error("無法取得即時匯率數據")

    elif mode == "📋 協作白板":
        st.title("📋 團隊即時白板")
        with st.container(border=True):
            if not st.session_state.shared_board: st.write("目前尚無訊息...")
            for msg in st.session_state.shared_board: st.text(msg)
        c1, c2 = st.columns([4, 1])
        uname = c2.text_input("暱稱", value="小龍蝦", key="wb_name")
        m_in = c1.text_input("輸入訊息...", key="wb_msg")
        if st.button("發送訊息", use_container_width=True):
            if m_in:
                t = datetime.datetime.now().strftime("%H:%M")
                st.session_state.shared_board.append(f"[{t}] {uname}: {m_in}")
                st.rerun()

    elif mode == "🌟 星座運勢":
        st.title("🌟 今日星座占卜")
        z = st.selectbox("選擇你的星座", ["白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"])
        if st.button("🔮 獲取今日啟示"):
            if not st.session_state["google_api_key"]: st.warning("⚠️ 請先輸入 API Key")
            else:
                with st.spinner("正在觀測星象中..."):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        response = model.generate_content(f"請以專業占星師口吻，為{z}寫一段今日運勢，繁體中文，約 150 字。")
                        st.success(response.text)
                    except Exception as e: st.error(f"占卜失敗: {e}")

    elif mode == "🎨 畫圖展示":
        st.title("🎨 AI 畫廊展示")
        st.image("https://images.unsplash.com/photo-1551244072-5d12893278ab?w=1000")

if __name__ == "__main__":
    run()
