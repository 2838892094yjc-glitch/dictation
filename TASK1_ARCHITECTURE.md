# 任务1架构设计：词库持久化存储

## 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Streamlit App (app.py)                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Session State 管理                           │  │
│  │  ┌────────────────┬──────────────────┬────────────────┐  │  │
│  │  │ word_list      │ current_vocabulary│ vocab_store   │  │  │
│  │  │ (当前单词列表)   │  (当前词库名称)     │ (存储实例)    │  │  │
│  │  └────────────────┴──────────────────┴────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓ ↑                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  UI 界面层                                │  │
│  │  ┌──────────┬───────────┬───────────┬────────────────┐  │  │
│  │  │词库选择器 │ 保存按钮  │ 新建按钮  │  删除按钮       │  │  │
│  │  └──────────┴───────────┴───────────┴────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │          词库列表显示 + 编辑功能                    │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓ ↑                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          VocabularyStore (业务逻辑层)                    │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │  save_vocabulary()      保存词库                    │ │  │
│  │  │  load_vocabulary()      加载词库                    │ │  │
│  │  │  list_vocabularies()    列出所有词库                │ │  │
│  │  │  delete_vocabulary()    删除词库                    │ │  │
│  │  │  rename_vocabulary()    重命名词库                  │ │  │
│  │  │  vocabulary_exists()    检查词库存在                │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓ ↑                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              文件系统 (数据持久化层)                      │  │
│  │  data/vocabularies/                                      │  │
│  │  ├── 默认词库.json                                       │  │
│  │  ├── 词库_1.json                                         │  │
│  │  └── 词库_2.json                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 数据流图

### 1. 应用启动流程

```
应用启动
   ↓
初始化 VocabularyStore
   ↓
加载默认词库 (load_vocabulary("默认词库"))
   ↓
读取 data/vocabularies/默认词库.json
   ↓
解析 JSON 数据
   ↓
加载到 st.session_state.word_list
   ↓
渲染 UI 界面
```

### 2. 切换词库流程

```
用户选择新词库
   ↓
触发 selectbox onChange 事件
   ↓
调用 vocab_store.load_vocabulary(selected_vocab)
   ↓
读取对应的 JSON 文件
   ↓
更新 st.session_state.word_list
   ↓
更新 st.session_state.current_vocabulary
   ↓
st.rerun() 刷新界面
```

### 3. 添加单词流程（自动保存）

```
用户添加单词 (拍照/手动输入)
   ↓
单词添加到 st.session_state.word_list
   ↓
自动调用 vocab_store.save_vocabulary()
   ↓
构建 JSON 数据结构
   ↓
写入文件 data/vocabularies/{name}.json
   ↓
显示成功提示
```

### 4. 删除单词流程（自动保存）

```
用户点击删除按钮
   ↓
从 st.session_state.word_list 移除单词
   ↓
自动调用 vocab_store.save_vocabulary()
   ↓
更新 JSON 文件
   ↓
st.rerun() 刷新界面
```

### 5. 新建词库流程

```
用户点击"新建词库"
   ↓
生成新词库名称 (词库_N)
   ↓
清空 st.session_state.word_list = []
   ↓
更新 st.session_state.current_vocabulary
   ↓
st.rerun() 刷新界面
   ↓
用户添加单词时才创建文件
```

### 6. 删除词库流程

```
用户点击"删除词库"
   ↓
检查是否为默认词库 (不允许删除)
   ↓
调用 vocab_store.delete_vocabulary()
   ↓
删除文件系统中的 JSON 文件
   ↓
切换到默���词库
   ↓
st.rerun() 刷新界面
```

---

## 类图

```
┌──────────────────────────────────────────────────────────���──┐
│                    VocabularyStore                          │
├─────────────────────────────────────────────────────────────┤
│ - base_dir: str                                             │
├─────────────────────────────────────────────────────────────┤
│ + __init__(base_dir: str = None)                            │
│ + save_vocabulary(name: str, words: List[Dict],             │
│                   update_time: bool = True) -> bool         │
│ + load_vocabulary(name: str) -> Optional[Dict]              │
│ + list_vocabularies() -> List[Dict]                         │
│ + delete_vocabulary(name: str) -> bool                      │
│ + rename_vocabulary(old_name: str, new_name: str) -> bool   │
│ + vocabulary_exists(name: str) -> bool                      │
│ - _get_file_path(name: str) -> str                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 状态机图

### 词库生命周期

```
    [不存在]
       ↓ save_vocabulary()
    [已创建]
       ↓ load_vocabulary()
    [已加载]
       ↓ 编辑操作
    [已修改]
       ↓ save_vocabulary()
    [已保存]
       ↓ rename_vocabulary()
    [已重命名]
       ↓ delete_vocabulary()
    [已删除]
```

---

## 时序图：保存词库

```
用户          app.py         VocabularyStore      文件系统
 |              |                  |                  |
 |--点击保存---->|                  |                  |
 |              |--save_vocabulary->|                  |
 |              |                  |--检查文件存在----->|
 |              |                  |<----返回状态-----|
 |              |                  |--读取旧数据------->|
 |              |                  |<----返回数据-----|
 |              |                  |--构建新数据-------|
 |              |                  |--写入JSON文件---->|
 |              |                  |<----返回成功-----|
 |              |<----返回True-----|                  |
 |<--显示成功----|                  |                  |
