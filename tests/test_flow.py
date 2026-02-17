"""
完整流程测试 - 端到端测试
"""
import pytest
import os
import tempfile
from PIL import Image


class TestDictationFlow:
    """听写完整流程测试"""

    @pytest.mark.slow
    def test_en_to_cn_flow(self, sample_word_list):
        """测试英译中完整流程"""
        from data.vocabulary_store import VocabularyStore
        from src.audio_cache import AudioCache
        from src.handwriting_recognizer import HandwritingRecognizer

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. 创建词库
            store = VocabularyStore(data_dir=tmpdir)
            vocab_data = {
                'name': '英译中测试',
                'words': sample_word_list[:3],
                'description': '测试'
            }
            store.save_vocabulary('英译中测试', vocab_data)

            # 2. 加载词库
            loaded = store.load_vocabulary('英译中测试')
            assert loaded is not None
            assert len(loaded['words']) == 3

            # 3. 预加载音频（英译中模式播报英文）
            cache = AudioCache()
            cache.preload_words(loaded['words'], mode='en_to_cn', use_minimax=False)

            # 等待预加载
            import time
            max_wait = 30
            waited = 0
            while cache.preload_active and waited < max_wait:
                time.sleep(0.5)
                waited += 0.5

            # 4. 验证音频生成
            status = cache.get_preload_status()
            assert status['finished'] == True

            # 5. 模拟用户答案（中文）
            user_answers = ['苹果', '香蕉', '电脑']

            # 6. 批改
            recognizer = HandwritingRecognizer()
            result = recognizer.compare(user_answers, loaded['words'], mode='en_to_cn')

            assert result['total'] == 3
            assert 'score' in result
            assert 'correct_count' in result

            # 清理
            cache.cleanup()

    @pytest.mark.slow
    def test_cn_to_en_flow(self, sample_word_list):
        """测试中译英完整流程"""
        from data.vocabulary_store import VocabularyStore
        from src.audio_cache import AudioCache
        from src.handwriting_recognizer import HandwritingRecognizer

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. 创建词库
            store = VocabularyStore(data_dir=tmpdir)
            vocab_data = {
                'name': '中译英测试',
                'words': sample_word_list[:3],
                'description': '测试'
            }
            store.save_vocabulary('中译英测试', vocab_data)

            # 2. 加载词库
            loaded = store.load_vocabulary('中译英测试')
            assert loaded is not None

            # 3. 预加载音频（中译英模式播报中文）
            cache = AudioCache()
            cache.preload_words(loaded['words'], mode='cn_to_en', use_minimax=False)

            # 等待预加载
            import time
            max_wait = 30
            waited = 0
            while cache.preload_active and waited < max_wait:
                time.sleep(0.5)
                waited += 0.5

            # 4. 模拟用户答案（英文）
            user_answers = ['apple', 'banana', 'computer']

            # 5. 批改
            recognizer = HandwritingRecognizer()
            result = recognizer.compare(user_answers, loaded['words'], mode='cn_to_en')

            assert result['total'] == 3
            assert result['correct_count'] == 3
            assert result['score'] == 100.0

            # 清理
            cache.cleanup()

    @pytest.mark.slow
    def test_spell_mode_flow(self, sample_word_list):
        """测试拼写模式完整流程"""
        from src.audio_cache import AudioCache
        from src.handwriting_recognizer import HandwritingRecognizer

        # 1. 预加载音频（拼写模式需要英文和中文）
        cache = AudioCache()
        cache.preload_words(sample_word_list[:2], mode='spell', use_minimax=False)

        # 等待预加载
        import time
        max_wait = 30
        waited = 0
        while cache.preload_active and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        # 2. 验证英文和中文音频都生成了
        status = cache.get_preload_status()
        assert status['finished'] == True
        # 拼写模式每个单词需要英文+中文，所以总数是单词数*2
        assert status['total'] >= 2

        # 3. 模拟用户答案（拼写英文）
        user_answers = ['apple', 'banana']

        # 4. ���改
        recognizer = HandwritingRecognizer()
        result = recognizer.compare(user_answers, sample_word_list[:2], mode='spell')

        assert result['total'] == 2
        assert result['correct_count'] == 2

        # 清理
        cache.cleanup()


