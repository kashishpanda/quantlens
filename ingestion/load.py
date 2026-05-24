import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# Read the CSV we already saved
data = pd.read_csv("ingestion/aapl_raw.csv")
data["Date"] = pd.to_datetime(data["Date"]).dt.date
data["Volume"] = data["Volume"].astype(int)
data["ticker"] = "AAPL"
data.columns = data.columns.str.lower()

# Preview it
print(data.head())
print(data.dtypes)

# Insert data into PostgreSQL
data.to_sql(
    "equity_prices",
    engine,
    if_exists="append",
    index=False
)

print("Data inserted successfully")