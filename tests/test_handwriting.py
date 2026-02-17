"""
手写识别器单元测试
"""
import pytest
from src.handwriting_recognizer import HandwritingRecognizer


class TestHandwritingRecognizer:
    """手写识别器测试类"""

    def test_init(self):
        """测试初始化"""
        recognizer = HandwritingRecognizer()
        assert recognizer.ocr is not None

    def test_clean_recognized_text(self):
        """测试文本清理"""
        recognizer = HandwritingRecognizer()

        # 移除序号
        assert recognizer._clean_recognized_text('1. apple') == 'apple'
        assert recognizer._clean_recognized_text('(2) banana') == 'banana'

        # 移除特殊字符
        assert recognizer._clean_recognized_text('app!le@') == 'apple'

        # 保留中文
        result = recognizer._clean_recognized_text('苹果123', keep_chinese=True)
        assert result == '苹果'

        # 不保留中文
        result = recognizer._clean_recognized_text('苹果abc', keep_chinese=False)
        assert result == 'abc'

    def test_is_match(self):
        """测试单词匹配"""
        recognizer = HandwritingRecognizer()

        # 完全匹配
        assert recognizer._is_match('apple', 'apple') == True

        # 大小写不敏感
        assert recognizer._is_match('Apple', 'apple') == True
        assert recognizer._is_match('APPLE', 'apple') == True

        # 空格trim
        assert recognizer._is_match(' apple ', 'apple') == True

        # 编辑距离容忍（长单词）
        assert recognizer._is_match('beautifu', 'beautiful') == True

        # 短单词不容忍错误
        assert recognizer._is_match('appl', 'apple') == False

        # 完全不同
        assert recognizer._is_match('apple', 'banana') == False

    def test_is_match_multilang(self):
        """测试多语言匹配"""
        recognizer = HandwritingRecognizer()

        # 英文匹配（宽松）
        assert recognizer._is_match_multilang('apple', 'apple', is_chinese=False) == True
        assert recognizer._is_match_multilang('Apple', 'apple', is_chinese=False) == True

        # 中文匹配（严格）
        assert recognizer._is_match_multilang('苹果', '苹果', is_chinese=True) == True
        assert recognizer._is_match_multilang('苹 果', '苹果', is_chinese=True) == True

        # 中文不匹配
        assert recognizer._is_match_multilang('苹果', '香蕉', is_chinese=True) == False

    def test_edit_distance(self):
        """测试编辑距离"""
        recognizer = HandwritingRecognizer()

        # 相同
        assert recognizer._edit_distance('apple', 'apple') == 0

        # 插入
        assert recognizer._edit_distance('apple', 'apples') == 1

        # 删除
        assert recognizer._edit_distance('apple', 'aple') == 1

        # 替换
        assert recognizer._edit_distance('apple', 'apxle') == 1

        # 多个操作
        assert recognizer._edit_distance('apple', 'banana') > 3

    def test_compare_en_to_cn(self):
        """测试英译中批改"""
        recognizer = HandwritingRecognizer()

        # 准备数据
        recognized = ['苹果', '香蕉', '电脑']
        expected = [
            {'en': 'apple', 'cn': '苹果'},
            {'en': 'banana', 'cn': '香蕉'},
            {'en': 'computer', 'cn': '电脑'},
        ]

        result = recognizer.compare(recognized, expected, mode='en_to_cn')

        # 检查结果
        assert result['total'] == 3
        assert result['correct_count'] == 3
        assert result['score'] == 100.0
        assert len(result['words']) == 3

    def test_compare_cn_to_en(self):
        """测试中译英批改"""
        recognizer = HandwritingRecognizer()

        # 准备数据
        recognized = ['apple', 'banana', 'computer']
        expected = [
            {'en': 'apple', 'cn': '苹果'},
            {'en': 'banana', 'cn': '香蕉'},
            {'en': 'computer', 'cn': '电脑'},
        ]

        result = recognizer.compare(recognized, expected, mode='cn_to_en')

        # 检查结果
        assert result['total'] == 3
        assert result['correct_count'] == 3
        assert result['score'] == 100.0

    def test_compare_partial_correct(self):
        """测试部分正确"""
        recognizer = HandwritingRecognizer()

        # 准备数据（有错误）
        recognized = ['apple', 'banan', 'computer']  # banan拼写错误
        expected = [
            {'en': 'apple', 'cn': '苹果'},
            {'en': 'banana', 'cn': '香蕉'},
            {'en': 'computer', 'cn': '电脑'},
        ]

        result = recognizer.compare(recognized, expected, mode='cn_to_en')

        # 检查结果
        assert result['total'] == 3
        assert result['correct_count'] == 2  # apple和computer正确
        assert result['score'] == pytest.approx(66.7, rel=0.1)

    def test_compare_empty(self):
        """测试空列表"""
        recognizer = HandwritingRecognizer()

        result = recognizer.compare([], [], mode='en_to_cn')

        assert result['total'] == 0
        assert result['correct_count'] == 0
        assert result['score'] == 0

    def test_extract_words_from_lines(self):
        """测试从文本行提取单词"""
        recognizer = HandwritingRecognizer()

        lines = [
            '1. apple banana',
            '2. computer',
            'phone',
        ]

        words = recognizer.extract_words_from_lines(lines)

        assert 'apple' in words
        assert 'banana' in words
        assert 'computer' in words
        assert 'phone' in words

    @pytest.mark.slow
    def test_preprocess_image(self, sample_image):
        """测试图像预处理"""
        recognizer = HandwritingRecognizer()

        processed_path = recognizer.preprocess_image(sample_image)

        # 应该生成新文件
        assert processed_path != sample_image
        assert '_processed' in processed_path
        # 注意：由于是空白图片，可能不会生成文件，这里只测试函数不报错


class TestHandwritingIntegration:
    """手写识别集成测试"""

    @pytest.mark.slow
    def test_recognize_and_compare(self, sample_image):
        """测试完整流程"""
        recognizer = HandwritingRecognizer()

        # 识别
        words = recognizer.recognize(sample_image, preprocess=True)

        # 应该返回列表
        assert isinstance(words, list)

        # 批改（即使识别结果为空也应该正常工作）
        expected = [
            {'en': 'apple', 'cn': '苹果'},
            {'en': 'banana', 'cn': '香蕉'},
        ]

        result = recognizer.compare(words, expected, mode='en_to_cn')

        assert 'score' in result
        assert 'total' in result
        assert 'correct_count' in result
        assert 'words' in result
