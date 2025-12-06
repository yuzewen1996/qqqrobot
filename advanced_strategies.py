#!/usr/bin/env python
# coding: utf-8
"""
高级合约交易策略示例
包含：
- 移动平均线策略（合约）
- RSI指标策略（合约）
- 网格交易策略（合约）
- 配置多个合约
"""

import time
import logging
from decimal import Decimal as D
from typing import List, Dict, Optional
from collections import deque
import gate_api
from gate_api.exceptions import ApiException, GateApiException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuturesAdvancedTrader:
    """高级合约交易机器人"""
    
    def __init__(self, api_key: str, api_secret: str, settle: str = 'usdt', use_testnet: bool = False):
        """
        初始化合约交易机器人
        
        Args:
            api_key: API密钥
            api_secret: API密钥
            settle: 结算货币 ('usdt' 或 'btc')
            use_testnet: 是否使用测试网
        """
        host = "https://fx-api-testnet.gateio.ws/api/v4" if use_testnet else "https://api.gateio.ws/api/v4"
        config = gate_api.Configuration(host=host, key=api_key, secret=api_secret)
        self.api_client = gate_api.ApiClient(config)
        self.futures_api = gate_api.FuturesApi(self.api_client)
        self.settle = settle
        logger.info(f"合约API已初始化 - 结算货币: {settle.upper()}")
    
    def get_candlesticks(self, contract: str, interval: str = '1h', limit: int = 100) -> List[Dict]:
        """获取合约K线数据
        
        Args:
            contract: 合约名称，如 'BTC_USDT'
            interval: K线周期 ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: 获取数量
        """
        try:
            candlesticks = self.futures_api.list_futures_candlesticks(
                settle=self.settle,
                contract=contract,
                interval=interval,
                limit=limit
            )
            return [
                {
                    'time': int(cs.t),
                    'open': D(cs.o),
                    'close': D(cs.c),
                    'high': D(cs.h),
                    'low': D(cs.l),
                    'volume': D(cs.v)
                }
                for cs in candlesticks
            ]
        except (ApiException, GateApiException) as e:
            logger.error(f"获取合约K线失败: {e}")
            return []
    
    def calculate_ma(self, prices: List[D], period: int) -> List[D]:
        """计算移动平均线"""
        if len(prices) < period:
            return []
        
        mas = []
        for i in range(len(prices) - period + 1):
            ma = sum(prices[i:i+period]) / period
            mas.append(ma)
        return mas


# ============ 策略1: 移动平均线交叉策略 ============
class MAStrategy:
    """移动平均线交叉策略 (金叉/死叉) - 合约版本
    
    逻辑：
    - 当快线(MA5) 上穿 慢线(MA20) 时，生成做多信号
    - 当快线(MA5) 下穿 慢线(MA20) 时，生成做空信号
    """
    
    def __init__(self, trader: FuturesAdvancedTrader, contract: str):
        self.trader = trader
        self.contract = contract
        self.last_signal = None  # 上一个信号
    
    def generate_signal(self, candles: List[Dict]) -> str:
        """生成交易信号"""
        if len(candles) < 20:
            return 'hold'
        
        closes = [D(c['close']) for c in candles]
        
        # 计算MA5和MA20
        ma5_list = []
        ma20_list = []
        
        for i in range(len(closes)):
            if i >= 4:
                ma5_list.append(sum(closes[i-4:i+1]) / 5)
            if i >= 19:
                ma20_list.append(sum(closes[i-19:i+1]) / 20)
        
        if len(ma5_list) < 2 or len(ma20_list) < 2:
            return 'hold'
        
        ma5_prev, ma5_curr = ma5_list[-2], ma5_list[-1]
        ma20_prev, ma20_curr = ma20_list[-2], ma20_list[-1]
        
        # 检查交叉
        if ma5_prev <= ma20_prev and ma5_curr > ma20_curr:
            signal = 'long'  # 金叉 - 做多
        elif ma5_prev >= ma20_prev and ma5_curr < ma20_curr:
            signal = 'short'  # 死叉 - 做空
        else:
            signal = 'hold'
        
        if signal != 'hold':
            logger.info(f"🎯 MA策略信号 [{self.contract}]: {signal.upper()}")
            logger.info(f"   MA5: {ma5_curr:.2f} | MA20: {ma20_curr:.2f}")
        
        return signal


