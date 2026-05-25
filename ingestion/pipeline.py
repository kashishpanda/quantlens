import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

symbol = input("Enter stock symbol (e.g AAPL)")
period = "1mo"
ticker = yf.Ticker(symbol)
data = ticker.history(period = period)

data = data[[ "Open", "High", "Low", "Close", "Volume"]]
data = data.reset_index()
data.rename(columns = {"Date" : "date"}, inplace =True)
data["date"] = pd.to_datetime(data["date"]).dt.date
data["Volume"] = data["Volume"].astype(int)
data["Ticker"] = symbol
data.columns = data.columns.str.lower()


print(data)

# Insert data to database
data.to_sql( 
    "equity_prices",
    engine,
    if_exists = 'append',
    index = False
)

print('Data inserted successfully')
