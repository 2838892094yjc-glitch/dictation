# API 文档

## OCR引擎 (ocr_engine.py)

### OCREngine

OCR识别引擎，用于识别图片中的文字。

#### 初始化

```python
from src.ocr_engine import OCREngine

engine = OCREngine()
```

#### 方法

##### recognize(image_path: str) -> List[Tuple[str, float]]

识别图片中的文字。

**参数:**
- `image_path`: 图片路径

**返回:**
- 识别结果列表 `[(文字, 置信度), ...]`

**示例:**
```python
texts = engine.recognize('wordlist.jpg')
for text, confidence in texts:
    print(f"{text} (置信度: {confidence:.2f})")
```

##### extract_word_pairs(texts: List[Tuple[str, float]]) -> List[dict]

从识别结果中提取单词对（英文+中文）。

**参数:**
- `texts`: OCR识别结果

**返回:**
- 单词对列表 `[{'english': '...', 'chinese': '...', 'raw': '...', 'confidence': ...}, ...]`

**示例:**
```python
pairs = engine.extract_word_pairs(texts)
for pair in pairs:
    print(f"{pair['english']} = {pair['chinese']}")
```

### 便捷函数

##### extract_words_from_image(image_path: str) -> List[dict]

从图片中提取单词对（一步到位）。

**参数:**
- `image_path`: 图片路径

**返回:**
- 单词列表 `[{en: str, cn: str}, ...]`

**示例:**
```python
from src.ocr_engine import extract_words_from_image

words = extract_words_from_image('wordlist.jpg')
```

---

## TTS引擎 (tts_engine.py)

### TTSEngine

文字转语音引擎。

#### 初始化

```python
from src.tts_engine import TTSEngine

engine = TTSEngine()
```

#### 方法

##### set_voice(voice_type: str)

设置语音类型。

**参数:**
- `voice_type`: 音色类型
  - `"us_female"`: 美式英语女声
  - `"us_male"`: 美式英语男声
  - `"uk_female"`: 英式英语女声
  - `"uk_male"`: 英式英语男声
  - `"chinese"`: 中文

**示例:**
```python
engine.set_voice("us_female")
```

##### set_rate(speed: float)

设置语速。

**参数:**
- `speed`: 语速倍数 (0.5-2.0)，1.0为正常速度

**示例:**
```python
engine.set_rate(1.2)  # 加速20%
```

##### speak(text: str, save_path: Optional[str] = None) -> str

播报文字。

**参数:**
- `text`: 要播报的文字
- `save_path`: 保存路径，None则创建临时文件

**返回:**
- 音频文件路径

**示例:**
```python
audio_path = engine.speak("Hello World")
```

##### get_audio_bytes(text: str) -> bytes

获取音频文件的二进制数据。

**参数:**
- `text`: 要播报的文字

**返回:**
- 音频数据（bytes）

**示例:**
```python
audio_data = engine.get_audio_bytes("Hello")
```

### 便捷函数

##### speak_word(word: str, meaning: str = "", mode: str = "en_to_cn", accent: str = "us") -> str

播报单词的便捷函数。

**参数:**
- `word`: 英文单词
- `meaning`: 中文释义
- `mode`: 播报模式
  - `"en_to_cn"`: 报英文，要求写中文
  - `"cn_to_en"`: 报中文，要求写英文
  - `"spell"`: 报英文+释义，要求拼写
- `accent`: 英语口音，`"us"` 或 `"uk"`

**返回:**
- 音频文件路径

**示例:**
```python
from src.tts_engine import speak_word

audio_path = speak_word("apple", "苹果", mode="en_to_cn", accent="us")
```

---

## AI纠正器 (ai_corrector.py)

### AICorrector

AI单词纠正器。

#### 初始化

```python
from src.ai_corrector import AICorrector

corrector = AICorrector()
```

#### 方法

##### correct_word(word: str, context: str = "") -> Tuple[str, str]

纠正单个单词。

**参数:**
- `word`: 待纠正的单词
- `context`: 上下文（中文释义）

**返回:**
- `(纠正后的单词, 纠正说明)`

**示例:**
```python
corrected, note = corrector.correct_word("ofien")
print(f"{corrected} - {note}")  # often - 纠正: ofien -> often
```

##### correct_word_list(words: List[Dict]) -> Tuple[List[Dict], List[Dict]]

纠正单词列表。

**参数:**
- `words`: 单词列表 `[{'english': '...', 'chinese': '...'}, ...]`

**返回:**
- `(纠正后的列表, 修改记录列表)`

**示例:**
```python
words = [
    {'english': 'ofien', 'chinese': '经常'},
    {'english': 'apple', 'chinese': '苹果'},
]

corrected, changes = corrector.correct_word_list(words)
```

