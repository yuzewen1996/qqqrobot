# 🐧 Ubuntu 服务器部署指南

**适用**: Ubuntu 18.04 LTS / 20.04 LTS / 22.04 LTS 或更新版本

---

## 📋 前提条件

在开始部署之前，请确保您的 Ubuntu 服务器上已安装：

- Python 3.7+ (通常 Ubuntu 预装)
- `curl` 或 `wget` (用于下载)
- `screen` 或 `nohup` (用于后台运行)

### 检查系统环境

```bash
# 检查 Python 版本
python3 --version

# 检查是否安装了 screen
command -v screen

# 查看操作系统版本
cat /etc/os-release
```

---

## 🚀 快速部署（5分钟）

### 步骤1: 上传文件到服务器

从本地上传项目文件到服务器：

```bash
# 在本地运行
scp -r qqqrobot/ user@your_server:/root/

# 或者如果已经在服务器上，直接 git clone
ssh user@your_server
cd /root
git clone https://github.com/yuzewen1996/qqqrobot.git
cd qqqrobot
```

### 步骤2: 创建虚拟环境

```bash
# 进入项目目录
cd /root/qqqrobot

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 步骤3: 配置 API 密钥

```bash
# 创建配置文件
cat > .env << 'EOF'
GATE_API_KEY=your_api_key_here
GATE_API_SECRET=your_api_secret_here
EOF

# 设置文件权限（重要！）
chmod 600 .env
```

### 步骤4: 测试脚本

```bash
# 运行检查脚本
bash check_ubuntu.sh

# 或者直接前台运行脚本测试
python3 auto_stop_loss.py
```

### 步骤5: 后台运行

```bash
# 给脚本执行权限
chmod +x start.sh start_background.sh stop.sh

# 后台启动
./start_background.sh

# 查看运行状态
screen -r trading

# 或查看日志
tail -f auto_trade.log
```

---

## 📖 详细部署步骤

### 1️⃣ 连接到服务器

```bash
ssh root@your_server_ip
# 或
ssh -i /path/to/key.pem user@your_server_ip
```

### 2️⃣ 安装系统依赖

如果您的 Ubuntu 缺少某些包，可以安装：

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装 Python 开发环境
sudo apt install -y python3 python3-venv python3-pip

# 安装 screen (用于后台运行)
sudo apt install -y screen

# 安装其他工具
sudo apt install -y curl wget git
```

### 3️⃣ 下载项目代码

**方式 A: 使用 Git**
```bash
cd /root
git clone https://github.com/yuzewen1996/qqqrobot.git
cd qqqrobot
```

**方式 B: 使用 SCP 上传**
```bash
# 从本地运行
scp -r /local/path/qqqrobot root@your_server:/root/
```

**方式 C: 使用 wget 下载压缩包**
```bash
cd /root
wget https://github.com/yuzewen1996/qqqrobot/archive/main.zip
unzip main.zip
mv qqqrobot-main qqqrobot
cd qqqrobot
```

### 4️⃣ 设置 Python 虚拟环境

```bash
# 进入项目目录
cd /root/qqqrobot

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 验证激活成功（提示符应该显示 (.venv)）
which python
# 输出应该类似: /root/qqqrobot/.venv/bin/python

# 升级 pip、setuptools、wheel
pip install --upgrade pip setuptools wheel

# 安装项目依赖
pip install -r requirements.txt
```

### 5️⃣ 配置 API 密钥

```bash
# 创建 .env 文件
nano .env

# 粘贴以下内容（替换为实际的密钥）：
GATE_API_KEY=your_actual_api_key
GATE_API_SECRET=your_actual_api_secret

# 保存: Ctrl+O, Enter, Ctrl+X

# 或者使用 cat 命令（一行创建）：
cat > .env << 'EOF'
GATE_API_KEY=your_actual_api_key
GATE_API_SECRET=your_actual_api_secret
EOF

# 设置正确的文件权限
chmod 600 .env
```

### 6️⃣ 运行检查脚本

```bash
# 给检查脚本执行权限
chmod +x check_ubuntu.sh

# 运行检查
./check_ubuntu.sh

# 输出应该显示所有检查通过
```

