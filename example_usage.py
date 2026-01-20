# 使用示例
import pandas as pd
from trading_strategies.main import (
    generate_signals, 
    execute_trading_strategy, 
    daily_check,
    compare_strategies
)
from trading_strategies.utils.data_loader import DataLoader

# 1. 加载数据
df = DataLoader.load_csv('stock_data.csv')

# 2. 使用特定策略生成信号
signals, strategy = generate_signals('rsi', df, {'period': 14, 'oversold': 30, 'overbought': 70})

# 3. 执行策略
result_df, strategy, performance, latest_signal = execute_trading_strategy(
    'macd', 
    df,
    strategy_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
    initial_capital=100000
)

# 4. 每日检查
signal_info = daily_check(df, 'rsi')

# 5. 比较多个策略
comparison_results = compare_strategies(df, ['macd', 'rsi', 'ma'])