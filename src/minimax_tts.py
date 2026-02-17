"""
MiniMax TTS 引擎 - 高质量云端语音合成
文档: https://platform.minimax.io/docs/api-reference/speech-t2a-http
"""
import os
import requests
import tempfile
from typing import Optional


class MiniMaxTTSEngine:
    """MiniMax 语音合成引擎"""
    
    # API 配置 - 使用正确的 minimaxi.com 域名
    API_URL = "https://api.minimaxi.com/v1/t2a_v2"
    API_URL_FAST = "https://api.minimaxi.com/v1/t2a_v2"  # 统一使用正确域名
    
    # 可用模型 - 使用官方文档的正确名称
    MODELS = {
        "hd": "speech-02-hd",        # 高质量
        "turbo": "speech-02-turbo",  # 更快更便宜
    }
    
    # 英文音色列表 (实测可用的音色)
    ENGLISH_VOICES = {
        "male_qn_qingse": "male-qn-qingse",       # 男声-青年-轻熟
        "female_shaonv": "female-shaonv",          # 女声-少女
        "male_qn_jingying": "male-qn-jingying",   # 男声-青年-精英
        "female_yujie": "female-yujie",            # 女声-御姐
        "male_qn_badao": "male-qn-badao",          # 男声-青年-霸道
    }

    # 中文音色 (实测可用的音色)
    CHINESE_VOICES = {
        "male_qn_qingse": "male-qn-qingse",       # 男声-青年-轻熟
        "female_shaonv": "female-shaonv",          # 女声-少女
        "male_qn_jingying": "male-qn-jingying",   # 男声-青年-精英
        "female_yujie": "female-yujie",            # 女声-御姐
        "male_qn_badao": "male-qn-badao",         # 男声-青年-霸道
    }
    
    # 内置 API Key（项目使用）- 优先从环境变量读取
    DEFAULT_API_KEY = os.getenv("MINIMAX_API_KEY", "sk-api-vgkUWazo08PYHpD0TDyKkLYxifoJYn9woKcDDzcHvToQDxSOp454WsBs9UoGca4rS-1QrdjMqVA5bWNVlN6pZ-4Boyv-MxcNC6Ha_y5KrPEqp5_WDEX4fFo")
    
    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None):
        """
        初始化 MiniMax TTS 引擎

        Args:
            api_key: MiniMax API Key（可选，默认从环境变量 MINIMAX_API_KEY 读取）
            group_id: MiniMax Group ID (部分账号需要)
        """
        # 优先使用传入的 api_key，其次从环境变量读取，最后使用默认值
        if api_key is None:
            api_key = os.getenv("MINIMAX_API_KEY", self.DEFAULT_API_KEY)
        self.api_key = api_key
        self.group_id = group_id or os.getenv("MINIMAX_GROUP_ID", "")
        self.model = self.MODELS["turbo"]  # 固定使用 turbo，性价比高
        self.voice = self.ENGLISH_VOICES["male_qn_qingse"]  # 默认使用第一个可用音色
        self.speed = 1.0
        self.vol = 1.0
        self.pitch = 0
        self.use_fast_endpoint = True  # 使用更快响应的 endpoint
        
    def set_api_key(self, api_key: str):
        """设置 API Key"""
        self.api_key = api_key
        
    def set_voice(self, voice_type: str = "expressive_narrator", is_english: bool = True):
        """
        设置音色
        
        Args:
            voice_type: 音色名称
            is_english: 是否是英文音色
        """
        if is_english:
            if voice_type in self.ENGLISH_VOICES:
                self.voice = self.ENGLISH_VOICES[voice_type]
            else:
                self.voice = voice_type  # 支持直接传入 voice_id
        else:
            if voice_type in self.CHINESE_VOICES:
                self.voice = self.CHINESE_VOICES[voice_type]
            else:
                self.voice = voice_type
    
    def set_model(self, model_name: str = "turbo"):
        """
        设置模型
        
        Args:
            model_name: hd/turbo/02_hd/02_turbo
        """
        if model_name in self.MODELS:
            self.model = self.MODELS[model_name]
    
    def set_rate(self, speed: float = 1.0):
        """
        设置语速
        
        Args:
            speed: 0.5 - 2.0，1.0 为正常
        """
        self.speed = max(0.5, min(2.0, speed))
    
    def speak(self, text: str, save_path: Optional[str] = None) -> str:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            save_path: 保存路径，None 则创建临时文件
            
        Returns:
            音频文件路径
        """
        if not self.api_key:
            raise ValueError("MiniMax API Key 未设置")
        
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 构建请求
        url = self.API_URL_FAST if self.use_fast_endpoint else self.API_URL
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Group ID (如果配置了)
        if self.group_id:
            headers["Group-Id"] = self.group_id
        
        payload = {
            "model": self.model,
            "text": text.strip(),
            "stream": False,
            "output_format": "hex",
            "language_boost": "auto",
            "voice_setting": {
                "voice_id": self.voice,
                "speed": self.speed,
                "vol": self.vol,
                "pitch": self.pitch
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1
            }
        }
        
        # 发送请求
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60  # MiniMax 可能需要一些时间
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise RuntimeError("MiniMax API 请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"MiniMax API 请求失败: {e}")
        
        # 解析响应
        result = response.json()
        
        # 检查响应状态
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            error_msg = base_resp.get("status_msg", "未知错误")
            raise RuntimeError(f"MiniMax 合成失败: {error_msg}")
        
        # 获取音频数据
        data = result.get("data", {})
        if not data or "audio" not in data:
            raise RuntimeError("MiniMax 返回数据格式错误")
        
        # hex 解码
        import binascii
        audio_hex = data["audio"]
        audio_bytes = binascii.unhexlify(audio_hex)
        
        # 保存文件
        if save_path is None:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                save_path = f.name
        
        with open(save_path, "wb") as f:
            f.write(audio_bytes)
        
        return save_path
    
    def get_audio_bytes(self, text: str) -> bytes:
        """获取音频二进制数据"""
        path = self.speak(text)
        with open(path, "rb") as f:
            data = f.read()
        try:
            os.remove(path)
        except:
            pass
        return data
    
    @classmethod
    def get_voice_list(cls, is_english: bool = True) -> dict:
        """获取可用音色列表"""
        if is_english:
            return cls.ENGLISH_VOICES.copy()
        return cls.CHINESE_VOICES.copy()


# 全局实例（延迟初始化）
_minimax_engine: Optional[MiniMaxTTSEngine] = None


def get_minimax_engine(api_key: Optional[str] = None) -> MiniMaxTTSEngine:
    """获取 MiniMax TTS 引擎实例"""
    global _minimax_engine
    if _minimax_engine is None:
        _minimax_engine = MiniMaxTTSEngine(api_key=api_key)
    elif api_key:
        _minimax_engine.set_api_key(api_key)
    return _minimax_engine


if __name__ == "__main__":
    # 测试
    import os
    
    api_key = os.getenv("MINIMAX_API_KEY", "")
    if not api_key:
        print("请先设置 MINIMAX_API_KEY 环境变量")
        exit(1)
    
    engine = MiniMaxTTSEngine(api_key=api_key)
    
    # 测试英文
    print("测试英文...")
    engine.set_voice("expressive_narrator", is_english=True)
    path = engine.speak("Hello, this is a test of MiniMax TTS.")
    print(f"英文音频已生成: {path}")
    
    # 测试不同音色
    print("\n测试不同音色...")
    for voice_name in ["calm_reader", "energetic_presenter"]:
        engine.set_voice(voice_name, is_english=True)
        path = engine.speak(f"This is the {voice_name} voice.", save_path=f"/tmp/test_{voice_name}.mp3")
        print(f"  {voice_name}: {path}")
    
    # 测试中文
    print("\n测试中文...")
    engine.set_voice("xiaoxiao", is_english=False)
    path = engine.speak("你好，这是 MiniMax 语音合成测试。")
    print(f"中文音频已生成: {path}")
