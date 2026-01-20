# trading_strategies/strategies/ma_strategy.py
import pandas as pd
import numpy as np
from .base_strategy import BaseTradingStrategy

class MAStrategy(BaseTradingStrategy):
    """移动平均线交叉策略"""
    
    def __init__(self, short_window=20, long_window=50):
        params = {
            'short_window': short_window,
            'long_window': long_window
        }
        super().__init__('Moving Average Strategy', **params)
    
    def calculate_indicators(self, df):
        """计算移动平均线"""
        df = df.copy()
        
        short_window = self.params['short_window']
        long_window = self.params['long_window']
        
        # 计算移动平均线
        df['ma_short'] = df['close'].rolling(window=short_window).mean()
        df['ma_long'] = df['close'].rolling(window=long_window).mean()
        
        # 计算价格与均线的距离
        df['price_to_short_ma'] = (df['close'] - df['ma_short']) / df['ma_short'] * 100
        df['price_to_long_ma'] = (df['close'] - df['ma_long']) / df['ma_long'] * 100
        
        return df
    
    def generate_signals(self, df):
        """生成移动平均线交易信号"""
        df = self.calculate_indicators(df)
        
        short_window = self.params['short_window']
        
        # 初始化信号列
        signals = pd.Series(0, index=df.index)
        
        # 生成信号（需要足够的数据）
        for i in range(short_window, len(df)):
            prev_short = df.loc[i-1, 'ma_short']
            prev_long = df.loc[i-1, 'ma_long']
            curr_short = df.loc[i, 'ma_short']
            curr_long = df.loc[i, 'ma_long']
            
            # 金叉：短期均线上穿长期均线（买入）
            if prev_short <= prev_long and curr_short > curr_long:
                signals.iloc[i] = 1
            
            # 死叉：短期均线下穿长期均线（卖出）
            elif prev_short >= prev_long and curr_short < curr_long:
                signals.iloc[i] = -1
        
        return signals
    
    def _get_indicators_info(self, row):
        """获取移动平均线指标信息"""
        return {
            'ma_short': row.get('ma_short', 0),
            'ma_long': row.get('ma_long', 0),
            'price_to_short_ma_pct': row.get('price_to_short_ma', 0),
            'price_to_long_ma_pct': row.get('price_to_long_ma', 0)
        }