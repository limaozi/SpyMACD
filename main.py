# trading_strategies/main.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 导入自定义模块
from strategy import StrategyFactory
from utils.data_loader import DataLoader
from utils.performance_analyzer import PerformanceAnalyzer
import config

def generate_signals(strategy_name, df, strategy_params=None):
    """
    生成交易信号（重构的通用函数）
    
    Args:
        strategy_name: 策略名称 ('macd', 'rsi', 'ma')
        df: 股票数据DataFrame
        strategy_params: 策略参数字典
    
    Returns:
        signals: 交易信号Series
        strategy: 策略实例
    """
    # 使用策略工厂创建策略
    if strategy_params is None:
        strategy_params = config.STRATEGY_CONFIGS.get(strategy_name, {})
    
    strategy = StrategyFactory.create_strategy(strategy_name, **strategy_params)
    
    # 生成信号
    signals = strategy.generate_signals(df)
    
    return signals, strategy

def execute_trading_strategy(strategy_name, df, strategy_params=None, 
                            initial_capital=None, **trading_params):
    """
    执行交易策略（重构的通用函数）
    
    Args:
        strategy_name: 策略名称
        df: 股票数据DataFrame
        strategy_params: 策略参数
        initial_capital: 初始资金
        **trading_params: 其他交易参数
    
    Returns:
        result_df: 包含交易结果的DataFrame
        strategy: 策略实例
        performance: 性能指标
    """
    # 设置默认值
    if initial_capital is None:
        initial_capital = config.TRADING_CONFIG['initial_capital']
    
    if strategy_params is None:
        strategy_params = config.STRATEGY_CONFIGS.get(strategy_name, {})
    
    # 合并交易参数
    trading_config = {**config.TRADING_CONFIG, **trading_params}
    
    # 创建并执行策略
    strategy = StrategyFactory.create_strategy(strategy_name, **strategy_params)
    result_df = strategy.execute_strategy(df, initial_capital=initial_capital)
    
    # 分析性能
    performance = PerformanceAnalyzer.analyze_performance(result_df, initial_capital)
    
    # 获取最新信号
    latest_signal = strategy.get_daily_signal(result_df)
    
    return result_df, strategy, performance, latest_signal

def compare_strategies(df, strategies=['macd', 'rsi', 'ma'], 
                      initial_capital=100000):
    """
    比较多个策略
    
    Args:
        df: 股票数据
        strategies: 策略列表
        initial_capital: 初始资金
    
    Returns:
        comparison_results: 策略比较结果
    """
    results = {}
    
    for strategy_name in strategies:
        print(f"\n执行 {strategy_name.upper()} 策略...")
        
        try:
            result_df, strategy, performance, latest_signal = execute_trading_strategy(
                strategy_name, df, initial_capital=initial_capital
            )
            
            results[strategy_name] = {
                'dataframe': result_df,
                'strategy': strategy,
                'performance': performance,
                'latest_signal': latest_signal
            }
            
            # 打印报告
            report = PerformanceAnalyzer.generate_report(
                strategy.name, performance, latest_signal
            )
            print(report)
            
            # 保存结果
            result_df.to_csv(f"results/{strategy_name}_results.csv", index=False)
            
        except Exception as e:
            print(f"执行策略 {strategy_name} 时出错: {e}")
    
    return results

