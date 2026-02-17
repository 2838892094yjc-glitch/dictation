"""
答案批改页面模块
包含手动输入批改、拍照批改和批改结果展示功能
"""
import streamlit as st
import time
from PIL import Image

from src.handwriting_recognizer import HandwritingRecognizer
from services.dictation_service import check_answer, get_correct_answer, get_display_text


def render_manual_grading():
    """渲染手动输入批改部分（答案对照）"""
    st.subheader("📋 答案对照")

    # 获取当前听写模式
    mode = st.session_state.get('dictation_mode', 'en_to_cn')

    correct_count = 0
    for i, idx in enumerate(st.session_state.dictation_order):
        word = st.session_state.selected_words[idx]
        user_ans = st.session_state.user_answers.get(idx, {})

        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            st.markdown(f"**{i+1}.**")

        with col2:
            # 根据模式显示题目
            display_text = get_display_text(word, mode)
            correct_answer = get_correct_answer(word, mode)

            if mode == "en_to_cn":
                st.markdown(f"**题目：** {word['en']}")
                st.markdown(f"*正确答案：{word['cn']}*")
            elif mode == "cn_to_en":
                st.markdown(f"**题目：** {word['cn']}")
                st.markdown(f"*正确答案：{word['en']}*")
            else:  # spell
                st.markdown(f"**题目：** {word['en']} / {word['cn']}")
                st.markdown(f"*正确答案：{word['en']}*")

        with col3:
            if user_ans:
                is_correct = check_answer(user_ans['user'], user_ans['correct'])
                if is_correct:
                    st.success(f"✅ {user_ans['user']}")
                    correct_count += 1
                else:
                    st.error(f"❌ {user_ans['user']} (正确答案: {user_ans['correct']})")
                    # 添加到错题本
                    st.session_state.wrong_answer_manager.add_wrong_answer(
                        en=word['en'],
                        cn=word['cn'],
                        user_answer=user_ans['user']
                    )
            else:
                st.warning("未作答")

    # 统计
    total = len(st.session_state.selected_words)
    answered = len(st.session_state.user_answers)
    st.markdown(f"**正确：{correct_count} / {answered}**")

    return correct_count


def render_photo_grading():
    """渲染拍照批改部分"""
    st.divider()
    st.subheader("📷 拍照批改")

    st.info("提示：请将手写答案按顺序书写，每行一个单词，书写清晰。支持英文或中文答案。")

    uploaded_answer = st.file_uploader("上传手写答案照片", type=['jpg', 'png', 'jpeg'], key="answer_upload")

    if uploaded_answer:
        # 显示上传的图片
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(uploaded_answer, caption="上传的答案图片", use_container_width=True)

        with col2:
            # 识别按钮
            if st.button("🔍 开始识别并批改", type="primary"):
                _process_photo_grading(uploaded_answer)


def _process_photo_grading(uploaded_answer):
    """处理拍照批改的识别和批改逻辑"""
    with st.spinner("正在识别手写文字..."):
        # 保存上传的图片
        img_path = f"/tmp/{uploaded_answer.name}"
        Image.open(uploaded_answer).save(img_path)

        # 获取当前听写模式
        mode = st.session_state.get('dictation_mode', 'en_to_cn')

        # 根据模式初始化识别器（中文模式使用ch，英文模式使用en）
        if mode == "en_to_cn":
            # 英译中：用户写中文，使用中英文混合模型
            recognizer = HandwritingRecognizer(lang='ch')
            keep_chinese = True
        else:
            # 中译英/拼写：用户写英文，使用英文模型
            recognizer = HandwritingRecognizer(lang='en')
            keep_chinese = False

        # 识别文字
        recognized_words = recognizer.recognize(img_path, preprocess=True, keep_chinese=keep_chinese)

        st.success(f"识别到 {len(recognized_words)} 个单词")

        # 显示识别结果
        with st.expander("📝 识别结果"):
            for i, word in enumerate(recognized_words):
                st.markdown(f"{i+1}. {word}")

        # 准备标准答案
        expected_words = _prepare_expected_words(mode)

        # 批改
        with st.spinner("正在批改..."):
            result = recognizer.compare(recognized_words, expected_words, mode=mode)
            st.session_state.grading_result = result

            # 保存历史记录
            _save_grading_history(result, mode)

            st.rerun()


