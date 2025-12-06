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
    
    def __init__(self):
        """初始化配置，加载 API 密钥"""
        if TradingConfig._api_key is None:
            try:
                TradingConfig._api_key, TradingConfig._api_secret = load_env_config()
            except ValueError as e:
                logger.error(str(e))
                raise
    
    @property
    def API_KEY(self):
        return TradingConfig._api_key
    
    @property
    def API_SECRET(self):
        return TradingConfig._api_secret
    
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
    USE_TESTNET = False  # 是否使用测试网


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
    
    



# ============ 交易策略 ============
class TradingStrategy:
    """交易策略类"""
    
    def __init__(self, trader: GateIOTrader, config: TradingConfig):
        self.trader = trader
        self.config = config
        self.last_buy_price = None  # 记录最后的买入价格
        self.buy_hold = False  # 是否持有买入仓位
    



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
            
            print(f"\n合约: {pos['contract']}")
            print(f"  方向: {side} | 仓位价值: {pos['value']:.2f} USDT | 杠杆: {leverage_str}{mode_str}")
            print(f"  开仓价: {pos['entry_price']:.2f} | 标记价: {pos['mark_price']:.2f}")
            print(f"  未实现盈亏: {pnl_color} {pnl_sign}{pos['unrealised_pnl']:.4f} USDT")
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
    print("\n🤖 自动策略功能开发中...")
    print("即将支持: MA策略、RSI策略、网格交易等")


def handle_view_orders(trader: GateIOTrader):
    """查看订单"""
    print("\n📜 订单查询功能开发中...")


def handle_settings(config: TradingConfig):
    """设置参数"""
    print("\n⚙️ 当前配置:")
    print(f"  合约: {config.CONTRACT}")
    print(f"  结算货币: {config.SETTLE.upper()}")
    print(f"  默认张数: {config.DEFAULT_SIZE}")
    print(f"  默认杠杆: {config.DEFAULT_LEVERAGE}x")
    print(f"  使用测试网: {'是' if config.USE_TESTNET else '否'}")


# ============ 机器人主程序 ============
def run_bot(config: TradingConfig):
    """运行交易机器人主程序"""
    try:
        trader = GateIOTrader(config)
        
        # 启动时显示仓位信息
        display_positions(trader)
        
        # 主循环
        while True:
            try:
                display_menu()
                choice = input("请输入选项 (0-6): ").strip()
                
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
        
        # 运行机器人
        run_bot(config)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        print(f"\n❌ 程序异常: {e}")
    
    print("\n程序已结束")
