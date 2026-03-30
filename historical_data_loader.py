from datetime import datetime, timedelta
import pandas as pd
import time

from zerodha_data_provider import fetch_data
from dataset_recorder import save_market_data
from nse_symbols import get_nse_symbols


# ==============================
# CONFIG
# ==============================

DAYS = 30   # fetch extra to safely cover 21 trading days
INTERVAL = "5minute"


# ==============================
# FILTER NSE MARKET HOURS
# ==============================

def filter_market_hours(df):
    df = df.copy()

    # Keep only weekdays
    df = df[df.index.dayofweek < 5]

    # Keep only NSE trading hours
    df = df.between_time("09:15", "15:30")

    return df


# ==============================
# FETCH & SAVE
# ==============================

def fetch_symbol_data(symbol):

    print(f"\nFetching {symbol}...")

    df = fetch_data(symbol, interval=INTERVAL)

    if df is None or len(df) == 0:
        print(f"❌ No data for {symbol}")
        return

    df = filter_market_hours(df)

    save_market_data(symbol, df)

    print(f"✅ Saved {symbol} | Rows: {len(df)}")


# ==============================
# MAIN
# ==============================

def main():

    print("\n==============================")
    print("HISTORICAL DATA LOADER STARTED")
    print("==============================\n")

    symbols = get_nse_symbols()

    for symbol in symbols:

        try:
            fetch_symbol_data(symbol)

            # avoid API overload
            time.sleep(0.5)

        except Exception as e:
            print(f"Error with {symbol}: {e}")

    print("\n✅ Historical data collection complete!")


if __name__ == "__main__":
    main()