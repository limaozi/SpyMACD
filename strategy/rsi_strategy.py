# trading_strategies/strategies/rsi_strategy.py
import pandas as pd
import numpy as np
from .base_strategy import BaseTradingStrategy

class RSIStrategy(BaseTradingStrategy):
    """RSI交易策略"""
    
    def __init__(self, period=14, oversold=30, overbought=70):
        params = {
            'period': period,
            'oversold': oversold,
            'overbought': overbought
        }
        super().__init__('RSI Strategy', **params)
    
    def calculate_indicators(self, df):
        """计算RSI指标"""
        df = df.copy()
        
        period = self.params['period']
        
        # 计算价格变化
        delta = df['close'].diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均增益和平均损失
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 计算RS和RSI
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 添加平滑版本（可选）
        df['rsi_smoothed'] = df['rsi'].rolling(window=3).mean()
        
        return df
    
    def generate_signals(self, df):
        """生成RSI交易信号"""
        df = self.calculate_indicators(df)
        
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        # 初始化信号列
        signals = pd.Series(0, index=df.index)
        
        # 生成信号
        for i in range(1, len(df)):
            rsi = df.loc[i, 'rsi']
            prev_rsi = df.loc[i-1, 'rsi']
            
            # RSI从超卖区域上穿（买入信号）
            if prev_rsi < oversold and rsi > oversold:
                signals.iloc[i] = 1
            
            # RSI从超买区域下穿（卖出信号）
            elif prev_rsi > overbought and rsi < overbought:
                signals.iloc[i] = -1
            
            # 额外的确认信号：RSI在极端位置
            elif rsi < 20:  # 极度超卖
                signals.iloc[i] = 1
            elif rsi > 80:  # 极度超买
                signals.iloc[i] = -1
        
        return signals
    
    def _get_indicators_info(self, row):
        """获取RSI指标信息"""
        return {
            'rsi': row.get('rsi', 50),
            'rsi_smoothed': row.get('rsi_smoothed', 50),
            'status': self._get_rsi_status(row.get('rsi', 50))
        }
    
    def _get_rsi_status(self, rsi_value):
        """获取RSI状态描述"""
        if rsi_value < 30:
            return '极度超卖'
        elif rsi_value < 40:
            return '超卖'
        elif rsi_value > 70:
            return '极度超买'
        elif rsi_value > 60:
            return '超买'
        else:
            return '中性'