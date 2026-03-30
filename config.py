# ==============================
# MARKET SETTINGS
# ==============================

TIMEFRAME = "5minute"
LOOKBACK = 8000
SCAN_INTERVAL = 300

# ==============================
# MODEL SETTINGS
# ==============================

INTRADAY_MODEL_PATH = "models/intraday_model.pkl"
SWING_MODEL_PATH = "models/swing_model.pkl"

DATASET_PATH = "dataset/market_data.parquet"
LIVE_TRADE_PATH = "data/live_trades.csv"

# ==============================
# RISK MANAGEMENT
# ==============================

RISK_PER_TRADE = 0.01

TP_MULTIPLIER = 1.5
SL_MULTIPLIER = 0.7

# ==============================
# AI FILTERS
# ==============================

BUY_THRESHOLD = 0.53
SELL_THRESHOLD = 0.47