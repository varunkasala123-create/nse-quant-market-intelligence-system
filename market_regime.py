from feature_engine import add_features


def detect_market_regime(df):

    df = add_features(df)

    if df is None or len(df) < 50:
        return "UNKNOWN"

    ema50 = df.ema50.iloc[-1]
    ema200 = df.ema200.iloc[-1]

    atr = df.atr.iloc[-1]
    price = df.close.iloc[-1]

    volatility = atr / price

    if ema50 > ema200 and volatility > 0.0006:
        return "UPTREND"

    elif ema50 < ema200 and volatility > 0.0006:
        return "DOWNTREND"

    else:
        return "SIDEWAYS"