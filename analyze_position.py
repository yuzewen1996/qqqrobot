#!/usr/bin/env python
# coding: utf-8
"""
持仓分析工具 - 分析当前持仓是否应该继续持有
包含技术指标分析：移动平均线、RSI、布林带等
"""

import os
import logging
from pathlib import Path
from decimal import Decimal as D, getcontext
from typing import List, Dict
import gate_api
from gate_api.exceptions import ApiException, GateApiException
from datetime import datetime
import argparse
import json

# 提高 Decimal 精度
getcontext().prec = 12

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============ 配置加载 ============
def load_env_config():
    """从环境变量或 .env 文件加载配置"""
    env_paths = [
        Path(__file__).parent / ".env",
        Path("C:/Users/admin/Desktop/gatekey.env"),
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
            break
    
    api_key = os.getenv('GATE_API_KEY')
    api_secret = os.getenv('GATE_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError("未找到 API 密钥配置")
    
    return api_key, api_secret


# ============ 技术分析类 ============
class TechnicalAnalyzer:
    """技术分析工具"""
    
    def __init__(self, api_key: str, api_secret: str, settle: str = 'usdt'):
        configuration = gate_api.Configuration(
            host="https://api.gateio.ws/api/v4",
            key=api_key,
            secret=api_secret
        )
        self.api_client = gate_api.ApiClient(configuration)
        self.futures_api = gate_api.FuturesApi(self.api_client)
        self.settle = settle
        logger.info("技术分析工具已初始化")
    
    def get_candlesticks(self, contract: str, interval: str = '1h', limit: int = 200) -> List[Dict]:
        """获取K线数据"""
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
                    'datetime': datetime.fromtimestamp(int(cs.t)),
                    'open': float(cs.o),
                    'close': float(cs.c),
                    'high': float(cs.h),
                    'low': float(cs.l),
                    'volume': float(cs.v) if cs.v else 0
                }
                for cs in candlesticks
            ]
        except (ApiException, GateApiException) as e:
            logger.error(f"获取K线数据失败: {e}")
            return []
    
    def calculate_ma(self, closes: List[float], period: int) -> float:
        """计算移动平均线"""
        if len(closes) < period:
            return 0
        return sum(closes[-period:]) / period
    
    def calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """计算RSI指标"""
        if len(closes) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, closes: List[float], period: int = 20, std_dev: float = 2):
        """计算布林带"""
        if len(closes) < period:
            return None, None, None
        
        ma = self.calculate_ma(closes, period)
        
        # 计算标准差
        variance = sum((x - ma) ** 2 for x in closes[-period:]) / period
        std = variance ** 0.5
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        return upper_band, ma, lower_band

    def calculate_ema(self, closes: List[float], period: int) -> float:
        """计算 EMA，返回最后一个 EMA 值"""
        if not closes or period <= 0:
            return 0.0
        k = 2 / (period + 1)
        ema = closes[0]
        for price in closes[1:]:
            ema = price * k + ema * (1 - k)
        return ema

    def calculate_macd(self, closes: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """计算 MACD 返回 (macd_line, signal_line, histogram) 最新值"""
        if not closes or len(closes) < slow_period:
            return 0.0, 0.0, 0.0
        # 计算快速 EMA 与慢速 EMA序列
        def ema_series(data, period):
            k = 2 / (period + 1)
            emas = [data[0]]
            for price in data[1:]:
                emas.append(price * k + emas[-1] * (1 - k))
            return emas

        fast_emas = ema_series(closes, fast_period)
        slow_emas = ema_series(closes, slow_period)
        # macd line sequence
        macd_line_seq = [f - s for f, s in zip(fast_emas[-len(slow_emas):], slow_emas)] if len(fast_emas) >= len(slow_emas) else [f - s for f, s in zip(fast_emas, slow_emas[-len(fast_emas):])]
        if not macd_line_seq:
            return 0.0, 0.0, 0.0
        # signal line as EMA of macd_line_seq
        signal_emas = ema_series(macd_line_seq, signal_period)
        macd_line = macd_line_seq[-1]
        signal_line = signal_emas[-1] if signal_emas else 0.0
        hist = macd_line - signal_line
        return macd_line, signal_line, hist

    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """计算 ATR（平均真实波幅）"""
        if len(closes) < period + 1 or len(highs) < period + 1 or len(lows) < period + 1:
            return 0.0
        trs = []
        for i in range(1, len(closes)):
            high = highs[i]
            low = lows[i]
            prev_close = closes[i-1]
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            trs.append(tr)
        atr = sum(trs[-period:]) / period
        return atr
    
    def analyze_position(self, contract: str, entry_price: float = 0.0, current_size: float = 0.0, position_obj=None, atr_k: float = 2.0):
        """分析持仓情况并给出建议

        支持直接传入 `position_obj`（Gate API 返回的 position 对象），
        当 `entry_price` 为 0 时会回退到 `mark_price`。
        """
        logger.info(f"\n{'='*100}")
        logger.info(f"正在分析 {contract} 持仓...")
        logger.info(f"{'='*100}")

        # 如果传入 position_obj，则优先从中读取 entry_price/size
        if position_obj is not None:
            try:
                if getattr(position_obj, 'entry_price', None):
                    entry_price = float(position_obj.entry_price)
                if getattr(position_obj, 'size', None):
                    current_size = float(position_obj.size)
                if getattr(position_obj, 'mark_price', None) and (not entry_price or entry_price == 0):
                    # 若 entry_price 无效，回退到 mark_price
                    entry_price = float(position_obj.mark_price)
                    logger.warning(f"position entry_price 为 0，回退使用 mark_price={entry_price}")
            except Exception:
                pass
        
        # 获取不同时间周期的K线数据
        candles_1h = self.get_candlesticks(contract, interval='1h', limit=200)
        candles_4h = self.get_candlesticks(contract, interval='4h', limit=100)
        candles_1d = self.get_candlesticks(contract, interval='1d', limit=50)
        
        if not candles_1h or not candles_4h or not candles_1d:
            logger.error("无法获取K线数据")
            return
        
        current_price = candles_1h[-1]['close']
        
        # 提取收盘价与高低
        closes_1h = [c['close'] for c in candles_1h]
        closes_4h = [c['close'] for c in candles_4h]
        closes_1d = [c['close'] for c in candles_1d]
        highs_1h = [c['high'] for c in candles_1h]
        lows_1h = [c['low'] for c in candles_1h]
        
        # 计算技术指标（使用 EMA 与 MACD）
        ema5_1h = self.calculate_ema(closes_1h, 5)
        ema20_1h = self.calculate_ema(closes_1h, 20)
        ema50_1h = self.calculate_ema(closes_1h, 50)

        ema5_4h = self.calculate_ema(closes_4h, 5)
        ema20_4h = self.calculate_ema(closes_4h, 20)

        macd_1h_line, macd_1h_signal, macd_1h_hist = self.calculate_macd(closes_1h)
        macd_4h_line, macd_4h_signal, macd_4h_hist = self.calculate_macd(closes_4h)
        
        rsi_1h = self.calculate_rsi(closes_1h, 14)
        rsi_4h = self.calculate_rsi(closes_4h, 14)
        rsi_1d = self.calculate_rsi(closes_1d, 14)
        
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(closes_1h, 20, 2)
        # ATR 用于动态止损
        atr_1h = self.calculate_atr(highs_1h, lows_1h, closes_1h, period=14)
        
        # 价格变化分析
        price_24h_ago = candles_1h[-24]['close'] if len(candles_1h) >= 24 else closes_1h[0]
        price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
        
        price_7d_ago = candles_4h[-42]['close'] if len(candles_4h) >= 42 else closes_4h[0]  # 7天 = 42个4小时
        price_change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
        
        # 持仓盈亏（精度用 Decimal）
        try:
            entry_dec = D(str(entry_price))
            current_dec = D(str(current_price))
            profit_loss = float((current_dec - entry_dec) / entry_dec * D('100')) if entry_dec != 0 else 0.0
        except Exception:
            profit_loss = ((current_price - entry_price) / entry_price) * 100 if entry_price else 0.0
        
        # ============ 打印分析结果 ============
        print(f"\n{'='*100}")
        print(f"📊 {contract} 持仓分析报告")
        print(f"{'='*100}\n")
        
        print(f"【基本信息】")
        print(f"  当前价格:     ${current_price:.6f}")
        print(f"  入场价格:     ${entry_price:.6f}")
        print(f"  持仓数量:     {current_size}")
        print(f"  持仓盈亏:     {profit_loss:+.2f}%")
        print(f"  24小时涨跌:   {price_change_24h:+.2f}%")
        print(f"  7天涨跌:      {price_change_7d:+.2f}%")
        
        print(f"\n【指数移动平均 - 1小时】")
        print(f"  EMA5:         ${ema5_1h:.6f}")
        print(f"  EMA20:        ${ema20_1h:.6f}")
        print(f"  EMA50:        ${ema50_1h:.6f}")
        print(f"  价格 vs EMA5: {((current_price - ema5_1h) / ema5_1h * 100):+.2f}%")
        print(f"  价格 vs EMA20:{((current_price - ema20_1h) / ema20_1h * 100):+.2f}%")
        
        print(f"\n【指数移动平均 - 4小时】")
        print(f"  EMA5:         ${ema5_4h:.6f}")
        print(f"  EMA20:        ${ema20_4h:.6f}")
        
        print(f"\n【RSI 指标】")
        print(f"  RSI (1小时):  {rsi_1h:.2f}")
        print(f"  RSI (4小时):  {rsi_4h:.2f}")
        print(f"  RSI (1天):    {rsi_1d:.2f}")
        
        print(f"\n【布林带 (1小时)】")
        print(f"  上轨:         ${upper_bb:.6f}")
        print(f"  中轨:         ${middle_bb:.6f}")
        print(f"  下轨:         ${lower_bb:.6f}")
        print(f"  价格位置:     {((current_price - lower_bb) / (upper_bb - lower_bb) * 100):.1f}%")
        
        # ============ 趋势判断 ============
        print(f"\n{'='*100}")
        print(f"📈 趋势分析")
        print(f"{'='*100}\n")
        
        # ============ 指标打分（加权，使用 EMA 与 MACD） ============
        # 权重可调整
        weights = {
            'ema': 1.0,
            'rsi': 1.0,
            'bb': 0.8,
            'ema_cross': 0.8,
            'macd': 1.0,
        }

        score = 0.0
        reasons = []

        # EMA 趋势评分（1h）
        if current_price > ema5_1h > ema20_1h > ema50_1h:
            score += 2 * weights['ema']; reasons.append('EMA 多头排列')
        elif current_price > ema5_1h > ema20_1h:
            score += 1 * weights['ema']; reasons.append('EMA 短期上涨')
        elif current_price < ema5_1h < ema20_1h < ema50_1h:
            score -= 2 * weights['ema']; reasons.append('EMA 空头排列')
        elif current_price < ema5_1h < ema20_1h:
            score -= 1 * weights['ema']; reasons.append('EMA 短期下跌')
        else:
            reasons.append('EMA 震荡')

        # RSI 得分
        if rsi_1h > 70:
            score -= 1 * weights['rsi']; reasons.append('RSI超买(1h)')
        elif rsi_1h < 30:
            score += 1 * weights['rsi']; reasons.append('RSI超卖(1h)')

        if rsi_4h > 70:
            score -= 1 * weights['rsi']; reasons.append('RSI超买(4h)')
        elif rsi_4h < 30:
            score += 1 * weights['rsi']; reasons.append('RSI超卖(4h)')

        # 布林带位置
        bb_position = (current_price - lower_bb) / (upper_bb - lower_bb) if upper_bb > lower_bb else 0.5
        if bb_position > 0.8:
            score -= 1 * weights['bb']; reasons.append('接近布林上轨')
        elif bb_position < 0.2:
            score += 1 * weights['bb']; reasons.append('接近布林下轨')

        # MACD 得分（1h）
        if macd_1h_line > macd_1h_signal:
            score += 1 * weights['macd']; reasons.append('MACD 看涨')
        elif macd_1h_line < macd_1h_signal:
            score -= 1 * weights['macd']; reasons.append('MACD 看跌')

        # 多周期 EMA 金叉/死叉
        if ema5_1h > ema20_1h and ema5_4h > ema20_4h:
            score += 1 * weights['ema_cross']; reasons.append('多周期 EMA 金叉')
        elif ema5_1h < ema20_1h and ema5_4h < ema20_4h:
            score -= 1 * weights['ema_cross']; reasons.append('多周期 EMA 死叉')

        # 打印理由
        for r in reasons:
            print(f"  - {r}")

        total_score = score

        print(f"\n{'='*100}")
        print(f"💡 操作建议")
        print(f"{'='*100}\n")

        print(f"  综合评分: {total_score:+.2f}")

        if total_score >= 3:
            recommendation = "🟢 强烈建议继续持有"
            reason = "多个技术指标显示强势上涨趋势"
        elif total_score >= 1:
            recommendation = "🟢 建议继续持有"
            reason = "整体趋势偏向看涨"
        elif total_score <= -3:
            recommendation = "🔴 建议平仓离场"
            reason = "多个技术指标显示下跌风险较大"
        elif total_score <= -1:
            recommendation = "🟡 建议减仓或设置止损"
            reason = "出现一些看跌信号，风险增加"
        else:
            recommendation = "🟡 谨慎持有，密切关注"
            reason = "市场方向不明确，建议观望"

        print(f"  {recommendation}")
        print(f"  理由: {reason}")

        # 基于 ATR 的动态止损（对多头）
        if atr_1h and atr_1h > 0:
            try:
                entry_d = D(str(entry_price))
                atr_d = D(str(atr_1h))
                if current_size > 0:
                    stop_loss_price = float(max((entry_d - D(str(atr_k)) * atr_d), D('0')))
                else:
                    stop_loss_price = float(entry_d + D(str(atr_k)) * atr_d)
                take_profit_price = float((D(str(current_price)) + D(str(current_price)) * D('0.05'))) if profit_loss > 0 else float((entry_d * D('1.02')))
            except Exception:
                stop_loss_price = entry_price * 0.98 if profit_loss > 0 else entry_price * 0.95
                take_profit_price = current_price * 1.05 if profit_loss > 0 else entry_price * 1.02
        else:
            stop_loss_price = entry_price * 0.98 if profit_loss > 0 else entry_price * 0.95
            take_profit_price = current_price * 1.05 if profit_loss > 0 else entry_price * 1.02

        print(f"  建议止损价:   ${stop_loss_price:.6f}")
        print(f"  建议止盈价:   ${take_profit_price:.6f}")
        
        print(f"\n{'='*100}\n")

    def analyze_market(self, contract: str, atr_k: float = 2.0):
        """对任意交易对进行买入/卖出分析（即使当前没有持仓）"""
        logger.info(f"\n{'='*100}")
        logger.info(f"正在分析市场信号 {contract} ...")
        logger.info(f"{'='*100}")

        # 获取不同时间周期的K线数据
        candles_1h = self.get_candlesticks(contract, interval='1h', limit=200)
        candles_4h = self.get_candlesticks(contract, interval='4h', limit=100)
        candles_1d = self.get_candlesticks(contract, interval='1d', limit=50)

        if not candles_1h or not candles_4h or not candles_1d:
            logger.error("无法获取K线数据")
            return

        current_price = candles_1h[-1]['close']

        closes_1h = [c['close'] for c in candles_1h]
        closes_4h = [c['close'] for c in candles_4h]
        closes_1d = [c['close'] for c in candles_1d]
        highs_1h = [c['high'] for c in candles_1h]
        lows_1h = [c['low'] for c in candles_1h]

        # 计算指标
        ema5_1h = self.calculate_ema(closes_1h, 5)
        ema20_1h = self.calculate_ema(closes_1h, 20)
        ema50_1h = self.calculate_ema(closes_1h, 50)

        ema5_4h = self.calculate_ema(closes_4h, 5)
        ema20_4h = self.calculate_ema(closes_4h, 20)

        macd_1h_line, macd_1h_signal, macd_1h_hist = self.calculate_macd(closes_1h)
        macd_4h_line, macd_4h_signal, macd_4h_hist = self.calculate_macd(closes_4h)

        rsi_1h = self.calculate_rsi(closes_1h, 14)
        rsi_4h = self.calculate_rsi(closes_4h, 14)
        rsi_1d = self.calculate_rsi(closes_1d, 14)

        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(closes_1h, 20, 2)
        atr_1h = self.calculate_atr(highs_1h, lows_1h, closes_1h, period=14)

        price_24h_ago = candles_1h[-24]['close'] if len(candles_1h) >= 24 else closes_1h[0]
        price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100

        price_7d_ago = candles_4h[-42]['close'] if len(candles_4h) >= 42 else closes_4h[0]
        price_change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100

        # 打印市场分析结果
        print(f"\n{'='*100}")
        print(f"🔎 {contract} 市场分析报告")
        print(f"{'='*100}\n")

        print(f"  当前价格:     ${current_price:.6f}")
        print(f"  24小时涨跌:   {price_change_24h:+.2f}%")
        print(f"  7天涨跌:      {price_change_7d:+.2f}%")

        print(f"\n【EMA】 1小时 EMA5:{ema5_1h:.6f} EMA20:{ema20_1h:.6f} EMA50:{ema50_1h:.6f}")
        print(f"\n【RSI】 1h:{rsi_1h:.2f} 4h:{rsi_4h:.2f} 1d:{rsi_1d:.2f}")
        print(f"\n【布林带】 上:{upper_bb:.6f} 中:{middle_bb:.6f} 下:{lower_bb:.6f}")

        # 评分逻辑与 analyze_position 基本一致，用于判断买/卖/观望
        weights = {'ema':1.0,'rsi':1.0,'bb':0.8,'ema_cross':0.8,'macd':1.0}
        score = 0.0
        reasons = []

        if current_price > ema5_1h > ema20_1h > ema50_1h:
            score += 2 * weights['ema']; reasons.append('EMA 多头排列')
        elif current_price > ema5_1h > ema20_1h:
            score += 1 * weights['ema']; reasons.append('EMA 短期上涨')
        elif current_price < ema5_1h < ema20_1h < ema50_1h:
            score -= 2 * weights['ema']; reasons.append('EMA 空头排列')
        elif current_price < ema5_1h < ema20_1h:
            score -= 1 * weights['ema']; reasons.append('EMA 短期下跌')
        else:
            reasons.append('EMA 震荡')

        if rsi_1h > 70:
            score -= 1 * weights['rsi']; reasons.append('RSI超买(1h)')
        elif rsi_1h < 30:
            score += 1 * weights['rsi']; reasons.append('RSI超卖(1h)')

        if rsi_4h > 70:
            score -= 1 * weights['rsi']; reasons.append('RSI超买(4h)')
        elif rsi_4h < 30:
            score += 1 * weights['rsi']; reasons.append('RSI超卖(4h)')

        bb_position = (current_price - lower_bb) / (upper_bb - lower_bb) if upper_bb > lower_bb else 0.5
        if bb_position > 0.8:
            score -= 1 * weights['bb']; reasons.append('接近布林上轨')
        elif bb_position < 0.2:
            score += 1 * weights['bb']; reasons.append('接近布林下轨')

        if macd_1h_line > macd_1h_signal:
            score += 1 * weights['macd']; reasons.append('MACD 看涨')
        elif macd_1h_line < macd_1h_signal:
            score -= 1 * weights['macd']; reasons.append('MACD 看跌')

        if ema5_1h > ema20_1h and ema5_4h > ema20_4h:
            score += 1 * weights['ema_cross']; reasons.append('多周期 EMA 金叉')
        elif ema5_1h < ema20_1h and ema5_4h < ema20_4h:
            score -= 1 * weights['ema_cross']; reasons.append('多周期 EMA 死叉')

        for r in reasons:
            print(f"  - {r}")

        total_score = score

        print(f"\n{'='*100}")
        print(f"💡 买/卖 建议")
        print(f"{'='*100}\n")
        print(f"  综合评分: {total_score:+.2f}")

        # 对于市场分析，基于评分给出 买/卖/观望
        if total_score >= 1:
            recommendation = "🟢 建议买入"
            reason = "多数指标偏多，适合考虑建仓（小仓位试探）"
        elif total_score <= -1:
            recommendation = "🔴 建议卖出或观望"
            reason = "多数指标偏空，谨慎或考虑做空/离场"
        else:
            recommendation = "🟡 观望"
            reason = "市场方向不明确，建议等待更明确信号"

        print(f"  {recommendation}")
        print(f"  理由: {reason}")

        # 建议下单价位（基于 ATR）
        if atr_1h and atr_1h > 0:
            if total_score >= 1:
                entry_price = current_price
                stop_loss_price = float(max(current_price - atr_k * atr_1h, 0))
                take_profit_price = float(current_price * 1.05)
            elif total_score <= -1:
                entry_price = current_price
                stop_loss_price = float(current_price + atr_k * atr_1h)
                take_profit_price = float(current_price * 0.95)
            else:
                entry_price = current_price
                stop_loss_price = float(max(current_price - atr_k * atr_1h, 0))
                take_profit_price = float(current_price * 1.02)
        else:
            entry_price = current_price
            stop_loss_price = current_price * 0.98
            take_profit_price = current_price * 1.02

        print(f"  建议下单价:   ${entry_price:.6f}")
        print(f"  建议止损价:   ${stop_loss_price:.6f}")
        print(f"  建议止盈价:   ${take_profit_price:.6f}")
        print(f"\n{'='*100}\n")


# ============ 主程序 ============
def main():
    parser = argparse.ArgumentParser(description='基于K线的持仓分析工具')
    parser.add_argument('--contract', '-c', help='只分析指定合约，例如 ASTER_USDT')
    parser.add_argument('--pair', '-p', help='分析指定交易对（无论是否持仓）例如 ASTER_USDT')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式，输入交易对或查看持仓')
    parser.add_argument('--dry-run', action='store_true', help='仅打印分析，不执行任何交易')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='输出格式')
    args = parser.parse_args()

    try:
        api_key, api_secret = load_env_config()
        analyzer = TechnicalAnalyzer(api_key, api_secret)

        # 启动时若未提供参数，则询问用户要分析当前持仓还是其他交易对
        if not (args.pair or args.contract or args.interactive):
            try:
                print("请选择要执行的操作：")
                print("  1) 分析当前持仓")
                print("  2) 分析其他交易对")
                print("  3) 进入交互式模式")
                print("  q) 退出")
                choice = input('> ').strip()
            except (EOFError, KeyboardInterrupt):
                return

            if not choice:
                pass
            elif choice.lower() in ('q', 'quit', 'exit'):
                return
            elif choice == '1':
                # 保持默认，后续代码将分析当前持仓
                pass
            elif choice == '2':
                pair_input = input('请输入交易对（例如 ASTER_USDT）: ').strip()
                if pair_input:
                    args.pair = pair_input
            elif choice == '3':
                args.interactive = True

        # 交互式模式：可反复输入交易对或查看持仓
        if args.interactive:
            print("进入交互式模式。输入交易对（例如 ASTER_USDT）进行市场分析，输入 'positions' 查看持仓，输入 'contract <合约>' 分析指定持仓（若存在），输入 'q' 退出。")
            while True:
                try:
                    cmd = input('> ').strip()
                except (EOFError, KeyboardInterrupt):
                    print('\n退出交互式模式')
                    break

                if not cmd:
                    continue
                if cmd.lower() in ('q', 'quit', 'exit'):
                    print('退出交互式模式')
                    break
                if cmd.lower() == 'positions' or cmd.lower() == 'pos':
                    try:
                        positions = analyzer.futures_api.list_positions(settle=analyzer.settle)
                    except Exception as e:
                        logger.error(f"获取仓位失败: {e}")
                        positions = []

                    any_flag = False
                    for pos in positions:  # type: ignore
                        try:
                            size = float(pos.size) if getattr(pos, 'size', None) else 0.0
                        except Exception:
                            try:
                                size = float(str(pos.to_dict().get('size', 0)))
                            except Exception:
                                size = 0.0
                        if abs(size) <= 0:
                            continue
                        contract = getattr(pos, 'contract', None) or (pos.to_dict().get('contract') if hasattr(pos, 'to_dict') else None)
                        print(f"- {contract}: size={size}")
                        any_flag = True
                    if not any_flag:
                        print('未发现任何有仓位的合约')
                    continue

                if cmd.lower().startswith('contract '):
                    _, _, target = cmd.partition(' ')
                    target = target.strip()
                    if not target:
                        print('请指定合约名称，例如: contract ASTER_USDT')
                        continue
                    # 尝试找到持仓并分析；若无持仓则做市场分析
                    try:
                        positions = analyzer.futures_api.list_positions(settle=analyzer.settle)
                    except Exception as e:
                        logger.error(f"获取仓位失败: {e}")
                        positions = []
                    matched = None
                    for pos in positions:  # type: ignore
                        c = getattr(pos, 'contract', None) or (pos.to_dict().get('contract') if hasattr(pos, 'to_dict') else None)
                        if c == target:
                            matched = pos
                            break
                    if matched:
                        analyzer.analyze_position(contract=target, position_obj=matched)
                    else:
                        print(f'未找到 {target} 的持仓，改为市场分析')
                        analyzer.analyze_market(target)
                    continue

                # 默认将输入视为交易对，执行市场分析
                analyzer.analyze_market(cmd)
            return
        # 如果用户指定了单独的交易对（无论是否持仓），优先进行市场分析
        if args.pair:
            analyzer.analyze_market(args.pair)
        else:
            # 从 Gate Futures API 获取当前持仓并逐个分析
            try:
                positions = analyzer.futures_api.list_positions(settle=analyzer.settle)
            except Exception as e:
                logger.error(f"获取仓位失败: {e}")
                positions = []

            any_analyzed = False
            results = []
            for pos in positions:  # type: ignore
                try:
                    size = float(pos.size) if getattr(pos, 'size', None) else 0.0
                except Exception:
                    try:
                        size = float(str(pos.to_dict().get('size', 0)))
                    except Exception:
                        size = 0.0

                if abs(size) <= 0:
                    continue

                contract = getattr(pos, 'contract', None) or (pos.to_dict().get('contract') if hasattr(pos, 'to_dict') else None)
                if not contract:
                    continue

                if args.contract and args.contract != contract:
                    continue

                any_analyzed = True
                logger.info(f"开始分析仓位: {contract} | size={size}")
                # 将 position 对象传入，分析内部会取 entry_price 或回退到 mark_price
                analyzer.analyze_position(contract=contract, position_obj=pos, current_size=size)

                if args.output == 'json':
                    results.append({'contract': contract, 'size': size})

            if not any_analyzed:
                logger.info("未发现任何有仓位的合约，脚本结束。")

            if args.output == 'json':
                print(json.dumps(results, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()
