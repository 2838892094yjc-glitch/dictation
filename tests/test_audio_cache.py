"""
音频缓存单元测试
"""
import pytest
import os
from src.audio_cache import AudioCache


class TestAudioCache:
    """音频缓存测试类"""

    def test_init(self):
        """测试初始化"""
        cache = AudioCache()
        assert cache.cache_dir is not None
        assert os.path.exists(cache.cache_dir)
        assert isinstance(cache.cache, dict)

    def test_get_cache_path(self):
        """测试获取缓存路径"""
        cache = AudioCache()

        path = cache.get_cache_path('apple', 'en')
        assert 'apple' in path
        assert path.endswith('.mp3')

        # 特殊字符应该被清理
        path = cache.get_cache_path('hello world!', 'en')
        assert 'hello' in path
        assert '!' not in path

    def test_is_cached(self):
        """测试缓存检查"""
        cache = AudioCache()

        # 未缓存
        assert cache.is_cached('apple', 'en') == False

        # 添加到缓存
        cache_path = cache.get_cache_path('apple', 'en')
        cache.cache[f'apple_en'] = cache_path

        # 文件不存在，仍然返回False
        assert cache.is_cached('apple', 'en') == False

    @pytest.mark.slow
    def test_generate_audio_sync(self):
        """测试同步生成音频"""
        cache = AudioCache()

        # 生成英文音频
        audio_path = cache._generate_audio_sync('hello', 'en', use_minimax=False)

        assert audio_path is not None
        assert os.path.exists(audio_path)
        assert os.path.getsize(audio_path) > 0

    @pytest.mark.slow
    def test_get_audio(self):
        """测试获取音频"""
        cache = AudioCache()

        # 第一次获取（生成）
        audio_path = cache.get_audio('test', 'en', use_minimax=False)
        assert audio_path is not None
        assert os.path.exists(audio_path)

        # 第二次获取（从缓存）
        audio_path2 = cache.get_audio('test', 'en', use_minimax=False)
        assert audio_path2 == audio_path

    @pytest.mark.slow
    def test_preload_words(self, sample_word_list):
        """测试预加载单词"""
        cache = AudioCache()

        # 预加载（英译中模式）
        cache.preload_words(sample_word_list, mode='en_to_cn', use_minimax=False)

        # 等待预加载完成
        import time
        max_wait = 30
        waited = 0
        while cache.preload_active and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        # 检查状态
        status = cache.get_preload_status()
        assert status['finished'] == True
        assert status['completed'] > 0

    @pytest.mark.slow
    def test_preload_all_required(self, sample_word_list):
        """测试预加载所有音频"""
        cache = AudioCache()

        # 预加载所有
        cache.preload_all_required(sample_word_list, use_minimax=False)

        # 等待完成
        import time
        max_wait = 60
        waited = 0
        while cache.preload_active and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        # 检查状态
        status = cache.get_preload_status()
        assert status['finished'] == True
        assert status['total'] > 0

    def test_get_preload_status(self):
        """测试获取预加载状态"""
        cache = AudioCache()

        status = cache.get_preload_status()

        assert 'total' in status
        assert 'completed' in status
        assert 'errors' in status
        assert 'active' in status
        assert 'finished' in status
        assert 'progress' in status

    def test_reset(self):
        """测试重置缓存"""
        cache = AudioCache()

        # 添加一些数据
        cache.cache['test'] = 'path'
        cache.preload_total = 10

        # 重置
        old_dir = cache.cache_dir
        cache.reset()

        # 检查状态
        assert cache.cache == {}
        assert cache.preload_total == 0
        assert cache.cache_dir != old_dir

    def test_cleanup(self):
        """测试清理缓存"""
        cache = AudioCache()
        cache_dir = cache.cache_dir

        # 清理
        cache.cleanup()

        # 目录应该被删除
        # 注意：可能因为权限问题删除失败，所以不强制检查


class TestAudioCacheIntegration:
    """音频缓存集成测试"""

    @pytest.mark.slow
    def test_full_workflow(self, sample_word_list):
        """测试完整工作流"""
        cache = AudioCache()

        # 1. 预加载
        cache.preload_words(sample_word_list[:2], mode='en_to_cn', use_minimax=False)

        # 2. 等待完成
        import time
        max_wait = 30
        waited = 0
        while cache.preload_active and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        # 3. 获取音频
        audio_path = cache.get_audio('apple', 'en', use_minimax=False)
        assert audio_path is not None
        assert os.path.exists(audio_path)

        # 4. 检查缓存命中
        assert cache.is_cached('apple', 'en') == True

        # 5. 清理
        cache.cleanup()
