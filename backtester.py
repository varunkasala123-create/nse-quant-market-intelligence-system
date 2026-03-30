import pandas as pd
import numpy as np

from feature_engine import add_features
from config import TP_MULTIPLIER, SL_MULTIPLIER


SLIPPAGE = 0.0002
COMMISSION = 0.0004


def simulate_trade(df, i, horizon):

    price = df.close.iloc[i]
    atr = df.atr.iloc[i]

    if pd.isna(atr):
        return 0

    entry = price * (1 + SLIPPAGE)

    tp = entry + atr * TP_MULTIPLIER
    sl = entry - atr * SL_MULTIPLIER

    future = df.iloc[i+1:i+horizon+1]

    for _, row in future.iterrows():

        if row.low <= sl:
            pnl = (sl - entry) / entry
            pnl = pnl - COMMISSION
            return pnl

        if row.high >= tp:
            pnl = (tp - entry) / entry
            pnl = pnl - COMMISSION
            return pnl

    exit_price = future.close.iloc[-1]

    pnl = (exit_price - entry) / entry

    pnl = pnl - COMMISSION

    return pnl


def walk_forward_backtest(df, model, horizon=5):

    print("\n===== WALK FORWARD BACKTEST =====\n")

    df = add_features(df)

    if len(df) < 200:
        print("Dataset too small for backtest")
        return

    ema50 = df["ema50"]
    ema200 = df["ema200"]

    atr = df["atr"]
    price = df["close"]

    volatility = atr / price
    trend_strength = (ema50 - ema200) / price

    conditions = [
        (ema50 > ema200) & (volatility > 0.001) & (trend_strength > 0.0005),
        (ema50 < ema200) & (volatility > 0.001) & (trend_strength < -0.0005)
    ]

    choices = ["UPTREND", "DOWNTREND"]

    df["regime"] = np.select(conditions, choices, default="SIDEWAYS")

    feature_cols = df.columns.tolist()

    for col in ["target", "symbol", "timestamp", "regime"]:
        if col in feature_cols:
            feature_cols.remove(col)

    X = df[feature_cols]

    probs = model.predict_proba(X)[:,1]

    df["prob"] = probs

    trades = []

    for i in range(len(df) - horizon - 1):

        if df.prob.iloc[i] > 0.6:

            if df.regime.iloc[i] == "SIDEWAYS":
                continue

            pnl = simulate_trade(df, i, horizon)

            # Safety clamp to prevent overflow
            pnl = np.clip(pnl, -0.2, 0.2)

            trades.append(pnl)

    trades = np.array(trades)

    if len(trades) == 0:
        print("No trades generated")
        return

    # -----------------------------
    # PERFORMANCE
    # -----------------------------

    equity = np.cumprod(1 + trades)

    # Prevent numerical explosion
    equity = np.clip(equity, 0.0001, 1e6)

    # Prevent overflow
    equity = np.nan_to_num(equity, nan=1.0, posinf=1.0, neginf=1.0)

    peak = np.maximum.accumulate(equity)

    drawdown = (equity - peak) / peak

    max_drawdown = np.min(drawdown)

    win_rate = np.mean(trades > 0)

    gross_profit = trades[trades > 0].sum()
    gross_loss = abs(trades[trades < 0].sum())

    profit_factor = gross_profit / (gross_loss + 1e-10)

    sharpe = np.mean(trades) / (np.std(trades) + 1e-10) * np.sqrt(252)

    avg_trade = np.mean(trades)

    # -----------------------------
    # OUTPUT
    # -----------------------------

    print("Trades:", len(trades))
    print("Win rate:", round(win_rate*100,2), "%")
    print("Profit factor:", round(profit_factor,2))
    print("Sharpe:", round(sharpe,2))
    print("Average trade:", round(avg_trade*100,3), "%")
    print("Max drawdown:", round(max_drawdown*100,2), "%")