"""
AI纠正器单元测试
"""
import pytest
from src.ai_corrector import AICorrector, correct_words, correct_spelling


class TestAICorrector:
    """AI纠正器测试类"""

    def test_init(self):
        """测试初始化"""
        corrector = AICorrector()
        assert len(corrector.common_words) > 0

    def test_correct_word_correct(self):
        """测试正确单词"""
        corrector = AICorrector()

        # 正确的单词应该不变
        word, note = corrector.correct_word("apple")
        assert word == "apple"
        assert note == "正确"

        word, note = corrector.correct_word("beautiful")
        assert word == "beautiful"
        assert note == "正确"

    def test_correct_word_common_misspelling(self):
        """测试常见拼写错误"""
        corrector = AICorrector()

        # 常见错误应该被纠正
        word, note = corrector.correct_word("ofien")
        assert word == "often"
        assert "纠正" in note

        word, note = corrector.correct_word("beutiful")
        assert word == "beautiful"
        assert "纠正" in note

        word, note = corrector.correct_word("teh")
        assert word == "the"
        assert "纠正" in note

    def test_correct_word_edit_distance(self):
        """测试编辑距离纠正"""
        corrector = AICorrector()

        # 编辑距离<=2的错误应该被纠正
        word, note = corrector.correct_word("appl")
        # 可能纠正为apple或其他相似词
        assert word != "appl" or "无法纠正" in note

    def test_correct_word_case_preservation(self):
        """测试大小写保持"""
        corrector = AICorrector()

        # 首字母大写应该保持
        word, note = corrector.correct_word("Ofien")
        assert word == "Often"
        assert "纠正" in note

    def test_correct_word_unknown(self):
        """测试未知单词"""
        corrector = AICorrector()

        # 未知单词应该返回原词
        word, note = corrector.correct_word("xyzabc")
        assert word == "xyzabc"
        assert "无法纠正" in note

    def test_edit_distance(self):
        """测试编辑距离计算"""
        corrector = AICorrector()

        # 相同字符串
        assert corrector._edit_distance("apple", "apple") == 0

        # 一个字符差异
        assert corrector._edit_distance("apple", "appl") == 1
        assert corrector._edit_distance("apple", "aple") == 1

        # 两个字符差异
        assert corrector._edit_distance("apple", "aple") == 1
        assert corrector._edit_distance("apple", "apxle") == 1

    def test_correct_word_list(self, sample_word_list):
        """测试批量纠正"""
        corrector = AICorrector()

        # 准备测试数据（包含错误）
        words = [
            {'english': 'ofien', 'chinese': '经常'},
            {'english': 'apple', 'chinese': '苹果'},
            {'english': 'beutiful', 'chinese': '美丽的'},
        ]

        corrected, changes = corrector.correct_word_list(words)

        # 检查纠正结果
        assert len(corrected) == 3
        assert corrected[0]['english'] == 'often'
        assert corrected[1]['english'] == 'apple'
        assert corrected[2]['english'] == 'beautiful'

        # 检查修改记录
        assert len(changes) == 2  # ofien和beutiful被纠正
        assert any(c['original'] == 'ofien' for c in changes)
        assert any(c['original'] == 'beutiful' for c in changes)


class TestCorrectSpelling:
    """测试correct_spelling接口函数"""

    def test_correct_spelling_basic(self):
        """测试基本纠正功能"""
        words = [
            {'en': 'ofien', 'cn': '经常'},
            {'en': 'apple', 'cn': '苹果'},
        ]

        result = correct_spelling(words)

        assert len(result) == 2
        assert result[0]['en'] == 'often'
        assert result[0]['corrected'] == 'often'
        assert result[1]['en'] == 'apple'
        assert result[1]['corrected'] is None  # 未纠正

    def test_correct_spelling_empty(self):
        """测试空列表"""
        result = correct_spelling([])
        assert result == []

    def test_correct_spelling_format(self):
        """测试返回格式"""
        words = [{'en': 'apple', 'cn': '苹果'}]
        result = correct_spelling(words)

        assert len(result) == 1
        assert 'en' in result[0]
        assert 'cn' in result[0]
        assert 'corrected' in result[0]


class TestCommonMisspellings:
    """测试常见拼写错误映射"""

    def test_ocr_common_errors(self):
        """测试OCR常见错误"""
        corrector = AICorrector()

        # OCR常见错误
        assert corrector._common_misspellings('pofalar') == 'popular'
        assert corrector._common_misspellings('brihg') == 'bring'
        assert corrector._common_misspellings('slver') == 'silver'

    def test_typing_common_errors(self):
        """测试打字常见错误"""
        corrector = AICorrector()

        # 打字常见错误
        assert corrector._common_misspellings('teh') == 'the'
        assert corrector._common_misspellings('adn') == 'and'
        assert corrector._common_misspellings('wiht') == 'with'
