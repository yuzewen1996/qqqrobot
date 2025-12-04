#!/usr/bin/env python
# coding: utf-8
"""
测试脚本 - 验证所有功能是否正常工作
运行此脚本来测试机器人的各项功能
"""

import sys
import logging
from decimal import Decimal as D

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_imports():
    """测试依赖包导入"""
    logger.info("=" * 60)
    logger.info("测试1: 检查依赖包")
    logger.info("=" * 60)
    
    try:
        import gate_api
        logger.info("✅ gate_api 导入成功")
        logger.info(f"   版本信息: {gate_api.__version__ if hasattr(gate_api, '__version__') else '未知'}")
    except ImportError as e:
        logger.error("❌ gate_api 导入失败")
        logger.error(f"   错误: {e}")
        logger.info("   请运行: pip install gate-api")
        return False
    
    try:
        from v2_improved import GateIOTrader, TradingConfig, TradingStrategy
        logger.info("✅ 项目模块导入成功")
    except ImportError as e:
        logger.error("❌ 项目模块导入失败")
        logger.error(f"   错误: {e}")
        return False
    
    return True


def test_decimal():
    """测试Decimal精度"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 检查Decimal精度")
    logger.info("=" * 60)
    
    # 浮点数精度问题
    float_result = 0.1 + 0.2
    logger.info(f"⚠️  浮点数: 0.1 + 0.2 = {float_result}")
    logger.info(f"   (应该是0.3，但得到: {float_result})")
    
    # Decimal精度
    decimal_result = D("0.1") + D("0.2")
    logger.info(f"✅ Decimal: D('0.1') + D('0.2') = {decimal_result}")
    
    if decimal_result == D("0.3"):
        logger.info("✅ Decimal精度测试通过")
        return True
    else:
        logger.error("❌ Decimal精度测试失败")
        return False


def test_config():
    """测试配置类"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 检查配置类")
    logger.info("=" * 60)
    
    try:
        from v2_improved import TradingConfig
        
        config = TradingConfig()
        
        # 检查必要的配置项
        required_attrs = [
            'API_KEY', 'API_SECRET', 'CURRENCY_PAIR', 
            'BUY_AMOUNT', 'SELL_AMOUNT', 'CHECK_INTERVAL'
        ]
        
        for attr in required_attrs:
            if hasattr(config, attr):
                value = getattr(config, attr)
                logger.info(f"✅ {attr}: {value}")
            else:
                logger.error(f"❌ 缺少必要配置: {attr}")
                return False
        
        logger.info("✅ 配置类测试通过")
        return True
    
    except Exception as e:
        logger.error(f"❌ 配置类测试失败: {e}")
        return False


def test_api_connection(use_testnet=True):
    """测试API连接"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 检查API连接")
    logger.info("=" * 60)
    
    try:
        from v2_improved import GateIOTrader, TradingConfig
        import gate_api
        
        # 使用测试密钥测试连接
        config = TradingConfig()
        config.USE_TESTNET = use_testnet
        
        logger.info(f"📡 正在连接 {'测试网' if use_testnet else '实盘'}...")
        
        # 尝试创建API客户端
        trader = GateIOTrader(config)
        logger.info("✅ API客户端创建成功")
        
        # 如果API密钥是默认值，提醒用户
        if config.API_KEY == "你的_API_KEY":
            logger.warning("⚠️  API密钥未配置（使用了默认值）")
            logger.info("   请在 TradingConfig 中设置真实的 API_KEY 和 API_SECRET")
            return True
        
        # 尝试获取行情（公开API，无需认证）
        try:
            ticker = trader.get_ticker()
            if ticker:
                logger.info(f"✅ 获取行情成功")
                logger.info(f"   {config.CURRENCY_PAIR}: {ticker['last']} USDT")
                return True
            else:
                logger.warning("⚠️  获取行情返回为空")
                return False
        
        except Exception as e:
            logger.error(f"❌ 获取行情失败: {e}")
            logger.info("   可能原因:")
            logger.info("   - API密钥无效")
            logger.info("   - 网络连接问题")
            logger.info("   - API服务暂时不可用")
            return False
    
    except Exception as e:
        logger.error(f"❌ API连接测试失败: {e}")
        return False


def test_strategies():
    """测试策略类"""
    logger.info("\n" + "=" * 60)
    logger.info("测试5: 检查策略类")
    logger.info("=" * 60)
    
    try:
        from advanced_strategies import MAStrategy, RSIStrategy, GridTradingStrategy
        
        logger.info("✅ MAStrategy 导入成功")
        logger.info("✅ RSIStrategy 导入成功")
        logger.info("✅ GridTradingStrategy 导入成功")
        
        # 测试网格交易
        strategy = GridTradingStrategy(
            lower_price=D("40000"),
            upper_price=D("60000"),
            grid_count=10
        )
        logger.info(f"✅ 网格策略创建成功")
        logger.info(f"   网格数: {len(strategy.grids)}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ 策略类测试失败: {e}")
        return False


def test_config_examples():
    """测试配置示例"""
    logger.info("\n" + "=" * 60)
    logger.info("测试6: 检查配置示例")
    logger.info("=" * 60)
    
    try:
        from config_examples import (
            ConservativeConfig, BalancedConfig, AggressiveConfig,
            DayTradingConfig, LongTermConfig, get_config
        )
        
        configs = [
            ('conservative', ConservativeConfig()),
            ('balanced', BalancedConfig()),
            ('aggressive', AggressiveConfig()),
        ]
        
        for name, config in configs:
            logger.info(f"✅ {name.upper()}配置:")
            logger.info(f"   买入价: {config.TARGET_BUY_PRICE}")
            logger.info(f"   卖出价: {config.TARGET_SELL_PRICE}")
        
        # 测试工厂函数
        config = get_config('balanced')
        logger.info(f"✅ 工厂函数 get_config('balanced') 调用成功")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ 配置示例测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 开始运行测试套件\n")
    
    tests = [
        ("依赖包", test_imports),
        ("Decimal精度", test_decimal),
        ("配置类", test_config),
        ("API连接", lambda: test_api_connection(use_testnet=True)),
        ("策略类", test_strategies),
        ("配置示例", test_config_examples),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name}测试发生异常: {e}")
            results.append((test_name, False))
    
    # 打印总结
    logger.info("\n" + "=" * 60)
    logger.info("📊 测试总结")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n总体: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("\n🎉 所有测试通过！")
        logger.info("✨ 您的环境已准备好运行交易机器人")
        logger.info("\n下一步:")
        logger.info("1. 配置 API_KEY 和 API_SECRET")
        logger.info("2. 修改交易参数（目标价格、交易量等）")
        logger.info("3. 使用 USE_TESTNET = True 在测试网测试")
        logger.info("4. 运行: python v2_improved.py")
        return 0
    else:
        logger.info(f"\n❌ 有 {total - passed} 个测试失败")
        logger.info("请根据上面的错误信息进行修复")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
