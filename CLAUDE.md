# 自动英语听写软件 - Agent Teams 配置

## 项目概述

这是一款智能英语听写工具，支持拍照上传单词表、语音播报、中英互译听写模式。

技术栈：
- 前端：Streamlit
- OCR：PaddleOCR
- TTS：Edge TTS / pyttsx3
- 图像处理：Pillow

## Agent Teams

### @ocr-agent - OCR 识别专家

**职责范围**：
- OCR 引擎开发和优化（`src/ocr_engine.py`）
- 图像预处理和文字识别
- 单词提取和格式化
- OCR 相关的错误处理和性能优化

**专长**：
- PaddleOCR API 使用
- 图像处理（PIL/OpenCV）
- 中英文文字识别
- 表格识别和单词提取

**上下文文件**：
- `src/ocr_engine.py`
- `demo_test.py`（OCR 测试相关）

### @tts-agent - 语音合成专家

**职责范围**：
- TTS 引擎开发和优化（`src/tts_engine.py`）
- 多语音引擎集成（Edge TTS, pyttsx3）
- 语音播放控制（语速、音量、重复）
- 音频文件管理

**专长**：
- Edge TTS / pyttsx3 API
- 异步音频播放
- 多语言语音合成
- 语音质量优化

**上下文文件**：
- `src/tts_engine.py`
- 相关的音频配置代码

### @ui-agent - 界面开发专家

**职责范围**：
- Streamlit 界面开发（`app.py`）
- 用户交互流程设计
- 页面布局和样式
- 主题配置（`themes/`）

**专长**：
- Streamlit 组件和布局
- 会话状态管理
- 用户体验优化
- 响应式设计

**上下文文件**：
- `app.py`
- `themes/`
- `design_preview/`

### @test-agent - 测试和质量保证专家

**职责范围**：
- 编写和维护测试代码
- 性能测试和优化
- Bug 修复和回归测试
- 代码质量审查

**专长**：
- Python 单元测试
- 集成测试
- 性能分析
- 错误诊断

**上下文文件**：
- `demo_test.py`
- `requirements.txt`

### @devops-agent - 部署和运维专家

**职责范围**：
- 部署脚本维护（`start.sh`, `init.sh`）
- 依赖管理（`requirements.txt`）
- 环境配置
- 文档维护

**专长**：
- Bash 脚本
- Python 依赖管理
- 跨平台兼容性
- 文档编写

**上下文文件**：
- `start.sh`
- `start_dual_window.sh`
- `init.sh`
- `run_test_window.command`
- `requirements.txt`
- `README.md`
- `PRD.md`

## 协作流程

### 新功能开发流程

1. **需求分析**：由相关领域的 agent 评估需求
2. **设计方案**：多个 agents 协同设计方案
3. **并行开发**：各 agent 负责各自模块
4. **集成测试**：@test-agent 进行集成测试
5. **部署上线**：@devops-agent 处理部署

### 示例：添加新的 OCR 功能

```
@ocr-agent: 实现新的 OCR 预处理算法
@test-agent: 编写相关单元测试
@ui-agent: 更新 UI 界面以展示新功能
@devops-agent: 更新文档说明
```

### 示例：优化语音播放

```
@tts-agent: 优化语音合成质量
@ui-agent: 添加语音控制选项
@test-agent: 测试不同语速和音量
```

## 项目文件结构

```
.
├── app.py                 # 主应用入口 [@ui-agent]
├── requirements.txt       # 依赖管理 [@devops-agent]
├── src/
│   ├── ocr_engine.py     # OCR 模块 [@ocr-agent]
│   └── tts_engine.py     # TTS 模块 [@tts-agent]
├── demo_test.py          # 测试文件 [@test-agent, @ocr-agent]
├── themes/               # 主题配置 [@ui-agent]
├── design_preview/       # 设计预览 [@ui-agent]
├── docs/                 # 文档目录 [@devops-agent]
├── start.sh              # 启动脚本 [@devops-agent]
├── init.sh               # 初始化脚本 [@devops-agent]
├── README.md             # 项目说明 [@devops-agent]
└── PRD.md                # 需求文档 [@devops-agent]
```

## 当前开发优先级

### Phase 1: MVP 核心功能
- [ ] OCR 识别准确性优化 [@ocr-agent]
- [ ] TTS 多引擎支持 [@tts-agent]
- [ ] 基础听写流程完善 [@ui-agent]
- [ ] 单元测试覆盖 [@test-agent]

### Phase 2: 功能增强
- [ ] 手写识别支持 [@ocr-agent]
- [ ] 自定义语音选项 [@tts-agent]
- [ ] 学习进度追踪 [@ui-agent]
- [ ] 性能优化 [@test-agent, @devops-agent]

### Phase 3: 高级特性
- [ ] 拍照批改功能 [@ocr-agent, @ui-agent]
- [ ] 错题本系统 [@ui-agent, @devops-agent]
- [ ] 内置词库 [@devops-agent]

## 使用说明

### 调用特定 Agent

在 Claude Code 中使用 `@agent-name` 来调用特定的 agent：

```
@ocr-agent 请优化图像预处理算法
@tts-agent 添加对英式发音的支持
@ui-agent 改进听写页面的布局
@test-agent 为新功能编写测试用例
@devops-agent 更新部署文档
```

### 多 Agent 协作

对于复杂任务，可以同时调用多个 agents：

```
@ocr-agent @ui-agent
实现新的单词表格式识别功能，并在界面中添加相应的预览选项
```

## 最佳实践

1. **明确职责**：每个 agent 专注于自己的领域
2. **协同工作**：跨模块功能需要多个 agents 配合
3. **测试先行**：新功能开发时同时让 @test-agent 参与
4. **文档同步**：功能变更时及时让 @devops-agent 更新文档
5. **代码审查**：重要变更由相关 agents 共同审查

## 技术规范

### 代码风格
- Python 遵循 PEP 8
- 函数和类添加 docstring
- 重要逻辑添加注释

### Git 提交规范
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/配置相关

### 测试要求
- 新功能必须有单元测试
- 关键路径需要集成测试
- 性能敏感代码需要性能测试

## 相关资源

- [PRD 文档](./PRD.md) - 详细的产品需求
- [README](./README.md) - 快速开始指南
- [PaddleOCR 文档](https://github.com/PaddlePaddle/PaddleOCR)
- [Edge TTS 文档](https://github.com/rany2/edge-tts)
- [Streamlit 文档](https://docs.streamlit.io)
