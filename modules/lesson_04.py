import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import os
import requests
import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

def run():

    # ═══ 1. API Key ═══
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

    # ═══ 2. 初始化 ═══
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "shared_board" not in st.session_state:
        st.session_state.shared_board = []

    if "news_list" not in st.session_state:
        st.session_state.news_list = []

    # ═══ 3. 模式選單 ═══
    st.sidebar.divider()
    mode = st.sidebar.radio(
        "功能切換",
        [
            "💬 智能對話",
            "📰 今日新聞",
            "📮 郵遞查詢",
            "💹 今日匯率",
            "📋 協作白板",
            "🌟 星座運勢",
            "🎨 畫圖展示"
        ]
    )

    # ═════════════════════════════
    # 💬 智能對話
    # ═════════════════════════════
    if mode == "💬 智能對話":

        st.title("💬 小龍蝦 AI 智慧對話")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("請輸入問題..."):

            st.session_state.messages.append(
                {"role": "user", "content": prompt}
            )

            with st.chat_message("assistant"):

                if not st.session_state["google_api_key"]:
                    st.warning("請輸入 API Key")

                else:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    st.write(response.text)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": response.text}
                    )

    # ═════════════════════════════
    # 📰 今日新聞
    # ═════════════════════════════
    elif mode == "📰 今日新聞":

        st.title("📰 新聞")

        st.info("略（你原本OK）")

    # ═════════════════════════════
    # 📮 郵遞查詢（已修正）
    # ═════════════════════════════
    elif mode == "📮 郵遞查詢":

        st.title("📮 全台郵遞區號查詢系統")

    import os
    import xml.etree.ElementTree as ET

    # ================= 路徑（雲端穩定版） =================
    xml_file = os.path.join(
        os.getcwd(),
        "data",
        "County_h_10906.xml"
    )

    # ================= 檔案存在檢查 =================
    if not os.path.exists(xml_file):
        st.error(f"❌ 找不到檔案：{xml_file}")
        st.stop()

    # ================= XML 解析 =================
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        data = []

        # 你的 XML 結構：直接 children 就是 County_h_10906
        for item in root.findall("./County_h_10906"):

            data.append({
                "郵遞區號": item.findtext("欄位1"),
                "行政區": item.findtext("欄位2"),
                "英文名稱": item.findtext("欄位3")
            })

        df = pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ XML 解析失敗：{e}")
        st.stop()

    # ================= 資料顯示 =================
    st.success(f"✅ 載入成功：{len(df)} 筆資料")
    st.dataframe(df, use_container_width=True)

    # ================= 搜尋功能 =================
    st.divider()
    st.subheader("🔍 搜尋郵遞區號 / 行政區")

    keyword = st.text_input("請輸入關鍵字（例如：100 / 中正區 / Taipei）")

    if keyword:

        filtered_df = df[
            df.astype(str).apply(
                lambda row: row.str.contains(keyword, case=False).any(),
                axis=1
            )
        ]

        st.info(f"🔎 找到 {len(filtered_df)} 筆結果")
        st.dataframe(filtered_df, use_container_width=True)

    else:

        st.caption("輸入關鍵字開始搜尋")

    # ═════════════════════════════
    # 💹 匯率
    # ═════════════════════════════
    elif mode == "💹 今日匯率":

        st.title("💹 匯率")

        try:
            res = requests.get(
                "https://open.er-api.com/v6/latest/USD"
            ).json()

            twd = res["rates"]["TWD"]

            st.metric("USD/TWD", twd)

        except:
            st.error("匯率失敗")

    # ═════════════════════════════
    # 📋 白板
    # ═════════════════════════════
    elif mode == "📋 協作白板":

        st.title("白板")

    # ═════════════════════════════
    # 🌟 星座
    # ═════════════════════════════
    elif mode == "🌟 星座運勢":

        st.title("星座")

    # ═════════════════════════════
    # 🎨 畫圖
    # ═════════════════════════════
    elif mode == "🎨 畫圖展示":

        st.title("畫圖")

        st.image(
            "https://images.unsplash.com/photo-1551244072-5d12893278ab?w=1000"
        )


if __name__ == "__main__":
    run()
