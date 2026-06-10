CREATE TABLE dim_symbol (
    symbol_id      SERIAL PRIMARY KEY,
    symbol         VARCHAR(20) NOT NULL,
    company_name   VARCHAR(100),
    sector         VARCHAR(50),
    exchange       VARCHAR(20),
    start_date     DATE NOT NULL,
    end_date       DATE,
    is_current     BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_date (
    date_id      SERIAL PRIMARY KEY,
    date         DATE UNIQUE NOT NULL,
    day_of_week  VARCHAR(10),
    month        INTEGER,  
    quarter      INTEGER,
    year         INTEGER,
    is_trading   BOOLEAN
);     

CREATE TABLE fact_market_data (
    fact_id     SERIAL PRIMARY KEY,
    symbol_id   INTEGER REFERENCES dim_symbol(symbol_id),
    date_id     INTEGER REFERENCES dim_date(date_id),
    open        NUMERIC(10,2),
    high        NUMERIC(10,2),
    low         NUMERIC(10,2),
    close       NUMERIC(10,2),
    volume      BIGINT
);