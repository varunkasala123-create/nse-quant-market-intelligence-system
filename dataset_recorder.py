import os
import pandas as pd
import threading

DATASET_PATH = "dataset/market_data.parquet"

lock = threading.Lock()


def save_market_data(symbol, df):

    if df is None or len(df) == 0:
        return

    df = df.copy()

    # ensure timestamp index
    if not isinstance(df.index, pd.DatetimeIndex):
        return

    df["symbol"] = symbol

    # ensure dataset folder exists
    os.makedirs("dataset", exist_ok=True)

    with lock:

        if os.path.exists(DATASET_PATH):

            try:

                existing = pd.read_parquet(DATASET_PATH)

                # combine existing + new
                combined = pd.concat([existing, df])

            except Exception as e:

                print("Dataset read error:", e)

                combined = df

        else:

            combined = df

        # reset index to clean duplicates
        combined = combined.reset_index()

        # ensure timestamp column exists
        if "timestamp" not in combined.columns:
            combined.rename(columns={"index": "timestamp"}, inplace=True)

        # remove duplicate candles
        combined = combined.drop_duplicates(
            subset=["timestamp", "symbol"],
            keep="last"
        )

        # restore timestamp index
        combined = combined.set_index("timestamp")

        # sort dataset chronologically
        combined = combined.sort_index()

        # save dataset
        combined.to_parquet(DATASET_PATH)