import pandas as pd

def transform(df ,symbol): 
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame.")
    if df.empty:
        raise ValueError("Input DataFrame is empty.")
    
    df = df.reset_index() 
    df.columns = df.columns.str.lower()  
    df['symbol'] = symbol
    df = df.rename(columns = {"date" : "candle_time"})
    df = df.drop(columns=['dividends', 'stock splits'], errors='ignore')
    df = df.dropna()

    return df