"""
Pytest配置文件 - 共享fixtures
"""
import pytest
import os
import sys
import tempfile
from PIL import Image
import numpy as np

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_word_list():
    """示例单词列表"""
    return [
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'},
        {'en': 'computer', 'cn': '电脑'},
        {'en': 'beautiful', 'cn': '美丽的'},
        {'en': 'often', 'cn': '经常'},
    ]


@pytest.fixture
def sample_word_list_extended():
    """扩展的示例单词列表"""
    return [
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'},
        {'en': 'computer', 'cn': '电脑'},
        {'en': 'beautiful', 'cn': '美丽的'},
        {'en': 'often', 'cn': '经常'},
        {'en': 'student', 'cn': '学生'},
        {'en': 'teacher', 'cn': '老师'},
        {'en': 'school', 'cn': '学校'},
        {'en': 'friend', 'cn': '朋友'},
        {'en': 'family', 'cn': '家庭'},
    ]


@pytest.fixture
def sample_image(temp_dir):
    """创建示例图片"""
    img = Image.new('RGB', (800, 600), color='white')
    img_path = os.path.join(temp_dir, 'test_image.jpg')
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_image_with_text(temp_dir):
    """创建带文字的示例图片（用于OCR测试）"""
    from PIL import ImageDraw, ImageFont

    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        font = ImageFont.load_default()

    # 绘制文字
    draw.text((50, 50), "apple", fill='black', font=font)
    draw.text((50, 100), "banana", fill='black', font=font)
    draw.text((50, 150), "computer", fill='black', font=font)

    img_path = os.path.join(temp_dir, 'test_image_with_text.jpg')
    img.save(img_path)
    return img_path


@pytest.fixture
def mock_ocr_result():
    """模拟OCR识别结果"""
    return [
        ('apple', 0.95),
        ('苹果', 0.92),
        ('banana', 0.88),
        ('香蕉', 0.90),
    ]


@pytest.fixture
def mock_ocr_result_with_errors():
    """模拟包含错误的OCR识别结果"""
    return [
        ('ofien', 0.85),  # often的错误识别
        ('经常', 0.92),
        ('beutiful', 0.80),  # beautiful的错误识别
        ('美丽的', 0.90),
        ('apple', 0.95),
        ('苹果', 0.92),
    ]


@pytest.fixture
def sample_history_records():
    """示例历史记录"""
    return [
        {
            'mode': 'en_to_cn',
            'vocabulary_name': '测试词库1',
            'total_words': 10,
            'correct_count': 8,
            'duration_seconds': 120,
            'wrong_words': [
                {'en': 'apple', 'cn': '苹果', 'user_answer': '苹'},
                {'en': 'banana', 'cn': '香蕉', 'user_answer': '香'}
            ]
        },
        {
            'mode': 'cn_to_en',
            'vocabulary_name': '测试词库2',
            'total_words': 5,
            'correct_count': 5,
            'duration_seconds': 60,
            'wrong_words': []
        },
    ]


@pytest.fixture
def sample_wrong_answers():
    """示例错题"""
    return [
        {'en': 'apple', 'cn': '苹果', 'user_answer': '苹'},
        {'en': 'banana', 'cn': '香蕉', 'user_answer': '香'},
        {'en': 'computer', 'cn': '电脑', 'user_answer': '电'},
    ]


# 配置pytest标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "slow: 标记为慢速测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "unit: 单元测试")
