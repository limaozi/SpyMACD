import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 1. 读取数据
def load_stock_data():
    """加载股票数据"""
    df = pd.read_csv('stock_data.csv')
    
    # 转换日期格式
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # 确保数据列是数值类型
    numeric_cols = ['open', 'high', 'low', 'close', 'adjclose', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# 2. 计算MACD指标
def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """计算MACD指标"""
    df = df.copy()
    
    # 计算指数移动平均线（EMA）
    df['ema_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
    
    # 计算MACD线
    df['macd'] = df['ema_fast'] - df['ema_slow']
    
    # 计算信号线
    df['signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
    
    # 计算MACD柱状图（Histogram）
    df['histogram'] = df['macd'] - df['signal']
    
    return df

# 3. 生成交易信号
def generate_macd_signals(df):
    """生成MACD交易信号"""
    df = df.copy()
    
    # 初始化信号列
    df['signal'] = 0  # 0: 无信号, 1: 买入, -1: 卖出
    df['position'] = 0  # 持仓状态: 0: 空仓, 1: 持有多头
    df['entry_price'] = np.nan  # 入场价格
    df['exit_price'] = np.nan  # 出场价格
    
    # 计算信号
    for i in range(1, len(df)):
        # MACD金叉（买入信号）：MACD从下方穿过信号线
        if (df.loc[i-1, 'macd'] < df.loc[i-1, 'signal'] and 
            df.loc[i, 'macd'] > df.loc[i, 'signal']):
            df.loc[i, 'signal'] = 1
        
        # MACD死叉（卖出信号）：MACD从上方穿过信号线
        elif (df.loc[i-1, 'macd'] > df.loc[i-1, 'signal'] and 
              df.loc[i, 'macd'] < df.loc[i, 'signal']):
            df.loc[i, 'signal'] = -1
    
    return df

# 4. 执行交易策略
def execute_trading_strategy(df, initial_capital=100000):
    """执行交易策略并计算收益"""
    df = df.copy()
    
    # 添加策略列
    df['action'] = 'HOLD'  # 交易动作
    df['position'] = 0  # 持仓数量
    df['cash'] = initial_capital  # 现金
    df['portfolio_value'] = initial_capital  # 投资组合价值
    df['returns'] = 0.0  # 日收益率
    df['strategy_returns'] = 0.0  # 策略收益率
    
    position = 0  # 当前持仓
    entry_price = 0  # 入场价格
    shares_held = 0  # 持有股数
    
    for i in range(len(df)):
        current_price = df.loc[i, 'close']
        current_date = df.loc[i, 'date']
        signal = df.loc[i, 'signal']
        cash = df.loc[i-1, 'cash'] if i > 0 else initial_capital
        
        # 买入信号且当前没有持仓
        if signal == 1 and position == 0:
            # 计算可买入的股票数量（假设全仓买入）
            shares_to_buy = int(cash / current_price)
            if shares_to_buy > 0:
                position = 1
                shares_held = shares_to_buy
                entry_price = current_price
                cash -= shares_to_buy * current_price
                df.loc[i, 'action'] = 'BUY'
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
        df.loc[i, 'entry_price'] = entry_price if position == 1 else np.nan
        df.loc[i, 'cash'] = cash
        df.loc[i, 'portfolio_value'] = cash + (shares_held * current_price if position == 1 else 0)
    
    return df

# 5. 每日检查函数
def check_daily_signals(df, check_date=None):
    """检查特定日期的交易信号"""
    if check_date is None:
        check_date = datetime.now().date()
    else:
        check_date = pd.to_datetime(check_date).date()
    
    # 找到最接近的交易日
    df['date_only'] = df['date'].dt.date
    if check_date in df['date_only'].values:
        day_data = df[df['date_only'] == check_date].iloc[0]
    else:
        # 如果不是交易日，找到前一个交易日
        earlier_dates = df[df['date_only'] < check_date]
        if len(earlier_dates) == 0:
            return "没有找到历史数据"
        day_data = earlier_dates.iloc[-1]
        check_date = day_data['date_only']
    
    # 获取MACD指标
    macd_value = day_data['macd']
    signal_value = day_data['signal']
    histogram = day_data['histogram']
    close_price = day_data['close']
    
    # 分析信号
    signal_type = "无信号"
    recommendation = "持有"
    
    if day_data['signal'] == 1:
        signal_type = "买入信号 (MACD金叉)"
        recommendation = "考虑买入"
    elif day_data['signal'] == -1:
        signal_type = "卖出信号 (MACD死叉)"
        recommendation = "考虑卖出"
    
    # 趋势分析
    if macd_value > 0:
        trend = "上升趋势"
    else:
        trend = "下降趋势"
    
    # 动量分析
    if histogram > 0 and histogram > day_data.get('histogram_prev', 0):
        momentum = "增强"
    elif histogram > 0:
        momentum = "减弱"
    elif histogram < 0 and histogram < day_data.get('histogram_prev', 0):
        momentum = "增强"
    else:
        momentum = "减弱"
    
    return {
        'date': check_date,
        'close_price': close_price,
        'macd': macd_value,
        'signal_line': signal_value,
        'histogram': histogram,
        'trend': trend,
        'momentum': momentum,
        'signal_type': signal_type,
        'recommendation': recommendation,
        'action': day_data.get('action', 'HOLD')
    }

# 6. 回测和性能评估
def evaluate_strategy(df):
    """评估策略性能"""
    # 计算基准收益（买入并持有）
    initial_price = df.loc[0, 'close']
    final_price = df.loc[len(df)-1, 'close']
    buy_hold_return = (final_price / initial_price - 1) * 100
    
    # 计算策略收益
    initial_portfolio = df.loc[0, 'portfolio_value']
    final_portfolio = df.loc[len(df)-1, 'portfolio_value']
    strategy_return = (final_portfolio / initial_portfolio - 1) * 100
    
    # 计算最大回撤
    df['cummax'] = df['portfolio_value'].cummax()
    df['drawdown'] = (df['portfolio_value'] - df['cummax']) / df['cummax'] * 100
    max_drawdown = df['drawdown'].min()
    
    # 统计交易次数
    buy_signals = len(df[df['action'] == 'BUY'])
    sell_signals = len(df[df['action'] == 'SELL'])
    total_trades = buy_signals + sell_signals
    
    # 计算胜率（如果有卖出记录）
    trades = []
    entry_price = None
    for i in range(len(df)):
        if df.loc[i, 'action'] == 'BUY':
            entry_price = df.loc[i, 'close']
        elif df.loc[i, 'action'] == 'SELL' and entry_price is not None:
            exit_price = df.loc[i, 'close']
            profit_pct = (exit_price / entry_price - 1) * 100
            trades.append({
                'entry_date': df.loc[i-1, 'date'],
                'exit_date': df.loc[i, 'date'],
                'entry_price': entry_price,
                'exit_price': exit_price,
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
    
    return {
        '初始投资': f"${df.loc[0, 'portfolio_value']:,.2f}",
        '最终价值': f"${final_portfolio:,.2f}",
        '策略总收益': f"{strategy_return:.2f}%",
        '买入持有收益': f"{buy_hold_return:.2f}%",
        '超额收益': f"{strategy_return - buy_hold_return:.2f}%",
        '最大回撤': f"{max_drawdown:.2f}%",
        '总交易次数': total_trades,
        '买入信号': buy_signals,
        '卖出信号': sell_signals,
        '胜率': f"{win_rate:.1f}%",
        '平均每笔收益': f"{avg_profit:.2f}%",
        '平均盈利': f"{avg_win:.2f}%",
        '平均亏损': f"{avg_loss:.2f}%",
        '交易次数': len(trades)
    }

# 7. 可视化结果
def visualize_results(df):
    """可视化MACD策略结果"""
    fig, axes = plt.subplots(3, 1, figsize=(15, 12))
    
    # 子图1：价格和交易信号
    ax1 = axes[0]
    ax1.plot(df['date'], df['close'], label='收盘价', color='blue', alpha=0.7)
    
    # 标记买入点
    buy_points = df[df['action'] == 'BUY']
    if not buy_points.empty:
        ax1.scatter(buy_points['date'], buy_points['close'], 
                   color='green', marker='^', s=100, label='买入', zorder=5)
    
    # 标记卖出点
    sell_points = df[df['action'] == 'SELL']
    if not sell_points.empty:
        ax1.scatter(sell_points['date'], sell_points['close'], 
                   color='red', marker='v', s=100, label='卖出', zorder=5)
    
    ax1.set_title('股票价格与交易信号')
    ax1.set_ylabel('价格 ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 子图2：MACD指标
    ax2 = axes[1]
    ax2.plot(df['date'], df['macd'], label='MACD', color='blue')
    ax2.plot(df['date'], df['signal'], label='信号线', color='orange')
    
    # 绘制MACD柱状图
    colors = ['green' if h > 0 else 'red' for h in df['histogram']]
    ax2.bar(df['date'], df['histogram'], color=colors, alpha=0.3, label='柱状图')
    
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.set_title('MACD指标')
    ax2.set_ylabel('MACD值')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 子图3：投资组合价值
    ax3 = axes[2]
    ax3.plot(df['date'], df['portfolio_value'], label='策略组合价值', color='green')
    ax3.plot(df['date'], df['close'] / df['close'].iloc[0] * df['portfolio_value'].iloc[0], 
            label='买入持有', color='blue', alpha=0.5)
    ax3.set_title('投资组合表现对比')
    ax3.set_ylabel('价值 ($)')
    ax3.set_xlabel('日期')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('macd_strategy_results.png', dpi=300, bbox_inches='tight')
    plt.show()

# 8. 主函数
def main():
    """主函数：执行完整的MACD策略"""
    print("=" * 60)
    print("MACD交易策略模型")
    print("=" * 60)
    
    # 步骤1：加载数据
    print("\n1. 加载股票数据...")
    df = load_stock_data()
    print(f"   数据范围: {df['date'].min().date()} 到 {df['date'].max().date()}")
    print(f"   数据行数: {len(df)}")
    
    # 步骤2：计算MACD指标
    print("\n2. 计算MACD指标...")
    df = calculate_macd(df)
    
    # 步骤3：生成交易信号
    print("\n3. 生成交易信号...")
    df = generate_macd_signals(df)
    
    # 步骤4：执行交易策略
    print("\n4. 执行交易策略...")
    df = execute_trading_strategy(df, initial_capital=100000)
    
    # 步骤5：评估策略性能
    print("\n5. 评估策略性能...")
    performance = evaluate_strategy(df)
    
    print("\n" + "=" * 60)
    print("策略性能报告")
    print("=" * 60)
    for key, value in performance.items():
        print(f"{key:15}: {value}")
    
    # 步骤6：可视化结果
    print("\n6. 生成可视化图表...")
    visualize_results(df)
    
    # 步骤7：检查最新交易信号
    print("\n7. 最新交易信号检查...")
    latest_date = df['date'].max()
    signal_info = check_daily_signals(df, latest_date)
    
    print(f"\n最新交易日: {signal_info['date']}")
    print(f"收盘价: ${signal_info['close_price']:.2f}")
    print(f"MACD: {signal_info['macd']:.4f}")
    print(f"信号线: {signal_info['signal_line']:.4f}")
    print(f"趋势: {signal_info['trend']}")
    print(f"动量: {signal_info['momentum']}")
    print(f"信号类型: {signal_info['signal_type']}")
    print(f"建议: {signal_info['recommendation']}")
    print(f"操作: {signal_info['action']}")
    
    return df, performance

# 9. 每日运行函数
def daily_check():
    """每日运行检查交易信号"""
    print(f"\n{'='*60}")
    print(f"每日交易信号检查 - {datetime.now().date()}")
    print(f"{'='*60}")
    
    # 加载数据
    df = load_stock_data()
    df = calculate_macd(df)
    df = generate_macd_signals(df)
    
    # 获取最新数据
    latest_data = df.iloc[-1]
    prev_data = df.iloc[-2] if len(df) > 1 else latest_data
    
    # 分析当前信号
    current_macd = latest_data['macd']
    current_signal = latest_data['signal_line'] if 'signal_line' in latest_data else latest_data['signal']
    prev_macd = prev_data['macd']
    prev_signal = prev_data['signal_line'] if 'signal_line' in prev_data else prev_data['signal']
    
    # 判断信号
    buy_signal = False
    sell_signal = False
    
    # MACD金叉：MACD从下方上穿信号线
    if prev_macd < prev_signal and current_macd > current_signal:
        buy_signal = True
    
    # MACD死叉：MACD从上方下穿信号线
    elif prev_macd > prev_signal and current_macd < current_signal:
        sell_signal = True
    
    # 输出结果
    print(f"\n📅 日期: {latest_data['date'].date()}")
    print(f"💰 收盘价: ${latest_data['close']:.2f}")
    print(f"📊 MACD: {current_macd:.4f}")
    print(f"📈 信号线: {current_signal:.4f}")
    print(f"📉 MACD柱状图: {latest_data['histogram']:.4f}")
    
    print(f"\n{'🔍 信号分析 ':-^50}")
    if buy_signal:
        print("✅ **强烈买入信号** - MACD金叉形成")
        print("   建议: 考虑建立多头仓位")
    elif sell_signal:
        print("❌ **强烈卖出信号** - MACD死叉形成")
        print("   建议: 考虑平仓或建立空头仓位")
    else:
        if current_macd > 0:
            if current_macd > current_signal:
                print("📈 趋势: 上升趋势中，MACD在信号线上方")
                print("   建议: 持有或等待更好的买入机会")
            else:
                print("⚠️  注意: 上升趋势但MACD在信号线下方")
                print("   建议: 谨慎观望")
        else:
            if current_macd < current_signal:
                print("📉 趋势: 下降趋势中，MACD在信号线下方")
                print("   建议: 避免买入，考虑减仓")
            else:
                print("🔄 趋势: 下降趋势但MACD在信号线上方")
                print("   建议: 可能即将反弹，保持关注")
    
    print(f"\n💡 技术指标:")
    print(f"   12日EMA: ${latest_data['ema_fast']:.2f}")
    print(f"   26日EMA: ${latest_data['ema_slow']:.2f}")
    print(f"   成交量: {latest_data['volume']:,}")
    
    # 返回信号供其他系统使用
    return {
        'date': latest_data['date'].date(),
        'close': latest_data['close'],
        'macd': current_macd,
        'signal_line': current_signal,
        'histogram': latest_data['histogram'],
        'buy_signal': buy_signal,
        'sell_signal': sell_signal,
        'recommendation': 'BUY' if buy_signal else 'SELL' if sell_signal else 'HOLD'
    }

# 运行主程序
if __name__ == "__main__":
    # 运行完整策略分析
    df, performance = main()
    
    # 运行每日检查
    print(f"\n{'='*60}")
    print("每日检查模式")
    print(f"{'='*60}")
    daily_check()
    
    # 保存结果到CSV
    df.to_csv('macd_trading_signals.csv', index=False)
    print(f"\n✅ 交易信号已保存到: macd_trading_signals.csv")
    print(f"✅ 图表已保存到: macd_strategy_results.png")