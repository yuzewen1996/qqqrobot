#!/usr/bin/env python
# coding: utf-8
"""
查询合约仓位信息
支持：期货、永续合约等衍生品交易
"""

import os
import logging
from pathlib import Path
from decimal import Decimal as D
import gate_api
from gate_api.exceptions import ApiException, GateApiException

# ============ 配置加载 ============
def load_env_config():
    """从环境变量或 .env 文件加载配置"""
    env_paths = [
        Path(__file__).parent / ".env",
        Path("C:/Users/admin/Desktop/gatekey.env"),
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
            break
    
    api_key = os.getenv('GATE_API_KEY')
    api_secret = os.getenv('GATE_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError("未找到 API 密钥配置")
    
    return api_key, api_secret

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============ 合约仓位查询类 ============
class FuturesPositionQuery:
    """期货/永续合约仓位查询"""
    
    def __init__(self, api_key: str, api_secret: str):
        configuration = gate_api.Configuration(
            host="https://api.gateio.ws/api/v4",
            key=api_key,
            secret=api_secret
        )
        self.api_client = gate_api.ApiClient(configuration)
        self.futures_api = gate_api.FuturesApi(self.api_client)
        logger.info("期货 API 客户端已初始化")
    
    def get_account_leverage(self, settle: str = 'usdt'):
        """获取账户杠杆设置"""
        try:
            account = self.futures_api.list_futures_accounts(settle=settle)
            if account:
                # 全仓模式下的杠杆
                cross_leverage = getattr(account, 'cross_leverage', None)
                logger.info(f"[INFO] {settle.upper()} 账户全仓杠杆: {cross_leverage}")
                return cross_leverage
        except Exception as e:
            logger.error(f"[ERROR] 获取账户杠杆失败: {e}")
        return None
    
    def get_all_positions(self, settle: str = 'usdt'):
        """获取指定结算货币的所有合约仓位 (settle: usdt / btc)"""
        try:
            logger.info(f"\n[*] 获取 {settle.upper()} 所有合约仓位...")
            
            # 获取账户杠杆(用于全仓模式)
            account_leverage = self.get_account_leverage(settle)
            
            positions = self.futures_api.list_positions(settle=settle)
            
            if not positions:
                logger.info(f"   {settle.upper()} 无持仓")
                return []
            
            result = []
            for pos in positions:
                # 只返回有持仓的合约（size != 0）- size 是字符串，需要转换为数字比较
                try:
                    size_float = float(pos.size) if pos.size else 0
                    if abs(size_float) == 0:
                        continue
                except (ValueError, TypeError):
                    continue
                
                # 打印所有可能包含杠杆的字段
                logger.info(f"[DEBUG] 合约 {pos.contract}:")
                logger.info(f"  - leverage: {pos.leverage}")
                logger.info(f"  - leverage_max: {pos.leverage_max if hasattr(pos, 'leverage_max') else 'N/A'}")
                logger.info(f"  - cross_leverage_limit: {pos.cross_leverage_limit if hasattr(pos, 'cross_leverage_limit') else 'N/A'}")
                logger.info(f"  - margin: {pos.margin}")
                logger.info(f"  - size: {pos.size}")
                logger.info(f"  - mark_price: {pos.mark_price}")
                logger.info(f"  - mode: {pos.mode if hasattr(pos, 'mode') else 'N/A'}")
                
                # 安全处理杠杆字段 - 可能是字符串或数字
                try:
                    leverage_val = D(str(pos.leverage)) if pos.leverage and str(pos.leverage) != '0' else D(0)
                except:
                    leverage_val = D(0)
                
                # 获取实际杠杆 - 优先级顺序:
                # 1. API 返回的 leverage (逐仓模式下有值)
                # 2. cross_leverage_limit (全仓模式下的合约杠杆限制)
                # 3. 账户全仓杠杆
                final_leverage = D(0)
                
                if leverage_val > 0:
                    # 逐仓模式下 API 会返回 leverage
                    final_leverage = leverage_val
                    logger.info(f"[INFO] 合约 {pos.contract} 使用 API leverage: {float(final_leverage)}x")
                elif hasattr(pos, 'cross_leverage_limit') and pos.cross_leverage_limit:
                    # 全仓模式下使用 cross_leverage_limit
                    try:
                        final_leverage = D(str(pos.cross_leverage_limit))
                        logger.info(f"[INFO] 合约 {pos.contract} 使用 cross_leverage_limit: {float(final_leverage)}x")
                    except:
                        pass
                elif account_leverage:
                    # 使用账户全仓杠杆
                    try:
                        final_leverage = D(str(account_leverage))
                        logger.info(f"[INFO] 合约 {pos.contract} 使用账户全仓杠杆: {float(final_leverage)}x")
                    except:
                        pass
                
                if final_leverage == 0:
                    logger.warning(f"[WARNING] 合约 {pos.contract} 无法获取杠杆信息")
                
                # 计算收益率 = (标记价 - 入场价) / 入场价 * 100% * 方向
                entry_price_val = D(str(pos.entry_price)) if pos.entry_price else D(0)
                mark_price_val = D(str(pos.mark_price)) if pos.mark_price else D(0)
                size_val = D(str(pos.size))
                
                roi_percent = D(0)
                if entry_price_val > 0:
                    price_change_rate = (mark_price_val - entry_price_val) / entry_price_val
                    # 多头: size > 0, 收益率 = 价格涨幅 * 杠杆
                    # 空头: size < 0, 收益率 = 价格跌幅 * 杠杆 (价格下跌时为正)
                    if size_val > 0:
                        roi_percent = price_change_rate * final_leverage * 100
                    else:
                        roi_percent = -price_change_rate * final_leverage * 100
                
                result.append({
                    'contract': str(pos.contract) if pos.contract else 'N/A',
                    'size': size_val,
                    'leverage': final_leverage,
                    'entry_price': entry_price_val,
                    'mark_price': mark_price_val,
                    'unrealised_pnl': D(str(pos.unrealised_pnl)) if pos.unrealised_pnl else D(0),
                    'roi_percent': roi_percent,
                    'pnl_percent': D(str(pos.pnl_percent)) if hasattr(pos, 'pnl_percent') and pos.pnl_percent else D(0),
                    'margin': D(str(pos.margin)) if hasattr(pos, 'margin') and pos.margin else D(0),
                    'maintenance_rate': D(str(pos.maintenance_rate)) if hasattr(pos, 'maintenance_rate') and pos.maintenance_rate else D(0),
                })
            
            logger.info(f"   找到 {len(result)} 个有持仓的合约")
            return result
            
        except GateApiException as ex:
            logger.error(f"Gate API异常 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return []
    
    def get_usdt_perpetual_positions(self):
        """获取 USDT 永续合约所有仓位"""
        return self.get_all_positions(settle='usdt')
    
    def get_btc_perpetual_positions(self):
        """获取 BTC 永续合约所有仓位"""
        return self.get_all_positions(settle='btc')
    
    def get_all_settle_positions(self):
        """获取所有结算货币的所有合约仓位"""
        result = {}
        
        usdt_pos = self.get_usdt_perpetual_positions()
        if usdt_pos:
            result['usdt'] = usdt_pos
        
        btc_pos = self.get_btc_perpetual_positions()
        if btc_pos:
            result['btc'] = btc_pos
        
        return result

def print_positions(positions, title: str):
    """格式化打印仓位信息"""
    if not positions:
        print(f"\n{title}")
        print("   无持仓")
        return
    
    print(f"\n{title}")
    print("-" * 145)
    print(f"{'合约':<18} {'方向':<8} {'数量':<15} {'入场价':<18} {'标记价':<18} {'未实现盈亏':<18} {'收益率':<12} {'杠杆':<10}")
    print("-" * 145)
    
    for pos in positions:
        direction = "[多]" if pos['size'] > 0 else "[空]"
        size = abs(pos['size'])
        leverage_val = pos['leverage']
        # 直接处理 Decimal 类型
        if isinstance(leverage_val, D):
            leverage_str = f"{float(leverage_val):.1f}x"
        else:
            leverage_str = f"{float(leverage_val):.1f}x" if leverage_val and leverage_val != 0 else "N/A"
        
        # 盈亏显示
        pnl_val = float(pos['unrealised_pnl'])
        if pnl_val >= 0:
            pnl_display = f"[+] {pnl_val:>12.2f}"
        else:
            pnl_display = f"[-] {pnl_val:>12.2f}"
        
        # 收益率显示
        roi_val = float(pos['roi_percent'])
        if roi_val >= 0:
            roi_display = f"[+]{roi_val:>7.2f}%"
        else:
            roi_display = f"[{roi_val:>8.2f}%"
        
        print(f"{pos['contract']:<18} {direction:<8} {float(size):<15.4f} {float(pos['entry_price']):<18.2f} {float(pos['mark_price']):<18.2f} {pnl_display:<18} {roi_display:<12} {leverage_str:<10}")
    
    print("-" * 145)

def main():
    try:
        api_key, api_secret = load_env_config()
        query = FuturesPositionQuery(api_key, api_secret)
        
        print("\n" + "="*100)
        print("[*] 所有合约仓位查询")
        print("="*100)
        
        # 获取所有结算货币的所有仓位
        all_positions = query.get_all_settle_positions()
        
        if not all_positions:
            print("\n[!] 未找到任何合约持仓")
        else:
            # 显示 USDT 永续合约仓位
            if 'usdt' in all_positions:
                print_positions(all_positions['usdt'], "[USDT] 永续合约仓位")
            else:
                print("\n[USDT] 永续合约仓位")
                print("   无持仓")
            
            # 显示 BTC 永续合约仓位
            if 'btc' in all_positions:
                print_positions(all_positions['btc'], "[BTC] 永续合约仓位")
            else:
                print("\n[BTC] 永续合约仓位")
                print("   无持仓")
        
        print("\n" + "="*100)
        print("[OK] 查询完成")
        print("="*100 + "\n")
        
    except ValueError as e:
        logger.error(f"[ERROR] 配置错误: {e}")
    except Exception as e:
        logger.error(f"[ERROR] 错误: {e}")

if __name__ == '__main__':
    main()
