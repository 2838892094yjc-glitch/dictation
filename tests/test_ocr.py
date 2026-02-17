"""
OCR引擎单元测试
"""
import pytest
from src.ocr_engine import OCREngine


class TestOCREngine:
    """OCR引擎测试类"""

    def test_init(self):
        """测试初始化"""
        engine = OCREngine()
        assert engine.ocr is not None

    def test_is_english_word(self):
        """测试英文单词判断"""
        engine = OCREngine()

        # 正常英文单词
        assert engine._is_english_word('apple') == True
        assert engine._is_english_word('beautiful') == True
        assert engine._is_english_word('Hello World') == True

        # 中文
        assert engine._is_english_word('苹果') == False
        assert engine._is_english_word('你好') == False

        # 混合（英文占比高）
        assert engine._is_english_word('apple123') == True

        # 空字符串
        assert engine._is_english_word('') == False
        assert engine._is_english_word('   ') == False

    def test_is_chinese_text(self):
        """测试中文文本判断"""
        engine = OCREngine()

        # 纯中文
        assert engine._is_chinese_text('苹果') == True
        assert engine._is_chinese_text('你好世界') == True

        # 英文
        assert engine._is_chinese_text('apple') == False
        assert engine._is_chinese_text('Hello') == False

        # 空字符串
        assert engine._is_chinese_text('') == False

    def test_is_title(self):
        """测试标��判断"""
        engine = OCREngine()

        # 标题
        assert engine._is_title('Word List') == True
        assert engine._is_title('Unit 1') == True
        assert engine._is_title('Starter Unit') == True
        assert engine._is_title('unit') == True

        # 非标题
        assert engine._is_title('apple') == False
        assert engine._is_title('苹果') == False

    def test_parse_inline_pair(self):
        """测试同行单词对解析"""
        engine = OCREngine()

        # 使用分隔符
        result = engine._parse_inline_pair('apple - 苹果')
        assert result == ('apple', '苹果')

        result = engine._parse_inline_pair('banana：香蕉')
        assert result == ('banana', '香蕉')

        # 空格分隔
        result = engine._parse_inline_pair('computer 电脑')
        assert result == ('computer', '电脑')

        # 带序号
        result = engine._parse_inline_pair('1. apple 苹果')
        assert result == ('apple', '苹果')

        # 无法解析
        result = engine._parse_inline_pair('apple')
        assert result is None

        result = engine._parse_inline_pair('苹果')
        assert result is None

    def test_extract_word_pairs(self, mock_ocr_result):
        """测试单词对提取"""
        engine = OCREngine()

        # 模拟识别结果
        pairs = engine.extract_word_pairs(mock_ocr_result)

        assert len(pairs) >= 2
        assert any(p['english'] == 'apple' for p in pairs)
        assert any(p['english'] == 'banana' for p in pairs)


class TestOCRIntegration:
    """OCR集成测试"""

    @pytest.mark.slow
    def test_recognize_real_image(self, sample_image):
        """测试真实图片识别（需要PaddleOCR模型）"""
        engine = OCREngine()

        # 识别图片
        texts = engine.recognize(sample_image)

        # 应该返回列表
        assert isinstance(texts, list)

        # 每个元素应该是(文字, 置信度)元组
        for text, conf in texts:
            assert isinstance(text, str)
            assert 0 <= conf <= 1
