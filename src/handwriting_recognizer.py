"""
手写识别和批改模块 - 使用PaddleOCR识别手写答案并批改
"""
import re
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# PaddleOCR 仅本地使用
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False


class HandwritingRecognizer:
    """手写识别和批改器"""

    def __init__(self, lang='ch'):
        """
        初始化OCR引擎

        Args:
            lang: 语言模型，'ch'(中英文混合) 或 'en'(仅英文)
        """
        if not PADDLEOCR_AVAILABLE:
            print("⚠️ PaddleOCR 不可用，手写识别功能仅限本地使用")
            self.ocr = None
            return

        print("正在初始化手写识别引擎...")
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # 方向分类器
            lang=lang            # 'ch'支持中英文混合，'en'仅英文
        )
        print("手写识别引擎初始化完成！")

    def preprocess_image(self, image_path: str) -> str:
        """
        图像预处理 - 灰度化、去噪、增强对比度

        Args:
            image_path: 原始图片路径

        Returns:
            预处理后的图片路径
        """
        try:
            # 打开图片
            img = Image.open(image_path)

            # 转换为RGB模式（如果是RGBA等）
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 灰度化
            img = img.convert('L')

            # 增强对比度
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            # 增强锐度
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.5)

            # 去噪
            img = img.filter(ImageFilter.MedianFilter(size=3))

            # 保存预处理后的图片
            processed_path = image_path.replace('.', '_processed.')
            img.save(processed_path)

            return processed_path

        except Exception as e:
            print(f"图像预处理失败: {e}")
            return image_path  # 返回原图

    def recognize(self, image_path: str, preprocess: bool = True, keep_chinese: bool = False) -> List[str]:
        """
        识别手写文字

        Args:
            image_path: 图片路径
            preprocess: 是否进行预处理
            keep_chinese: 是否保留中文字符

        Returns:
            识别出的文字列表
        """
        if self.ocr is None:
            return []

        # 预处理
        if preprocess:
            processed_path = self.preprocess_image(image_path)
        else:
            processed_path = image_path

        # OCR识别
        result = self.ocr.ocr(processed_path)

        words = []
        if result and len(result) > 0:
            # 新版本的PaddleOCR返回OCRResult对象列表
            page = result[0]

            # 转换为字典获取数据
            data = dict(page)
            rec_texts = data.get('rec_texts', [])
            rec_scores = data.get('rec_scores', [])

            for text, score in zip(rec_texts, rec_scores):
                # 只保留置信度较高的结果
                if score > 0.5:
                    # 清理识别结果
                    cleaned = self._clean_recognized_text(text, keep_chinese=keep_chinese)
                    if cleaned:
                        words.append(cleaned)

        return words

    def _clean_recognized_text(self, text: str, keep_chinese: bool = False) -> str:
        """
        清理识别的文字
        - 移除序号
        - 移除特殊字符

        Args:
            text: 原始文本
            keep_chinese: 是否保留中文字符
        """
        # 移除序号前缀（1. 2. 等）
        text = re.sub(r'^[\(\[（【]?\d+[\)\]）】]?[\.、．\s]*', '', text)

        if keep_chinese:
            # 保留字母和中文
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', '', text)
        else:
            # 只保留字母
            text = re.sub(r'[^a-zA-Z\s]', '', text)

        # trim 空格
        text = text.strip()

        return text

    def compare(self, recognized_words: List[str], expected_words: List[Dict], mode: str = 'en_to_cn') -> Dict:
        """
        比对识别结果和标准答案

        Args:
            recognized_words: 识别出的单词列表
            expected_words: 标准答案列表 [{'en': '...', 'cn': '...', 'expected': '...'}, ...]
            mode: 听写模式 'en_to_cn' | 'cn_to_en' | 'spell'

        Returns:
            批改结果 {
                'words': [{'expected': '...', 'recognized': '...', 'correct': bool}, ...],
                'score': float,  # 正确率百分比
                'total': int,
                'correct_count': int
            }
        """
        results = []
        correct_count = 0

        # 遍历标准答案
        for i, expected_word in enumerate(expected_words):
            # 根据模式获取期望答案
            if 'expected' in expected_word:
                expected = expected_word['expected'].strip()
            else:
                # 兼容旧格式
                if mode == 'en_to_cn':
                    expected = expected_word.get('cn', '').strip()
                else:
                    expected = expected_word.get('en', '').strip()

            # 对应位置的识别结果
            recognized = ''
            if i < len(recognized_words):
                recognized = recognized_words[i]

            # 比对（根据是否为中文使用不同策略）
            is_correct = self._is_match_multilang(recognized, expected, is_chinese=(mode == 'en_to_cn'))

            if is_correct:
                correct_count += 1

            results.append({
                'expected': expected,
                'recognized': recognized,
                'correct': is_correct,
                'chinese': expected_word.get('cn', '')
            })

        # 计算正确率
        total = len(expected_words)
        score = (correct_count / total * 100) if total > 0 else 0

        return {
            'words': results,
            'score': round(score, 1),
            'total': total,
            'correct_count': correct_count
        }

    def _is_match(self, text1: str, text2: str) -> bool:
        """
        比对两个英文单词是否匹配
        - 忽略大小写
        - trim 空格
        - 容忍少量拼写错误（编辑距离<=1）
        """
        if not text1 or not text2:
            return False

        # 标准化
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        # 完全匹配
        if text1 == text2:
            return True

        # 计算编辑距离，容忍1个字符的差异
        distance = self._edit_distance(text1, text2)

        # 如果单词长度>5，容忍1个字符差异
        # 如果单词长度<=5，必须完全匹配
        if len(text2) > 5 and distance <= 1:
            return True

        return False

    def _is_match_multilang(self, text1: str, text2: str, is_chinese: bool = False) -> bool:
        """
        比对两个文本是否匹配（支持中英文）

        Args:
            text1: 识别的文本
            text2: 标准答案
            is_chinese: 是否为中文比对
        """
        if not text1 or not text2:
            return False

        # 标准化
        text1 = text1.strip()
        text2 = text2.strip()

        if is_chinese:
            # 中文比对：去除空格后完全匹配
            text1 = text1.replace(' ', '')
            text2 = text2.replace(' ', '')
            return text1 == text2
        else:
            # 英文比对：使用原有的宽松匹配策略
            return self._is_match(text1, text2)

    def _edit_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离（Levenshtein距离）"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def extract_words_from_lines(self, lines: List[str]) -> List[str]:
        """
        从识别的文本行中提取单词
        - 处理每行可能包含多个单词的情况
        - 清理和标准化
        """
        words = []

        for line in lines:
            # 按空格分割
            parts = line.split()
            for part in parts:
                cleaned = self._clean_recognized_text(part)
                if cleaned and len(cleaned) >= 2:  # 至少2个字母
                    words.append(cleaned)

        return words


