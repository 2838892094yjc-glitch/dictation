"""
测试学习历史记录功能
"""
from src.history_manager import HistoryManager
import time


def test_history_manager():
    """测试历史管理器"""
    print("=" * 50)
    print("测试学习历史记录功能")
    print("=" * 50)

    hm = HistoryManager()

    # 测试1: 添加记录
    print("\n[测试1] 添加历史记录")
    record_id = hm.add_record(
        mode='en_to_cn',
        vocabulary_name='小学英语',
        total_words=10,
        correct_count=8,
        duration_seconds=300,
        wrong_words=[
            {'en': 'apple', 'cn': '苹果', 'user_answer': 'aple'},
            {'en': 'banana', 'cn': '香蕉', 'user_answer': 'bananna'}
        ]
    )
    print(f"✓ 记录ID: {record_id}")

    # 测试2: 添加多条记录
    print("\n[测试2] 添加多条记录")
    modes = ['en_to_cn', 'cn_to_en', 'spell']
    for i in range(5):
        hm.add_record(
            mode=modes[i % 3],
            vocabulary_name='测试词库',
            total_words=10,
            correct_count=6 + i,
            duration_seconds=200 + i * 30,
            wrong_words=[]
        )
    print("✓ 已添加5条记录")

    # 测试3: 获取所有记录
    print("\n[测试3] 获取所有记录")
    records = hm.get_all_records()
    print(f"✓ 总记录数: {len(records)}")
    for i, record in enumerate(records[:3]):
        print(f"  {i+1}. {record['date'][:19]} - {record['mode']} - 分数: {record['score']}%")

    # 测试4: 获取统计信息
    print("\n[测试4] 获取统计信息")
    stats = hm.get_statistics()
    print(f"✓ 总听写次数: {stats['total_sessions']}")
    print(f"✓ 总单词数: {stats['total_words']}")
    print(f"✓ 平均分: {stats['average_score']:.2f}%")
    print(f"✓ 总时长: {stats['total_duration']}秒")
    print(f"✓ 模式统计: {stats['mode_stats']}")

    # 测试5: 获取高频错词
    print("\n[测试5] 获取高频错词")
    wrong_freq = hm.get_wrong_words_frequency(limit=10)
    print(f"✓ 高频错词数: {len(wrong_freq)}")
    for i, word in enumerate(wrong_freq):
        print(f"  {i+1}. {word['en']} ({word['cn']}) - 错误{word['count']}次")

    # 测试6: 导出CSV
    print("\n[测试6] 导出CSV")
    output_file = "/tmp/test_history.csv"
    if hm.export_to_csv(output_file):
        print(f"✓ 已导出到: {output_file}")
        with open(output_file, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            print(f"  文件行数: {len(lines)}")
    else:
        print("✗ 导出失败")

    # 测试7: 删除记录
    print("\n[测试7] 删除记录")
    if records:
        first_id = records[0]['id']
        if hm.delete_record(first_id):
            print(f"✓ 已删除记录: {first_id}")
            new_count = len(hm.get_all_records())
            print(f"  剩余记录数: {new_count}")
        else:
            print("✗ 删除失败")

    # 测试8: 清空所有记录
    print("\n[测试8] 清空所有记录")
    if hm.clear_all_records():
        print("✓ 已清空所有记录")
        final_count = len(hm.get_all_records())
        print(f"  最终记录数: {final_count}")
    else:
        print("✗ 清空失败")

    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    test_history_manager()
