# QQQ Robot - Gate.io 交易机器人

## ⚠️ 安全提示

**永远不要在代码中硬编码 API 密钥！**

已更新 `v1.py` 以从环境变量或 `.env` 文件安全加载配置。

## 使用方式

### 方式 1: 环境变量（推荐在服务器上使用）

```bash
export GATE_API_KEY="your_api_key_here"
export GATE_API_SECRET="your_api_secret_here"
python v1.py
```

### 方式 2: .env 文件（本地开发使用）

1. 复制示例文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env`，填入你的 API 密钥：
   ```
   GATE_API_KEY=your_actual_api_key
   GATE_API_SECRET=your_actual_api_secret
   ```

3. 运行机器人：
   ```bash
   python v1.py
   ```

**重要：** `.env` 已在 `.gitignore` 中，不会被提交到 Git。

### 方式 3: 在服务器上通过 systemd 环境文件

编辑 `/etc/default/qqqrobot`：
```
GATE_API_KEY=your_api_key
GATE_API_SECRET=your_api_secret
```

然后在 systemd 服务文件中引用：
```ini
[Service]
EnvironmentFile=/etc/default/qqqrobot
ExecStart=/usr/bin/python3 /path/to/v1.py
```

## 已有的硬编码密钥

⚠️ **你之前硬编码的 API 密钥已被公开在代码中，建议立即：**

1. **在 Gate.io 网站上删除旧密钥** - 登录账户 → API → 删除该密钥
2. **生成新的 API 密钥** - 创建新密钥并设置正确的权限
3. **更新本地配置** - 使用 `.env` 文件或环境变量存放新密钥
4. **如果已推送到 GitHub**：
   - 运行 `git log` 或使用工具如 `BFG Repo-Cleaner` 删除历史记录中的密钥
   - 或重新创建私有仓库

## 配置说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `GATE_API_KEY` | Gate.io API Key | 必填 |
| `GATE_API_SECRET` | Gate.io API Secret | 必填 |
| `GATE_HOST` | Gate.io API 端点 | https://api.gateio.ws/api/v4（实盘） |

## 测试配置

测试你的配置是否正确加载：
```bash
python -c "from v1 import API_KEY; print('API Key loaded:', 'Yes' if API_KEY else 'No')"
```

## 其他安全建议

- 定期轮换 API 密钥
- 为 API 密钥设置最小必需权限（仅允许交易，不允许提币）
- 使用 IP 白名单限制 API 访问
- 不要在日志或监控系统中记录敏感信息
- 在生产环境使用密钥管理工具（如 HashiCorp Vault、AWS Secrets Manager）
