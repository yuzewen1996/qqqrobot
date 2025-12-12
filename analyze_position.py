#!/usr/bin/env python
# coding: utf-8
"""
持仓分析工具 - 分析当前持仓是否应该继续持有
包含技术指标分析：移动平均线、RSI、布林带等
"""

import os
import logging
from pathlib import Path
from decimal import Decimal as D
from typing import List, Dict
import gate_api
from gate_api.exceptions import ApiException, GateApiException
from datetime import datetime

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
    
    def analyze_position(self, contract: str, entry_price: float, current_size: float):
        """分析持仓情况并给出建议"""
        logger.info(f"\n{'='*100}")
        logger.info(f"正在分析 {contract} 持仓...")
        logger.info(f"{'='*100}")
        
        # 获取不同时间周期的K线数据
        candles_1h = self.get_candlesticks(contract, interval='1h', limit=200)
        candles_4h = self.get_candlesticks(contract, interval='4h', limit=100)
        candles_1d = self.get_candlesticks(contract, interval='1d', limit=50)
        
        if not candles_1h or not candles_4h or not candles_1d:
            logger.error("无法获取K线数据")
            return
        
        current_price = candles_1h[-1]['close']
        
        # 提取收盘价
        closes_1h = [c['close'] for c in candles_1h]
        closes_4h = [c['close'] for c in candles_4h]
        closes_1d = [c['close'] for c in candles_1d]
        
        # 计算技术指标
        ma5_1h = self.calculate_ma(closes_1h, 5)
        ma20_1h = self.calculate_ma(closes_1h, 20)
        ma50_1h = self.calculate_ma(closes_1h, 50)
        
        ma5_4h = self.calculate_ma(closes_4h, 5)
        ma20_4h = self.calculate_ma(closes_4h, 20)
        
        rsi_1h = self.calculate_rsi(closes_1h, 14)
        rsi_4h = self.calculate_rsi(closes_4h, 14)
        rsi_1d = self.calculate_rsi(closes_1d, 14)
        
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(closes_1h, 20, 2)
        
        # 价格变化分析
        price_24h_ago = candles_1h[-24]['close'] if len(candles_1h) >= 24 else closes_1h[0]
        price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
        
        price_7d_ago = candles_4h[-42]['close'] if len(candles_4h) >= 42 else closes_4h[0]  # 7天 = 42个4小时
        price_change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
        
        # 持仓盈亏
        profit_loss = ((current_price - entry_price) / entry_price) * 100
        
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
        
        print(f"\n【移动平均线 - 1小时】")
        print(f"  MA5:          ${ma5_1h:.6f}")
        print(f"  MA20:         ${ma20_1h:.6f}")
        print(f"  MA50:         ${ma50_1h:.6f}")
        print(f"  价格 vs MA5:  {((current_price - ma5_1h) / ma5_1h * 100):+.2f}%")
        print(f"  价格 vs MA20: {((current_price - ma20_1h) / ma20_1h * 100):+.2f}%")
        
        print(f"\n【移动平均线 - 4小时】")
        print(f"  MA5:          ${ma5_4h:.6f}")
        print(f"  MA20:         ${ma20_4h:.6f}")
        
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
        
        signals = []
        
        # 1. 均线趋势
        if current_price > ma5_1h > ma20_1h > ma50_1h:
            signals.append(("✅ 多头排列", "强烈看涨", 2))
        elif current_price > ma5_1h > ma20_1h:
            signals.append(("✅ 短期上涨趋势", "看涨", 1))
        elif current_price < ma5_1h < ma20_1h < ma50_1h:
            signals.append(("⚠️ 空头排列", "强烈看跌", -2))
        elif current_price < ma5_1h < ma20_1h:
            signals.append(("⚠️ 短期下跌趋势", "看跌", -1))
        else:
            signals.append(("➖ 震荡行情", "方向不明", 0))
        
        # 2. RSI超买超卖
        if rsi_1h > 70:
            signals.append(("⚠️ RSI超买 (1h)", "可能回调", -1))
        elif rsi_1h < 30:
            signals.append(("✅ RSI超卖 (1h)", "可能反弹", 1))
        
        if rsi_4h > 70:
            signals.append(("⚠️ RSI超买 (4h)", "中期压力", -1))
        elif rsi_4h < 30:
            signals.append(("✅ RSI超卖 (4h)", "中期支撑", 1))
        
        # 3. 布林带位置
        bb_position = (current_price - lower_bb) / (upper_bb - lower_bb) if upper_bb > lower_bb else 0.5
        if bb_position > 0.8:
            signals.append(("⚠️ 接近布林带上轨", "超买区域", -1))
        elif bb_position < 0.2:
            signals.append(("✅ 接近布林带下轨", "超卖区域", 1))
        
        # 4. 均线金叉/死叉
        if ma5_1h > ma20_1h and ma5_4h > ma20_4h:
            signals.append(("✅ 金叉信号", "多头信号", 1))
        elif ma5_1h < ma20_1h and ma5_4h < ma20_4h:
            signals.append(("⚠️ 死叉信号", "空头信号", -1))
        
        for signal_name, description, _ in signals:
            print(f"  {signal_name:30s} -> {description}")
        
        # ============ 综合评分和建议 ============
        total_score = sum(score for _, _, score in signals)
        
        print(f"\n{'='*100}")
        print(f"💡 操作建议")
        print(f"{'='*100}\n")
        
        print(f"  综合评分: {total_score:+d}")
        
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
        
        # 止损止盈建议
        print(f"\n【风险管理建议】")
        if profit_loss > 0:
            stop_loss_price = entry_price * 0.98  # 止损设在入场价下方2%
            take_profit_price = current_price * 1.05  # 止盈设在当前价上方5%
            print(f"  建议止损价:   ${stop_loss_price:.6f} (保护利润)")
            print(f"  建议止盈价:   ${take_profit_price:.6f} (锁定收益)")
        else:
            stop_loss_price = entry_price * 0.95  # 止损设在入场价下方5%
            take_profit_price = entry_price * 1.02  # 止盈设回本价上方2%
            print(f"  建议止损价:   ${stop_loss_price:.6f} (控制亏损)")
            print(f"  建议止盈价:   ${take_profit_price:.6f} (减少亏损)")
        
        print(f"\n{'='*100}\n")


# ============ 主程序 ============
def main():
    try:
        api_key, api_secret = load_env_config()
        analyzer = TechnicalAnalyzer(api_key, api_secret)
        
        # 分析 ASTER_USDT 持仓
        # 根据之前的查询结果: 入场价0.96, 持仓30
        analyzer.analyze_position(
            contract="ASTER_USDT",
            entry_price=0.96,
            current_size=30.0
        )
        
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()
