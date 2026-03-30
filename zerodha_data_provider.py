from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "paste api key here"
ACCESS_TOKEN = "paste generated access token here"

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)


def get_instrument_map():
    instruments = kite.instruments("NSE")
    return {i["tradingsymbol"]: i["instrument_token"] for i in instruments}


instrument_map = get_instrument_map()


def fetch_data(symbol, interval="5minute", lookback=8000):
    token = instrument_map.get(symbol)

    if not token:
        return None

    end = datetime.now()
    start = end - timedelta(days=30)

    try:
        data = kite.historical_data(
            token,
            from_date=start,
            to_date=end,
            interval=interval
        )
    except Exception as e:
        print(f"Fetch failed for {symbol}: {e}")
        return None

    df = pd.DataFrame(data)

    if df.empty:
        return None

    df = df.rename(columns={
        "date": "timestamp",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume"
    })

    df = df.set_index("timestamp")
    df["symbol"] = symbol

    return df