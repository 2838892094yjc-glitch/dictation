# 任务1: 词库持久化存储

## 任务目标
实现词库的本地保存和加载，支持多词库管理

## 文件变更

### 新增文件
```
data/
├── __init__.py
└── vocabulary_store.py   # 词库存储模块
```

### 修改文件
```
app.py                     # 集成存储功能
```

## 功能清单
- [ ] 保存词库到 JSON 文件
- [ ] 加载已有词库
- [ ] 创建新词库
- [ ] 删除词库
- [ ] 重命名词库
- [ ] 默认词库加载

## session_state 结构 (保持不变)
```python
st.session_state.word_list      # [{en, cn, checked}, ...]
st.session_state.selected_words # 选中的单词
st.session_state.current_index  # 当前进度
```

## 数据结构

### 词库文件格式 (data/vocabularies/)
```json
{
  "default": {
    "name": "默认词库",
    "words": [
      {"en": "apple", "cn": "苹果", "checked": false},
      {"en": "banana", "cn": "香蕉", "checked": false}
    ],
    "created_at": "2026-02-16T20:00:00",
    "updated_at": "2026-02-16T20:00:00"
  }
}
```

## 实现步骤

### 步骤1: 创建目录结构
```bash
mkdir -p data/vocabularies
```

### 步骤2: 创建 vocabulary_store.py
- VocabularyStore 类
- save_vocabulary() 保存词库
- load_vocabulary() 加载词库
- list_vocabularies() 列出所有词库
- delete_vocabulary() 删除词库

### 步骤3: 修改 app.py
- 导入 vocabulary_store
- 应用启动时加载默认词库
- 添加"保存词库"按钮
- 添加词库管理 UI

## 测试要点
1. 新增单词后保存，刷新页面词库仍在
2. 删除词库后确认删除
3. 多词库间切换正常

## 预计改动量
- 新增代码: ~100 行
- 修改代码: ~30 行

---

## 下一任务
[任务2: 听写模式切换](./TASK2_DICTATION_MODE.md)
