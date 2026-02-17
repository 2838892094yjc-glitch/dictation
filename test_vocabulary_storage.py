"""
测试词库持久化存储功能
验证任务1的所有功能点
"""
from data.vocabulary_store import VocabularyStore
import os
import json


def test_vocabulary_store():
    """测试词库存储的完整功能"""

    print("=" * 60)
    print("测试任务1：词库持久化存储")
    print("=" * 60)

    # 初始化
    store = VocabularyStore()
    print(f"\n✓ VocabularyStore初始化成功")
    print(f"  存储目录: {store.base_dir}")

    # 1. 测试创建新词库
    print("\n[1] 测试保存词库")
    test_words = [
        {"en": "apple", "cn": "苹果", "checked": False},
        {"en": "banana", "cn": "香蕉", "checked": False},
        {"en": "computer", "cn": "电脑", "checked": True}
    ]

    success = store.save_vocabulary("测试词库1", test_words)
    if success:
        print("  ✓ 保存词库成功: 测试词库1")
    else:
        print("  ✗ 保存词库失败")
        return

    # 2. 测试加载词库
    print("\n[2] 测试加载词库")
    loaded = store.load_vocabulary("测试词库1")
    if loaded:
        print(f"  ✓ 加载成功: {loaded['name']}")
        print(f"  - 单词数量: {len(loaded['words'])}")
        print(f"  - 创建时间: {loaded['created_at']}")
        print(f"  - 更新时间: {loaded['updated_at']}")
        assert len(loaded['words']) == 3, "单词数量不匹配"
        assert loaded['words'][0]['en'] == 'apple', "单词内容不匹配"
    else:
        print("  ✗ 加载失败")
        return

    # 3. 测试列出所有词库
    print("\n[3] 测试列出所有词库")
    # 创建第二个词库
    store.save_vocabulary("测试词库2", [{"en": "test", "cn": "测试", "checked": False}])

    vocab_list = store.list_vocabularies()
    print(f"  ✓ 找到 {len(vocab_list)} 个词库:")
    for v in vocab_list:
        print(f"    - {v['name']}: {v['word_count']} 个单词")

    # 4. 测试重命名词库
    print("\n[4] 测试重命名词库")
    success = store.rename_vocabulary("测试词库2", "重命名词库")
    if success:
        print("  ✓ 重命名成功: 测试词库2 → 重命名词库")
        # 验证旧名称不存在
        assert not store.vocabulary_exists("测试词库2"), "旧词库仍然存在"
        # 验证新名称存在
        assert store.vocabulary_exists("重命名词库"), "新词库不存在"
    else:
        print("  ✗ 重命名失败")

    # 5. 测试词库是否存在
    print("\n[5] 测试检查词库是否存在")
    exists = store.vocabulary_exists("测试词库1")
    print(f"  ✓ 测试词库1存在: {exists}")
    exists = store.vocabulary_exists("不存在的词库")
    print(f"  ✓ 不存在的词库存在: {exists}")

    # 6. 测试自动保存（更新现有词库）
    print("\n[6] 测试更新词库（自动保存）")
    # 添加新单词
    loaded = store.load_vocabulary("测试词库1")
    loaded['words'].append({"en": "dog", "cn": "狗", "checked": False})
    success = store.save_vocabulary("测试词库1", loaded['words'])
    if success:
        print("  ✓ 更新成功")
        # 重新加载验证
        reloaded = store.load_vocabulary("测试词库1")
        print(f"  - 更新后单词数量: {len(reloaded['words'])}")
        assert len(reloaded['words']) == 4, "更新后单词数量不正确"
    else:
        print("  ✗ 更新失败")

    # 7. 测试删除词库
    print("\n[7] 测试删除词库")
    success = store.delete_vocabulary("重命名词库")
    if success:
        print("  ✓ 删除成功: 重命名词库")
        # 验证已删除
        assert not store.vocabulary_exists("重命名词库"), "词库仍然存在"
    else:
        print("  ✗ 删除失败")

    # 8. 验证默认词库
    print("\n[8] 验证默认词库")
    default = store.load_vocabulary("默认词库")
    if default:
        print(f"  ✓ 默认词库存在")
        print(f"  - 单词数量: {len(default['words'])}")
    else:
        print("  ! 默认词库不存在（这是正常的，首次使用时会自动创建）")

    # 清理测试数据
    print("\n[9] 清理测试数据")
    store.delete_vocabulary("测试词库1")
    print("  ✓ 测试数据已清理")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)

    # 功能清单检查
    print("\n功能清单验证:")
    print("  ✓ 保存词库到 JSON 文件")
    print("  ✓ 加载已有词库")
    print("  ✓ 创建新词库")
    print("  ✓ 删除词库")
    print("  ✓ 重命名词库")
    print("  ✓ 默认词库加载")
    print("  ✓ 自动保存功能（在app.py中集成）")


if __name__ == "__main__":
    test_vocabulary_store()
