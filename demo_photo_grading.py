"""
拍照批改功能演示脚本
展示完整的使用流程和功能特性
"""
from src.handwriting_recognizer import HandwritingRecognizer
from PIL import Image, ImageDraw, ImageFont
import os


def create_demo_answer_sheet():
    """创建一个演示用的答案纸图片"""
    print("📝 创建演示答案纸...")

    # 创建白色背景
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)

    # 模拟手写答案（使用系统字体）
    answers = [
        "apple",
        "banana",
        "computer",
        "student",
        "teacher"
    ]

    try:
        # 尝试使用不同的字体
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()

    # 绘制答案
    y_position = 100
    for i, answer in enumerate(answers):
        text = f"{i+1}. {answer}"
        draw.text((100, y_position), text, fill='black', font=font)
        y_position += 80

    # 保存图片
    demo_path = "/tmp/demo_answer_sheet.jpg"
    img.save(demo_path)
    print(f"✅ 演示答案纸已创建: {demo_path}")

    return demo_path, answers


def demo_basic_workflow():
    """演示基本工作流程"""
    print("\n" + "=" * 70)
    print("🎯 拍照批改功能 - 基本工作流程演示")
    print("=" * 70)

    # 步骤1: 创建演示答案纸
    print("\n📌 步骤1: 准备答案纸")
    print("-" * 70)
    demo_image, demo_answers = create_demo_answer_sheet()
    print(f"答案纸内容:")
    for i, ans in enumerate(demo_answers):
        print(f"  {i+1}. {ans}")

    # 步骤2: 初始化识别器
    print("\n📌 步骤2: 初始化识别器")
    print("-" * 70)
    recognizer = HandwritingRecognizer()

    # 步骤3: 识别手写文字
    print("\n📌 步骤3: 识别手写文字")
    print("-" * 70)
    print("正在识别...")
    recognized_words = recognizer.recognize(demo_image, preprocess=True)
    print(f"✅ 识别完成，识别到 {len(recognized_words)} 个单词:")
    for i, word in enumerate(recognized_words):
        print(f"  {i+1}. {word}")

    # 步骤4: 准备标准答案
    print("\n📌 步骤4: 准备标准答案")
    print("-" * 70)
    expected_words = [
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'},
        {'en': 'computer', 'cn': '电脑'},
        {'en': 'student', 'cn': '学生'},
        {'en': 'teacher', 'cn': '老师'}
    ]
    print("标准答案:")
    for i, word in enumerate(expected_words):
        print(f"  {i+1}. {word['en']} - {word['cn']}")

    # 步骤5: 批改
    print("\n📌 步骤5: 智能批改")
    print("-" * 70)
    result = recognizer.compare(recognized_words, expected_words)

    # 显示成绩统计
    print(f"\n📊 成绩统计:")
    print(f"  正确数: {result['correct_count']}/{result['total']}")
    print(f"  正确率: {result['score']}%")

    # 评级
    score = result['score']
    if score >= 90:
        grade = "优秀 🌟"
    elif score >= 80:
        grade = "良好 👍"
    elif score >= 60:
        grade = "及格 ✓"
    else:
        grade = "不及格 ✗"
    print(f"  评级: {grade}")

    # 详细结果
    print(f"\n📋 详细结果:")
    for i, item in enumerate(result['words']):
        status = "✅" if item['correct'] else "❌"
        print(f"  {status} {i+1}. 标准: {item['expected']} ({item['chinese']}) | 识别: {item['recognized']}")

    print("\n" + "=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)


def demo_tolerance_features():
    """演示智能容错功能"""
    print("\n" + "=" * 70)
    print("🎯 智能容错功能演示")
    print("=" * 70)

    recognizer = HandwritingRecognizer()

    # 标准答案
    expected = [
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'},
        {'en': 'beautiful', 'cn': '美丽的'}
    ]

    # 测试用例
    test_cases = [
        {
            'name': '完全正确',
            'recognized': ['apple', 'banana', 'beautiful'],
            'expected_score': 100.0
        },
        {
            'name': '大小写混合',
            'recognized': ['Apple', 'BANANA', 'Beautiful'],
            'expected_score': 100.0
        },
        {
            'name': '带空格',
            'recognized': [' apple ', 'banana ', ' beautiful'],
            'expected_score': 100.0
        },
        {
            'name': '长单词拼写错误（容错）',
            'recognized': ['apple', 'banana', 'beautful'],  # 少一个i
            'expected_score': 100.0  # 长单词容错1个字符
        },
        {
            'name': '短单词拼写错误（不容错）',
            'recognized': ['aple', 'banana', 'beautiful'],  # apple少一个p
            'expected_score': 66.7  # 短单词不容错
        }
    ]

    for i, test_case in enumerate(test_cases):
        print(f"\n📌 测试用例 {i+1}: {test_case['name']}")
        print("-" * 70)

        result = recognizer.compare(test_case['recognized'], expected)

        print(f"识别结果: {test_case['recognized']}")
        print(f"标准答案: {[w['en'] for w in expected]}")
        print(f"正确率: {result['score']}%")

        # 详细结果
        for j, item in enumerate(result['words']):
            status = "✅" if item['correct'] else "❌"
            comparison = "一致" if item['correct'] else "不符"
            print(f"  {status} {j+1}. {item['expected']} vs {item['recognized']} ({comparison})")

        # 验证是否符合预期
        if abs(result['score'] - test_case['expected_score']) < 0.5:
            print(f"✅ 测试通过（期望: {test_case['expected_score']}%, 实际: {result['score']}%）")
        else:
            print(f"⚠️  测试结果: 期望 {test_case['expected_score']}%, 实际 {result['score']}%")

    print("\n" + "=" * 70)
    print("✅ 容错功能演示完成！")
    print("=" * 70)


def demo_preprocess():
    """演示图像预处理功能"""
    print("\n" + "=" * 70)
    print("🎯 图像预处理功能演示")
    print("=" * 70)

    # 创建测试图片
    print("\n📌 创建测试图片...")
    img = Image.new('RGB', (400, 300), color='lightgray')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except:
        font = ImageFont.load_default()

    draw.text((50, 100), "Test Image", fill='black', font=font)

    test_path = "/tmp/test_preprocess_demo.jpg"
    img.save(test_path)
    print(f"✅ 测试图片已创建: {test_path}")

    # 预处理
    print("\n📌 执行预处理...")
    recognizer = HandwritingRecognizer()
    processed_path = recognizer.preprocess_image(test_path)

    if os.path.exists(processed_path):
        print(f"✅ 预处理完成: {processed_path}")
        print(f"\n预处理步骤:")
        print(f"  1. 灰度化")
        print(f"  2. 对比度增强 (2.0x)")
        print(f"  3. 锐度增强 (1.5x)")
        print(f"  4. 中值滤波去噪 (size=3)")

        # 比较文件大小
        original_size = os.path.getsize(test_path)
        processed_size = os.path.getsize(processed_path)
        print(f"\n文件大小:")
        print(f"  原图: {original_size} bytes")
        print(f"  预处理图: {processed_size} bytes")

        # 清理文件
        os.remove(test_path)
        os.remove(processed_path)
        print(f"\n✅ 测试文件已清理")
    else:
        print("❌ 预处理失败")

    print("\n" + "=" * 70)
    print("✅ 预处理演示完成！")
    print("=" * 70)


def print_feature_summary():
    """打印功能特性总结"""
    print("\n" + "=" * 70)
    print("📚 功能特性总结")
    print("=" * 70)

    features = [
        ("📷 图像上传", "支持 JPG/PNG/JPEG 格式"),
        ("🔍 OCR识别", "使用 PaddleOCR 英文模型"),
        ("🎨 图像预处理", "灰度化、对比度增强、锐度增强、去噪"),
        ("🧠 智能比对", "大小写容错、空格处理、编辑距离"),
        ("📊 成绩统计", "正确率、正确数、评级系统"),
        ("📋 详细结果", "逐题对照、正确/错误标记"),
        ("🔄 重新批改", "支持重新上传和批改"),
        ("📖 友好UI", "清晰的提示和结果展示")
    ]

    for feature, description in features:
        print(f"  {feature}: {description}")

    print("\n" + "=" * 70)
    print("使用提示:")
    print("=" * 70)

    tips = [
        "1. 书写清晰工整，使用白纸和深色笔",
        "2. 光线充足，正面拍摄，避免倾斜",
        "3. 每行一个单词，按顺序书写",
        "4. 避免阴影、反光和涂改",
        "5. 长单词（>5字符）容忍1个字符差异",
        "6. 短单词需完全匹配（大小写不敏感）"
    ]

    for tip in tips:
        print(f"  {tip}")

    print("\n" + "=" * 70)


def main():
    """主函数"""
    print("\n" + "🌟" * 35)
    print("拍照批改功能 - 完整演示")
    print("🌟" * 35)

    # 演示1: 基本工作流程
    demo_basic_workflow()

    # 演示2: 智能容错功能
    demo_tolerance_features()

    # 演示3: 图像预处理
    demo_preprocess()

    # 功能特性总结
    print_feature_summary()

    print("\n" + "🎉" * 35)
    print("演示完成！感谢使用拍照批改功能！")
    print("🎉" * 35 + "\n")


if __name__ == '__main__':
    main()
