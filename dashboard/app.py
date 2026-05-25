import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

st.title("Quantitative Dashboard")
st.write("Institutional Quantitative Research Platform")

# Stock Selector
ticker = st.selectbox("Select a Stock", ["AAPL", "GOOGL", "MSFT"])

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
col1, col2, col3 = st.columns(3)

col1.metric("Latest Close", f"${df['close'].iloc[-1]:.2f}")
col2.metric("Monthly Return", f"{((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
col3.metric("Volatility", f"{df['daily_return'].std():.2f}%")