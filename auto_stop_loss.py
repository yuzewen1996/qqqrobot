#!/usr/bin/env python
# coding: utf-8
"""
自动止损止盈监控脚本
功能：
1. 每分钟自动获取行情
2. 检查是否触发止损/止盈条件
3. 自动下市价单平仓
4. 支持服务器后台运行
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal as D
import gate_api
from gate_api.exceptions import ApiException, GateApiException

# ============ 日志配置 ============
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("auto_trade.log", encoding='utf-8'),  # 记录到文件
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# ============ 配置加载 ============
def load_env_config():
    """从环境变量或 .env 文件加载配置"""
    env_paths = [
        Path(__file__).parent / ".env",
        Path("C:/Users/admin/Desktop/gatekey.env"),
        Path("/root/gatekey.env"),  # Linux服务器路径
        Path.home() / "gatekey.env",  # 用户目录
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            logger.info(f"加载配置文件: {env_path}")
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


# ============ 自动交易监控类 ============
class AutoTradingMonitor:
    """自动止损止盈监控器"""
    
    def __init__(self, api_key: str, api_secret: str, settle: str = 'usdt'):
        configuration = gate_api.Configuration(
            host="https://api.gateio.ws/api/v4",
            key=api_key,
            secret=api_secret
        )
        self.api_client = gate_api.ApiClient(configuration)
        self.futures_api = gate_api.FuturesApi(self.api_client)
        self.settle = settle
        self.running = True
        logger.info("=" * 100)
        logger.info("自动交易监控已启动")
        logger.info("=" * 100)
    
    def get_current_price(self, contract: str) -> float:
        """获取当前市价"""
        try:
            ticker = self.futures_api.list_futures_tickers(settle=self.settle, contract=contract)
            if ticker and len(ticker) > 0:
                return float(ticker[0].last)
            return 0
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            return 0
    
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
    
    def close_position(self, contract: str, size: float, mode: str):
        """市价平仓
        
        Args:
            contract: 合约名称
            size: 持仓数量（正数=做多，负数=做空）
            mode: 持仓模式 (dual_long/dual_short/single)
        """
        try:
            # 判断平仓方向
            # 如果是做多(size>0)，平仓需要卖出(size<0)
            # 如果是做空(size<0)，平仓需要买入(size>0)
            close_size = -size
            
            # 确定reduce_only标志
            reduce_only = True
            
            logger.info(f"准备平仓: {contract}")
            logger.info(f"  持仓数量: {size}")
            logger.info(f"  平仓数量: {close_size}")
            logger.info(f"  持仓模式: {mode}")
            
            # 创建市价单
            order = gate_api.FuturesOrder(
                contract=contract,
                size=close_size,
                price="0",  # 市价单价格设为0
                tif="ioc",  # Immediate or Cancel
                reduce_only=reduce_only
            )
            
            # 下单
            result = self.futures_api.create_futures_order(settle=self.settle, futures_order=order)
            
            logger.info("=" * 100)
            logger.info("✅ 平仓订单已提交")
            logger.info(f"  订单ID: {result.id}")
            logger.info(f"  合约: {result.contract}")
            logger.info(f"  数量: {result.size}")
            logger.info(f"  状态: {result.status}")
            logger.info("=" * 100)
            
            return True
            
        except (ApiException, GateApiException) as e:
            logger.error(f"平仓失败: {e}")
            if hasattr(e, 'body'):
                logger.error(f"错误详情: {e.body}")
            return False
    
    def check_and_execute(self, contract: str, stop_loss_price: float, take_profit_price: float):
        """检查价格并执行止损止盈"""
        
        # 获取当前持仓
        position = self.get_position(contract)
        
        if not position:
            logger.warning(f"未找到 {contract} 持仓")
            return False
        
        # 获取当前价格
        current_price = self.get_current_price(contract)
        if current_price == 0:
            logger.error("获取价格失败，跳过本次检查")
            return True
        
        # 计算盈亏
        entry_price = position['entry_price']
        size = position['size']
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        # 判断是做多还是做空
        is_long = size > 0
        
        # 打印当前状态
        direction = "做多" if is_long else "做空"
        logger.info("-" * 100)
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控状态")
        logger.info(f"  合约: {contract} [{direction}]")
        logger.info(f"  持仓数量: {size}")
        logger.info(f"  入场价格: ${entry_price:.6f}")
        logger.info(f"  当前价格: ${current_price:.6f}")
        logger.info(f"  盈亏: {pnl_pct:+.2f}%")
        logger.info(f"  止损价: ${stop_loss_price:.6f}")
        logger.info(f"  止盈价: ${take_profit_price:.6f}")
        
        # 检查止损止盈条件
        should_close = False
        reason = ""
        
        if is_long:
            # 做多仓位
            if current_price <= stop_loss_price:
                should_close = True
                reason = f"触发止损 (价格 ${current_price:.6f} <= 止损价 ${stop_loss_price:.6f})"
            elif current_price >= take_profit_price:
                should_close = True
                reason = f"触发止盈 (价格 ${current_price:.6f} >= 止盈价 ${take_profit_price:.6f})"
        else:
            # 做空仓位
            if current_price >= stop_loss_price:
                should_close = True
                reason = f"触发止损 (价格 ${current_price:.6f} >= 止损价 ${stop_loss_price:.6f})"
            elif current_price <= take_profit_price:
                should_close = True
                reason = f"触发止盈 (价格 ${current_price:.6f} <= 止盈价 ${take_profit_price:.6f})"
        
        if should_close:
            logger.warning("=" * 100)
            logger.warning(f"🚨 {reason}")
            logger.warning("=" * 100)
            
            # 执行平仓
            success = self.close_position(contract, size, position['mode'])
            
            if success:
                logger.info("✅ 自动平仓成功，停止监控")
                return False  # 停止监控
            else:
                logger.error("❌ 自动平仓失败，将在下次循环重试")
        else:
            logger.info("  ✓ 未触发条件，继续监控...")
        
        logger.info("-" * 100)
        return True
    
    def run(self, contract: str, stop_loss_price: float, take_profit_price: float, check_interval: int = 60):
        """
        运行监控循环
        
        Args:
            contract: 合约名称
            stop_loss_price: 止损价格
            take_profit_price: 止盈价格
            check_interval: 检查间隔（秒），默认60秒
        """
        logger.info("=" * 100)
        logger.info("监控参数:")
        logger.info(f"  合约: {contract}")
        logger.info(f"  止损价: ${stop_loss_price:.6f}")
        logger.info(f"  止盈价: ${take_profit_price:.6f}")
        logger.info(f"  检查间隔: {check_interval}秒")
        logger.info(f"  日志文件: auto_trade.log")
        logger.info("=" * 100)
        logger.info("按 Ctrl+C 停止监控\n")
        
        try:
            while self.running:
                # 执行检查
                continue_monitoring = self.check_and_execute(contract, stop_loss_price, take_profit_price)
                
                if not continue_monitoring:
                    # 已平仓，停止监控
                    break
                
                # 等待下次检查
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n收到停止信号，退出监控...")
        except Exception as e:
            logger.error(f"监控过程出错: {e}", exc_info=True)
        finally:
            logger.info("=" * 100)
            logger.info("监控已停止")
            logger.info("=" * 100)


# ============ 主程序 ============
def main():
    """主程序入口"""
    
    # ============ 配置区域 - 请根据实际情况修改 ============
    
    # 合约配置
    CONTRACT = "ASTER_USDT"  # 要监控的合约
    
    # 止损止盈价格（根据分析结果设置）
    STOP_LOSS_PRICE = 0.912    # 止损价: -5%
    TAKE_PROFIT_PRICE = 0.9792  # 止盈价: +2%
    
    # 检查间隔（秒）
    CHECK_INTERVAL = 60  # 每60秒检查一次（1分钟）
    
    # 结算货币
    SETTLE = 'usdt'
    
    # ============ 配置区域结束 ============
    
    try:
        # 加载API密钥
        api_key, api_secret = load_env_config()
        
        # 创建监控器
        monitor = AutoTradingMonitor(api_key, api_secret, settle=SETTLE)
        
        # 开始监控
        monitor.run(
            contract=CONTRACT,
            stop_loss_price=STOP_LOSS_PRICE,
            take_profit_price=TAKE_PROFIT_PRICE,
            check_interval=CHECK_INTERVAL
        )
        
    except ValueError as e:
        logger.error(f"配置错误: {e}")
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)


if __name__ == "__main__":
    main()
