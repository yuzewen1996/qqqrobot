#!/usr/bin/env python
# coding: utf-8
"""
快速查询账户仓位信息
"""

import os
import sys
from pathlib import Path
from decimal import Decimal as D

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from v2_improved import GateIOTrader, TradingConfig

def main():
    try:
        config = TradingConfig()
        trader = GateIOTrader(config)
        
        print("\n" + "="*60)
        print("📊 账户仓位信息")
        print("="*60)
        
        position = trader.get_position_info()
        
        if position:
            print(f"\n交易对: {position['base_currency']}/{position['quote_currency']}")
            print(f"当前价格: {position['current_price']} USDT\n")
            
            print(f"💰 {position['base_currency']} (基础币):")
            print(f"   可用: {position['base_available']}")
            print(f"   冻结: {position['base_locked']}")
            print(f"   总计: {position['base_total']}")
            print(f"   价值: {position['base_position_value']} USDT\n")
            
            print(f"💵 {position['quote_currency']} (计价币):")
            print(f"   可用: {position['quote_available']}")
            print(f"   冻结: {position['quote_locked']}")
            print(f"   总计: {position['quote_total']}\n")
            
            print(f"📈 总资产价值: {position['total_assets']} USDT")
            print(f"📊 仓位占比: {position['position_ratio']:.2%}")
            print("="*60 + "\n")
        else:
            print("❌ 无法获取仓位信息")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == '__main__':
    main()