class TestOCRToCorrection:
    """OCR到纠正流程测试"""

    def test_ocr_correction_flow(self):
        """测试OCR识别后AI纠正流程"""
        from src.ai_corrector import correct_spelling

        # 模拟OCR识别结果（包含错误）
        ocr_results = [
            {'en': 'ofien', 'cn': '经常'},
            {'en': 'beutiful', 'cn': '美丽的'},
            {'en': 'apple', 'cn': '苹果'},
        ]

        # AI纠正
        corrected = correct_spelling(ocr_results)

        # 验证纠正结果
        assert len(corrected) == 3
        assert corrected[0]['en'] == 'often'
        assert corrected[1]['en'] == 'beautiful'
        assert corrected[2]['en'] == 'apple'

        # 验证纠正标记
        assert corrected[0]['corrected'] == 'often'
        assert corrected[1]['corrected'] == 'beautiful'
        assert corrected[2]['corrected'] is None  # apple没有被纠正


class TestHistoryFlow:
    """历史记录流程测试"""

    def test_history_record_flow(self, temp_dir):
        """测试历史记录完整流程"""
        from src.history_manager import HistoryManager

        manager = HistoryManager(data_dir=temp_dir)

        # 1. 添加记录
        manager.add_record(
            mode='en_to_cn',
            vocabulary_name='测试词库',
            total_words=10,
            correct_count=8,
            duration_seconds=120,
            wrong_words=[
                {'en': 'apple', 'cn': '苹果', 'user_answer': '苹'},
                {'en': 'banana', 'cn': '香蕉', 'user_answer': '香'}
            ]
        )

        # 2. 获取记录
        records = manager.get_all_records()
        assert len(records) == 1
        assert records[0]['score'] == 80.0

        # 3. 获取统计
        stats = manager.get_statistics()
        assert stats['total_sessions'] == 1
        assert stats['total_words'] == 10
        assert stats['average_score'] == 80.0

        # 4. 获取高频错词
        wrong_freq = manager.get_wrong_words_frequency()
        assert len(wrong_freq) == 2

        # 5. 删除记录
        record_id = records[0]['id']
        manager.delete_record(record_id)
        assert len(manager.get_all_records()) == 0


class TestWrongAnswerFlow:
    """错题本流程测试"""

    def test_wrong_answer_flow(self, temp_dir):
        """测试错题本完整流程"""
        from src.wrong_answer_manager import WrongAnswerManager

        manager = WrongAnswerManager(data_dir=temp_dir)

        # 1. 添加错题
        manager.add_wrong_answer('apple', '苹果', '苹')
        manager.add_wrong_answer('banana', '香蕉', '香')
        manager.add_wrong_answer('apple', '苹果', '苹果')  # 再次错误

        # 2. 获取错题列表
        wrong_words = manager.get_all_wrong_answers()
        assert len(wrong_words) == 2  # 去重后2个

        # 3. 获取复习单词（按错误次数排序）
        review_words = manager.get_review_words()
        assert review_words[0]['en'] == 'apple'  # apple错了2次，排第一
        assert review_words[0]['wrong_count'] == 2

        # 4. 获取统计
        stats = manager.get_stats()
        assert stats['total_wrong'] == 3
        assert stats['unique_words'] == 2

        # 5. 移除单词
        manager.remove_word('apple')
        assert len(manager.get_all_wrong_answers()) == 1

        # 6. 清空
        manager.clear_all()
        assert len(manager.get_all_wrong_answers()) == 0


