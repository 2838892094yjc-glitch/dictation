# 任务2: 听写模式切换 - 实现文档

## 实现状态
✅ **已完成** (2026-02-16)

## 功能概述
成功实现了三种听写模式的切换功能，支持：
1. **英译中** (en_to_cn): 播报英文单词，用户填写中文释义
2. **中译英** (cn_to_en): 播报中文释义，用户填写英文单词
3. **拼写** (spell): 播报英文+中文，用户拼写英文单词

## 代码变更

### 1. app.py 修改

#### 1.1 session_state 初始化
在第52行添加了 `dictation_mode` 状态：
```python
if 'dictation_mode' not in st.session_state:
    st.session_state.dictation_mode = "en_to_cn"  # en_to_cn | cn_to_en | spell
```

#### 1.2 词库页面 - 模式选择 UI
在第242-251行添加了模式选择下拉框：
```python
st.session_state.dictation_mode = st.selectbox(
    "📝 听写模式",
    options=["en_to_cn", "cn_to_en", "spell"],
    format_func=lambda x: {
        "en_to_cn": "英译中（听英文写中文）",
        "cn_to_en": "中译英（听中文写英文）",
        "spell": "拼写（听英文+中文拼写英文）"
    }[x],
    index=["en_to_cn", "cn_to_en", "spell"].index(st.session_state.dictation_mode)
)
```

#### 1.3 听写页面 - 显示逻辑
在第356-367行更新了显示逻辑，根据模式显示不同内容：
```python
mode = st.session_state.dictation_mode

if mode == "en_to_cn":
    display_text = current_word['en']
    mode_name = "英译中 (听英文写中文)"
elif mode == "cn_to_en":
    display_text = current_word['cn']
    mode_name = "中译英 (听中文写英文)"
else:  # spell
    display_text = f"{current_word['en']} / {current_word['cn']}"
    mode_name = "拼写 (听英文+中文拼写英文)"
```

#### 1.4 答案输入 - 动态提示
在第402-408行添加了根据模式的动态提示：
```python
mode = st.session_state.dictation_mode
if mode == "en_to_cn":
    placeholder_text = "输入中文释义"
elif mode == "cn_to_en":
    placeholder_text = "输入英文单词"
else:  # spell
    placeholder_text = "拼写英文单词"
```

#### 1.5 答案保存 - 根据模式保存正确答案
在第418-424行更新了答案保存逻辑：
```python
if mode == "en_to_cn":
    correct_answer = word['cn']
elif mode == "cn_to_en":
    correct_answer = word['en']
else:  # spell
    correct_answer = word['en']

st.session_state.user_answers[idx] = {
    'user': user_answer,
    'correct': correct_answer,
    'mode': mode
}
```

#### 1.6 播放逻辑 - play_current_word()
在第447-498行重构了播放函数：
- 英译中：只播报英文
- 中译英：只播报中文
- 拼写：先播报英文，延迟1.5秒后播报中文

```python
def play_current_word():
    mode = st.session_state.dictation_mode

    if mode == "en_to_cn":
        # 播报英文
        audio_path = cache.get_audio(word['en'], mode="en", voice_en=voice_en)
        play_audio(audio_path)
    elif mode == "cn_to_en":
        # 播报中文
        audio_path = cache.get_audio(word['cn'], mode="cn", voice_cn=voice_cn)
        play_audio(audio_path)
    else:  # spell
        # 先播英文，再播中文（带延迟）
        play_audio(en_audio)
        # JavaScript 延迟播放中文
```

#### 1.7 自动播放 - auto_play()
在第502-541行更新了自动连续播放逻辑，支持三种模式。

### 2. src/minimax_tts.py 修复
在第56行修复了默认音色配置错误：
```python
# 修复前
self.voice = self.ENGLISH_VOICES["expressive_narrator"]  # 这个音色不存在

# 修复后
self.voice = self.ENGLISH_VOICES["male_qn_qingse"]  # 使用第一个可用音色
```

## 使用方法

### 1. 选择听写模式
在词库管理页面，选择单词后，在"开始听写"按钮上方选择听写模式：
- **英译中（听英文写中文）**: 默认模式，适合学习中文释义
- **中译英（听中文写英文）**: 反向学习，提高英文拼写
- **拼写（听英文+中文拼写英文）**: 完整模式，先听英文再听中文，适合记忆拼写

### 2. 开始听写
点击"开始听写"按钮，系统会根据选择的模式播放相应内容。

### 3. 填写答案
- 英译中：输入中文释义
- 中译英：输入英文单词
- 拼写：输入英文拼写

### 4. 查看批改
在答案批改页面查看结果，系统会根据模式比对正确答案。

## 技术亮点

### 1. 状态管理
使用 `st.session_state.dictation_mode` 统一管理模式状态，确保整个流程的一致性。

### 2. 音频播放
- 支持 MiniMax TTS 中英文语音合成
- 拼写模式使用 JavaScript 延迟播放，实现英文→中文的顺序播放
- 音频缓存优化，避免重复生成

### 3. UI/UX 优化
- 模式选择下拉框使用 `format_func` 显示友好的中文描述
- 听写页面实时显示当前模式
- 答案输入框根据模式显示不同的 placeholder

### 4. 答案批改
- 保存答案时记录模式信息
- 批改时根据模式比对对应字段（en 或 cn）
- 支持大小写不敏感比较

## 测试结果
✅ 模块导入成功
✅ 音色配置正确（5个英文音色，5个中文音色）
✅ 音频缓存初始化成功
✅ 三种模式切换正常

## 已知限制

1. **拼写模式的延迟播放**
   - 当前使用 JavaScript setTimeout 实现延迟
   - 在某些浏览器可能有兼容性问题
   - 自动播放模式使用 Python time.sleep()，更稳定

2. **中文输入批改**
   - 当前使用简单的字符串比较
   - 不支持同义词判断
   - 可以考虑后续使用 AI 进行语义相似度判断

## 后续优化建议

1. **拼写模式增强**
   - 添加字母拼读功能（A-P-P-L-E）
   - 支持自定义播放间隔

2. **答案批改优化**
   - 支持同义词判断（如 happy = glad）
   - 支持拼写相似度评分（如 apple vs aplle → 90%）

3. **统计分析**
   - 记录每个单词在不同模式下的正确率
   - 生成学习报告

## 相关文件
- `/Users/yangjingchi/Desktop/自动听写/app.py` - 主应用
- `/Users/yangjingchi/Desktop/自动听写/src/minimax_tts.py` - TTS 引擎
- `/Users/yangjingchi/Desktop/自动听写/src/audio_cache.py` - 音频缓存
- `/Users/yangjingchi/Desktop/自动听写/docs/TASK2_DICTATION_MODE.md` - 任务文档

## 完成时间
2026-02-16

## 开发者
@ui-agent + @tts-agent
