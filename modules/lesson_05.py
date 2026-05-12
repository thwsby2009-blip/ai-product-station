import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

def run():

    # ═══ 1. API Key ═══
    if "cwa_api_key" not in st.session_state:
        st.session_state["cwa_api_key"] = ""

    st.sidebar.header("⚓ 海象監控中心")
    st.session_state["cwa_api_key"] = st.sidebar.text_input(
        "輸入 CWA API Key",
        type="password",
        value=st.session_state["cwa_api_key"]
    )

    cwa_key = st.session_state["cwa_api_key"]

    if not cwa_key:
        st.info("🔑 請在左側輸入 CWA API Key 以開始載入資料")
        return

    # ═══ 2. 統一抓取工具 ═══
    import ssl
    _ssl_ctx = ssl._create_unverified_context()
    
    def safe_fetch(api_id, api_key):
        fixed_id = api_id.replace('0-', 'O-')
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{fixed_id}"
        try:
            r = requests.get(url, params={"Authorization": api_key}, timeout=10, verify=False)
            return r.json() if r.status_code == 200 else None
        except:
            return None

    # ═══ 3. 資料載入 ═══
    with st.spinner("📡 正在載入海象資料..."):
        tide_data = safe_fetch("F-A0021-001", cwa_key)
        obs_data = safe_fetch("O-B0075-001", cwa_key)
        weather_data = safe_fetch("O-A0003-001", cwa_key)

    # ═══ 4. 解析邏輯 ═══
    def get_tide_locations(raw_data):
        """專門解析潮汐資料：回傳 Location dict 的 list"""
        if not raw_data:
            return []
        records = raw_data.get("records", {})
        forecasts = records.get("TideForecasts", [])
        if not isinstance(forecasts, list):
            return []
        result = []
        for item in forecasts:
            loc = item.get("Location")
            if isinstance(loc, dict) and loc.get("LocationName"):
                result.append(loc)
        return result

    def get_weather_stations(raw_data):
        """專門解析氣象站資料"""
        if not raw_data:
            return []
        records = raw_data.get("records", {})
        stations = records.get("Station", [])
        return stations if isinstance(stations, list) else []

    tide_locs = get_tide_locations(tide_data)
    weather_stats = get_weather_stations(weather_data)

    # ═══ 5. 畫面佈局 ═══
    st.title("🌊 台灣海象即時儀表板")
    st.caption("資料來源：中央氣象署開放資料平臺")

    col_map, col_info = st.columns([2.5, 1])

    with col_map:
        st.subheader("🗺️ 全台站點分佈")
        m = folium.Map(location=[23.7, 121.0], zoom_start=7, tiles="OpenStreetMap")

        for s in weather_stats[:50]:
            try:
                lat = float(s.get("StationLatitude", s.get("Latitude")))
                lon = float(s.get("StationLongitude", s.get("Longitude")))
                folium.CircleMarker(
                    [lat, lon], radius=5, color="orange", fill=True,
                    tooltip=f"氣象站: {s.get('StationName')}"
                ).add_to(m)
            except:
                continue

        st_folium(m, width="100%", height=500)

    with col_info:
        st.subheader("📊 即時數據報表")
        if tide_locs:
            loc_names = [l.get("LocationName") for l in tide_locs if l.get("LocationName")]
            if loc_names:
                target = st.selectbox("切換位置", loc_names)
                curr = next((l for l in tide_locs if l.get("LocationName") == target), None)
                if curr:
                    # 從 TimePeriods -> Daily -> Time 取得最新一筆潮汐
                    daily_list = curr.get("TimePeriods", {}).get("Daily", [])
                    all_times = []
                    for day in daily_list:
                        for t in day.get("Time", []):
                            all_times.append(t)
                    
                    if all_times:
                        # 找最新的（日期最大的）
                        latest = max(all_times, key=lambda x: x.get("DateTime", ""))
                        tide_h = latest.get("TideHeights", {})
                        height = tide_h.get("AboveLocalMSL", tide_h.get("AboveTWVD", "--"))
                        # 找到當天的 TideRange
                        day_data = next((d for d in daily_list if any(t.get("DateTime","").startswith(d.get("Date","")) for t in [latest])), None)
                        tide_range = day_data.get("TideRange", "") if day_data else ""
                        st.markdown(f"""
                        <div style="background:#0f1e2d; padding:20px; border-radius:12px; border-left:5px solid #00d4ff; color:white;">
                            <h3 style="margin:0;">📍 {target}</h3>
                            <p style="color:#aaa;">{latest.get('DateTime', '')} ｜ 潮差: {tide_range}</p>
                            <h1 style="color:#00d4ff; font-size:48px;">{height} <small style="font-size:20px;">cm</small></h1>
                            <p>潮別: {latest.get('Tide', '--')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info(f"📍 {target}：暫無潮汐時序資料")
                else:
                    st.warning("⚠️ 無法取得該站點資料")
            else:
                st.warning("⚠️ 未能解析潮汐站點資料")
        else:
            st.warning("⚠️ 潮汐資料載入失敗，請檢查 API Key 是否有效")
