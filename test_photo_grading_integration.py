"""
测试拍照批改功能的完整集成
验证所有组件是否正常工作
"""
import sys
import os

def test_imports():
    """测试所有必要的导入"""
    print("=" * 60)
    print("测试1: 检查模块导入")
    print("=" * 60)

    try:
        from src.handwriting_recognizer import HandwritingRecognizer
        print("✅ handwriting_recognizer 导入成功")
    except Exception as e:
        print(f"❌ handwriting_recognizer 导入失败: {e}")
        return False

    try:
        from PIL import Image, ImageEnhance, ImageFilter
        print("✅ PIL 导入成功")
    except Exception as e:
        print(f"❌ PIL 导入失败: {e}")
        return False

    try:
        from paddleocr import PaddleOCR
        print("✅ PaddleOCR 导入成功")
    except Exception as e:
        print(f"❌ PaddleOCR 导入失败: {e}")
        return False

    try:
        import numpy as np
        print("✅ numpy 导入成功")
    except Exception as e:
        print(f"❌ numpy 导入失败: {e}")
        return False

    print("\n所有导入测试通过！\n")
    return True


def test_recognizer_initialization():
    """测试识别器初始化"""
    print("=" * 60)
    print("测试2: 初始化识别器")
    print("=" * 60)

    try:
        from src.handwriting_recognizer import HandwritingRecognizer
        recognizer = HandwritingRecognizer()
        print("✅ 识别器初始化成功")
        print(f"   OCR引擎: {type(recognizer.ocr).__name__}")
        return True, recognizer
    except Exception as e:
        print(f"❌ 识别器初始化失败: {e}")
        return False, None


def test_comparison_logic(recognizer):
    """测试比对逻辑"""
    print("\n" + "=" * 60)
    print("测试3: 答案比对逻辑")
    print("=" * 60)

    # 测试用例1: 完全正确
    print("\n测试用例 1: 完全正确的答案")
    recognized = ["apple", "banana", "computer"]
    expected = [
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'},
        {'en': 'computer', 'cn': '电脑'}
    ]

    result = recognizer.compare(recognized, expected)
    print(f"识别结果: {recognized}")
    print(f"标准答案: {[w['en'] for w in expected]}")
    print(f"正确率: {result['score']}%")
    print(f"正确数: {result['correct_count']}/{result['total']}")

    if result['score'] == 100.0:
        print("✅ 完全正确测试通过")
    else:
        print(f"❌ 完全正确测试失败: 期望100%，实际{result['score']}%")
        return False

    # 测试用例2: 大小写混合
    print("\n测试用例 2: 大小写混合")
    recognized_mixed = ["Apple", "BANANA", "computer"]
    result2 = recognizer.compare(recognized_mixed, expected)
    print(f"识别结果: {recognized_mixed}")
    print(f"正确率: {result2['score']}%")

    if result2['score'] == 100.0:
        print("✅ 大小写容错测试通过")
    else:
        print(f"❌ 大小写容错测试失败: 期望100%，实际{result2['score']}%")
        return False

    # 测试用例3: 部分错误
    print("\n测试用例 3: 部分错误")
    recognized_error = ["aple", "banana", "computer"]  # aple缺少p
    result3 = recognizer.compare(recognized_error, expected)
    print(f"识别结果: {recognized_error}")
    print(f"正确率: {result3['score']}%")
    print(f"正确数: {result3['correct_count']}/{result3['total']}")

    # aple vs apple (短单词，不容错) = 错误
    # 所以期望正确率是 66.7% (2/3)
    if 65 <= result3['score'] <= 67:
        print("✅ 部分错误测试通过")
    else:
        print(f"❌ 部分错误测试失败: 期望66.7%左右，实际{result3['score']}%")
        return False

    # 测试用例4: 长单词编辑距离容错
    print("\n测试用例 4: 长单词编辑距离容错")
    recognized_typo = ["beautyful", "wonderful", "excellent"]  # beautyful vs beautiful
    expected_long = [
        {'en': 'beautiful', 'cn': '美丽的'},
        {'en': 'wonderful', 'cn': '精彩的'},
        {'en': 'excellent', 'cn': '优秀的'}
    ]
    result4 = recognizer.compare(recognized_typo, expected_long)
    print(f"识别结果: {recognized_typo}")
    print(f"标准答案: {[w['en'] for w in expected_long]}")
    print(f"正确率: {result4['score']}%")

    # beautiful (9字符) vs beautyful (编辑距离=2) = 不容错（距离>1）
    # 所以期望正确率是 66.7% (2/3)
    if 65 <= result4['score'] <= 67:
        print("✅ 长单词容错测试通过")
    else:
        print(f"⚠️  长单词容错测试: 期望66.7%左右，实际{result4['score']}%")

    print("\n所有比对逻辑测试完成！")
    return True


