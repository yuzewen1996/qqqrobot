import time
import yaml
import sys
from pathlib import Path
from core.exchange import Exchange
from core.notifier import logger
from strategies.stop_loss import StopLossStrategy

class Engine:
    def __init__(self):
        try:
            self.config = self.load_config()
            # 允许在配置中覆盖 settle 参数
            self.exchange = Exchange(settle=self.config.get('settle', 'usdt'))
            self.strategies = []
            self.running = True
            
            # 初始化策略
            self.init_strategies()
        except Exception as e:
            logger.critical(f"引擎初始化失败: {e}")
            raise

    def load_config(self):
        """加载配置文件 (使用绝对路径)"""
        # 获取当前文件 (core/engine.py) 的父目录的父目录 (项目根目录)
        root_dir = Path(__file__).parent.parent
        config_path = root_dir / "config" / "settings.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def init_strategies(self):
        """初始化策略"""
        # 1. 加载止损策略 (默认启用，除非配置中明确禁用)
        if self.config.get('enable_stop_loss', True):
            try:
                sl_strategy = StopLossStrategy(self.exchange, self.config)
                self.strategies.append(sl_strategy)
            except Exception as e:
                logger.error(f"加载 StopLossStrategy 失败: {e}")

        if not self.strategies:
            logger.warning("没有加载任何策略！请检查配置文件。")
        else:
            logger.info(f"已加载策略: {[s.name for s in self.strategies]}")

    def start(self):
        """启动主循环"""
        interval = self.config.get('check_interval', 60)
        logger.info(f"引擎启动，检查间隔: {interval}秒")
        
        try:
            while self.running:
                start_time = time.time()
                
                for strategy in self.strategies:
                    try:
                        strategy.run()
                    except Exception as e:
                        logger.error(f"策略 {strategy.name} 执行出错: {e}", exc_info=True)
                
                # 计算需要休眠的时间，扣除策略执行消耗的时间
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    logger.warning(f"策略执行时间过长 ({elapsed:.2f}s)，跳过本次休眠")
                    
        except KeyboardInterrupt:
            logger.info("收到停止信号，引擎停止")
        except Exception as e:
            logger.error(f"引擎异常退出: {e}", exc_info=True)
