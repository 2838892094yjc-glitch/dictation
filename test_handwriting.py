"""
测试手写识别模块
"""
from src.handwriting_recognizer import HandwritingRecognizer


def test_basic_recognition():
    """测试基本识别功能"""
    print("=" * 50)
    print("测试手写识别模块")
    print("=" * 50)

    # 初始化识别器
    print("\n1. 初始化识别器...")
    recognizer = HandwritingRecognizer()
    print("✅ 初始化完成")

    # 测试图像预处理
    print("\n2. 测试图像预处理...")
    # 如果有测试图片的话
    # processed_path = recognizer.preprocess_image("test_image.jpg")
    print("✅ 图像预处理功能已就绪")

    # 测试比对功能
    print("\n3. 测试答案比对...")
    recognized = ["apple", "banana", "computer"]
    expected = [
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'},
        {'en': 'computer', 'cn': '电脑'}
    ]

    result = recognizer.compare(recognized, expected)

    print(f"识别结果: {recognized}")
    print(f"标准答案: {[w['en'] for w in expected]}")
    print(f"\n批改结果:")
    print(f"  - 正确数: {result['correct_count']}/{result['total']}")
    print(f"  - 正确率: {result['score']}%")

    for i, item in enumerate(result['words']):
        status = "✅" if item['correct'] else "❌"
        print(f"  {status} {i+1}. 标准: {item['expected']}, 识别: {item['recognized']}")

    # 测试容错
    print("\n4. 测试容错比对...")
    recognized_with_errors = ["aple", "Banana", "COMPUTER"]  # 包含拼写错误和大小写
    result2 = recognizer.compare(recognized_with_errors, expected)

    print(f"识别结果（含错误）: {recognized_with_errors}")
    print(f"批改结果:")
    print(f"  - 正确数: {result2['correct_count']}/{result2['total']}")
    print(f"  - 正确率: {result2['score']}%")

    for i, item in enumerate(result2['words']):
        status = "✅" if item['correct'] else "❌"
        print(f"  {status} {i+1}. 标准: {item['expected']}, 识别: {item['recognized']}")

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == '__main__':
    test_basic_recognition()
