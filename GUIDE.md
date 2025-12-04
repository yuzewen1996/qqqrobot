# 交易机器人使用指南

## 📚 项目概述

这是一个基于 GateIO 官方 API 库的智能交易机器人，支持自动化的现货交易。

### 版本对比

| 特性 | v1.py | v2_improved.py |
|------|-------|----------------|
| 代码结构 | 简单 | 面向对象（OOP） |
| 错误处理 | 基础 | 完善 |
| 功能模块 | 基础 | 丰富（订单管理、交易记录等） |
| 配置管理 | 硬编码 | 配置类 |
| 日志系统 | 简单 | 文件+控制台双输出 |
| 订单查询 | ❌ | ✅ |
| 待处理订单列表 | ❌ | ✅ |
| 策略类 | ❌ | ✅ |

## 🚀 快速开始

### 1. 配置API密钥

编辑 `v2_improved.py`，找到 `TradingConfig` 类：

```python
class TradingConfig:
    API_KEY = "你的_API_KEY"
    API_SECRET = "你的_API_SECRET"
    USE_TESTNET = True  # 首次建议使用测试网
```

**获取API密钥步骤：**
1. 登录 [Gate.io](https://www.gate.io)
2. 点击右上角头像 → API管理
3. 创建新的 API Key
4. 复制 Key 和 Secret（**Secret 只显示一次，务必妥善保管**）

### 2. 配置交易参数

```python
# 交易对配置
CURRENCY_PAIR = "BTC_USDT"  # 交易对
CURRENCY = "USDT"           # 基础货币

# 交易参数
BUY_AMOUNT = D("0.001")           # 每次买入0.001 BTC
SELL_AMOUNT = D("0.001")          # 每次卖出0.001 BTC
TARGET_BUY_PRICE = D("50000")     # 目标买入价格
TARGET_SELL_PRICE = D("60000")    # 目标卖出价格

# 机器人参数
CHECK_INTERVAL = 10  # 每10秒检查一次
USE_TESTNET = False  # 改为 True 使用测试网
```

### 3. 运行机器人

```bash
# 方法1：直接运行
python v2_improved.py

# 方法2：使用测试网（推荐首先尝试）
# 先在代码中设置 USE_TESTNET = True，然后运行
python v2_improved.py
```

## 📖 核心概念

### GateIOTrader 类

**主要功能：**
- `get_ticker()` - 获取实时行情
- `get_balance()` - 获取账户余额
- `get_cryptocurrency_balance(currency)` - 获取特定币种余额
- `place_order(side, amount, price)` - 下单（买/卖）
- `cancel_order(order_id)` - 取消订单
- `get_order(order_id)` - 查询单个订单
- `list_pending_orders()` - 查询待处理订单

### TradingStrategy 类

**内置策略：**
```
simple_strategy():
  ├─ 如果价格 < 买入目标价 且 未持仓
  │  └─ 执行买入
  └─ 如果价格 > 卖出目标价 且 已持仓
     └─ 执行卖出
```

## 🔧 API 学习资源

### 官方文档
- [GateIO API 文档](https://www.gate.io/docs/apiv4/en)
- [Python SDK 文档](https://github.com/gateio/gateapi-python)

### 常用API调用

```python
# 1. 获取行情
tickers = spot_api.list_tickers(currency_pair='BTC_USDT')
print(tickers[0].last)  # 最新价格

# 2. 获取账户信息
accounts = spot_api.list_spot_accounts(currency='USDT')
print(accounts[0].available)  # 可用余额

# 3. 下单
order = gate_api.Order(
    currency_pair='BTC_USDT',
    side='buy',
    amount='0.001',
    price='50000'
)
created = spot_api.create_order(order)

# 4. 查询订单
order = spot_api.get_order('order_id', 'BTC_USDT')
print(order.status)  # 订单状态

# 5. 取消订单
spot_api.cancel_order('order_id', currency_pair='BTC_USDT')

# 6. 查询待处理订单
orders = spot_api.list_orders(currency_pair='BTC_USDT', status='open')
```

## 🎯 改进建议

### 短期改进

1. **添加止损逻辑**
```python
def advanced_strategy(self):
    """添加止损保护"""
    STOP_LOSS_PERCENTAGE = 0.02  # 亏损2%止损
    
    if self.buy_hold and current_price < self.last_buy_price * (1 - STOP_LOSS_PERCENTAGE):
        logger.warning("⚠️ 触发止损")
        self.trader.place_order('sell', self.config.SELL_AMOUNT, current_price)
```

2. **使用市价单**
```python
# 替代限价单，立即成交
order = gate_api.Order(
    currency_pair='BTC_USDT',
    side='buy',
    amount='0.001',
    price='0',  # 价格设为0表示市价
    tif='ioc'   # IOC: 立即成交或取消
)
```

3. **记录交易历史**
```python
import json
from datetime import datetime

def log_trade(self, side, amount, price):
    """记录交易到文件"""
    trade_record = {
        'timestamp': datetime.now().isoformat(),
        'side': side,
        'amount': str(amount),
        'price': str(price)
    }
    with open('trades.json', 'a') as f:
        json.dump(trade_record, f)
        f.write('\n')
```

### 中期改进

1. **添加技术指标**（需要安装 `pandas` 和 `ta-lib`）
```bash
pip install pandas ta-lib
```

```python
def calculate_moving_averages(self):
    """计算移动平均线"""
    # 获取K线数据
    candlesticks = self.spot_api.list_candlesticks(
        currency_pair=self.config.CURRENCY_PAIR,
        interval='1h',  # 1小时K线
        limit=50
    )
    # 计算MA20, MA50
```

2. **多品种交易**
```python
trading_pairs = ['BTC_USDT', 'ETH_USDT', 'XRP_USDT']
for pair in trading_pairs:
    self.config.CURRENCY_PAIR = pair
    self.strategy.simple_strategy()
```

3. **添加数据库存储**
```bash
pip install sqlalchemy
```

### 长期改进

1. **WebSocket实时行情**
2. **机器学习预测**
3. **风险管理系统**
4. **Web仪表板**

## ⚠️ 重要安全提示

### 安全最佳实践

1. **不要硬编码密钥**
```python
# ❌ 不要这样做
API_KEY = "abc123def456"

# ✅ 使用环境变量
import os
API_KEY = os.getenv('GATE_API_KEY')
```

2. **使用IP白名单**
   - 在GateIO中设置 IP 白名单
   - 只允许特定IP调用API

3. **限制API权限**
   - 只授予"现货交易"权限
   - 禁用"充提币"权限

4. **监控账户活动**
   - 定期检查交易记录
   - 设置异常交易告警

## 📊 日志文件

机器人会生成 `trading_bot.log` 文件，记录所有操作：

```
2025-12-04 10:30:15,123 - INFO - API客户端已初始化 - 模式: 测试网
2025-12-04 10:30:16,456 - INFO - 当前价格: 50100 USDT | 24h高: 50500 | 24h低: 49800
2025-12-04 10:30:16,789 - INFO - 账户余额 - USDT: 1000.50 | BTC: 0.001
```

## 🐛 常见问题

### Q: 怎样区分订单是否成交？
**A:** 检查订单状态
```python
order = trader.get_order(order_id)
if order['status'] == 'closed':
    print("订单已成交")
elif order['status'] == 'open':
    print("订单待处理")
elif order['status'] == 'cancelled':
    print("订单已取消")
```

### Q: 如何测试而不实际下单？
**A:** 使用 `USE_TESTNET = True` 连接测试网

### Q: 怎样快速止损？
**A:** 使用市价单立即卖出
```python
order = gate_api.Order(
    currency_pair='BTC_USDT',
    side='sell',
    amount='0.001',
    price='0',
    tif='ioc'
)
```

## 📚 相关资源

- [Gate API Python SDK](https://github.com/gateio/gateapi-python)
- [Gate 官方API文档](https://www.gate.io/docs/apiv4)
- [Python Decimal 文档](https://docs.python.org/3/library/decimal.html)
- [异常处理最佳实践](https://docs.python.org/3/tutorial/errors.html)

---

**最后更新:** 2025-12-04
**作者:** GitHub Copilot
**版本:** 2.0
