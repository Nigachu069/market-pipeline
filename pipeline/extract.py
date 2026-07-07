import psycopg2
import os
import requests as rq
from datetime import date, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

os.environ["ALPHA_VANTAGE_KEY"] = "YO5P6XFFU9YAJEE5"

@retry(
    stop = stop_after_attempt(4),
    wait = wait_exponential(multiplier=1, min=1, max=10),
    retry = retry_if_exception_type(ConnectionError)
)
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
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"DB connection failed: {e}") from e
    except Exception:
        return None

def validate_extract(df, symbol):
    if df.empty:
        raise ValueError(f"Empty DataFrame returned for '{symbol}'")

    required_columns = {"open", "high", "low", "close", "volume"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for '{symbol}': {missing}")
    
    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' is not numeric for '{symbol}'")
        
        if df[col].isnull().any():
            raise ValueError(f"Null value in {col} for '{symbol}'")
    
    if (df["volume"] < 0).any():
        raise ValueError(f"Volume must be above or equal to 0 for'{symbol}'")

    if (df["high"] < df["low"]).any():
        raise ValueError(f"day high is below day low for '{symbol}'")
    
    df_check = df.reset_index()
    if df_check.duplicated(subset=["Date"]).any():
        raise ValueError(f"Duplicated data for '{symbol}'")
    
    if df.index.max().date() < (date.today() - timedelta(days = 5)):
        print(f"Outdated data for '{symbol}' - latest date: {date.today() - timedelta(days = 5)}")
    
    return True

@retry(
    stop = stop_after_attempt(4),
    wait = wait_exponential(multiplier=1, min=1, max=10),
    retry = retry_if_exception_type(ConnectionError)
)
def extract(symbol):
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string.")
    try: 
        last_date = get_last_loaded_date()
        if last_date is None:
            period = 180
        else:
            days_since = (date.today() - last_date).days
            period = max(days_since , 2)

        response = rq.get(
            "https://www.alphavantage.co/query",
            params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": os.environ.get("ALPHA_VANTAGE_KEY")
            }
        )

        data = response.json()
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index")

        df.columns = [col.split(". ")[1] for col in df.columns]
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"
        df = df.astype(float)

        df = df.head(period)

        if df.empty:
            raise RuntimeError(f"Failed to extract data for {symbol}") 
        
        validate_extract(df, symbol)
        return df
    
    except ValueError as e:
        raise 

    except Exception as e:
        raise ConnectionError(f"Network error extracting {symbol}: {e}") from e