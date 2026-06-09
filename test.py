import pandas as pd
from data_fetcher import fetch_data
from wyckoff_strategy import generate_signals
from backtester import run_backtest

df = fetch_data(symbol='BTC/USDT', timeframe='1h', limit=40000)

signals = generate_signals(df, lookback=50, reverse=True)

print("Optimizing Leverage to find best Balance to Drawdown ratio...")
for lev in [1.0, 1.2, 1.5, 1.8, 2.0]:
    for m_rr in [0.1, 0.12]:
        trades, bal = run_backtest(signals, initial_balance=1000, leverage=lev, min_rr=m_rr, compounding=True)
        if not trades: continue
        
        wins = len([t for t in trades if t['pnl'] > 0])
        wr = (wins/len(trades)*100)
        
        max_bal = 1000
        max_dd = 0
        for t in trades:
            if t['balance'] > max_bal: max_bal = t['balance']
            dd = (max_bal - t['balance']) / max_bal * 100
            if dd > max_dd: max_dd = dd
            
        print(f"Lev {lev}x | Min RR {m_rr} | Final Bal: ${bal:.2f} | Trades: {len(trades)} | WinRate: {wr:.2f}% | Max DD: {max_dd:.2f}%")
