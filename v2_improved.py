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
from decimal import Decimal as D
from typing import Optional, Dict, List
import gate_api
from gate_api.exceptions import ApiException, GateApiException

# ============ 配置部分 ============
class TradingConfig:
    """交易配置类"""
    API_KEY = "你的_API_KEY"
    API_SECRET = "你的_API_SECRET"
    
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
            if tickers:
                ticker = tickers[0]
                return {
                    'last': D(ticker.last),
                    'high_24h': D(ticker.high_24h),
                    'low_24h': D(ticker.low_24h),
                    'volume_24h': D(ticker.volume_24h)
                }
        except GateApiException as ex:
            logger.error(f"Gate API异常 - {ex.label}: {ex.message}")
        except ApiException as e:
            logger.error(f"API异常: {e}")
        return None
    
    def get_balance(self) -> Optional[Dict]:
        """获取账户余额"""
        try:
            accounts = self.spot_api.list_spot_accounts(currency=self.config.CURRENCY)
            if accounts:
                account = accounts[0]
                return {
                    'available': D(account.available),
                    'locked': D(account.locked),
                    'total': D(account.available) + D(account.locked)
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
            if accounts:
                return D(accounts[0].available)
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
            if base_accounts:
                base_available = D(base_accounts[0].available)
                base_locked = D(base_accounts[0].locked)
            
            # 获取计价币种余额
            quote_accounts = self.spot_api.list_spot_accounts(currency=quote_currency)
            quote_available = D(0)
            quote_locked = D(0)
            if quote_accounts:
                quote_available = D(quote_accounts[0].available)
                quote_locked = D(quote_accounts[0].locked)
            
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
            created = self.spot_api.create_order(order)
            logger.info(f"✓ 下单成功 - {side.upper()} | ID: {created.id} | 状态: {created.status}")
            logger.info(f"  数量: {amount} | 价格: {price}")
            return str(created.id)
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
            logger.info(f"✓ 订单已取消 - ID: {order_id} | 状态: {result.status}")
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
            return {
                'id': order.id,
                'status': order.status,
                'side': order.side,
                'amount': D(order.amount),
                'price': D(order.price),
                'filled_total': D(order.filled_total) if order.filled_total else D(0)
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
                    'id': order.id,
                    'side': order.side,
                    'amount': D(order.amount),
                    'price': D(order.price)
                }
                for order in orders
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
    
    def simple_strategy(self) -> bool:
        """简单的买卖策略
        
        逻辑：
        1. 如果价格低于目标买入价格，且未持仓，则买入
        2. 如果已持仓且价格高于目标卖出价格，则卖出
        
        Returns:
            bool: 是否执行了交易
        """
        # 获取行情
        ticker = self.trader.get_ticker()
        if not ticker:
            return False
        
        current_price = ticker['last']
        logger.info(f"当前价格: {current_price} USDT | 24h高: {ticker['high_24h']} | 24h低: {ticker['low_24h']}")
        
        # 获取余额
        usdt_balance = self.trader.get_balance()
        if not usdt_balance:
            return False
        
        btc_balance = self.trader.get_cryptocurrency_balance("BTC")
        logger.info(f"账户余额 - USDT: {usdt_balance['available']} | BTC: {btc_balance if btc_balance else 0}")
        
        # 买入逻辑
        if current_price < self.config.TARGET_BUY_PRICE and not self.buy_hold:
            required_usdt = current_price * self.config.BUY_AMOUNT
            if usdt_balance['available'] > required_usdt:
                logger.info(f"🟢 买入信号 - 价格 {current_price} < 目标 {self.config.TARGET_BUY_PRICE}")
                order_id = self.trader.place_order(
                    'buy',
                    self.config.BUY_AMOUNT,
                    current_price
                )
                if order_id:
                    self.buy_hold = True
                    self.last_buy_price = current_price
                    return True
            else:
                logger.warning(f"余额不足 - 需要: {required_usdt}, 可用: {usdt_balance['available']}")
        
        # 卖出逻辑
        if current_price > self.config.TARGET_SELL_PRICE and self.buy_hold:
            btc_amount = self.trader.get_cryptocurrency_balance("BTC")
            if btc_amount and btc_amount >= self.config.SELL_AMOUNT:
                profit = (current_price - self.last_buy_price) * self.config.SELL_AMOUNT if self.last_buy_price else D(0)
                logger.info(f"🔴 卖出信号 - 价格 {current_price} > 目标 {self.config.TARGET_SELL_PRICE}")
                logger.info(f"预期收益: {profit} USDT (买入价: {self.last_buy_price})")
                order_id = self.trader.place_order(
                    'sell',
                    self.config.SELL_AMOUNT,
                    current_price
                )
                if order_id:
                    self.buy_hold = False
                    return True
        
        return False
    
    def check_pending_orders(self):
        """检查待处理订单"""
        orders = self.trader.list_pending_orders()
        if orders:
            logger.info(f"待处理订单: {len(orders)}笔")
            for order in orders:
                logger.info(f"  - {order['side'].upper()} | 数量: {order['amount']} | 价格: {order['price']}")


# ============ 机器人主程序 ============
def run_bot(config: TradingConfig):
    """运行交易机器人"""
    logger.info("=" * 50)
    logger.info("交易机器人启动")
    logger.info("=" * 50)
    logger.info(f"交易对: {config.CURRENCY_PAIR}")
    logger.info(f"买入目标价: {config.TARGET_BUY_PRICE} USDT")
    logger.info(f"卖出目标价: {config.TARGET_SELL_PRICE} USDT")
    logger.info("=" * 50)
    
    trader = GateIOTrader(config)
    strategy = TradingStrategy(trader, config)
    
    try:
        while True:
            try:
                logger.info("-" * 50)
                
                # 执行交易策略
                strategy.simple_strategy()
                
                # 检查待处理订单
                strategy.check_pending_orders()
                
                # 等待下一次检查
                logger.info(f"等待 {config.CHECK_INTERVAL} 秒后进行下一次检查...\n")
                time.sleep(config.CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("收到退出信号，停止机器人")
                break
            except Exception as e:
                logger.error(f"发生错误: {e}")
                logger.info(f"等待 {config.ERROR_WAIT_TIME} 秒后重试...\n")
                time.sleep(config.ERROR_WAIT_TIME)
    
    except KeyboardInterrupt:
        logger.info("机器人已停止")
    finally:
        logger.info("=" * 50)
        logger.info("交易机器人已关闭")
        logger.info("=" * 50)


if __name__ == '__main__':
    # 创建配置对象
    config = TradingConfig()
    
    # 运行机器人
    run_bot(config)