def grade_handwriting_answer(image_path: str, expected_words: List[Dict]) -> Dict:
    """
    批改手写答案（便捷函数）

    Args:
        image_path: 手写答案图片路径
        expected_words: 标准答案列表 [{'en': '...', 'cn': '...'}, ...]

    Returns:
        批改结果
    """
    recognizer = HandwritingRecognizer()

    # 识别文字
    recognized_words = recognizer.recognize(image_path)

    # 比对答案
    result = recognizer.compare(recognized_words, expected_words)

    return result


if __name__ == '__main__':
    # 测试
    import sys

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"识别图片: {image_path}")

        recognizer = HandwritingRecognizer()
        words = recognizer.recognize(image_path)

        print(f"\n识别结果 ({len(words)} 个单词):")
        for i, word in enumerate(words):
            print(f"  {i+1}. {word}")

        # 测试比对
        test_expected = [
            {'en': 'apple', 'cn': '苹果'},
            {'en': 'banana', 'cn': '香蕉'},
            {'en': 'computer', 'cn': '电脑'}
        ]

        result = recognizer.compare(words[:3], test_expected)
        print(f"\n批改结果:")
        print(f"  正确率: {result['score']}%")
        print(f"  正确数: {result['correct_count']}/{result['total']}")

        for item in result['words']:
            status = "✅" if item['correct'] else "❌"
            print(f"  {status} 标准答案: {item['expected']}, 识别结果: {item['recognized']}")
