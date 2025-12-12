# 🖥️ Windows vs Ubuntu 部署对比指南

---

## 📋 快速对比表

| 功能 | Windows | Ubuntu/Linux |
|------|---------|-------------|
| **配置方式** | PowerShell 脚本 | Bash 脚本 |
| **启动命令** | `.\start_background.ps1` | `./start_background.sh` |
| **停止命令** | `.\stop.ps1` | `./stop.sh` |
| **查看日志** | `Get-Content auto_trade.log -Tail 100` | `tail -f auto_trade.log` |
| **后台运行方式** | 隐藏窗口进程 | Screen 或 nohup |
| **虚拟环境激活** | `.\.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| **Python 命令** | `python` 或 `python.exe` | `python3` |
| **权限管理** | 文件属性 | `chmod` 命令 |
| **进程查看** | 任务管理器或 `tasklist` | `ps aux` 或 `pgrep` |
| **进程停止** | `taskkill` | `kill` 或 `pkill` |

---

## 🚀 部署流程对比

### Windows 部署流程

```powershell
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建配置文件
# 手动创建 .env 文件，内容：
# GATE_API_KEY=your_key
# GATE_API_SECRET=your_secret

# 5. 运行检查
python check_auto_monitor.py

# 6. 前台测试
python auto_stop_loss.py

# 7. 后台启动
.\start_background.ps1

# 8. 查看日志
Get-Content auto_trade.log -Tail 100 -Wait

# 9. 停止
.\stop.ps1
```

### Ubuntu 部署流程

```bash
# 1. 创建虚拟环境
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建配置文件
cat > .env << 'EOF'
GATE_API_KEY=your_key
GATE_API_SECRET=your_secret
EOF
chmod 600 .env

# 5. 运行检查
bash check_ubuntu.sh

# 6. 前台测试
python3 auto_stop_loss.py

# 7. 后台启动
./start_background.sh

# 8. 查看日志
tail -f auto_trade.log

# 9. 停止
./stop.sh
```

---

## 📁 文件结构对比

### Windows 相关文件
```
qqqrobot/
├── start.bat                  # Batch 前台启动脚本
├── start_background.bat       # Batch 后台启动脚本
├── start_background.ps1       # PowerShell 后台启动
├── stop.ps1                   # PowerShell 停止脚本
├── check_auto_monitor.py      # Windows 检查工具 ✨
├── test_auto_monitor.py       # Windows 测试工具 ✨
├── quick_start_check.py       # Windows 快速启动 ✨
├── SCRIPT_CHECK_REPORT.md     # Windows 检查报告 ✨
├── CHECK_COMPLETE.md          # Windows 完成报告 ✨
└── auto_stop_loss.py          # 主脚本
```

### Ubuntu 相关文件
```
qqqrobot/
├── start.sh                   # Bash 前台启动脚本
├── start_background.sh        # Bash 后台启动脚本
├── stop.sh                    # Bash 停止脚本
├── start_ubuntu.sh            # Ubuntu 快速启动向导 ✨
├── check_ubuntu.sh            # Ubuntu 检查工具 ✨
├── UBUNTU_DEPLOYMENT.md       # Ubuntu 部署指南 ✨
├── UBUNTU_CHECK_REPORT.md     # Ubuntu 检查报告 ✨
└── auto_stop_loss.py          # 主脚本（相同）
```

✨ = 新创建的文件

---

## 🎯 Windows 用户指南

### 你需要的文件：
1. **`start_background.ps1`** - 后台启动脚本
2. **`stop.ps1`** - 停止脚本
3. **`check_auto_monitor.py`** - 环境检查工具
4. **`SCRIPT_CHECK_REPORT.md`** - 详细报告
5. **`CHECK_COMPLETE.md`** - 快速参考

### 快速启动步骤：
```powershell
# 1. 打开 PowerShell（Win+R 输入 powershell）

# 2. 进入项目目录
cd d:\codee\qqqrobot

# 3. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 4. 后台启动
.\start_background.ps1

# 5. 查看日志
Get-Content auto_trade.log -Tail 100 -Wait
```

### 日常操作：
```powershell
# 停止脚本
.\stop.ps1

# 查看进程
Get-Process python

# 清空日志
Clear-Content auto_trade.log
```

---

## 🐧 Ubuntu 用户指南

### 你需要的文件：
1. **`start_background.sh`** - 后台启动脚本
2. **`stop.sh`** - 停止脚本
3. **`check_ubuntu.sh`** - 环境检查工具
4. **`UBUNTU_DEPLOYMENT.md`** - 详细部署指南
5. **`UBUNTU_CHECK_REPORT.md`** - 快速参考

### 快速启动步骤：
```bash
# 1. SSH 连接到服务器
ssh root@your_server_ip

# 2. 进入项目目录
cd /root/qqqrobot

# 3. 给脚本执行权限（首次）
chmod +x *.sh

# 4. 后台启动
./start_background.sh

# 5. 查看日志
tail -f auto_trade.log
```

### 日常操作：
```bash
# 停止脚本
./stop.sh

# 查看进程
ps aux | grep auto_stop_loss

