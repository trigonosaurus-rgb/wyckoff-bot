import pandas as pd
from data_fetcher import fetch_data
from wyckoff_strategy import generate_signals
from backtester import run_backtest

df = fetch_data(symbol='BTC/USDT', timeframe='1h', limit=40000)

signals = generate_signals(df, lookback=50, reverse=True)

print("Optimizing Leverage precisely...")
best_bal = 0
best_lev = 0

for lev in [2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]:
    trades, bal = run_backtest(signals, initial_balance=1000, leverage=lev, min_rr=0.12, compounding=True)
    if not trades: continue
    if bal > best_bal:
        best_bal = bal
        best_lev = lev
        
    print(f"Lev {lev}: Final Bal = ${bal:.2f}")
    
print(f"BEST: {best_lev} -> ${best_bal:.2f}")
