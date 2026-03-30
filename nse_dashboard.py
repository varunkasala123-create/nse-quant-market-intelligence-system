import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.title("🇮🇳 NSE AI Trading Dashboard")

st.button("Refresh")

os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

TRADE_FILE = "data/live_trades.csv"

if not os.path.exists(TRADE_FILE):
    st.warning("No NSE trade data yet")
    st.stop()

trades = pd.read_csv(TRADE_FILE)

intraday = trades[trades["strategy"] == "intraday"]
swing = trades[trades["strategy"] == "swing"]

st.subheader("⚡ Intraday Trades")
st.dataframe(intraday)

st.subheader("📊 Swing Trades")
st.dataframe(swing)

st.subheader("📜 All Trades")
st.dataframe(trades)