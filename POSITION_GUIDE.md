# 仓位信息查询完全指南

## 📊 获取仓位信息的方法

### 方法1: 获取单个币种余额

```python
from v2_improved import GateIOTrader, TradingConfig

config = TradingConfig()
trader = GateIOTrader(config)

# 获取BTC余额
btc_balance = trader.get_cryptocurrency_balance('BTC')
print(f"BTC余额: {btc_balance}")

# 获取USDT余额
usdt_balance = trader.get_cryptocurrency_balance('USDT')
print(f"USDT余额: {usdt_balance}")
```

### 方法2: 获取计价币种余额

```python
# 获取账户中的USDT余额（包括可用和冻结）
usdt_info = trader.get_balance()
print(f"USDT可用: {usdt_info['available']}")
print(f"USDT冻结: {usdt_info['locked']}")
print(f"USDT总量: {usdt_info['total']}")
```

### 方法3: 获取完整仓位信息 ⭐ 推荐

```python
# 获取完整的仓位信息（推荐使用）
position = trader.get_position_info()

print(f"BTC数量: {position['base_total']}")
print(f"USDT数量: {position['quote_total']}")
print(f"当前价格: {position['current_price']}")
print(f"总资产价值: {position['total_assets']}")
print(f"仓位占比: {position['position_ratio'] * 100:.2f}%")
```

## 📈 仓位信息详解

`get_position_info()` 返回的完整数据结构：

```python
{
    'base_currency': 'BTC',                    # 基础币种（交易对左边的币）
    'quote_currency': 'USDT',                  # 计价币种（交易对右边的币）
    
    # 基础币信息
    'base_available': Decimal('0.001'),        # 可用的BTC
    'base_locked': Decimal('0'),               # 冻结的BTC（未成交订单）
    'base_total': Decimal('0.001'),            # BTC总量
    
    # 计价币信息
    'quote_available': Decimal('1000.50'),     # 可用的USDT
    'quote_locked': Decimal('50.00'),          # 冻结的USDT（未成交订单）
    'quote_total': Decimal('1050.50'),         # USDT总量
    
    # 价格和价值
    'current_price': Decimal('50000'),         # 当前BTC/USDT价格
    'base_position_value': Decimal('50000'),   # BTC仓位的USDT价值
    'total_assets': Decimal('51050.50'),       # 总资产USDT价值
    
    # 仓位占比
    'position_ratio': Decimal('0.98')          # 仓位占比 (98% 在BTC, 2% 在USDT)
}
```

## 🔍 实际使用示例

### 示例1: 检查是否持有仓位

```python
position = trader.get_position_info()

if position['base_total'] > 0:
    print(f"✅ 持有 {position['base_total']} {position['base_currency']}")
else:
    print("⚠️  未持有任何币种")
```

### 示例2: 计算账户总资产

```python
position = trader.get_position_info()

total_value = position['total_assets']
print(f"账户总资产: {total_value:.2f} USDT")

# 计算各部分占比
btc_value = position['base_position_value']
usdt_value = position['quote_total']

print(f"BTC价值: {btc_value:.2f} USDT ({btc_value/total_value*100:.2f}%)")
print(f"USDT持有: {usdt_value:.2f} USDT ({usdt_value/total_value*100:.2f}%)")
```

### 示例3: 检查可用余额

```python
position = trader.get_position_info()

available = position['quote_available']
locked = position['quote_locked']

print(f"可用资金: {available:.2f}")
print(f"冻结资金: {locked:.2f}")

if available < 100:
    print("⚠️  可用资金不足100，可能无法下单")
```

### 示例4: 监控仓位变化

