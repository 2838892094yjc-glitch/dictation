"""
主题管理器 - 支持多主题切换
"""
import os
from typing import Dict, Optional

# 主题文件映射
THEMES: Dict[str, str] = {
    "light": "light.css",
    "dark": "dark.css",
    "cozy": "cozy.css",
    "vintage": "vintage.css",
}

# 主题显示名称
THEME_NAMES: Dict[str, str] = {
    "default": "🎨 默认风格",
    "light": "☀️ 浅色模式",
    "dark": "🌙 深色模式",
    "cozy": "🌈 温馨学习",
    "vintage": "📜 复古学院",
}


def get_theme_path(theme_name: str) -> Optional[str]:
    """
    获取主题文件的完整路径
    
    Args:
        theme_name: 主题名称 (cozy, vintage, etc.)
        
    Returns:
        主题文件路径，不存在则返回 None
    """
    if theme_name not in THEMES:
        return None
    
    # 获取当前文件所在目录的父目录（项目根目录）
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    theme_file = os.path.join(current_dir, "themes", THEMES[theme_name])
    
    return theme_file if os.path.exists(theme_file) else None


def load_theme(theme_name: str) -> str:
    """
    加载主题 CSS 内容
    
    Args:
        theme_name: 主题名称
        
    Returns:
        CSS 样式字符串
    """
    if theme_name == "default" or theme_name not in THEMES:
        return ""
    
    theme_path = get_theme_path(theme_name)
    if not theme_path:
        return f"/* 主题文件不存在: {theme_name} */"
    
    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        return f"<style>{css_content}</style>"
    except Exception as e:
        return f"/* 加载主题失败: {e} */"


def get_available_themes() -> Dict[str, str]:
    """
    获取所有可用主题
    
    Returns:
        {主题值: 显示名称} 的字典
    """
    return THEME_NAMES.copy()


def render_theme_selector() -> str:
    """
    渲染主题选择器（返回选中的主题值）
    
    使用方式：
        theme = render_theme_selector()
        if theme != "default":
            st.markdown(load_theme(theme), unsafe_allow_html=True)
    
    Returns:
        选中的主题名称
    """
    import streamlit as st
    
    themes = get_available_themes()
    
    # 从 session state 获取当前主题，默认为 default
    current_theme = st.session_state.get("theme", "default")
    
    # 主题选择器（放在侧边栏或设置区域）
    selected_theme = st.selectbox(
        "🎨 界面主题",
        options=list(themes.keys()),
        format_func=lambda x: themes[x],
        index=list(themes.keys()).index(current_theme) if current_theme in themes else 0,
        help="选择你喜欢的界面风格"
    )
    
    # 保存到 session state
    if selected_theme != current_theme:
        st.session_state.theme = selected_theme
        st.rerun()
    
    return selected_theme


if __name__ == "__main__":
    # 测试
    print("可用主题:", get_available_themes())
    print("\ncozy 主题路径:", get_theme_path("cozy"))
    print("\ncozy 主题内容预览:")
    css = load_theme("cozy")
    print(css[:200] + "..." if len(css) > 200 else css)