def visualize_comparison(results):
    """可视化策略比较结果"""
    if not results:
        print("没有可可视化的结果")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 子图1：策略组合价值对比
    ax1 = axes[0, 0]
    for strategy_name, result in results.items():
        df = result['dataframe']
        ax1.plot(df['date'], df['portfolio_value'], 
                label=f"{strategy_name.upper()}", linewidth=2)
    
    ax1.set_title('策略组合价值对比')
    ax1.set_ylabel('组合价值 ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 子图2：买入持有对比
    ax2 = axes[0, 1]
    for strategy_name, result in results.items():
        df = result['dataframe']
        if 'close' in df.columns:
            buy_hold = df['close'] / df['close'].iloc[0] * config.TRADING_CONFIG['initial_capital']
            ax2.plot(df['date'], buy_hold, '--', label=f"{strategy_name} - 买入持有", alpha=0.7)
            ax2.plot(df['date'], df['portfolio_value'], '-', label=f"{strategy_name} - 策略", linewidth=2)
    
    ax2.set_title('策略 vs 买入持有')
    ax2.set_ylabel('价值 ($)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 子图3：每日收益率分布
    ax3 = axes[1, 0]
    all_returns = []
    labels = []
    for strategy_name, result in results.items():
        df = result['dataframe']
        if 'portfolio_value' in df.columns:
            returns = df['portfolio_value'].pct_change().dropna()
            all_returns.append(returns)
            labels.append(strategy_name.upper())
    
    if all_returns:
        ax3.boxplot(all_returns, labels=labels)
        ax3.set_title('每日收益率分布')
        ax3.set_ylabel('收益率')
        ax3.grid(True, alpha=0.3)
    
    # 子图4：累计收益
    ax4 = axes[1, 1]
    for strategy_name, result in results.items():
        df = result['dataframe']
        if 'portfolio_value' in df.columns:
            cumulative_returns = (df['portfolio_value'] / df['portfolio_value'].iloc[0] - 1) * 100
            ax4.plot(df['date'], cumulative_returns, label=strategy_name.upper(), linewidth=2)
    
    ax4.set_title('累计收益率对比')
    ax4.set_ylabel('累计收益率 (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/strategy_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def daily_check(df, strategy_name='macd'):
    """每日检查交易信号"""
    print(f"\n{'='*60}")
    print(f"每日交易信号检查 - {datetime.now().date()}")
    print(f"策略: {strategy_name.upper()}")
    print(f"{'='*60}")
    
    # 执行策略
    result_df, strategy, performance, latest_signal = execute_trading_strategy(
        strategy_name, df
    )
    
    if latest_signal:
        print(f"\n📅 日期: {latest_signal['date']}")
        print(f"💰 收盘价: ${latest_signal['close']:.2f}")
        print(f"📊 策略: {latest_signal['strategy']}")
        print(f"🚦 信号: {latest_signal['signal']}")
        print(f"🎯 操作: {latest_signal['action']}")
        
        if latest_signal['signal'] == 1:
            print(f"\n✅ **买入信号**")
            print("   建议: 考虑建立多头仓位")
        elif latest_signal['signal'] == -1:
            print(f"\n❌ **卖出信号**")
            print("   建议: 考虑平仓")
        else:
            print(f"\n🔄 **无信号**")
            print("   建议: 持有或观望")
        
        # 显示技术指标
        if 'indicators' in latest_signal:
            print(f"\n💡 技术指标:")
            for key, value in latest_signal['indicators'].items():
                print(f"   {key:20}: {value}")
    
    return latest_signal

def main():
    """主函数"""
    print("=" * 60)
    print("模块化交易策略系统")
    print("=" * 60)
    
    # 1. 加载数据
    print("\n1. 加载数据...")
    df = DataLoader.load_csv(config.DATA_PATH)
    df = DataLoader.prepare_data(df)
    print(f"   数据范围: {df['date'].min().date()} 到 {df['date'].max().date()}")
    print(f"   数据行数: {len(df)}")
    
    # 2. 显示可用策略
    print("\n2. 可用策略:")
    available_strategies = StrategyFactory.get_available_strategies()
    for key, info in available_strategies.items():
        print(f"   - {key}: {info['name']}")
        print(f"     描述: {info['description']}")
    
    # 3. 执行单个策略
    print("\n3. 执行MACD策略...")
    macd_results = execute_trading_strategy('macd', df)
    
    # 4. 比较多个策略
    print("\n4. 比较多个策略...")
    strategies_to_compare = ['macd', 'rsi', 'ma']
    comparison_results = compare_strategies(df, strategies_to_compare)
    
    # 5. 可视化比较结果
    print("\n5. 生成可视化图表...")
    visualize_comparison(comparison_results)
    
    # 6. 每日检查
    print("\n6. 每日信号检查...")
    latest_signal = daily_check(df, 'macd')
    
    # 7. 保存总结报告
    print("\n7. 生成总结报告...")
    with open('results/summary_report.txt', 'w') as f:
        f.write("交易策略总结报告\n")
        f.write("=" * 50 + "\n\n")
        
        for strategy_name, result in comparison_results.items():
            f.write(f"策略: {strategy_name.upper()}\n")
            f.write("-" * 30 + "\n")
            
            performance = result['performance']
            for key, value in performance.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n")
    
    print(f"\n✅ 所有结果已保存到 'results/' 目录")
    print("✅ 总结报告: results/summary_report.txt")
    print("✅ 策略对比图: results/strategy_comparison.png")

if __name__ == "__main__":
    main()