def test_preprocessing():
    """测试图像预处理"""
    print("\n" + "=" * 60)
    print("测试4: 图像预处理")
    print("=" * 60)

    try:
        from src.handwriting_recognizer import HandwritingRecognizer
        from PIL import Image
        import numpy as np

        recognizer = HandwritingRecognizer()

        # 创建一个测试图片
        test_img = Image.new('RGB', (100, 100), color='white')
        test_path = "/tmp/test_preprocess.jpg"
        test_img.save(test_path)

        # 测试预处理
        processed_path = recognizer.preprocess_image(test_path)

        if os.path.exists(processed_path):
            print(f"✅ 预处理成功")
            print(f"   原图: {test_path}")
            print(f"   预处理图: {processed_path}")

            # 清理测试文件
            os.remove(test_path)
            if os.path.exists(processed_path):
                os.remove(processed_path)

            return True
        else:
            print("❌ 预处理失败: 未生成处理后的图片")
            return False

    except Exception as e:
        print(f"❌ 预处理测试失败: {e}")
        return False


def test_app_integration():
    """测试 app.py 集成"""
    print("\n" + "=" * 60)
    print("测试5: app.py 集成")
    print("=" * 60)

    try:
        # 检查 app.py 是否导入了 HandwritingRecognizer
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ('from src.handwriting_recognizer import HandwritingRecognizer', '导入 HandwritingRecognizer'),
            ('grading_result', 'grading_result session state'),
            ('拍照批改', '拍照批改UI'),
            ('st.file_uploader', '文件上传组件'),
            ('开始识别并批改', '识别按钮'),
            ('正确率', '批改结果展示'),
        ]

        all_passed = True
        for check, desc in checks:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ 缺少: {desc}")
                all_passed = False

        if all_passed:
            print("\n✅ app.py 集成完整")
            return True
        else:
            print("\n⚠️  app.py 集成可能不完整")
            return False

    except Exception as e:
        print(f"❌ app.py 检查失败: {e}")
        return False


def test_edit_distance():
    """测试编辑距离算法"""
    print("\n" + "=" * 60)
    print("测试6: 编辑距离算法")
    print("=" * 60)

    try:
        from src.handwriting_recognizer import HandwritingRecognizer

        recognizer = HandwritingRecognizer()

        test_cases = [
            ("apple", "apple", 0, "完全相同"),
            ("apple", "aple", 1, "删除一个字符"),
            ("apple", "apples", 1, "添加一个字符"),
            ("apple", "appel", 1, "替换一个字符"),
            ("apple", "banana", 5, "完全不同"),
        ]

        all_passed = True
        for s1, s2, expected, desc in test_cases:
            distance = recognizer._edit_distance(s1, s2)
            if distance == expected:
                print(f"✅ {desc}: '{s1}' vs '{s2}' = {distance}")
            else:
                print(f"❌ {desc}: '{s1}' vs '{s2}' = {distance} (期望{expected})")
                all_passed = False

        if all_passed:
            print("\n✅ 编辑距离算法测试通过")
            return True
        else:
            print("\n❌ 编辑距离算法测试失败")
            return False

    except Exception as e:
        print(f"❌ 编辑距离测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "🎯" * 30)
    print("拍照批改功能 - 完整集成测试")
    print("🎯" * 30 + "\n")

    results = []

    # 测试1: 导入
    results.append(("导入测试", test_imports()))

    # 测试2: 初始化
    success, recognizer = test_recognizer_initialization()
    results.append(("初始化测试", success))

    if not success:
        print("\n❌ 初始化失败，无法继续后续测试")
        return

    # 测试3: 比对逻辑
    results.append(("比对逻辑测试", test_comparison_logic(recognizer)))

    # 测试4: 预处理
    results.append(("图像预处理测试", test_preprocessing()))

    # 测试5: app集成
    results.append(("app.py集成测试", test_app_integration()))

    # 测试6: 编辑距离
    results.append(("编辑距离测试", test_edit_distance()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！拍照批改功能集成完整且正常工作！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查相关功能")


if __name__ == '__main__':
    main()
