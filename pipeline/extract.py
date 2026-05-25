import yfinance as yf

def extract(symbol, period = "5d"):
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string.")
    try: 
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            raise ValueError(f"No data found for symbol '{symbol}' with period '{period}'.")
        return df
    
    except Exception as e:
        raise ValueError(f"Error occurred while extracting data for symbol '{symbol}': {e}")