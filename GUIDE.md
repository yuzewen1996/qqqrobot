# QQQRobot 使用指南 (GUIDE)

本指南将帮助你从零开始安装、配置、运行和部署 QQQRobot。

## 1. 环境准备

### 系统要求
- **操作系统**: Windows 10/11, macOS, 或 Linux (Ubuntu 20.04+ 推荐)
- **Python**: 版本 3.8 或更高

### 安装步骤

1. **克隆或下载代码**
   确保你已经获取了项目的最新代码。

2. **安装依赖**
   在项目根目录下打开终端，运行以下命令安装所需的 Python 库：
   ```bash
   pip install -r requirements.txt
   ```

## 2. 配置参数

所有配置文件均位于 `config/` 目录下。

### 2.1 API 密钥配置 (.env)
在 `config/` 目录下创建一个名为 `.env` 的文件（如果不存在），并填入你的 Gate.io API 密钥：
```env
GATE_API_KEY=your_api_key_here
GATE_API_SECRET=your_api_secret_here
```
> **注意**: 请勿将 `.env` 文件提交到版本控制系统（如 Git），以防密钥泄露。

### 2.2 策略与风控配置 (settings.yaml)
编辑 `config/settings.yaml` 文件以调整运行参数：

- **exchange**: 设置交易所相关参数（如是否使用测试网）。
- **strategies**: 启用或禁用策略，并设置具体参数（如止损比例、网格数量）。
- **risk_control**: 设置全局风控参数（如最大持仓、单日最大亏损）。

## 3. 本地运行 (Windows/Mac)

### 启动主程序
配置完成后，直接运行 `main.py` 启动机器人：

```bash
python main.py
```

如果看到类似以下的日志，说明启动成功：
```text
2025-12-19 18:00:00 - INFO - 交易所 API 初始化完成
2025-12-19 18:00:00 - INFO - 已加载策略: ['StopLossStrategy']
2025-12-19 18:00:00 - INFO - 引擎启动，检查间隔: 60秒
```

### 交互式模式
如果你需要手动查询账户余额、当前持仓或手动下单，可以使用交互式工具：

```bash
python interactive_bot.py
```

## 4. 服务器部署 (Linux/Ubuntu)

本项目提供了方便的 Shell 脚本用于 Linux 环境部署，位于 `scripts/ubuntu/` 目录下。

### 4.1 赋予执行权限
首次部署时，需要赋予脚本执行权限：
```bash
chmod +x scripts/ubuntu/*.sh
```

### 4.2 常用命令

| 功能 | 命令 | 说明 |
|------|------|------|
| **后台启动** | `./scripts/ubuntu/start_background.sh` | 推荐方式，即使断开 SSH 连接也会继续运行 |
| **停止运行** | `./scripts/ubuntu/stop.sh` | 安全停止正在运行的机器人 |
| **环境检查** | `./scripts/ubuntu/check_ubuntu.sh` | 检查 Python 环境和依赖是否就绪 |
| **前台调试** | `./scripts/ubuntu/start.sh` | 在当前终端运行，Ctrl+C 可退出 |

### 4.3 查看日志
后台运行时，日志会输出到 `logs/bot.log`。使用以下命令实时查看：

```bash
tail -f logs/bot.log
```

## 5. 策略开发

如果你需要开发新的交易策略，请遵循以下步骤：

1. **创建文件**: 在 `strategies/` 目录下新建 Python 文件（例如 `my_strategy.py`）。
2. **继承基类**: 导入并继承 `BaseStrategy` 类。
3. **实现逻辑**: 重写 `run()` 方法，编写你的交易逻辑。
4. **注册策略**: 在 `main.py` 或配置文件中启用你的新策略。

示例代码：
```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def run(self):
        # 获取行情
        ticker = self.exchange.get_ticker(self.symbol)
        # 你的交易逻辑...
```

## 6. 常见问题 (FAQ)

**Q: 报错 `ValueError: 未找到 API 密钥配置`**
A: 请检查 `config/.env` 文件是否存在，且内容格式正确（KEY=VALUE）。

**Q: 报错 `ImportError: No module named ...`**
A: 请确保已运行 `pip install -r requirements.txt` 安装所有依赖。

**Q: 如何修改交易对？**
A: 在 `config/settings.yaml` 中找到 `symbol` 字段进行修改（例如 `BTC_USDT`）。

---
如需更多帮助，请联系项目维护者。
