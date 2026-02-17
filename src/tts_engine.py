"""
TTS语音引擎 - 文字转语音播报
"""
import asyncio
import tempfile
import os
from typing import Optional
import edge_tts

# pyttsx3 仅本地使用，云端跳过
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class TTSEngine:
    """语音播报引擎"""
    
    def __init__(self):
        self.engine_type = "edge"  # 默认使用edge-tts
        self.voice = "en-US-AriaNeural"  # 默认美式英语女声
        self.rate = "+0%"  # 语速
        self.volume = "+0%"  # 音量
        
        # 初始化本地TTS作为备选
        self._init_local_tts()
    
    def _init_local_tts(self):
        """初始化本地TTS引擎"""
        if not PYTTSX3_AVAILABLE:
            self.local_tts = None
            return
        try:
            self.local_tts = pyttsx3.init()
            self.local_tts.setProperty('rate', 150)
            self.local_tts.setProperty('volume', 0.9)
        except Exception as e:
            print(f"本地TTS初始化失败: {e}")
            self.local_tts = None
    
    def set_voice(self, voice_type: str = "us_female"):
        """
        设置语音类型
        
        Args:
            voice_type: 
                - "us_female": 美式英语女声
                - "us_male": 美式英语男声
                - "uk_female": 英式英语女声
                - "uk_male": 英式英语男声
                - "chinese": 中文
        """
        voices = {
            "us_female": "en-US-AriaNeural",
            "us_male": "en-US-GuyNeural",
            "uk_female": "en-GB-SoniaNeural",
            "uk_male": "en-GB-RyanNeural",
            "chinese": "zh-CN-XiaoxiaoNeural",
        }
        
        if voice_type in voices:
            self.voice = voices[voice_type]
    
    def set_rate(self, speed: float = 1.0):
        """
        设置语速
        
        Args:
            speed: 0.5-2.0，1.0为正常速度
        """
        if speed < 0.5:
            speed = 0.5
        if speed > 2.0:
            speed = 2.0
        
        # 转换为edge-tts格式
        if speed > 1.0:
            self.rate = f"+{int((speed - 1) * 100)}%"
        elif speed < 1.0:
            self.rate = f"-{int((1 - speed) * 100)}%"
        else:
            self.rate = "+0%"
        
        # 同时更新本地TTS
        if self.local_tts:
            rate = int(150 * speed)
            self.local_tts.setProperty('rate', rate)
    
    async def _speak_edge_async(self, text: str) -> str:
        """
        使用edge-tts生成语音文件
        
        Returns:
            生成的音频文件路径
        """
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume
        )
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name
        
        await communicate.save(temp_path)
        return temp_path
    
    def speak(self, text: str, save_path: Optional[str] = None) -> str:
        """
        播报文字
        
        Args:
            text: 要播报的文字
            save_path: 保存路径，None则创建临时文件
            
        Returns:
            音频文件路径
        """
        if not text:
            return ""
        
        try:
            # 使用edge-tts
            audio_path = asyncio.run(self._speak_edge_async(text))
            
            if save_path:
                os.rename(audio_path, save_path)
                return save_path
            
            return audio_path
            
        except Exception as e:
            print(f"Edge TTS失败，尝试本地TTS: {e}")
            return self._speak_local(text, save_path)
    
    def _speak_local(self, text: str, save_path: Optional[str] = None) -> str:
        """使用本地TTS"""
        if not self.local_tts:
            raise RuntimeError("没有可用的TTS引擎")
        
        if save_path is None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                save_path = f.name
        
        self.local_tts.save_to_file(text, save_path)
        self.local_tts.runAndWait()
        
        return save_path
    
    def get_audio_bytes(self, text: str) -> bytes:
        """获取音频文件的二进制数据"""
        audio_path = self.speak(text)
        with open(audio_path, 'rb') as f:
            data = f.read()
        
        # 删除临时文件
        try:
            os.remove(audio_path)
        except:
            pass
        
        return data


# 全局TTS引擎实例
tts_engine = TTSEngine()


def speak_word(word: str, meaning: str = "", mode: str = "en_to_cn", accent: str = "us") -> str:
    """
    播报单词的便捷函数
    
    Args:
        word: 英文单词
        meaning: 中文释义
        mode: 播报模式
            - "en_to_cn": 报英文，要求写中文
            - "cn_to_en": 报中文，要求写英文
            - "spell": 报英文+释义，要求拼写
        accent: 英语口音，"us" 或 "uk"
    
    Returns:
        音频文件路径
    """
    # 根据口音选择音色
    en_voice = "us_female" if accent == "us" else "uk_female"
    
    if mode == "en_to_cn":
        text = word
        tts_engine.set_voice(en_voice)
    elif mode == "cn_to_en":
        text = meaning or word
        tts_engine.set_voice("chinese")
    elif mode == "spell":
        text = f"{word}. {meaning}" if meaning else word
        tts_engine.set_voice(en_voice)
    else:
        text = word
        tts_engine.set_voice(en_voice)
    
    return tts_engine.speak(text)


if __name__ == '__main__':
    # 测试
    print("测试TTS引擎...")
    
    # 测试英文
    print("播报英文: Hello")
    path = speak_word("Hello", "你好", "en_to_cn")
    print(f"生成文件: {path}")
    
    # 测试中文
    print("播报中文: 苹果")
    tts_engine.set_voice("chinese")
    path = tts_engine.speak("苹果")
    print(f"生成文件: {path}")
