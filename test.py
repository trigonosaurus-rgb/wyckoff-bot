import pandas as pd
from data_fetcher import fetch_data
from wyckoff_strategy import generate_signals

df = fetch_data(symbol='BTC/USDT', timeframe='1h', limit=40000)
signals = generate_signals(df, lookback=50, reverse=True)

for lev in [1, 2, 3]:
    balance = 1000
    position = None 
    for i in range(len(signals)):
        row = signals.iloc[i]
        
        if position is not None:
            exit_price = None
            if position['type'] == 1:
                if row['low'] <= position['sl']: exit_price = position['sl']
                elif row['high'] >= position['tp']: exit_price = position['tp']
            elif position['type'] == -1:
                if row['high'] >= position['sl']: exit_price = position['sl']
                elif row['low'] <= position['tp']: exit_price = position['tp']
                    
            if exit_price is not None:
                fee = 0.0004
                if position['type'] == 1:
                    pnl_percent = ((exit_price - position['entry']) / position['entry']) - (fee * 2)
                else:
                    pnl_percent = ((position['entry'] - exit_price) / position['entry']) - (fee * 2)
                    
                pnl = position['invested'] * pnl_percent * lev
                balance += pnl
                position = None
                
        if position is None:
            if row['signal'] != 0:
                entry = row['entry_price']
                sl = row['stop_loss']
                tp = row['take_profit']
                dist_sl = abs(entry - sl)
                dist_tp = abs(entry - tp)
                if dist_sl == 0: continue
                rr = dist_tp / dist_sl
                
                if rr >= 0.1:
                    position = {
                        'type': row['signal'],
                        'entry': entry,
                        'sl': sl,
                        'tp': tp,
                        'invested': balance
                    }
    print(f"Leverage {lev}x (Min RR 0.1): Final Bal = ${balance:.2f}")


