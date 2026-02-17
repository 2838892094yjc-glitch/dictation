# 自动英语听写软件 v3.1

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

一款智能化的英语听写辅助工具，支持OCR识别、AI纠错、语音播报、手写批改等功能。

## ✨ 主要特性

- 📸 **OCR识别** - 拍照识别单词表，自动提取英文和中文
- 🤖 **AI纠错** - 智能纠正OCR识别错误
- 🔊 **语音播报** - 支持多种音色和口音（美式/英式）
- ✍️ **手写批改** - 拍照批改手写答案
- 📚 **词库管理** - 创建、编辑、导入导出词库
- 🎯 **多种模式** - 英译中、中译英、拼写模式
- 📊 **历史记录** - 查看听写历史和错题本
- 🎨 **主题切换** - 多种界面主题可选
- 💾 **数据导入导出** - 支持JSON格式

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
streamlit run app.py
```

或使用启动脚本：

```bash
./start.sh
```

### 首次使用

1. 在"词库管理"页面创建或导入词库
2. 选择要听写的单词
3. 进入"听写播放"页面开始听写
4. 完成后在"答案批改"页面拍照批改

## 📖 详细文档

- [快速入门指南](QUICK_START.md)
- [用户手册](TASK1_USER_GUIDE.md)
- [API文档](docs/API.md)
- [部署指南](docs/DEPLOYMENT.md)
- [开发指南](docs/DEVELOPMENT.md)

## 🧪 测试

运行测试套件：

```bash
# 运行快速测试（跳过慢速测试）
./run_tests.sh

# 运行所有测试（包括慢速测试）
./run_tests.sh -a

# 生成覆盖率报告
./run_tests.sh -c

# 详细输出
./run_tests.sh -v

# 或使用pytest直接运行
python -m pytest tests/ -v -m "not slow"

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov=data --cov-report=html
```

## 📁 项目结构

```
自动听写/
├── app.py                 # 主应用
├── src/                   # 源代码
│   ├── ocr_engine.py     # OCR识别引擎
│   ├── tts_engine.py     # TTS语音引擎
│   ├── ai_corrector.py   # AI纠错模块
│   ├── handwriting_recognizer.py  # 手写识别
│   ├── audio_cache.py    # 音频缓存
│   ├── minimax_tts.py    # MiniMax TTS
│   ├── history_manager.py # 历史记录
│   ├── wrong_answer_manager.py # 错题本
│   ├── theme_manager.py  # 主题管理
│   └── logger.py         # 日志系统
├── data/                  # 数据存储
│   └── vocabulary_store.py # 词库存储
├── tests/                 # 测试套件
│   ├── conftest.py       # 共享fixtures
│   ├── test_ocr.py
│   ├── test_tts.py
│   ├── test_corrector.py
│   ├── test_handwriting.py
│   ├── test_audio_cache.py
│   ├── test_vocabulary_store.py
│   ├── test_flow.py      # 端到端流程测试
│   └── test_integration.py
├── docs/                  # 文档
│   ├── API.md            # API文档
│   └── DEPLOYMENT.md     # 部署指南
├── logs/                  # 日志目录
├── themes/                # 主题文件
├── pytest.ini             # 测试配置
├── run_tests.sh           # 测试脚本
├── requirements.txt       # 依赖列表
├── LICENSE                # MIT许可证
└── CHANGELOG.md           # 变更日志
```

## 🔧 配置

### 环境变量

```bash
# MiniMax API配置（可选）
export MINIMAX_API_KEY="your_api_key"
export MINIMAX_GROUP_ID="your_group_id"
```

### 配置文件

在 `.streamlit/config.toml` 中配置Streamlit：

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
```

## 🎯 功能模块

### 1. 词库管理
- 创建和编辑词库
- OCR识别单词表
- AI智能纠错
- 导入导出词库

### 2. 听写播放
- 三种听写模式
- 自动/手动播放
- 音频缓存加速
- 多种音色选择

### 3. 答案批改
- 手写识别
- 自动批改
- 错题统计
- 历史记录

### 4. 历史记录
- 查看听写历史
- 成绩统计
- 错题本管理
- 数据导出

## 🛠️ 技术栈

- **前端框架**: Streamlit
- **OCR引擎**: PaddleOCR
- **TTS引擎**: Edge-TTS / MiniMax
- **图像处理**: Pillow
- **测试框架**: Pytest
- **代码质量**: Black, Flake8, MyPy

## 📊 性能优化

- ✅ 音频预加载和缓存
- ✅ OCR结果缓存
- ✅ 并发音频生成
- ✅ 图像预处理优化
- ✅ 懒加载模块

## 🐛 问题排查

### OCR识别不准确
- 确保图片清晰，光线充足
- 尝试调整图片角度
- 使用图像预处理功能

### 语音播报失败
- 检查网络连接
- 尝试切换TTS引擎
- 查看错误日志

### 手写识别错误
- 确保字迹清晰
- 避免背景干扰
- 使用图像增强功能

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📮 联系方式

- 项目主页: [GitHub](https://github.com/yourusername/dictation)
- 问题反馈: [Issues](https://github.com/yourusername/dictation/issues)

## 🙏 致谢

- PaddleOCR团队
- Edge-TTS项目
- Streamlit社区
- 所有贡献者

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

---

**注意**: 首次运行需要下载OCR模型，可能需要几分钟时间。
