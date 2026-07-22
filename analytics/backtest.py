import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Load price data and regime labels together
query = """
    SELECT e.date, e.ticker, e.close, s.regime_label
    FROM equity_prices e
    JOIN stock_regimes s ON e.date = s.date AND e.ticker = s.ticker
    ORDER BY e.ticker, e.date ASC
"""

data = pd.read_sql(query, engine)
print(data.head(10))
print("Shape:", data.shape)

def backtest(stock_data, initial_capital = 1000):
    capital = initial_capital
    position = 0 #how many shares we hold
    portfolio_values = []

    for _, row in stock_data.iterrows():
        price = row["close"]
        regime = row["regime_label"]

        #Buy signal
        if regime == "Trending Up" and position == 0:
            position = capital / price  # buy as many shares as we can
            capital = 0
    
        # Sell signal
        elif regime == "Trending Down" and position > 0:
            capital = position * price  # sell all shares
            position = 0
        
        # Calculate current portfolio value
        current_value = capital + (position * price)
        portfolio_values.append(current_value)
    
    return portfolio_values

# Run backtest for each stock
for ticker in data["ticker"].unique():
    stock_data = data[data["ticker"] == ticker].copy().reset_index(drop=True)
    
    portfolio_values = backtest(stock_data)
    stock_data["portfolio_value"] = portfolio_values
    
    # Calculate returns
    final_value = portfolio_values[-1]
    strategy_return = ((final_value - 1000) / 1000) * 100
    buy_hold_return = ((stock_data["close"].iloc[-1] - stock_data["close"].iloc[0]) / stock_data["close"].iloc[0]) * 100
    
    print(f"\n{ticker}:")
    print(f"  Strategy Return:   {strategy_return:.2f}%")
    print(f"  Buy & Hold Return: {buy_hold_return:.2f}%")
    print(f"  Outperformed: {strategy_return > buy_hold_return}")

    