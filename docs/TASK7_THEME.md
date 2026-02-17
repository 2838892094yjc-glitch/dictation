# 任务7: 深色模式/主题

## 任务目标
支持深色模式和主题切换

## 文件变更

### 修改文件
```
app.py                      # 添加主题支持
src/theme_manager.py        # 扩展主题功能
themes/
├── dark.css               # 新增深色主题
└── ...
```

## 功能清单
- [ ] 深色/浅色模式切换
- [ ] 主题选择器
- [ ] 主题记忆
- [ ] 预设主题 (可选)

## 实现方案

### 方案1: Streamlit 内置
```python
st.set_page_config(layout="wide")
# Streamlit 自身的主题切换有限
```

### 方案2: 自定义 CSS (推荐)
```python
# 添加深色模式 CSS
dark_css = """
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)
```

## 实现步骤

### 步骤1: 添加主题管理
- 在 session_state 添加主题状态
- 创建深色/浅色 CSS

### 步骤2: 添加主题切换 UI
- 侧边栏添加主题选择器
- 支持深色/浅色切换

### 步骤3: 应用主题
- 根据选择加载对应 CSS
- 记住用户偏好

## 测试要点
1. 主题切换生效
2. 刷新后保持主题
3. 所有页面主题一致

## 预计改动量
- 新增代码: ~50 行
- 新增 CSS: ~30 行

---

## 上一任务
[任务6: 词库导入导出](./TASK6_IMPORT_EXPORT.md)

## 下一任务
[任务8: 代码优化与测试](./TASK8_OPTIMIZATION.md)
