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
        # self.spot_api = gate_api.SpotApi(self.api_client)
        logger.info(f"API客户端已初始化 - 模式: {'测试网' if self.config.USE_TESTNET else '实盘'}")
    
    
    
    



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
                # TODO: Add Futures trading logic here
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
