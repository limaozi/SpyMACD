import os

# 策略配置
STRATEGY_CONFIGS = {
    'macd': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    },
    'rsi': {
        'period': 14,
        'oversold': 30,
        'overbought': 70
    },
    'ma': {
        'short_window': 20,
        'long_window': 50
    }
}

# 交易配置
TRADING_CONFIG = {
    'initial_capital': 100000,
    'commission_rate': 0.001,  # 0.1% 手续费
    'slippage': 0.001,  # 0.1% 滑点
    'position_size': 1.0  # 仓位大小（1.0表示全仓）
}

# 文件路径
DATA_PATH = 'stock_data.csv'
RESULTS_PATH = 'results'

# 创建结果目录
os.makedirs(RESULTS_PATH, exist_ok=True)