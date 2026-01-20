# trading_strategies/utils/performance_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime

class PerformanceAnalyzer:
    """性能分析器"""
    
    @staticmethod
    def analyze_performance(df, initial_capital=100000):
        """分析策略性能"""
        
        # 计算基准收益（买入并持有）
        if 'close' in df.columns:
            initial_price = df.iloc[0]['close']
            final_price = df.iloc[-1]['close']
            buy_hold_return = (final_price / initial_price - 1) * 100
        
        # 计算策略收益
        if 'portfolio_value' in df.columns:
            initial_portfolio = df.iloc[0]['portfolio_value']
            final_portfolio = df.iloc[-1]['portfolio_value']
            strategy_return = (final_portfolio / initial_portfolio - 1) * 100
        
        # 计算最大回撤
        if 'portfolio_value' in df.columns:
            df['cummax'] = df['portfolio_value'].cummax()
            df['drawdown'] = (df['portfolio_value'] - df['cummax']) / df['cummax'] * 100
            max_drawdown = df['drawdown'].min()
        
        # 统计交易信息
        buy_signals = len(df[df['action'] == 'BUY'])
        sell_signals = len(df[df['action'] == 'SELL'])
        total_trades = buy_signals + sell_signals
        
        # 计算胜率
        trades = []
        entry_price = None
        for i in range(len(df)):
            if df.iloc[i]['action'] == 'BUY':
                entry_price = df.iloc[i]['close']
            elif df.iloc[i]['action'] == 'SELL' and entry_price is not None:
                exit_price = df.iloc[i]['close']
                profit_pct = (exit_price / entry_price - 1) * 100
                trades.append({
                    'profit_pct': profit_pct,
                    'win': profit_pct > 0
                })
                entry_price = None
        
        winning_trades = len([t for t in trades if t['win']])
        win_rate = (winning_trades / len(trades) * 100) if trades else 0
        
        # 平均盈利/亏损
        if trades:
            avg_profit = np.mean([t['profit_pct'] for t in trades])
            avg_win = np.mean([t['profit_pct'] for t in trades if t['win']]) if winning_trades > 0 else 0
            avg_loss = np.mean([t['profit_pct'] for t in trades if not t['win']]) if len(trades) - winning_trades > 0 else 0
        else:
            avg_profit = avg_win = avg_loss = 0
        
        # 计算夏普比率（简化版）
        if 'portfolio_value' in df.columns:
            df['daily_returns'] = df['portfolio_value'].pct_change()
            sharpe_ratio = df['daily_returns'].mean() / df['daily_returns'].std() * np.sqrt(252) if df['daily_returns'].std() > 0 else 0
        
        return {
            '初始投资': f"${initial_capital:,.2f}",
            '最终价值': f"{final_portfolio:,.2f}" if 'final_portfolio' in locals() else "N/A",
            '策略总收益': f"{strategy_return:.2f}%" if 'strategy_return' in locals() else "N/A",
            '买入持有收益': f"{buy_hold_return:.2f}%" if 'buy_hold_return' in locals() else "N/A",
            '超额收益': f"{strategy_return - buy_hold_return:.2f}%" if all(k in locals() for k in ['strategy_return', 'buy_hold_return']) else "N/A",
            '最大回撤': f"{max_drawdown:.2f}%" if 'max_drawdown' in locals() else "N/A",
            '夏普比率': f"{sharpe_ratio:.2f}" if 'sharpe_ratio' in locals() else "N/A",
            '总交易次数': total_trades,
            '买入信号': buy_signals,
            '卖出信号': sell_signals,
            '胜率': f"{win_rate:.1f}%",
            '平均每笔收益': f"{avg_profit:.2f}%",
            '平均盈利': f"{avg_win:.2f}%",
            '平均亏损': f"{avg_loss:.2f}%"
        }
    
    @staticmethod
    def generate_report(strategy_name, performance_metrics, signal_info=None):
        """生成性能报告"""
        report = []
        report.append("=" * 60)
        report.append(f"策略性能报告 - {strategy_name}")
        report.append("=" * 60)
        
        for key, value in performance_metrics.items():
            report.append(f"{key:15}: {value}")
        
        if signal_info:
            report.append("\n最新信号分析:")
            report.append("-" * 40)
            for key, value in signal_info.items():
                if key != 'indicators':
                    report.append(f"{key:15}: {value}")
            
            if 'indicators' in signal_info:
                report.append("\n技术指标:")
                for indicator_key, indicator_value in signal_info['indicators'].items():
                    report.append(f"  {indicator_key:20}: {indicator_value}")
        
        return "\n".join(report)