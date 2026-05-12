import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import google.generativeai as genai
import urllib3

def run():  # 所有內容現在都縮排在 run 裡面了
    # 關閉 SSL 警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # ==================== UI ====================
    # 注意：子模組不需要 set_page_config，由主程式 app.py 負責
    
    st.title("📊 課程3 AI券商級看盤系統（選股 + K線 + AI分析）")

    # ==================== SESSION ====================
    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = None

    if "confirmed" not in st.session_state:
        st.session_state.confirmed = False

    if "google_api_key" not in st.session_state:
        st.session_state["google_api_key"] = ""

    # ==================== GOOGLE API ====================
    st.sidebar.title("🔑 AI設定（Google Gemini）")

    st.session_state["google_api_key"] = st.sidebar.text_input(
        "請輸入 Google API Key",
        type="password",
        value=st.session_state["google_api_key"]
    )

    # ==================== TWSE 全市場 ====================
    @st.cache_data(ttl=3600)
    def get_twse_all():
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=20, verify=False)
            if res.status_code != 200:
                st.error(f"TWSE API 狀態錯誤：{res.status_code}")
                return pd.DataFrame(columns=["name", "ticker"])

            data = res.json()
            df = pd.DataFrame(data)
            col_map = {}
            for c in df.columns:
                c_lower = str(c).lower()
                if "code" in c_lower: col_map[c] = "code"
                if "name" in c_lower: col_map[c] = "name"
            
            df = df.rename(columns=col_map)
            if "code" not in df.columns or "name" not in df.columns:
                return pd.DataFrame(columns=["name", "ticker"])

            df = df.dropna(subset=["code", "name"])
            df["ticker"] = df["code"].astype(str) + ".TW"
            return df[["name", "ticker"]]
        except Exception as e:
            st.error(f"TWSE API 錯誤：{e}")
            return pd.DataFrame(columns=["name", "ticker"])

    df_stocks = get_twse_all()

    # ==================== SEARCH ====================
    st.sidebar.title("🔍 全市場選股")
    keyword = st.sidebar.text_input("搜尋股票（名稱 / 代碼）")

    if keyword:
        filtered = df_stocks[
            df_stocks["name"].astype(str).str.contains(keyword, na=False) |
            df_stocks["ticker"].astype(str).str.contains(keyword.upper(), na=False)
        ]
    else:
        filtered = df_stocks.head(50)

    if filtered.empty:
        st.sidebar.warning("⚠️ 查無股票資料")
        st.stop()

    stock_options = {
        f"{row['name']} ({row['ticker']})": row["ticker"]
        for _, row in filtered.iterrows()
    }

    selected_label = st.sidebar.selectbox("📌 選擇股票", list(stock_options.keys()))
    selected_ticker = stock_options[selected_label]
    st.session_state.selected_ticker = selected_ticker

    if st.sidebar.button("🚀 載入K線"):
        st.session_state.confirmed = True

    st.sidebar.success(f"目前選擇：{selected_ticker}")

    # ==================== HELPERS ====================
    def safe_float(x):
        try:
            if isinstance(x, pd.Series): return float(x.iloc[-1])
            return float(x)
        except: return 0.0

    def clean(df):
        if df is None or df.empty: return pd.DataFrame()
        df = df.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).title() for c in df.columns]
        for c in ["Open", "High", "Low", "Close", "Volume"]:
            if c not in df.columns: df[c] = 0
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df.dropna(subset=["Close"])

    def indicator(df):
        df = df.copy()
        df["MA20"] = df["Close"].rolling(20, min_periods=1).mean()
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean())
        loss = (-delta.where(delta < 0, 0).ewm(span=14, adjust=False).mean())
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        return df

    def get_kline(symbol):
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            df = clean(df)
            if df.empty: return df
            return indicator(df).tail(120)
        except: return pd.DataFrame()

    def build_prompt(df, ticker):
        last = df.iloc[-1]
        return f"請分析台股：\n股票：{ticker}\n收盤價：{last['Close']}\n成交量：{last['Volume']}\nRSI：{last['RSI']}\nMA20：{last['MA20']}\n\n請給我：\n1. 趨勢判斷\n2. 技術面分析\n3. 風險\n4. 短線操作建議\n請使用繁體中文。"

    def call_ai(prompt):
        if not st.session_state["google_api_key"]: return "❌ 請先輸入 API Key"
        try:
            genai.configure(api_key=st.session_state["google_api_key"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e: return f"⚠️ AI錯誤：{str(e)}"

    # ==================== MAIN ====================
    if st.session_state.confirmed and st.session_state.selected_ticker:
        ticker = st.session_state.selected_ticker
        st.subheader(f"📈 {ticker}")
        df = get_kline(ticker)

        if df.empty:
            st.warning("⚠️ 無K線資料")
            st.stop()

        last_close = safe_float(df["Close"].iloc[-1])
        prev_close = safe_float(df["Close"].iloc[-2]) if len(df) > 1 else last_close
        diff = last_close - prev_close
        last_rsi = safe_float(df["RSI"].iloc[-1])

        c1, c2, c3 = st.columns(3)
        c1.metric("收盤價", f"{last_close:.2f}", f"{diff:.2f}")
        c2.metric("RSI", f"{last_rsi:.2f}")
        c3.write(f"更新：{datetime.now().strftime('%H:%M:%S')}")

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
        fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="K線"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="成交量"), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        if st.button("🤖 AI分析這檔股票"):
            with st.spinner("AI分析中..."):
                result = call_ai(build_prompt(df, ticker))
                st.subheader("🤖 AI分析結果")
                st.write(result)
    else:
        st.info("👉 請搜尋股票 → 選擇 → 載入K線")
