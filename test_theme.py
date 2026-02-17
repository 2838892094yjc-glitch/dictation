#!/usr/bin/env python3
"""
测试主题功能
验证深色/浅色模式切换是否正常工作
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theme_manager import (
    get_available_themes,
    load_theme,
    get_theme_path,
    THEMES,
    THEME_NAMES
)

def test_theme_manager():
    """测试主题管理器"""
    print("=" * 60)
    print("测试主题管理器")
    print("=" * 60)

    # 测试1: 获取可用主题
    print("\n1. 测试获取可用主题")
    themes = get_available_themes()
    print(f"   可用主题数量: {len(themes)}")
    for key, name in themes.items():
        print(f"   - {key}: {name}")

    # 测试2: 检查主题文件是否存在
    print("\n2. 测试主题文件路径")
    for theme_key in THEMES.keys():
        path = get_theme_path(theme_key)
        exists = os.path.exists(path) if path else False
        status = "✅" if exists else "❌"
        print(f"   {status} {theme_key}: {path}")

    # 测试3: 加载主题CSS
    print("\n3. 测试加载主题CSS")
    for theme_key in ["light", "dark", "cozy", "vintage"]:
        css = load_theme(theme_key)
        if css and not css.startswith("/*"):
            print(f"   ✅ {theme_key}: 加载成功 ({len(css)} 字符)")
        else:
            print(f"   ❌ {theme_key}: 加载失败")

    # 测试4: 验证深色模式CSS内容
    print("\n4. 测试深色模式CSS内容")
    dark_css = load_theme("dark")
    dark_keywords = [
        "--color-bg-primary: #1a1a2e",
        "--color-text: #e8e8e8",
        "深色模式",
        "Dark Mode"
    ]
    for keyword in dark_keywords:
        if keyword in dark_css:
            print(f"   ✅ 包含关键字: {keyword}")
        else:
            print(f"   ❌ 缺少关键字: {keyword}")

    # 测试5: 验证浅色模式CSS内容
    print("\n5. 测试浅色模式CSS内容")
    light_css = load_theme("light")
    light_keywords = [
        "--color-bg-primary: #ffffff",
        "--color-text: #2c3e50",
        "浅色模式",
        "Light Mode"
    ]
    for keyword in light_keywords:
        if keyword in light_css:
            print(f"   ✅ 包含关键字: {keyword}")
        else:
            print(f"   ❌ 缺少关键字: {keyword}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def test_streamlit_config():
    """测试Streamlit配置文件"""
    print("\n" + "=" * 60)
    print("测试Streamlit配置文件")
    print("=" * 60)

    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".streamlit",
        "config.toml"
    )

    if os.path.exists(config_path):
        print(f"\n✅ 配置文件存在: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"   文件大小: {len(content)} 字符")

            # 检查关键配置项
            required_sections = ["[theme]", "[server]", "[browser]", "[runner]"]
            for section in required_sections:
                if section in content:
                    print(f"   ✅ 包含配置节: {section}")
                else:
                    print(f"   ❌ 缺少配置节: {section}")
    else:
        print(f"\n❌ 配置文件不存在: {config_path}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_theme_manager()
    test_streamlit_config()

    print("\n✨ 所有测试完成！")
    print("\n使用方法:")
    print("1. 运行应用: streamlit run app.py")
    print("2. 在侧边栏找到 '🎨 主题设置'")
    print("3. 选择不同的主题查看效果")
    print("4. 主题会自动保存，刷新后保持")
