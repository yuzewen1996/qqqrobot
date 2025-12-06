#!/usr/bin/env python
# coding: utf-8
"""临时调试脚本 - 查看仓位API返回的完整数据"""

import os
from pathlib import Path
import gate_api

# 加载环境变量
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

api_key = os.getenv('GATE_API_KEY')
api_secret = os.getenv('GATE_API_SECRET')

# 初始化API
config = gate_api.Configuration(
    host="https://api.gateio.ws/api/v4",
    key=api_key,
    secret=api_secret
)
api = gate_api.FuturesApi(gate_api.ApiClient(config))

# 获取仓位
positions = api.list_positions(settle='usdt')

if positions:
    pos = positions[0]
    print("="*80)
    print("仓位对象的所有属性:")
    print("="*80)
    
    for attr in dir(pos):
        if not attr.startswith('_'):
            try:
                value = getattr(pos, attr)
                if not callable(value):
                    print(f"{attr}: {value}")
            except:
                pass
    
    print("\n" + "="*80)
    print("重点关注的杠杆相关字段:")
    print("="*80)
    print(f"leverage: {pos.leverage if hasattr(pos, 'leverage') else 'N/A'}")
    print(f"leverage_max: {pos.leverage_max if hasattr(pos, 'leverage_max') else 'N/A'}")
    print(f"cross_leverage_limit: {pos.cross_leverage_limit if hasattr(pos, 'cross_leverage_limit') else 'N/A'}")
    print(f"mode: {pos.mode if hasattr(pos, 'mode') else 'N/A'}")
    
    # 获取账户信息中的杠杆设置
    print("\n" + "="*80)
    print("账户信息:")
    print("="*80)
    account = api.list_futures_accounts(settle='usdt')
    print(f"cross_leverage: {account.cross_leverage if hasattr(account, 'cross_leverage') else 'N/A'}")
    
else:
    print("没有持仓")