# 清空日志
> auto_trade.log
```

---

## 🔧 常见任务对比

### 任务1: 查看脚本是否运行

**Windows**
```powershell
Get-Process python
# 或
tasklist | findstr auto_stop_loss
```

**Ubuntu**
```bash
ps aux | grep auto_stop_loss
# 或
pgrep -a auto_stop_loss
```

### 任务2: 查看实时日志

**Windows**
```powershell
Get-Content auto_trade.log -Tail 100 -Wait
# 或用记事本打开
notepad auto_trade.log
```

**Ubuntu**
```bash
tail -f auto_trade.log
# 或
less auto_trade.log
```

### 任务3: 修改监控参数

**两个系统都相同**
```
编辑 auto_stop_loss.py
修改 CONTRACT、STOP_LOSS_PRICE、TAKE_PROFIT_PRICE
保存文件
重启脚本
```

### 任务4: 后台运行

**Windows**
```powershell
.\start_background.ps1
# 查看日志了解运行状态
tail -f auto_trade.log  # 如果安装了 git bash
```

**Ubuntu**
```bash
./start_background.sh
# 查看日志了解运行状态
tail -f auto_trade.log
```

### 任务5: 停止运行

**Windows**
```powershell
.\stop.ps1
# 或手动
taskkill /IM python.exe /F
```

**Ubuntu**
```bash
./stop.sh
# 或手动
kill $(cat bot.pid)
pkill -f auto_stop_loss
```

---

## 💻 虚拟环境对比

### Windows 虚拟环境

```powershell
# 创建
python -m venv .venv

# 激活
.\.venv\Scripts\Activate.ps1

# 如果出现权限错误，运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 安装依赖
pip install -r requirements.txt

# 退出
deactivate
```

### Ubuntu 虚拟环境

```bash
# 创建
python3 -m venv .venv

# 激活
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 退出
deactivate
```

---

## 🔐 配置文件对比

### Windows (.env 创建方式)

```powershell
# 方法1: 使用 PowerShell
@"
GATE_API_KEY=your_key
GATE_API_SECRET=your_secret
"@ | Out-File -Encoding UTF8 .env

# 方法2: 使用记事本
notepad .env
# 手动输入内容
```

### Ubuntu (.env 创建方式)

```bash
# 方法1: 使用 cat
cat > .env << 'EOF'
GATE_API_KEY=your_key
GATE_API_SECRET=your_secret
EOF

# 方法2: 使用 nano
nano .env
# 手动输入内容，Ctrl+O 保存，Ctrl+X 退出

# 设置权限
chmod 600 .env
```

---

## 📊 性能对比

### 资源占用

| 方面 | Windows | Ubuntu |
|------|---------|--------|
| 内存占用 | 较高（隐藏进程还占用） | 较低（轻量级） |
| CPU 占用 | 中等 | 低 |
| 启动时间 | 稍长 | 快速 |
| 稳定性 | 一般（需定期重启） | 高（可运行数月） |
| 24小时运行 | 需要特别配置 | 原生支持 |

---

## ✅ 两个系统的脚本检查

### Windows 脚本检查

已为 Windows 创建的工具：
- ✅ `check_auto_monitor.py` - 6项全面检查
- ✅ `test_auto_monitor.py` - 功能测试
- ✅ `quick_start_check.py` - 快速检查

运行检查：
```powershell
python check_auto_monitor.py
```

### Ubuntu 脚本检查

已为 Ubuntu 创建的工具：
- ✅ `check_ubuntu.sh` - 9项全面检查
- ✅ `start_ubuntu.sh` - 交互式菜单

运行检查：
```bash
bash check_ubuntu.sh
```

---

## 🎓 选择建议

### 选择 Windows 如果：
- ✅ 你在本地开发和测试
- ✅ 你偏好图形界面
- ✅ 你需要频繁修改配置
- ✅ 你的电脑就是交易电脑

### 选择 Ubuntu/Linux 如果：
- ✅ 你使用服务器部署（推荐）
- ✅ 你需要 24/7 不间断运行
- ✅ 你希望稳定性更高
- ✅ 你想节省资源
- ✅ 你有多个交易任务需要并行运行

---

## 🚀 两个系统都适用的功能

以下功能在两个系统上都相同：

| 功能 | Windows | Ubuntu |
|------|---------|--------|
| 自动止损 | ✅ | ✅ |
| 自动止盈 | ✅ | ✅ |
| 市价平仓 | ✅ | ✅ |
| 实时监控 | ✅ | ✅ |
| 日志记录 | ✅ | ✅ |
| 错误处理 | ✅ | ✅ |
| 灵活配置 | ✅ | ✅ |

---

## 📞 按系统获取帮助

### Windows 用户请查看：
- `SCRIPT_CHECK_REPORT.md` - 完整报告
- `CHECK_COMPLETE.md` - 快速参考

### Ubuntu 用户请查看：
- `UBUNTU_DEPLOYMENT.md` - 详细指南
- `UBUNTU_CHECK_REPORT.md` - 检查报告

### 两个系统的用户都可查看：
- `QUICKSTART_AUTO.md` - 自动止损快速开始
- `GUIDE.md` - 完整功能指南
- `README.md` - 项目概览

---

## ✨ 总结

无论您使用 Windows 还是 Ubuntu，脚本的**核心功能完全相同**，区别只在于：

1. **脚本语言** (PowerShell vs Bash)
2. **后台运行方式** (进程 vs Screen)
3. **命令语法** (PowerShell vs Bash)

已为两个系统都创建了相应的工具和文档，可以直接按照指南使用。

**建议**：如果这是生产环境，强烈推荐使用 **Ubuntu 服务器**，因为稳定性更高，适合 24 小时不间断运行。

---

**祝您部署顺利！** 🎯

