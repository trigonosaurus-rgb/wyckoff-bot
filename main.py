import pandas as pd
from data_fetcher import fetch_data
from wyckoff_strategy import generate_signals
from backtester import run_portfolio_backtest, print_report

def main():
    symbols = ['BTC/USDT', 'SOL/USDT']
    timeframe = '1h'
    limit = 40000   # Number of candles to fetch (40000 hours = ~4.5 years)
    
    print(f"--- Portfolio Wyckoff Price Action Backtester ---")
    
    dfs_signals = {}
    
    for symbol in symbols:
        print(f"\n1. Fetching historical data for {symbol}...")
        df = fetch_data(symbol=symbol, timeframe=timeframe, limit=limit)
        
        print(f"2. Applying Wyckoff Strategy (Inverted) for {symbol}...")
        df_signals = generate_signals(df, lookback=50, reverse=True)
        dfs_signals[symbol] = df_signals
    
    print("\n3. Running Portfolio simulation...")
    initial_balance = 1000.0
    trades, final_balance = run_portfolio_backtest(dfs_signals, initial_balance=initial_balance, leverage=1.8, min_rr=0.1)
    
    print("\n4. Generating Report...")
    print_report(trades, initial_balance, final_balance)

if __name__ == "__main__":
    # Pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    main()
