import psycopg2
import os
import boto3
from datetime import date
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop = stop_after_attempt(4),
    wait = wait_exponential(multiplier=1, min=1, max=10),
    retry = retry_if_exception_type(ConnectionError)
)
def get_or_create_symbol(cursor, symbol):
    cursor.execute("""
        SELECT symbol_id FROM dim_symbol 
        WHERE symbol = %s AND is_current = TRUE
    """, (symbol,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        cursor.execute("""
            INSERT INTO dim_symbol (symbol, start_date, is_current)
            VALUES (%s, %s, TRUE)
            RETURNING symbol_id
        """, (symbol, date.today()))
        return cursor.fetchone()[0]

def get_or_create_date(cursor, candle_time):
    candle_date = candle_time.date()
    
    cursor.execute("""
        SELECT date_id FROM dim_date WHERE date = %s
    """, (candle_date,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute("""
            INSERT INTO dim_date (date, day_of_week, month, quarter, year, is_trading)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING date_id
        """, (
            candle_date,
            candle_time.strftime('%A'),      
            candle_time.month,
            (candle_time.month - 1) // 3 + 1, 
            candle_time.year,
            True
        ))
        return cursor.fetchone()[0]

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(ConnectionError)
)
def load(df):
    host = os.environ["DB_HOST"]
    name = os.environ["DB_NAME"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]

    try:
        conn = psycopg2.connect(
            host=host,
            database=name,
            user=user,
            password=password
        )
        cursor = conn.cursor()

        sql = """
                INSERT INTO fact_market_data
                (symbol_id, date_id, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol_id, date_id)
                DO UPDATE SET
            open   = EXCLUDED.open,
            high   = EXCLUDED.high,
            low    = EXCLUDED.low,
            close  = EXCLUDED.close,
            volume = EXCLUDED.volume
            """
        
        for _, row in df.iterrows():
            symbol_id = get_or_create_symbol(cursor, row['symbol'])
            date_id = get_or_create_date(cursor, row['candle_time'])
            value = (symbol_id, date_id, row['open'], row['high'], row['low'], row['close'], row['volume'])

            cursor.execute(sql, value)
        
        print(f"Loaded {len(df)} rows for {df['symbol'].iloc[0]}")

        conn.commit()

        s3 = boto3.client('s3')
        symbol = df['symbol'].iloc[0]
        filename = f"/tmp/{symbol}.csv"
        df.to_csv(filename, index=False)
        s3.upload_file(filename, os.environ['S3_BUCKET'], f"clean/{symbol}.csv")
        print(f"Saved {symbol}.csv to S3")

    except Exception as e:
        print(f"Error loading data: {e}")
    
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"DB connection failed: {e}") from e

    except psycopg2.IntegrityError as e:
        raise ValueError(f"Data integrity volation: {e}") from e
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()