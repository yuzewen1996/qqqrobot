#!/bin/bash
# 后台运行脚本 (使用 screen 或 nohup)

echo "======================================"
echo "  后台启动监控程序"
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
    pip install -q gate-api python-dotenv
fi

# 后台运行
echo ""
echo "启动程序到后台..."

if command -v screen &> /dev/null; then
    # 使用 screen（推荐）
    screen -d -m -S trading python3 auto_stop_loss.py
    echo "✓ 程序已通过 screen 启动"
    echo "   查看: screen -r trading"
    echo "   停止: screen -X -S trading quit"
else
    # 使用 nohup
    nohup python3 auto_stop_loss.py > output.log 2>&1 &
    PID=$!
    echo "✓ 程序已通过 nohup 启动"
    echo "  进程ID: $PID"
    echo "  日志文件: auto_trade.log"
    echo "  输出文件: output.log"
    echo "  查看日志: tail -f auto_trade.log"
    echo "  停止程序: kill $PID"
    echo "$PID" > bot.pid
fi

echo ""
