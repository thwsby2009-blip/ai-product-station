import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import os
import requests
import datetime
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

    # --- 模式：智能對話 ---
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
                    st.warning("⚠️ 請先輸入 API Key")
                else:
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        chat = model.start_chat()
                        response = chat.send_message(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"AI 回應失敗: {e}")

    # --- 模式：今日新聞 ---
    elif mode == "📰 今日新聞":
        st.title("📰 全球新聞即時觀測站")
        col_l, col_r = st.columns([1, 1.2])
        with col_l:
            ch_name = st.selectbox("情報頻道", ["🔥 為你推薦", "🇹🇼 台灣", "🌍 國際", "💻 科技"])
            search_q = st.text_input("🔍 關鍵字搜尋")
            if st.button("🛰️ 獲取最新情報", use_container_width=True):
                news_map = {"🔥 為你推薦": "", "🇹🇼 台灣": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd3U0FtdHdaV1JlU0Vsb0x3b0FQAQ", "🌍 國際": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtdHdaV1JlU0Vsb0x3b0FQAQ", "💻 科技": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVd4b1NBTXpXalJmZEdvU0Vsb0x3b0FQAQ"}
                try:
                    url = f"https://news.google.com/rss/search?q={requests.utils.quote(search_q)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant" if search_q else (f"https://news.google.com/rss/topics/{news_map[ch_name]}?hl=zh-TW&gl=TW&ceid=TW:zh-Hant" if news_map[ch_name] else "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
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
                    st.markdown(f"### {n['title']}"); st.caption(f"📅 {n['date']}")
                    st.markdown(n['desc'], unsafe_allow_html=True)
                    st.link_button("🚀 閱讀原文", n['link'], use_container_width=True)

    # --- 模式：郵遞查詢 (讀取外部 XML 檔案) ---
    elif mode == "📮 郵遞查詢":
        st.title("📮 全台郵遞區號查詢系統")
        base_path = os.path.dirname(__file__)
        xml_file = os.path.join(base_path, "data", "County_h_10906.xml")
        
        if os.path.exists(xml_file):
            try:
                tree = ET.parse(xml_file)
        
                # 動態解析 XML
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                data = []
                # 遍歷 XML 內的所有節點
                for item in root.findall('.//County_h_10906'):
                    data.append({
                        "郵遞區號": item.findtext('欄位1'),
                        "行政區": item.findtext('欄位2'),
                        "英文名稱": item.findtext('欄位3')
                    })
                
                df = pd.DataFrame(data)
                
                # 搜尋介面
                keyword = st.text_input("🔍 輸入區名或郵遞區號進行搜尋")
                if keyword:
                    # 使用 apply 搜尋整列，只要任一欄位包含關鍵字就顯示
                    filtered_df = df[df.apply(lambda r: r.astype(str).str.contains(keyword).any(), axis=1)]
                    st.success(f"找到 {len(filtered_df)} 筆結果")
                    st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
                    
            except Exception as e:
                st.error(f"讀取 XML 發生錯誤: {e}")
        else:
            st.error(f"找不到檔案: {xml_file}")
            st.info("請確認該 XML 檔案已放在程式碼所在的資料夾中。")

    # --- 模式：今日匯率 ---
    elif mode == "💹 今日匯率":
        st.title("💹 即時外幣匯率 (TWD)")
        try:
            res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
            twd = res["rates"]["TWD"]
            rates = {"美金 (USD/TWD)": round(twd, 2), "日幣 (JPY/TWD)": round(twd / res["rates"]["JPY"], 4), "歐元 (EUR/TWD)": round(twd / res["rates"]["EUR"], 2)}
            cols = st.columns(3)
            for i, (k, v) in enumerate(rates.items()): cols[i].metric(k, v)
        except: st.error("無法取得即時匯率數據")

    # --- 模式：協作白板 ---
    elif mode == "📋 協作白板":
        st.title("📋 團隊即時白板")
        with st.container(border=True):
            if not st.session_state.shared_board: st.write("目前尚無訊息...")
            for msg in st.session_state.shared_board: st.text(msg)
        c1, c2 = st.columns([4, 1])
        uname = c2.text_input("暱稱", value="小龍蝦")
        m_in = c1.text_input("輸入訊息...")
        if st.button("發送"):
            if m_in:
                st.session_state.shared_board.append(f"[{datetime.datetime.now().strftime('%H:%M')}] {uname}: {m_in}")
                st.rerun()

    # --- 模式：星座運勢 ---
    elif mode == "🌟 星座運勢":
        st.title("🌟 今日星座占卜")
        z = st.selectbox("選擇星座", ["白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"])
        if st.button("🔮 獲取啟示"):
            if st.session_state["google_api_key"]:
                model = genai.GenerativeModel("gemini-2.5-flash")
                st.write(model.generate_content(f"請寫一段{z}的今日運勢").text)
            else: st.warning("請先輸入 API Key")

    # --- 模式：畫圖展示 ---
    elif mode == "🎨 畫圖展示":
        st.title("🎨 AI 畫廊展示")
        st.image("https://images.unsplash.com/photo-1551244072-5d12893278ab?w=1000")

if __name__ == "__main__":
    run()
