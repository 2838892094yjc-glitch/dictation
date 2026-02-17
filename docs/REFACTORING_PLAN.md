# 代码重构计划 - 降低耦合度

## 当前问题分析

### 1. app.py 过于臃肿 (1432行)
- 所有页面渲染逻辑都在一个文件
- UI 逻辑和业务逻辑混合
- 重复代码多

### 2. 高耦合区域识别

| 区域 | 行数 | 问题 |
|------|------|------|
| render_vocabulary_page() | ~200行 | 词库管理+导入导出混合 |
| render_dictation_page() | ~150行 | 播放控制+答案输入混合 |
| render_answer_page() | ~220行 | 手动批改+拍照批改混合 |
| render_history_page() | ~150行 | 统计+图表+列表混合 |
| render_wrong_answers_page() | ~100行 | 错题展示+复习混合 |

### 3. 重复代码

1. **音频播放逻辑** - `play_current_word()` 和 `auto_play()` 有大量重复
2. **模式判断逻辑** - 多处 `if mode == "en_to_cn"` 重复
3. **保存词库逻辑** - 多处调用 `vocab_store.save_vocabulary()`

---

## 重构方案

### Phase 1: 拆分页面组件 (优先级: P0)

创建 `pages/` 目录，每个页面独立文件：

```
pages/
├── __init__.py
├── vocabulary_page.py      # 词库管理页
├── dictation_page.py       # 听写播放页
├── answer_page.py          # 答案批改页
├── history_page.py         # 学习历史页
└── wrong_answers_page.py   # 错题本页
```

### Phase 2: 提取公共组件 (优先级: P0)

创建 `components/` 目录：

```
components/
├── __init__.py
├── audio_player.py         # 音频播放组件
├── word_card.py            # 单词卡片组件
├── stats_card.py           # 统计卡片组件
└── navigation.py           # 导航组件
```

### Phase 3: 业务逻辑抽象 (优先级: P1)

创建 `services/` 目录：

```
services/
├── __init__.py
├── dictation_service.py    # 听写服务（模式切换、播放控制）
├── grading_service.py      # 批改服务（手动+拍照）
└── vocabulary_service.py   # 词库服务（CRUD+导入导出）
```

---

## 具体重构任务

### 任务 R1: 提取音频播放组件
**文件**: `components/audio_player.py`
**内容**:
- `play_audio(audio_path)` - 播放单个音频
- `play_word(word, mode, cache, voice_en, voice_cn)` - 根据模式播放单词
- `auto_play_all(words, mode, cache, voice_en, voice_cn, interval)` - 自动连续播放

### 任务 R2: 提取听写服务
**文件**: `services/dictation_service.py`
**内容**:
- `get_display_text(word, mode)` - 根据模式获取显示文本
- `get_correct_answer(word, mode)` - 根据模式获取正确答案
- `check_answer(user_answer, correct_answer, mode)` - 检查答案

### 任务 R3: 拆分词库管理页
**文件**: `pages/vocabulary_page.py`
**内容**:
- `render_vocabulary_manager()` - 词库选择/保存/删除
- `render_import_export()` - 导入导出功能
- `render_word_list()` - 单词列表展示
- `render_word_input()` - 单词输入

### 任务 R4: 拆分答案批改页
**文件**: `pages/answer_page.py`
**内容**:
- `render_manual_grading()` - 手动输入批改
- `render_photo_grading()` - 拍照批改
- `render_grading_result()` - 批改结果展示

---

## 重构后的 app.py 结构

```python
"""
自动英语听写软件 - v4.0 重构版
"""
import streamlit as st

# 导入页面
from pages.vocabulary_page import render_vocabulary_page
from pages.dictation_page import render_dictation_page
from pages.answer_page import render_answer_page
from pages.history_page import render_history_page
from pages.wrong_answers_page import render_wrong_answers_page

# 导入组件
from components.navigation import render_header, render_theme_selector

# 初始化
def init_session_state():
    """初始化所有 session state"""
    # ... 所有初始化逻辑
    pass

def main():
    init_session_state()
    render_theme_selector()
    render_header()

    # 路由
    page = st.session_state.page
    if page == 'vocabulary':
        render_vocabulary_page()
    elif page == 'dictation':
        render_dictation_page()
    elif page == 'answer':
        render_answer_page()
    elif page == 'history':
        render_history_page()
    elif page == 'wrong_answers':
        render_wrong_answers_page()

if __name__ == "__main__":
    main()
```

---

## 执行顺序

1. **R1: 提取音频播放组件** - 消除最大的重复代码
2. **R2: 提取听写服务** - 统一模式处理逻辑
3. **R3: 拆分词库管理页** - 最大的页面
4. **R4: 拆分答案批改页** - 第二大的页面
5. **R5: 拆分其他页面** - 历史、错题本

---

## 预期效果

| 指标 | 重构前 | 重构后 |
|------|--------|--------|
| app.py 行数 | 1432 | ~200 |
| 重复代码 | 多处 | 消除 |
| 模块数 | 11 | 18 |
| 可测试性 | 低 | 高 |
| 可维护性 | 低 | 高 |

---

## Agent Team 分工建议

| Agent | 任务 | 文件 |
|-------|------|------|
| @ui-agent | R3, R4, R5 | pages/*.py |
| @tts-agent | R1 | components/audio_player.py |
| @devops-agent | R2 | services/dictation_service.py |
| @test-agent | 测试 | tests/test_*.py |
