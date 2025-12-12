#!/usr/bin/env python
# coding: utf-8
"""
all_strategies.py
整合全库主要策略类与函数：
- MA移动平均线策略
- RSI相对强弱指标策略
- 网格交易策略
- 分钟级别策略（EMA突破、布林带、动量、MACD、波动率）
"""

from decimal import Decimal as D
from typing import List, Dict, Optional
import logging

# ============ MA移动平均线策略 ============
class MAStrategy:
    """移动平均线交叉策略 (金叉/死叉)"""
    def __init__(self, trader, contract: str):
        self.trader = trader
        self.contract = contract
        self.last_signal = None
    def generate_signal(self, candles: List[Dict]) -> str:
        if len(candles) < 20:
            return 'hold'
        closes = [D(c['close']) for c in candles]
        ma5_list, ma20_list = [], []
        for i in range(len(closes)):
            if i >= 4:
                ma5_list.append(sum(closes[i-4:i+1]) / 5)
            if i >= 19:
                ma20_list.append(sum(closes[i-19:i+1]) / 20)
        if len(ma5_list) < 2 or len(ma20_list) < 2:
            return 'hold'
        ma5_prev, ma5_curr = ma5_list[-2], ma5_list[-1]
        ma20_prev, ma20_curr = ma20_list[-2], ma20_list[-1]
        if ma5_prev <= ma20_prev and ma5_curr > ma20_curr:
            return 'long'
        elif ma5_prev >= ma20_prev and ma5_curr < ma20_curr:
            return 'short'
        else:
            return 'hold'

# ============ RSI策略 ============
class RSIStrategy:
    """RSI相对强度指数策略"""
    def __init__(self, trader, contract: str, period: int = 14):
        self.trader = trader
        self.contract = contract
        self.period = period
    def calculate_rsi(self, candles: List[Dict]) -> float:
        if len(candles) < self.period + 1:
            return 50
        closes = [D(c['close']) for c in candles]
        changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = sum([c for c in changes[-self.period:] if c > 0]) / self.period
        losses = abs(sum([c for c in changes[-self.period:] if c < 0])) / self.period
        if losses == 0:
            return 100 if gains > 0 else 0
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    def generate_signal(self, candles: List[Dict]) -> str:
        rsi = self.calculate_rsi(candles)
        if rsi < 30:
            return 'long'
        elif rsi > 70:
            return 'short'
        else:
            return 'hold'

# ============ 网格交易策略 ============
class GridTradingStrategy:
    """合约网格交易策略"""
    def __init__(self, lower_price: D, upper_price: D, grid_count: int = 10, grid_size: int = 1, leverage: int = 10):
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.grid_count = grid_count
        self.grid_size = grid_size
        self.leverage = leverage
        self.grid_step = (upper_price - lower_price) / grid_count
        self.grids = self._init_grids()
    def _init_grids(self) -> List[Dict]:
        grids = []
        for i in range(self.grid_count + 1):
            price = self.lower_price + self.grid_step * i
            grids.append({'price': price, 'buy_triggered': False, 'sell_triggered': False})
        return grids
    def get_orders(self, current_price: D) -> List[Dict]:
        orders = []
        for grid in self.grids:
            if not grid['buy_triggered'] and current_price <= grid['price']:
                orders.append({'side': 'buy', 'price': grid['price'], 'size': self.grid_size, 'leverage': self.leverage})
                grid['buy_triggered'] = True
            if not grid['sell_triggered'] and current_price >= grid['price']:
                orders.append({'side': 'sell', 'price': grid['price'], 'size': self.grid_size, 'leverage': self.leverage})
                grid['sell_triggered'] = True
        return orders

