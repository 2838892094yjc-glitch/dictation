"""
完整流程集成测试
"""
import pytest
import os
import tempfile
from PIL import Image


class TestFullWorkflow:
    """完整工作流测试"""

    @pytest.mark.slow
    def test_vocabulary_to_dictation_workflow(self, sample_word_list):
        """测试从词库到听写的完整流程"""
        from data.vocabulary_store import VocabularyStore
        from src.audio_cache import AudioCache

        # 1. 创建词库
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VocabularyStore(data_dir=tmpdir)
            vocab_data = {
                'name': '测试词库',
                'words': sample_word_list,
                'description': '测试'
            }
            store.save_vocabulary('测试词库', vocab_data)

            # 2. 加载词库
            loaded = store.load_vocabulary('测试词库')
            assert loaded is not None
            assert len(loaded['words']) > 0

            # 3. 预加载音频
            cache = AudioCache()
            cache.preload_words(loaded['words'][:2], mode='en_to_cn', use_minimax=False)

            # 等待预加载
            import time
            max_wait = 30
            waited = 0
            while cache.preload_active and waited < max_wait:
                time.sleep(0.5)
                waited += 0.5

            # 4. 获取音频
            audio_path = cache.get_audio(loaded['words'][0]['en'], 'en', use_minimax=False)
            assert audio_path is not None
            assert os.path.exists(audio_path)

            # 清理
            cache.cleanup()

    @pytest.mark.slow
    def test_ocr_to_correction_workflow(self):
        """测试从OCR到纠正的完整流程"""
        from src.ocr_engine import OCREngine
        from src.ai_corrector import correct_spelling

        # 创建测试图片
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, 'test.jpg')
            img = Image.new('RGB', (800, 600), color='white')
            img.save(img_path)

            # 1. OCR识别
            engine = OCREngine()
            texts = engine.recognize(img_path)

            # 2. 提取单词对
            pairs = engine.extract_word_pairs(texts)

            # 3. AI纠正
            if pairs:
                corrected = correct_spelling(pairs)
                assert isinstance(corrected, list)

    @pytest.mark.slow
    def test_dictation_to_grading_workflow(self, sample_word_list):
        """测试从听写到批改的完整流程"""
        from src.audio_cache import AudioCache
        from src.handwriting_recognizer import HandwritingRecognizer

        # 1. 准备听写
        cache = AudioCache()
        cache.preload_words(sample_word_list[:2], mode='en_to_cn', use_minimax=False)

        # 等待预加载
        import time
        max_wait = 30
        waited = 0
        while cache.preload_active and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        # 2. 模拟用户答案
        user_answers = ['苹果', '香蕉']

        # 3. 批改
        recognizer = HandwritingRecognizer()
        result = recognizer.compare(user_answers, sample_word_list[:2], mode='en_to_cn')

        assert result['total'] == 2
        assert 'score' in result
        assert 'correct_count' in result

        # 清理
        cache.cleanup()


class TestErrorHandling:
    """错误处理测试"""

    def test_ocr_invalid_image(self):
        """测试无效图片"""
        from src.ocr_engine import OCREngine

        engine = OCREngine()

        # 不存在的文件
        with pytest.raises(Exception):
            engine.recognize('/nonexistent/image.jpg')

    def test_vocabulary_invalid_data(self, temp_dir):
        """测试无效词库数据"""
        from data.vocabulary_store import VocabularyStore

        store = VocabularyStore(data_dir=temp_dir)

        # 保存无效数据
        result = store.save_vocabulary('invalid', None)
        # 应该处理错误而不是崩溃

    def test_audio_cache_invalid_word(self):
        """测试无效单词"""
        from src.audio_cache import AudioCache

        cache = AudioCache()

        # 空字符串
        result = cache.get_audio('', 'en', use_minimax=False)
        # 应该返回None或处理错误

        cache.cleanup()

    def test_corrector_empty_input(self):
        """测试空输入"""
        from src.ai_corrector import correct_spelling

        result = correct_spelling([])
        assert result == []

        result = correct_spelling([{'en': '', 'cn': ''}])
        assert len(result) == 1


class TestPerformance:
    """性能测试"""

    @pytest.mark.slow
    def test_batch_audio_generation(self, sample_word_list):
        """测试批量音频生成性能"""
        from src.audio_cache import AudioCache
        import time

        cache = AudioCache()

        # 记录时间
        start_time = time.time()

        # 预加载
        cache.preload_words(sample_word_list, mode='en_to_cn', use_minimax=False)

        # 等待完成
        max_wait = 60
        waited = 0
        while cache.preload_active and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        elapsed = time.time() - start_time

        # 检查性能（5个单词应该在60秒内完成）
        assert elapsed < 60

        # 清理
        cache.cleanup()

    def test_corrector_performance(self):
        """测试纠正器性能"""
        from src.ai_corrector import correct_spelling
        import time

        # 准备大量数据
        words = [{'en': f'word{i}', 'cn': f'词{i}'} for i in range(100)]

        # 记录时间
        start_time = time.time()
        result = correct_spelling(words)
        elapsed = time.time() - start_time

        # 100个单词应该在1秒内完成
        assert elapsed < 1.0
        assert len(result) == 100


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_vocabulary(self, temp_dir):
        """测试空词库"""
        from data.vocabulary_store import VocabularyStore

        store = VocabularyStore(data_dir=temp_dir)

        vocab_data = {'name': '空词库', 'words': []}
        store.save_vocabulary('空词库', vocab_data)

        loaded = store.load_vocabulary('空词库')
        assert loaded is not None
        assert len(loaded['words']) == 0

    def test_very_long_word(self):
        """测试超长单词"""
        from src.ai_corrector import AICorrector

        corrector = AICorrector()

        long_word = 'a' * 1000
        result, note = corrector.correct_word(long_word)

        # 应该能处理而不崩溃
        assert isinstance(result, str)

    def test_special_characters_in_word(self):
        """测试特殊字符"""
        from src.ai_corrector import AICorrector

        corrector = AICorrector()

        # 包含特殊字符
        result, note = corrector.correct_word('app!e@#$')
        assert isinstance(result, str)

    def test_unicode_characters(self):
        """测试Unicode字符"""
        from src.ai_corrector import correct_spelling

        words = [
            {'en': 'café', 'cn': '咖啡馆'},
            {'en': 'naïve', 'cn': '天真的'},
        ]

        result = correct_spelling(words)
        assert len(result) == 2
