# trading_strategies/strategies/base_strategy.py
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseTradingStrategy(ABC):
    """基础交易策略抽象类"""
    
    def __init__(self, name, **params):
        self.name = name
        self.params = params
        self.signals = None
        self.positions = None
    
    @abstractmethod
    def calculate_indicators(self, df):
        """计算技术指标"""
        pass
    
    @abstractmethod
    def generate_signals(self, df):
        """生成交易信号"""
        pass
    
    def execute_strategy(self, df, initial_capital=100000):
        """执行交易策略"""
        df = df.copy()
        
        # 确保数据已排序
        if 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)
        
        # 生成信号
        self.signals = self.generate_signals(df)
        df['signal'] = self.signals
        
        # 初始化策略列
        df['action'] = 'HOLD'
        df['position'] = 0
        df['shares_held'] = 0
        df['entry_price'] = np.nan
        df['cash'] = initial_capital
        df['portfolio_value'] = initial_capital
        
        position = 0
        entry_price = 0
        shares_held = 0
        cash = initial_capital
        
        for i in range(len(df)):
            current_price = df.loc[i, 'close']
            current_date = df.loc[i, 'date']
            signal = df.loc[i, 'signal']
            
            # 买入信号且当前没有持仓
            if signal == 1 and position == 0:
                # 计算可买入的股票数量
                shares_to_buy = int(cash / current_price)
                if shares_to_buy > 0:
                    position = 1
                    shares_held = shares_to_buy
                    entry_price = current_price
                    cash -= shares_to_buy * current_price
                    df.loc[i, 'action'] = 'BUY'
                    df.loc[i, 'entry_price'] = entry_price
                    print(f"{current_date.date()}: 买入 {shares_to_buy}股 @ {current_price:.2f}")
            
            # 卖出信号且当前持有仓位
            elif signal == -1 and position == 1:
                if shares_held > 0:
                    cash += shares_held * current_price
                    profit = (current_price - entry_price) * shares_held
                    profit_pct = (current_price / entry_price - 1) * 100
                    df.loc[i, 'action'] = 'SELL'
                    position = 0
                    print(f"{current_date.date()}: 卖出 {shares_held}股 @ {current_price:.2f}, "
                      f"盈利: ${profit:.2f} ({profit_pct:.2f}%)")
                    shares_held = 0
                    
            
            # 更新持仓信息
            df.loc[i, 'position'] = position
            df.loc[i, 'shares_held'] = shares_held
            df.loc[i, 'cash'] = cash
            df.loc[i, 'portfolio_value'] = cash + (shares_held * current_price if position == 1 else 0)
        
        self.positions = df[['position', 'action', 'shares_held', 'entry_price']].copy()
        return df
    
    def get_daily_signal(self, df, check_date=None):
        """获取指定日期的信号"""
        if check_date is not None:
            df = df[df['date'] == check_date]
        
        if len(df) == 0:
            return None
        
        latest = df.iloc[-1]
        
        signal_info = {
            'strategy': self.name,
            'date': latest.get('date'),
            'close': latest.get('close'),
            'signal': latest.get('signal', 0),
            'action': latest.get('action', 'HOLD'),
            'indicators': self._get_indicators_info(latest)
        }
        
        return signal_info
    
    def _get_indicators_info(self, row):
        """获取指标信息（子类可重写）"""
        return {}