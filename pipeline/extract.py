import psycopg2
import os
from datetime import date
import yfinance as yf

def get_last_loaded_date():
    """Check the most recent date already in the database."""
    try:
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"]
        )
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(date) FROM dim_date")
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return result   
    except Exception:
        return None     

def extract(symbol):
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string.")
    try: 
        last_date = get_last_loaded_date()
        if last_date is None:
            period = "3mo"
        else:
            days_since = (date.today() - last_date).days
            period = f"{max(days_since , 2)}d"

        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            raise RuntimeError(f"Failed to extract data for {symbol}: {e}") from e
        return df
    
    except Exception as e:
        raise ValueError(f"Error occurred while extracting data for symbol '{symbol}': {e}")