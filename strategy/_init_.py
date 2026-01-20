# trading_strategies/strategies/__init__.py
from .macd_strategy import MACDStrategy
from .rsi_strategy import RSIStrategy
from .ma_strategy import MAStrategy

class StrategyFactory:
    """策略工厂类"""
    
    @staticmethod
    def create_strategy(strategy_name, **params):
        """创建策略实例"""
        strategy_name = strategy_name.lower()
        
        if strategy_name in ['macd', 'macd_strategy']:
            return MACDStrategy(**params)
        elif strategy_name in ['rsi', 'rsi_strategy']:
            return RSIStrategy(**params)
        elif strategy_name in ['ma', 'moving_average', 'ma_strategy']:
            return MAStrategy(**params)
        else:
            raise ValueError(f"未知策略: {strategy_name}")
    
    @staticmethod
    def get_available_strategies():
        """获取可用策略列表"""
        return {
            'macd': {
                'name': 'MACD Strategy',
                'description': '移动平均收敛发散指标策略',
                'params': {
                    'fast_period': 12,
                    'slow_period': 26,
                    'signal_period': 9
                }
            },
            'rsi': {
                'name': 'RSI Strategy',
                'description': '相对强弱指标策略',
                'params': {
                    'period': 14,
                    'oversold': 30,
                    'overbought': 70
                }
            },
            'ma': {
                'name': 'Moving Average Strategy',
                'description': '移动平均线交叉策略',
                'params': {
                    'short_window': 20,
                    'long_window': 50
                }
            }
        }