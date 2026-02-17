"""
学习历史记录功能演示
展示如何在听写流程中使用历史记录
"""
from src.history_manager import HistoryManager
import time


def demo_dictation_with_history():
    """演示带历史记录的听写流程"""
    print("=" * 60)
    print("学习历史记录功能演示")
    print("=" * 60)

    # 初始化历史管理器
    hm = HistoryManager()

    # 模拟听写流程
    print("\n📚 开始听写...")
    print("词库: 小学英语")
    print("模式: 英译中")
    print("单词数: 10")

    # 记录开始时间
    start_time = time.time()

    # 模拟听写过程
    print("\n🎧 播放单词...")
    time.sleep(1)  # 模拟听写时间

    # 模拟批改结果
    total_words = 10
    correct_count = 8
    wrong_words = [
        {'en': 'apple', 'cn': '苹果', 'user_answer': 'aple'},
        {'en': 'computer', 'cn': '电脑', 'user_answer': 'compter'}
    ]

    # 计算用时
    duration = int(time.time() - start_time)

    print("\n✅ 批改完成！")
    print(f"正确: {correct_count}/{total_words}")
    print(f"分数: {correct_count/total_words*100:.1f}%")
    print(f"用时: {duration}秒")

    # 保存历史记录
    print("\n💾 保存历史记录...")
    record_id = hm.add_record(
        mode='en_to_cn',
        vocabulary_name='小学英语',
        total_words=total_words,
        correct_count=correct_count,
        duration_seconds=duration,
        wrong_words=wrong_words
    )
    print(f"✓ 记录已保存，ID: {record_id}")

    # 查看统计信息
    print("\n📊 学习统计:")
    stats = hm.get_statistics()
    print(f"- 总听写次数: {stats['total_sessions']}")
    print(f"- 总单词数: {stats['total_words']}")
    print(f"- 平均正确率: {stats['average_score']:.1f}%")
    print(f"- 总学习时长: {stats['total_duration']}秒")

    # 查看高频错词
    print("\n🔥 高频错词:")
    wrong_freq = hm.get_wrong_words_frequency(limit=5)
    if wrong_freq:
        for i, word in enumerate(wrong_freq):
            print(f"{i+1}. {word['en']} ({word['cn']}) - 错误{word['count']}次")
    else:
        print("暂无错词记录")

    # 查看历史记录
    print("\n📋 最近的听写记录:")
    records = hm.get_all_records(limit=5)
    for i, record in enumerate(records):
        date = record['date'][:19]
        mode_name = {'en_to_cn': '英译中', 'cn_to_en': '中译英', 'spell': '拼写'}.get(record['mode'], record['mode'])
        print(f"{i+1}. {date} - {mode_name} - {record['vocabulary_name']} - {record['score']:.1f}%")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo_dictation_with_history()
