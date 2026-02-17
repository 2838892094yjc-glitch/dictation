# 自动英语听写 - 开发文档

## 项目概述
基于 Streamlit 的英语听写应用，使用 MiniMax TTS + PaddleOCR 技术。

## 当前状态

**更新日期**: 2026-02-17

### 完成进度: 5/8 (62.5%)

| 状态 | 数量 |
|------|------|
| ✅ 已完成 | 5 |
| ⬜ 待完成 | 3 |

---

## 启动脚本

### 基本用法
```bash
cd /Users/yangjingchi/Desktop/自动听写
./init.sh
```

### 命令行选项
```bash
./init.sh dev     # 启动开发服务器 (端口 8501)
./init.sh test    # 启动测试服务器 (端口 8502)
./init.sh run     # 生产环境启动
./init.sh check   # 环境检查
./init.sh stop    # 停止所有服务
./init.sh help    # 显示帮助
```

---

## 开发任务清单

| # | 任务 | 状态 | 文档 |
|---|------|------|------|
| 1 | 词库持久化存储 | ✅ 已完成 | [查看](./TASK1_IMPLEMENTATION.md) |
| 2 | 听写模式切换 | ✅ 已完成 | [查看](./TASK2_IMPLEMENTATION.md) |
| 3 | 拍照批改功能 | ✅ 已完成 | [查看](./TASK3_IMPLEMENTATION.md) |
| 4 | 错题本功能 | ⬜ 待开始 | [查看](./TASK4_WRONG_ANSWERS.md) |
| 5 | 学习历史记录 | ✅ 已完成 | [查看](./TASK5_IMPLEMENTATION.md) |
| 6 | 词库导入/导出 | ⬜ 待开始 | [查看](./TASK6_IMPORT_EXPORT.md) |
| 7 | 深色模式/主题 | ⬜ 待开始 | [查看](./TASK7_THEME.md) |
| 8 | 代码优化与测试 | ⬜ 待开始 | [查看](./TASK8_OPTIMIZATION.md) |

---

## 已实现功能

### 核心功能
- ✅ OCR 识别单词 (PaddleOCR)
- ✅ TTS 语音播报 (MiniMax API)
- ✅ AI 拼写纠正
- ✅ 音频缓存

### 已完成任务
- ✅ 词库持久化存储 (本地 JSON)
- ✅ 听写模式切换 (英译中/中译英/拼写)
- ✅ 拍照批改 (手写识别+智能比对)
- ✅ 学习历史记录

### 待实现功能
- ⬜ 错题本
- ⬜ 词库导入/导出
- ⬜ 深色模式
- ⬜ 测试覆盖

---

## 项目结构

```
/Users/yangjingchi/Desktop/自动听写/
├── app.py                    # 主应用
├── init.sh                   # 启动脚本
├── requirements.txt          # 依赖
│
├── src/                      # 源代码
│   ├── ocr_engine.py         # OCR 识别
│   ├── minimax_tts.py        # MiniMax TTS
│   ├── tts_engine.py         # 备用 TTS
│   ├── ai_corrector.py       # AI 纠正
│   ├── audio_cache.py        # 音频缓存
│   └── theme_manager.py      # 主题管理
│
├── data/                     # 数据目录
│   ├── vocabularies/         # 词库文件
│   ├── history.json          # 历史记录
│   └── settings.json         # 设置
│
├── docs/                     # 开发文档
│   ├── STATUS.md             # 开发状态报告
│   ├── TASK1_IMPLEMENTATION.md
│   ├── TASK2_IMPLEMENTATION.md
│   ├── TASK3_IMPLEMENTATION.md
│   ├── TASK4_WRONG_ANSWERS.md
│   ├── TASK5_IMPLEMENTATION.md
│   ├── TASK6_IMPORT_EXPORT.md
│   ├── TASK7_THEME.md
│   └── TASK8_OPTIMIZATION.md
│
└── tests/                    # 测试目录
```

---

## 端口说明

| 端口 | 用途 |
|------|------|
| 8501 | 主开发窗口 |
| 8502 | 测试/验证窗口 |

---

## 技术栈

- **前端**: Streamlit
- **OCR**: PaddleOCR
- **TTS**: MiniMax API
- **存储**: 本地 JSON
- **Python**: 3.8+

---

## 下一步

详细状态报告: [STATUS.md](./STATUS.md)

开始新任务请告诉我任务编号 (5-8)。
