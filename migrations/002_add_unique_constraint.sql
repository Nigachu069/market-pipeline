ALTER TABLE fact_market_data
ADD CONSTRAINT unique_symbol_date
UNIQUE (symbol_id, date_id);

ALTER TABLE fact_market_data
DROP CONSTRAINT unique_symbol_date;