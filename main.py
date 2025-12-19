#!/usr/bin/env python
# coding: utf-8
"""
QQQRobot 统一入口
"""
import sys
from core.engine import Engine
from core.notifier import logger

def main():
    try:
        engine = Engine()
        engine.start()
    except Exception as e:
        logger.critical(f"程序启动失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