# ============ 策略2: RSI策略 ============
class RSIStrategy:
    """RSI相对强度指数策略 - 合约版本
    
    逻辑：
    - RSI < 30: 超卖，生成做多信号
    - RSI > 70: 超买，生成做空信号
    """
    
    def __init__(self, trader: FuturesAdvancedTrader, contract: str, period: int = 14):
        self.trader = trader
        self.contract = contract
        self.period = period
    
    def calculate_rsi(self, candles: List[Dict]) -> float:
        """计算RSI指标"""
        if len(candles) < self.period + 1:
            return 50  # 默认中立
        
        closes = [D(c['close']) for c in candles]
        
        # 计算涨跌
        changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        # 分别统计涨幅和跌幅
        gains = sum([c for c in changes[-self.period:] if c > 0]) / self.period
        losses = abs(sum([c for c in changes[-self.period:] if c < 0])) / self.period
        
        # 避免除以0
        if losses == 0:
            return 100 if gains > 0 else 0
        
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def generate_signal(self, candles: List[Dict]) -> str:
        """生成RSI信号"""
        rsi = self.calculate_rsi(candles)
        
        if rsi < 30:
            signal = 'long'  # 超卖 - 做多
            logger.info(f"🎯 RSI策略信号 [{self.contract}]: {signal.upper()}")
            logger.info(f"   RSI: {rsi:.2f} (超卖)")
            return signal
        elif rsi > 70:
            signal = 'short'  # 超买 - 做空
            logger.info(f"🎯 RSI策略信号 [{self.contract}]: {signal.upper()}")
            logger.info(f"   RSI: {rsi:.2f} (超买)")
            return signal
        else:
            return 'hold'


# ============ 策略3: 合约网格交易策略 ============
class FuturesGridTradingStrategy:
    """合约网格交易策略
    
    逻辑：
    - 在价格区间内，以固定间隔设置做多/做空订单
    - 当价格波动时，自动执行交易
    - 支持双向持仓
    """
    
    def __init__(self, 
                 lower_price: D,
                 upper_price: D,
                 grid_count: int = 10,
                 grid_size: int = 1,  # 合约张数
                 leverage: int = 10):  # 杠杆倍数
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.grid_count = grid_count
        self.grid_size = grid_size
        self.leverage = leverage
        
        # 计算网格间距
        self.grid_step = (upper_price - lower_price) / grid_count
        
        # 初始化网格
        self.grids = self._init_grids()
    
    def _init_grids(self) -> List[Dict]:
        """初始化网格"""
        grids = []
        for i in range(self.grid_count + 1):
            price = self.lower_price + self.grid_step * i
            grids.append({
                'price': price,
                'buy_triggered': False,
                'sell_triggered': False
            })
        return grids
    
    def get_orders(self, current_price: D) -> List[Dict]:
        """根据当前价格，返回应该下的合约订单"""
        orders = []
        
        for grid in self.grids:
            # 价格接近网格点时（±0.5%）
            if abs(grid['price'] - current_price) / grid['price'] < 0.005:
                if not grid['buy_triggered']:
                    orders.append({
                        'side': 'long',  # 做多
                        'price': grid['price'],
                        'size': self.grid_size,
                        'leverage': self.leverage
                    })
                    grid['buy_triggered'] = True
                
                if not grid['sell_triggered'] and grid['price'] > self.lower_price:
                    orders.append({
                        'side': 'short',  # 做空
                        'price': grid['price'],
                        'size': self.grid_size,
                        'leverage': self.leverage
                    })
                    grid['sell_triggered'] = True
        
        return orders


# ============ 示例使用 ============
def example_ma_strategy():
    """MA策略示例 - 合约版本"""
    logger.info("=" * 60)
    logger.info("合约MA交叉策略示例")
    logger.info("=" * 60)
    
    trader = FuturesAdvancedTrader(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_SECRET",
        settle="usdt",
        use_testnet=True
    )
    
    strategy = MAStrategy(trader, "BTC_USDT")
    
    # 获取合约K线
    candles = trader.get_candlesticks("BTC_USDT", interval="1h", limit=50)
    
    if candles:
        signal = strategy.generate_signal(candles)
        logger.info(f"交易信号: {signal} (long=做多, short=做空, hold=持有)")