# ============ 分钟级别策略 ============
# 只整合策略类，不含运行器和Bot
class EMABreakoutStrategy:
    """EMA快速突破策略"""
    def __init__(self, bot, contract: str, fast_period: int = 5, slow_period: int = 13, volume_threshold: float = 1.2):
        self.bot = bot
        self.contract = contract
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.volume_threshold = volume_threshold
    def calculate_ema(self, prices: List[D], period: int) -> List[D]:
        if len(prices) < period:
            return []
        emas = []
        multiplier = D(2) / D(period + 1)
        sma = sum(prices[:period]) / D(period)
        emas.append(sma)
        for price in prices[period:]:
            ema = (price - emas[-1]) * multiplier + emas[-1]
            emas.append(ema)
        return emas
    def generate_signal(self, candles: List[Dict]) -> str:
        if len(candles) < self.slow_period + 5:
            return 'hold'
        closes = [c['close'] for c in candles]
        volumes = [c['volume'] for c in candles]
        fast_ema = self.calculate_ema(closes, self.fast_period)
        slow_ema = self.calculate_ema(closes, self.slow_period)
        if len(fast_ema) < 2 or len(slow_ema) < 2:
            return 'hold'
        fast_prev, fast_curr = fast_ema[-2], fast_ema[-1]
        slow_prev, slow_curr = slow_ema[-2], slow_ema[-1]
        avg_volume = sum(volumes[-20:]) / D(20) if len(volumes) >= 20 else sum(volumes) / D(len(volumes))
        curr_volume = volumes[-1]
        volume_confirmed = curr_volume > avg_volume * D(self.volume_threshold)
        if fast_prev <= slow_prev and fast_curr > slow_curr and volume_confirmed:
            return 'long'
        elif fast_prev >= slow_prev and fast_curr < slow_curr and volume_confirmed:
            return 'short'
        return 'hold'

class BollingerBandsStrategy:
    """布林带突破策略"""
    def __init__(self, bot, contract: str, period: int = 20, std_dev: float = 2.0):
        self.bot = bot
        self.contract = contract
        self.period = period
        self.std_dev = D(std_dev)
    def calculate_bollinger_bands(self, candles: List[Dict]) -> Optional[Dict]:
        if len(candles) < self.period:
            return None
        closes = [c['close'] for c in candles[-self.period:]]
        middle = sum(closes) / D(self.period)
        variance = sum([(price - middle) ** 2 for price in closes]) / D(self.period)
        std = variance ** D('0.5')
        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std
        return {'upper': upper, 'middle': middle, 'lower': lower, 'current': candles[-1]['close']}
    def generate_signal(self, candles: List[Dict]) -> str:
        if len(candles) < self.period + 1:
            return 'hold'
        bb_curr = self.calculate_bollinger_bands(candles)
        bb_prev = self.calculate_bollinger_bands(candles[:-1])
        if not bb_curr or not bb_prev:
            return 'hold'
        price_curr = bb_curr['current']
        price_prev = candles[-2]['close']
        if price_prev <= bb_prev['upper'] and price_curr > bb_curr['upper']:
            return 'long'
        elif price_prev >= bb_prev['lower'] and price_curr < bb_curr['lower']:
            return 'short'
        return 'hold'

class MomentumBreakoutStrategy:
    """动量突破策略"""
    def __init__(self, bot, contract: str, lookback: int = 10, threshold_pct: float = 0.3, volume_multiplier: float = 1.5):
        self.bot = bot
        self.contract = contract
        self.lookback = lookback
        self.threshold_pct = D(threshold_pct) / D(100)
        self.volume_multiplier = D(volume_multiplier)
    def generate_signal(self, candles: List[Dict]) -> str:
        if len(candles) < self.lookback + 1:
            return 'hold'
        historical = candles[-(self.lookback + 1):-1]
        current = candles[-1]
        high_prices = [c['high'] for c in historical]
        low_prices = [c['low'] for c in historical]
        max_high = max(high_prices)
        min_low = min(low_prices)
        current_price = current['close']
        current_high = current['high']
        current_low = current['low']
        avg_price = (max_high + min_low) / D(2)
        volumes = [c['volume'] for c in historical]
        avg_volume = sum(volumes) / D(len(volumes))
        current_volume = current['volume']
        volume_confirmed = current_volume > avg_volume * self.volume_multiplier
        if current_high > max_high:
            breakout_pct = (current_price - max_high) / avg_price
            if breakout_pct >= self.threshold_pct and volume_confirmed:
                return 'long'
        elif current_low < min_low:
            breakout_pct = (min_low - current_price) / avg_price
            if breakout_pct >= self.threshold_pct and volume_confirmed:
                return 'short'
        return 'hold'