class TestVocabularyImportExport:
    """词库导入导出流程测试"""

    def test_json_import_export(self, temp_dir, sample_word_list):
        """测试JSON格式导入导出"""
        from data.vocabulary_store import VocabularyStore
        import json

        store = VocabularyStore(data_dir=temp_dir)

        # 1. 保存词库
        vocab_data = {
            'name': '导出测试',
            'words': sample_word_list,
            'description': '测试描述'
        }
        store.save_vocabulary('导出测试', vocab_data)

        # 2. 导出为JSON
        export_path = os.path.join(temp_dir, 'export.json')
        success = store.export_to_json('导出测试', export_path)
        assert success == True
        assert os.path.exists(export_path)

        # 3. 验证导出内容
        with open(export_path, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        assert exported['name'] == '导出测试'
        assert len(exported['words']) == len(sample_word_list)

        # 4. 导入JSON
        result = store.import_from_json(export_path, '导入测试')
        assert result is not None
        assert result['name'] == '导入测试'

        # 5. 验证导入结果
        loaded = store.load_vocabulary('导入测试')
        assert loaded is not None
        assert len(loaded['words']) == len(sample_word_list)

    def test_txt_import_export(self, temp_dir, sample_word_list):
        """测试TXT格式导入导出"""
        from data.vocabulary_store import VocabularyStore

        store = VocabularyStore(data_dir=temp_dir)

        # 1. 保存词库
        store.save_vocabulary('TXT测试', {'name': 'TXT测试', 'words': sample_word_list})

        # 2. 导出为TXT
        export_path = os.path.join(temp_dir, 'export.txt')
        success = store.export_to_txt('TXT测试', export_path)
        assert success == True

        # 3. 验证TXT内容
        with open(export_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == len(sample_word_list)

        # 4. 导入TXT
        result = store.import_from_txt(export_path, 'TXT导入')
        assert result is not None

    def test_csv_import_export(self, temp_dir, sample_word_list):
        """测试CSV格式导入导出"""
        from data.vocabulary_store import VocabularyStore

        store = VocabularyStore(data_dir=temp_dir)

        # 1. 保存词库
        store.save_vocabulary('CSV测试', {'name': 'CSV测试', 'words': sample_word_list})

        # 2. 导出为CSV
        export_path = os.path.join(temp_dir, 'export.csv')
        success = store.export_to_csv('CSV测试', export_path)
        assert success == True

        # 3. 导入CSV
        result = store.import_from_csv(export_path, 'CSV导入')
        assert result is not None


class TestThemeFlow:
    """主题切换流程测试"""

    def test_theme_loading(self):
        """测试主题加载"""
        from src.theme_manager import load_theme, get_available_themes

        # 获取可用主题
        themes = get_available_themes()
        assert 'default' in themes
        assert 'dark' in themes
        assert 'light' in themes

        # 加载深色主题
        dark_css = load_theme('dark')
        assert dark_css is not None
        assert 'background' in dark_css.lower() or 'color' in dark_css.lower()

        # 加载浅色主题
        light_css = load_theme('light')
        assert light_css is not None


class TestAudioCacheFlow:
    """音频缓存流程测试"""

    @pytest.mark.slow
    def test_cache_hit_miss(self, sample_word_list):
        """测试缓存命中和未命中"""
        from src.audio_cache import AudioCache

        cache = AudioCache()

        # 1. 首次获取（未命中，需要生成）
        word = sample_word_list[0]['en']
        assert cache.is_cached(word, 'en') == False

        # 2. 生成音频
        audio_path = cache.get_audio(word, 'en', use_minimax=False)
        assert audio_path is not None
        assert os.path.exists(audio_path)

        # 3. 再次获取（命中缓存）
        assert cache.is_cached(word, 'en') == True
        audio_path2 = cache.get_audio(word, 'en', use_minimax=False)
        assert audio_path2 == audio_path

        # 清理
        cache.cleanup()

    @pytest.mark.slow
    def test_preload_progress(self, sample_word_list):
        """测试预加载进度"""
        from src.audio_cache import AudioCache
        import time

        cache = AudioCache()

        # 开始预加载
        cache.preload_words(sample_word_list[:2], mode='en_to_cn', use_minimax=False)

        # 检查进度
        status = cache.get_preload_status()
        assert 'total' in status
        assert 'completed' in status
        assert 'progress' in status

        # 等待完成
        max_wait = 30
        waited = 0
        while cache.preload_active and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        # 验证完成
        status = cache.get_preload_status()
        assert status['finished'] == True
        assert status['progress'] == 1.0

        # 清理
        cache.cleanup()
