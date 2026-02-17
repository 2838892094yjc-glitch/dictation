"""
TTS引擎单元测试
"""
import pytest
import os
from src.tts_engine import TTSEngine, speak_word


class TestTTSEngine:
    """TTS引擎测试类"""

    def test_init(self):
        """测试初始化"""
        engine = TTSEngine()
        assert engine.engine_type == "edge"
        assert engine.voice is not None

    def test_set_voice(self):
        """测试设置音色"""
        engine = TTSEngine()

        # 美式英语女声
        engine.set_voice("us_female")
        assert engine.voice == "en-US-AriaNeural"

        # 美式英语男声
        engine.set_voice("us_male")
        assert engine.voice == "en-US-GuyNeural"

        # 英式英语女声
        engine.set_voice("uk_female")
        assert engine.voice == "en-GB-SoniaNeural"

        # 中文
        engine.set_voice("chinese")
        assert engine.voice == "zh-CN-XiaoxiaoNeural"

    def test_set_rate(self):
        """测试设置语速"""
        engine = TTSEngine()

        # 正常速度
        engine.set_rate(1.0)
        assert engine.rate == "+0%"

        # 加速
        engine.set_rate(1.5)
        assert engine.rate == "+50%"

        # 减速
        engine.set_rate(0.8)
        assert engine.rate == "-20%"

        # 边界值
        engine.set_rate(0.3)  # 应该被限制为0.5
        assert engine.rate == "-50%"

        engine.set_rate(3.0)  # 应该被限制为2.0
        assert engine.rate == "+100%"

    @pytest.mark.slow
    def test_speak_english(self, temp_dir):
        """测试英文语音生成"""
        engine = TTSEngine()
        engine.set_voice("us_female")

        # 生成音频
        audio_path = engine.speak("Hello", save_path=os.path.join(temp_dir, "hello.mp3"))

        # 检查文件是否生成
        assert audio_path is not None
        assert os.path.exists(audio_path)
        assert os.path.getsize(audio_path) > 0

    @pytest.mark.slow
    def test_speak_chinese(self, temp_dir):
        """测试中文语音生成"""
        engine = TTSEngine()
        engine.set_voice("chinese")

        # 生成音频
        audio_path = engine.speak("你好", save_path=os.path.join(temp_dir, "nihao.mp3"))

        # 检查文件是否生成
        assert audio_path is not None
        assert os.path.exists(audio_path)
        assert os.path.getsize(audio_path) > 0

    def test_speak_empty_text(self):
        """测试空文本"""
        engine = TTSEngine()
        result = engine.speak("")
        assert result == ""

    @pytest.mark.slow
    def test_get_audio_bytes(self):
        """测试获取音频字节"""
        engine = TTSEngine()

        # 生成音频字节
        audio_bytes = engine.get_audio_bytes("test")

        # 检查返回值
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0


class TestSpeakWord:
    """测试speak_word便捷函数"""

    @pytest.mark.slow
    def test_speak_word_en_to_cn(self):
        """测试英译中模式"""
        audio_path = speak_word("apple", "苹果", mode="en_to_cn", accent="us")

        assert audio_path is not None
        assert os.path.exists(audio_path)

    @pytest.mark.slow
    def test_speak_word_cn_to_en(self):
        """测试中译英模式"""
        audio_path = speak_word("apple", "苹果", mode="cn_to_en", accent="us")

        assert audio_path is not None
        assert os.path.exists(audio_path)

    @pytest.mark.slow
    def test_speak_word_spell(self):
        """测试拼写模式"""
        audio_path = speak_word("apple", "苹果", mode="spell", accent="us")

        assert audio_path is not None
        assert os.path.exists(audio_path)

    @pytest.mark.slow
    def test_speak_word_uk_accent(self):
        """测试英式口音"""
        audio_path = speak_word("hello", "你好", mode="en_to_cn", accent="uk")

        assert audio_path is not None
        assert os.path.exists(audio_path)
