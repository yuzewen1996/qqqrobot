# QQQRobot - Gate.io 合约交易机器人

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Gate API](https://img.shields.io/badge/Gate-API-green)](https://www.gate.io/docs/apiv4)

QQQRobot 是一个基于 Gate.io 官方 API 的自动化合约交易机器人，支持自动止损止盈、策略扩展和多环境部署。

## ✨ 核心特性

- **自动化交易**：全自动监控行情，触发条件自动下单。
- **灵活配置**：通过 YAML 文件轻松管理交易对和风控参数。
- **模块化架构**：清晰的目录结构，易于扩展新策略。
- **多环境支持**：支持 Windows 和 Linux (Ubuntu) 部署，提供一键启动脚本。
- **完善的日志**：详细的运行日志，便于回溯和分析。

## 📂 项目结构

```
qqqrobot/
├── config/                 # 配置中心
│   ├── settings.yaml       # 策略参数、交易对、风控配置
│   └── .env                # API 密钥 (不上传 git)
├── core/                   # 核心引擎
│   ├── engine.py           # 主循环/调度器
│   ├── exchange.py         # 交易所 API 封装
│   └── notifier.py         # 日志与通知
# 项目索引（INDEX）

## 目录
1. [项目简介](#项目简介)
2. [目录结构](#目录结构)
3. [模块说明](#模块说明)
4. [使用方法](#使用方法)
5. [策略说明](#策略说明)
6. [配置说明](#配置说明)
7. [脚本说明](#脚本说明)
8. [常见问题](#常见问题)

---

## 项目简介
本项目为量化交易机器人，支持多种策略、风控、通知和多平台部署。

## 目录结构
- `main.py`：主入口
- `interactive_bot.py`：交互入口
- `auto_stop_loss.py`：止损脚本
- `core/`：核心模块
- `strategies/`：策略模块
- `data/`：数据存储
- `config/`：配置文件
- `logs/`：日志
- `scripts/`：启动/停止脚本

## 模块说明
- **core/**
  - `engine.py`：交易主引擎，调度各模块
  - `exchange.py`：对接交易所API
  - `notifier.py`：消息通知
  - `risk_control.py`：风控逻辑
- **strategies/**
  - `base_strategy.py`：所有策略基类
  - `grid.py`：网格策略
  - `stop_loss.py`：止损策略
  - `trend_following.py`：趋势跟随策略
- **data/storage.py**：数据存储与管理
- **config/settings.yaml**：全局配置

## 使用方法
1. 安装依赖：
	```bash
	pip install -r requirements.txt
	```
2. 配置参数：
	编辑 `config/settings.yaml`。
3. 启动：
	```bash
	python main.py
	```
	或使用 `scripts/` 下的脚本。

## 策略说明
- 策略需继承 `base_strategy.py`，并实现核心方法。
- 可在 `strategies/` 目录下添加自定义策略。

## 配置说明
- `settings.yaml` 包含交易所、策略、风控等参数。
- 修改后需重启服务生效。

## 脚本说明
- `scripts/ubuntu/`、`scripts/windows/` 提供一键启动/停止脚本。

## 常见问题
- 依赖未安装：请先执行 `pip install -r requirements.txt`
- 配置错误：检查 `settings.yaml` 格式
- 运行异常：查看 `logs/` 日志文件

---
如需更多帮助，请参考 GUIDE.md 或联系开发者。
│   ├── base_strategy.py    # 策略基类
│   └── stop_loss.py        # 自动止损止盈策略
├── scripts/                # 运维脚本
│   └── ubuntu/             # Linux 启动/停止脚本
├── main.py                 # 程序入口
├── interactive_bot.py      # 交互式工具 (旧版入口)
└── GUIDE.md                # 详细使用指南
```

## 🚀 快速导航

- **[使用指南 (GUIDE.md)](GUIDE.md)**：安装、配置、运行和部署的详细说明。
- **[策略配置](GUIDE.md#3-修改配置)**：如何调整止损止盈参数。
- **[服务器部署](GUIDE.md#5-服务器部署)**：如何在 Ubuntu 上后台运行机器人。

---
*本项目仅供学习和研究使用，实盘交易请注意风险。*
