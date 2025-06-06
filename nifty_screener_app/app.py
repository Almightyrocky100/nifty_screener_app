import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📈 Nifty 50 Stocks Live Screener with Option Chain (using yfinance)")

# Nifty 50 tickers on Yahoo Finance (with '.NS' suffix)
nifty50_tickers = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HDFC.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS",
    "ITC.NS", "ASIANPAINT.NS", "AXISBANK.NS", "LT.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "BAJFINANCE.NS", "WIPRO.NS", "NESTLEIND.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "DIVISLAB.NS", "JSWSTEEL.NS", "POWERGRID.NS", "TECHM.NS",
    "ONGC.NS", "ADANIGREEN.NS", "HCLTECH.NS", "TATASTEEL.NS", "BRITANNIA.NS",
    "M&M.NS", "EICHERMOT.NS", "DRREDDY.NS", "COALINDIA.NS", "HDFCLIFE.NS",
    "INDUSINDBK.NS", "CIPLA.NS", "HEROMOTOCO.NS", "BAJAJFINSV.NS", "BPCL.NS",
    "GRASIM.NS", "HINDALCO.NS", "SHREECEM.NS", "TATAMOTORS.NS", "DIVISLAB.NS",
    "ICICIPRULI.NS", "SBILIFE.NS", "UPL.NS", "BIOCON.NS", "VEDL.NS"
]

@st.cache_data(ttl=300)
def fetch_stock_data(tickers):
    data = yf.download(tickers, period="1d", group_by='ticker', threads=True)
    records = []
    for ticker in tickers:
        try:
            ticker_data = data[ticker].iloc[-1]
            open_price = ticker_data['Open']
            close_price = ticker_data['Close']
            volume = ticker_data['Volume']
            change = ((close_price - open_price) / open_price) * 100
            if change > 1:
                trend = "Very Bullish"
            elif change > 0:
                trend = "Bullish"
            elif change < -1:
                trend = "Very Bearish"
            elif change < 0:
                trend = "Bearish"
            else:
                trend = "Neutral"
            records.append({
                "Ticker": ticker,
                "Open": open_price,
                "Close": close_price,
                "Volume": volume,
                "% Change": round(change, 2),
                "Trend": trend
            })
        except Exception as e:
            continue
    df = pd.DataFrame(records)
    return df

st.sidebar.header("Filters")
selected_trends = st.sidebar.multiselect(
    "Select Trends",
    options=["Very Bullish", "Bullish", "Neutral", "Bearish", "Very Bearish"],
    default=["Very Bullish", "Bullish", "Neutral", "Bearish", "Very Bearish"]
)

with st.spinner("Fetching live stock data..."):
    df_stocks = fetch_stock_data(nifty50_tickers)

filtered_df = df_stocks[df_stocks['Trend'].isin(selected_trends)]

st.subheader("Nifty 50 Stocks Live Data")
st.dataframe(filtered_df.sort_values(by="% Change", ascending=False), use_container_width=True)

# India VIX from Yahoo Finance (symbol ^INDIAVIX or fallback)
try:
    vix_ticker = yf.Ticker("^INDIAVIX")
    vix_data = vix_ticker.history(period="1d")
    vix_last = vix_data['Close'][-1]
    st.metric("India VIX (Volatility Index)", f"{vix_last:.2f}")
except:
    st.warning("India VIX data unavailable")

# NIFTY Option Chain snapshot (calls and puts summary)
st.subheader("NIFTY Option Chain Snapshot")

nifty_ticker = yf.Ticker("^NSEI")  # Yahoo ticker for Nifty 50 index
try:
    options_dates = nifty_ticker.options
    if options_dates:
        expiry = options_dates[0]  # nearest expiry
        opt_chain = nifty_ticker.option_chain(expiry)
        
        calls = opt_chain.calls[['strike', 'lastPrice', 'change', 'volume', 'openInterest']]
        puts = opt_chain.puts[['strike', 'lastPrice', 'change', 'volume', 'openInterest']]

        st.markdown(f"**Nearest Expiry Date:** {expiry}")

        st.markdown("**Call Options**")
        st.dataframe(calls.head(20), use_container_width=True)
        
        st.markdown("**Put Options**")
        st.dataframe(puts.head(20), use_container_width=True)
    else:
        st.info("Option chain data not available currently.")
except Exception as e:
    st.error(f"Failed to fetch option chain data: {e}")

# CSV download
csv = filtered_df.to_csv(index=False)
st.download_button(label="Download Nifty 50 Stock Data as CSV", data=csv, file_name="nifty50_live_data.csv", mime="text/csv")