### 7️⃣ 前台测试（可选）

```bash
# 在启动后台之前，先在前台测试一次
python3 auto_stop_loss.py

# 观察日志输出，确保没有错误
# 按 Ctrl+C 停止

# 检查日志文件
cat auto_trade.log
```

### 8️⃣ 后台启动

```bash
# 给启动脚本执行权限
chmod +x start.sh start_background.sh stop.sh

# 后台启动
./start_background.sh

# 等待几秒钟，让脚本启动

# 查看运行状态
ps aux | grep auto_stop_loss.py

# 查看日志
tail -f auto_trade.log

# 在 screen 中查看
screen -r trading
```

---

## 💻 常用命令

### 启动和停止

```bash
# 前台运行
python3 auto_stop_loss.py

# 后台启动
./start_background.sh

# 停止运行
./stop.sh

# 或手动停止
kill $(cat bot.pid)
```

### 查看日志

```bash
# 实时查看日志
tail -f auto_trade.log

# 查看最后 100 行
tail -n 100 auto_trade.log

# 完整查看日志
cat auto_trade.log

# 清空日志
> auto_trade.log

# 搜索特定内容
grep "触发止损" auto_trade.log
```

### 在 Screen 中操作

```bash
# 启动 screen 会话
screen -d -m -S trading python3 auto_stop_loss.py

# 进入 screen 会话
screen -r trading

# 在 screen 中：
#   查看帮助: Ctrl+A 然后 ?
#   分屏: Ctrl+A 然后 |
#   切换窗口: Ctrl+A 然后 Tab
#   退出会话: Ctrl+A 然后 D (程序继续运行)

# 列出所有 screen 会话
screen -ls

# 杀死 screen 会话
screen -X -S trading quit
```

### 虚拟环境管理

```bash
# 激活虚拟环境
source .venv/bin/activate

# 查看已安装的包
pip list

# 升级包
pip install --upgrade package_name

# 退出虚拟环境
deactivate
```

---

## ⚙️ 配置参数修改

编辑脚本来修改监控参数：

```bash
# 编辑脚本
nano auto_stop_loss.py

# 找到主程序部分（大约第290行）
# CONTRACT = "ASTER_USDT"          # 要监控的合约
# STOP_LOSS_PRICE = 0.912          # 止损价格
# TAKE_PROFIT_PRICE = 0.9792       # 止盈价格
# CHECK_INTERVAL = 60              # 检查间隔（秒）

# 修改参数后保存：Ctrl+O, Enter, Ctrl+X

# 重启脚本使配置生效
./stop.sh
./start_background.sh
```

---

## 🔒 安全建议

### 1. 保护 API 密钥

```bash
# 确保 .env 文件只有所有者可读
chmod 600 .env

# 不要将 .env 上传到 Git
echo ".env" >> .gitignore

# 检查权限
ls -la .env
# 输出应该是: -rw------- (600)
```

### 2. 定期备份日志

```bash
# 创建日志备份目录
mkdir -p logs_backup

# 备份日志
cp auto_trade.log logs_backup/auto_trade_$(date +%Y%m%d_%H%M%S).log

# 或使用计划任务（cron）
crontab -e
# 添加这一行: 0 0 * * * cd /root/qqqrobot && cp auto_trade.log logs_backup/auto_trade_$(date +\%Y\%m\%d).log
```

### 3. 监控磁盘空间

```bash
# 检查磁盘使用
df -h

# 如果日志文件过大，可以清空
# 但先备份：cp auto_trade.log auto_trade.log.bak
rm auto_trade.log

# 或使用日志轮转（logrotate）
```

---

## 🐛 故障排除

### 问题1: "Permission denied" 错误

```bash
# 解决方案：给脚本执行权限
chmod +x check_ubuntu.sh start.sh start_background.sh stop.sh

# 验证
ls -la *.sh
```

### 问题2: "No module named 'gate_api'"

```bash
# 解决方案1：激活虚拟环境
source .venv/bin/activate

# 解决方案2：重新安装依赖
pip install -r requirements.txt

# 验证
python3 -c "import gate_api; print('OK')"
```

