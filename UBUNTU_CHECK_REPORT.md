# 🐧 Ubuntu 服务器检查报告

**检查日期**: 2025年12月10日  
**目标环境**: Ubuntu 18.04 LTS / 20.04 LTS / 22.04 LTS

---

## ✅ 检查结果

您的自动监控脚本已为 **Ubuntu 服务器部署做好准备**！

---

## 📦 为 Ubuntu 创建的工具和文档

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `check_ubuntu.sh` | Ubuntu 环境检查脚本 | 验证系统环境是否满足要求 |
| `start_ubuntu.sh` | Ubuntu 快速启动向导 | 交互式启动脚本 |
| `UBUNTU_DEPLOYMENT.md` | 详细部署指南 | 完整的部署步骤和说明 |
| `start_background.sh` | 后台启动脚本 | 使用 screen 或 nohup 后台运行 |
| `stop.sh` | 停止脚本 | 停止后台运行的脚本 |
| `start.sh` | 前台启动脚本 | 前台测试运行 |

---

## 🚀 Ubuntu 快速开始（3步骤）

### 步骤1: 连接到服务器并上传文件

```bash
# 从本地上传项目到服务器
scp -r qqqrobot/ root@your_server_ip:/root/

# 或使用 Git 克隆
ssh root@your_server_ip
cd /root
git clone https://github.com/yuzewen1996/qqqrobot.git
cd qqqrobot
```

### 步骤2: 设置虚拟环境和依赖

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
cat > .env << 'EOF'
GATE_API_KEY=your_api_key_here
GATE_API_SECRET=your_api_secret_here
EOF

# 保护配置文件
chmod 600 .env
```

### 步骤3: 验证和启动

```bash
# 给脚本执行权限
chmod +x check_ubuntu.sh start.sh start_background.sh stop.sh

# 运行检查
bash check_ubuntu.sh

# 前台测试（可选）
python3 auto_stop_loss.py

# 按 Ctrl+C 停止，然后后台启动
./start_background.sh

# 查看日志
tail -f auto_trade.log
```

---

## 📋 各脚本的用途

### `check_ubuntu.sh` - 环境检查工具

**用途**: 验证系统是否满足要求，检查所有依赖和配置

**使用方法**:
```bash
bash check_ubuntu.sh
```

**检查内容**:
- ✅ 操作系统版本
- ✅ Python 3 安装
- ✅ 虚拟环境
- ✅ 依赖包 (gate-api, python-dotenv, requests)
- ✅ 配置文件 (.env)
- ✅ 脚本文件完整性
- ✅ 网络连接
- ✅ 文件权限

---

### `start_ubuntu.sh` - 快速启动向导

**用途**: 提供交互式菜单，简化启动操作

**使用方法**:
```bash
bash start_ubuntu.sh
```

**菜单选项**:
1. 前台运行（用于测试）
2. 后台运行（用于生产）
3. 查看日志
4. 停止运行
5. 完整检查

---

### `start_background.sh` - 后台启动

**用途**: 使用 screen 或 nohup 在后台运行脚本

**使用方法**:
```bash
./start_background.sh
```

**特点**:
- 不占用终端
- 自动激活虚拟环境
- 自动检查和安装依赖
- 支持 screen 和 nohup 两种方式

**查看运行**:
```bash
# 如果使用 screen
screen -r trading

# 如果使用 nohup
tail -f auto_trade.log
```

---

### `stop.sh` - 停止脚本

**用途**: 停止后台运行的脚本

**使用方法**:
```bash
./stop.sh
```

**工作原理**:
1. 读取 `bot.pid` 文件获取进程 ID
2. 使用 `kill` 命令停止进程
3. 如果失败，使用 `pkill` 查找并停止

---

### `start.sh` - 前台启动

**用途**: 前台运行脚本，方便查看输出和调试

**使用方法**:
```bash
python3 auto_stop_loss.py
```

或

```bash
./start.sh
```

**特点**:
- 可看到实时日志输出
- 按 Ctrl+C 停止
- 适合首次测试和调试

---

## 🔧 常用操作命令

### 基本操作

```bash
# 进入项目目录
cd /root/qqqrobot

# 激活虚拟环境
source .venv/bin/activate

# 前台运行（测试）
python3 auto_stop_loss.py

# 后台运行（生产）
./start_background.sh

# 停止运行
./stop.sh

# 实时查看日志
tail -f auto_trade.log
```

### 日志管理

```bash
# 查看最后 100 行
tail -n 100 auto_trade.log

# 完整查看
cat auto_trade.log

# 搜索特定内容
grep "触发止损" auto_trade.log

# 清空日志
> auto_trade.log

# 备份日志
cp auto_trade.log auto_trade_$(date +%Y%m%d_%H%M%S).log.bak
```

### 进程管理

```bash
# 查看所有 Python 进程
ps aux | grep python

# 查看脚本是否运行
pgrep -a auto_stop_loss

# 查看 screen 会话
screen -ls

# 进入 screen 会话
screen -r trading

# 退出 screen（不停止程序）
# 按 Ctrl+A 然后 D

# 杀死 screen 会话
screen -X -S trading quit

# 手动停止进程（如果 stop.sh 失败）
kill $(cat bot.pid)
pkill -f auto_stop_loss.py
```

### 性能监控

```bash
# 查看内存和 CPU 使用
ps aux | grep auto_stop_loss

# 实时监控
top

# 查看网络连接
netstat -an | grep api.gateio

