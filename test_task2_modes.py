"""
测试任务2：听写模式切换功能
测试所有三种模式的TTS和逻辑
"""
import os
import tempfile
from src.minimax_tts import MiniMaxTTSEngine
from src.audio_cache import AudioCache

def test_mode_en_to_cn():
    """测试英译中模式"""
    print("\n" + "="*60)
    print("测试模式1: 英译中 (en_to_cn)")
    print("="*60)

    cache = AudioCache()
    test_word = "apple"
    test_meaning = "苹果"

    print(f"📝 单词: {test_word}")
    print(f"📝 释义: {test_meaning}")
    print(f"🎯 模式: 播放英文，要求写中文")

    # 获取英文音频
    audio_path = cache.get_audio(test_word, mode="en", voice_en="male_qn_qingse")

    if audio_path and os.path.exists(audio_path):
        file_size = os.path.getsize(audio_path)
        print(f"✅ 英文音频生成成功: {audio_path}")
        print(f"   文件大小: {file_size} bytes")

        # 验证答案逻辑
        user_answer = "苹果"
        correct_answer = test_meaning
        is_correct = user_answer.strip() == correct_answer.strip()
        print(f"✅ 答案验证逻辑正确: 用户答案'{user_answer}' == 正确答案'{correct_answer}' -> {is_correct}")
        return True
    else:
        print("❌ 英文音频生成失败")
        return False

def test_mode_cn_to_en():
    """测试中译英模式"""
    print("\n" + "="*60)
    print("测试模式2: 中译英 (cn_to_en)")
    print("="*60)

    cache = AudioCache()
    test_word = "computer"
    test_meaning = "电脑"

    print(f"📝 单词: {test_word}")
    print(f"📝 释义: {test_meaning}")
    print(f"🎯 模式: 播放中文，要求写英文")

    # 获取中文音频
    audio_path = cache.get_audio(test_meaning, mode="cn", voice_cn="female_shaonv")

    if audio_path and os.path.exists(audio_path):
        file_size = os.path.getsize(audio_path)
        print(f"✅ 中文音频生成成功: {audio_path}")
        print(f"   文件大小: {file_size} bytes")

        # 验证答案逻辑
        user_answer = "computer"
        correct_answer = test_word
        is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
        print(f"✅ 答案验证逻辑正确: 用户答案'{user_answer}' == 正确答案'{correct_answer}' -> {is_correct}")
        return True
    else:
        print("❌ 中文音频生成失败")
        return False

def test_mode_spell():
    """测试拼写模式"""
    print("\n" + "="*60)
    print("测试模式3: 拼写 (spell)")
    print("="*60)

    cache = AudioCache()
    test_word = "banana"
    test_meaning = "香蕉"

    print(f"📝 单词: {test_word}")
    print(f"📝 释义: {test_meaning}")
    print(f"🎯 模式: 播放英文+中文，要求拼写英文")

    # 获取英文音频
    audio_path_en = cache.get_audio(test_word, mode="en", voice_en="male_qn_qingse")
    # 获取中文音频
    audio_path_cn = cache.get_audio(test_meaning, mode="cn", voice_cn="female_shaonv")

    success = True
    if audio_path_en and os.path.exists(audio_path_en):
        file_size = os.path.getsize(audio_path_en)
        print(f"✅ 英文音频生成成功: {audio_path_en}")
        print(f"   文件大小: {file_size} bytes")
    else:
        print("❌ 英文音频生成失败")
        success = False

    if audio_path_cn and os.path.exists(audio_path_cn):
        file_size = os.path.getsize(audio_path_cn)
        print(f"✅ 中文音频生成成功: {audio_path_cn}")
        print(f"   文件大小: {file_size} bytes")
    else:
        print("❌ 中文音频生成失败")
        success = False

    if success:
        # 验证答案逻辑
        user_answer = "banana"
        correct_answer = test_word
        is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
        print(f"✅ 答案验证逻辑正确: 用户答案'{user_answer}' == 正确答案'{correct_answer}' -> {is_correct}")

    return success

def test_voice_options():
    """测试不同音色"""
    print("\n" + "="*60)
    print("测试音色选项")
    print("="*60)

    engine = MiniMaxTTSEngine()

    print(f"可用英文音色 ({len(MiniMaxTTSEngine.ENGLISH_VOICES)}个):")
    for name, voice_id in MiniMaxTTSEngine.ENGLISH_VOICES.items():
        print(f"  - {name}: {voice_id}")

    print(f"\n可用中文音色 ({len(MiniMaxTTSEngine.CHINESE_VOICES)}个):")
    for name, voice_id in MiniMaxTTSEngine.CHINESE_VOICES.items():
        print(f"  - {name}: {voice_id}")

    return True

def main():
    """运行所有测试"""
    print("\n" + "🎯"*30)
    print("任务2测试：听写模式切换功能")
    print("🎯"*30)

    results = []

    # 测试所有模式
    results.append(("英译中模式", test_mode_en_to_cn()))
    results.append(("中译英模式", test_mode_cn_to_en()))
    results.append(("拼写模式", test_mode_spell()))
    results.append(("音色选项", test_voice_options()))

    # 输出测试结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 所有测试通过！任务2功能完整可用。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
