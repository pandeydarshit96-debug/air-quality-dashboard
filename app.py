"""Air Quality Monitoring Dashboard — Streamlit only."""

from datetime import datetime, timezone
import math
from urllib.parse import quote

import requests
import streamlit as st

WAQI_API_URL = "https://api.waqi.info/feed/{city}/"
POLLUTANT_LABELS = {
    "pm25": "PM2.5", "pm10": "PM10", "o3": "Ozone (O3)",
    "no2": "Nitrogen Dioxide (NO2)", "so2": "Sulfur Dioxide (SO2)",
    "co": "Carbon Monoxide (CO)",
}


def valid_number(value):
    """Reject missing/invalid readings instead of inventing zero readings."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def classify_aqi(aqi):
    """Return category, emoji, advisory using the US EPA AQI scale."""
    if aqi is None:
        return "Unknown", "❓", "No overall air-quality reading is available."
    if aqi <= 50:
        return "Good", "✅", "Air quality is satisfactory for most people."
    if aqi <= 100:
        return "Moderate", "⚠️", "Unusually sensitive people should consider limiting prolonged outdoor exertion."
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups", "⚠️", "Sensitive groups should limit prolonged outdoor exertion."
    if aqi <= 200:
        return "Unhealthy", "❌", "Everyone should limit prolonged outdoor activity, especially sensitive groups."
    if aqi <= 300:
        return "Very Unhealthy", "☠️", "Everyone should limit outdoor exertion; sensitive groups should avoid it."
    return "Hazardous", "☠️", "Everyone should avoid outdoor exertion and follow local health guidance."


def fetch_air_quality(city, token):
    """Fetch one real feed, with safe, readable errors."""
    if not token:
        raise ValueError("Add waqi_token to .streamlit/secrets.toml or Cloud secrets.")
    try:
        response = requests.get(
            WAQI_API_URL.format(city=quote(city, safe="")),
            params={"token": token}, timeout=15,
        )
    except requests.Timeout:
        raise ValueError("The API timed out. Please try again.") from None
    except requests.RequestException:
        raise ValueError("Cannot connect to the API. Check your internet connection.") from None
    if response.status_code in (401, 403):
        raise ValueError("API access denied. Check your WAQI token.")
    if response.status_code == 429:
        raise ValueError("API rate limit reached. Please wait and retry.")
    if not response.ok:
        raise ValueError(f"API error (HTTP {response.status_code}). Try again later.")
    try:
        data = response.json()
    except ValueError:
        raise ValueError("The API returned an unreadable response.") from None
    if not isinstance(data, dict):
        raise ValueError("Unexpected API response.")
    if data.get("status") != "ok":
        message = str(data.get("data", "")).lower()
        if "quota" in message or "limit" in message:
            raise ValueError("API rate limit reached. Please wait and retry.")
        if "token" in message or "key" in message:
            raise ValueError("Invalid API token. Check your WAQI token.")
        raise ValueError("No feed available. Check the city spelling or try another city/station.")
    if not isinstance(data.get("data"), dict) or not data["data"]:
        raise ValueError("No station data returned.")
    return data["data"]


def parse_readings(api_data):
    """Extract actual readings. WAQI city.name identifies the reporting station."""
    city = api_data.get("city")
    city = city if isinstance(city, dict) else {}
    iaqi = api_data.get("iaqi")
    iaqi = iaqi if isinstance(iaqi, dict) else {}
    raw_time = api_data.get("time")
    server_ts = None
    if isinstance(raw_time, dict):
        iso = raw_time.get("iso")
        if not iso and raw_time.get("s") and raw_time.get("tz"):
            iso = f"{raw_time['s']}{raw_time['tz']}"
        try:
            parsed = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                server_ts = parsed
        except ValueError:
            pass
    readings = []
    for code, label in POLLUTANT_LABELS.items():
        item = iaqi.get(code)
        value = valid_number(item.get("v")) if isinstance(item, dict) else None
        if value is not None:
            readings.append({"Pollutant": label, "Individual AQI": value})
    return {
        "aqi": valid_number(api_data.get("aqi")),
        "station": city.get("name") or "Not reported",
        "readings": readings, "server_ts": server_ts,
        "attributions": api_data.get("attributions") or [],
    }


# Streamlit UI — no separate backend or frontend files.
st.set_page_config(page_title="Air Quality Monitoring Dashboard", page_icon="🌬️", layout="wide")
st.title("🌬️ Air Quality Monitoring Dashboard")
st.caption("Real-time air quality from WAQI API • Search any city")

try:
    token = st.secrets.get("waqi_token", "")
except Exception:
    token = ""
token = token.strip() if isinstance(token, str) else ""
if not token or token == "your_waqi_token_here":
    token = ""
    st.info("🔑 Please add your WAQI token to `.streamlit/secrets.toml` (local) or Streamlit Cloud secrets.")

# Input section — clean card
with st.container(border=True):
    st.subheader("🔍 Search City")
    col1, col2 = st.columns([4, 1])
    with col1:
        city = st.text_input("City name", value="Jodhpur", placeholder="e.g. Jodhpur, Delhi, Mumbai", label_visibility="collapsed")
    with col2:
        search_clicked = st.button("Search", use_container_width=True, type="primary", disabled=not token)

# Last retrieval time
fetch_time = st.session_state.get("fetch_time")
if fetch_time:
    st.info(f"✅ Last successful data retrieval (UTC): {fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.info("ℹ️ No data retrieved yet. Enter a city and click Search.")

# Fetch logic
result = None
if search_clicked:
    if not city.strip():
        st.warning("⚠️ Please enter a city name.")
    else:
        with st.spinner("Fetching live air-quality data..."):
            try:
                result = parse_readings(fetch_air_quality(city.strip(), token))
                st.session_state.fetch_time = datetime.now(timezone.utc)
            except ValueError as exc:
                st.error(f"❌ {exc}")

if not result:
    st.stop()

# Results section
st.divider()
st.subheader(f"📍 {city.strip()} — Air Quality")
st.write("**Reporting station:**", result["station"])
st.caption("A city search may resolve to a nearby monitoring station. Coverage depends on WAQI station availability.")

# Observation time
observed = result["server_ts"]
if observed:
    st.caption(f"🕒 Station observation time: {observed.isoformat(sep=' ')}")
    age_hours = (datetime.now(timezone.utc) - observed).total_seconds() / 3600
    if age_hours > 3:
        st.warning("⚠️ Delayed data: this report is over 3 hours old. Not a current reading.")
    elif age_hours < -1 / 6:
        st.warning("⚠️ Station timestamp is in the future. Freshness cannot be verified.")
else:
    st.warning("⚠️ Station observation time unavailable.")

# AQI Card
aqi = result["aqi"]
category, emoji, advisory = classify_aqi(aqi)

with st.container(border=True):
    st.markdown("### 📊 Air Quality Index (AQI)")
    mcol1, mcol2 = st.columns(2)
    with mcol1:
        st.metric("Reported AQI (US EPA)", f"{aqi:g}" if aqi is not None else "N/A")
    with mcol2:
        st.metric("Category", f"{emoji} {category}")
    st.write(f"**Health Advisory:** {advisory}")

st.caption("US EPA scale: 0–50 Good • 51–100 Moderate • 101–150 Unhealthy for Sensitive Groups • 151–200 Unhealthy • 201–300 Very Unhealthy • 300+ Hazardous")

# Pollutants
st.markdown("### 🧪 Pollutant Readings")
st.caption("Individual AQI indices (not raw concentrations). Missing pollutants are omitted.")

if result["readings"]:
    metrics = result["readings"]
    cols = st.columns(min(4, len(metrics)))
    for i, item in enumerate(metrics):
        with cols[i % len(cols)]:
            st.metric(f"{item['Pollutant']} AQI", f"{item['Individual AQI']:g}")

    chart_data = {item["Pollutant"]: [item["Individual AQI"]] for item in metrics}
    st.bar_chart(chart_data)
else:
    st.info("No individual pollutant readings were provided by the station.")

if aqi is not None:
    st.markdown("### 🎯 AQI Gauge")
    st.progress(min(aqi / 500, 1.0), text=f"{category} — AQI {aqi:g} (0–500 scale)")

st.divider()
st.subheader("📡 Data Sources")
st.link_button("World Air Quality Index Project (WAQI)", "https://aqicn.org/")
if isinstance(result["attributions"], list):
    for source in result["attributions"]:
        if isinstance(source, dict):
            name = str(source.get("name") or "Monitoring agency")
            st.write(f"• {name}")
            url = source.get("url")
            if isinstance(url, str) and url.startswith(("https://", "http://")):
                st.link_button(f"Open {name}", url)

st.caption("Readings are provisional. Three hours is an app freshness rule, not a provider guarantee. Not medical advice.")