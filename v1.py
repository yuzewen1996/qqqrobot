import time
import logging
from decimal import Decimal as D
import gate_api
from gate_api.exceptions import ApiException, GateApiException

# --- 配置部分 ---
API_KEY = "f9c0d44163b9c7227fc2b9b271c394b6"
API_SECRET = "cc7bc07a047abcd26cbef20b4309a8c74955c8605b44914cd9121584ff06843a"
# 如果是实盘，使用 "https://api.gateio.ws/api/v4"
# 如果是测试网，使用 "https://fx-api-testnet.gateio.ws/api/v4"
HOST = "https://api.gateio.ws/api/v4" 

# 交易对配置
CURRENCY_PAIR = "BTC_USDT"
CURRENCY = "USDT"

# 初始化配置
configuration = gate_api.Configuration(
    host=HOST,
    key=API_KEY,
    secret=API_SECRET
)
api_client = gate_api.ApiClient(configuration)
spot_api = gate_api.SpotApi(api_client)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def get_last_price(pair):
    """获取最新成交价"""
    tickers = spot_api.list_tickers(currency_pair=pair)
    return tickers[0].last

def get_balance(currency):
    """获取账户余额"""
    accounts = spot_api.list_spot_accounts(currency=currency)
    if len(accounts) > 0:
        return accounts[0].available
    return "0"

def place_order(pair, side, amount, price):
    """下单函数"""
    order = gate_api.Order(
        currency_pair=pair,
        side=side,        # 'buy' 或 'sell'
        amount=amount,    # 下单数量
        price=price       # 下单价格
    )
    try:
        created = spot_api.create_order(order)
        logger.info(f"下单成功! ID: {created.id}, 状态: {created.status}")
        return created
    except GateApiException as ex:
        logger.error(f"下单失败: {ex.label}, {ex.message}")
    except ApiException as e:
        logger.error(f"API 异常: {e}")

def run_bot():
    """机器人主循环"""
    logger.info("机器人启动...")
    
    while True:
        try:
            # 1. 获取行情
            last_price = get_last_price(CURRENCY_PAIR)
            logger.info(f"当前 {CURRENCY_PAIR} 价格: {last_price}")
            
            # 2. 获取余额
            balance = get_balance(CURRENCY)
            logger.info(f"当前 {CURRENCY} 余额: {balance}")
            
            # --- 3. 这里写你的交易策略逻辑 ---
            # 示例策略：如果价格低于 50000 (仅作演示)，且余额充足，就买入 0.001 BTC
            target_price = D("50000")
            buy_amount = "0.001"
            
            if D(last_price) < target_price and D(balance) > D(last_price) * D(buy_amount):
                 logger.info("价格达到目标，正在买入...")
                 place_order(CURRENCY_PAIR, 'buy', buy_amount, last_price)
            else:
                 logger.info("未满足交易条件，继续等待...")
            
            # 4. 休息一段时间，避免请求太频繁被封 IP
            time.sleep(10) 
            
        except Exception as e:
            logger.error(f"发生错误: {e}")
            time.sleep(5)

if __name__ == '__main__':
    run_bot()