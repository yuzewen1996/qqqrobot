# 交易机器人快速参考

## 📂 文件结构

```
qqqrobot/
├── v1.py                    # 原始版本（基础功能）
├── v2_improved.py           # ✨ 改进版本（推荐使用）
├── advanced_strategies.py   # 高级策略示例
├── GUIDE.md                 # 详细使用指南
└── trading_bot.log         # 运行日志（自动生成）
```

## 🔑 核心API速查表

### 1. 初始化API

```python
import gate_api

config = gate_api.Configuration(
    host="https://api.gateio.ws/api/v4",
    key="YOUR_API_KEY",
    secret="YOUR_API_SECRET"
)
spot_api = gate_api.SpotApi(gate_api.ApiClient(config))
```

### 2. 获取行情

```python
# 获取Ticker
tickers = spot_api.list_tickers(currency_pair='BTC_USDT')
print(tickers[0].last)  # 最新价格

# 获取K线
candles = spot_api.list_candlesticks(
    currency_pair='BTC_USDT',
    interval='1h',  # 可选：5m, 15m, 30m, 1h, 4h, 8h, 1d, 7d, 30d
    limit=100
)
```

### 3. 账户相关

```python
# 获取账户余额
accounts = spot_api.list_spot_accounts(currency='USDT')
available = accounts[0].available  # 可用余额
locked = accounts[0].locked        # 冻结余额

# 获取账户手续费
fee = spot_api.get_fee()
print(fee.taker_fee)  # Taker手续费
```

### 4. 下单操作

```python
# 下限价单
order = gate_api.Order(
    currency_pair='BTC_USDT',
    side='buy',          # 'buy' 或 'sell'
    amount='0.001',      # 数量
    price='50000'        # 价格
)
created = spot_api.create_order(order)
order_id = created.id

# 下市价单（IOC - 立即成交或取消）
order = gate_api.Order(
    currency_pair='BTC_USDT',
    side='sell',
    amount='0.001',
    price='0',           # 价格为0表示市价
    tif='ioc'           # 时间条件
)
```

### 5. 订单管理

```python
# 查询单个订单
order = spot_api.get_order('order_id', currency_pair='BTC_USDT')
print(order.status)  # open, closed, cancelled

# 查询待处理订单
orders = spot_api.list_orders(
    currency_pair='BTC_USDT',
    status='open'  # 'open', 'closed', 'cancelled'
)

# 取消订单
cancelled = spot_api.cancel_order(
    'order_id',
    currency_pair='BTC_USDT'
)
```

### 6. 交易记录

```python
# 查询成交记录
trades = spot_api.list_my_trades(
    currency_pair='BTC_USDT',
    limit=100,
    _from=start_timestamp,
    to=end_timestamp
)
```

## 🎯 v2_improved.py 使用步骤

### 第1步：配置

```python
class TradingConfig:
    API_KEY = "your_api_key"
    API_SECRET = "your_api_secret"
    
    TARGET_BUY_PRICE = D("50000")      # 买入价格
    TARGET_SELL_PRICE = D("60000")     # 卖出价格
    BUY_AMOUNT = D("0.001")            # 买入数量
    SELL_AMOUNT = D("0.001")           # 卖出数量
    CHECK_INTERVAL = 10                # 检查间隔(秒)
    USE_TESTNET = True                 # 测试网/实盘
```

### 第2步：运行

```bash
python v2_improved.py
```

### 第3步：查看日志

```bash
# 实时查看日志
tail -f trading_bot.log

# PowerShell中查看
Get-Content trading_bot.log -Tail 20 -Wait
```

## 🚀 常用命令

### Git相关

```bash
# 查看状态
git status

# 查看修改内容
git diff

# 添加文件
git add filename.py

# 提交更改
git commit -m "描述信息"

# 推送到GitHub
git push origin main

# 拉取最新代码
git pull origin main

# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout branch-name
```

### Python相关

```bash
# 安装依赖
pip install gate-api

# 查看已安装包
pip list

# 运行Python文件
python filename.py

# 进入Python交互模式
python

# 退出交互模式
exit()
```

## ⚠️ 错误处理

### 常见错误

```python
# 错误1：API密钥无效
GateApiException: {'label': 'INVALID_API_KEY', 'message': 'Invalid API key'}

# 错误2：余额不足
GateApiException: {'label': 'INSUFFICIENT_BALANCE', 'message': 'Insufficient balance'}

# 错误3：请求过于频繁
GateApiException: {'label': 'TOO_MANY_REQUESTS', 'message': 'Too many requests'}

# 解决方案：
try:
    result = spot_api.create_order(order)
except GateApiException as ex:
    logger.error(f"错误码: {ex.label}, 信息: {ex.message}")
    if ex.label == "INSUFFICIENT_BALANCE":
        logger.error("余额不足，降低交易量")
    time.sleep(5)  # 等待后重试
except ApiException as e:
    logger.error(f"API异常: {e}")
```

## 💡 优化技巧

### 1. 减少API调用

```python
# ❌ 不好的做法 - 每次循环都调用API
while True:
    ticker = spot_api.list_tickers()  # 浪费API额度
    time.sleep(1)

# ✅ 好的做法 - 缓存数据
cache_time = 0
cache_data = None
while True:
    if time.time() - cache_time > 10:
        cache_data = spot_api.list_tickers()
        cache_time = time.time()
    time.sleep(1)
```

### 2. 使用Decimal处理浮点数

```python
# ❌ 精度问题
price = 0.1 + 0.2  # 0.30000000000000004

# ✅ 使用Decimal
from decimal import Decimal as D
price = D("0.1") + D("0.2")  # D('0.3')
```

### 3. 异步请求（高级）

```python
# Gate API支持异步请求
result = spot_api.create_order(order, async_req=True)
# result是一个Thread对象
order_data = result.get()  # 等待返回结果
```

## 📊 监控指标

```python
# 计算ROI
roi = (sell_price - buy_price) / buy_price * 100

# 计算收益
profit = (sell_price - buy_price) * amount

# 计算胜率
win_rate = wins / total_trades * 100

# 计算风险回报比
risk_reward_ratio = (sell_price - buy_price) / (buy_price - stop_loss_price)
```

## 🔗 有用链接

| 资源 | 链接 |
|-----|-----|
| Gate官网 | https://www.gate.io |
| API文档 | https://www.gate.io/docs/apiv4 |
| Python SDK | https://github.com/gateio/gateapi-python |
| 问题反馈 | https://github.com/gateio/gateapi-python/issues |
| 官方社区 | https://discord.gg/gateio |

## 📝 笔记空间

```
// 在这里记录你的想法、改进建议等
```

---

**提示：** 本文档可以在IDE中快速查看，按 `Ctrl+K Ctrl+V` 可以预览Markdown文件
