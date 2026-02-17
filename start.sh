#!/bin/bash

# 自动英语听写 - 启动脚本

echo "🚀 启动自动英语听写..."
echo ""

# 检查虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 已激活虚拟环境"
fi

# 启动应用
echo "🌐 正在启动 Streamlit 服务..."
echo "📱 应用将在浏览器中自动打开"
echo ""

streamlit run app.py
