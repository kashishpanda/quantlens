from fastapi import FastAPI
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.get("/")
def home():
    return {"message": "QuantLens API is running"}

@app.get("/prices/{ticker}")
def get_Prices(ticker: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM equity_prices WHERE ticker = :ticker ORDER BY date ASC"),
            {"ticker": ticker.upper()}
        )
        rows = result.fetchall()
        return {"ticker": ticker.upper(), "data": [dict(row._mapping) for row in rows]}
    
@app.get("/returns")
def get_returns():
    with engine.connect() as conn:
        result = conn.execute(
            text("select ticker, date, close from equity_prices order by ticker, date asc")
        )   
        rows = result.fetchall()
    
    # Convert to Dataframe for Calculation
    import pandas as pd
    df = pd.DataFrame(rows, columns=["ticker", "date", "close"])
    df["daily_return"] = df.groupby("ticker")["close"].pct_change()*100
    return {"data": df.dropna().to_dict(orient="records")}