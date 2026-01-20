from strategy import StrategyFactory

# 创建策略
strategy = StrategyFactory.create_strategy('rsi', period=14, oversold=30, overbought=70)

# 生成信号
signals = strategy.generate_signals(df)

# 执行策略
result_df = strategy.execute_strategy(df, initial_capital=100000)