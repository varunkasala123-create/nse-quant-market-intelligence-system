import pandas as pd
import numpy as np
import joblib
import time
import os

from config import *
from backtester import walk_forward_backtest
from concurrent.futures import ThreadPoolExecutor
from model_trainer import train_model
from feature_engine import add_features
from risk_manager import position_size
from market_regime import detect_market_regime
from dataset_recorder import save_market_data

# 🔁 FORCE NSE MODE
USE_NSE = True

# ===============================
# NSE IMPORTS ONLY
# ===============================

from zerodha_data_provider import fetch_data as nse_fetch_data
from nse_symbols import get_nse_symbols
from nse_market_hours import is_nse_market_open

def get_sentiment(symbol):
    return 0  # disabled


INTRADAY_MODEL_PATH = "models/intraday_model.pkl"
SWING_MODEL_PATH = "models/swing_model.pkl"

DATASET_PATH = "dataset/market_data.parquet"
LIVE_TRADE_PATH = "data/live_trades.csv"

# ===============================
# NSE MARKET ONLY
# ===============================

MARKET_UNIVERSE = get_nse_symbols()


# ===============================
# FETCH DATA (ONLY NSE)
# ===============================

def fetch_data(symbol):
    return nse_fetch_data(symbol)


# ===============================
# PREDICTION (UNCHANGED)
# ===============================

def predict(df, model):

    if df is None:
        return None

    df = add_features(df)

    if len(df) < 50:
        return None

    features = df.drop(columns=["target","symbol"], errors="ignore")

    try:
        prob = model.predict_proba(features.tail(1))[0][1]
    except:
        return None

    return prob


# ===============================
# GENERATE TRADE (UNCHANGED)
# ===============================

def generate_trade(symbol, model):
    df = fetch_data(symbol)

    if df is None:
        return None

    save_market_data(symbol, df)

    df = add_features(df)

    if len(df) < 50:
        return None

    prob = predict(df, model)

    if prob is None:
        return None

    regime = detect_market_regime(df)

    price = df.close.iloc[-1]
    atr = df.atr.iloc[-1]
    rsi = df.rsi.iloc[-1]
    vol_spike = df.volume_spike.iloc[-1]

    if pd.isna(atr) or atr <= 0:
        return None

    signal = None

    # Primary ML thresholds
    if prob >= BUY_THRESHOLD:
        signal = "BUY"
    elif prob <= SELL_THRESHOLD:
        signal = "SELL"

    if signal is None:
        return None

    # Softer regime filter:
    # allow SIDEWAYS only if confidence is stronger
    if regime == "SIDEWAYS":
        if signal == "BUY" and prob < 0.52:
            return None
        if signal == "SELL" and prob > 0.48:
            return None

    # Extra sanity filters instead of hard regime rejection
    if signal == "BUY" and rsi > 75:
        return None
    if signal == "SELL" and rsi < 25:
        return None

    trend_strength = df.trend_strength.iloc[-1]

    if signal == "BUY" and trend_strength < 0:
        return None

    if signal == "SELL" and trend_strength > 0:
        return None


    # Optional: require at least neutral liquidity participation
    if pd.notna(vol_spike) and vol_spike < 0.8:
        return None

    tp = price + atr * TP_MULTIPLIER
    sl = price - atr * SL_MULTIPLIER

    if signal == "SELL":
        tp = price - atr * TP_MULTIPLIER
        sl = price + atr * SL_MULTIPLIER

    if signal == "BUY":
        profit_pct = (tp - price) / price * 100
    else:
        profit_pct = (price - tp) / price * 100

    size = position_size(10000, price, sl)

    trade = {
        "time": pd.Timestamp.now(),
        "symbol": symbol,
        "signal": signal,
        "confidence": round(prob, 3),
        "regime": regime,
        "rsi": round(float(rsi), 2),
        "volume_spike": round(float(vol_spike), 2) if pd.notna(vol_spike) else None,
        "entry": round(price, 2),
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "expected_profit_pct": round(profit_pct, 2),
        "position_size": size
    }

    return trade

# ===============================
# SAVE TRADES (UNCHANGED)
# ===============================

def save_live_trades(intraday_trades, swing_trades):

    trades = []

    for t in intraday_trades:
        t["strategy"] = "intraday"
        trades.append(t)

    for t in swing_trades:
        t["strategy"] = "swing"
        trades.append(t)

    df = pd.DataFrame(trades)

    os.makedirs("data", exist_ok=True)

    df.to_csv(LIVE_TRADE_PATH, index=False)


# ===============================
# SCAN MARKET (UNCHANGED)
# ===============================

def scan_market(model):

    trades = []

    with ThreadPoolExecutor(max_workers=2) as executor:

        results = executor.map(
            lambda s: generate_trade(s, model),
            MARKET_UNIVERSE
        )

    for r in results:

        if r is not None:
            trades.append(r)

    trades = sorted(
        trades,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return trades


# ===============================
# TRAIN MODELS (UNCHANGED)
# ===============================

def train_models():

    if not os.path.exists(DATASET_PATH):
        print("Dataset not found")
        return None, None

    df = pd.read_parquet(DATASET_PATH)

    print("Total dataset rows:", len(df))

    print("\nTraining intraday model...\n")

    intraday_model = train_model(
        df,
        horizon=3,
        model_name=INTRADAY_MODEL_PATH
    )

    print("\nRunning backtest...\n")

    walk_forward_backtest(df, intraday_model)

    print("\nTraining swing model...\n")

    swing_model = train_model(
        df,
        horizon=15,
        model_name=SWING_MODEL_PATH
    )

    return intraday_model, swing_model


# ===============================
# MAIN ENGINE (ONLY NSE HOURS)
# ===============================

def main():

    print("\n==============================")
    print("NSE AI TRADING ENGINE STARTED")
    print("==============================\n")

    if os.path.exists(INTRADAY_MODEL_PATH) and os.path.exists(SWING_MODEL_PATH):

        print("Loading existing models...\n")

        intraday_model = joblib.load(INTRADAY_MODEL_PATH)
        swing_model = joblib.load(SWING_MODEL_PATH)

    else:

        intraday_model, swing_model = train_models()

    print("\nStarting NSE market scanner...\n")

    swing_timer = 0
    swing_trades = []

    while True:

        if not is_nse_market_open():
            print("Market closed")
            time.sleep(60)
            continue

        print("\n==============================")
        print("INTRADAY SCAN")
        print("==============================\n")

        intraday_trades = scan_market(intraday_model)[:5]

        for t in intraday_trades:
            print(t["symbol"], t["signal"], t["confidence"])

        if swing_timer >= 6:

            print("\n==============================")
            print("SWING SCAN")
            print("==============================\n")

            swing_trades = scan_market(swing_model)[:5]

            for t in swing_trades:
                print(t["symbol"], t["signal"], t["confidence"])

            swing_timer = 0

        save_live_trades(intraday_trades, swing_trades)

        swing_timer += 1

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()