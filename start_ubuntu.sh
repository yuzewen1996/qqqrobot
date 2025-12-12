#!/bin/bash
# Ubuntu 服务器快速启动指南

clear

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║    🐧 Ubuntu 自动监控脚本 - 快速启动指南                      ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查是否有配置文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  警告: 未找到 .env 配置文件${NC}"
    echo ""
    echo "请创建 .env 文件:"
    echo ""
    echo "  cat > .env << 'EOF'"
    echo "  GATE_API_KEY=your_api_key_here"
    echo "  GATE_API_SECRET=your_api_secret_here"
    echo "  EOF"
    echo ""
    echo "  chmod 600 .env"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ 配置文件已找到${NC}"
echo ""

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ 虚拟环境存在${NC}"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo -e "${GREEN}✅ 虚拟环境存在${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    echo -e "${GREEN}✅ 虚拟环境已创建${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${BLUE}📋 启动选项${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  前台运行 (推荐测试)"
echo "   python3 auto_stop_loss.py"
echo ""
echo "2️⃣  后台运行 (推荐生产)"
echo "   ./start_background.sh"
echo ""
echo "3️⃣  查看日志"
echo "   tail -f auto_trade.log"
echo ""
echo "4️⃣  停止运行"
echo "   ./stop.sh"
echo ""
echo "5️⃣  完整检查"
echo "   bash check_ubuntu.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}输入您的选择 (1-5):${NC} "
read -r choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}▶️ 前台运行脚本...${NC}"
        echo "按 Ctrl+C 停止"
        echo ""
        python3 auto_stop_loss.py
        ;;
    2)
        echo ""
        echo -e "${GREEN}▶️ 后台启动脚本...${NC}"
        chmod +x start_background.sh
        ./start_background.sh
        echo ""
        echo -e "${GREEN}✅ 脚本已启动${NC}"
        echo ""
        echo "查看日志:"
        echo "  tail -f auto_trade.log"
        echo ""
        echo "查看运行状态:"
        echo "  ps aux | grep auto_stop_loss"
        echo ""
        ;;
    3)
        echo ""
        echo -e "${GREEN}▶️ 显示最后 50 行日志...${NC}"
        echo "(按 Ctrl+C 退出)"
        echo ""
        tail -f auto_trade.log
        ;;
    4)
        echo ""
        echo -e "${GREEN}▶️ 停止脚本...${NC}"
        chmod +x stop.sh
        ./stop.sh
        echo -e "${GREEN}✅ 脚本已停止${NC}"
        ;;
    5)
        echo ""
        echo -e "${GREEN}▶️ 运行完整检查...${NC}"
        echo ""
        chmod +x check_ubuntu.sh
        bash check_ubuntu.sh
        ;;
    *)
        echo -e "${YELLOW}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
