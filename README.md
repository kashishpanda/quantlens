# QuantLens

QuantLens is an institutional-style quantitative data engineering platform 
designed to simulate the data infrastructure used by professional finance teams. 
It automates the ingestion, storage, and analysis of equity market data, 
exposing results through a REST API and interactive dashboard.

## Current Capabilities
- Automated equity data ingestion from Yahoo Finance via yfinance
- Persistent storage in a normalized PostgreSQL database
- Quantitative analytics: daily returns, cumulative returns, and volatility
- RESTful API built with FastAPI to serve processed data
- Interactive Streamlit dashboard for visualization and stock comparison

## Tech Stack
COMPONENT -> TECHNOLOGY 

Data Ingestion -> Python, yfinance 
Database       -> PostgreSQL, SQLAlchemy 
Analytics      -> Pandas 
API            -> FastAPI, Uvicorn 
Dashboard      -> Streamlit 

## Getting Started

### Prerequisites
- Python 3.13+
- PostgreSQL 18+

### Installation

**1. Clone the repository**
git clone https://github.com/kashishpanda/quantlens.git
cd quantlens

**2. Create and activate virtual environment**
python -m venv venv
source venv/bin/activate

**3. Install dependencies**
pip install -r requirements.txt

**4. Configure environment variables**
Create a .env file in the project root:
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/quantlens

**5. Initialize the database**
psql -U postgres -c "CREATE DATABASE quantlens;"
psql -U postgres -d quantlens -c "CREATE TABLE equity_prices (
    date DATE NOT NULL,
    ticker TEXT NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    PRIMARY KEY (date, ticker)
);"

**6. Ingest data**
python ingestion/pipeline.py

**7. Start the API**
uvicorn api.main:app --reload

**8. Launch the dashboard**
streamlit run dashboard/app.py

## Project Structure
quantlens/
├── ingestion/       # Data fetching and loading pipeline
├── analytics/       # Quantitative computations
├── api/             # FastAPI REST endpoints
├── dashboard/       # Streamlit visualization app
├── db/              # Database schemas and migrations
└── tests/           # Test suite

## Roadmap
- Version 2: Multi-stock automation, scheduling, cloud deployment
- Version 3: Advanced analytics, alerting system
- Version 4: ML layer — regime detection and signal generation