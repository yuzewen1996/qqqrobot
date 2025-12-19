#!/bin/bash
# Linux/Mac 启动脚本

echo "======================================"
echo "  自动止损止盈监控 - 启动脚本"
echo "======================================"

echo ""
echo "检查虚拟环境..."

# 尝试激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
elif [ -f ".venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source .venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo "⚠ 未找到虚拟环境，使用系统 Python"
fi

# 检查依赖
echo ""
echo "检查依赖..."
pip list 2>/dev/null | grep -i gate-api > /dev/null
if [ $? -ne 0 ]; then
    echo "安装缺失的依赖..."
    pip install gate-api python-dotenv
    if [ $? -ne 0 ]; then
        echo "✗ 依赖安装失败"
        exit 1
    fi
fi
echo "✓ 依赖检查完成"

# 启动程序
echo ""
echo "启动监控程序..."
python3 auto_stop_loss.py
