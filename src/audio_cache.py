"""
音频缓存模块 - 预加载TTS音频
"""
import os
import tempfile
from typing import Dict, List, Optional
import threading
import streamlit as st

# 导入TTS引擎
from src.tts_engine import tts_engine, speak_word
from src.minimax_tts import MiniMaxTTSEngine


class AudioCache:
    """音频缓存管理器"""
    
    def __init__(self):
        self.cache_dir = tempfile.mkdtemp(prefix="dictation_audio_")
        self.cache: Dict[str, str] = {}  # word -> audio_path
        self.loading_status: Dict[str, str] = {}  # word -> status
        self._lock = threading.Lock()
        self._tts_lock = threading.Lock()
        self.preload_total = 0
        self.preload_completed = 0
        self.preload_errors = 0
        self.preload_active = False
        self.preload_finished = False
        self._minimax_engine: Optional[MiniMaxTTSEngine] = None
    
    def _get_minimax_engine(self) -> Optional[MiniMaxTTSEngine]:
        """获取或创建 MiniMax 引擎"""
        if self._minimax_engine is None:
            # MiniMaxTTSEngine 内部已有默认 API Key
            self._minimax_engine = MiniMaxTTSEngine()
        return self._minimax_engine
        
    def get_cache_path(self, word: str, mode: str = "en") -> str:
        """获取缓存文件路径"""
        safe_word = "".join(c for c in word if c.isalnum() or c in ' _-').strip()
        return os.path.join(self.cache_dir, f"{safe_word}_{mode}.mp3")
    
    def is_cached(self, word: str, mode: str = "en") -> bool:
        """检查是否已缓存"""
        cache_key = f"{word}_{mode}"
        return cache_key in self.cache and os.path.exists(self.cache[cache_key])
    
    def get_audio(self, word: str, mode: str = "en", accent: str = "us",
                  use_minimax: bool = True,
                  voice_en: str = "expressive_narrator",
                  voice_cn: str = "xiaoxiao") -> Optional[str]:
        """获取音频路径"""
        cache_key = f"{word}_{mode}"
        
        if self.is_cached(word, mode):
            return self.cache[cache_key]
        
        # 如果未缓存，同步生成
        return self._generate_audio_sync(word, mode, accent=accent,
                                        use_minimax=use_minimax,
                                        voice_en=voice_en, voice_cn=voice_cn)
    
    def _generate_audio_sync(self, word: str, mode: str, accent: str = "us", 
                             use_minimax: bool = True,
                             voice_en: str = "expressive_narrator",
                             voice_cn: str = "xiaoxiao") -> Optional[str]:
        """同步生成音频"""
        try:
            cache_path = self.get_cache_path(word, mode)
            
            # 判断是否使用 MiniMax
            if use_minimax:
                minimax = self._get_minimax_engine()
                if minimax:
                    with self._tts_lock:
                        if mode == "en":
                            minimax.set_voice(voice_en, is_english=True)
                            minimax.set_rate(1.0)  # MiniMax 语速单独控制
                            audio_path = minimax.speak(word, save_path=cache_path)
                        else:  # cn
                            minimax.set_voice(voice_cn, is_english=False)
                            audio_path = minimax.speak(word, save_path=cache_path)
                else:
                    # MiniMax 初始化失败，回退到 Edge TTS
                    raise RuntimeError("MiniMax 引擎未初始化")
            else:
                # 使用 Edge TTS
                en_voice = "us_female" if accent == "us" else "uk_female"
                with self._tts_lock:
                    if mode == "en":
                        tts_engine.set_voice(en_voice)
                        audio_path = tts_engine.speak(word, save_path=cache_path)
                    else:  # cn
                        tts_engine.set_voice("chinese")
                        audio_path = tts_engine.speak(word, save_path=cache_path)
            
            cache_key = f"{word}_{mode}"
            with self._lock:
                self.cache[cache_key] = audio_path
            
            return audio_path
        except Exception as e:
            print(f"生成音频失败 {word}: {e}")
            # 如果 MiniMax 失败，尝试回退到 Edge TTS
            if use_minimax:
                print(f"尝试使用 Edge TTS 回退...")
                return self._generate_audio_sync(word, mode, accent, use_minimax=False)
            return None
    
    def preload_words(self, words: List[Dict], mode: str = "en_to_cn", accent: str = "us",
                      use_minimax: bool = True,
                      voice_en: str = "expressive_narrator",
                      voice_cn: str = "xiaoxiao") -> None:
        """
        预加载单词音频
        
        Args:
            words: 单词列表
            mode: 听写模式
            accent: 英语口音，"us" 或 "uk"
            use_minimax: 是否使用 MiniMax
            voice_en: 英文音色
            voice_cn: 中文音色
        """
        # 准备任务列表
        tasks = []
        for word_data in words:
            # 兼容两种 key 格式
            en = word_data.get('english', word_data.get('en', ''))
            cn = word_data.get('chinese', word_data.get('cn', ''))

            if mode == "en_to_cn" and en:
                tasks.append((en, "en"))
            elif mode == "cn_to_en" and cn:
                tasks.append((cn, "cn"))
            elif mode == "spell":
                if en:
                    tasks.append((en, "en"))
                if cn:
                    tasks.append((cn, "cn"))

        self._preload_tasks(tasks, accent=accent, use_minimax=use_minimax,
                           voice_en=voice_en, voice_cn=voice_cn)

    def preload_all_required(self, words: List[Dict], accent: str = "us",
                            use_minimax: bool = True,
                            voice_en: str = "expressive_narrator",
                            voice_cn: str = "xiaoxiao") -> None:
        """预加载听写可能用到的所有音频（英文+中文，自动去重）"""
        tasks = []
        for word_data in words:
            # 兼容两种 key 格式
            en = word_data.get('english', word_data.get('en', ''))
            cn = word_data.get('chinese', word_data.get('cn', ''))

            if en:
                tasks.append((en, "en"))
            if cn:
                tasks.append((cn, "cn"))

        self._preload_tasks(tasks, accent=accent, use_minimax=use_minimax,
                           voice_en=voice_en, voice_cn=voice_cn)

    def _preload_tasks(self, tasks: List[tuple], accent: str = "us",
                       use_minimax: bool = True,
                       voice_en: str = "expressive_narrator",
                       voice_cn: str = "xiaoxiao") -> None:
        """统一预加载实现，带进度统计"""
        import concurrent.futures

        # 去重，避免相同文本重复生成
        deduped_tasks = []
        seen = set()
        for item in tasks:
            if item in seen:
                continue
            seen.add(item)
            deduped_tasks.append(item)

        with self._lock:
            self.preload_total = len(deduped_tasks)
            self.preload_completed = 0
            self.preload_errors = 0
            self.preload_active = bool(deduped_tasks)
            self.preload_finished = not deduped_tasks

        if not deduped_tasks:
            return

        # 初始化 MiniMax 引擎（如果需要）
        minimax = None
        if use_minimax:
            minimax = self._get_minimax_engine()

        # 根据是否使用 MiniMax 选择音色
        if minimax:
            en_voice_selected = voice_en
        else:
            en_voice_selected = "us_female" if accent == "us" else "uk_female"

        def generate_one(item):
            word, audio_mode = item
            cache_path = self.get_cache_path(word, audio_mode)

            if os.path.exists(cache_path):
                return word, audio_mode, cache_path

            with self._tts_lock:
                if minimax:
                    # 使用 MiniMax
                    if audio_mode == "en":
                        minimax.set_voice(en_voice_selected, is_english=True)
                    else:
                        minimax.set_voice(voice_cn, is_english=False)
                    minimax.speak(word, save_path=cache_path)
                else:
                    # 使用 Edge TTS
                    if audio_mode == "en":
                        tts_engine.set_voice(en_voice_selected)
                    else:
                        tts_engine.set_voice("chinese")
                    tts_engine.speak(word, save_path=cache_path)

            return word, audio_mode, cache_path

        # MiniMax API 调用比 edge-tts 更稳定，可以适当提高并发

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(generate_one, task) for task in deduped_tasks]

            for future in concurrent.futures.as_completed(futures):
                try:
                    word, audio_mode, path = future.result()
                    if path:
                        cache_key = f"{word}_{audio_mode}"
                        with self._lock:
                            self.cache[cache_key] = path
                except Exception as e:
                    with self._lock:
                        self.preload_errors += 1
                    print(f"预加载失败: {e}")
                finally:
                    with self._lock:
                        self.preload_completed += 1

        with self._lock:
            self.preload_active = False
            self.preload_finished = True

    def get_preload_status(self) -> Dict[str, float]:
        """返回后台预加载状态"""
        with self._lock:
            total = self.preload_total
            completed = self.preload_completed
            errors = self.preload_errors
            active = self.preload_active
            finished = self.preload_finished

        progress = (completed / total) if total else 1.0
        return {
            "total": total,
            "completed": completed,
            "errors": errors,
            "active": active,
            "finished": finished,
            "progress": progress,
        }
    
    def get_progress(self) -> tuple:
        """获取加载进度"""
        total = len(self.cache)
        loaded = sum(1 for path in self.cache.values() if os.path.exists(path))
        return loaded, total
    
    def reset(self):
        """重置缓存目录和状态，用于切换到新词库。"""
        self.cleanup()
        self.cache_dir = tempfile.mkdtemp(prefix="dictation_audio_")
        with self._lock:
            self.cache = {}
            self.loading_status = {}
            self.preload_total = 0
            self.preload_completed = 0
            self.preload_errors = 0
            self.preload_active = False
            self.preload_finished = False

    def cleanup(self):
        """清理缓存"""
        try:
            import shutil
            shutil.rmtree(self.cache_dir, ignore_errors=True)
        except:
            pass


