import ccxt
import pandas as pd
import time
import os

def fetch_data(symbol='BTC/USDT', timeframe='1h', limit=5000):
    filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
    if os.path.exists(filename):
        print(f"Data found locally. Loading {filename}...")
        df = pd.read_csv(filename, parse_dates=['timestamp'])
        return df

    print(f"Fetching {limit} candles of {symbol} {timeframe} from Binance Futures...")
    exchange = ccxt.binance({'options': {'defaultType': 'future'}})
    
    all_ohlcv = []
    
    # Calculate starting timestamp
    tf_ms = exchange.parse_timeframe(timeframe) * 1000
    since = exchange.milliseconds() - (limit * tf_ms)
    
    current_limit = min(1500, limit)
    
    while len(all_ohlcv) < limit:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=current_limit)
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + tf_ms  # next candle
            print(f"Fetched {len(all_ohlcv)}/{limit} candles...")
            
            # We don't break if len(ohlcv) < current_limit because some exchanges 
            # hard-cap at 1000 even if we ask for 1500. 
            time.sleep(0.5)  # rate limit precaution
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
            
    # Cut down to exact limit if we over-fetched
    all_ohlcv = all_ohlcv[:limit]
            
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Drop duplicates just in case
    df.drop_duplicates(subset=['timestamp'], inplace=True)
    df.sort_values('timestamp', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} candles to {filename}")
    return df
