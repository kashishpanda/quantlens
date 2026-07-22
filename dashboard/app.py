import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
except:
    DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

st.title("Quantitative Dashboard")
st.write("Institutional Quantitative Research Platform")

# Stock Selector
# Get tickers dynamically from database
with engine.connect() as conn:
    result = conn.execute(text("SELECT ticker FROM watched_stocks WHERE active = TRUE ORDER BY ticker"))
    tickers = [row[0] for row in result.fetchall()]
ticker = st.selectbox("Select a Stock", tickers)

# Fetch data from database
with engine.connect() as conn:
    result = conn.execute(
        text("select date, close from equity_prices where ticker = :ticker order by date asc"),
        {"ticker": ticker}
    )
    rows = result.fetchall()
df = pd.DataFrame(rows, columns = ["date", "close"])

#Price Chart
st.subheader(f"{ticker} - Closing Price")
st.line_chart(df.set_index("date")["close"])

# Calculate and show daily returns
df["daily_return"] = df["close"].pct_change() * 100

st.subheader(f"{ticker} - Daily Returns (%)")
st.line_chart(df.set_index("date")["daily_return"].dropna())

# Summary stats
st.subheader(f"{ticker} - Summary")
col1, col2, col3, col4, col5 = st.columns(5)

volatility = df["daily_return"].std()
sharpe = df["daily_return"].mean() / volatility
max_dd = ((1 + df["daily_return"]/100).cumprod() / (1 + df["daily_return"]/100).cumprod().cummax() - 1).min() * 100

col1.metric("Latest Close", f"${df['close'].iloc[-1]:.2f}")
col2.metric("Monthly Return", f"{((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
col3.metric("Volatility", f"{volatility:.2f}%")
col4.metric("Sharpe Ratio", f"{sharpe:.3f}")
col5.metric("Max Drawdown", f"{max_dd:.2f}%")

# Current Regime
st.subheader(f"{ticker} - Current Market Regime")

with engine.connect() as conn:
    regime_result = conn.execute(
        text("SELECT regime_label FROM stock_regimes WHERE ticker = :ticker ORDER BY date DESC LIMIT 1"),
        {"ticker": ticker}
    )
    regime_row = regime_result.fetchone()

if regime_row:
    regime = regime_row[0]
    if regime == "Trending Up":
        st.success(f"🟢 {regime}")
    elif regime == "Trending Down":
        st.error(f"🔴 {regime}")
    else:
        st.warning(f"🟡 {regime}")
else:
    st.info("No regime data available")


# Backtesting Results
st.subheader(f"{ticker} - Backtest Results")

with engine.connect() as conn:
    bt_data = pd.read_sql(
        text("SELECT e.date, e.close, s.regime_label FROM equity_prices e JOIN stock_regimes s ON e.date = s.date AND e.ticker = s.ticker WHERE e.ticker = :ticker ORDER BY e.date ASC"),
        conn,
        params={"ticker": ticker}
    )

if not bt_data.empty:
    # Run backtest
    capital = 1000
    position = 0
    portfolio_values = []

    for _, row in bt_data.iterrows():
        price = row["close"]
        regime = row["regime_label"]
        if regime == "Trending Up" and position == 0:
            position = capital / price
            capital = 0
        elif regime == "Trending Down" and position > 0:
            capital = position * price
            position = 0
        current_value = capital + (position * price)
        portfolio_values.append(current_value)

    bt_data["portfolio_value"] = portfolio_values
    final_value = portfolio_values[-1]
    strategy_return = ((final_value - 1000) / 1000) * 100
    buy_hold_return = ((bt_data["close"].iloc[-1] - bt_data["close"].iloc[0]) / bt_data["close"].iloc[0]) * 100

    col1, col2 = st.columns(2)
    col1.metric("Strategy Return", f"{strategy_return:.2f}%")
    col2.metric("Buy & Hold Return", f"{buy_hold_return:.2f}%")

    st.line_chart(bt_data.set_index("date")["portfolio_value"])