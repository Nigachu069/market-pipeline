# Market Data Pipeline

Automated ETL pipeline that fetches daily OHLCV market data for stocks and crypto, transforms it, and loads it into a star schema PostgreSQL database on AWS RDS — with CSV backups stored in S3.

## Architecture

```
yfinance API → extract() → transform() → load()
                                           ├── AWS RDS (star schema PostgreSQL)
                                           └── AWS S3 (CSV backup)

Orchestrated by Apache Airflow running in Docker
Scheduled: weekdays at 8am
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | Apache Airflow 2.9 |
| Infrastructure | AWS EC2, RDS, S3 |
| Database | PostgreSQL (star schema) |
| Language | Python 3 |
| Libraries | yfinance, psycopg2, pandas, boto3 |
| Containerisation | Docker, Docker Compose |

## Data Model — Star Schema

```
dim_symbol          dim_date
──────────          ────────
symbol_id PK        date_id PK
symbol              date
company_name        day_of_week
sector              month
exchange            quarter
start_date (SCD2)   year
end_date   (SCD2)   is_trading
is_current (SCD2)
      │                  │
      └──── fact_market_data ────┘
            ────────────────
            fact_id PK
            symbol_id FK
            date_id FK
            open / high / low / close
            volume
```

- `dim_symbol` implements **SCD Type 2** for tracking historical sector/company changes
- `dim_date` pre-calculates quarter, day of week for fast analytical queries

## Pipeline Flow

1. **Extract** — fetches 5 days of OHLCV data from yfinance for AMD, NVDA, BTC-USD
2. **Transform** — cleans column names, drops nulls, standardises timestamps
3. **Load** — inserts into RDS star schema + uploads CSV backup to S3

## Airflow DAG

- Schedule: `0 8 * * 1-5` (weekdays at 8am)
- Retries: 2 attempts with 5 minute delay
- Failure callback: logs task ID, DAG ID, and execution time

## How to Run

```bash
# clone the repo
git clone https://github.com/Nigachu069/market-pipeline.git
cd market-pipeline

# set environment variables
export DB_HOST=your_rds_endpoint
export DB_NAME=market_db
export DB_USER=postgres
export DB_PASSWORD=your_password
export S3_BUCKET=your_bucket_name
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# start Airflow + PostgreSQL
docker-compose up --build

# open Airflow UI
open http://localhost:8080
```

## Project Structure

```
market_pipeline/
├── dags/
│   └── market_dags.py      # Airflow DAG definition
├── pipeline/
│   ├── extract.py          # yfinance data fetch
│   ├── transform.py        # data cleaning
│   ├── load.py             # RDS insert + S3 upload
│   └── main.py             # pipeline entry point
├── sql/
│   └── init.sql            # star schema DDL
├── Dockerfile.airflow       # custom Airflow image
└── docker-compose.yml       # services definition
```
