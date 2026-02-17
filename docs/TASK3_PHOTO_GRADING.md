# 任务3: 拍照批改功能

## 任务目标
拍照上传手写答案纸，自动识别并批改

## 文件变更

### 新增文件
```
src/handwriting_recognizer.py   # 手写识别模块 ✅
test_handwriting.py              # 测试脚本 ✅
docs/TASK3_IMPLEMENTATION.md     # 实现文档 ✅
```

### 修改文件
```
app.py                          # 添加拍照批改 UI ✅
```

## 功能清单
- [x] 拍照上传答案纸
- [x] 手写文字 OCR 识别
- [x] 智能比对（忽略大小写）
- [x] 错误可视化标记
- [x] 成绩统计
- [x] 批改结果展示

## 技术方案

### OCR 方案选择
1. **PaddleOCR** - 现有依赖，支持中文识别
2. **EasyOCR** - PyTorch 实现，识别效果好但慢

推荐使用 PaddleOCR，利用现有依赖。

### 识别流程
```
1. 用户拍照/上传答案纸
2. 图像预处理（灰度、去噪）
3. OCR 识别文字区域
4. 提取每个单词
5. 与标准答案比对
6. 显示结果
```

## 数据结构

### 用户答案 (识别后)
```python
{
    "words": [
        {"expected": "apple", "recognized": "apple", "correct": true},
        {"expected": "banana", "recognized": "bananq", "correct": false}
    ],
    "score": 50,
    "total": 2
}
```

## 实现步骤

### 步骤1: 创建手写识别模块
- HandwritingRecognizer 类
- preprocess_image() 图像预处理
- recognize() 识别文字
- compare() 与答案比对

### 步骤2: 添加拍照批改 UI
- 在"答案批改"页面添加上传区域
- 显示识别进度
- 展示批改结果

### 步骤3: 实现批改逻辑
- 对齐识别结果与标准答案
- 计算正确率
- 标记错误单词

### 步骤4: 优化体验
- 图像旋转校正
- 噪点处理
- 错误提示

## 测试要点
1. 上传清晰的书写图片能识别
2. 识别结果与标准答案比对正确
3. 错误单词有标记

## 预计改动量
- 新增代码: ~250 行
- 修改代码: ~100 行

## 实现状态
✅ **已完成** (2026-02-16)

详细实现文档: [TASK3_IMPLEMENTATION.md](./TASK3_IMPLEMENTATION.md)

---

## 上一任务
[任务2: 听写模式切换](./TASK2_DICTATION_MODE.md)

## 下一任务
[任务4: 错题本功能](./TASK4_WRONG_ANSWERS.md)
