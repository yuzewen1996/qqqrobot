#!/usr/bin/env python
# coding: utf-8
"""
合约交易机器人 - 基于GateIO官方库
支持：
- 合约仓位查询
- 合约行情获取
- 智能下单（做多/做空）
- 订单管理（查询、取消）
- 策略管理
- 交互式操作界面
"""

import time
import logging
import os
from pathlib import Path
from decimal import Decimal as D
from typing import Optional, Dict, List
import gate_api
from gate_api.exceptions import ApiException, GateApiException
import socket
import requests

# ============ 网络检测函数 ============
def check_network() -> bool:
    """检测网络连接是否正常"""
    try:
        # 尝试连接到公共DNS服务器
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except (socket.timeout, socket.error):
        try:
            # 备用方案：尝试连接到百度
            requests.get("https://www.baidu.com", timeout=3)
            return True
        except:
            return False


# ============ 配置加载函数 ============
def load_env_config():
    """从环境变量或 .env 文件加载配置"""
    # 尝试加载的 .env 文件路径列表（按优先级）
    env_paths = [
        Path(__file__).parent / ".env",  # 项目目录
        Path("C:/Users/admin/Desktop/gatekey.env"),  # 用户指定的路径
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            logger.info(f"加载配置文件: {env_path}")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ.setdefault(key.strip(), value.strip())
            break
    
    api_key = os.getenv('GATE_API_KEY')
    api_secret = os.getenv('GATE_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError(
            "❌ 错误: 未找到 API 密钥配置\n"
            "请使用以下方式之一设置密钥:\n"
            "  1. 环境变量: export GATE_API_KEY=xxx && export GATE_API_SECRET=xxx\n"
            "  2. .env 文件: 在项目根目录创建 .env，或使用 C:\\Users\\admin\\Desktop\\gatekey.env\n"
            "     GATE_API_KEY=your_api_key\n"
            "     GATE_API_SECRET=your_api_secret"
        )
    
    return api_key, api_secret

# ============ 配置部分 ============
class TradingConfig:
    """交易配置类"""
    # 从环境变量或 .env 文件加载 API 密钥
    _api_key = None
    _api_secret = None
    
    # API端点
    LIVE_HOST = "https://api.gateio.ws/api/v4"  # 实盘
    TESTNET_HOST = "https://fx-api-testnet.gateio.ws/api/v4"  # 测试网
    
    # 合约配置
    SETTLE = "usdt"  # 结算货币 (usdt 或 btc)
    CONTRACT = "BTC_USDT"  # 合约名称
    
    # 交易参数
    DEFAULT_SIZE = 1  # 默认交易张数
    DEFAULT_LEVERAGE = 10  # 默认杠杆倍数
    
    # 机器人参数
    CHECK_INTERVAL = 10  # 检查间隔（秒）
    ERROR_WAIT_TIME = 5  # 错误后等待时间（秒）
    
    def __init__(self):
        """初始化配置，加载 API 密钥"""
        if TradingConfig._api_key is None:
            try:
                TradingConfig._api_key, TradingConfig._api_secret = load_env_config()
            except ValueError as e:
                logger.error(str(e))
                raise
        self.USE_TESTNET = False  # 是否使用测试网
    
    @property
    def API_KEY(self):
        return TradingConfig._api_key
    
    @property
    def API_SECRET(self):
        return TradingConfig._api_secret


# ============ 日志配置 ============
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ API类 ============
class GateIOTrader:
    """GateIO合约交易机器人类"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self._init_api()
    
    def _init_api(self):
        """初始化API客户端"""
        host = self.config.TESTNET_HOST if self.config.USE_TESTNET else self.config.LIVE_HOST
        configuration = gate_api.Configuration(
            host=host,
            key=self.config.API_KEY,
            secret=self.config.API_SECRET
        )
        self.api_client = gate_api.ApiClient(configuration)
        self.futures_api = gate_api.FuturesApi(self.api_client)
        logger.info(f"合约API已初始化 - 模式: {'测试网' if self.config.USE_TESTNET else '实盘'} | 结算: {self.config.SETTLE.upper()}")
    
    def get_positions(self) -> Optional[List[Dict]]:
        """获取当前合约仓位"""
        try:
            positions = self.futures_api.list_positions(settle=self.config.SETTLE)  # type: ignore
            result = []
            for pos in positions:  # type: ignore
                size = float(pos.size) if pos.size else 0
                if abs(size) > 0:  # 只返回有持仓的合约
                    # 获取杠杆倍数：逐仓用leverage，全仓用cross_leverage_limit
                    leverage = 0
                    if hasattr(pos, 'leverage') and pos.leverage and float(pos.leverage) > 0:
                        leverage = int(float(pos.leverage))
                    elif hasattr(pos, 'cross_leverage_limit') and pos.cross_leverage_limit:
                        leverage = int(float(pos.cross_leverage_limit))
                    
                    # 合约价值（USDT）
                    value = float(pos.value) if pos.value else 0
                    
                    result.append({
                        'contract': pos.contract,
                        'size': size,
                        'value': value,  # 合约价值（USDT）
                        'leverage': leverage,
                        'entry_price': float(pos.entry_price) if pos.entry_price else 0,
                        'mark_price': float(pos.mark_price) if pos.mark_price else 0,
                        'unrealised_pnl': float(pos.unrealised_pnl) if pos.unrealised_pnl else 0,
                        'realised_pnl': float(pos.realised_pnl) if pos.realised_pnl else 0,
                        'margin': float(pos.margin) if pos.margin else 0,
                        'mode': pos.mode if hasattr(pos, 'mode') else 'unknown',
                    })
            return result
        except (ApiException, GateApiException) as e:
            logger.error(f"获取仓位失败: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """获取合约账户信息"""
        try:
            account = self.futures_api.list_futures_accounts(settle=self.config.SETTLE)  # type: ignore
            if account:
                return {
                    'total': float(account.total) if account.total else 0,  # type: ignore
                    'available': float(account.available) if account.available else 0,  # type: ignore
                    'unrealised_pnl': float(account.unrealised_pnl) if account.unrealised_pnl else 0,  # type: ignore
                    'position_margin': float(account.position_margin) if account.position_margin else 0,  # type: ignore
                    'order_margin': float(account.order_margin) if account.order_margin else 0,  # type: ignore
                }
        except (ApiException, GateApiException) as e:
            logger.error(f"获取账户信息失败: {e}")
            return None
    
    def get_candlesticks(self, contract: str, interval: str = '1h', limit: int = 200) -> List[Dict]:
        """获取K线数据"""
        try:
            candlesticks = self.futures_api.list_futures_candlesticks(
                settle=self.config.SETTLE,
                contract=contract,
                interval=interval,
                limit=limit
            )
            from datetime import datetime
            return [
                {
                    'time': int(cs.t),
                    'datetime': datetime.fromtimestamp(int(cs.t)),
                    'open': float(cs.o),
                    'close': float(cs.c),
                    'high': float(cs.h),
                    'low': float(cs.l),
                    'volume': float(cs.v) if cs.v else 0
                }
                for cs in candlesticks
            ]
        except (ApiException, GateApiException) as e:
            logger.error(f"获取K线数据失败: {e}")
            return []
    
    



# ============ 策略统一导入 ============

# ============ 策略统一导入 ============
from all_strategies import MAStrategy, RSIStrategy, GridTradingStrategy, EMABreakoutStrategy, BollingerBandsStrategy, MomentumBreakoutStrategy, MACDFastStrategy, VolatilityBreakoutStrategy

# ============ 多币种详细仓位查询类 ============
class FuturesPositionQuery:
    """期货/永续合约仓位查询（支持多币种）"""
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
        try:
            account = self.futures_api.list_futures_accounts(settle=settle)
            if account:
                cross_leverage = getattr(account, 'cross_leverage', None)
                logger.info(f"[INFO] {settle.upper()} 账户全仓杠杆: {cross_leverage}")
                return cross_leverage
        except Exception as e:
            logger.error(f"[ERROR] 获取账户杠杆失败: {e}")
        return None

    def get_all_positions(self, settle: str = 'usdt'):
        try:
            logger.info(f"\n[*] 获取 {settle.upper()} 所有合约仓位...")
            account_leverage = self.get_account_leverage(settle)
            positions = self.futures_api.list_positions(settle=settle)
            if not positions:
                logger.info(f"   {settle.upper()} 无持仓")
                return []
            result = []
            for pos in positions:
                try:
                    size_float = float(pos.size) if pos.size else 0
                    if abs(size_float) == 0:
                        continue
                except (ValueError, TypeError):
                    continue
                leverage_val = D(str(pos.leverage)) if pos.leverage and str(pos.leverage) != '0' else D(0)
                final_leverage = D(0)
                if leverage_val > 0:
                    final_leverage = leverage_val
                elif hasattr(pos, 'cross_leverage_limit') and pos.cross_leverage_limit:
                    try:
                        final_leverage = D(str(pos.cross_leverage_limit))
                    except:
                        pass
                elif account_leverage:
                    try:
                        final_leverage = D(str(account_leverage))
                    except:
                        pass
                entry_price_val = D(str(pos.entry_price)) if pos.entry_price else D(0)
                mark_price_val = D(str(pos.mark_price)) if pos.mark_price else D(0)
                size_val = D(str(pos.size))
                roi_percent = D(0)
                if entry_price_val > 0:
                    price_change_rate = (mark_price_val - entry_price_val) / entry_price_val
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
        return self.get_all_positions(settle='usdt')

    def get_btc_perpetual_positions(self):
        return self.get_all_positions(settle='btc')

    def get_all_settle_positions(self):
        result = {}
        usdt_pos = self.get_usdt_perpetual_positions()
        if usdt_pos:
            result['usdt'] = usdt_pos
        btc_pos = self.get_btc_perpetual_positions()
        if btc_pos:
            result['btc'] = btc_pos
        return result

# ============ 仓位信息格式化打印 ============
def print_positions(positions, title: str):
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
        if isinstance(leverage_val, D):
            leverage_str = f"{float(leverage_val):.1f}x"
        else:
            leverage_str = f"{float(leverage_val):.1f}x" if leverage_val and leverage_val != 0 else "N/A"
        pnl_val = float(pos['unrealised_pnl'])
        if pnl_val >= 0:
            pnl_display = f"[+] {pnl_val:>12.2f}"
        else:
            pnl_display = f"[-] {pnl_val:>12.2f}"
        roi_val = float(pos['roi_percent'])
        if roi_val >= 0:
            roi_display = f"[+]{roi_val:>7.2f}%"
        else:
            roi_display = f"[{roi_val:>8.2f}%"
        print(f"{pos['contract']:<18} {direction:<8} {float(size):<15.4f} {float(pos['entry_price']):<18.2f} {float(pos['mark_price']):<18.2f} {pnl_display:<18} {roi_display:<12} {leverage_str:<10}")
    print("-" * 145)

# ============ 显示功能 ============
def display_positions(trader: GateIOTrader):
    """显示当前合约仓位"""
    print("\n" + "="*80)
    print("📊 当前合约仓位")
    print("="*80)
    
    positions = trader.get_positions()
    
    if not positions or len(positions) == 0:
        print("暂无持仓")
    else:
        for pos in positions:
            side = "做多 📈" if pos['size'] > 0 else "做空 📉"
            pnl_sign = "+" if pos['unrealised_pnl'] >= 0 else ""
            pnl_color = "💚" if pos['unrealised_pnl'] >= 0 else "💔"
            
            # 杠杆和模式显示
            leverage_str = f"{pos['leverage']}x" if pos['leverage'] > 0 else "未知"
            mode_str = ""
            if 'mode' in pos and pos['mode'] != 'unknown':
                if 'dual' in pos['mode']:
                    mode_str = " [双向持仓]"
                elif 'single' in pos['mode']:
                    mode_str = " [单向持仓]"
            
            # 计算收益率百分比（按照本金计算）
            roi_percent = 0.0
            if pos['value'] > 0 and pos['leverage'] > 0:
                # 本金 = 仓位价值 ÷ 杠杆倍数
                principal = pos['value'] / pos['leverage']
                roi_percent = (pos['unrealised_pnl'] / principal) * 100
            elif pos['value'] > 0:
                # 如果没有杠杆信息，用仓位价值作为本金
                roi_percent = (pos['unrealised_pnl'] / pos['value']) * 100
            
            roi_sign = "+" if roi_percent >= 0 else ""
            roi_color = "📈" if roi_percent >= 0 else "📉"
            
            print(f"\n合约: {pos['contract']}")
            print(f"  方向: {side} | 仓位价值: {pos['value']:.2f} USDT | 杠杆: {leverage_str}{mode_str}")
            print(f"  开仓价: {pos['entry_price']:.2f} | 标记价: {pos['mark_price']:.2f}")
            print(f"  未实现盈亏: {pnl_color} {pnl_sign}{pos['unrealised_pnl']:.4f} USDT | 收益率: {roi_color} {roi_sign}{roi_percent:.2f}%")
            print(f"  占用保证金: {pos['margin']:.4f} USDT")
    
    # 显示账户信息
    account = trader.get_account_info()
    if account:
        print(f"\n💰 账户总览:")
        print(f"  总资产: {account['total']:.4f} USDT")
        print(f"  可用余额: {account['available']:.4f} USDT")
        print(f"  未实现盈亏: {account['unrealised_pnl']:.4f} USDT")
        print(f"  仓位保证金: {account['position_margin']:.4f} USDT")
    
    print("="*80)


def display_menu():
    """显示操作菜单"""
    print("\n📋 请选择操作:")
    print("  1. 刷新仓位信息")
    print("  2. 查看策略状态")
    print("  3. 手动交易")
    print("  4. 启动自动策略")
    print("  5. 查看订单")
    print("  6. 设置参数")
    print("  7. 详细合约仓位查询（多币种）")
    print("  0. 退出程序")
    print("-" * 80)


def handle_manual_trade(trader: GateIOTrader):
    """处理手动交易"""
    print("\n🔧 手动交易功能开发中...")
    print("即将支持: 开多、开空、平仓等操作")


def handle_strategy_view(trader: GateIOTrader):
    """查看策略状态"""
    print("\n📈 策略状态:")
    print("当前没有运行中的策略")
    print("提示: 选择菜单4可以启动自动策略")


def handle_auto_strategy(trader: GateIOTrader):
    """启动自动策略"""
    print("\n🤖 策略示例调用：")
    # 示例：获取K线数据（假设trader有get_kline方法，实际请根据你的API实现调整）
    try:
        # 假设有BTC_USDT合约，获取最近50根K线
        candles = []
        if hasattr(trader, 'get_candlesticks'):
            candles = trader.get_candlesticks('BTC_USDT', interval='1h', limit=50)
        elif hasattr(trader, 'get_kline'):
            candles = trader.get_kline('BTC_USDT', interval='1h', limit=50)
        if not candles:
            print("未获取到K线数据，无法演示策略调用。")
            return
        # MA策略
        ma_strategy = MAStrategy(trader, 'BTC_USDT')
        ma_signal = ma_strategy.generate_signal(candles)
        print(f"MA策略信号: {ma_signal}")
        # RSI策略
        rsi_strategy = RSIStrategy(trader, 'BTC_USDT')
        rsi_signal = rsi_strategy.generate_signal(candles)
        print(f"RSI策略信号: {rsi_signal}")
        # 网格策略
        grid_strategy = GridTradingStrategy(D('40000'), D('60000'), grid_count=10)
        grid_orders = grid_strategy.get_orders(D(candles[-1]['close']))
        print(f"网格策略订单数: {len(grid_orders)}")
    except Exception as e:
        print(f"策略调用示例出错: {e}")


def handle_view_orders(trader: GateIOTrader):
    """查看订单"""
    print("\n📜 订单查询功能开发中...")


def run_bot(config: TradingConfig):
    """运行交易机器人主程序"""
    try:
        trader = GateIOTrader(config)
        # 启动时显示仓位信息
        display_positions(trader)
        # 初始化多币种查询类
        api_key, api_secret = config.API_KEY, config.API_SECRET
        futures_query = FuturesPositionQuery(api_key, api_secret)
        # 主循环
        while True:
            try:
                display_menu()
                choice = input("请输入选项 (0-7): ").strip()
                if choice == '0':
                    print("\n👋 退出程序...")
                    break
                elif choice == '1':
                    display_positions(trader)
                elif choice == '2':
                    handle_strategy_view(trader)
                elif choice == '3':
                    handle_manual_trade(trader)
                elif choice == '4':
                    handle_auto_strategy(trader)
                elif choice == '5':
                    handle_view_orders(trader)
                elif choice == '6':
                    handle_settings(config)
                elif choice == '7':
                    print("\n========== 多币种详细合约仓位查询 ==========")
                    all_positions = futures_query.get_all_settle_positions()
                    if not all_positions:
                        print("\n[!] 未找到任何合约持仓")
                    else:
                        if 'usdt' in all_positions:
                            print_positions(all_positions['usdt'], "[USDT] 永续合约仓位")
                        else:
                            print("\n[USDT] 永续合约仓位\n   无持仓")
                        if 'btc' in all_positions:
                            print_positions(all_positions['btc'], "[BTC] 永续合约仓位")
                        else:
                            print("\n[BTC] 永续合约仓位\n   无持仓")
                    print("\n========== 查询完成 ==========")
                else:
                    print("❌ 无效选项，请重新输入")
            except KeyboardInterrupt:
                print("\n\n👋 检测到中断信号，退出程序...")
                break
            except Exception as e:
                logger.error(f"操作出错: {e}")
                print(f"❌ 操作失败: {e}")
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        print(f"❌ 程序启动失败: {e}")


if __name__ == '__main__':
    print("🚀 合约交易机器人启动中...\n")
    
    try:
        # 创建配置对象
        config = TradingConfig()
        # === 这里控制是否连接测试网 ===
        config.USE_TESTNET = False  # True=测试网，False=实盘
        # ===========================
        # 运行机器人
        run_bot(config)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        print(f"\n❌ 程序异常: {e}")
    
    print("\n程序已结束")
