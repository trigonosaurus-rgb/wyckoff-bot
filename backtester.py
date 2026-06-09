import pandas as pd
from tabulate import tabulate

def run_portfolio_backtest(dfs, initial_balance=1000, leverage=1.8, min_rr=0.1):
    """
    Simulates trades across a portfolio of assets.
    Allocates (balance * leverage) / num_assets to each trade.
    """
    balance = initial_balance
    positions = []
    trades = []
    
    # Find common timeline
    all_timestamps = set()
    for sym, df in dfs.items():
        all_timestamps.update(df['timestamp'].tolist())
    
    sorted_timestamps = sorted(list(all_timestamps))
    
    # For fast lookup
    data = {}
    for sym, df in dfs.items():
        df_indexed = df.set_index('timestamp')
        data[sym] = df_indexed.to_dict('index')
        
    num_assets = len(dfs)
        
    for ts in sorted_timestamps:
        # 1. Manage existing positions
        active_positions = []
        for pos in positions:
            sym = pos['symbol']
            if ts not in data[sym]:
                active_positions.append(pos)
                continue
                
            row = data[sym][ts]
            
            exit_price = None
            exit_reason = ""
            
            if pos['type'] == 1: # LONG
                if row['low'] <= pos['sl']:
                    exit_price = pos['sl']
                    exit_reason = "SL"
                elif row['high'] >= pos['tp']:
                    exit_price = pos['tp']
                    exit_reason = "TP"
            elif pos['type'] == -1: # SHORT
                if row['high'] >= pos['sl']:
                    exit_price = pos['sl']
                    exit_reason = "SL"
                elif row['low'] <= pos['tp']:
                    exit_price = pos['tp']
                    exit_reason = "TP"
                    
            if exit_price is not None:
                fee = 0.0004
                if pos['type'] == 1:
                    pnl_percent = ((exit_price - pos['entry']) / pos['entry']) - (fee * 2)
                else:
                    pnl_percent = ((pos['entry'] - exit_price) / pos['entry']) - (fee * 2)
                    
                pnl = pos['invested'] * pnl_percent
                balance += pnl
                
                trades.append({
                    'entry_time': pos['time'],
                    'exit_time': ts,
                    'symbol': sym,
                    'type': 'LONG' if pos['type'] == 1 else 'SHORT',
                    'pattern': pos['pattern'],
                    'entry_price': pos['entry'],
                    'exit_price': exit_price,
                    'reason': exit_reason,
                    'pnl': round(pnl, 2),
                    'balance': round(balance, 2)
                })
            else:
                active_positions.append(pos)
                
        positions = active_positions
        if balance <= 0:
            break
            
        # 2. Check for new entries
        trade_capital = (balance * leverage) / num_assets
        
        for sym, df_dict in data.items():
            if ts not in df_dict: continue
            row = df_dict[ts]
            
            # Check if we already have an open position for this symbol
            has_pos = any(p['symbol'] == sym for p in positions)
            if has_pos: continue
                
            if row['signal'] != 0:
                entry = row['entry_price']
                sl = row['stop_loss']
                tp = row['take_profit']
                
                dist_sl = abs(entry - sl)
                dist_tp = abs(entry - tp)
                if dist_sl == 0: continue
                rr = dist_tp / dist_sl
                
                if rr >= min_rr:
                    positions.append({
                        'symbol': sym,
                        'type': row['signal'],
                        'entry': entry,
                        'sl': sl,
                        'tp': tp,
                        'time': ts,
                        'pattern': row['pattern'],
                        'invested': trade_capital
                    })
                    
    return trades, balance

