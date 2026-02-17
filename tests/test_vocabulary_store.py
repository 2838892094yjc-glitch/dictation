"""
词库存储单元测试
"""
import pytest
import os
import json
from data.vocabulary_store import VocabularyStore


class TestVocabularyStore:
    """词库存储测试类"""

    def test_init(self, temp_dir):
        """测试初始化"""
        store = VocabularyStore(data_dir=temp_dir)
        assert store.data_dir == temp_dir
        assert os.path.exists(temp_dir)

    def test_save_and_load_vocabulary(self, temp_dir, sample_word_list):
        """测试保存和加载词库"""
        store = VocabularyStore(data_dir=temp_dir)

        # 保存词库
        vocab_data = {
            'name': '测试词库',
            'words': sample_word_list,
            'description': '这是一个测试词库'
        }

        success = store.save_vocabulary('测试词库', vocab_data)
        assert success == True

        # 加载词库
        loaded = store.load_vocabulary('测试词库')
        assert loaded is not None
        assert loaded['name'] == '测试词库'
        assert len(loaded['words']) == len(sample_word_list)
        assert loaded['description'] == '这是一个测试词库'

    def test_list_vocabularies(self, temp_dir, sample_word_list):
        """测试列出词库"""
        store = VocabularyStore(data_dir=temp_dir)

        # 保存几个词库
        store.save_vocabulary('词库1', {'name': '词库1', 'words': sample_word_list})
        store.save_vocabulary('词库2', {'name': '词库2', 'words': sample_word_list})

        # 列出词库
        vocabs = store.list_vocabularies()

        assert len(vocabs) >= 2
        assert any(v['name'] == '词库1' for v in vocabs)
        assert any(v['name'] == '词库2' for v in vocabs)

    def test_delete_vocabulary(self, temp_dir, sample_word_list):
        """测试删除词库"""
        store = VocabularyStore(data_dir=temp_dir)

        # 保存词库
        store.save_vocabulary('待删除', {'name': '待删除', 'words': sample_word_list})

        # 确认存在
        assert store.load_vocabulary('待删除') is not None

        # 删除
        success = store.delete_vocabulary('待删除')
        assert success == True

        # 确认已删除
        assert store.load_vocabulary('待删除') is None

    def test_rename_vocabulary(self, temp_dir, sample_word_list):
        """测试重命名词库"""
        store = VocabularyStore(data_dir=temp_dir)

        # 保存词库
        store.save_vocabulary('旧名称', {'name': '旧名称', 'words': sample_word_list})

        # 重命名
        success = store.rename_vocabulary('旧名称', '新名称')
        assert success == True

        # 检��
        assert store.load_vocabulary('旧名称') is None
        assert store.load_vocabulary('新名称') is not None

    def test_export_vocabulary(self, temp_dir, sample_word_list):
        """测试导出词库"""
        store = VocabularyStore(data_dir=temp_dir)

        # 保存词库
        vocab_data = {'name': '导出测试', 'words': sample_word_list}
        store.save_vocabulary('导出测试', vocab_data)

        # 导出
        export_path = os.path.join(temp_dir, 'export.json')
        success = store.export_vocabulary('导出测试', export_path)
        assert success == True
        assert os.path.exists(export_path)

        # 检查导出内容
        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data['name'] == '导出测���'
            assert len(data['words']) == len(sample_word_list)

    def test_import_vocabulary(self, temp_dir, sample_word_list):
        """测试导入词库"""
        store = VocabularyStore(data_dir=temp_dir)

        # 创建导入文件
        import_path = os.path.join(temp_dir, 'import.json')
        vocab_data = {'name': '导入测试', 'words': sample_word_list}
        with open(import_path, 'w', encoding='utf-8') as f:
            json.dump(vocab_data, f, ensure_ascii=False)

        # 导入
        success = store.import_vocabulary(import_path)
        assert success == True

        # 检查
        loaded = store.load_vocabulary('导入测试')
        assert loaded is not None
        assert len(loaded['words']) == len(sample_word_list)

    def test_load_nonexistent(self, temp_dir):
        """测试加载不存在的词库"""
        store = VocabularyStore(data_dir=temp_dir)

        result = store.load_vocabulary('不存在的词库')
        assert result is None

    def test_delete_nonexistent(self, temp_dir):
        """测试删除不存在的词库"""
        store = VocabularyStore(data_dir=temp_dir)

        result = store.delete_vocabulary('不存在的词库')
        assert result == False

    def test_special_characters_in_name(self, temp_dir, sample_word_list):
        """测试名称中的特殊字符"""
        store = VocabularyStore(data_dir=temp_dir)

        # 包含特殊字符的名称
        name = '测试/词库:2024'
        vocab_data = {'name': name, 'words': sample_word_list}

        # 保存和加载应该正常工作
        success = store.save_vocabulary(name, vocab_data)
        assert success == True

        loaded = store.load_vocabulary(name)
        assert loaded is not None
        assert loaded['name'] == name


class TestVocabularyStoreIntegration:
    """词库存储集成测试"""

    def test_full_workflow(self, temp_dir, sample_word_list):
        """测试完整工作流"""
        store = VocabularyStore(data_dir=temp_dir)

        # 1. 创建词库
        vocab_data = {
            'name': '完整测试',
            'words': sample_word_list,
            'description': '完整流程测试'
        }
        store.save_vocabulary('完整测试', vocab_data)

        # 2. 列出词库
        vocabs = store.list_vocabularies()
        assert any(v['name'] == '完整测试' for v in vocabs)

        # 3. 加载词库
        loaded = store.load_vocabulary('完整测试')
        assert loaded is not None

        # 4. 导出词库
        export_path = os.path.join(temp_dir, 'export.json')
        store.export_vocabulary('完整测试', export_path)
        assert os.path.exists(export_path)

        # 5. 重命名词库
        store.rename_vocabulary('完整测试', '完整测试_重命名')
        assert store.load_vocabulary('完整测试_重命名') is not None

        # 6. 删除词库
        store.delete_vocabulary('完整测试_重命名')
        assert store.load_vocabulary('完整测试_重命名') is None

        # 7. 导入词库
        store.import_vocabulary(export_path)
        assert store.load_vocabulary('完整测试') is not None