### 便捷函数

##### correct_spelling(raw_words: List[dict]) -> List[dict]

纠正单词拼写（app.py调用的接口）。

**参数:**
- `raw_words`: 原始单词列表 `[{'en': '...', 'cn': '...'}, ...]`

**返回:**
- 纠正后的单词列表 `[{'en': '...', 'cn': '...', 'corrected': '...'}, ...]`

**示例:**
```python
from src.ai_corrector import correct_spelling

words = [{'en': 'ofien', 'cn': '经常'}]
corrected = correct_spelling(words)
```

---

## 手写识别器 (handwriting_recognizer.py)

### HandwritingRecognizer

手写识别和批改器。

#### 初始化

```python
from src.handwriting_recognizer import HandwritingRecognizer

recognizer = HandwritingRecognizer(lang='ch')
```

**参数:**
- `lang`: 语言模型，`'ch'`(中英文混合) 或 `'en'`(仅英文)

#### 方法

##### recognize(image_path: str, preprocess: bool = True, keep_chinese: bool = False) -> List[str]

识别手写文字。

**参数:**
- `image_path`: 图片路径
- `preprocess`: 是否进行预处理
- `keep_chinese`: 是否保留中文字符

**返回:**
- 识别出的文字列表

**示例:**
```python
words = recognizer.recognize('answer.jpg')
```

##### compare(recognized_words: List[str], expected_words: List[Dict], mode: str = 'en_to_cn') -> Dict

比对识别结果和标准答案。

**参数:**
- `recognized_words`: 识别出的单词列表
- `expected_words`: 标准答案列表 `[{'en': '...', 'cn': '...', 'expected': '...'}, ...]`
- `mode`: 听写模式 `'en_to_cn'` | `'cn_to_en'` | `'spell'`

**返回:**
- 批改结果
```python
{
    'words': [{'expected': '...', 'recognized': '...', 'correct': bool}, ...],
    'score': float,  # 正确率百分比
    'total': int,
    'correct_count': int
}
```

**示例:**
```python
result = recognizer.compare(
    recognized_words=['apple', 'banana'],
    expected_words=[
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'}
    ],
    mode='cn_to_en'
)

print(f"正确率: {result['score']}%")
```

---

## 音频缓存 (audio_cache.py)

### AudioCache

音频缓存管理器。

#### 初始化

```python
from src.audio_cache import AudioCache

cache = AudioCache()
```

#### 方法

##### preload_words(words: List[Dict], mode: str = "en_to_cn", accent: str = "us", use_minimax: bool = True, voice_en: str = "expressive_narrator", voice_cn: str = "xiaoxiao")

预加载单词音频。

**参数:**
- `words`: 单词列表
- `mode`: 听写模式
- `accent`: 英语口音
- `use_minimax`: 是否使用MiniMax
- `voice_en`: 英文音色
- `voice_cn`: 中文音色

**示例:**
```python
words = [
    {'en': 'apple', 'cn': '苹果'},
    {'en': 'banana', 'cn': '香蕉'},
]

cache.preload_words(words, mode='en_to_cn', accent='us')
```

##### get_audio(word: str, mode: str = "en", accent: str = "us", use_minimax: bool = True, voice_en: str = "expressive_narrator", voice_cn: str = "xiaoxiao") -> Optional[str]

获取音频路径。

**参数:**
- `word`: 单词
- `mode`: 模式 `"en"` 或 `"cn"`
- `accent`: 口音
- `use_minimax`: 是否使用MiniMax
- `voice_en`: 英文音色
- `voice_cn`: 中文音色

**返回:**
- 音频文件路径

**示例:**
```python
audio_path = cache.get_audio('apple', mode='en', accent='us')
```

##### get_preload_status() -> Dict[str, float]

返回后台预加载状态。

**返回:**
```python
{
    "total": int,
    "completed": int,
    "errors": int,
    "active": bool,
    "finished": bool,
    "progress": float,
}
```

**示例:**
```python
status = cache.get_preload_status()
print(f"进度: {status['progress']*100:.1f}%")
```

---

## 词库存储 (vocabulary_store.py)

### VocabularyStore

词库存储管理器。

#### 初始化

```python
from data.vocabulary_store import VocabularyStore

store = VocabularyStore(data_dir='./data/vocabularies')
```

#### 方法

##### save_vocabulary(name: str, data: dict) -> bool

保存词库。

**参数:**
- `name`: 词库名称
- `data`: 词库数据 `{'name': '...', 'words': [...], 'description': '...'}`

**返回:**
- 是否成功

