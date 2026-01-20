# trading_strategies/strategies/macd_strategy.py
import pandas as pd
import numpy as np
from .base_strategy import BaseTradingStrategy

class MACDStrategy(BaseTradingStrategy):
    """MACD交易策略"""
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period
        }
        super().__init__('MACD Strategy', **params)
    
    def calculate_indicators(self, df):
        """计算MACD指标"""
        df = df.copy()
        
        # 计算指数移动平均线
        fast_period = self.params['fast_period']
        slow_period = self.params['slow_period']
        signal_period = self.params['signal_period']
        
        df['ema_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线
        df['macd'] = df['ema_fast'] - df['ema_slow']
        
        # 计算信号线
        df['signal_line'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
        
        # 计算MACD柱状图
        df['histogram'] = df['macd'] - df['signal_line']
        
        return df
    
    def generate_signals(self, df):
        """生成MACD交易信号"""
        df = self.calculate_indicators(df)
        
        # 初始化信号列
        signals = pd.Series(0, index=df.index)
        
        # 计算MACD金叉和死叉
        for i in range(1, len(df)):
            prev_macd = df.loc[i-1, 'macd']
            prev_signal = df.loc[i-1, 'signal_line']
            curr_macd = df.loc[i, 'macd']
            curr_signal = df.loc[i, 'signal_line']
            
            # MACD金叉（买入信号）
            if prev_macd < prev_signal and curr_macd > curr_signal:
                signals.iloc[i] = 1
            
            # MACD死叉（卖出信号）
            elif prev_macd > prev_signal and curr_macd < curr_signal:
                signals.iloc[i] = -1
        
        return signals
    
    def _get_indicators_info(self, row):
        """获取MACD指标信息"""
        return {
            'macd': row.get('macd', 0),
            'signal_line': row.get('signal_line', 0),
            'histogram': row.get('histogram', 0),
            'ema_fast': row.get('ema_fast', 0),
            'ema_slow': row.get('ema_slow', 0)
        }
