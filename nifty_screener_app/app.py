# NOTE: This version is for environments where Streamlit is not installed.
# It gracefully warns the user instead of failing with ImportError.

try:
    import streamlit as st
    import pandas as pd
    import requests
    from datetime import datetime
except ModuleNotFoundError as e:
    print("\n❌ Required module is missing:", e)
    print("👉 Please install required packages using: pip install streamlit pandas requests\n")
    exit(1)

# --- CONFIG ---
NSE_URL = "https://www.nseindia.com"
OC_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

@st.cache_data(ttl=300)
def fetch_option_chain():
    session = requests.Session()
    session.get(NSE_URL, headers=HEADERS)
    response = session.get(OC_URL, headers=HEADERS)
    data = response.json()
    return data['records']['data']

@st.cache_data(ttl=300)
def fetch_india_vix():
    url = "https://www.nseindia.com/api/marketStatus"
    session = requests.Session()
    session.get(NSE_URL, headers=HEADERS)
    response = session.get(url, headers=HEADERS)
    data = response.json()
    for index in data['marketState']:
        if index['index'] == "India VIX":
            return float(index['last'])
    return None

# Classify Trend Based on OI and Price
def classify_trend(price_change, oi_change):
    if price_change > 0 and oi_change > 0:
        return "Long Buildup"
    elif price_change < 0 and oi_change > 0:
        return "Short Buildup"
    elif price_change > 0 and oi_change < 0:
        return "Short Covering"
    elif price_change < 0 and oi_change < 0:
        return "Long Unwinding"
    else:
        return "Neutral"

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📈 Nifty Screener + Option Chain Analyzer")

with st.spinner("Fetching live data from NSE..."):
    oc_data = fetch_option_chain()
    vix = fetch_india_vix()

# India VIX Display
if vix:
    st.metric("India VIX (Volatility Index)", f"{vix:.2f}")
else:
    st.warning("India VIX data unavailable")

# Parse Option Chain Data
records = []
for row in oc_data:
    strike = row.get("strikePrice")
    ce = row.get("CE")
    if ce:
        price_change = ce.get("change") or 0
        oi_change = ce.get("changeinOpenInterest") or 0
        trend = classify_trend(price_change, oi_change)
        records.append({
            "Strike": strike,
            "Price Change": price_change,
            "OI Change": oi_change,
            "Open Interest": ce.get("openInterest"),
            "Volume": ce.get("totalTradedVolume"),
            "Trend": trend
        })

# DataFrame
df = pd.DataFrame(records)

# UI Display
st.subheader("Call Option Chain Trends (NIFTY)")
selected_trend = st.selectbox("Filter by Trend", ["All"] + df["Trend"].unique().tolist())

if selected_trend != "All":
    df = df[df["Trend"] == selected_trend]

st.dataframe(df.style.applymap(
    lambda x: "background-color: lightgreen" if x == "Long Buildup" else 
              "background-color: salmon" if x == "Short Buildup" else 
              "background-color: lightblue" if x == "Short Covering" else 
              "background-color: orange" if x == "Long Unwinding" else "",
    subset=["Trend"]
))

# Export
st.download_button("Download CSV", data=df.to_csv(index=False), file_name="nifty_option_trends.csv")

# Footer
st.caption("Built using live data from NSE. Refresh every 5 minutes.")
