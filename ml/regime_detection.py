import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Load price data from database
data = pd.read_sql("SELECT date, ticker, close FROM equity_prices ORDER BY ticker, date ASC", engine)

# Calculate daily return per stock
data["daily_return"] = data.groupby("ticker")["close"].pct_change() * 100

# Calculate rolling volatility (5-day window)
data["volatility"] = data.groupby("ticker")["daily_return"].transform(lambda x: x.rolling(window=5).std())

#Drop rows with NaN values
data = data.dropna()

print(data.head(10))
print("Shape: ", data.shape)

# Train GMM seperately for each stock
results = []

for ticker in data["ticker"].unique():
    #Get data for this stock only
    stock_data = data[data["ticker"] == ticker].copy()            
    # Features for the model: daily return and volatility
    features = stock_data[["daily_return", "volatility"]].values  
    
    # Scale the features so both are on same scale
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features) 

    # Train GMM with 3 components (up, down, sideways)
    gmm = GaussianMixture(n_components = 3, random_state = 42)
    gmm.fit(features_scaled)    

    # Predict regime for each day
    stock_data["regime"]  = gmm.predict(features_scaled)

    results.append(stock_data)  

# Combine all stocks back together
final_data = pd.concat(results)
print(final_data[["date", "ticker", "daily_return", "regime"]].head(20))

# Map numeric labels to meaningful regime names
for ticker in final_data["ticker"].unique():
    stock = final_data[final_data["ticker"] == ticker]

    # Calculate average return per regime
    regime_means = stock.groupby("regime")["daily_return"].mean()

    # Sort by return: lowest=down, middle=sideways, highest=up
    sorted_regimes = regime_means.sort_values()
    regime_map = {
        sorted_regimes.index[0]: "Trending Down",
        sorted_regimes.index[1]: "Sideways",
        sorted_regimes.index[2]: "Trending Up",
    }

    final_data.loc[final_data["ticker"] == ticker, "regime_label"] = \
    final_data.loc[final_data["ticker"] == ticker, "regime"].map(regime_map)

print(final_data[["date", "ticker", "daily_return", "regime_label"]].head(20))

# Save regime labels to database
with engine.connect() as conn:
    for _, row in final_data.iterrows():
        conn.execute(text("""
            INSERT INTO stock_regimes (date, ticker, regime_label, daily_return, volatility)
            VALUES (:date, :ticker, :regime_label, :daily_return, :volatility)
            ON CONFLICT (date, ticker) DO NOTHING
        """), {
            "date": row["date"],
            "ticker": row["ticker"],
            "regime_label": row["regime_label"],
            "daily_return": row["daily_return"],
            "volatility": row["volatility"]
        })
    conn.commit()

print("Regime labels saved to database successfully")

