import streamlit as st
import pandas as pd
import plotly.express as px
from nsepython import nse_optionchain_scrapper, get_vix

st.set_page_config(layout="wide")
st.title("📊 Nifty Option Chain + India VIX + Weightage Heatmap")

# --- Fetch India VIX ---
vix = get_vix()
if vix:
    st.metric("India VIX (Volatility Index)", vix)
else:
    st.warning("India VIX data not available")

# --- Fetch Nifty Option Chain ---
option_data = nse_optionchain_scrapper('NIFTY')
if not option_data:
    st.error("Option chain data not available")
else:
    raw_data = option_data['records']['data']
    calls = []
    for row in raw_data:
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

    # Simple trend classifier based on OI change and lastPrice
    def classify_trend(row):
        if row['changeinOpenInterest'] > 0 and row['lastPrice'] > 0:
            return "Long Buildup"
        elif row['changeinOpenInterest'] > 0 and row['lastPrice'] <= 0:
            return "Short Buildup"
        elif row['changeinOpenInterest'] < 0 and row['lastPrice'] > 0:
            return "Short Coverin
