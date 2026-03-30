import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.title("AI Trading System Dashboard")

st.button("Refresh")

# Ensure folders exist
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ==============================
# LOAD LIVE TRADES
# ==============================

TRADE_FILE = "data/live_trades.csv"

if not os.path.exists(TRADE_FILE):
    st.warning("No trade data yet")
    st.stop()

trades = pd.read_csv(TRADE_FILE)

# Save all signals to Excel log
trades.to_excel("logs/best_trades.xlsx", index=False)

# ==============================
# SPLIT STRATEGIES
# ==============================

intraday = trades[trades["strategy"] == "intraday"]
swing = trades[trades["strategy"] == "swing"]

intraday = intraday.sort_values("confidence", ascending=False).head(5)
swing = swing.sort_values("confidence", ascending=False).head(5)

# ==============================
# LOAD EXECUTED TRADES
# ==============================

EXECUTED_FILE = "logs/executed_trades.xlsx"

if os.path.exists(EXECUTED_FILE):
    executed_trades = pd.read_excel(EXECUTED_FILE)
else:
    executed_trades = pd.DataFrame(columns=trades.columns)

# ==============================
# INTRADAY TRADES
# ==============================

st.subheader("⚡ Intraday Trade Opportunities")

# ---- HEADER ROW ----
h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(8)

h1.markdown("**Symbol**")
h2.markdown("**Signal**")
h3.markdown("**Entry**")
h4.markdown("**SL**")
h5.markdown("**TP**")
h6.markdown("**Profit %**")
h7.markdown("**Confidence**")
h8.markdown("**Execute**")

for i, row in intraday.iterrows():

    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

    c1.write(row["symbol"])
    c2.write(row["signal"])
    c3.write(row["entry"])
    c4.write(row["sl"])
    c5.write(row["tp"])
    c6.write(row["expected_profit_pct"])
    c7.write(row["confidence"])

    if c8.button("Execute", key=f"intra_{i}"):

        executed_trades = pd.concat(
            [executed_trades, pd.DataFrame([row])],
            ignore_index=True
        )

        executed_trades.to_excel(EXECUTED_FILE, index=False)

        st.success(f"Executed trade: {row['symbol']}")

# ==============================
# SWING TRADES
# ==============================

st.subheader("📊 Swing Trade Opportunities")

if len(swing) == 0:
    st.info("No swing trades right now")

# ---- HEADER ROW ----
h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(8)

h1.markdown("**Symbol**")
h2.markdown("**Signal**")
h3.markdown("**Entry**")
h4.markdown("**SL**")
h5.markdown("**TP**")
h6.markdown("**Profit %**")
h7.markdown("**Confidence**")
h8.markdown("**Execute**")

for i, row in swing.iterrows():

    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

    c1.write(row["symbol"])
    c2.write(row["signal"])
    c3.write(row["entry"])
    c4.write(row["sl"])
    c5.write(row["tp"])
    c6.write(row["expected_profit_pct"])
    c7.write(row["confidence"])

    if c8.button("Execute", key=f"swing_{i}"):

        executed_trades = pd.concat(
            [executed_trades, pd.DataFrame([row])],
            ignore_index=True
        )

        executed_trades.to_excel(EXECUTED_FILE, index=False)

        st.success(f"Executed trade: {row['symbol']}")

# ==============================
# EXECUTED TRADES
# ==============================

st.subheader("✅ Executed Trades")

if len(executed_trades) > 0:

    st.dataframe(
        executed_trades[
            [
                "symbol",
                "strategy",
                "signal",
                "entry",
                "sl",
                "tp",
                "expected_profit_pct",
                "confidence",
            ]
        ]
    )

else:
    st.info("No trades executed yet")

# ==============================
# TRADE LOGS
# ==============================

st.subheader("📜 Trade Logs")

st.dataframe(
    trades[
        [
            "symbol",
            "strategy",
            "signal",
            "entry",
            "sl",
            "tp",
            "expected_profit_pct",
            "confidence",
        ]
    ]
)