### 问题3: "Can't open .env file"

```bash
# 检查文件是否存在
ls -la .env

# 如果不存在，创建它
cat > .env << 'EOF'
GATE_API_KEY=your_key
GATE_API_SECRET=your_secret
EOF

chmod 600 .env
```

### 问题4: 脚本启动后立即退出

```bash
# 查看错误日志
tail -f auto_trade.log

# 或者前台运行看错误信息
python3 auto_stop_loss.py
```

### 问题5: 无法连接到 API

```bash
# 检查网络连接
ping api.gateio.ws

# 检查防火墙
sudo ufw status

# 允许 HTTPS (443 端口)
sudo ufw allow 443/tcp
```

### 问题6: 找不到运行进程

```bash
# 查找所有 Python 进程
ps aux | grep python

# 或查找特定脚本
pgrep -a auto_stop_loss

# 使用 screen 列出所有会话
screen -ls
```

---

## 📊 性能监控

### 监控脚本运行状态

```bash
# 查看内存使用
ps aux | grep auto_stop_loss

# 实时监控（类似 htop）
top

# 查看网络连接
netstat -an | grep api.gateio

# 查看文件大小
du -sh auto_trade.log
```

### 设置定期检查（Cron）

```bash
# 编辑 crontab
crontab -e

# 添加定期检查任务
# 每小时检查一次脚本是否运行
0 * * * * pgrep -f auto_stop_loss.py > /dev/null || /root/qqqrobot/start_background.sh

# 每天凌晨2点清空日志
0 2 * * * > /root/qqqrobot/auto_trade.log

# 每周备份日志
0 3 * * 0 cp /root/qqqrobot/auto_trade.log /root/qqqrobot/logs_backup/auto_trade_$(date +\%Y\%m\%d).log
```

### 查看 cron 日志

```bash
# 查看 cron 执行历史
grep CRON /var/log/syslog

# 或
sudo journalctl -u cron
```

---

## 🔄 更新脚本

当有新版本时，更新代码：

```bash
# 停止运行中的脚本
./stop.sh

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖更新
pip install -r requirements.txt

# 重新启动
./start_background.sh

# 查看日志确认运行
tail -f auto_trade.log
```

---

## 📝 常见问题 FAQ

**Q: 脚本和 API 密钥保存在哪里最安全？**
A: 将 `.env` 文件存储在项目目录，设置权限为 `600`，不要上传到 Git。

**Q: 如何在多台服务器上运行？**
A: 在每台服务器上重复部署步骤，注意各自的 `.env` 配置不同。

**Q: 如何实现 24 小时不间断运行？**
A: 使用 `screen` 后台运行，并配置 `cron` 定期检查和自动重启。

**Q: 日志文件太大怎么办？**
A: 使用 `logrotate` 或定期清理：`> auto_trade.log`

**Q: 如何监控多个合约？**
A: 运行多个脚本实例，每个使用不同的配置文件：`python3 auto_stop_loss.py`

---

## ✨ 最终检查清单

部署完成前，请确认以下各项：

- [ ] Python 3.7+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 依赖包已安装 (`pip list` 显示 `gate-api`)
- [ ] `.env` 文件已创建并包含 API 密钥
- [ ] `.env` 文件权限为 `600` (`chmod 600 .env`)
- [ ] 脚本文件有执行权限 (`chmod +x *.sh`)
- [ ] 运行了检查脚本 (`bash check_ubuntu.sh`)
- [ ] 前台测试成功，无错误
- [ ] 后台启动成功
- [ ] 日志文件正在生成 (`tail -f auto_trade.log`)

---

## 🎯 快速参考命令

```bash
# 进入项目目录
cd /root/qqqrobot

# 激活环境并启动
source .venv/bin/activate && python3 auto_stop_loss.py

# 后台启动
./start_background.sh

# 查看日志
tail -f auto_trade.log

# 停止
./stop.sh

# 完整检查
bash check_ubuntu.sh
```

---

**祝部署顺利！** 🚀

如有问题，请查看日志文件 `auto_trade.log` 获取更多信息。

