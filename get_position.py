#!/usr/bin/env python
# coding: utf-8
"""
仓位信息查询示例
展示如何获取和分析当前的仓位信息
"""

import logging
from v2_improved import GateIOTrader, TradingConfig
from decimal import Decimal as D

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def display_position_info(trader: GateIOTrader):
    """显示仓位信息"""
    logger.info("=" * 70)
    logger.info("📊 当前仓位信息")
    logger.info("=" * 70)
    
    position = trader.get_position_info()
    
    if not position:
        logger.error("❌ 获取仓位信息失败")
        return
    
    # 解析交易对名称
    base = position['base_currency']  # 如BTC
    quote = position['quote_currency']  # 如USDT
    
    # 基础币信息
    logger.info(f"\n💎 {base}币 (基础币)")
    logger.info(f"   可用: {position['base_available']:.8f}")
    logger.info(f"   冻结: {position['base_locked']:.8f}")
    logger.info(f"   总量: {position['base_total']:.8f}")
    
    # 计价币信息
    logger.info(f"\n💵 {quote}币 (计价币)")
    logger.info(f"   可用: {position['quote_available']:.2f}")
    logger.info(f"   冻结: {position['quote_locked']:.2f}")
    logger.info(f"   总量: {position['quote_total']:.2f}")
    
    # 价格和价值信息
    logger.info(f"\n📈 价格和价值")
    logger.info(f"   当前价格: {position['current_price']:.2f} {quote}")
    logger.info(f"   {base}仓位价值: {position['base_position_value']:.2f} {quote}")
    
    # 总资产
    logger.info(f"\n💰 资产汇总")
    logger.info(f"   总资产价值: {position['total_assets']:.2f} {quote}")
    logger.info(f"   仓位占比: {position['position_ratio'] * 100:.2f}%")
    logger.info(f"   现金占比: {(1 - position['position_ratio']) * 100:.2f}%")
    
    logger.info("\n" + "=" * 70)


def display_all_balances(trader: GateIOTrader):
    """显示所有币种的余额"""
    logger.info("=" * 70)
    logger.info("💼 所有币种余额")
    logger.info("=" * 70)
    
    # 这个示例只展示两个主要币种，实际可以获取所有币种
    currencies = ['BTC', 'ETH', 'USDT', 'XRP']
    
    for currency in currencies:
        balance = trader.get_cryptocurrency_balance(currency)
        if balance and balance > 0:
            logger.info(f"{currency}: {balance:.8f}")
    
    logger.info("=" * 70)


def analyze_position(trader: GateIOTrader):
    """分析仓位"""
    logger.info("=" * 70)
    logger.info("🔍 仓位分析")
    logger.info("=" * 70)
    
    position = trader.get_position_info()
    
    if not position:
        logger.error("❌ 无法获取仓位信息")
        return
    
    base = position['base_currency']
    quote = position['quote_currency']
    
    # 分析1: 仓位占比
    position_ratio = position['position_ratio']
    if position_ratio > D('0.8'):
        logger.warning(f"⚠️  仓位过重: {position_ratio * 100:.2f}%")
        logger.info("   建议: 考虑降低仓位或套现")
    elif position_ratio < D('0.2'):
        logger.info(f"✅ 仓位较轻: {position_ratio * 100:.2f}%")
        logger.info("   状态: 现金充足，可以继续建仓")
    else:
        logger.info(f"✅ 仓位合理: {position_ratio * 100:.2f}%")
    
    # 分析2: 可用资金
    available_quote = position['quote_available']
    quote_total = position['quote_total']
    
    logger.info(f"\n💰 流动性分析")
    logger.info(f"   可用{quote}: {available_quote:.2f}")
    logger.info(f"   冻结{quote}: {position['quote_locked']:.2f}")
    
    if available_quote < D('100'):
        logger.warning(f"⚠️  可用{quote}较少，建议清理已完成的订单")
    
    # 分析3: 仓位价值变化
    logger.info(f"\n📊 仓位成分")
    logger.info(f"   {base}仓位价值: {position['base_position_value']:.2f} {quote} "
                f"({position['position_ratio'] * 100:.2f}%)")
    logger.info(f"   {quote}持有量: {position['quote_total']:.2f} {quote} "
                f"({(1 - position['position_ratio']) * 100:.2f}%)")
    
    logger.info("=" * 70)


def main():
    """主程序"""
    # 创建配置
    config = TradingConfig()
    config.USE_TESTNET = True  # 使用测试网
    
    # 创建交易者
    trader = GateIOTrader(config)
    
    # 获取并显示仓位信息
    display_position_info(trader)
    
    # 显示所有余额
    display_all_balances(trader)
    
    # 分析仓位
    analyze_position(trader)


if __name__ == '__main__':
    logger.info("🚀 开始查询仓位信息\n")
    main()
    logger.info("\n✅ 仓位查询完成")
