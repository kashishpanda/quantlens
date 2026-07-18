import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(
     filename = "logs/pipeline.log",
     level = logging.INFO,
     format = "%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT ticker FROM watched_stocks WHERE active = TRUE"))
    symbols = [row[0] for row in result.fetchall()]

logging.info(f"Fetching data for: {symbols}")
period = "1mo"
for symbol in symbols:
    try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period = period)
            if data.empty:
                logging.warning(f"No data found for {symbol}, skipping")
                continue
            data = data[[ "Open", "High", "Low", "Close", "Volume"]]
            data = data.reset_index()
            data.rename(columns = {"Date" : "date"}, inplace =True)
            data["date"] = pd.to_datetime(data["date"]).dt.date
            data["Volume"] = data["Volume"].astype(int)
            data["Ticker"] = symbol
            data.columns = data.columns.str.lower()
            with engine.connect() as conn:
                for _, row in data.iterrows():
                    conn.execute(text("""
                        INSERT INTO equity_prices (date, open, high, low, close, volume, ticker)
                        VALUES (:date, :open, :high, :low, :close, :volume, :ticker)
                        ON CONFLICT (date, ticker) DO NOTHING
                    """), {
                        "date": row["date"],
                        "open": row["open"],
                        "high": row["high"],
                        "low": row["low"],
                        "close": row["close"],
                        "volume": row["volume"],
                        "ticker": row["ticker"]
                    })
                conn.commit()  
            logging.info(f"{symbol} inserted successfully")
    except Exception as e:
        logging.error(f"{symbol} failed: {e}")                
    
    
