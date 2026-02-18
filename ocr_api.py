"""
本地 OCR API 服务
运行后暴露给云端调用
"""
from flask import Flask, request, jsonify
from PIL import Image
import io
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# 全局 OCR 引擎
ocr_engine = None

def get_ocr_engine():
    """延迟初始化 OCR 引擎"""
    global ocr_engine
    if ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            print("初始化 PaddleOCR...")
            ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch')
            print("PaddleOCR 初始化完成!")
        except Exception as e:
            print(f"OCR 初始化失败: {e}")
            return None
    return ocr_engine

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "ocr_available": get_ocr_engine() is not None})

@app.route('/ocr', methods=['POST'])
def ocr():
    """OCR 识别接口"""
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    try:
        # 获取图片
        file = request.files['image']
        image = Image.open(file.stream)

        # 转换为 numpy 数组
        import numpy as np
        img_array = np.array(image)

        # OCR 识别
        engine = get_ocr_engine()
        if engine is None:
            return jsonify({"error": "OCR engine not available"}), 500

        result = engine.ocr(img_array, cls=True)

        # 解析结果
        texts = []
        if result and result[0]:
            for line in result[0]:
                box = line[0]  # 坐标
                text = line[1][0]  # 文字
                score = line[1][1]  # 置信度
                texts.append({
                    "text": text,
                    "score": float(score),
                    "box": box.tolist() if hasattr(box, 'tolist') else list(box)
                })

        return jsonify({
            "success": True,
            "count": len(texts),
            "results": texts
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/extract-words', methods=['POST'])
def extract_words():
    """提取单词对接口"""
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    try:
        from src.ocr_engine import extract_words_from_image
        import tempfile

        # 保存上传的图片
        file = request.files['image']
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # 提取单词
        words = extract_words_from_image(tmp_path)

        # 清理
        os.unlink(tmp_path)

        return jsonify({
            "success": True,
            "words": words
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("本地 OCR API 服务")
    print("=" * 50)
    print("启动后用 ngrok 暴露:")
    print("  ngrok http 5000")
    print("")
    print("访问: http://localhost:5000/health")
    print("=" * 50)

    # 预热 OCR
    get_ocr_engine()

    app.run(host='0.0.0.0', port=5001, debug=False)
