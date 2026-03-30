import pandas as pd

DATASET_PATH = "dataset/market_data.parquet"

print("\n==============================")
print("DATASET DIAGNOSTIC")
print("==============================\n")

# Load dataset
df = pd.read_parquet(DATASET_PATH)

print("Total rows:", len(df))
print()

# ==============================
# TIME RANGE
# ==============================

print("Dataset start:", df.index.min())
print("Dataset end:", df.index.max())

duration = df.index.max() - df.index.min()

print("Total duration:", duration)
print()

# ==============================
# SYMBOL ANALYSIS
# ==============================

symbols = df["symbol"].unique()

print("Total symbols:", len(symbols))
print()

print("Symbols in dataset:")
print(symbols)
print()

# ==============================
# ROWS PER SYMBOL
# ==============================

print("Rows per symbol (top 20):\n")

rows_per_symbol = df.groupby("symbol").size().sort_values(ascending=False)

print(rows_per_symbol.head(20))
print()

# ==============================
# TIMEFRAME CHECK
# ==============================

print("Checking timeframe consistency...\n")

sample_symbol = symbols[0]

sample = df[df["symbol"] == sample_symbol]

time_diffs = sample.index.to_series().diff().value_counts()

print("Timeframe distribution:")
print(time_diffs.head())
print()

# ==============================
# MISSING DATA
# ==============================

print("Missing values:\n")

print(df.isnull().sum())
print()

# ==============================
# VOLUME CHECK
# ==============================

print("Zero volume rows:", (df["volume"] == 0).sum())
print()

# ==============================
# CRYPTO VS STOCKS
# ==============================

crypto = df[df["symbol"].str.contains("/")]
stocks = df[~df["symbol"].str.contains("/")]

print("Crypto rows:", len(crypto))
print("Stock rows:", len(stocks))
print()

# ==============================
# DATA SAMPLE
# ==============================

print("First rows:\n")
print(df.head())

print("\nLast rows:\n")
print(df.tail())

print("\n==============================")
print("DATASET TEST COMPLETE")
print("==============================\n")