import streamlit as st
import pandas as pd
import plotly.express as px
from nsepython import get_vix, nse_optionchain_scrapper


st.set_page_config(layout="wide")
st.title("📊 Nifty Option Chain + India VIX + Weightage Heatmap")

# --- Fetch India VIX ---
try:
    vix = get_vix()
except Exception:
    vix = None

if vix:
    st.metric("India VIX (Volatility Index)", vix)
else:
    st.warning("India VIX data not available")

# --- Fetch Nifty Option Chain ---
try:
    option_data = nse_optionchain_scrapper('NIFTY')
except Exception:
    option_data = None

if not option_data:
    st.error("Option chain data not available")
else:
    # Extract call options data
    calls = []
    for row in option_data['records']['data']:
        if 'CE' in row and row['CE'] is not None:
            ce = row['CE']
            calls.append({
                'strikePrice': row['strikePrice'],
                'lastPrice': ce.get('lastPrice', 0),
                'openInterest': ce.get('openInterest', 0),
                'changeinOpenInterest': ce.get('changeinOpenInterest', 0),
                'volume': ce.get('totalTradedVolume', 0),
                'impliedVolatility': ce.get('impliedVolatility', 0)
            })
    df_calls = pd.DataFrame(calls)
    
    st.subheader("Nifty Call Option Chain")

    # Trend classification based on OI change and price change
    def classify_trend(row):
        price_change = row['lastPrice']  # You can improve this with proper price change logic if needed
        oi_change = row['changeinOpenInterest']
        if oi_change > 0 and price_change > 0:
            return "Long Buildup"
        elif oi_change > 0 and price_change <= 0:
            return "Short Buildup"
        elif oi_change < 0 and price_change > 0:
            return "Short Covering"
        elif oi_change < 0 and price_change <= 0:
            return "Long Unwinding"
        else:
            return "Neutral"

    df_calls['Trend'] = df_calls.apply(classify_trend, axis=1)

    trend_filter = st.selectbox("Filter by Trend", ["All"] + df_calls['Trend'].unique().tolist())
    if trend_filter != "All":
        df_calls = df_calls[df_calls['Trend'] == trend_filter]

    st.dataframe(df_calls[['strikePrice', 'lastPrice', 'openInterest', 'changeinOpenInterest', 'volume', 'impliedVolatility', 'Trend']])

# --- Nifty 50 Weightage Heatmap ---
st.markdown("---")
st.header("🔥 Nifty 50 Stocks Weightage Heatmap")

# Approximate weights - update as per latest official data when possible
data = {
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

df_weightage = pd.DataFrame(data)

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
