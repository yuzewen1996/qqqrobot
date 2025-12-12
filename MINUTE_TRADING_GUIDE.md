# 分钟级别交易策略指南

## 📋 概述

本指南介绍如何使用分钟级别的高频交易策略进行合约交易。这些策略专为短线交易设计，适合快速进出场。

---

## 🎯 包含的策略

### 1️⃣ **EMA快速突破策略**
- **原理**: 使用EMA5和EMA13的快速交叉
- **适用场景**: 趋势明确的行情
- **时间周期**: 1分钟、5分钟
- **优势**: 反应迅速，适合捕捉短期趋势
- **参数**:
  - `fast_period`: 快速EMA周期（默认5）
  - `slow_period`: 慢速EMA周期（默认13）
  - `volume_threshold`: 成交量倍数（默认1.2）

**信号条件**:
```
做多: EMA5上穿EMA13 且 成交量 > 平均成交量 × 1.2
做空: EMA5下穿EMA13 且 成交量 > 平均成交量 × 1.2
```

---

### 2️⃣ **布林带突破策略**
- **原理**: 价格突破布林带上下轨
- **适用场景**: 震荡行情的突破
- **时间周期**: 1分钟、5分钟
- **优势**: 明确的进出场位置
- **参数**:
  - `period`: 周期（默认20）
  - `std_dev`: 标准差倍数（默认2.0）

**信号条件**:
```
做多: 价格从下方突破上轨
做空: 价格从上方突破下轨
```

---

### 3️⃣ **动量突破策略**
- **原理**: 监控价格在短时间内的突破
- **适用场景**: 强势单边行情
- **时间周期**: 1分钟、5分钟
- **优势**: 捕捉快速突破机会
- **参数**:
  - `lookback`: 回溯周期（默认10）
  - `threshold_pct`: 突破阈值百分比（默认0.3%）

**信号条件**:
```
做多: 价格突破N分钟最高点 且 涨幅 > 0.3%
做空: 价格跌破N分钟最低点 且 跌幅 > 0.3%
```

---

### 4️⃣ **MACD快速交叉策略**
- **原理**: 使用短周期MACD捕捉趋势
- **适用场景**: 趋势初期
- **时间周期**: 1分钟、5分钟、15分钟
- **优势**: 经典指标，稳定可靠
- **参数**:
  - `fast`: 快线周期（默认5）
  - `slow`: 慢线周期（默认13）
  - `signal`: 信号线周期（默认5）

**信号条件**:
```
做多: MACD线上穿信号线（金叉）
做空: MACD线下穿信号线（死叉）
```

---

### 5️⃣ **波动率突破策略**
- **原理**: 基于ATR的波动率通道
- **适用场景**: 波动率扩大时
- **时间周期**: 5分钟、15分钟
- **优势**: 自适应市场波动
- **参数**:
  - `atr_period`: ATR周期（默认14）
  - `atr_multiplier`: ATR倍数（默认1.5）

**信号条件**:
```
做多: 价格 > 中轨 + ATR × 1.5
做空: 价格 < 中轨 - ATR × 1.5
```

---

## 🚀 快速开始

### 方法1: 使用默认配置

```python
from minute_trading_strategy import *
import os

# 设置API密钥
api_key = os.getenv('GATE_API_KEY')
api_secret = os.getenv('GATE_API_SECRET')

# 初始化机器人
bot = MinuteTradingBot(api_key, api_secret, settle='usdt')

# 设置要监控的合约
contracts = ['BTC_USDT', 'ETH_USDT']

# 创建运行器
runner = MinuteTradingRunner(bot, contracts)

# 添加所有策略
runner.add_strategy('EMA突破', EMABreakoutStrategy)
runner.add_strategy('布林带', BollingerBandsStrategy)
runner.add_strategy('动量突破', MomentumBreakoutStrategy)
runner.add_strategy('MACD快速', MACDFastStrategy)
runner.add_strategy('波动率突破', VolatilityBreakoutStrategy)

# 运行（1分钟K线，每60秒检查一次）
runner.run_continuous(interval='1m', check_interval=60)
```

### 方法2: 自定义参数

```python
# 创建运行器
runner = MinuteTradingRunner(bot, ['BTC_USDT'])

# 添加策略并自定义参数
runner.add_strategy(
    'EMA突破', 
    EMABreakoutStrategy,
    fast_period=3,      # 更快的反应
    slow_period=8,
    volume_threshold=1.5  # 更严格的成交量要求
)

runner.add_strategy(
    '布林带',
    BollingerBandsStrategy,
    period=15,          # 更短的周期
    std_dev=2.5         # 更宽的布林带
)

# 运行
runner.run_continuous(interval='5m', check_interval=300)  # 5分钟
```

