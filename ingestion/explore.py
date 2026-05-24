import yfinance as yf

symbol = "AAPL"
period = "1mo"

ticker = yf.Ticker(symbol)
data = ticker.history(period= period)
data.index = data.index.date

data = data[["Open", "High", "Low", "Close", "Volume"]]

print(data)
print("---")
print(type(data))
print("---")
print(data.columns)

data.to_csv("ingestion/aapl_raw.csv", index_label="Date")