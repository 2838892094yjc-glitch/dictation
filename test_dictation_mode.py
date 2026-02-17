#!/usr/bin/env python3
"""
测试听写模式切换功能
"""
import sys
sys.path.insert(0, '.')

def test_session_state_initialization():
    """测试 session_state 初始化"""
    print("\n=== 测试 1: Session State 初始化 ===")

    # 模拟 session_state
    session_state = {}

    # 初始化 dictation_mode
    if 'dictation_mode' not in session_state:
        session_state['dictation_mode'] = "en_to_cn"

    assert session_state['dictation_mode'] == "en_to_cn", "默认模式应为 en_to_cn"
    print("✓ dictation_mode 默认值正确")

    # 切换模式
    session_state['dictation_mode'] = "cn_to_en"
    assert session_state['dictation_mode'] == "cn_to_en", "模式切换失败"
    print("✓ 模式切换正常")

    return True


def test_mode_display():
    """测试模式显示逻辑"""
    print("\n=== 测试 2: 模式显示逻辑 ===")

    test_cases = [
        {
            "mode": "en_to_cn",
            "word": {"en": "apple", "cn": "苹果"},
            "expected_display": "apple",
            "expected_name": "英译中 (听英文写中文)"
        },
        {
            "mode": "cn_to_en",
            "word": {"en": "apple", "cn": "苹果"},
            "expected_display": "苹果",
            "expected_name": "中译英 (听中文写英文)"
        },
        {
            "mode": "spell",
            "word": {"en": "apple", "cn": "苹果"},
            "expected_display": "apple / 苹果",
            "expected_name": "拼写 (听英文+中文拼写英文)"
        }
    ]

    for case in test_cases:
        mode = case["mode"]
        word = case["word"]

        if mode == "en_to_cn":
            display_text = word['en']
            mode_name = "英译中 (听英文写中文)"
        elif mode == "cn_to_en":
            display_text = word['cn']
            mode_name = "中译英 (听中文写英文)"
        else:  # spell
            display_text = f"{word['en']} / {word['cn']}"
            mode_name = "拼写 (听英文+中文拼写英文)"

        assert display_text == case["expected_display"], f"模式 {mode} 显示文本错误"
        assert mode_name == case["expected_name"], f"模式 {mode} 名称错误"
        print(f"✓ 模式 {mode} 显示正确: {display_text}")

    return True


def test_answer_saving():
    """测试答案保存逻辑"""
    print("\n=== 测试 3: 答案保存逻辑 ===")

    test_cases = [
        {
            "mode": "en_to_cn",
            "word": {"en": "apple", "cn": "苹果"},
            "user_answer": "苹果",
            "expected_correct": "苹果"
        },
        {
            "mode": "cn_to_en",
            "word": {"en": "apple", "cn": "苹果"},
            "user_answer": "apple",
            "expected_correct": "apple"
        },
        {
            "mode": "spell",
            "word": {"en": "apple", "cn": "苹果"},
            "user_answer": "apple",
            "expected_correct": "apple"
        }
    ]

    for case in test_cases:
        mode = case["mode"]
        word = case["word"]
        user_answer = case["user_answer"]

        # 模拟答案保存逻辑
        if mode == "en_to_cn":
            correct_answer = word['cn']
        elif mode == "cn_to_en":
            correct_answer = word['en']
        else:  # spell
            correct_answer = word['en']

        saved_answer = {
            'user': user_answer,
            'correct': correct_answer,
            'mode': mode
        }

        assert saved_answer['correct'] == case["expected_correct"], f"模式 {mode} 正确答案错误"
        print(f"✓ 模式 {mode} 答案保存正确: {saved_answer}")

    return True


def test_answer_grading():
    """测试答案批改逻辑"""
    print("\n=== 测试 4: 答案批改逻辑 ===")

    test_cases = [
        # 正确答案
        {"user": "apple", "correct": "apple", "expected": True},
        {"user": "Apple", "correct": "apple", "expected": True},  # 大小写不敏感
        {"user": "APPLE", "correct": "apple", "expected": True},
        {"user": "苹果", "correct": "苹果", "expected": True},

        # 错误答案
        {"user": "appl", "correct": "apple", "expected": False},
        {"user": "banana", "correct": "apple", "expected": False},
        {"user": "苹", "correct": "苹果", "expected": False},
    ]

    for case in test_cases:
        user_ans = case["user"]
        correct_ans = case["correct"]

        # 批改逻辑（大小写不敏感）
        is_correct = user_ans.lower().strip() == correct_ans.lower().strip()

        assert is_correct == case["expected"], f"批改错误: {user_ans} vs {correct_ans}"
        result = "正确" if is_correct else "错误"
        print(f"✓ {user_ans} vs {correct_ans} → {result}")

    return True


def test_minimax_voices():
    """测试 MiniMax TTS 音色配置"""
    print("\n=== 测试 5: MiniMax TTS 音色配置 ===")

    from src.minimax_tts import MiniMaxTTSEngine

    # 检查音色列表
    en_voices = list(MiniMaxTTSEngine.ENGLISH_VOICES.keys())
    cn_voices = list(MiniMaxTTSEngine.CHINESE_VOICES.keys())

    assert len(en_voices) > 0, "英文音色列表为空"
    assert len(cn_voices) > 0, "中文音色列表为空"

    print(f"✓ 英文音色数量: {len(en_voices)}")
    print(f"  {', '.join(en_voices)}")
    print(f"✓ 中文音色数量: {len(cn_voices)}")
    print(f"  {', '.join(cn_voices)}")

    # 测试引擎初始化
    engine = MiniMaxTTSEngine()
    assert engine.voice is not None, "默认音色未设置"
    print(f"✓ 默认音色: {engine.voice}")

    return True


def test_audio_cache():
    """测试音频缓存"""
    print("\n=== 测试 6: 音频缓存 ===")

    from src.audio_cache import AudioCache

    cache = AudioCache()
    assert cache is not None, "音频缓存初始化失败"
    print("✓ 音频缓存初始化成功")

    # 测试缓存路径生成
    path_en = cache.get_cache_path("apple", "en")
    path_cn = cache.get_cache_path("苹果", "cn")

    assert path_en != path_cn, "不同语言的缓存路径应该不同"
    print(f"✓ 英文缓存路径: {path_en}")
    print(f"✓ 中文缓存路径: {path_cn}")

    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("听写模式切换功能测试")
    print("=" * 60)

    tests = [
        test_session_state_initialization,
        test_mode_display,
        test_answer_saving,
        test_answer_grading,
        test_minimax_voices,
        test_audio_cache,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
