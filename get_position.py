#!/usr/bin/env python
# coding: utf-8
"""
Position Information Query Script
Displays current holdings and asset breakdown
"""

import logging
from v2_improved import GateIOTrader, TradingConfig
from decimal import Decimal as D

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def display_position_info(trader: GateIOTrader):
    """Display comprehensive position information"""
    logger.info("=" * 70)
    logger.info("[Position Info]")
    logger.info("=" * 70)
    
    position = trader.get_position_info()
    
    if not position:
        logger.error("[ERROR] Failed to get position info")
        return
    
    base = position['base_currency']
    quote = position['quote_currency']
    
    logger.info(f"\n[{base} Coin] (Base Currency)")
    logger.info(f"   Available: {position['base_available']:.8f}")
    logger.info(f"   Locked: {position['base_locked']:.8f}")
    logger.info(f"   Total: {position['base_total']:.8f}")
    
    logger.info(f"\n[{quote} Coin] (Quote Currency)")
    logger.info(f"   Available: {position['quote_available']:.2f}")
    logger.info(f"   Locked: {position['quote_locked']:.2f}")
    logger.info(f"   Total: {position['quote_total']:.2f}")
    
    logger.info(f"\n[Price and Value]")
    logger.info(f"   Current Price: {position['current_price']:.2f} {quote}")
    logger.info(f"   {base} Position Value: {position['base_position_value']:.2f} {quote}")
    
    logger.info(f"\n[Assets Summary]")
    logger.info(f"   Total Assets: {position['total_assets']:.2f} {quote}")
    logger.info(f"   Position Ratio: {position['position_ratio'] * 100:.2f}%")
    logger.info(f"   Cash Ratio: {(1 - position['position_ratio']) * 100:.2f}%")
    
    logger.info("\n" + "=" * 70)


def display_all_balances(trader: GateIOTrader):
    """Display all cryptocurrency balances"""
    logger.info("=" * 70)
    logger.info("[All Balances]")
    logger.info("=" * 70)
    
    currencies = ['BTC', 'ETH', 'USDT', 'XRP']
    
    for currency in currencies:
        balance = trader.get_cryptocurrency_balance(currency)
        if balance and balance > 0:
            logger.info(f"{currency}: {balance:.8f}")
    
    logger.info("=" * 70)


def analyze_position(trader: GateIOTrader):
    """Analyze and provide recommendations for position"""
    logger.info("=" * 70)
    logger.info("[Position Analysis]")
    logger.info("=" * 70)
    
    position = trader.get_position_info()
    
    if not position:
        logger.error("[ERROR] Unable to get position info")
        return
    
    base = position['base_currency']
    quote = position['quote_currency']
    
    # Analysis 1: Position ratio
    position_ratio = position['position_ratio']
    if position_ratio > D('0.8'):
        logger.warning(f"[WARNING] Heavy position: {position_ratio * 100:.2f}%")
        logger.info("   Suggestion: Consider reducing position or taking profit")
    elif position_ratio < D('0.2'):
        logger.info(f"[OK] Light position: {position_ratio * 100:.2f}%")
        logger.info("   Status: Sufficient cash, can continue to build position")
    else:
        logger.info(f"[OK] Balanced position: {position_ratio * 100:.2f}%")
    
    # Analysis 2: Available liquidity
    available_quote = position['quote_available']
    
    logger.info(f"\n[Liquidity Analysis]")
    logger.info(f"   Available {quote}: {available_quote:.2f}")
    logger.info(f"   Locked {quote}: {position['quote_locked']:.2f}")
    
    if available_quote < D('100'):
        logger.warning(f"[WARNING] Low available {quote}, check pending orders")
    
    # Analysis 3: Position composition
    logger.info(f"\n[Position Composition]")
    logger.info(f"   {base} Position Value: {position['base_position_value']:.2f} {quote} "
                f"({position['position_ratio'] * 100:.2f}%)")
    logger.info(f"   {quote} Holdings: {position['quote_total']:.2f} {quote} "
                f"({(1 - position['position_ratio']) * 100:.2f}%)")
    
    logger.info("=" * 70)


def main():
    """Main function"""
    config = TradingConfig()
    config.USE_TESTNET = True
    
    trader = GateIOTrader(config)
    
    display_position_info(trader)
    display_all_balances(trader)
    analyze_position(trader)


if __name__ == '__main__':
    logger.info("[START] Querying position information\n")
    main()
    logger.info("\n[OK] Position query completed")
