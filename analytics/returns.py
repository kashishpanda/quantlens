import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Connect to database
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Load data from database
data = pd.read_sql("SELECT date, ticker, close from equity_prices order by date asc", engine)

# Calculate daily return
# Formula : (Today's Close - Yesterday's Close) / Yesterday's Close
# pct_change() - calculates percentage change from one row to next      
data["daily_return"] = data.groupby("ticker")["close"].pct_change()*100

# Cumulative return
# Formula: (1 + r1) × (1 + r2) × ... × (1 + rn) - 1
# cumprod() multiplies progressively across all rows
data["cumulative_return"] = data.groupby("ticker")["daily_return"].apply(lambda x: (1 + x/100).cumprod() - 1).reset_index(level=0, drop=True) * 100

# Volatility = standard deviation of daily returns
volatility = data.groupby("ticker")["daily_return"].std()
print("Volatility per stock:")
print(volatility.round(2))

print(data)

# Sharpe Ratio = Average Daily Return / Volatility
# Higher = better return per unit of risk
sharpe = data.groupby("ticker")["daily_return"].mean()/volatility
print("\nSharpe Ratio per stock:")
print(sharpe.round(3))

# Max Drawdown = biggest drop from peak to trough
# Shows worst case scenario for each stock
def max_drawdown(prices):
    cumulative = (1 + prices/100).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    return drawdown.min() * 100

max_dd = data.groupby("ticker")["daily_return"].apply(max_drawdown)
print("\nMax Drawdown per stock:")
print(max_dd.round(2))