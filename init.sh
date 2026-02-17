#!/bin/bash
# init.sh - 自动英语听写开发环境启动脚本

PROJECT_DIR="/Users/yangjingchi/Desktop/自动听写"
cd "$PROJECT_DIR"

echo "========================================="
echo "  自动英语听写 - 开发环境"
echo "========================================="
echo ""

# 检查并创建数据目录
mkdir -p data

# 检查 Python 环境
echo "📦 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 检查依赖
echo ""
echo "📦 检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 不存在"
    exit 1
fi
echo "✅ requirements.txt 存在"

# 解析命令行参数
MODE=${1:-"dev"}  # 默认开发模式

case $MODE in
    "dev")
        echo ""
        echo "🌐 启动开发服务器 (端口 8501)..."
        echo "📱 访问 http://localhost:8501"
        echo ""
        streamlit run app.py --server.port 8501
        ;;

    "test")
        echo ""
        echo "🧪 启动测试服务器 (端口 8502)..."
        echo "📱 访问 http://localhost:8502"
        echo ""
        streamlit run app.py --server.port 8502
        ;;

    "run")
        echo ""
        echo "🚀 生产环境启动..."
        streamlit run app.py
        ;;

    "check")
        echo "🔍 环境检查..."
        echo ""
        echo "Python 版本:"
        python3 --version
        echo ""
        echo "已安装的关键包:"
        pip3 list | grep -E "streamlit|paddleocr|minimax|Pillow" || echo "  ⚠️  部分依赖未安装"
        echo ""
        echo "端口占用:"
        lsof -i :8501 -i :8502 2>/dev/null || echo "  8501, 8502 可用"
        echo ""
        echo "数据目录:"
        ls -la data/ 2>/dev/null || echo "  data/ 目录不存在"
        ;;

    "stop")
        echo "🛑 停止所有 Streamlit 服务..."
        pkill -f "streamlit run" || echo "没有运行中的 Streamlit 进程"
        ;;

    "help"|"-h"|"--help")
        echo "用法: ./init.sh [命令]"
        echo ""
        echo "命令:"
        echo "  dev     启动开发服务器 (默认, 端口 8501)"
        echo "  test    启动测试服务器 (端口 8502)"
        echo "  run     生产环境启动"
        echo "  check   环境检查"
        echo "  stop    停止所有服务"
        echo "  help    显示帮助"
        echo ""
        echo "示例:"
        echo "  ./init.sh        # 启动开发服务器"
        echo "  ./init.sh test   # 启动测试服务器"
        echo "  ./init.sh check  # 检查环境"
        ;;

    *)
        echo "❌ 未知命令: $MODE"
        echo "使用 ./init.sh help 查看帮助"
        exit 1
        ;;
esac
