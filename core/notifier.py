import logging
import os
from pathlib import Path

def setup_logger(name: str = "qqqrobot", log_file: str = "bot.log", level=logging.INFO):
    """配置日志"""
    # 确保日志目录存在
    log_path = Path("logs")
    if not log_path.exists():
        log_path.mkdir(parents=True)
        
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path / log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(name)

logger = setup_logger()
