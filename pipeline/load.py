import psycopg2  
import os

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
                INSERT INTO market_data (candle_time, open, high, low, close, volume, symbol)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """ 
        
        for _, row in df.iterrows():
            value = (row['candle_time'], row['open'], row['high'], row['low'], row['close'], row['volume'], row['symbol'])
            cursor.execute(sql, value)
        
        print(f"Loaded {len(df)} rows for {df['symbol'].iloc[0]}")

        conn.commit()

    except Exception as e:
        print(f"Error loading data: {e}")
    
    finally:
        cursor.close()
        conn.close()