```

---

## 时序图：加载词库

```
用户          app.py         VocabularyStore      文件系统
 |              |                  |                  |
 |--选择词库---->|                  |                  |
 |              |--load_vocabulary->|                  |
 |              |                  |--构建文件路径-----|
 |              |                  |--检查文件存在----->|
 |              |                  |<----返回True-----|
 |              |                  |--读取JSON文件---->|
 |              |                  |<----返回内容-----|
 |              |                  |--解析JSON--------|
 |              |<----返回Dict-----|                  |
 |--更新界面-----|                  |                  |
 |<--显示词库----|                  |                  |
```

---

## 目录结构详解

```
自动听写/
├── data/                           # 数据模块目录
│   ├── __init__.py                 # 模块初始化
│   ├── vocabulary_store.py         # 词库存储核心类
│   └── vocabularies/               # 词库文件存储目录
│       ├── 默认词库.json           # 默认词库
│       ├── 词库_1.json             # 用户词库1
│       └── 词库_2.json             # 用户词库2
├── src/                            # 源代码目录
│   ├── tts_engine.py               # TTS引擎
│   ├── audio_cache.py              # 音频缓存
│   ├── ocr_engine.py               # OCR引擎
│   └── ...
├── app.py                          # 主应用
└── test_vocabulary_storage.py      # 测试脚本
```

---

## JSON 数据结构详解

### 词库文件格式

```json
{
  "name": "默认词库",           // 词库名称
  "words": [                    // 单词列表
    {
      "en": "apple",            // 英文单词
      "cn": "苹果",             // 中文释义
      "checked": false          // 是否选中（用于听写）
    },
    {
      "en": "banana",
      "cn": "香蕉",
      "checked": false
    }
  ],
  "created_at": "2026-02-16T22:23:34.700253",  // 创建时间 (ISO 8601)
  "updated_at": "2026-02-16T22:23:34.700262"   // 更新时间 (ISO 8601)
}
```

### 词库列表格式（内存）

```python
[
  {
    "name": "默认词库",
    "word_count": 10,
    "created_at": "2026-02-16T22:23:34.700253",
    "updated_at": "2026-02-16T22:23:34.700262"
  },
  {
    "name": "词库_1",
    "word_count": 5,
    "created_at": "2026-02-16T20:00:00.000000",
    "updated_at": "2026-02-16T21:00:00.000000"
  }
]
```

---

## 错误处理机制

### 异常捕获层级

```
┌─────────────────────────────────────┐
│      UI 层 (app.py)                 │
│  - 显示错误提示                      │
│  - 用户友好的错误信息                 │
└───────────────┬─────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  业务逻辑层 (VocabularyStore)        │
│  - try/except 捕获异常               │
│  - 返回 bool/None 表示成功/失败       │
│  - print() 打印错误日志              │
└───────────────┬─────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  文件系统层                          │
│  - IOError, OSError                 │
│  - JSONDecodeError                  │
│  - PermissionError                  │
└─────────────────────────────────────┘
```

### 错误处理示例

```python
def save_vocabulary(self, name: str, words: List[Dict]) -> bool:
    try:
        # 文件操作
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(vocabulary_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存词库失败: {e}")  # 记录错误
        return False                 # 返回失败状态
```

---

## 性能优化

### 1. 文件系统操作

- ✅ 只在必要时读写文件
- ✅ 使用缓存避免重复读取
- ✅ 异步操作（后续可优化）

### 2. 内存管理

- ✅ 词库数据存储在 session_state
- ✅ 避免重复加载
- ✅ 只加载当前词库

### 3. UI 响应

- ✅ 自动保存不阻塞 UI
- ✅ 加载操作有 spinner 提示
- ✅ 使用 st.rerun() 及时更新界面

---

## 安全性考虑

### 1. 文件名安全

```python
def _get_file_path(self, name: str) -> str:
    # 只保留安全字符
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_name:
        safe_name = "vocabulary"
    return os.path.join(self.base_dir, f"{safe_name}.json")
```

### 2. 默认词库保护

```python
if st.session_state.current_vocabulary != "默认词库":
    # 只有非默认词库才能删除
    st.session_state.vocab_store.delete_vocabulary(...)
else:
    st.warning("不能删除默认词库")
```

### 3. 路径安全

- ✅ 使用 `os.path.join()` 构建路径
- ✅ 不允许用户指定绝对路径
- ✅ 限制在 `data/vocabularies/` 目录内

---

## 扩展性设计

### 1. 存储后端可替换

```python
# 当前实现：JSON 文件
class VocabularyStore:
    pass

# 未来可扩展：数据库存储
class VocabularyStoreDB:
    def __init__(self, db_connection):
        self.db = db_connection

    # 相同的接口
    def save_vocabulary(self, name, words):
        pass
```

### 2. 数据格式可扩展

```json
{
  "name": "词库名称",
  "words": [...],
  "created_at": "...",
  "updated_at": "...",
  // 未来可添加新字段
  "tags": ["小学", "英语"],
  "difficulty": "easy",
  "source": "教材",
  "metadata": {}
}
```

### 3. 功能可扩展

- 导入导出（CSV, Excel, Anki）
- 词库合并
- 词库同步（云端）
- 词库分享
- 词库统计

---

## 总结

任务1的架构设计遵循以下原则：

1. **分层架构**：UI层、业务逻辑层、数据持久化层清晰分离
2. **单一职责**：每个类/函数职责明确
3. **接口简洁**：VocabularyStore 提供简洁的 API
4. **错误处理**：完善的异常捕获和错误提示
5. **可扩展性**：易于添加新功能和新存储后端
6. **可测试性**：业务逻辑与 UI 分离，便于单元测试

整体架构稳定、清晰、易于维护。
