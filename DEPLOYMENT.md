# 服务器部署指南

## 📦 部署步骤

### 1. 上传文件到服务器

将以下文件上传到服务器：
```
- auto_stop_loss.py           # 主程序
- gatekey.env 或 .env         # API密钥配置文件
- requirements.txt            # 依赖包列表
```

### 2. 服务器环境准备

#### Linux服务器 (推荐 Ubuntu/Debian/CentOS)

```bash
# 更新系统
sudo apt update  # Ubuntu/Debian
# 或
sudo yum update  # CentOS

# 安装Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# 创建工作目录
mkdir -p ~/qqqrobot
cd ~/qqqrobot
```

### 3. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖包
pip install gate-api python-dotenv

# 或者使用requirements.txt
pip install -r requirements.txt
```

### 4. 配置API密钥

创建配置文件 `gatekey.env`:
```bash
nano ~/qqqrobot/gatekey.env
```

输入以下内容（替换为你的真实密钥）:
```
GATE_API_KEY=your_api_key_here
GATE_API_SECRET=your_api_secret_here
```

保存并设置权限：
```bash
chmod 600 ~/qqqrobot/gatekey.env
```

### 5. 测试运行

```bash
# 前台测试运行
python3 auto_stop_loss.py
```

如果看到类似输出，说明运行正常：
```
====================================================================================================
自动交易监控已启动
====================================================================================================
监控参数:
  合约: ASTER_USDT
  止损价: $0.912000
  止盈价: $0.979200
  检查间隔: 60秒
====================================================================================================
```

### 6. 后台运行（重要！）

#### 方法1: 使用 nohup (简单)

```bash
# 后台运行并记录日志
nohup python3 auto_stop_loss.py > output.log 2>&1 &

# 查看进程
ps aux | grep auto_stop_loss

# 查看日志
tail -f auto_trade.log
tail -f output.log

# 停止程序
kill <进程ID>
```

#### 方法2: 使用 screen (推荐)

```bash
# 安装screen
sudo apt install screen -y

# 创建新会话
screen -S trading_bot

# 在screen中运行
python3 auto_stop_loss.py

# 按 Ctrl+A 然后按 D 退出screen（程序继续运行）

# 重新连接
screen -r trading_bot

# 查看所有会话
screen -ls

# 停止程序：重新连接后按 Ctrl+C
```

#### 方法3: 使用 systemd (专业)

创建服务文件：
```bash
sudo nano /etc/systemd/system/trading_bot.service
```

输入以下内容：
```ini
[Unit]
Description=Auto Trading Bot
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/qqqrobot
Environment="PATH=/home/你的用户名/qqqrobot/venv/bin"
ExecStart=/home/你的用户名/qqqrobot/venv/bin/python3 auto_stop_loss.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start trading_bot

# 设置开机自启
sudo systemctl enable trading_bot

# 查看状态
sudo systemctl status trading_bot

# 查看日志
sudo journalctl -u trading_bot -f

# 停止服务
sudo systemctl stop trading_bot
```

### 7. 监控和日志

```bash
# 实时查看日志
tail -f ~/qqqrobot/auto_trade.log

# 查看最近100行日志
tail -n 100 ~/qqqrobot/auto_trade.log

# 搜索特定内容
grep "触发止损" ~/qqqrobot/auto_trade.log
grep "触发止盈" ~/qqqrobot/auto_trade.log
```

### 8. 修改监控参数

编辑 `auto_stop_loss.py` 文件的配置区域：
```bash
nano auto_stop_loss.py
```

找到这部分并修改：
```python
# ============ 配置区域 - 请根据实际情况修改 ============

# 合约配置
CONTRACT = "ASTER_USDT"  # 要监控的合约

# 止损止盈价格
STOP_LOSS_PRICE = 0.912    # 止损价
TAKE_PROFIT_PRICE = 0.9792  # 止盈价

# 检查间隔（秒）
CHECK_INTERVAL = 60  # 每60秒检查一次

# ============ 配置区域结束 ============
```

修改后重启程序。

## 🔒 安全建议

1. **保护API密钥**
   ```bash
   chmod 600 gatekey.env
   ```

2. **定期检查日志**
   ```bash
   # 每天检查一次
   crontab -e
   # 添加：0 9 * * * tail -n 50 ~/qqqrobot/auto_trade.log | mail -s "Trading Log" your@email.com
   ```

3. **设置API权限**
   - 只给API合约交易权限
   - 禁用提现权限
   - 设置IP白名单

4. **备份配置**
   ```bash
   cp gatekey.env gatekey.env.backup
   ```

## 📊 故障排查

### 问题1: 无法连接API
```bash
# 测试网络
ping api.gateio.ws

# 检查防火墙
sudo ufw status
```

### 问题2: 程序崩溃
```bash
# 查看错误日志
tail -n 100 auto_trade.log

# 检查Python版本
python3 --version  # 需要3.8+
```

### 问题3: 找不到持仓
- 检查合约名称是否正确
- 确认API密钥权限
- 查看日志中的错误信息

## 🎯 Windows服务器

如果使用Windows服务器：

```powershell
# 使用任务计划程序或创建Windows服务
# 或者简单后台运行：
Start-Process -FilePath "python" -ArgumentList "auto_stop_loss.py" -WindowStyle Hidden

# 使用NSSM创建Windows服务
nssm install TradingBot "D:\qqqrobot\.venv\Scripts\python.exe" "D:\qqqrobot\auto_stop_loss.py"
nssm start TradingBot
```

## 📞 紧急情况处理

如果需要立即停止程序：

```bash
# 查找进程
ps aux | grep auto_stop_loss

# 强制停止
kill -9 <进程ID>

# 或停止所有Python进程（谨慎使用）
pkill -9 python3
```

## ✅ 验证清单

部署前确认：
- [ ] API密钥配置正确
- [ ] 合约名称正确
- [ ] 止损止盈价格合理
- [ ] 服务器网络通畅
- [ ] Python依赖已安装
- [ ] 日志文件可写入
- [ ] 后台运行方式已选择
