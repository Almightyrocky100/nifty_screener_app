import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Nifty Screener + Option Chain Analyzer + Weightage Heatmap")

# --- Fetch India VIX using yfinance ---
def fetch_india_vix_yf():
    try:
        vix_ticker = "^INDIAVIX"
        vix = yf.Ticker(vix_ticker)
        data = vix.history(period="1d")
        if not data.empty:
            last_vix = data['Close'].iloc[-1]
            return round(last_vix, 2)
        return None
    except Exception as e:
        return None

vix = fetch_india_vix_yf()
if vix:
    st.metric("India VIX (Volatility Index)", f"{vix}")
else:
    st.warning("India VIX data unavailable")

# --- Fetch Option Chain Data for Nifty from yfinance ---
# Note: yfinance doesn't provide detailed option chain OI & price change by default for indices.
# We'll fetch available expiry dates and call/put data for demo.

nifty = yf.Ticker("^NSEI")  # Nifty 50 index symbol in yfinance

expiries = nifty.options
if not expiries:
    st.error("No option expiry data found for Nifty via yfinance.")
else:
    expiry = st.selectbox("Select Expiry Date", expiries)
    opt_chain = nifty.option_chain(expiry)
    
    # Use calls dataframe for analysis
    df_calls = opt_chain.calls
    # Demo: Use 'impliedVolatility' and 'volume' as proxies for interest and activity
    df_calls['Price Change'] = df_calls['lastPrice'].diff().fillna(0)
    df_calls['OI Change'] = df_calls['openInterest'].diff().fillna(0)

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
    
    df_calls['Trend'] = df_calls.apply(lambda x: classify_trend(x['Price Change'], x['OI Change']), axis=1)
    
    st.subheader(f"Call Option Chain Trends for Expiry {expiry}")
    
    selected_trend = st.selectbox("Filter by Trend", ["All"] + df_calls["Trend"].unique().tolist())
    df_filtered = df_calls if selecte
