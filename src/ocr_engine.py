"""
OCR引擎模块 - 使用PaddleOCR识别图片中的文字
"""
import re
from typing import List, Tuple, Optional
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np


class OCREngine:
    """OCR识别引擎"""
    
    def __init__(self):
        # 初始化PaddleOCR，支持中英文
        print("正在初始化OCR引擎，首次加载需要下载模型...")
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # 方向分类器
            lang='ch'            # 中文模型（包含英文）
        )
        print("OCR引擎初始化完成！")
    
    def recognize(self, image_path: str) -> List[Tuple[str, float]]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            识别结果列表 [(文字, 置信度), ...]
        """
        result = self.ocr.ocr(image_path)
        
        texts = []
        if result and len(result) > 0:
            # 新版本的PaddleOCR返回OCRResult对象列表
            page = result[0]
            
            # 转换为字典获取数据
            data = dict(page)
            rec_texts = data.get('rec_texts', [])
            rec_scores = data.get('rec_scores', [])
            
            for text, score in zip(rec_texts, rec_scores):
                texts.append((text, float(score)))
        
        return texts
    
    def extract_word_pairs(self, texts: List[Tuple[str, float]]) -> List[dict]:
        """
        从识别结果中提取单词对（英文+中文）
        
        支持格式：
        - 同行: apple 苹果
        - 跨行: apple\n苹果
        """
        pairs = []
        
        # 合并所有识别结果
        all_texts = [t[0].strip() for t in texts]
        
        print(f"DEBUG - 共 {len(all_texts)} 行识别结果")
        
        i = 0
        while i < len(all_texts):
            line = all_texts[i]
            
            # 跳过空行和标题
            if not line or self._is_title(line):
                i += 1
                continue
            
            # 策略1: 检查当前行是否包含英文和中文
            pair = self._parse_inline_pair(line)
            if pair:
                pairs.append({
                    'english': pair[0],
                    'chinese': pair[1],
                    'raw': line,
                    'confidence': 1.0
                })
                i += 1
                continue
            
            # 策略2: 检查当前行是英文，下一行是中文
            if i + 1 < len(all_texts):
                next_line = all_texts[i + 1]
                
                if self._is_english_word(line) and self._is_chinese_text(next_line):
                    pairs.append({
                        'english': line,
                        'chinese': next_line,
                        'raw': f"{line} {next_line}",
                        'confidence': 1.0
                    })
                    i += 2
                    continue
                
                # 当前行是中文，前一个是英文（已经配对过了，跳过）
                if self._is_chinese_text(line) and i > 0 and self._is_english_word(all_texts[i-1]):
                    i += 1
                    continue
            
            # 策略3: 只有英文
            if self._is_english_word(line):
                pairs.append({
                    'english': line,
                    'chinese': '',
                    'raw': line,
                    'confidence': 1.0
                })
            
            i += 1
        
        return pairs
    
    def _is_title(self, text: str) -> bool:
        """判断是否为标题类文字"""
        titles = ['word list', 'starter unit', 'unit', 'starter unlt']
        text_lower = text.lower().strip()
        
        for title in titles:
            if title in text_lower:
                return True
        
        # 匹配 "unit 1", "unit 2" 等
        if re.match(r'^unit\s*\d*$', text_lower):
            return True
        
        return False
    
    def _parse_inline_pair(self, text: str) -> Optional[Tuple[str, str]]:
        """
        解析同行单词对
        
        Returns:
            (英文, 中文) 或 None
        """
        # 移除序号前缀
        text = re.sub(r'^[\(\[（【]?\d+[\)\]）】]?[\.、．\s]*', '', text)
        text = re.sub(r'^[①②③④⑤⑥⑦⑧⑨⑩]\s*', '', text)
        text = text.strip()
        
        if not text:
            return None
        
        # 尝试多种分隔符
        separators = ['——', '--', '－', '-', '：', ':', '·', '•', '|', '/']
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep, 1)
                if len(parts) == 2:
                    left, right = parts[0].strip(), parts[1].strip()
                    
                    left_is_en = self._is_english_word(left)
                    right_is_en = self._is_english_word(right)
                    
                    if left_is_en and not right_is_en:
                        return (left, right)
                    elif right_is_en and not left_is_en:
                        return (right, left)
        
        # 按空格分割尝试
        parts = text.split()
        if len(parts) >= 2:
            english_parts = []
            chinese_parts = []
            
            for part in parts:
                if self._is_english_word(part):
                    if chinese_parts:  # 已经有中文了，停止
                        break
                    english_parts.append(part)
                elif self._is_chinese_text(part):
                    chinese_parts.append(part)
            
            if english_parts and chinese_parts:
                return (' '.join(english_parts), ''.join(chinese_parts))
        
        return None
    
    def _is_english_word(self, text: str) -> bool:
        """判断是否为英文单词"""
        if not text:
            return False
        
        text = text.strip()
        cleaned = re.sub(r'[^\w\s\-]', '', text).strip()
        if not cleaned:
            return False
        
        english_chars = len(re.findall(r'[a-zA-Z]', cleaned))
        total_chars = len(re.sub(r'\s', '', cleaned))
        
        return total_chars > 0 and english_chars / total_chars >= 0.5 and english_chars > 0
    
    def _is_chinese_text(self, text: str) -> bool:
        """判断是否为中文文本"""
        if not text:
            return False
        
        text = text.strip()
        
        # 包含中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # 至少有1个中文字符，且英文比例低
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.sub(r'\s', '', text))
        
        if chinese_chars > 0:
            return True
        
        # 如果没有中文，但有大量标点符号，也可能是中文注释
        if total_chars > 0 and english_chars / total_chars < 0.3:
            return True
        
        return False


def extract_words_from_image(image_path: str) -> List[dict]:
    """
    从图片中提取单词对（英文+中文）

    Args:
        image_path: 图片路径

    Returns:
        单词列表 [{en: str, cn: str}, ...]
    """
    engine = OCREngine()
    texts = engine.recognize(image_path)
    pairs = engine.extract_word_pairs(texts)

    # 转换为 app.py 期望的格式
    result = []
    for pair in pairs:
        result.append({
            'en': pair.get('english', ''),
            'cn': pair.get('chinese', '')
        })
    return result


def test_ocr():
    """测试OCR功能"""
    engine = OCREngine()
    
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"识别图片: {image_path}")
        
        texts = engine.recognize(image_path)
        print(f"\n原始识别结果 ({len(texts)} 行):")
        for i, (text, conf) in enumerate(texts[:50]):
            print(f"  {i+1}. [{conf:.2f}] {text!r}")
        
        pairs = engine.extract_word_pairs(texts)
        print(f"\n提取的单词对 ({len(pairs)} 个):")
        for pair in pairs[:30]:
            cn = pair['chinese'] or '(无)'
            print(f"  {pair['english']} = {cn}")


if __name__ == '__main__':
    test_ocr()
