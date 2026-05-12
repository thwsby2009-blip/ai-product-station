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

        # ================= 路徑（雲端穩定版） =================
        base_dir = os.path.dirname(os.path.abspath(__file__))
        xml_file = os.path.join(
            base_dir,
            "..",
            "data",
            "County_h_10906.xml"
        )
        xml_file = os.path.normpath(xml_file)

        # ================= 檔案存在檢查 =================
        if not os.path.exists(xml_file):
            st.error(f"❌ 找不到檔案：{xml_file}")
            st.stop()

        # ================= XML 解析 =================
        try:
            # 讀取檔案，跳過第一行（瀏覽器加的提示文字）
            with open(xml_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # 跳過非 XML 的第一行
            xml_content = "".join(
                line for line in lines if not line.startswith("This XML file")
            )
            root = ET.fromstring(xml_content)

            data = []

            # 你的 XML 結構：直接 children 就是 County_h_10906
            for item in root.findall("County_h_10906"):
                data.append({
                    "郵遞區號": item.findtext("欄位1"),
                    "行政區": item.findtext("欄位2"),
                    "英文名稱": item.findtext("欄位3")
                })

            df = pd.DataFrame(data)

        except Exception as e:
            st.error(f"❌ XML 解析失敗：{e}")
            st.stop()

        # ================= 資料載入（只載一次，存進 session_state） =================
        if "zip_df" not in st.session_state:
            try:
                with open(xml_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                xml_content = "".join(
                    line for line in lines if not line.startswith("This XML file")
                )
                root = ET.fromstring(xml_content)

                data = []
                for item in root.findall("County_h_10906"):
                    data.append({
                        "郵遞區號": item.findtext("欄位1"),
                        "行政區": item.findtext("欄位2"),
                        "英文名稱": item.findtext("欄位3")
                    })
                st.session_state.zip_df = pd.DataFrame(data)
                st.success(f"✅ 載入成功：{len(st.session_state.zip_df)} 筆資料")
            except Exception as e:
                st.error(f"❌ 資料載入失敗：{e}")
                st.stop()

        df = st.session_state.zip_df

        # ================= 三層連動選單 =================
        st.markdown("### 🏙️ 三步驟查詢：縣市 → 區域 → 郵遞區號")

        # 第一步：選縣市
        df["縣市"] = df["行政區"].str.extract(r"^(.+?[縣市])")
        cities = sorted(df["縣市"].dropna().unique())
        selected_city = st.selectbox("1️⃣ 選擇縣市", [""] + cities)

        # 第二步：選區域
        selected_district = ""
        selected_zip = ""
        if selected_city:
            districts = sorted(df[df["縣市"] == selected_city]["行政區"].tolist())
            selected_district = st.selectbox("2️⃣ 選擇行政區", [""] + districts)

        # 第三步：顯示結果
        if selected_district:
            result = df[df["行政區"] == selected_district]
            if not result.empty:
                selected_zip = result.iloc[0]["郵遞區號"]
                st.success(f"✅ **郵遞區號：{selected_zip}**")
                st.info(f"📍 {selected_district}（{result.iloc[0]['英文名稱']}）")

        # ================= 快速搜尋（輔助） =================
        with st.expander("🔍 也可以直接用關鍵字搜尋"):
            keyword = st.text_input("輸入郵遞區號或行政區名稱")
            if keyword:
                filtered = df[
                    df.astype(str).apply(
                        lambda row: row.str.contains(keyword, case=False).any(),
                        axis=1
                    )
                ]
                st.info(f"🔎 找到 {len(filtered)} 筆結果")
                st.dataframe(filtered, use_container_width=True)

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