**示例:**
```python
vocab_data = {
    'name': '我的词库',
    'words': [{'en': 'apple', 'cn': '苹果'}],
    'description': '测试词库'
}

store.save_vocabulary('我的词库', vocab_data)
```

##### load_vocabulary(name: str) -> Optional[dict]

加载词库。

**参数:**
- `name`: 词库名称

**返回:**
- 词库数据或None

**示例:**
```python
vocab = store.load_vocabulary('我的词库')
if vocab:
    print(f"加载了 {len(vocab['words'])} 个单词")
```

##### list_vocabularies() -> List[dict]

列出所有词库。

**返回:**
- 词库列表 `[{'name': '...', 'word_count': ..., 'created_at': '...'}, ...]`

**示例:**
```python
vocabs = store.list_vocabularies()
for vocab in vocabs:
    print(f"{vocab['name']}: {vocab['word_count']} 个单词")
```

##### delete_vocabulary(name: str) -> bool

删除词库。

**参数:**
- `name`: 词库名称

**返回:**
- 是否成功

##### export_vocabulary(name: str, export_path: str) -> bool

导出词库。

**参数:**
- `name`: 词库名称
- `export_path`: 导出文件路径

**返回:**
- 是否成功

##### import_vocabulary(import_path: str) -> bool

导入词库。

**参数:**
- `import_path`: 导入文件路径

**返回:**
- 是否成功

---

## 日志系统 (logger.py)

### 获取日志器

```python
from src.logger import get_logger

logger = get_logger("my_module")
logger.info("这是一条日志")
logger.error("这是错误日志")
```

### 模块日志器

```python
from src.logger import ModuleLoggers

# 获取预定义的模块日志器
ocr_logger = ModuleLoggers.ocr()
tts_logger = ModuleLoggers.tts()
cache_logger = ModuleLoggers.cache()
```

### 日志装饰器

```python
from src.logger import log_function_call, log_performance

@log_function_call("my_module")
@log_performance("my_module")
def my_function(x, y):
    return x + y
```

### 设置日志级别

```python
from src.logger import set_log_level, enable_debug, disable_debug
import logging

set_log_level(logging.DEBUG)  # 设置为调试级别
enable_debug()  # 启用调试模式
disable_debug()  # 禁用调试模式
```

---

## 历史管理器 (history_manager.py)

### HistoryManager

历史记录管理器。

#### 初始化

```python
from src.history_manager import HistoryManager

manager = HistoryManager(data_dir='./data/history')
```

#### 方法

##### add_record(mode: str, vocabulary_name: str, total_words: int, correct_count: int, duration_seconds: int, wrong_words: List[dict])

添加历史记录。

**参数:**
- `mode`: 听写模式
- `vocabulary_name`: 词库名称
- `total_words`: 总单词数
- `correct_count`: 正确数量
- `duration_seconds`: 用时（秒）
- `wrong_words`: 错误单词列表

**示例:**
```python
manager.add_record(
    mode='en_to_cn',
    vocabulary_name='测试词库',
    total_words=10,
    correct_count=8,
    duration_seconds=120,
    wrong_words=[{'en': 'apple', 'cn': '苹果', 'user_answer': '苹'}]
)
```

##### get_all_records() -> List[dict]

获取所有历史记录。

##### get_statistics() -> dict

获取统计信息。

**返回:**
```python
{
    'total_sessions': int,
    'total_words': int,
    'average_score': float,
    'total_duration': int,
    'mode_stats': dict,
    'recent_scores': list
}
```

##### get_wrong_words_frequency(limit: int = 20) -> List[dict]

获取高频错词。

---

## 错题本管理器 (wrong_answer_manager.py)

### WrongAnswerManager

错题本管理器。

#### 初始化

```python
from src.wrong_answer_manager import WrongAnswerManager

manager = WrongAnswerManager(data_dir='./data/wrong_answers')
```

#### 方法

##### add_wrong_answer(en: str, cn: str, user_answer: str)

添加错题。

##### get_all_wrong_answers() -> List[dict]

获取所有错题。

##### get_review_words() -> List[dict]

获取复习单词（按错误次数排序）。

##### get_stats() -> dict

获取统计信息。

**返回:**
```python
{
    'total_wrong': int,
    'unique_words': int
}
```

##### remove_word(en: str)

移除单词。

##### clear_all()

清空错题本。

---

## 错误处理

所有API都应该进行适当的错误处理：

```python
try:
    result = some_api_call()
except Exception as e:
    print(f"错误: {e}")
    # 处理错误
```

## 类型提示

建议使用类型提示以提高代码可读性：

```python
from typing import List, Dict, Optional, Tuple

def process_words(words: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # 处理逻辑
    return processed_words
```
