import time
import yaml
from pathlib import Path
from core.exchange import Exchange
from core.notifier import logger
from strategies.stop_loss import StopLossStrategy

class Engine:
    def __init__(self):
        self.config = self.load_config()
        self.exchange = Exchange(settle=self.config.get('settle', 'usdt'))
        self.strategies = []
        self.running = True
        
        # 初始化策略
        self.init_strategies()

    def load_config(self):
        """加载配置文件"""
        config_path = Path("config/settings.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def init_strategies(self):
        """初始化启用的策略"""
        # 目前只硬编码 StopLossStrategy，后续可以根据配置动态加载
        sl_strategy = StopLossStrategy(self.exchange, self.config)
        self.strategies.append(sl_strategy)
        logger.info(f"已加载策略: {[s.name for s in self.strategies]}")

    def start(self):
        """启动主循环"""
        interval = self.config.get('check_interval', 60)
        logger.info(f"引擎启动，检查间隔: {interval}秒")
        
        try:
            while self.running:
                for strategy in self.strategies:
                    try:
                        strategy.run()
                    except Exception as e:
                        logger.error(f"策略 {strategy.name} 执行出错: {e}", exc_info=True)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("收到停止信号，引擎停止")
        except Exception as e:
            logger.error(f"引擎异常退出: {e}", exc_info=True)