### 方法3: 单独使用某个策略

```python
# 只使用EMA突破策略
bot = MinuteTradingBot(api_key, api_secret)
strategy = EMABreakoutStrategy(bot, 'BTC_USDT', fast_period=5, slow_period=13)

# 获取K线
candles = bot.get_candlesticks('BTC_USDT', interval='1m', limit=100)

# 生成信号
signal = strategy.generate_signal(candles)

if signal == 'long':
    bot.place_order('BTC_USDT', size=1, is_long=True)
elif signal == 'short':
    bot.place_order('BTC_USDT', size=1, is_long=False)
```

---

## ⚙️ 参数调优建议

### 1分钟K线配置（极短线）
```python
# EMA突破 - 超快反应
runner.add_strategy('EMA', EMABreakoutStrategy, 
    fast_period=3, slow_period=8, volume_threshold=1.5)

# MACD - 快速周期
runner.add_strategy('MACD', MACDFastStrategy,
    fast=3, slow=8, signal=3)

# 动量突破 - 小回溯期
runner.add_strategy('动量', MomentumBreakoutStrategy,
    lookback=5, threshold_pct=0.2)
```

### 5分钟K线配置（短线）
```python
# EMA突破 - 标准配置
runner.add_strategy('EMA', EMABreakoutStrategy,
    fast_period=5, slow_period=13, volume_threshold=1.2)

# 布林带 - 标准配置
runner.add_strategy('布林带', BollingerBandsStrategy,
    period=20, std_dev=2.0)

# 波动率突破
runner.add_strategy('波动率', VolatilityBreakoutStrategy,
    atr_period=14, atr_multiplier=1.5)
```

### 15分钟K线配置（中短线）
```python
# MACD - 标准周期
runner.add_strategy('MACD', MACDFastStrategy,
    fast=12, slow=26, signal=9)

# 波动率突破 - 更宽的通道
runner.add_strategy('波动率', VolatilityBreakoutStrategy,
    atr_period=14, atr_multiplier=2.0)
```

---

## 🎨 多策略组合建议

### 组合1: 激进型（1分钟）
适合追求高频交易，能够快速反应的交易者

```python
contracts = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT']
runner = MinuteTradingRunner(bot, contracts)

runner.add_strategy('EMA', EMABreakoutStrategy, fast_period=3, slow_period=8)
runner.add_strategy('动量', MomentumBreakoutStrategy, lookback=5, threshold_pct=0.2)
runner.add_strategy('MACD', MACDFastStrategy, fast=3, slow=8, signal=3)

runner.run_continuous(interval='1m', check_interval=60)
```

### 组合2: 稳健型（5分钟）
平衡风险和收益

```python
contracts = ['BTC_USDT', 'ETH_USDT']
runner = MinuteTradingRunner(bot, contracts)

runner.add_strategy('EMA', EMABreakoutStrategy, fast_period=5, slow_period=13)
runner.add_strategy('布林带', BollingerBandsStrategy, period=20, std_dev=2.0)
runner.add_strategy('波动率', VolatilityBreakoutStrategy, atr_period=14)

runner.run_continuous(interval='5m', check_interval=300)
```

### 组合3: 多信号确认型
需要多个策略同时确认才交易

```python
contracts = ['BTC_USDT']
runner = MinuteTradingRunner(bot, contracts)

# 添加所有5个策略
runner.add_strategy('EMA', EMABreakoutStrategy)
runner.add_strategy('布林带', BollingerBandsStrategy)
runner.add_strategy('动量', MomentumBreakoutStrategy)
runner.add_strategy('MACD', MACDFastStrategy)
runner.add_strategy('波动率', VolatilityBreakoutStrategy)

# 在 run_continuous 中添加逻辑：
# 只有当至少3个策略同时产生相同信号时才执行交易
```

---

## 📊 实时监控示例

创建一个简单的监控脚本：

```python
def monitor_with_alert():
    """带告警的监控"""
    bot = MinuteTradingBot(api_key, api_secret)
    contracts = ['BTC_USDT', 'ETH_USDT']
    
    runner = MinuteTradingRunner(bot, contracts)
    runner.add_strategy('EMA', EMABreakoutStrategy)
    runner.add_strategy('MACD', MACDFastStrategy)
    
    while True:
        signals = runner.run_once(interval='5m')
        
        for contract, strategy_signals in signals.items():
            long_count = sum(1 for _, s in strategy_signals if s == 'long')
            short_count = sum(1 for _, s in strategy_signals if s == 'short')
            
            # 多个策略确认时发出告警
            if long_count >= 2:
                print(f"🚨 强烈做多信号: {contract}")
                # 可以在这里添加下单逻辑
                # bot.place_order(contract, size=1, is_long=True)
            
            if short_count >= 2:
                print(f"🚨 强烈做空信号: {contract}")
                # bot.place_order(contract, size=1, is_long=False)
        
        time.sleep(300)  # 5分钟检查一次

if __name__ == '__main__':
    monitor_with_alert()
```

