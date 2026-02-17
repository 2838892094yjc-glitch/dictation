#!/usr/bin/env python3
"""
测试任务6：词库导入/导出功能
"""
import os
import json
import csv
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.vocabulary_store import VocabularyStore


def test_import_export():
    """测试导入导出功能"""
    print("=" * 60)
    print("测试任务6：词库导入/导出功能")
    print("=" * 60)

    # 初始化存储
    store = VocabularyStore()

    # 测试1: 列出预置词库
    print("\n【测试1】列出预置词库")
    builtin_vocabs = store.list_builtin_vocabularies()
    print(f"找到 {len(builtin_vocabs)} 个预置词库:")
    for vocab in builtin_vocabs:
        print(f"  - {vocab['name']}: {vocab['word_count']} 个单词")
        if vocab.get('description'):
            print(f"    描述: {vocab['description']}")
    assert len(builtin_vocabs) >= 4, "应该有至少4个预置词库"
    print("✅ 测试通过")

    # 测试2: 加载预置词库
    print("\n【测试2】加载预置词库")
    if builtin_vocabs:
        first_vocab = builtin_vocabs[0]
        result = store.load_builtin_vocabulary(first_vocab['file_path'], "测试_" + first_vocab['name'])
        assert result is not None, "加载预置词库失败"
        print(f"✅ 成功加载预置词库: {result['name']} ({result['word_count']}个单词)")

    # 测试3: JSON导出
    print("\n【测试3】JSON格式导出")
    test_words = [
        {"en": "test", "cn": "测试", "checked": False},
        {"en": "export", "cn": "导出", "checked": False},
        {"en": "import", "cn": "导入", "checked": False}
    ]
    store.save_vocabulary("测试导出", test_words)
    json_path = "/tmp/test_export.json"
    success = store.export_to_json("测试导出", json_path)
    assert success, "JSON导出失败"
    assert os.path.exists(json_path), "JSON文件未创建"
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert len(data['words']) == 3, "导出的单词数量不正确"
    print(f"✅ JSON导出成功: {json_path}")

    # 测试4: TXT导出
    print("\n【测试4】TXT格式导出")
    txt_path = "/tmp/test_export.txt"
    success = store.export_to_txt("测试导出", txt_path)
    assert success, "TXT导出失败"
    assert os.path.exists(txt_path), "TXT文件未创建"
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assert len(lines) == 3, "导出的行数不正确"
    print(f"✅ TXT导出成功: {txt_path}")
    print(f"   内容预览:")
    for line in lines:
        print(f"   {line.strip()}")

    # 测试5: CSV导出
    print("\n【测试5】CSV格式导出")
    csv_path = "/tmp/test_export.csv"
    success = store.export_to_csv("测试导出", csv_path)
    assert success, "CSV导出失败"
    assert os.path.exists(csv_path), "CSV文件未创建"
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 3, "导出的行数不正确"
    print(f"✅ CSV导出成功: {csv_path}")

    # 测试6: JSON导入
    print("\n【测试6】JSON格式导入")
    result = store.import_from_json(json_path, "测试导入JSON")
    assert result is not None, "JSON导入失败"
    assert result['word_count'] == 3, "导入的单词数量不正确"
    print(f"✅ JSON导入成功: {result['name']} ({result['word_count']}个单词)")

    # 测试7: TXT导入
    print("\n【测试7】TXT格式导入")
    result = store.import_from_txt(txt_path, "测试导入TXT")
    assert result is not None, "TXT导入失败"
    assert result['word_count'] == 3, "导入的单词数量不正确"
    print(f"✅ TXT导入成功: {result['name']} ({result['word_count']}个单词)")

    # 测试8: CSV导入
    print("\n【测试8】CSV格式导入")
    result = store.import_from_csv(csv_path, "测试导入CSV")
    assert result is not None, "CSV导入失败"
    assert result['word_count'] == 3, "导入的单词数量不正确"
    print(f"✅ CSV导入成功: {result['name']} ({result['word_count']}个单词)")

    # 测试9: 验证导入的数据
    print("\n【测试9】验证导入的数据完整性")
    loaded = store.load_vocabulary("测试导入JSON")
    assert loaded is not None, "加载导入的词库失败"
    assert len(loaded['words']) == 3, "词库单词数量不正确"
    assert loaded['words'][0]['en'] == 'test', "单词内容不正确"
    assert loaded['words'][0]['cn'] == '测试', "中文翻译不正确"
    print("✅ 数据完整性验证通过")

    # 清理测试数据
    print("\n【清理】删除测试词库")
    store.delete_vocabulary("测试导出")
    store.delete_vocabulary("测试导入JSON")
    store.delete_vocabulary("测试导入TXT")
    store.delete_vocabulary("测试导入CSV")
    for vocab in builtin_vocabs:
        store.delete_vocabulary("测试_" + vocab['name'])
    print("✅ 清理完成")

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)

    # 显示预置词库统计
    print("\n【预置词库统计】")
    total_words = sum(v['word_count'] for v in builtin_vocabs)
    print(f"预置词库总数: {len(builtin_vocabs)}")
    print(f"总单词数: {total_words}")
    print("\n详细列表:")
    for vocab in builtin_vocabs:
        print(f"  📚 {vocab['name']}: {vocab['word_count']} 个单词")


if __name__ == "__main__":
    try:
        test_import_export()
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
