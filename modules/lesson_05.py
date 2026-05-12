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
    def get_locations(raw_data, root_key):
        if not raw_data:
            return []
        records = raw_data.get("records", {})
        if isinstance(records, list):
            for item in records:
                if isinstance(item, dict) and (root_key in item or "Location" in item):
                    inner = item.get(root_key, {})
                    if isinstance(inner, list):
                        return inner
                    return inner.get("Location", [])
            return records
        target = records.get(root_key, {})
        if isinstance(target, list):
            return target
        return target.get("Location", []) or records.get("Location", [])

    tide_locs = get_locations(tide_data, "TideForecasts")
    weather_stats = get_locations(weather_data, "Station")

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
                    t_times = curr.get("Time", [])
                    if t_times:
                        latest = t_times[0]
                        st.markdown(f"""
                        <div style="background:#0f1e2d; padding:20px; border-radius:12px; border-left:5px solid #00d4ff; color:white;">
                            <h3 style="margin:0;">📍 {target}</h3>
                            <p style="color:#aaa;">{latest.get('DateTime', '')}</p>
                            <h1 style="color:#00d4ff; font-size:48px;">{latest.get('TideHeight', '--')} <small style="font-size:20px;">m</small></h1>
                            <p>潮別: {latest.get('Tide', '--')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ 未能解析潮汐站點資料")
        else:
            st.warning("⚠️ 潮汐資料載入失敗，請檢查 API Key 是否有效")
