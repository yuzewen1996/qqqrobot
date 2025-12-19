import os
import gate_api
from typing import List, Dict
from datetime import datetime
from gate_api.exceptions import ApiException, GateApiException
from core.notifier import logger
from pathlib import Path
from dotenv import load_dotenv

class Exchange:
    """交易所 API 封装"""
    
    def __init__(self, settle: str = 'usdt'):
        self.load_keys()
        self.settle = settle
        
        configuration = gate_api.Configuration(
            host="https://api.gateio.ws/api/v4",
            key=self.api_key,
            secret=self.api_secret
        )
        self.api_client = gate_api.ApiClient(configuration)
        self.futures_api = gate_api.FuturesApi(self.api_client)
        logger.info("交易所 API 初始化完成")

    def load_keys(self):
        """加载 API 密钥"""
        # 尝试加载 config/.env
        env_path = Path("config/.env")
        if env_path.exists():
            load_dotenv(env_path)
        
        self.api_key = os.getenv('GATE_API_KEY')
        self.api_secret = os.getenv('GATE_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            # 尝试其他路径 (兼容旧逻辑)
            other_paths = [
                Path("C:/Users/admin/Desktop/gatekey.env"),
                Path("/root/gatekey.env"),
                Path.home() / "gatekey.env",
            ]
            for p in other_paths:
                if p.exists():
                    load_dotenv(p)
                    self.api_key = os.getenv('GATE_API_KEY')
                    self.api_secret = os.getenv('GATE_API_SECRET')
                    if self.api_key and self.api_secret:
                        break
                        
        if not self.api_key or not self.api_secret:
            raise ValueError("未找到 API 密钥配置 (GATE_API_KEY, GATE_API_SECRET)")

    def get_current_price(self, contract: str) -> float:
        """获取当前市价"""
        try:
            ticker = self.futures_api.list_futures_tickers(settle=self.settle, contract=contract)
            if ticker and len(ticker) > 0:
                return float(ticker[0].last)
            return 0.0
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            return 0.0

    def get_position(self, contract: str):
        """获取当前持仓"""
        try:
            positions = self.futures_api.list_positions(settle=self.settle)
            for pos in positions:
                if pos.contract == contract:
                    size = float(pos.size) if pos.size else 0
                    if abs(size) > 0:
                        return {
                            'contract': pos.contract,
                            'size': size,
                            'entry_price': float(pos.entry_price) if pos.entry_price else 0,
                            'mark_price': float(pos.mark_price) if pos.mark_price else 0,
                            'unrealised_pnl': float(pos.unrealised_pnl) if pos.unrealised_pnl else 0,
                            'mode': pos.mode,
                            'leverage': float(pos.leverage) if pos.leverage else 0
                        }
            return None
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return None

    def close_position(self, contract: str, size: float, mode: str) -> bool:
        """市价平仓"""
        try:
            close_size = -size
            reduce_only = True
            
            logger.info(f"执行平仓: {contract}, 数量: {close_size}")
            
            order = gate_api.FuturesOrder(
                contract=contract,
                size=close_size,
                price="0",
                tif="ioc",
                reduce_only=reduce_only
            )
            
            result = self.futures_api.create_futures_order(settle=self.settle, futures_order=order)
            logger.info(f"平仓订单已提交: ID={result.id}, 状态={result.status}")
            return True
            
        except (ApiException, GateApiException) as e:
            logger.error(f"平仓失败: {e}")
            if hasattr(e, 'body'):
                logger.error(f"错误详情: {e.body}")
            return False

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

    def calculate_atr(self, contract: str, interval: str = '1h', period: int = 14) -> float:
        """计算 ATR (平均真实波幅)"""
        candles = self.get_candlesticks(contract, interval=interval, limit=period + 1)
        if len(candles) < period + 1:
            logger.warning(f"K线数据不足，无法计算 ATR (需要 {period+1}, 实际 {len(candles)})")
            return 0.0
        
        tr_list = []
        for i in range(1, len(candles)):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_close = candles[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_list.append(tr)
            
        if not tr_list:
            return 0.0
            
        return sum(tr_list[-period:]) / period
