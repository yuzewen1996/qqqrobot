#!/bin/bash
# 停止后台运行的监控程序

if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    echo "停止进程 $PID ..."
    kill $PID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "程序已停止"
        rm bot.pid
    else
        echo "未找到运行中的进程，尝试查找..."
        pkill -f auto_stop_loss.py
        rm bot.pid
        echo "清理完成"
    fi
else
    echo "未找到 bot.pid 文件，尝试查找进程..."
    PID=$(ps aux | grep auto_stop_loss.py | grep -v grep | awk '{print $2}')
    if [ -n "$PID" ]; then
        echo "找到进程 $PID，停止中..."
        kill $PID
        echo "程序已停止"
    else
        echo "未找到运行中的程序"
    fi
fi
