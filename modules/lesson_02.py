import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import google.generativeai as genai

# ==================== UI ====================
st.set_page_config(page_title="AI券商級看盤系統", layout="wide")
st.title("📊 課程3 AI券商級看盤系統（選股 + K線 + AI分析）")

# ==================== SESSION ====================
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

if "google_api_key" not in st.session_state:
    st.session_state["google_api_key"] = ""

# ==================== GOOGLE API KEY ====================
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

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(
            url,
            headers=headers,
            timeout=20
            verify=False
        )

        # 檢查狀態
        if res.status_code != 200:
            st.error(f"TWSE API 狀態錯誤：{res.status_code}")
            return pd.DataFrame(columns=["name", "ticker"])

        data = res.json()

        # 檢查格式
        if not isinstance(data, list):
            st.error("TWSE API 回傳格式異常")
            return pd.DataFrame(columns=["name", "ticker"])

        df = pd.DataFrame(data)

        # 自動找欄位
        col_map = {}

        for c in df.columns:

            c_lower = str(c).lower()

            if "code" in c_lower:
                col_map[c] = "code"

            if "name" in c_lower:
                col_map[c] = "name"

        df = df.rename(columns=col_map)

        # 檢查必要欄位
        if "code" not in df.columns or "name" not in df.columns:
            st.error("TWSE 欄位解析失敗")
            st.write(df.columns)
            return pd.DataFrame(columns=["name", "ticker"])

        # 清理資料
        df = df.dropna(subset=["code", "name"])

        # 建立 ticker
        df["ticker"] = df["code"].astype(str) + ".TW"

        return df[["name", "ticker"]]

    except Exception as e:

        st.error(f"TWSE API 錯誤：{e}")

        return pd.DataFrame(columns=["name", "ticker"])


df_stocks = get_twse_all()
# ==================== SEARCH ====================
st.sidebar.title("🔍 全市場選股")

keyword = st.sidebar.text_input("搜尋股票（名稱 / 代碼）")

# 過濾股票
if keyword:
    filtered = df_stocks[
        df_stocks["name"].astype(str).str.contains(keyword, na=False) |
        df_stocks["ticker"].astype(str).str.contains(keyword.upper(), na=False)
    ]
else:
    filtered = df_stocks.head(50)

# 沒資料時顯示錯誤
if filtered.empty:
    st.sidebar.warning("⚠️ 查無股票資料")
    st.write("目前 df_stocks 資料：")
    st.write(df_stocks.head())
    st.write("資料筆數：", df_stocks.shape)
    st.stop()

# 建立選單（真正綁定 ticker）
stock_options = {
    f"{row['name']} ({row['ticker']})": row['ticker']
    for _, row in filtered.iterrows()
}

# 股票選擇
selected_label = st.sidebar.selectbox(
    "📌 選擇股票",
    list(stock_options.keys())
)

# 真正 ticker
selected_ticker = stock_options[selected_label]

# session
st.session_state.selected_ticker = selected_ticker

# 載入按鈕
if st.sidebar.button("🚀 載入K線"):
    st.session_state.confirmed = True

# 顯示目前股票
st.sidebar.success(f"目前選擇：{selected_ticker}")

# ==================== SAFE FUNCTION ====================
def safe_float(x):
    try:
        if isinstance(x, pd.Series):
            return float(x.iloc[-1])
        return float(x)
    except:
        return 0.0


def clean(df):
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [str(c).title() for c in df.columns]

    for c in ["Open", "High", "Low", "Close", "Volume"]:
        if c not in df.columns:
            df[c] = 0

    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["Close"])

    return df


def indicator(df):
    df = df.copy()

    df["MA20"] = df["Close"].rolling(20, min_periods=1).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).ewm(span=14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()

    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df


def get_kline(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        df = clean(df)

        if df.empty:
            return df

        return indicator(df).tail(120)

    except:
        return pd.DataFrame()


# ==================== AI ====================
def build_prompt(df, ticker):
    last = df.iloc[-1]

    return f"""
請分析台股：

股票：{ticker}

收盤價：{last['Close']}
成交量：{last['Volume']}
RSI：{last['RSI']}
MA20：{last['MA20']}

請給我：
1. 趨勢判斷（多/空/震盪）
2. 技術面分析
3. 風險
4. 操作建議（短線）

請用繁體中文。
"""


def call_ai(prompt):

    if not st.session_state["google_api_key"]:
        return "❌ 請先輸入 Google API Key"

    try:
        genai.configure(api_key=st.session_state["google_api_key"])

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"⚠️ AI暫時無法使用：{str(e)}"


# ==================== MAIN ====================
if st.session_state.confirmed and st.session_state.selected_ticker:

    ticker = st.session_state.selected_ticker
    st.subheader(f"📈 {ticker}")

    df = get_kline(ticker)

    if df.empty:
        st.warning("⚠️ 無K線資料")
        st.stop()

    # ================= KPI =================
    last_close = safe_float(df["Close"].iloc[-1])
    prev_close = safe_float(df["Close"].iloc[-2]) if len(df) > 1 else last_close
    diff = last_close - prev_close

    last_rsi = safe_float(df["RSI"].iloc[-1])

    c1, c2, c3 = st.columns(3)
    c1.metric("收盤價", f"{last_close:.2f}", f"{diff:.2f}")
    c2.metric("RSI", f"{last_rsi:.2f}")
    c3.write(f"資料：{len(df)} 筆 | 更新：{datetime.now().strftime('%H:%M:%S')}")

    # ================= CHART =================
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="K線"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA20"],
        name="MA20"
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Volume"],
        name="Volume"
    ), row=2, col=1)

    fig.update_layout(
        height=800,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ================= AI BUTTON =================
    st.divider()

    if st.button("🤖 AI分析這檔股票"):

        with st.spinner("AI分析中..."):

            prompt = build_prompt(df, ticker)
            result = call_ai(prompt)

        st.subheader("🤖 AI分析結果")
        st.write(result)

else:
    st.info("👉 請搜尋股票 → 選擇 → 載入K線")
