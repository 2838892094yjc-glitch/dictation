"""
测试三种听写模式的音频生成
"""
import os
from src.minimax_tts import MiniMaxTTSEngine
from src.audio_cache import AudioCache

def test_dictation_modes():
    """测试三种听写模式"""
    print("=" * 60)
    print("测试听写模式切换功能")
    print("=" * 60)

    # 初始化引擎和缓存
    cache = AudioCache()

    # 测试单词
    test_words = [
        {'en': 'apple', 'cn': '苹果'},
        {'en': 'banana', 'cn': '香蕉'},
        {'en': 'computer', 'cn': '电脑'}
    ]

    print(f"\n测试单词: {[w['en'] for w in test_words]}")

    # 测试模式1：英译中 (播报英文)
    print("\n" + "=" * 60)
    print("模式1: 英译中 (en_to_cn)")
    print("=" * 60)
    print("播报: 英文单词")
    print("用户填写: 中文释义")

    for word in test_words:
        print(f"\n测试单词: {word['en']}")
        try:
            audio_path = cache.get_audio(
                word['en'],
                mode="en",
                voice_en="male_qn_qingse",
                use_minimax=True
            )
            if audio_path and os.path.exists(audio_path):
                size_kb = os.path.getsize(audio_path) / 1024
                print(f"  ✅ 英文音频生成成功: {audio_path}")
                print(f"     文件大小: {size_kb:.1f} KB")
            else:
                print(f"  ❌ 英文音频生成失败")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

    # 测试模式2：中译英 (播报中文)
    print("\n" + "=" * 60)
    print("模式2: 中译英 (cn_to_en)")
    print("=" * 60)
    print("播报: 中文释义")
    print("用户填写: 英文单词")

    for word in test_words:
        print(f"\n测试单词: {word['cn']}")
        try:
            audio_path = cache.get_audio(
                word['cn'],
                mode="cn",
                voice_cn="female_shaonv",
                use_minimax=True
            )
            if audio_path and os.path.exists(audio_path):
                size_kb = os.path.getsize(audio_path) / 1024
                print(f"  ✅ 中文音频生成成功: {audio_path}")
                print(f"     文件大小: {size_kb:.1f} KB")
            else:
                print(f"  ❌ 中文音频生成失败")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

    # 测试模式3：拼写 (播报英文+中文)
    print("\n" + "=" * 60)
    print("模式3: 拼写模式 (spell)")
    print("=" * 60)
    print("播报: 英文单词 + 中文释义")
    print("用户填写: 英文拼写")

    for word in test_words:
        print(f"\n测试单词: {word['en']} ({word['cn']})")
        try:
            # 播报英文
            audio_path_en = cache.get_audio(
                word['en'],
                mode="en",
                voice_en="male_qn_qingse",
                use_minimax=True
            )
            # 播报中文
            audio_path_cn = cache.get_audio(
                word['cn'],
                mode="cn",
                voice_cn="female_shaonv",
                use_minimax=True
            )

            if audio_path_en and os.path.exists(audio_path_en):
                size_kb = os.path.getsize(audio_path_en) / 1024
                print(f"  ✅ 英文音频: {size_kb:.1f} KB")
            else:
                print(f"  ❌ 英文音频生成失败")

            if audio_path_cn and os.path.exists(audio_path_cn):
                size_kb = os.path.getsize(audio_path_cn) / 1024
                print(f"  ✅ 中文音频: {size_kb:.1f} KB")
            else:
                print(f"  ❌ 中文音频生成失败")

        except Exception as e:
            print(f"  ❌ 错误: {e}")

    # 统计
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    status = cache.get_preload_status()
    print(f"缓存状态:")
    print(f"  总数: {len(cache.cache)}")
    print(f"  已完成: {status['completed']}")
    print(f"  错误数: {status['errors']}")

    print("\n✅ 所有模式测试完成！")

    # 清理缓存
    cache.cleanup()


if __name__ == '__main__':
    test_dictation_modes()
