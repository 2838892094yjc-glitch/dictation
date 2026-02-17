"""
OCR API 客户端
用于调用本地/远程 OCR 服务
"""
import os
import requests
from typing import List, Optional

# API 地址配置
OCR_API_URL = os.environ.get("OCR_API_URL", "")


class OCRClient:
    """OCR API 客户端"""

    def __init__(self, api_url: str = None):
        self.api_url = api_url or OCR_API_URL
        self.available = bool(self.api_url)

    def is_available(self) -> bool:
        """检查 API 是否可用"""
        if not self.api_url:
            return False
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5)
            return resp.status_code == 200
        except:
            return False

    def recognize(self, image_data: bytes) -> List[dict]:
        """识别图片文字"""
        if not self.available:
            return []

        try:
            files = {'image': ('image.jpg', image_data, 'image/jpeg')}
            resp = requests.post(f"{self.api_url}/ocr", files=files, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('results', [])
        except Exception as e:
            print(f"OCR API 调用失败: {e}")
        return []

    def extract_words(self, image_data: bytes) -> List[dict]:
        """提取单词对"""
        if not self.available:
            return []

        try:
            files = {'image': ('image.jpg', image_data, 'image/jpeg')}
            resp = requests.post(f"{self.api_url}/extract-words", files=files, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('words', [])
        except Exception as e:
            print(f"OCR API 调用失败: {e}")
        return []


# 全局客户端
ocr_client = OCRClient()


def get_ocr_client() -> OCRClient:
    """获取 OCR 客户端"""
    return ocr_client
