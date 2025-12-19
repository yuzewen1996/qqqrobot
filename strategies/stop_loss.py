from strategies.base_strategy import BaseStrategy
from core.notifier import logger
from datetime import datetime

class StopLossStrategy(BaseStrategy):
    def __init__(self, exchange, config):
        super().__init__(exchange, config)
        self.name = "StopLossStrategy"
        self.contract = config.get('contract')
        self.stop_loss_price = float(config.get('stop_loss_price', 0))
        self.take_profit_price = float(config.get('take_profit_price', 0))

    def run(self):
        """执行止损止盈检查"""
        if not self.contract:
            logger.warning("未配置合约，跳过检查")
            return

        # 获取当前持仓
        position = self.exchange.get_position(self.contract)
        
        if not position:
            # logger.debug(f"未找到 {self.contract} 持仓") # 减少日志噪音
            return
        
        # 获取当前价格
        current_price = self.exchange.get_current_price(self.contract)
        if current_price == 0:
            logger.error("获取价格失败，跳过本次检查")
            return
        
        # 计算盈亏
        entry_price = position['entry_price']
        size = position['size']
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        is_long = size > 0
        direction = "做多" if is_long else "做空"
        
        logger.info(f"[{self.contract}] {direction} | 价格: {current_price:.4f} | 入场: {entry_price:.4f} | 盈亏: {pnl_pct:+.2f}%")
        
        should_close = False
        reason = ""
        
        if is_long:
            if self.stop_loss_price > 0 and current_price <= self.stop_loss_price:
                should_close = True
                reason = f"触发止损 (价格 {current_price} <= {self.stop_loss_price})"
            elif self.take_profit_price > 0 and current_price >= self.take_profit_price:
                should_close = True
                reason = f"触发止盈 (价格 {current_price} >= {self.take_profit_price})"
        else:
            if self.stop_loss_price > 0 and current_price >= self.stop_loss_price:
                should_close = True
                reason = f"触发止损 (价格 {current_price} >= {self.stop_loss_price})"
            elif self.take_profit_price > 0 and current_price <= self.take_profit_price:
                should_close = True
                reason = f"触发止盈 (价格 {current_price} <= {self.take_profit_price})"
        
        if should_close:
            logger.warning(f"🚨 {reason}")
            self.exchange.close_position(self.contract, size, position['mode'])