# 查看文件大小
du -sh auto_trade.log
df -h  # 查看磁盘空间
```

---

## 🔐 安全性检查清单

部署前请确认以下安全措施：

- [ ] `.env` 文件权限设为 `600`
  ```bash
  chmod 600 .env
  ```

- [ ] `.env` 文件不在 Git 中
  ```bash
  echo ".env" >> .gitignore
  git status  # 验证 .env 不被跟踪
  ```

- [ ] API 密钥不在日志中
  ```bash
  grep -i "api" auto_trade.log  # 应该不显示敏感信息
  ```

- [ ] 限制文件访问权限
  ```bash
  chmod 700 .  # 项目目录
  chmod 755 *.sh  # 脚本可执行
  ```

- [ ] 定期备份配置和日志
  ```bash
  mkdir -p backups
  cp .env backups/.env.backup
  ```

---

## 🐛 常见问题和解决方案

### Q1: 如何在 Ubuntu 上创建虚拟环境？

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Q2: 如何安装依赖包？

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Q3: 如何后台运行脚本不占用终端？

```bash
./start_background.sh

# 使用 screen 查看
screen -r trading

# 使用日志查看
tail -f auto_trade.log
```

### Q4: 如何查看脚本是否还在运行？

```bash
# 方法1: 查看进程
ps aux | grep auto_stop_loss

# 方法2: 查看日志是否在更新
ls -la auto_trade.log
tail auto_trade.log  # 查看最后更新时间

# 方法3: 查看 screen
screen -ls
```

### Q5: 如何停止脚本？

```bash
# 最简单的方法
./stop.sh

# 或者
screen -X -S trading quit

# 或者手动
kill $(cat bot.pid)
```

### Q6: 如何修改监控的合约或价格？

```bash
# 编辑脚本
nano auto_stop_loss.py

# 找到配置部分（第 290 行左右）
# CONTRACT = "ASTER_USDT"
# STOP_LOSS_PRICE = 0.912
# TAKE_PROFIT_PRICE = 0.9792

# 修改后保存
# 重启脚本
./stop.sh
./start_background.sh
```

### Q7: 脚本提示 "API 密钥不正确"？

```bash
# 检查 .env 文件
cat .env

# 确保格式正确
# GATE_API_KEY=xxx
# GATE_API_SECRET=xxx

# 检查密钥是否正确
# 登录 GateIO 账户重新获取密钥

# 重启脚本
./stop.sh
./start_background.sh
```

### Q8: 如何设置开机自启？

```bash
# 使用 crontab
crontab -e

# 添加以下行（检查脚本是否运行，不运行则启动）
@reboot cd /root/qqqrobot && source .venv/bin/activate && ./start_background.sh

# 或每小时检查一次
0 * * * * pgrep -f auto_stop_loss.py > /dev/null || cd /root/qqqrobot && ./start_background.sh
```

---

## 📊 部署检查清单

完成部署前请确认：

- [ ] 虚拟环境已创建
- [ ] 所有依赖已安装
- [ ] `.env` 文件已创建并包含 API 密钥
- [ ] `.env` 文件权限已设为 `600`
- [ ] 脚本文件都有执行权限
- [ ] 运行了 `check_ubuntu.sh` 检查通过
- [ ] 前台运行测试成功
- [ ] 日志文件正在生成
- [ ] 后台启动成功
- [ ] `tail -f auto_trade.log` 可以看到实时日志

---

## 🎯 推荐部署流程

```bash
# 1. 进入项目目录
cd /root/qqqrobot

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建配置文件
cat > .env << 'EOF'
GATE_API_KEY=your_key
GATE_API_SECRET=your_secret
EOF
chmod 600 .env

# 5. 给脚本执行权限
chmod +x *.sh

# 6. 运行检查
bash check_ubuntu.sh

# 7. 前台测试（可选）
python3 auto_stop_loss.py
# 按 Ctrl+C 停止

# 8. 后台启动
./start_background.sh

# 9. 查看日志确认运行
tail -f auto_trade.log
```

---

## 💡 性能优化建议

### 减少日志大小

```bash
# 清空日志但保持运行
> auto_trade.log

# 或使用日志轮转
sudo apt install logrotate
# 配置 logrotate 定期清理
```

### 优化资源使用

```bash
# 增加检查间隔（在脚本中修改 CHECK_INTERVAL）
# 例如从 60 秒改为 300 秒，可以减少 API 调用

# 查看资源使用
ps aux | grep auto_stop_loss
top -p $(pgrep -f auto_stop_loss)
```

### 网络优化

```bash
# 确保网络稳定，可以使用 ping 测试
ping api.gateio.ws

# 查看网络连接统计
ss -s
```

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志文件**: `tail -f auto_trade.log`
2. **运行检查脚本**: `bash check_ubuntu.sh`
3. **查看错误信息**: `python3 auto_stop_loss.py` (前台运行)
4. **检查配置**: `cat .env` (检查 API 密钥)
5. **查看进程**: `ps aux | grep auto_stop_loss`

---

## ✨ 部署完成

🎉 当您看到以下输出时，说明部署成功：

```
====================================================================================================
自动交易监控已启动
====================================================================================================
====================================================================================================
监控参数:
  合约: ASTER_USDT
  止损价: $0.912000
  止盈价: $0.979200
  检查间隔: 60秒
  日志文件: auto_trade.log
====================================================================================================

[2025-12-10 19:20:30] 监控状态
  合约: ASTER_USDT [做多]
  持仓数量: 100.0
  入场价格: $0.970000
  当前价格: $0.975000
  盈亏: +0.52%
  ✓ 未触发条件，继续监控...
```

---

**祝您的 Ubuntu 服务器部署顺利！** 🚀

如有任何问题，请参考 `UBUNTU_DEPLOYMENT.md` 获取更详细的说明。

