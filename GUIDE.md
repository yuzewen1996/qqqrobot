# 项目指南（GUIDE）

## 项目简介
本项目是一个自动化量化交易机器人，支持多种策略（如网格、止损、趋势跟随），具备风控、通知、数据存储等模块，适用于多平台（Windows、Ubuntu）。

## 目录结构
- `main.py`：主程序入口
- `interactive_bot.py`：交互式机器人入口
- `auto_stop_loss.py`：自动止损脚本
- `core/`：核心功能模块
    - `engine.py`：交易引擎
    - `exchange.py`：交易所接口
    - `notifier.py`：通知模块
    - `risk_control.py`：风控模块
- `strategies/`：策略模块
    - `base_strategy.py`：策略基类
    - `grid.py`：网格策略
    - `stop_loss.py`：止损策略
    - `trend_following.py`：趋势跟随策略
- `data/`：数据存储模块
    - `storage.py`：数据存储实现
- `config/`：配置文件
    - `settings.yaml`：主配置文件
- `logs/`：日志目录
- `scripts/`：启动/停止脚本
    - `ubuntu/`、`windows/`：不同平台的脚本

## 快速开始
1. 安装依赖：
     ```bash
     pip install -r requirements.txt
     ```
2. 配置参数：
     - 修改 `config/settings.yaml` 以适配你的交易所和策略需求。
3. 启动机器人：
     ```bash
     python main.py
     ```
     或使用 `scripts/` 下的启动脚本。

## 策略扩展
- 新增策略请继承 `strategies/base_strategy.py`，并在 `main.py` 或相关入口注册。

## 其他说明
- 日志文件保存在 `logs/` 目录。
- 支持多平台运行，推荐使用 Ubuntu 或 Windows。
- 风控、通知等功能可在 `core/` 目录下扩展。

## 常见问题
- 配置错误：请检查 `settings.yaml` 格式及参数。
- 依赖缺失：请确保已正确安装 requirements.txt。

---
如需详细开发文档或遇到问题，请查阅 INDEX.md 或联系维护者。

### 本地运行 (Windows/Mac)

直接运行 `main.py`：

```bash
python main.py
```

如果看到类似以下的日志，说明启动成功：
```
2025-12-19 18:00:00 - INFO - 交易所 API 初始化完成
2025-12-19 18:00:00 - INFO - 已加载策略: ['StopLossStrategy']
2025-12-19 18:00:00 - INFO - 引擎启动，检查间隔: 60秒
```

### 交互式模式 (旧版功能)

如果你需要手动查询账户或下单，可以使用交互式工具：

```bash
python interactive_bot.py
```

## 5. 服务器部署 (Linux/Ubuntu)

本项目提供了方便的 Shell 脚本用于 Linux 环境部署。

### 脚本位置
所有脚本位于 `scripts/ubuntu/` 目录下。

### 常用命令

首先赋予脚本执行权限：
```bash
chmod +x scripts/ubuntu/*.sh
```

| 功能 | 命令 | 说明 |
|------|------|------|
| **启动** | `./scripts/ubuntu/start_background.sh` | 在后台启动机器人 (推荐) |
| **停止** | `./scripts/ubuntu/stop.sh` | 停止正在运行的机器人 |
| **检查** | `./scripts/ubuntu/check_ubuntu.sh` | 检查环境依赖和配置 |
| **前台运行** | `./scripts/ubuntu/start.sh` | 在当前终端运行 (用于调试) |

### 查看日志

后台运行时，日志会输出到 `logs/bot.log` (或项目根目录下的 `auto_trade.log`)。

```bash
tail -f logs/bot.log
```

## 6. 常见问题

**Q: 报错 `ValueError: 未找到 API 密钥配置`**
A: 请检查 `config/.env` 文件是否存在，且内容格式正确。确保没有多余的空格。

**Q: 报错 `ImportError: No module named ...`**
A: 请确保已运行 `pip install -r requirements.txt` 安装所有依赖。

**Q: 如何添加新策略？**
A: 
1. 在 `strategies/` 目录下新建 Python 文件（如 `my_strategy.py`）。
2. 继承 `BaseStrategy` 类并实现 `run` 方法。
3. 在 `core/engine.py` 中引入并注册你的新策略。

---
如有更多问题，请提交 Issue 或联系开发者。