def example_rsi_strategy():
    """RSI策略示例 - 合约版本"""
    logger.info("=" * 60)
    logger.info("合约RSI策略示例")
    logger.info("=" * 60)
    
    trader = FuturesAdvancedTrader(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_SECRET",
        settle="usdt",
        use_testnet=True
    )
    
    strategy = RSIStrategy(trader, "BTC_USDT")
    
    candles = trader.get_candlesticks("BTC_USDT", interval="1h", limit=30)
    
    if candles:
        signal = strategy.generate_signal(candles)
        logger.info(f"交易信号: {signal} (long=做多, short=做空, hold=持有)")


def example_grid_trading():
    """合约网格交易策略示例"""
    logger.info("=" * 60)
    logger.info("合约网格交易策略示例")
    logger.info("=" * 60)
    
    strategy = FuturesGridTradingStrategy(
        lower_price=D("40000"),    # 最低价格
        upper_price=D("60000"),    # 最高价格
        grid_count=20,             # 20个网格
        grid_size=10,              # 每笔10张合约
        leverage=10                # 10倍杠杆
    )
    
    # 模拟价格变化
    prices = [D("45000"), D("47000"), D("50000"), D("48000"), D("52000")]
    
    for price in prices:
        logger.info(f"\n当前价格: {price}")
        orders = strategy.get_orders(price)
        
        if orders:
            logger.info(f"生成订单: {len(orders)}笔")
            for order in orders:
                logger.info(f"  - {order['side'].upper()} | {order['size']} 张 @ {order['price']} | 杠杆: {order['leverage']}x")
        else:
            logger.info("暂无交易信号")


# ============ 多合约监控示例 ============
def multi_contract_monitoring():
    """监控多个合约"""
    logger.info("=" * 60)
    logger.info("多合约监控示例")
    logger.info("=" * 60)
    
    trader = FuturesAdvancedTrader(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_SECRET",
        settle="usdt",
        use_testnet=True
    )
    
    # 监控的合约
    contracts = ["BTC_USDT", "ETH_USDT", "XRP_USDT"]
    
    # 为每个合约创建不同的策略
    strategies = {
        contract: {
            'ma': MAStrategy(trader, contract),
            'rsi': RSIStrategy(trader, contract)
        }
        for contract in contracts
    }
    
    # 获取数据并分析
    for contract in contracts:
        logger.info(f"\n分析合约: {contract}")
        
        try:
            candles = trader.get_candlesticks(contract, interval="1h", limit=50)
            
            if candles:
                ma_signal = strategies[contract]['ma'].generate_signal(candles)
                rsi_signal = strategies[contract]['rsi'].generate_signal(candles)
                
                logger.info(f"综合信号 - MA: {ma_signal} | RSI: {rsi_signal}")
                logger.info(f"建议: {get_combined_signal(ma_signal, rsi_signal)}")
        
        except Exception as e:
            logger.error(f"分析 {contract} 失败: {e}")


def get_combined_signal(ma_signal: str, rsi_signal: str) -> str:
    """综合多个信号给出建议"""
    if ma_signal == 'long' and rsi_signal == 'long':
        return "强烈做多"
    elif ma_signal == 'short' and rsi_signal == 'short':
        return "强烈做空"
    elif ma_signal == 'long' or rsi_signal == 'long':
        return "考虑做多"
    elif ma_signal == 'short' or rsi_signal == 'short':
        return "考虑做空"
    else:
        return "观望"


if __name__ == '__main__':
    # 运行示例
    # 注意：需要替换真实的 API_KEY 和 API_SECRET
    
    logger.info("🤖 高级合约交易策略示例\n")
    
    # 取消注释以运行相应的示例
    # example_ma_strategy()
    # example_rsi_strategy()
    example_grid_trading()
    # multi_contract_monitoring()