def _prepare_expected_words(mode: str) -> list:
    """准备标准答案列表"""
    expected_words = []

    for idx in st.session_state.dictation_order:
        word = st.session_state.selected_words[idx]
        # 根据模式选择正确答案
        if mode == "en_to_cn":
            # 听英文写中文，用户写的是中文
            expected_words.append({'en': word['en'], 'cn': word['cn'], 'expected': word['cn']})
        elif mode == "cn_to_en":
            # 听中文写英文，用户写的是英文
            expected_words.append({'en': word['en'], 'cn': word['cn'], 'expected': word['en']})
        else:  # spell
            # 拼写英文，用户写的是英文
            expected_words.append({'en': word['en'], 'cn': word['cn'], 'expected': word['en']})

    return expected_words


def _save_grading_history(result: dict, mode: str):
    """保存批改历史记录"""
    # 计算用时
    if st.session_state.dictation_start_time:
        duration = int(time.time() - st.session_state.dictation_start_time)
    else:
        duration = 0

    # 收集错误的单词
    wrong_words = []
    for i, item in enumerate(result['words']):
        if not item['correct']:
            idx = st.session_state.dictation_order[i] if i < len(st.session_state.dictation_order) else i
            if idx < len(st.session_state.selected_words):
                word = st.session_state.selected_words[idx]
                wrong_words.append({
                    'en': word['en'],
                    'cn': word['cn'],
                    'user_answer': item.get('recognized', '')
                })

    # 添加历史记录
    st.session_state.history_manager.add_record(
        mode=mode,
        vocabulary_name=st.session_state.current_vocabulary,
        total_words=result['total'],
        correct_count=result['correct_count'],
        duration_seconds=duration,
        wrong_words=wrong_words
    )

    # 添加错题到错题本
    for wrong_word in wrong_words:
        st.session_state.wrong_answer_manager.add_wrong_answer(
            en=wrong_word['en'],
            cn=wrong_word['cn'],
            user_answer=wrong_word['user_answer']
        )


def render_grading_result():
    """渲染批改结果展示"""
    if not st.session_state.grading_result:
        return

    st.divider()
    st.subheader("📊 批改结果")

    result = st.session_state.grading_result

    # 成绩统计
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("正确数", f"{result['correct_count']}/{result['total']}")
    with col2:
        st.metric("正确率", f"{result['score']}%")
    with col3:
        grade = _get_grade(result['score'])
        st.metric("评级", grade)

    # 详细结果
    st.subheader("📋 详细结果")

    for i, item in enumerate(result['words']):
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

        with col1:
            st.markdown(f"**{i+1}.**")

        with col2:
            st.markdown(f"**标准答案:** {item['expected']}")
            if item.get('chinese'):
                st.markdown(f"*{item['chinese']}*")

        with col3:
            st.markdown(f"**识别结果:** {item['recognized'] if item['recognized'] else '(未识别)'}")

        with col4:
            if item['correct']:
                st.success("✅ 正确")
            else:
                st.error("❌ 错误")

    # 操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 重新批改"):
            st.session_state.grading_result = None
            st.rerun()
    with col2:
        if st.button("📊 查看历史记录"):
            st.session_state.page = 'history'
            st.rerun()


def _get_grade(score: float) -> str:
    """根据分数获取评级"""
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"


def render_answer_page():
    """答案批改页主渲染函数"""
    st.title("✅ 答案批改")

    # 返回听写
    if st.button("← 返回听写"):
        st.session_state.page = 'dictation'
        st.rerun()

    if not st.session_state.selected_words:
        st.warning("没有听写记录")
        return

    # 显示答案对照（手动输入批改）
    render_manual_grading()

    # 拍照批改
    render_photo_grading()

    # 显示批改结果
    render_grading_result()
