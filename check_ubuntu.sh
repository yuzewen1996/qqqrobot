#!/bin/bash
# Ubuntu 服务器 - 自动监控脚本检查工具
# 用于验证脚本在 Linux 环境下是否可以正常运行

set -e

echo ""
echo "======================================================================="
echo "  🐧 Ubuntu 服务器 - 自动监控脚本检查工具"
echo "======================================================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_passed=0
check_total=0

# 检查函数
check_item() {
    check_total=$((check_total + 1))
    local name="$1"
    local cmd="$2"
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 检查$check_total: $name${NC}"
        check_passed=$((check_passed + 1))
        return 0
    else
        echo -e "${RED}❌ 检查$check_total: $name${NC}"
        return 1
    fi
}

print_section() {
    echo ""
    echo "======================================================================="
    echo "  $1"
    echo "======================================================================="
}

# 检查1: 操作系统
print_section "📋 检查1: 操作系统信息"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "操作系统: $NAME $VERSION_ID"
    echo -e "${GREEN}✅${NC} Ubuntu/Linux 系统检测成功"
else
    echo -e "${YELLOW}⚠️${NC}  无法检测操作系统版本"
fi

# 检查2: Python 环境
print_section "🐍 检查2: Python 环境"
check_item "Python3 已安装" "command -v python3"

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION"

# 检查3: 虚拟环境
print_section "🔧 检查3: 虚拟环境"

VENV_PATH=""
if [ -d ".venv" ]; then
    VENV_PATH=".venv"
    echo -e "${GREEN}✅${NC} 虚拟环境位置: .venv"
elif [ -d "venv" ]; then
    VENV_PATH="venv"
    echo -e "${GREEN}✅${NC} 虚拟环境位置: venv"
else
    echo -e "${RED}❌${NC} 未找到虚拟环境"
    echo "    请运行: python3 -m venv .venv"
    exit 1
fi

# 检查4: 依赖包
print_section "📦 检查4: Python 依赖包"

if [ -n "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
fi

echo "检查依赖包..."
check_item "gate-api" "python3 -c 'import gate_api'"
check_item "python-dotenv" "python3 -c 'import dotenv'"
check_item "requests" "python3 -c 'import requests'"

# 检查5: 配置文件
print_section "📁 检查5: 配置文件"

CONFIG_FOUND=0
CONFIG_PATH=""

for path in ".env" "gatekey.env" "/root/gatekey.env" "$HOME/gatekey.env"; do
    if [ -f "$path" ]; then
        echo -e "${GREEN}✅${NC} 找到配置文件: $path"
        CONFIG_PATH="$path"
        CONFIG_FOUND=1
        
        # 检查配置文件内容
        if grep -q "GATE_API_KEY" "$path" && grep -q "GATE_API_SECRET" "$path"; then
            echo -e "${GREEN}✅${NC} 配置文件内容完整"
        else
            echo -e "${RED}❌${NC} 配置文件不完整 (缺少 API 密钥或密钥)"
            CONFIG_FOUND=0
        fi
        break
    fi
done

if [ $CONFIG_FOUND -eq 0 ]; then
    echo -e "${RED}❌${NC} 未找到有效的配置文件"
    echo "    请创建 .env 文件，内容如下:"
    echo "    GATE_API_KEY=your_key"
    echo "    GATE_API_SECRET=your_secret"
fi

# 检查6: 脚本文件
print_section "🎯 检查6: 脚本文件"

if [ -f "auto_stop_loss.py" ]; then
    echo -e "${GREEN}✅${NC} auto_stop_loss.py 存在"
    SIZE=$(ls -lh auto_stop_loss.py | awk '{print $5}')
    echo "   文件大小: $SIZE"
    
    # 检查语法
    if python3 -m py_compile auto_stop_loss.py 2>/dev/null; then
        echo -e "${GREEN}✅${NC} 脚本语法正确"
    else
        echo -e "${RED}❌${NC} 脚本有语法错误"
    fi
else
    echo -e "${RED}❌${NC} auto_stop_loss.py 不存在"
fi

# 检查7: 启动脚本
print_section "⚙️ 检查7: 启动脚本"

for script in "start.sh" "start_background.sh" "stop.sh"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo -e "${GREEN}✅${NC} $script (可执行)"
        else
            echo -e "${YELLOW}⚠️${NC}  $script (不可执行)"
            echo "    运行: chmod +x $script"
        fi
    else
        echo -e "${RED}❌${NC} $script 不存在"
    fi
done

# 检查8: 网络连接
print_section "🌐 检查8: 网络连接"

if command -v curl > /dev/null; then
    if curl -s -m 3 "https://api.gateio.ws/api/v4" > /dev/null; then
        echo -e "${GREEN}✅${NC} 可以连接到 GateIO API"
    else
        echo -e "${YELLOW}⚠️${NC}  无法连接到 GateIO API (可能是防火墙)"
    fi
elif command -v wget > /dev/null; then
    if wget -q -T 3 -O /dev/null "https://api.gateio.ws/api/v4"; then
        echo -e "${GREEN}✅${NC} 可以连接到 GateIO API"
    else
        echo -e "${YELLOW}⚠️${NC}  无法连接到 GateIO API (可能是防火墙)"
    fi
else
    echo -e "${YELLOW}⚠️${NC}  curl 和 wget 都未安装，跳过网络检查"
fi

# 检查9: 权限
print_section "🔐 检查9: 文件权限"

if [ -w "." ]; then
    echo -e "${GREEN}✅${NC} 当前目录可写"
else
    echo -e "${RED}❌${NC} 当前目录不可写"
fi

if [ -f ".env" ] && [ -r ".env" ]; then
    echo -e "${GREEN}✅${NC} .env 文件可读"
elif [ -f ".env" ]; then
    echo -e "${RED}❌${NC} .env 文件不可读"
fi

# 总结
print_section "📊 检查总结"

echo "通过: $check_passed / $check_total"
echo ""

if [ $CONFIG_FOUND -eq 1 ]; then
    echo -e "${GREEN}✅ 所有关键检查通过！${NC}"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  🚀 您现在可以启动脚本"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "启动方式:"
    echo ""
    echo "1️⃣  前台运行（推荐测试）:"
    echo "   python3 auto_stop_loss.py"
    echo ""
    echo "2️⃣  后台运行（推荐生产）:"
    echo "   ./start_background.sh"
    echo ""
    echo "3️⃣  停止运行:"
    echo "   ./stop.sh"
    echo ""
    echo "4️⃣  实时查看日志:"
    echo "   tail -f auto_trade.log"
    echo ""
    echo "5️⃣  在 screen 中查看:"
    echo "   screen -r trading"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    exit 0
else
    echo -e "${RED}❌ 检查有失败项，请修复后再运行${NC}"
    echo ""
    echo "常见问题解决:"
    echo "1. 配置文件: 创建 .env 文件包含 API 密钥"
    echo "2. 虚拟环境: python3 -m venv .venv"
    echo "3. 依赖包: source .venv/bin/activate && pip install -r requirements.txt"
    echo "4. 执行权限: chmod +x *.sh"
    echo ""
    exit 1
fi