# Session state中存储的缓存实例
def get_audio_cache() -> AudioCache:
    """获取或创建音频缓存实例"""
    if 'audio_cache' not in st.session_state:
        st.session_state.audio_cache = AudioCache()
    return st.session_state.audio_cache


def preload_audio_for_dictation(words: List[Dict], mode: str, **kwargs):
    """便捷函数：预加载听写音频"""
    cache = get_audio_cache()
    cache.preload_words(words, mode, **kwargs)


def get_cached_audio(word: str, mode: str = "en", accent: str = "us",
                     use_minimax: bool = True,
                     voice_en: str = "expressive_narrator",
                     voice_cn: str = "xiaoxiao") -> Optional[str]:
    """便捷函数：获取缓存的音频"""
    cache = get_audio_cache()
    return cache.get_audio(word, mode, accent=accent,
                          use_minimax=use_minimax,
                          voice_en=voice_en, voice_cn=voice_cn)


if __name__ == '__main__':
    # 测试
    cache = AudioCache()
    
    words = [
        {'english': 'apple', 'chinese': '苹果'},
        {'english': 'banana', 'chinese': '香蕉'},
        {'english': 'computer', 'chinese': '电脑'},
    ]
    
    print("预加载音频...")
    cache.preload_words(words, "en_to_cn")
    
    print(f"\n缓存完成: {cache.get_progress()}")
    
    # 测试获取
    path = cache.get_audio('apple', 'en')
    print(f"\napple音频路径: {path}")
    print(f"文件存在: {os.path.exists(path) if path else False}")
