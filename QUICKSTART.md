# 🚀 v2_improved.py - 快速启动指南

## 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

## 2️⃣ 配置 API 密钥

**选项 A: 使用 .env 文件（推荐本地开发）**

```bash
cp .env.example .env
# 编辑 .env，填入你的实际 API 密钥
```

**选项 B: 使用环境变量（推荐服务器部署）**

```bash
export GATE_API_KEY="your_api_key_here"
export GATE_API_SECRET="your_api_secret_here"
```

## 3️⃣ 修改交易参数（可选）

编辑 `v2_improved.py` 中的 `TradingConfig` 类：

```python
class TradingConfig:
    # ...
    CURRENCY_PAIR = "BTC_USDT"          # 交易对
    TARGET_BUY_PRICE = D("50000")       # 买入目标价
    TARGET_SELL_PRICE = D("60000")      # 卖出目标价
    BUY_AMOUNT = D("0.001")             # 买入数量（BTC）
    CHECK_INTERVAL = 10                 # 检查间隔（秒）
    USE_TESTNET = False                 # 是否使用测试网
```

## 4️⃣ 运行机器人

```bash
# 本地开发（使用 .env）
python v2_improved.py

# 或在服务器上（使用环境变量）
GATE_API_KEY=xxx GATE_API_SECRET=xxx python v2_improved.py
```

## 5️⃣ 查看日志

- **实时日志**: 运行时在控制台查看
- **日志文件**: 查看 `trading_bot.log`

## 🧪 测试模式

在测试网上运行（不实际交易）：

```python
# 编辑 v2_improved.py
USE_TESTNET = True
```

然后运行即可。

## ⚠️ 首次运行检查清单

- [ ] 已安装依赖：`pip install -r requirements.txt`
- [ ] 已设置 API 密钥（.env 或环境变量）
- [ ] 已确认交易参数（交易对、价格、数量）
- [ ] 已确认账户余额充足
- [ ] 已在测试网测试过（推荐）
- [ ] 已检查 `trading_bot.log` 确认无错误

## 🛑 停止机器人

按 `Ctrl+C` 优雅停止。

## 📊 典型输出示例

```
2025-12-05 10:30:45 - INFO - ==================================================
2025-12-05 10:30:45 - INFO - 交易机器人启动
2025-12-05 10:30:45 - INFO - ==================================================
2025-12-05 10:30:45 - INFO - 交易对: BTC_USDT
2025-12-05 10:30:45 - INFO - 买入目标价: 50000 USDT
2025-12-05 10:30:45 - INFO - 卖出目标价: 60000 USDT
2025-12-05 10:30:46 - INFO - API客户端已初始化 - 模式: 实盘
2025-12-05 10:30:46 - INFO - --------------------------------------------------
2025-12-05 10:30:48 - INFO - 当前价格: 52345.67 USDT | 24h高: 53000 | 24h低: 51000
2025-12-05 10:30:48 - INFO - 账户余额 - USDT: 1000.50 | BTC: 0.001
2025-12-05 10:30:48 - INFO - 未满足交易条件，继续等待...
2025-12-05 10:30:48 - INFO - 待处理订单: 0笔
2025-12-05 10:30:48 - INFO - 等待 10 秒后进行下一次检查...
```

## 🆘 常见问题

**Q: 运行时报 `ValueError: 未找到 API 密钥配置`**
- A: 确认已设置 GATE_API_KEY 和 GATE_API_SECRET（通过 .env 或环境变量）

**Q: 机器人启动了但没有执行交易**
- A: 检查当前价格是否满足 TARGET_BUY_PRICE 或 TARGET_SELL_PRICE 条件

**Q: 如何切换到测试网**
- A: 设置 `USE_TESTNET = True`

**Q: 日志文件在哪里**
- A: 在项目根目录的 `trading_bot.log`

---

**祝交易愉快！** 🎉
