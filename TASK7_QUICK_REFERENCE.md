# 任务7快速参考：主题切换功能

## 快速开始

### 使用主题切换
1. 运行应用：`streamlit run app.py`
2. 在侧边栏找到"🎨 主题设置"
3. 选择主题：默认/浅色/深色/温馨/复古
4. 主题立即生效，刷新后保持

## 可用主题

| 主题 | 图标 | 适用场景 | 特点 |
|------|------|----------|------|
| 默认风格 | 🎨 | 通用 | Streamlit原生样式 |
| 浅色模式 | ☀️ | 白天使用 | 清新明亮，专业简洁 |
| 深色模式 | 🌙 | 夜间使用 | 护眼舒适，减少疲劳 |
| 温馨学习 | 🌈 | 儿童使用 | 柔和色彩，活泼可爱 |
| 复古学院 | 📜 | 专业学习 | 经典风格，学术氛围 |

## 文件结构

```
自动听写/
├── .streamlit/
│   └── config.toml              # Streamlit配置
├── themes/
│   ├── light.css                # 浅色主题
│   ├── dark.css                 # 深色主题
│   ├── cozy.css                 # 温馨主题
│   └── vintage.css              # 复古主题
├── src/
│   └── theme_manager.py         # 主题管理器
├── app.py                       # 主应用（集成主题）
└── test_theme.py                # 主题测试脚本

## 核心代码

### 主题管理器
```python
from src.theme_manager import load_theme, get_available_themes

# 获取所有主题
themes = get_available_themes()

# 加载主题CSS
css = load_theme("dark")
st.markdown(css, unsafe_allow_html=True)
```

### 主题选择器
```python
def render_theme_selector():
    with st.sidebar:
        st.subheader("🎨 主题设置")
        selected_theme = st.selectbox(
            "选择主题",
            options=list(themes.keys()),
            format_func=lambda x: themes[x]
        )
        if selected_theme != "default":
            st.markdown(load_theme(selected_theme), unsafe_allow_html=True)
```

### Session State
```python
if 'theme' not in st.session_state:
    st.session_state.theme = "default"
```

## 深色模式配色

```css
--color-bg-primary: #1a1a2e      /* 主背景 */
--color-bg-secondary: #16213e    /* 次背景 */
--color-text: #e8e8e8            /* 文字 */
--color-blue: #4a90e2            /* 蓝色 */
--color-purple: #9b59b6          /* 紫色 */
--color-accent: #e94560          /* 强调色 */
```

## 浅色模式配色

```css
--color-bg-primary: #ffffff      /* 主背景 */
--color-bg-secondary: #f8f9fa    /* 次背景 */
--color-text: #2c3e50            /* 文字 */
--color-blue: #1f77b4            /* 蓝色 */
--color-purple: #8e44ad          /* 紫色 */
--color-accent: #0066cc          /* 强调色 */
```

## 测试命令

```bash
# 测试主题功能
python test_theme.py

# 运行应用
streamlit run app.py
```

## 常见问题

### Q: 主题切换后没有生效？
A: 确保在主函数中调用了 `render_theme_selector()`

### Q: 刷新后主题丢失？
A: 检查 session_state 是否正确保存主题

### Q: 某些组件样式不对？
A: 检查CSS选择器是否正确，可能需要添加 `!important`

### Q: 如何添加新主���？
A:
1. 在 `themes/` 目录创建新的CSS文件
2. 在 `theme_manager.py` 的 `THEMES` 字典添加映射
3. 在 `THEME_NAMES` 字典添加显示名称

## 性能提示

- 主题CSS只在切换时加载，不影响性能
- 使用CSS变量统一管理颜色，易于维护
- 所有过渡动画使用CSS实现，流畅高效

## 兼容性

- ✅ 所有页面（词库/听写/批改/历史/错题）
- ✅ 所有组件（按钮/输入框/选择框/提示框）
- ✅ 所有浏览器（Chrome/Firefox/Safari/Edge）
- ✅ 响应式设计（桌面/平板/手机）

## 相关文档

- [完整实现报告](./TASK7_COMPLETION_REPORT.md)
- [任务文档](./docs/TASK7_THEME.md)
- [主题管理器源码](./src/theme_manager.py)
