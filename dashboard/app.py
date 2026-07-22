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