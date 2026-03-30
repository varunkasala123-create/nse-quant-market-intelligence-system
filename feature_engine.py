import pandas as pd
import numpy as np


def add_features(df):

    df = df.copy()

    # ===============================
    # BASIC RETURNS
    # ===============================

    df["returns"] = df["close"].pct_change()

    df["returns_5"] = df["close"].pct_change(5)
    df["returns_10"] = df["close"].pct_change(10)
    df["returns_20"] = df["close"].pct_change(20)


    # ===============================
    # MOVING AVERAGES
    # ===============================

    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()


    # ===============================
    # TREND STRENGTH
    # ===============================

    df["trend_strength"] = (df["ema50"] - df["ema200"]) / df["close"]


    # ===============================
    # RSI
    # ===============================

    delta = df["close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss

    df["rsi"] = 100 - (100 / (1 + rs))


    # ===============================
    # ATR (VOLATILITY)
    # ===============================

    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)

    true_range = ranges.max(axis=1)

    df["atr"] = true_range.rolling(14).mean()


    # ===============================
    # VOLATILITY NORMALIZATION
    # ===============================

    df["volatility"] = df["atr"] / df["close"]


    # ===============================
    # VOLUME FEATURES
    # ===============================

    df["volume_ma20"] = df["volume"].rolling(20).mean()

    df["volume_spike"] = df["volume"] / df["volume_ma20"]


    # ===============================
    # PRICE DISTANCE FROM TREND
    # ===============================

    df["price_vs_ema20"] = (df["close"] - df["ema20"]) / df["ema20"]
    df["price_vs_ema50"] = (df["close"] - df["ema50"]) / df["ema50"]


    # ===============================
    # CLEAN DATA
    # ===============================

    df = df.replace([np.inf, -np.inf], np.nan)

    df = df.dropna()

    return df