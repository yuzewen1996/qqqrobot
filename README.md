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

```text
qqqrobot/
├── config/                 # 配置中心
│   ├── settings.yaml       # 策略参数、交易对、风控配置
│   └── .env                # API 密钥 (不上传 git)
├── core/                   # 核心引擎
│   ├── engine.py           # 主循环/调度器
│   ├── exchange.py         # 交易所 API 封装
│   └── notifier.py         # 日志与通知
│   └── risk_control.py     # 风控模块
├── strategies/             # 策略仓库
│   ├── base_strategy.py    # 策略基类
│   ├── grid.py             # 网格策略
│   ├── stop_loss.py        # 自动止损止盈策略
│   └── trend_following.py  # 趋势跟随策略
├── data/                   # 数据存储
│   └── storage.py          # 数据持久化
├── scripts/                # 运维脚本
│   ├── ubuntu/             # Linux 启动/停止脚本
│   └── windows/            # Windows 启动脚本
├── logs/                   # 运行日志
├── main.py                 # 程序主入口
├── interactive_bot.py      # 交互式工具 (手动操作)
└── GUIDE.md                # 详细使用指南
```

## 🚀 快速导航

- **[使用指南 (GUIDE.md)](GUIDE.md)**：安装、配置、运行和部署的详细说明。
- **[策略配置](GUIDE.md#2-配置参数)**：如何调整止损止盈参数。
- **[服务器部署](GUIDE.md#4-服务器部署-linuxubuntu)**：如何在 Ubuntu 上后台运行机器人。

---
*本项目仅供学习和研究使用，实盘交易请注意风险。*
