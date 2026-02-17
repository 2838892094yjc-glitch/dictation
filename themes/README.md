# 主题系统

## 目录结构

```
themes/
├── cozy.css          # 温馨学习风 - 适合小学生/儿童
├── vintage.css       # 复古学院风 - 适合文艺青年
└── README.md         # 本文档
```

## 主题预览

### 🌈 温馨学习风 (cozy.css)

| 属性 | 值 |
|------|-----|
| **定位** | 小学生、儿童 |
| **配色** | Pastel 淡黄 #FFE066 / 粉 #FFB3BA / 薄荷绿 #B5EAD7 |
| **字体** | Fredoka + Nunito（圆体）|
| **圆角** | 16-48px 大圆角 |
| **特点** | 柔和渐变、星星装饰、可爱友好 |

**适合场景**：儿童英语启蒙、亲子学习、轻松愉快的学习氛围

### 📜 复古学院风 (vintage.css)

| 属性 | 值 |
|------|-----|
| **定位** | 文艺青年、情怀用户 |
| **配色** | 深绿 #1a3a2f / 棕 #5d4037 / 金 #c9a227 |
| **字体** | Cinzel + Playfair Display + Crimson Text（衬线）|
| **纹理** | 羊皮纸噪点纹理 |
| **特点** | 书本效果、维多利亚装饰、古典优雅 |

**适合场景**：深度学习者、英语文学爱好者、追求格调的用户

## 使用方式

在 `app.py` 中选择主题：

```python
from src.theme_manager import load_theme, get_available_themes

# 显示主题选择器
themes = get_available_themes()  # {'default': '🎨 默认风格', 'cozy': '🌈 温馨学习', 'vintage': '📜 复古学院'}
theme = st.selectbox("界面主题", options=list(themes.keys()), format_func=lambda x: themes[x])

# 应用主题 CSS（如果不是默认主题）
if theme != "default":
    theme_css = load_theme(theme)
    st.markdown(theme_css, unsafe_allow_html=True)
```

## 添加新主题

1. 在 `themes/` 目录创建 `your-theme.css`
2. 使用 CSS 变量定义配色方案
3. 覆盖 Streamlit 的默认样式（使用 `!important`）
4. 在 `theme_manager.py` 的 `THEMES` 字典中添加映射：

```python
THEMES = {
    "default": "default.css",
    "cozy": "cozy.css",
    "vintage": "vintage.css",
    "your-theme": "your-theme.css",  # 添加新主题
}

THEME_NAMES = {
    "default": "🎨 默认风格",
    "cozy": "🌈 温馨学习",
    "vintage": "📜 复古学院",
    "your-theme": "✨ 你的主题",  # 添加显示名称
}
```

## 主题开发指南

### CSS 覆盖优先级

Streamlit 使用内联样式，需要使用 `!important` 覆盖：

```css
/* ✅ 正确 */
.stButton > button {
    background: pink !important;
}

/* ❌ 错误 - 可能被覆盖 */
.stButton > button {
    background: pink;
}
```

### 响应式设计

两个主题都已适配移动端：

```css
@media (max-width: 768px) {
    /* 移动端样式 */
}
```

### 性能注意

- CSS 文件大小：cozy.css (~8KB), vintage.css (~14KB)
- 使用 Google Fonts CDN，首次加载会请求字体
- 建议配合浏览器缓存使用

## 设计原则

1. **中英文混合**：所有界面文字都是中英双语
2. **功能完整**：覆盖所有 Streamlit 组件样式
3. **一致性**：同主题下所有元素风格统一
4. **可访问性**：保持足够的对比度

## 版权与授权

主题文件中的字体：
- **Cozy**: Fredoka + Nunito (SIL Open Font License)
- **Vintage**: Playfair Display + Crimson Text + Cinzel (SIL Open Font License)

样式代码：与项目主体一致
