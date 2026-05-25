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
data["daily_return"] = data["close"].pct_change()       
data["daily_return"] = data["daily_return"]*100

# Cumulative return
# Formula: (1 + r1) × (1 + r2) × ... × (1 + rn) - 1
# cumprod() multiplies progressively across all rows
data["cumulative_return"] = (1 + data["daily_return"] / 100).cumprod() -1
data["cumulative_return"] = data["cumulative_return"]*100

# Volatility = standard deviation of daily returns
volatility = data["daily_return"].std()
print(f"Volatility: {volatility:.2f}%")




print(data)