class MACDFastStrategy:
    """MACD快速交叉策略"""
    def __init__(self, bot, contract: str, fast: int = 5, slow: int = 13, signal: int = 5):
        self.bot = bot
        self.contract = contract
        self.fast_period = fast
        self.slow_period = slow
        self.signal_period = signal
    def calculate_ema(self, prices: List[D], period: int) -> List[D]:
        if len(prices) < period:
            return []
        emas = []
        multiplier = D(2) / D(period + 1)
        sma = sum(prices[:period]) / D(period)
        emas.append(sma)
        for price in prices[period:]:
            ema = (price - emas[-1]) * multiplier + emas[-1]
            emas.append(ema)
        return emas
    def calculate_macd(self, candles: List[Dict]) -> Optional[Dict]:
        if len(candles) < self.slow_period + self.signal_period:
            return None
        closes = [c['close'] for c in candles]
        fast_ema = self.calculate_ema(closes, self.fast_period)
        slow_ema = self.calculate_ema(closes, self.slow_period)
        if not fast_ema or not slow_ema:
            return None
        min_len = min(len(fast_ema), len(slow_ema))
        fast_ema = fast_ema[-min_len:]
        slow_ema = slow_ema[-min_len:]
        macd_line = [fast_ema[i] - slow_ema[i] for i in range(len(fast_ema))]
        signal_line = self.calculate_ema(macd_line, self.signal_period)
        if not signal_line or len(signal_line) < 2:
            return None
        return {'macd': macd_line[-len(signal_line):], 'signal': signal_line, 'histogram': [macd_line[-len(signal_line):][i] - signal_line[i] for i in range(len(signal_line))]}
    def generate_signal(self, candles: List[Dict]) -> str:
        macd_data = self.calculate_macd(candles)
        if not macd_data or len(macd_data['macd']) < 2:
            return 'hold'
        macd_prev = macd_data['macd'][-2]
        macd_curr = macd_data['macd'][-1]
        signal_prev = macd_data['signal'][-2]
        signal_curr = macd_data['signal'][-1]
        if macd_prev <= signal_prev and macd_curr > signal_curr:
            return 'long'
        elif macd_prev >= signal_prev and macd_curr < signal_curr:
            return 'short'
        return 'hold'

class VolatilityBreakoutStrategy:
    """波动率突破策略"""
    def __init__(self, bot, contract: str, atr_period: int = 14, atr_multiplier: float = 1.5):
        self.bot = bot
        self.contract = contract
        self.atr_period = atr_period
        self.atr_multiplier = D(atr_multiplier)
    def calculate_atr(self, candles: List[Dict]) -> Optional[D]:
        if len(candles) < self.atr_period + 1:
            return None
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_close = candles[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)
        if len(true_ranges) < self.atr_period:
            return None
        atr = sum(true_ranges[-self.atr_period:]) / D(self.atr_period)
        return atr
    def generate_signal(self, candles: List[Dict]) -> str:
        if len(candles) < self.atr_period + 10:
            return 'hold'
        atr = self.calculate_atr(candles)
        if not atr:
            return 'hold'
        closes = [c['close'] for c in candles[-20:]]
        middle = sum(closes) / D(len(closes))
        current_price = candles[-1]['close']
        upper_band = middle + atr * self.atr_multiplier
        lower_band = middle - atr * self.atr_multiplier
        if current_price > upper_band:
            return 'long'
        elif current_price < lower_band:
            return 'short'
        return 'hold'
