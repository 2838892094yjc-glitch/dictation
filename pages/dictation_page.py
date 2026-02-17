"""
听写播放页面模块

提供听写播放页面的渲染和控制功能，包括：
- 播放设置（音色、间隔）
- 单词播放控制（上一个/下一个/播放）
- 自动连续播放
- 答案输入和保存
"""
import streamlit as st

from components import AudioPlayer
from components.audio_player import create_audio_player_from_session
from services import get_display_text, get_mode_name, get_placeholder_text, get_correct_answer
from src.minimax_tts import MiniMaxTTSEngine


def play_current_word():
    """播放当前单词"""
    if not st.session_state.selected_words:
        return

    player = create_audio_player_from_session()
    idx = st.session_state.dictation_order[st.session_state.current_index]
    word = st.session_state.selected_words[idx]
    mode = st.session_state.dictation_mode

    player.play_word(word, mode, use_js_delay=True)


def auto_play():
    """自动连续播放所有单词"""
    if not st.session_state.selected_words:
        return

    player = create_audio_player_from_session()
    words = st.session_state.selected_words
    order = st.session_state.dictation_order
    mode = st.session_state.dictation_mode
    interval = st.session_state.playback_interval

    def on_progress(current_index, total):
        st.session_state.current_index = current_index

    player.auto_play_all(
        words=words,
        order=order,
        mode=mode,
        interval=interval,
        on_progress=on_progress
    )

    st.success("播放完成！")


def render_dictation_page():
    """听写播放页"""
    st.title("🎧 听写播放")

    # 返回词库
    if st.button("← 返回词库"):
        st.session_state.page = 'vocabulary'
        st.rerun()

    if not st.session_state.selected_words:
        st.warning("请先在词库中选择要听写的单词")
        if st.button("去选词"):
            st.session_state.page = 'vocabulary'
            st.rerun()
        return

    # 设置面板
    _render_settings_panel()

    # 播放控制
    _render_playback_controls()

    # 自动连续播放
    st.divider()
    if st.button("▶️ 自动连续播放", type="primary", use_container_width=True):
        auto_play()

    # 手动输入答案区域
    _render_answer_input()

    # 进度显示
    _render_progress()


def _render_settings_panel():
    """渲染设置面板"""
    with st.expander("⚙️ 播放设置", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state.voice_en = st.selectbox(
                "🔊 英文音色",
                options=list(MiniMaxTTSEngine.ENGLISH_VOICES.keys()),
                index=list(MiniMaxTTSEngine.ENGLISH_VOICES.keys()).index(st.session_state.voice_en)
            )

        with col2:
            st.session_state.voice_cn = st.selectbox(
                "🔊 中文音色",
                options=list(MiniMaxTTSEngine.CHINESE_VOICES.keys()),
                index=list(MiniMaxTTSEngine.CHINESE_VOICES.keys()).index(st.session_state.voice_cn)
            )

        with col3:
            st.session_state.playback_interval = st.slider(
                "⏱️ 播放间隔(秒)", 1, 10, st.session_state.playback_interval
            )

        if st.session_state.shuffle_order:
            st.info("🔀 顺序已打乱")


def _render_playback_controls():
    """渲染播放控制区域"""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⏮️ 上一个"):
            if st.session_state.current_index > 0:
                st.session_state.current_index -= 1
                play_current_word()
                st.rerun()

    with col2:
        _render_current_word_display()

        # 直接播放当前单词
        if st.button("🔊 播放", type="primary", use_container_width=True):
            play_current_word()

    with col3:
        if st.button("下一个 ⏭️"):
            if st.session_state.current_index < len(st.session_state.selected_words) - 1:
                st.session_state.current_index += 1
                play_current_word()
                st.rerun()


def _render_current_word_display():
    """渲染当前单词显示区域"""
    current_word = st.session_state.selected_words[
        st.session_state.dictation_order[st.session_state.current_index]
    ]
    mode = st.session_state.dictation_mode

    display_text = get_display_text(current_word, mode)
    mode_name = get_mode_name(mode)

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; color: white;">
        <div style="font-size: 1rem; opacity: 0.8;">单词 {st.session_state.current_index + 1} / {len(st.session_state.selected_words)}</div>
        <div style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">
            {display_text}
        </div>
        <div style="font-size: 1.2rem; opacity: 0.9;">
            {mode_name}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_answer_input():
    """渲染答案输入区域"""
    st.divider()
    st.subheader("📝 填写答案")

    mode = st.session_state.dictation_mode
    placeholder_text = get_placeholder_text(mode)

    answer_key = f"answer_{st.session_state.current_index}"
    user_answer = st.text_input("请输入你的答案", key=answer_key, placeholder=placeholder_text)

    if st.button("✅ 确认答案"):
        if user_answer:
            _save_answer(user_answer)


def _save_answer(user_answer: str):
    """保存用户答案"""
    idx = st.session_state.dictation_order[st.session_state.current_index]
    word = st.session_state.selected_words[idx]
    mode = st.session_state.dictation_mode

    correct_answer = get_correct_answer(word, mode)

    st.session_state.user_answers[idx] = {
        'user': user_answer,
        'correct': correct_answer,
        'mode': mode
    }
    st.success(f"已保存答案: {user_answer}")

    # 自动跳到下一个
    if st.session_state.current_index < len(st.session_state.selected_words) - 1:
        st.session_state.current_index += 1
        st.rerun()


def _render_progress():
    """渲染进度显示"""
    st.divider()
    answered = len(st.session_state.user_answers)
    total = len(st.session_state.selected_words)
    progress = answered / total if total > 0 else 0
    st.progress(progress)
    st.markdown(f"**进度：{answered} / {total}**")
