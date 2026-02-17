"""
音频播放组件
统一处理不同模式的音频播放逻辑
"""
import os
import base64
import time
import streamlit as st
from typing import Optional, List, Dict, Callable


class AudioPlayer:
    """音频播放器组件"""

    # 播放模式常量
    MODE_EN_TO_CN = "en_to_cn"  # 英译中：播放英文
    MODE_CN_TO_EN = "cn_to_en"  # 中译英：播放中文
    MODE_SPELL = "spell"        # 拼写模式：先英文后中文

    def __init__(self, audio_cache, voice_en: str = "male_qn_qingse", voice_cn: str = "female_shaonv"):
        """
        初始化音频播放器

        Args:
            audio_cache: 音频缓存对象
            voice_en: 英文语音
            voice_cn: 中文语音
        """
        self.audio_cache = audio_cache
        self.voice_en = voice_en
        self.voice_cn = voice_cn

    def update_voices(self, voice_en: str = None, voice_cn: str = None):
        """更新语音设置"""
        if voice_en:
            self.voice_en = voice_en
        if voice_cn:
            self.voice_cn = voice_cn

    @staticmethod
    def play_audio(audio_path: str) -> bool:
        """
        播放单个音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            是否播放成功
        """
        if not audio_path or not os.path.exists(audio_path):
            return False

        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        b64_audio = base64.b64encode(audio_bytes).decode()
        st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)
        return True

    @staticmethod
    def play_audio_delayed(audio_path: str, delay_ms: int = 1500) -> bool:
        """
        延迟播放音频（使用 JavaScript）

        Args:
            audio_path: 音频文件路径
            delay_ms: 延迟毫秒数

        Returns:
            是否设置成功
        """
        if not audio_path or not os.path.exists(audio_path):
            return False

        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        b64_audio = base64.b64encode(audio_bytes).decode()
        st.markdown(f"""
        <script>
            setTimeout(function() {{
                var audio = new Audio('data:audio/mp3;base64,{b64_audio}');
                audio.play();
            }}, {delay_ms});
        </script>
        """, unsafe_allow_html=True)
        return True

    def get_audio_path(self, text: str, lang: str = "en") -> Optional[str]:
        """
        获取音频文件路径

        Args:
            text: 要转换的文本
            lang: 语言类型 "en" 或 "cn"

        Returns:
            音频文件路径，失败返回 None
        """
        if lang == "en":
            return self.audio_cache.get_audio(text, mode="en", voice_en=self.voice_en)
        else:
            return self.audio_cache.get_audio(text, mode="cn", voice_cn=self.voice_cn)

    def play_word(self, word: Dict[str, str], mode: str, use_js_delay: bool = True) -> bool:
        """
        根据模式播放单词

        Args:
            word: 单词字典，包含 'en' 和 'cn' 键
            mode: 播放模式 (en_to_cn, cn_to_en, spell)
            use_js_delay: spell 模式下是否使用 JS 延迟（适用于单次播放）

        Returns:
            是否播放成功
        """
        if mode == self.MODE_EN_TO_CN:
            # 英译中：播放英文
            audio_path = self.get_audio_path(word['en'], "en")
            return self.play_audio(audio_path)

        elif mode == self.MODE_CN_TO_EN:
            # 中译英：播放中文
            audio_path = self.get_audio_path(word['cn'], "cn")
            return self.play_audio(audio_path)

        elif mode == self.MODE_SPELL:
            # 拼写模式：先播放英文，再播放中文
            audio_path_en = self.get_audio_path(word['en'], "en")
            audio_path_cn = self.get_audio_path(word['cn'], "cn")

            # 播放英文
            self.play_audio(audio_path_en)

            # 播放中文（延迟）
            if use_js_delay:
                # 使用 JavaScript 延迟（适用于单次播放，不阻塞）
                self.play_audio_delayed(audio_path_cn, 1500)
            else:
                # 使用 time.sleep（适用于连续播放）
                time.sleep(1.5)
                self.play_audio(audio_path_cn)
            return True

        return False

    def auto_play_all(
        self,
        words: List[Dict[str, str]],
        order: List[int],
        mode: str,
        interval: float = 3.0,
        on_progress: Callable[[int, int], None] = None,
        on_complete: Callable[[], None] = None
    ):
        """
        自动连续播放所有单词

        Args:
            words: 单词列表
            order: 播放顺序（索引列表）
            mode: 播放模式
            interval: 单词间隔时间（秒）
            on_progress: 进度回调函数 (current_index, total)
            on_complete: 完成回调函数
        """
        total = len(words)

        for i, idx in enumerate(order):
            word = words[idx]

            # 进度回调
            if on_progress:
                on_progress(i, total)

            # 播放单词（连续播放模式不使用 JS 延迟）
            self.play_word(word, mode, use_js_delay=False)

            # 等待间隔
            time.sleep(interval)

        # 完成回调
        if on_complete:
            on_complete()

    def preload_words(self, words: List[Dict[str, str]], mode: str) -> int:
        """
        预加载单词音频

        Args:
            words: 单词列表
            mode: 播放模式

        Returns:
            成功预加载的数量
        """
        count = 0
        for word in words:
            if mode in [self.MODE_EN_TO_CN, self.MODE_SPELL]:
                if self.get_audio_path(word['en'], "en"):
                    count += 1
            if mode in [self.MODE_CN_TO_EN, self.MODE_SPELL]:
                if self.get_audio_path(word['cn'], "cn"):
                    count += 1
        return count


# 便捷函数，保持向后兼容
def play_audio(audio_path: str) -> bool:
    """播放单个音频文件（便捷函数）"""
    return AudioPlayer.play_audio(audio_path)


def create_audio_player_from_session() -> AudioPlayer:
    """从 session state 创建音频播放器"""
    return AudioPlayer(
        audio_cache=st.session_state.audio_cache,
        voice_en=st.session_state.voice_en,
        voice_cn=st.session_state.voice_cn
    )
