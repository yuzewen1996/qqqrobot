#!/usr/bin/env python
# coding: utf-8
"""
自动止损止盈监控脚本 (动态 ATR 版)
功能：
1. 自动获取持仓
2. 根据 ATR 动态计算止损价格
3. 监控价格并自动平仓
"""

import os
import time
import logging
from datetime import datetime
from core.exchange import Exchange
from core.notifier import logger

# ============ 日志配置 ============
# 沿用 core.notifier 的 logger，但可以额外添加文件输出
file_handler = logging.FileHandler("auto_trade.log", encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

class AutoTradingMonitor:
    """自动止损止盈监控器"""
    
    def __init__(self, settle: str = 'usdt'):
        self.exchange = Exchange(settle=settle)
        self.running = True
        logger.info("=" * 100)
        logger.info("自动交易监控已启动 (动态 ATR 模式)")
        logger.info("=" * 100)
    
    def check_and_execute(self, contract: str, atr_k: float = 2.0, take_profit_pct: float = 5.0):
        """检查价格并执行止损止盈"""
        
        # 1. 获取当前持仓
        position = self.exchange.get_position(contract)
        if not position:
            logger.warning(f"未找到 {contract} 持仓，停止监控")
            return False
        
        # 2. 获取当前价格
        current_price = self.exchange.get_current_price(contract)
        if current_price == 0:
            logger.error("获取价格失败，跳过本次检查")
            return True
        
        # 3. 动态计算止损价 (基于 ATR)
        atr = self.exchange.calculate_atr(contract, interval='1h', period=14)
        entry_price = position['entry_price']
        size = position['size']
        is_long = size > 0
        
        if atr > 0:
            # 止损价 = 入场价 +/- (K * ATR)
            if is_long:
                stop_loss_price = entry_price - (atr_k * atr)
                take_profit_price = entry_price * (1 + take_profit_pct / 100)
            else:
                stop_loss_price = entry_price + (atr_k * atr)
                take_profit_price = entry_price * (1 - take_profit_pct / 100)
        else:
            # 如果 ATR 计算失败，使用固定比例 (例如 5%)
            logger.warning("ATR 计算失败，使用固定 5% 止损")
            if is_long:
                stop_loss_price = entry_price * 0.95
                take_profit_price = entry_price * 1.05
            else:
                stop_loss_price = entry_price * 1.05
                take_profit_price = entry_price * 0.95

        # 4. 打印当前状态
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        direction = "做多" if is_long else "做空"
        logger.info("-" * 100)
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控状态")
        logger.info(f"  合约: {contract} [{direction}] | 数量: {size}")
        logger.info(f"  入场: ${entry_price:.6f} | 当前: ${current_price:.6f} | 盈亏: {pnl_pct:+.2f}%")
        logger.info(f"  动态止损价: ${stop_loss_price:.6f} (ATR: {atr:.6f}, K: {atr_k})")
        logger.info(f"  预设止盈价: ${take_profit_price:.6f} ({take_profit_pct}%)")
        
        # 5. 检查触发条件
        should_close = False
        reason = ""
        
        if is_long:
            if current_price <= stop_loss_price:
                should_close = True
                reason = f"触发动态止损 (价格 ${current_price:.6f} <= ${stop_loss_price:.6f})"
            elif current_price >= take_profit_price:
                should_close = True
                reason = f"触发止盈 (价格 ${current_price:.6f} >= ${take_profit_price:.6f})"
        else:
            if current_price >= stop_loss_price:
                should_close = True
                reason = f"触发动态止损 (价格 ${current_price:.6f} >= ${stop_loss_price:.6f})"
            elif current_price <= take_profit_price:
                should_close = True
                reason = f"触发止盈 (价格 ${current_price:.6f} <= ${take_profit_price:.6f})"
        
        if should_close:
            logger.warning("=" * 100)
            logger.warning(f"🚨 {reason}")
            logger.warning("=" * 100)
            
            success = self.exchange.close_position(contract, size, position['mode'])
            if success:
                logger.info("✅ 自动平仓成功")
                return False
            else:
                logger.error("❌ 自动平仓失败，下次循环重试")
        
        return True

    def run(self, contract: str, atr_k: float = 2.0, take_profit_pct: float = 5.0, interval: int = 60):
        """运行监控"""
        try:
            while self.running:
                if not self.check_and_execute(contract, atr_k, take_profit_pct):
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("用户停止监控")
        except Exception as e:
            logger.error(f"监控异常: {e}", exc_info=True)

def main():
    # 配置
    CONTRACT = "ASTER_USDT"  # 修改为你持仓的合约
    ATR_K = 2.0             # ATR 倍数 (越大止损越宽)
    TP_PCT = 5.0            # 止盈比例 (%)
    INTERVAL = 60           # 检查间隔 (秒)

    try:
        monitor = AutoTradingMonitor()
        monitor.run(CONTRACT, atr_k=ATR_K, take_profit_pct=TP_PCT, interval=INTERVAL)
    except Exception as e:
        logger.error(f"程序启动失败: {e}")

if __name__ == "__main__":
    main()
