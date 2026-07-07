ALTER TABLE fact_market_data
ADD COLUMN data_source VARCHAR(20) DEFAULT 'alpha_vantage';

ALTER TABLE fact_market_data
DROP COLUMN data_source;