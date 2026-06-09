import pandas as pd
from data_fetcher import fetch_data
from wyckoff_strategy import generate_signals
from backtester import run_backtest, print_report

def main():
    symbol = 'BTC/USDT'
    timeframe = '1h'
    limit = 40000  # Number of candles to fetch (40000 hours = ~4.5 years)
    
    print(f"--- Wyckoff Price Action Backtester ---")
    
    print("\n1. Fetching historical data...")
    df = fetch_data(symbol=symbol, timeframe=timeframe, limit=limit)
    
    print("\n2. Applying Wyckoff Strategy (Finding Springs & Upthrusts)...")
    # lookback of 50 candles to determine the Trading Range Support & Resistance
    df_signals = generate_signals(df, lookback=50)
    
    print("3. Running simulation...")
    initial_balance = 1000.0
    trades, final_balance = run_backtest(df_signals, initial_balance=initial_balance)
    
    print("\n4. Generating Report...")
    print_report(trades, initial_balance, final_balance)

if __name__ == "__main__":
    # Pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    main()
