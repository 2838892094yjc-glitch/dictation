#!/usr/bin/env python3
"""
三种听写模式演示脚本
展示英译中、中译英、拼写三种模式的工作流程
"""
import os
from src.minimax_tts import MiniMaxTTSEngine
from src.audio_cache import AudioCache
from src.handwriting_recognizer import HandwritingRecognizer


def demo_mode_en_to_cn():
    """演示模式1：英译中"""
    print("\n" + "=" * 60)
    print("模式1：英译中 (English to Chinese)")
    print("=" * 60)
    print("📝 说明：播报英文单词，用户填写中文释义")
    print()

    cache = AudioCache()
    test_word = {'en': 'apple', 'cn': '苹果'}

    # 生成英文音频
    print(f"1. 播报英文: {test_word['en']}")
    audio_path = cache.get_audio(
        test_word['en'],
        mode="en",
        voice_en="male_qn_qingse",
        use_minimax=True
    )

    if audio_path and os.path.exists(audio_path):
        print(f"   ✅ 音频已生成: {os.path.basename(audio_path)}")
    else:
        print(f"   ❌ 音频生成失败")
        return

    # 模拟用户答案
    print(f"\n2. 用户填写: 苹果")
    print(f"3. 正确答案: {test_word['cn']}")

    # 验证答案
    user_answer = "苹果"
    correct_answer = test_word['cn']
    is_correct = user_answer.strip() == correct_answer.strip()

    if is_correct:
        print(f"   ✅ 回答正确！")
    else:
        print(f"   ❌ 回答错误")

    cache.cleanup()


def demo_mode_cn_to_en():
    """演示模式2：中译英"""
    print("\n" + "=" * 60)
    print("模式2：中译英 (Chinese to English)")
    print("=" * 60)
    print("📝 说明：播报中文释义，用户填写英文单词")
    print()

    cache = AudioCache()
    test_word = {'en': 'apple', 'cn': '苹果'}

    # 生成中文音频
    print(f"1. 播报中文: {test_word['cn']}")
    audio_path = cache.get_audio(
        test_word['cn'],
        mode="cn",
        voice_cn="female_shaonv",
        use_minimax=True
    )

    if audio_path and os.path.exists(audio_path):
        print(f"   ✅ 音频已生成: {os.path.basename(audio_path)}")
    else:
        print(f"   ❌ 音频生成失败")
        return

    # 模拟用户答案
    print(f"\n2. 用户填写: apple")
    print(f"3. 正确答案: {test_word['en']}")

    # 验证答案（容错拼写）
    recognizer = HandwritingRecognizer(lang='en')
    user_answer = "apple"
    correct_answer = test_word['en']
    is_correct = recognizer._is_match(user_answer, correct_answer)

    if is_correct:
        print(f"   ✅ 回答正确！")
    else:
        print(f"   ❌ 回答错误")

    # 测试容错
    print(f"\n4. 测试拼写容错:")
    test_answers = ["apple", "aple", "appl", "appel"]
    for ans in test_answers:
        is_correct = recognizer._is_match(ans, correct_answer)
        status = "✅" if is_correct else "❌"
        print(f"   {status} {ans}")

    cache.cleanup()


def demo_mode_spell():
    """演示模式3：拼写"""
    print("\n" + "=" * 60)
    print("模式3：拼写 (Spelling)")
    print("=" * 60)
    print("📝 说明：播报英文+中文，用户拼写英文单词")
    print()

    cache = AudioCache()
    test_word = {'en': 'apple', 'cn': '苹果'}

    # 生成英文音频
    print(f"1. 播报英文: {test_word['en']}")
    audio_path_en = cache.get_audio(
        test_word['en'],
        mode="en",
        voice_en="male_qn_qingse",
        use_minimax=True
    )

    if audio_path_en and os.path.exists(audio_path_en):
        print(f"   ✅ 英文音频已生成: {os.path.basename(audio_path_en)}")
    else:
        print(f"   ❌ 英文音频生成失败")
        return

    # 延迟（模拟）
    print(f"   ⏱️  延迟1.5秒...")

    # 生成中文音频
    print(f"\n2. 播报中文: {test_word['cn']}")
    audio_path_cn = cache.get_audio(
        test_word['cn'],
        mode="cn",
        voice_cn="female_shaonv",
        use_minimax=True
    )

    if audio_path_cn and os.path.exists(audio_path_cn):
        print(f"   ✅ 中文音频已生成: {os.path.basename(audio_path_cn)}")
    else:
        print(f"   ❌ 中文音频生成失败")
        return

    # 模拟用户答案
    print(f"\n3. 用户拼写: apple")
    print(f"4. 正确答案: {test_word['en']}")

    # 验证答案
    recognizer = HandwritingRecognizer(lang='en')
    user_answer = "apple"
    correct_answer = test_word['en']
    is_correct = recognizer._is_match(user_answer, correct_answer)

    if is_correct:
        print(f"   ✅ 拼写正确！")
    else:
        print(f"   ❌ 拼写错误")

    cache.cleanup()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("自动听写 - 三种模式演示")
    print("=" * 60)
    print("\n本脚本演示三种听写模式的工作流程：")
    print("1. 英译中 - 听英文写中文")
    print("2. 中译英 - 听中文写英文")
    print("3. 拼写   - 听英文+中文拼写英文")
    print()
    input("按 Enter 键开始演示...")

    # 演示三种模式
    try:
        demo_mode_en_to_cn()
        input("\n按 Enter 键继续下一个模式...")

        demo_mode_cn_to_en()
        input("\n按 Enter 键继续下一个模式...")

        demo_mode_spell()

        print("\n" + "=" * 60)
        print("✅ 演示完成！")
        print("=" * 60)
        print()
        print("提示：")
        print("- 运行 `streamlit run app.py` 启动完整应用")
        print("- 运行 `python test_dictation_modes.py` 测试音频生成")
        print("- 查看 docs/FEATURE_GUIDE.md 了解详细使用说明")
        print()

    except KeyboardInterrupt:
        print("\n\n用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
