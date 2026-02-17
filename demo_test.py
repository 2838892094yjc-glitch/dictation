"""
快速测试脚本 - 验证核心功能
"""
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

def create_test_image():
    """创建一个测试用的单词表图片"""
    # 创建白色背景
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
        small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 绘制标题
    draw.text((180, 20), "English Words", fill='black', font=font)
    draw.text((200, 60), "Unit 1", fill='black', font=small_font)
    
    # 绘制单词
    words = [
        ("apple", "苹果"),
        ("banana", "香蕉"),
        ("computer", "电脑"),
        ("hello", "你好"),
        ("book", "书"),
    ]
    
    y = 110
    for i, (en, cn) in enumerate(words, 1):
        draw.text((50, y), f"{i}. {en}", fill='black', font=small_font)
        draw.text((300, y), cn, fill='black', font=small_font)
        y += 50
    
    # 保存
    temp_path = "/tmp/test_word_list.png"
    img.save(temp_path)
    return temp_path

def test_ocr():
    """测试OCR功能"""
    print("=" * 50)
    print("测试OCR识别")
    print("=" * 50)
    
    # 创建测试图片
    img_path = create_test_image()
    print(f"✅ 创建测试图片: {img_path}")
    
    # 导入OCR引擎
    from src.ocr_engine import OCREngine
    
    print("⏳ 初始化OCR引擎...")
    ocr = OCREngine()
    
    print(f"⏳ 识别图片...")
    texts = ocr.recognize(img_path)
    
    print("\n📝 识别结果:")
    for text, conf in texts:
        print(f"   [{conf:.2f}] {text}")
    
    # 提取单词对
    pairs = ocr.extract_word_pairs(texts)
    print("\n📚 提取的单词对:")
    for p in pairs:
        print(f"   {p['english']} = {p['chinese']}")
    
    return pairs

def test_tts():
    """测试TTS功能"""
    print("\n" + "=" * 50)
    print("测试TTS语音")
    print("=" * 50)
    
    from src.tts_engine import speak_word
    
    print("⏳ 生成英文语音...")
    path1 = speak_word("apple", "苹果", "en_to_cn")
    print(f"✅ 生成: {path1}")
    
    print("⏳ 生成中文语音...")
    path2 = speak_word("apple", "苹果", "cn_to_en")
    print(f"✅ 生成: {path2}")
    
    # 清理
    os.remove(path1)
    os.remove(path2)
    print("✅ 临时文件已清理")

if __name__ == '__main__':
    try:
        # 测试OCR
        pairs = test_ocr()
        
        # 测试TTS
        test_tts()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        print("\n现在可以运行: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
