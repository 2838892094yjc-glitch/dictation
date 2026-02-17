#!/usr/bin/env python3
"""
任务6功能演示：词库导入/导出
展示如何使用新增的导入导出功能
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.vocabulary_store import VocabularyStore


def demo_import_export():
    """演示导入导出功能"""
    print("=" * 70)
    print("任务6功能演示：词库导入/导出")
    print("=" * 70)

    store = VocabularyStore()

    # 演示1: 查看预置词库
    print("\n【演示1】查看预置词库")
    print("-" * 70)
    builtin_vocabs = store.list_builtin_vocabularies()
    print(f"系统预置了 {len(builtin_vocabs)} 个词库：\n")

    for i, vocab in enumerate(builtin_vocabs, 1):
        print(f"{i}. {vocab['name']}")
        print(f"   📝 单词数量: {vocab['word_count']}")
        print(f"   📄 描述: {vocab.get('description', '无')}")
        print(f"   📂 文件: {os.path.basename(vocab['file_path'])}")
        print()

    # 演示2: 加载预置词库
    print("\n【演示2】加载预置词库")
    print("-" * 70)
    if builtin_vocabs:
        vocab = builtin_vocabs[0]
        print(f"正在加载: {vocab['name']}")
        result = store.load_builtin_vocabulary(vocab['file_path'], "演示_" + vocab['name'])
        if result:
            print(f"✅ 成功加载词库: {result['name']}")
            print(f"   包含 {result['word_count']} 个单词")

            # 显示前5个单词
            loaded = store.load_vocabulary(result['name'])
            if loaded:
                print(f"\n   前5个单词预览:")
                for i, word in enumerate(loaded['words'][:5], 1):
                    print(f"   {i}. {word['en']} - {word['cn']}")

    # 演示3: 创建自定义词库并导出
    print("\n\n【演示3】创建自定义词库并导出")
    print("-" * 70)
    custom_words = [
        {"en": "hello", "cn": "你好", "checked": False},
        {"en": "world", "cn": "世界", "checked": False},
        {"en": "python", "cn": "蟒蛇；Python语言", "checked": False},
        {"en": "code", "cn": "代码", "checked": False},
        {"en": "learn", "cn": "学习", "checked": False}
    ]

    print("创建词库: 演示词库")
    store.save_vocabulary("演示词库", custom_words)
    print(f"✅ 已保存 {len(custom_words)} 个单词\n")

    # 导出为不同格式
    formats = [
        ("JSON", "/tmp/demo_vocab.json", store.export_to_json),
        ("TXT", "/tmp/demo_vocab.txt", store.export_to_txt),
        ("CSV", "/tmp/demo_vocab.csv", store.export_to_csv)
    ]

    for format_name, path, export_func in formats:
        success = export_func("演示词库", path)
        if success:
            size = os.path.getsize(path)
            print(f"✅ {format_name}格式导出成功")
            print(f"   文件: {path}")
            print(f"   大小: {size} 字节")

            # 显示文件内容预览
            if format_name == "TXT":
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   内容预览:")
                for line in content.split('\n')[:3]:
                    if line.strip():
                        print(f"   {line}")
            print()

    # 演示4: 导入词库
    print("\n【演示4】导入词库")
    print("-" * 70)
    print("从TXT文件导入词库...")
    result = store.import_from_txt("/tmp/demo_vocab.txt", "演示_导入的词库")
    if result:
        print(f"✅ 导入成功: {result['name']}")
        print(f"   单词数量: {result['word_count']}")

        # 验证导入的内容
        loaded = store.load_vocabulary(result['name'])
        if loaded:
            print(f"\n   导入的单词:")
            for i, word in enumerate(loaded['words'], 1):
                print(f"   {i}. {word['en']} - {word['cn']}")

    # 演示5: 格式转换
    print("\n\n【演示5】格式转换示例")
    print("-" * 70)
    print("演示如何将JSON格式转换为TXT格式：")
    print("1. 导入JSON文件")
    print("2. 导出为TXT文件")
    print()

    # 使用预置词库进行转换
    if builtin_vocabs:
        vocab = builtin_vocabs[0]
        print(f"源文件: {os.path.basename(vocab['file_path'])} (JSON)")

        # 导入
        result = store.import_from_json(vocab['file_path'], "转换测试")
        if result:
            # 导出为TXT
            txt_path = "/tmp/converted.txt"
            store.export_to_txt("转换测试", txt_path)
            print(f"目标文件: {os.path.basename(txt_path)} (TXT)")
            print(f"✅ 转换完成")

            # 显示文件大小对比
            json_size = os.path.getsize(vocab['file_path'])
            txt_size = os.path.getsize(txt_path)
            print(f"\n文件大小对比:")
            print(f"  JSON: {json_size} 字节")
            print(f"  TXT:  {txt_size} 字节")
            print(f"  压缩率: {(1 - txt_size/json_size)*100:.1f}%")

    # 清理演示数据
    print("\n\n【清理】删除演示数据")
    print("-" * 70)
    demo_vocabs = ["演示词库", "演示_导入的词库", "转换测试"]
    for vocab in builtin_vocabs:
        demo_vocabs.append("演示_" + vocab['name'])

    for name in demo_vocabs:
        if store.vocabulary_exists(name):
            store.delete_vocabulary(name)
            print(f"✅ 已删除: {name}")

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)

    print("\n💡 使用提示:")
    print("1. 在Streamlit界面中，进入'词库管理'页面")
    print("2. 点击'📥📤 导入/导出'区域")
    print("3. 选择相应的标签页进行操作")
    print("4. 预置词库可以直接加载使用")
    print("5. 支持JSON、TXT、CSV三种格式互相转换")


if __name__ == "__main__":
    try:
        demo_import_export()
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