def print_report(trades, initial_balance, final_balance):
    max_bal = max([initial_balance] + [t['balance'] for t in trades]) if trades else initial_balance
    
    print(f"\n{'='*40}")
    print(f"   PORTFOLIO WYCKOFF BACKTEST REPORT")
    print(f"{'='*40}")
    print(f"Initial Balance: ${initial_balance}")
    print(f"Peak Balance:    ${max_bal:.2f}")
    print(f"Final Balance:   ${final_balance:.2f}")
    
    net_profit = final_balance - initial_balance
    print(f"Net Profit:      ${net_profit:.2f} ({(net_profit/initial_balance)*100:.2f}%)")
    
    if len(trades) == 0:
        print("No trades executed.")
        return
        
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    win_rate = len(wins) / len(trades) * 100
    
    longs = [t for t in trades if t['type'] == 'LONG']
    long_wins = [t for t in longs if t['pnl'] > 0]
    long_win_rate = (len(long_wins) / len(longs) * 100) if len(longs) > 0 else 0
    
    shorts = [t for t in trades if t['type'] == 'SHORT']
    short_wins = [t for t in shorts if t['pnl'] > 0]
    short_win_rate = (len(short_wins) / len(shorts) * 100) if len(shorts) > 0 else 0
    
    avg_win = sum([t['pnl'] for t in wins]) / len(wins) if len(wins) > 0 else 0
    avg_loss = sum([abs(t['pnl']) for t in losses]) / len(losses) if len(losses) > 0 else 0
    rr_ratio = (avg_win / avg_loss) if avg_loss > 0 else 0

    max_balance = initial_balance
    max_dd_percent = 0.0
    max_dd_usd = 0.0
    current_streak = 0
    max_losing_streak = 0
    worst_trade_usd = 0.0
    
    for t in trades:
        if t['balance'] > max_balance:
            max_balance = t['balance']
        dd_usd = max_balance - t['balance']
        dd_percent = (dd_usd / max_balance) * 100 if max_balance > 0 else 0
        if dd_percent > max_dd_percent:
            max_dd_percent = dd_percent
            max_dd_usd = dd_usd
            
        if t['pnl'] <= 0:
            current_streak += 1
            if current_streak > max_losing_streak:
                max_losing_streak = current_streak
        else:
            current_streak = 0
            
        if t['pnl'] < worst_trade_usd:
            worst_trade_usd = t['pnl']

    print(f"Total Trades:    {len(trades)}")
    print(f"Wins:            {len(wins)}")
    print(f"Losses:          {len(losses)}")
    print(f"Win Rate:        {win_rate:.2f}%")
    print(f"Avg Win:         ${avg_win:.2f}")
    print(f"Avg Loss:        ${avg_loss:.2f}")
    print(f"Risk/Reward (RR): {rr_ratio:.2f}")
    print(f"Max Drawdown:    ${max_dd_usd:.2f} ({max_dd_percent:.2f}%)")
    print(f"Longest Loss Strk: {max_losing_streak}")
    print(f"Worst Trade:     ${worst_trade_usd:.2f}\n")
    
    # Stats per Symbol
    print("--- STATS PER SYMBOL ---")
    symbols = set([t['symbol'] for t in trades])
    for sym in symbols:
        sym_trades = [t for t in trades if t['symbol'] == sym]
        sym_wins = [t for t in sym_trades if t['pnl'] > 0]
        sym_wr = (len(sym_wins) / len(sym_trades)) * 100
        sym_pnl = sum([t['pnl'] for t in sym_trades])
        print(f"{sym}: {len(sym_trades)} trades | WinRate: {sym_wr:.2f}% | PnL: ${sym_pnl:.2f}")
    print("")
    
    print(f"--- YEARLY PNL ---")
    yearly_pnl = {}
    current_year = None
    
    for t in trades:
        year_str = t['exit_time'].strftime('%Y')
        if current_year != year_str:
            if current_year is not None:
                yearly_pnl[current_year]['end_bal'] = t['balance'] - t['pnl']
                
            current_year = year_str
            yearly_pnl[current_year] = {
                'start_bal': t['balance'] - t['pnl'],
                'pnl_usd': 0.0,
                'end_bal': t['balance']
            }
            
        yearly_pnl[current_year]['pnl_usd'] += t['pnl']
        yearly_pnl[current_year]['end_bal'] = t['balance']
        
    for y in sorted(yearly_pnl.keys()):
        start_b = yearly_pnl[y]['start_bal']
        pnl_usd = yearly_pnl[y]['pnl_usd']
        pct_growth = (pnl_usd / start_b * 100) if start_b > 0 else 0
        print(f"{y}: ${pnl_usd:,.2f} ({pct_growth:+.2f}%)")

    unique_months = set([t['exit_time'].strftime('%Y-%m') for t in trades])
    num_months = len(unique_months) if len(unique_months) > 0 else 1
    total_pct = (final_balance - initial_balance) / initial_balance * 100
    avg_monthly_pct = total_pct / num_months
    
    print(f"\nAvg Monthly Profit: {avg_monthly_pct:+.2f}% (over {num_months} active months)")


