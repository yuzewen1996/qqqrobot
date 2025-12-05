#!/usr/bin/env python
# coding: utf-8
"""
改进的交易机器人 - 基于GateIO官方库最佳实践
支持：
- 实时行情获取
- 智能下单（买入/卖出）
- 订单管理（查询、取消）
- 账户余额查询
- 更完善的错误处理
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
    
    # 交易对配置
    CURRENCY_PAIR = "BTC_USDT"
    CURRENCY = "USDT"
    
    # 交易参数
    BUY_AMOUNT = D("0.001")  # 每次买入数量（BTC）
    SELL_AMOUNT = D("0.001")  # 每次卖出数量（BTC）
    TARGET_BUY_PRICE = D("50000")  # 目标买入价格
    TARGET_SELL_PRICE = D("60000")  # 目标卖出价格
    
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
    """GateIO交易机器人类"""
    
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
        self.spot_api = gate_api.SpotApi(self.api_client)
        logger.info(f"API客户端已初始化 - 模式: {'测试网' if self.config.USE_TESTNET else '实盘'}")
    
    def get_ticker(self) -> Optional[Dict]:
        """获取交易对行情"""
        try:
            tickers = self.spot_api.list_tickers(currency_pair=self.config.CURRENCY_PAIR)
            if tickers:  # type: ignore
                ticker = tickers[0]  # type: ignore
                last_price = getattr(ticker, 'last', None)
                high_24h = getattr(ticker, 'high_24h', None)
                low_24h = getattr(ticker, 'low_24h', None)
                volume_24h = getattr(ticker, 'volume_24h', None)
                
                return {
                    'last': D(last_price) if last_price else D(0),
                    'high_24h': D(high_24h) if high_24h else D(0),
                    'low_24h': D(low_24h) if low_24h else D(0),
                    'volume_24h': D(volume_24h) if volume_24h else D(0)
                }
        except AttributeError as ae:
            logger.warning(f"Ticker 属性缺失: {ae}，返回基础数据")
            try:
                if tickers:  # type: ignore
                    ticker = tickers[0]  # type: ignore
                    last_price = getattr(ticker, 'last', None)
                    high_24h = getattr(ticker, 'high_24h', None)
                    low_24h = getattr(ticker, 'low_24h', None)
                    
                    return {
                        'last': D(last_price) if last_price else D(0),
                        'high_24h': D(high_24h) if high_24h else D(0),
                        'low_24h': D(low_24h) if low_24h else D(0),
                        'volume_24h': D(0)
                    }
            except:
                return None
        except GateApiException as ex:
            logger.error(f"Gate API异常 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None
    
    def get_balance(self) -> Optional[Dict]:
        """获取账户余额"""
        try:
            accounts = self.spot_api.list_spot_accounts(currency=self.config.CURRENCY)
            if accounts:  # type: ignore
                account = accounts[0]  # type: ignore
                available = getattr(account, 'available', '0')
                locked = getattr(account, 'locked', '0')
                return {
                    'available': D(available),
                    'locked': D(locked),
                    'total': D(available) + D(locked)
                }
        except GateApiException as ex:
            logger.error(f"Gate API异常 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None
    
    def get_cryptocurrency_balance(self, currency: str) -> Optional[D]:
        """获取特定加密货币余额"""
        try:
            accounts = self.spot_api.list_spot_accounts(currency=currency)
            if accounts:  # type: ignore
                available = getattr(accounts[0], 'available', '0')  # type: ignore
                return D(available)
        except GateApiException as ex:
            logger.error(f"Gate API异常 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None
    
    def get_position_info(self) -> Optional[Dict]:
        """获取当前仓位信息（现货交易）
        
        Returns:
            包含仓位信息的字典，包括：
            - base_currency_balance: 基础币种（如BTC）的余额
            - quote_currency_balance: 计价币种（如USDT）的余额
            - position_value: 仓位价值
            - total_assets: 总资产价值
        """
        try:
            # 获取交易对的两个币种
            pair_parts = self.config.CURRENCY_PAIR.split('_')
            base_currency = pair_parts[0]  # 如BTC
            quote_currency = pair_parts[1]  # 如USDT
            
            # 获取基础币种余额
            base_accounts = self.spot_api.list_spot_accounts(currency=base_currency)
            base_available = D(0)
            base_locked = D(0)
            if base_accounts:  # type: ignore
                base_available = D(getattr(base_accounts[0], 'available', '0'))  # type: ignore
                base_locked = D(getattr(base_accounts[0], 'locked', '0'))  # type: ignore
            
            # 获取计价币种余额
            quote_accounts = self.spot_api.list_spot_accounts(currency=quote_currency)
            quote_available = D(0)
            quote_locked = D(0)
            if quote_accounts:  # type: ignore
                quote_available = D(getattr(quote_accounts[0], 'available', '0'))  # type: ignore
                quote_locked = D(getattr(quote_accounts[0], 'locked', '0'))  # type: ignore
            
            # 获取当前价格
            ticker = self.get_ticker()
            current_price = ticker['last'] if ticker else D(0)
            
            # 计算仓位价值
            base_position_value = (base_available + base_locked) * current_price
            quote_total = quote_available + quote_locked
            total_assets = base_position_value + quote_total
            
            return {
                'base_currency': base_currency,
                'quote_currency': quote_currency,
                'base_available': base_available,  # 可用的基础币
                'base_locked': base_locked,         # 冻结的基础币
                'base_total': base_available + base_locked,  # 基础币总量
                'quote_available': quote_available,  # 可用的计价币
                'quote_locked': quote_locked,        # 冻结的计价币
                'quote_total': quote_total,          # 计价币总量
                'current_price': current_price,      # 当前价格
                'base_position_value': base_position_value,  # 基础币的价值
                'total_assets': total_assets,        # 总资产价值
                'position_ratio': base_position_value / total_assets if total_assets > 0 else D(0)  # 仓位占比
            }
        except GateApiException as ex:
            logger.error(f"Gate API异常 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None
    
    def place_order(self, side: str, amount: D, price: D) -> Optional[str]:
        """下单
        
        Args:
            side: 'buy' 或 'sell'
            amount: 下单数量
            price: 下单价格
        
        Returns:
            订单ID或None
        """
        try:
            order = gate_api.Order(
                currency_pair=self.config.CURRENCY_PAIR,
                side=side,
                amount=str(amount),
                price=str(price)
            )
            created = self.spot_api.create_order(order)  # type: ignore
            order_id = getattr(created, 'id', '')  # type: ignore
            order_status = getattr(created, 'status', '')  # type: ignore
            logger.info(f"✓ 下单成功 - {side.upper()} | ID: {order_id} | 状态: {order_status}")
            logger.info(f"  数量: {amount} | 价格: {price}")
            return str(order_id)
        except GateApiException as ex:
            logger.error(f"下单失败 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            result = self.spot_api.cancel_order(
                order_id,
                currency_pair=self.config.CURRENCY_PAIR
            )
            result_status = getattr(result, 'status', '')  # type: ignore
            logger.info(f"✓ 订单已取消 - ID: {order_id} | 状态: {result_status}")
            return True
        except GateApiException as ex:
            logger.error(f"取消失败 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return False
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """查询订单详情"""
        try:
            order = self.spot_api.get_order(
                order_id,
                currency_pair=self.config.CURRENCY_PAIR
            )
            filled_total = getattr(order, 'filled_total', None)  # type: ignore
            return {
                'id': getattr(order, 'id', ''),  # type: ignore
                'status': getattr(order, 'status', ''),  # type: ignore
                'side': getattr(order, 'side', ''),  # type: ignore
                'amount': D(getattr(order, 'amount', '0')),  # type: ignore
                'price': D(getattr(order, 'price', '0')),  # type: ignore
                'filled_total': D(filled_total) if filled_total else D(0)
            }
        except GateApiException as ex:
            logger.error(f"查询失败 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None
    
    def list_pending_orders(self) -> Optional[List[Dict]]:
        """获取待处理订单列表"""
        try:
            orders = self.spot_api.list_orders(
                currency_pair=self.config.CURRENCY_PAIR,
                status='open'
            )
            return [
                {
                    'id': getattr(order, 'id', ''),  # type: ignore
                    'side': getattr(order, 'side', ''),  # type: ignore
                    'amount': D(getattr(order, 'amount', '0')),  # type: ignore
                    'price': D(getattr(order, 'price', '0'))  # type: ignore
                }
                for order in orders  # type: ignore
            ]
        except GateApiException as ex:
            logger.error(f"查询订单列表失败 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None


# ============ 交易策略 ============
class TradingStrategy:
    """交易策略类"""
    
    def __init__(self, trader: GateIOTrader, config: TradingConfig):
        self.trader = trader
        self.config = config
        self.last_buy_price = None  # 记录最后的买入价格
        self.buy_hold = False  # 是否持有买入仓位
    



# ============ 机器人主程序 ============
def run_bot(config: TradingConfig):
    """运行交易机器人"""
    trader = GateIOTrader(config)
    
    try:
        while True:
            try:
                # 获取行情
                ticker = trader.get_ticker()
                if ticker:
                    print(ticker)
                else:
                    # 获取不到行情，进行网络检测
                    if check_network():
                        print("❌ 交易所故障：网络正常，但无法获取行情数据")
                    else:
                        print("❌ 网络异常：无法连接到网络")
                
                time.sleep(config.CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                time.sleep(config.ERROR_WAIT_TIME)
    
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    # 创建配置对象
    config = TradingConfig()
    
    # 运行机器人
    run_bot(config)
