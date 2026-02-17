# 任务6：词库导入/导出 - 快速参考

## 功能概览

实现了完整的词库导入/导出系统，支持多种格式，并预置了常用词库。

## 核心功能

### 1. 导入功能
- **JSON导入**: 完整数据结构，包含元数据
- **TXT导入**: 简单文本格式，每行"英文 中文"
- **CSV导入**: 表格格式，包含en和cn列

### 2. 导出功能
- **JSON导出**: 完整数据，可再次导入
- **TXT导出**: 纯文本，便于编辑
- **CSV导出**: 表格格式，Excel兼容

### 3. 预置词库
- 中考核心词汇: 100个
- CET-4核心词汇: 101个
- CET-6核心词汇: 99个
- 高考核心词汇: 99个

## 使用方法

### 在UI中使用

1. **导入词库**
   - 进入"词库管理"页面
   - 点击"📥 导入词库"标签
   - 上传文件（json/txt/csv）
   - 输入词库名称（可选）
   - 点击"开始导入"

2. **导出词库**
   - 进入"词库管理"页面
   - 点击"📤 导出词库"标签
   - 选择导出格式
   - 点击"导出词库"
   - 点击下载按钮

3. **加载预置词库**
   - 进入"词库管理"页面
   - 点击"📚 预置词库"标签
   - 浏览可用词库
   - 点击"预览"查看内容
   - 点击"加载"使用词库

### 在代码中使用

```python
from data.vocabulary_store import VocabularyStore

store = VocabularyStore()

# 导入
result = store.import_from_json("path/to/vocab.json", "我的词库")
result = store.import_from_txt("path/to/vocab.txt", "我的词库")
result = store.import_from_csv("path/to/vocab.csv", "我的词库")

# 导出
store.export_to_json("我的词库", "output.json")
store.export_to_txt("我的词库", "output.txt")
store.export_to_csv("我的词库", "output.csv")

# 预置词库
builtin_vocabs = store.list_builtin_vocabularies()
result = store.load_builtin_vocabulary(file_path, "新词库名")
```

## 文件格式

### JSON格式
```json
{
  "name": "词库名称",
  "description": "描述（可选）",
  "words": [
    {"en": "apple", "cn": "苹果", "checked": false}
  ]
}
```

### TXT格式
```
apple 苹果
banana 香蕉
```

### CSV格式
```csv
en,cn
apple,苹果
banana,香蕉
```

## 测试命令

```bash
# 运行完整测试
python3 test_import_export.py

# 运行功能演示
python3 demo_import_export.py
```

## 文件位置

- 核心模块: `/Users/yangjingchi/Desktop/自动听写/data/vocabulary_store.py`
- UI界面: `/Users/yangjingchi/Desktop/自动听写/app.py`
- 预置词库: `/Users/yangjingchi/Desktop/自动听写/data/builtin/`
- 测试脚本: `/Users/yangjingchi/Desktop/自动听写/test_import_export.py`
- 演示脚本: `/Users/yangjingchi/Desktop/自动听写/demo_import_export.py`

## 技术特点

1. **格式灵活**: 支持3种常用格式
2. **数据安全**: 导入时验证数据完整性
3. **用户友好**: 详细的格式说明和错误提示
4. **开箱即用**: 预置常用词库
5. **格式转换**: 支持不同格式间转换

## 常见问题

**Q: TXT格式导入时需要注意什么？**
A: 每行一个单词，英文和中文用空格分隔，必须指定词库名称。

**Q: 导出的文件可以在其他设备使用吗？**
A: 可以，导出的文件可以在任何安装了本软件的设备上导入使用。

**Q: 预置词库可以修改吗？**
A: 预置词库是只读的，但可以加载后另存为新词库进行修改。

**Q: 支持批量导入吗？**
A: 当前版本支持单文件导入，可以多次导入不同文件。

## 下一步

参考文档: [任务7: 深色模式主题](./docs/TASK7_THEME.md)