---

## ⚠️ 风险管理建议

### 1. 设置止损止盈
```python
def place_order_with_stops(bot, contract, size, is_long, 
                           entry_price, stop_loss_pct=2.0, take_profit_pct=4.0):
    """带止损止盈的下单"""
    # 下单
    bot.place_order(contract, size, is_long=is_long)
    
    # 计算止损止盈价格
    if is_long:
        stop_loss = entry_price * (1 - stop_loss_pct / 100)
        take_profit = entry_price * (1 + take_profit_pct / 100)
    else:
        stop_loss = entry_price * (1 + stop_loss_pct / 100)
        take_profit = entry_price * (1 - take_profit_pct / 100)
    
    # 设置止损止盈订单
    # ... (使用Gate.io的止损止盈功能)
```

### 2. 仓位管理
```python
# 单次交易不超过账户资金的2%
max_risk_per_trade = 0.02

# 根据账户余额计算仓位大小
account_balance = 10000  # USDT
risk_amount = account_balance * max_risk_per_trade
position_size = risk_amount / (entry_price * stop_loss_pct / 100)
```

### 3. 时间过滤
```python
from datetime import datetime

def is_trading_time():
    """只在活跃时段交易"""
    hour = datetime.now().hour
    # 避开凌晨低流动性时段
    return 8 <= hour <= 23

# 在策略运行前检查
if is_trading_time():
    runner.run_once(interval='5m')
```

### 4. 最大持仓数量限制
```python
max_positions = 3  # 最多同时持有3个仓位
current_positions = len(get_active_positions())

if current_positions < max_positions:
    # 允许开新仓
    pass
else:
    print("已达到最大持仓数量")
```

---

## 📈 性能优化建议

### 1. 减少API调用
```python
# 缓存K线数据
from functools import lru_cache
from time import time

@lru_cache(maxsize=10)
def get_cached_candles(contract, interval, timestamp):
    """缓存K线数据（按分钟缓存）"""
    return bot.get_candlesticks(contract, interval, limit=100)

# 使用时
current_minute = int(time() // 60)
candles = get_cached_candles('BTC_USDT', '1m', current_minute)
```

### 2. 并行处理多个合约
```python
from concurrent.futures import ThreadPoolExecutor

def process_contract(contract):
    """处理单个合约"""
    candles = bot.get_candlesticks(contract, '1m', 100)
    signals = []
    for strategy in strategies:
        signal = strategy.generate_signal(candles)
        signals.append(signal)
    return contract, signals

# 并行处理
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(process_contract, contracts)
```

### 3. 使用WebSocket实时数据
```python
# TODO: 实现WebSocket连接以获取实时价格更新
# 这样可以避免轮询，提高响应速度
```

---

## 🔧 调试和测试

### 回测功能（简单版）
```python
def simple_backtest(strategy, contract, start_date, end_date):
    """简单回测"""
    # 获取历史数据
    candles = bot.get_candlesticks(contract, '5m', limit=1000)
    
    signals = []
    for i in range(50, len(candles)):
        window = candles[:i+1]
        signal = strategy.generate_signal(window)
        if signal != 'hold':
            signals.append({
                'time': candles[i]['time'],
                'signal': signal,
                'price': candles[i]['close']
            })
    
    return signals
```

### 日志记录
```python
# 详细的日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minute_trading.log'),
        logging.StreamHandler()
    ]
)
```

---

## 📞 常见问题

**Q: 为什么有时候没有信号？**
A: 策略需要足够的历史数据才能计算指标。确保K线数据量足够（至少100根）。

**Q: 可以同时运行多个时间周期吗？**
A: 可以，但需要为每个时间周期创建单独的runner实例。

**Q: 如何避免频繁交易？**
A: 增加check_interval值，或添加信号确认逻辑（如需要多个策略同时确认）。

**Q: 策略参数如何优化？**
A: 建议先用默认参数测试，然后根据历史数据回测调整参数。

---

## 📚 进阶阅读

- 查看 `advanced_strategies.py` 了解更多策略
- 查看 `main.py` 了解完整的交易系统
- 查看 `POSITION_GUIDE.md` 了解仓位管理

---

## ⚖️ 免责声明

本策略仅供学习和参考，不构成投资建议。
加密货币交易存在高风险，请谨慎投资，风险自负。
建议先在测试网环境充分测试后再使用实盘。

---

**祝交易顺利！** 🎯