```python
import time
from decimal import Decimal as D

config = TradingConfig()
config.CURRENCY_PAIR = "BTC_USDT"
trader = GateIOTrader(config)

previous_position = None

while True:
    current_position = trader.get_position_info()
    
    if previous_position:
        # 检查持仓是否变化
        if current_position['base_total'] != previous_position['base_total']:
            change = current_position['base_total'] - previous_position['base_total']
            print(f"🔔 持仓变化: {change:+.8f} {current_position['base_currency']}")
        
        # 检查价格是否变化
        if current_position['current_price'] != previous_position['current_price']:
            print(f"📈 价格更新: {current_position['current_price']} USDT")
    
    previous_position = current_position
    time.sleep(60)  # 每分钟检查一次
```

## 💡 仓位管理建议

### 1. 检查冻结资金

```python
position = trader.get_position_info()

# 如果冻结资金过多，可能是有待成交的订单
if position['quote_locked'] > position['quote_total'] * D('0.3'):
    print("⚠️  冻结资金过多，建议检查待处理订单")
    # 查看待处理订单
    orders = trader.list_pending_orders()
```

### 2. 评估仓位风险

```python
position = trader.get_position_info()

ratio = position['position_ratio']

if ratio > D('0.9'):
    print("🔴 仓位过重，建议降低风险")
elif ratio > D('0.7'):
    print("🟡 仓位较重，需要注意风险")
elif ratio < D('0.2'):
    print("🟢 仓位较轻，风险低")
else:
    print("🟢 仓位均衡")
```

### 3. 计算盈亏

```python
position = trader.get_position_info()

# 假设买入价格为40000
buy_price = 40000
current_price = float(position['current_price'])
btc_amount = float(position['base_total'])

cost = buy_price * btc_amount
current_value = current_price * btc_amount
profit = current_value - cost
profit_ratio = profit / cost * 100

print(f"成本: {cost:.2f} USDT")
print(f"现值: {current_value:.2f} USDT")
print(f"盈利: {profit:+.2f} USDT ({profit_ratio:+.2f}%)")
```

## 🔗 相关API方法

### GateIOTrader 类中的余额相关方法

| 方法 | 用途 | 返回值 |
|------|------|--------|
| `get_balance()` | 获取计价币余额 | Dict with available/locked/total |
| `get_cryptocurrency_balance(currency)` | 获取特定币种余额 | Decimal |
| `get_position_info()` | 获取完整仓位信息 | Dict with full position details |
| `get_ticker()` | 获取行情信息 | Dict with price/high/low/volume |

## 📊 完整查询脚本

运行以下脚本获取完整的仓位信息：

```bash
python get_position.py
```

输出示例：
```
======================================================================
📊 当前仓位信息
======================================================================

💎 BTC币 (基础币)
   可用: 0.10000000
   冻结: 0.00000000
   总量: 0.10000000

💵 USDT币 (计价币)
   可用: 5000.00
   冻结: 0.00
   总量: 5000.00

📈 价格和价值
   当前价格: 50000.00 USDT
   BTC仓位价值: 5000.00 USDT

💰 资产汇总
   总资产价值: 10000.00 USDT
   仓位占比: 50.00%
   现金占比: 50.00%
======================================================================
```

## 🛠️ 常见操作

### 清空所有仓位

```python
position = trader.get_position_info()

if position['base_total'] > 0:
    # 卖出所有币
    trader.place_order(
        'sell',
        position['base_total'],
        position['current_price']
    )
```

### 建仓指定比例

```python
from decimal import Decimal as D

position = trader.get_position_info()
total_assets = position['total_assets']

# 用50%的资金建仓
target_btc_value = total_assets * D('0.5')
buy_amount = target_btc_value / position['current_price']

trader.place_order('buy', buy_amount, position['current_price'])
```

### 定期监控账户

```python
import schedule
import time

def check_position():
    position = trader.get_position_info()
    print(f"账户资产: {position['total_assets']} USDT")

# 每小时检查一次
schedule.every(1).hour.do(check_position)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

**需要帮助？** 
- 查看 `QUICK_REFERENCE.md` 了解更多API调用
- 运行 `test_setup.py` 验证环境
- 查看 `GUIDE.md` 了解更多细节
