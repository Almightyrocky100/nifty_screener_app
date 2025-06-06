import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Nifty Option Chain + India VIX + Weightage Heatmap")

# --- Fetch India VIX using yfinance ---
def fetch_india_vix():
    try:
        vix_ticker = "^INDIAVIX"
        vix = yf.Ticker(vix_ticker)
        data = vix.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        else:
            return None
    except Exception:
        return None

vix = fetch_india_vix()
if vix:
    st.metric("India VIX (Volatility Index)", vix)
else:
    st.warning("India VIX data not available")

# --- Fetch Nifty Option Chain using yfinance ---
nifty = yf.Ticker("^NSEI")

expiries = nifty.options
if not expiries:
    st.error("No option expiry data found for Nifty.")
else:
    expiry = st.selectbox("Select Expiry Date", expiries)
    opt_chain = nifty.option_chain(expiry)

    df_calls = opt_chain.calls.copy()
    # Calculate price and OI change to classify trends
    df_calls['Price Change'] = df_calls['lastPrice'].diff().fillna(0)
    df_calls['OI Change'] = df_calls['openInterest'].diff().fillna(0)

    def classify_trend(row):
        if row['Price Change'] > 0 and row['OI Change'] > 0:
            return "Long Buildup"
        elif row['Price Change'] < 0 and row['OI Change'] > 0:
            return "Short Buildup"
        elif row['Price Change'] > 0 and row['OI Change'] < 0:
            return "Short Covering"
        elif row['Price Change'] < 0 and row['OI Change'] < 0:
            return "Long Unwinding"
        else:
            return "Neutral"

    df_calls['Trend'] = df_calls.apply(classify_trend, axis=1)

    st.subheader(f"Nifty Call Option Chain - Expiry {expiry}")
    trend_filter = st.selectbox("Filter by Trend", ["All"] + df_calls['Trend'].unique().tolist())
    if trend_filter != "All":
        df_filtered = df_calls[df_calls['Trend'] == trend_filter]
    else:
        df_filtered = df_calls

    st.dataframe(df_filtered[['contractSymbol', 'strike', 'lastPrice', 'openInterest', 'volume', 'impliedVolatility', 'Trend']])

    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name=f"nifty_option_chain_{expiry}.csv", mime='text/csv')

# --- Nifty 50 Weightage Heatmap ---
st.markdown("---")
st.header("🔥 Nifty 50 Stocks Weightage Heatmap")

weightage_data = {
    "Ticker": [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "HDFC", "ICICIBANK", "KOTAKBANK",
        "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "ASIANPAINT", "AXISBANK", "LT",
        "MARUTI", "SUNPHARMA", "BAJFINANCE", "WIPRO", "NESTLEIND", "TITAN",
        "ULTRACEMCO", "DIVISLAB", "JSWSTEEL", "POWERGRID", "TECHM", "ONGC",
        "ADANIGREEN", "HCLTECH", "TATASTEEL", "BRITANNIA", "M&M", "EICHERMOT",
        "DRREDDY", "COALINDIA", "HDFCLIFE", "INDUSINDBK", "CIPLA", "HEROMOTOCO",
        "BAJAJFINSV", "BPCL", "GRASIM", "HINDALCO", "SHREECEM", "TATAMOTORS",
        "ICICIPRULI", "SBILIFE", "UPL", "BIOCON", "VEDL"
    ],
    "Weightage": [
        13.5, 8.3, 7.0, 6.5, 5.0, 4.3, 3.2,
        3.0, 2.8, 2.5, 2.0, 1.8, 1.7, 1.5,
        1.5, 1.4, 1.3, 1.3, 1.2, 1.1,
        1.0, 0.9, 0.9, 0.8, 0.8, 0.7,
        0.6, 0.6, 0.6, 0.5, 0.5, 0.5,
        0.5, 0.4, 0.4, 0.4, 0.4, 0.4,
        0.4, 0.4, 0.3, 0.3, 0.3, 0.3,
        0.3, 0.3, 0.3, 0.3, 0.2
    ]
}

df_weightage = pd.DataFrame(weightage_data)

fig = px.imshow(
    [df_weightage['Weightage'].values],
    labels=dict(x="Stocks", y="Weightage"),
    x=df_weightage['Ticker'],
    y=["Weightage %"],
    color_continuous_scale="Viridis",
    aspect="auto"
)

fig.update_layout(
    title="Nifty 50 Stocks Weightage Heatmap",
    xaxis_tickangle=-45,
    height=300,
    margin=dict(l=20, r=20, t=50, b=50)
)

st.plotly_chart(fig, use_container_width=True)
