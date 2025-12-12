#!/usr/bin/env python
# coding: utf-8
"""
配置示例文件 - 展示不同的交易配置方案
请根据需要复制相应的配置类到你的代码中
"""

# from v2_improved import TradingConfig, GateIOTrader, TradingStrategy, run_bot
from decimal import Decimal as D


# ============ 配置方案1: 保守型交易 ============
class ConservativeConfig:
    """保守型 - 低风险，低收益"""
    # 资金管理
    BUY_AMOUNT = D("0.001")           # 较小的单笔交易量
    SELL_AMOUNT = D("0.001")
    
    # 策略参数
    TARGET_BUY_PRICE = D("45000")     # 偏低的买入价格
    TARGET_SELL_PRICE = D("48000")    # 保守的卖出目标
    
    # 运行参数
    CHECK_INTERVAL = 30               # 检查频率较低
    USE_TESTNET = False               # 实盘运行


# ============ 配置方案2: 平衡型交易 ============
class BalancedConfig:
    """平衡型 - 中等风险，中等收益（推荐新手）"""
    # 资金管理
    BUY_AMOUNT = D("0.005")
    SELL_AMOUNT = D("0.005")
    
    # 策略参数
    TARGET_BUY_PRICE = D("50000")     # 中等买入价格
    TARGET_SELL_PRICE = D("55000")    # 中等收益目标
    
    # 运行参数
    CHECK_INTERVAL = 15
    USE_TESTNET = True                # 测试网运行


# ============ 配置方案3: 激进型交易 ============
class AggressiveConfig:
    """激进型 - 高风险，高收益（仅供高手）"""
    # 资金管理
    BUY_AMOUNT = D("0.01")            # 较大的单笔交易量
    SELL_AMOUNT = D("0.01")
    
    # 策略参数
    TARGET_BUY_PRICE = D("52000")     # 相对高的买入价格
    TARGET_SELL_PRICE = D("54000")    # 快速小幅盈利
    
    # 运行参数
    CHECK_INTERVAL = 5                # 频繁检查
    USE_TESTNET = False               # 实盘运行


# ============ 配置方案4: 多币种交易 ============
class MultiPairConfig:
    """多币种配置 - 同时交易多个币种"""
    
    pairs = [
        {
            'pair': 'BTC_USDT',
            'buy': D("50000"),
            'sell': D("55000"),
            'amount': D("0.001")
        },
        {
            'pair': 'ETH_USDT',
            'buy': D("3000"),
            'sell': D("3500"),
            'amount': D("0.1")
        },
        {
            'pair': 'XRP_USDT',
            'buy': D("0.5"),
            'sell': D("0.6"),
            'amount': D("10")
        }
    ]


# ============ 配置方案5: 日间交易配置 ============
class DayTradingConfig:
    """日间交易 - 在工作时间内进行频繁交易"""
    BUY_AMOUNT = D("0.001")
    SELL_AMOUNT = D("0.001")
    
    # 每天的交易时间段 (24小时制)
    TRADING_START_HOUR = 9
    TRADING_END_HOUR = 17
    
    # 快速进出
    TARGET_BUY_PRICE = D("50000")
    TARGET_SELL_PRICE = D("50500")    # 只追求1%的快速利润
    
    CHECK_INTERVAL = 5                # 5秒检查一次
    USE_TESTNET = True


# ============ 配置方案6: 长期持仓配置 ============
class LongTermConfig:
    """长期持仓 - 看好长期趋势"""
    BUY_AMOUNT = D("0.1")             # 一次性买入较多
    SELL_AMOUNT = D("0.05")           # 分次卖出
    
    # 长期目标
    TARGET_BUY_PRICE = D("45000")     # 低价时建仓
    TARGET_SELL_PRICE = D("80000")    # 远期目标
    
    CHECK_INTERVAL = 3600             # 每小时检查一次
    USE_TESTNET = False


# ============ 配置方案7: 网格交易配置 ============
class GridTradingConfig:
    """网格交易 - 在价格区间内进行网格化交易"""
    
    # 网格参数
    GRID_LOWER = D("48000")           # 网格下限
    GRID_UPPER = D("52000")           # 网格上限
    GRID_COUNT = 20                   # 20条网格
    GRID_AMOUNT = D("0.001")          # 每条网格的交易量
    
    BUY_AMOUNT = D("0.001")
    SELL_AMOUNT = D("0.001")
    
    CHECK_INTERVAL = 10
    USE_TESTNET = True


# ============ 配置工厂函数 ============
def get_config(config_type: str):
    """获取配置
    
    Args:
        config_type: 配置类型
            - 'conservative': 保守型
            - 'balanced': 平衡型
            - 'aggressive': 激进型
            - 'day_trading': 日间交易
            - 'long_term': 长期持仓
    
    Returns:
        配置对象
    """
    configs = {
        'conservative': ConservativeConfig(),
        'balanced': BalancedConfig(),
        'aggressive': AggressiveConfig(),
        'day_trading': DayTradingConfig(),
        'long_term': LongTermConfig(),
    }
    
    config = configs.get(config_type)
    if config is None:
        raise ValueError(f"未知的配置类型: {config_type}")
    
    return config


# ============ 使用示例 ============
if __name__ == '__main__':
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 选择一个配置
    logger.info("=" * 60)
    logger.info("配置示例展示")
    logger.info("=" * 60)
    
    # 方法1: 直接使用预定义配置
    config = get_config('balanced')
    logger.info(f"\n✓ 已选择: 平衡型配置")
    logger.info(f"  买入价: {config.TARGET_BUY_PRICE}")
    logger.info(f"  卖出价: {config.TARGET_SELL_PRICE}")
    logger.info(f"  单笔量: {config.BUY_AMOUNT}")
    logger.info(f"  检查间隔: {config.CHECK_INTERVAL}秒")
    
    # 方法2: 自定义配置
    class CustomConfig:
        API_KEY = "YOUR_API_KEY"
        API_SECRET = "YOUR_API_SECRET"
        CURRENCY_PAIR = "ETH_USDT"
        TARGET_BUY_PRICE = D("3000")
        TARGET_SELL_PRICE = D("3500")
        BUY_AMOUNT = D("0.1")
        SELL_AMOUNT = D("0.1")
        USE_TESTNET = True
    
    logger.info(f"\n✓ 自定义配置示例")
    logger.info(f"  交易对: {CustomConfig.CURRENCY_PAIR}")
    logger.info(f"  买入价: {CustomConfig.TARGET_BUY_PRICE}")
    
    # 方法3: 运行机器人（需要配置真实的API密钥）
    # logger.info(f"\n开始运行机器人...")
    # run_bot(config)
    
    logger.info("\n" + "=" * 60)
    logger.info("提示: 请修改API密钥后再运行机器人")
    logger.info("=" * 60)
