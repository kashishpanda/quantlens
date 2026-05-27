import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

symbols = ["AAPL", "GOOGL", "MSFT", "NVDA", "JPM", "AMZN"]
period = "1mo"
for symbol in symbols:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period = period)
    data = data[[ "Open", "High", "Low", "Close", "Volume"]]
    data = data.reset_index()
    data.rename(columns = {"Date" : "date"}, inplace =True)
    data["date"] = pd.to_datetime(data["date"]).dt.date
    data["Volume"] = data["Volume"].astype(int)
    data["Ticker"] = symbol
    data.columns = data.columns.str.lower()
    data.to_sql(         # Insert data to database
        "equity_prices",
        engine,
        if_exists = 'append',
        index = False
    )

    print(f"{symbol} inserted successfully")
