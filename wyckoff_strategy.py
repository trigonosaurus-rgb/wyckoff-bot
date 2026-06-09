import pandas as pd

def generate_signals(df, lookback=50, reverse=False):
    """
    Applies pure Price Action Wyckoff logic (Spring / Upthrust).
    - lookback: Period to determine Trading Range (Support/Resistance)
    """
    df = df.copy()
    
    # Calculate Support and Resistance based on recent history (excluding current candle)
    df['TR_High'] = df['high'].rolling(window=lookback).max().shift(1)
    df['TR_Low'] = df['low'].rolling(window=lookback).min().shift(1)
    
    df['signal'] = 0  # 1 for LONG, -1 for SHORT
    df['entry_price'] = 0.0
    df['stop_loss'] = 0.0
    df['take_profit'] = 0.0
    df['pattern'] = ""
    
    for i in range(lookback, len(df)):
        current_low = df['low'].iloc[i]
        current_high = df['high'].iloc[i]
        current_close = df['close'].iloc[i]
        
        tr_low = df['TR_Low'].iloc[i]
        tr_high = df['TR_High'].iloc[i]
        
        if pd.isna(tr_low) or pd.isna(tr_high):
            continue
            
        # SPRING (Price swept support but closed above TR_Low)
        if current_low < tr_low and current_close > tr_low:
            if not reverse:
                df.loc[df.index[i], 'signal'] = 1
                df.loc[df.index[i], 'entry_price'] = current_close
                df.loc[df.index[i], 'stop_loss'] = current_low * 0.999 
                df.loc[df.index[i], 'take_profit'] = tr_high 
                df.loc[df.index[i], 'pattern'] = "Spring"
            else:
                # Reversed: We expect the price to continue dropping
                df.loc[df.index[i], 'signal'] = -1
                df.loc[df.index[i], 'entry_price'] = current_close
                df.loc[df.index[i], 'stop_loss'] = tr_high # Stop loss at the top of range
                df.loc[df.index[i], 'take_profit'] = current_low * 0.999 # Target the sweep low
                df.loc[df.index[i], 'pattern'] = "Rev_Spring"
            
        # UPTHRUST (Price swept resistance but closed below TR_High)
        elif current_high > tr_high and current_close < tr_high:
            if not reverse:
                df.loc[df.index[i], 'signal'] = -1
                df.loc[df.index[i], 'entry_price'] = current_close
                df.loc[df.index[i], 'stop_loss'] = current_high * 1.001 
                df.loc[df.index[i], 'take_profit'] = tr_low 
                df.loc[df.index[i], 'pattern'] = "Upthrust"
            else:
                # Reversed: We expect the price to continue pumping
                df.loc[df.index[i], 'signal'] = 1
                df.loc[df.index[i], 'entry_price'] = current_close
                df.loc[df.index[i], 'stop_loss'] = tr_low # Stop loss at bottom of range
                df.loc[df.index[i], 'take_profit'] = current_high * 1.001 # Target the sweep high
                df.loc[df.index[i], 'pattern'] = "Rev_Upthrust"
            
    return df
