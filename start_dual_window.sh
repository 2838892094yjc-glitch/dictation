#!/bin/bash
# start_dual_window.sh - 自动打开双窗口工作流

PROJECT_DIR="/Users/yangjingchi/Desktop/自动听写"

echo "🚀 正在打开双窗口工作流..."
echo ""

# 检查 Streamlit 是否已运行
if lsof -i:8501 &> /dev/null; then
    echo "⚠️  端口 8501 已被占用"
fi

# 使用 AppleScript 打开两个终端窗口
osascript << EOF
    tell application "Terminal"
        activate
        do script "cd $PROJECT_DIR && echo '📚 窗口1: 主开发窗口' && echo '用途: 框架搭建、功能开发' && echo '' && streamlit run app.py --server.port 8501"
    end tell

    delay 2

    tell application "Terminal"
        do script "cd $PROJECT_DIR && echo '🧪 窗口2: 测试窗口' && echo '用途: 功能测试、Bug验证' && echo '' && streamlit run app.py --server.port 8502"
    end tell
EOF

echo "✅ 已打开两个终端窗口"
echo ""
echo "窗口1: http://localhost:8501 (主开发)"
echo "窗口2: http://localhost:8502 (测试验证)"
echo ""
echo "💡 提示: 使用 Cmd+` 在两个终端窗口间切换"
