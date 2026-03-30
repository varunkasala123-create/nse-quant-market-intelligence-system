🧠 Repository Description (README Intro)

A market-specific extension of a quantitative trading intelligence system tailored for the Indian stock market (NSE), integrating Zerodha (Kite Connect) data APIs with machine learning-driven signal generation, real-time scanning, and structured trade evaluation.

The system incorporates NSE market constraints, localized asset universes, and adaptive filtering logic to generate high-confidence intraday and swing trade insights.

🚀 Key Features
🇮🇳 NSE-Specific Market Integration
Native support for Indian equities (NSE symbols)
Zerodha Kite Connect API integration for historical data
→ see:
🕒 Market-Aware Execution
Filters trades based on NSE trading hours (09:15–15:30 IST)
→ see:
Avoids non-trading days (weekends)
📊 Historical Data Pipeline
Automated data collection across multiple NSE symbols
Cleans and filters:
Trading hours only
Weekday-only data
→ see:
🧠 Machine Learning Engine (Improved)
LightGBM classifier with:
Adjusted labeling threshold (ATR-based)
Enhanced feature space
Time-series aware validation
→ see:
📈 Advanced Trade Filtering Logic

Beyond basic ML signals, includes:

RSI-based overbought/oversold filtering
Trend strength validation
Volume participation filtering
Soft regime filtering (not hard rejection)

→ see:

⚠️ Risk Management
Position sizing based on:
Stop-loss distance
Capital constraints
→ see:
📊 Backtesting Engine
Walk-forward simulation
Includes:
Slippage
Commission
Drawdown tracking
Sharpe ratio
→ see:
🖥️ NSE Dashboard
Dedicated Streamlit dashboard for:
Intraday trades
Swing trades
Trade logs
→ see:
🔁 Continuous Market Scanner
Real-time scanning of NSE stocks
Separate intraday and swing strategies
Confidence-ranked outputs
⚙️ Tech Stack
Python
LightGBM
Pandas / NumPy
Zerodha Kite Connect API
Streamlit
Parquet (data storage)
